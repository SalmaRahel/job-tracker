import pytest

from src.job_search_query.validator import UnsafeSQLError, validate_sql



def test_two_week_followup_question_with_interval():
    sql = (
        "SELECT company_name, position, application_date FROM job "
        "WHERE status = 'APPLIED' AND application_date < current_date - interval '14 days' "
        "ORDER BY application_date"
    )
    out = validate_sql(sql)
    assert "INTERVAL '14 DAYS'" in out.upper()
    assert out.upper().endswith("LIMIT 50")


@pytest.mark.parametrize("sql", [
    "SELECT status, count(*) AS n FROM job GROUP BY status ORDER BY n DESC",
    "SELECT count(*) FROM job",
    "SELECT lower(company_name) AS c FROM job GROUP BY c ORDER BY c",
    "SELECT id FROM job WHERE created_at >= now() - interval '7 days'",
    "SELECT extract(year from created_at) AS y, count(id) FROM job GROUP BY y",
    "SELECT date_trunc('month', created_at) AS m, count(*) FROM job GROUP BY m ORDER BY m",
    "SELECT created_at::date, cast(id AS text) FROM job",
    "SELECT company_name FROM job WHERE company_name ILIKE '%tech%' AND (status = 'OFFER' OR deadline IS NULL)",
    "SELECT CASE WHEN status = 'OFFER' THEN 1 ELSE 0 END AS won FROM job",
    "SELECT j.company_name FROM job j WHERE j.id = 1",
    "SELECT id FROM job WHERE id IN (SELECT id FROM job WHERE status = 'OFFER')",
    "SELECT company_name FROM job WHERE status = 'APPLIED';",
    "SELECT 'a--b' AS x FROM job",
])
def test_good_queries_pass(sql):
    assert validate_sql(sql).upper().startswith("SELECT")



@pytest.mark.parametrize("sql", [
    "'; DROP TABLE jobs; --",
    "SELECT id FROM job; DROP TABLE job",
    "SELECT id FROM job;;",
    "DELETE FROM job",
    "UPDATE job SET status = 'OFFER'",
    "INSERT INTO job (company_name) VALUES ('x')",
    "DROP TABLE job",
    "TRUNCATE job",
    "SET ROLE postgres",
    "SELECT id FROM job -- sneaky",
    "SELECT id /* sneaky */ FROM job",
    "SELECT email FROM users",
    "SELECT id FROM job WHERE id IN (SELECT id FROM users)",
    "SELECT * FROM job",
    "SELECT job.* FROM job",
    "SELECT user_id FROM job",
    "SELECT job_description FROM job",
    "SELECT job_link FROM job",
    "SELECT search_vector FROM job",
    "SELECT j.user_id FROM job j",
    "SELECT pg_sleep(10)",
    "SELECT id FROM job WHERE pg_sleep(10) IS NULL",
    "SELECT current_setting('app.user_id')",
    "SELECT set_config('app.user_id', '2', false)",
    "SELECT id FROM generate_series(1, 100000000) id",
    "SELECT id FROM pg_catalog.pg_user",
    "SELECT id FROM information_schema.tables",
    "SELECT id FROM public.job",
    "SELECT id FROM job UNION SELECT id FROM job",
    "WITH a AS (SELECT id FROM job) SELECT id FROM a",
    "SELECT id INTO newtable FROM job",
    "SELECT id FROM job FOR UPDATE",
    "SELECT id FROM job WHERE id = $1",
    "SELECT id FROM job WHERE id = :x",
    "SELECT id::regclass FROM job",
    'SELECT "id" FROM job',
    "SELECT id FROM job j JOIN users u ON u.id = j.user_id",
    "SELECT users.email FROM job",
    "SELECT id FROM job WHERE interval id > interval '1 day'",
    "this is not sql",
    "",
    "   ",
    "SELECT id FROM job WHERE " + " OR ".join(["id = 1"] * 400),
])
def test_bad_sql_is_rejected(sql):
    with pytest.raises(UnsafeSQLError):
        validate_sql(sql)



@pytest.mark.parametrize("sql", [
    "SELECT md5(company_name) FROM job",
    "SELECT concat(company_name, position) FROM job",
    "SELECT substring(company_name, 1, 3) FROM job",
    "SELECT abs(id) FROM job",
    "SELECT random() FROM job",
    "SELECT unnest(ARRAY[1,2]) FROM job",
])
def test_known_but_unlisted_functions_rejected(sql):
    with pytest.raises(UnsafeSQLError, match="function not allowed"):
        validate_sql(sql)



def test_alias_allowed_in_order_by():
    assert "ORDER BY n" in validate_sql("SELECT status, count(*) AS n FROM job GROUP BY status ORDER BY n")


@pytest.mark.parametrize("sql", [
    "SELECT count(*) AS n FROM job WHERE n > 1",
    "SELECT status AS s FROM job WHERE s = 'OFFER'",
    "SELECT id AS x FROM job ORDER BY x + 1",
    "SELECT status, count(*) AS n FROM job GROUP BY status HAVING n > 1",
])
def test_alias_not_allowed_outside_order_or_group(sql):
    with pytest.raises(UnsafeSQLError, match="column not allowed"):
        validate_sql(sql)


@pytest.mark.parametrize("sql", [
    "SELECT id AS user_id FROM job WHERE user_id = 1",
    "SELECT id AS user_id FROM job ORDER BY user_id",
    "SELECT status AS user_id, count(*) FROM job GROUP BY user_id",
    "SELECT company_name AS job_description FROM job",
])
def test_alias_named_like_hidden_column_rejected(sql):
    with pytest.raises(UnsafeSQLError):
        validate_sql(sql)



def test_limit_added_when_missing():
    assert validate_sql("SELECT id FROM job").upper().endswith("LIMIT 50")


def test_small_limit_kept():
    assert validate_sql("SELECT id FROM job LIMIT 5").upper().endswith("LIMIT 5")


@pytest.mark.parametrize("sql", [
    "SELECT id FROM job LIMIT 100000",
    "SELECT id FROM job LIMIT ALL",
    "SELECT id FROM job LIMIT -1",
])
def test_big_or_odd_limit_capped(sql):
    assert validate_sql(sql).upper().endswith("LIMIT 50")


def test_custom_max_rows():
    assert validate_sql("SELECT id FROM job", max_rows=10).upper().endswith("LIMIT 10")


def test_returned_sql_is_regenerated_not_original():
    out = validate_sql("select   id   from   job")
    assert out == "SELECT id FROM job LIMIT 50"
