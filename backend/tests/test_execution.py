import logging
import time

import pytest
from sqlalchemy import event, text

import src.database
from src.config import settings
from src.job_search_query import service
from src.job_search_query.service import (
    QueryExecutionError,
    QueryPermissionError,
    QueryTimeoutError,
    execute_query,
)
from src.job_search_query.utils import get_readonly_engine
from src.job_search_query.validator import validate_sql


def seed_jobs(db, user_id, count):
    db.execute(
        text(
            "INSERT INTO job (company_name, position, location, status, user_id) "
            "SELECT 'bulk' || g, 'p', 'l', 'APPLIED', :uid FROM generate_series(1, :n) g"
        ),
        {"uid": user_id, "n": count},
    )
    db.commit()


@pytest.fixture()
def statements():
    engine = get_readonly_engine()
    seen = []

    def record(conn, cursor, statement, parameters, context, executemany):
        seen.append((statement, parameters))

    event.listen(engine, "before_cursor_execute", record)
    yield seen
    event.remove(engine, "before_cursor_execute", record)


@pytest.fixture()
def checkouts():
    engine = get_readonly_engine()
    seen = []

    def record(dbapi_connection, connection_record, connection_proxy):
        seen.append(id(dbapi_connection))

    event.listen(engine, "checkout", record)
    yield seen
    event.remove(engine, "checkout", record)


@pytest.fixture()
def service_logs(monkeypatch):
    monkeypatch.setattr(service.logger, "disabled", False)


def test_user_a_gets_only_a_rows(two_users):
    a, _ = two_users
    result = execute_query("SELECT company_name FROM job ORDER BY id", a.id)
    assert result.columns == ["company_name"]
    assert [row["company_name"] for row in result.rows] == ["AlphaCorp", "AlphaTwo"]


def test_user_b_gets_only_b_rows(two_users):
    _, b = two_users
    result = execute_query("SELECT company_name FROM job ORDER BY id", b.id)
    assert [row["company_name"] for row in result.rows] == ["BetaSecret"]


def test_validated_query_runs_end_to_end(two_users):
    a, _ = two_users
    sql = validate_sql("SELECT status, count(*) AS n FROM job GROUP BY status ORDER BY n DESC, status")
    result = execute_query(sql, a.id)
    assert {row["status"]: row["n"] for row in result.rows} == {"APPLIED": 1, "SAVED": 1}


def test_other_users_data_returns_zero_rows(two_users):
    a, b = two_users
    by_name = validate_sql("SELECT company_name FROM job WHERE company_name = 'BetaSecret'")
    by_id = validate_sql(f"SELECT company_name FROM job WHERE id IN (SELECT id FROM job WHERE id = {b.id + 1000})")
    assert execute_query(by_name, a.id).rows == []
    assert execute_query(by_id, a.id).rows == []
    b_ids = execute_query("SELECT id FROM job", b.id).rows
    assert execute_query(f"SELECT company_name FROM job WHERE id = {b_ids[0]['id']}", a.id).rows == []


def test_unknown_user_gets_zero_rows(two_users):
    assert execute_query("SELECT id FROM job", 999999).rows == []


def test_row_cap_is_enforced(db, two_users):
    a, _ = two_users
    seed_jobs(db, a.id, 60)
    assert len(execute_query("SELECT id FROM job", a.id).rows) == settings.job_search_max_rows == 50


def test_row_cap_follows_settings(db, two_users, monkeypatch):
    a, _ = two_users
    seed_jobs(db, a.id, 20)
    monkeypatch.setattr(settings, "job_search_max_rows", 5)
    assert len(execute_query("SELECT id FROM job", a.id).rows) == 5


def test_heavy_cross_join_hits_the_timeout(db, two_users, monkeypatch):
    a, _ = two_users
    seed_jobs(db, a.id, 3000)
    monkeypatch.setattr(settings, "job_search_statement_timeout_seconds", 1)
    sql = validate_sql("SELECT count(*) FROM job a, job b, job c")
    started = time.monotonic()
    with pytest.raises(QueryTimeoutError):
        execute_query(sql, a.id)
    assert time.monotonic() - started < 6
    assert execute_query("SELECT id FROM job LIMIT 1", a.id).rows != []


def test_permission_error_is_friendly(two_users):
    a, _ = two_users
    with pytest.raises(QueryPermissionError):
        execute_query("SELECT user_id FROM job", a.id)


def test_write_is_blocked_and_rows_survive(db, two_users):
    a, _ = two_users
    with pytest.raises((QueryPermissionError, QueryExecutionError)):
        execute_query("DELETE FROM job", a.id)
    assert db.execute(text("SELECT count(*) FROM job")).scalar() == 3


