import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from src.job_search_query.utils import get_readonly_engine

ALLOWED = "id, created_at, company_name, position, location, application_date, deadline, status"


def ro_query(sql: str, user_id=None, params=None):
    """Run SQL as the read-only role in one transaction."""
    with get_readonly_engine().connect() as conn:
        with conn.begin():
            if user_id is not None:
                conn.execute(text("SELECT set_config('app.user_id', :u, true)"), {"u": str(user_id)})
            return conn.execute(text(sql), params or {}).fetchall()


def test_user_a_sees_only_a_rows_without_user_id_grant(two_users):
    a, b = two_users
    rows_a = ro_query(f"SELECT {ALLOWED} FROM job ORDER BY id", user_id=a.id)
    rows_b = ro_query(f"SELECT {ALLOWED} FROM job ORDER BY id", user_id=b.id)
    assert {r.company_name for r in rows_a} == {"AlphaCorp", "AlphaTwo"}
    assert {r.company_name for r in rows_b} == {"BetaSecret"}


INSUFFICIENT_PRIVILEGE = "42501"


def assert_permission_denied(sql: str, user_id):
    with pytest.raises(DBAPIError) as exc:
        ro_query(sql, user_id=user_id)
    assert exc.value.orig.pgcode == INSUFFICIENT_PRIVILEGE, exc.value.orig.pgcode


def test_user_id_is_not_readable(two_users):
    a, _ = two_users
    assert_permission_denied("SELECT user_id FROM job", a.id)


def test_where_clause_for_other_user_returns_nothing(two_users):
    a, _ = two_users
    rows = ro_query("SELECT company_name FROM job WHERE company_name = 'BetaSecret'", user_id=a.id)
    assert len(rows) == 0


def test_missing_user_id_returns_no_rows_not_error(two_users):
    assert ro_query(f"SELECT {ALLOWED} FROM job") == []


def test_empty_user_id_returns_no_rows(two_users):
    assert ro_query(f"SELECT {ALLOWED} FROM job", user_id="") == []


@pytest.mark.parametrize("col", ["job_description", "job_link", "search_vector"])
def test_hidden_columns_denied(two_users, col):
    a, _ = two_users
    assert_permission_denied(f"SELECT {col} FROM job", a.id)


def test_select_star_denied(two_users):
    a, _ = two_users
    assert_permission_denied("SELECT * FROM job", a.id)


@pytest.mark.parametrize("table", ["users", "profile", "skills", "matchresult", "cv_generations", "background_jobs"])
def test_other_tables_denied(two_users, table):
    a, _ = two_users
    assert_permission_denied(f"SELECT 1 FROM {table}", a.id)


@pytest.mark.parametrize("sql", [
    "INSERT INTO job (company_name, position, location, status, user_id) VALUES ('x','x','x','APPLIED',1)",
    "UPDATE job SET company_name = 'hacked'",
    "DELETE FROM job",
    "DROP TABLE job",
])
def test_writes_denied(two_users, sql):
    a, _ = two_users
    with pytest.raises(DBAPIError):
        ro_query(sql, user_id=a.id)


def test_role_cannot_bypass_rls_or_is_superuser(engine):
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT rolsuper, rolbypassrls, rolcreaterole, rolcreatedb FROM pg_roles WHERE rolname='job_search_ro'")
        ).one()
    assert tuple(row) == (False, False, False, False)


def test_timeout_default_is_three_seconds(two_users):
    assert ro_query("SHOW statement_timeout")[0][0] == "3s"


def test_app_connection_still_sees_all_rows(db, two_users):
    assert db.execute(text("SELECT count(*) FROM job")).scalar() == 3
    names = {r[0] for r in db.execute(text("SELECT company_name FROM job"))}
    assert names == {"AlphaCorp", "AlphaTwo", "BetaSecret"}