def test_bad_sql_becomes_generic_execution_error(two_users):
    a, _ = two_users
    with pytest.raises(QueryExecutionError):
        execute_query("SELEC nonsense", a.id)


def test_errors_do_not_expose_raw_text(two_users):
    a, _ = two_users
    with pytest.raises(QueryPermissionError) as exc:
        execute_query("SELECT user_id FROM job", a.id)
    assert exc.value.__cause__ is None
    assert exc.value.__suppress_context__ is True
    assert str(exc.value) == "query not permitted"


def test_logs_only_the_sqlstate(two_users, caplog, service_logs):
    a, _ = two_users
    with caplog.at_level(logging.DEBUG, logger=service.logger.name):
        with pytest.raises(QueryPermissionError):
            execute_query("SELECT user_id FROM job WHERE company_name = 'zebra-secret'", a.id)
    assert "42501" in caplog.text
    assert "zebra-secret" not in caplog.text
    assert "user_id" not in caplog.text
    assert "SELECT" not in caplog.text
    assert "refus" not in caplog.text.lower()


def test_runs_as_the_readonly_role(two_users):
    a, _ = two_users
    assert execute_query("SELECT current_user AS who", a.id).rows == [{"who": "job_search_ro"}]


def test_normal_app_connection_is_never_used(two_users, monkeypatch):
    a, _ = two_users
    user_id = a.id

    def boom(*args, **kwargs):
        raise AssertionError("normal app connection used")

    monkeypatch.setattr(src.database.engine, "connect", boom)
    monkeypatch.setattr(src.database, "SessionLocal", boom)
    assert len(execute_query("SELECT id FROM job", user_id).rows) == 2


def test_user_id_and_sql_text_stay_separate(two_users, statements):
    a, _ = two_users
    sql = "SELECT company_name FROM job WHERE company_name ILIKE '%alpha%' OR company_name = 'a:b'"
    result = execute_query(sql, a.id)
    assert len(result.rows) == 2
    executed = [statement for statement, _ in statements]
    assert sql.replace("%", "%%") in executed
    with_params = [(s, p) for s, p in statements if p]
    assert len(with_params) == 1
    statement, params = with_params[0]
    assert "set_config" in statement
    assert str(a.id) not in statement
    assert list(params.values()) == [str(a.id)] if isinstance(params, dict) else list(params) == [str(a.id)]
    for statement, _ in statements:
        if statement != sql.replace("%", "%%"):
            assert "company_name" not in statement


def test_transaction_settings_are_applied_in_order(two_users, statements):
    a, _ = two_users
    execute_query("SELECT id FROM job", a.id)
    executed = [statement for statement, _ in statements]
    assert executed[0] == "SET TRANSACTION READ ONLY"
    assert executed[1] == "SET LOCAL statement_timeout = 3000"
    assert "set_config" in executed[2]
    assert executed[3] == "SELECT id FROM job"


@pytest.mark.parametrize("value", [0, -3, 1.5, "3", True, None])
def test_invalid_timeout_is_rejected_before_any_statement(two_users, statements, monkeypatch, value):
    a, _ = two_users
    monkeypatch.setattr(settings, "job_search_statement_timeout_seconds", value)
    with pytest.raises(ValueError):
        execute_query("SELECT id FROM job", a.id)
    assert statements == []


@pytest.mark.parametrize("sql", [
    "SELECT 1/0 FROM job",
    "SELECT user_id FROM job",
    "DELETE FROM job",
    "SELEC nonsense",
])
def test_failed_query_leaves_no_user_id_behind(two_users, checkouts, sql):
    a, _ = two_users
    with pytest.raises((QueryExecutionError, QueryPermissionError)):
        execute_query(sql, a.id)

    with get_readonly_engine().connect() as conn:
        rows = conn.exec_driver_sql("SELECT id FROM job").fetchall()
        leftover = conn.exec_driver_sql("SELECT current_setting('app.user_id', true)").scalar()

    assert rows == []
    assert leftover in (None, "")
    assert len(checkouts) == 2
    assert len(set(checkouts)) == 1


def test_timeout_leaves_no_user_id_behind(db, two_users, checkouts, monkeypatch):
    a, _ = two_users
    seed_jobs(db, a.id, 3000)
    monkeypatch.setattr(settings, "job_search_statement_timeout_seconds", 1)
    with pytest.raises(QueryTimeoutError):
        execute_query("SELECT count(*) FROM job a, job b, job c", a.id)

    with get_readonly_engine().connect() as conn:
        rows = conn.exec_driver_sql("SELECT id FROM job").fetchall()
        leftover = conn.exec_driver_sql("SELECT current_setting('app.user_id', true)").scalar()

    assert rows == []
    assert leftover in (None, "")
    assert len(set(checkouts)) == 1
