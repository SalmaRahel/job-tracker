"""add read-only role and row level security for job search

Revision ID: a1f3c9d2b7e4
Revises: 8877c8286cd5
"""
import os
from alembic import op
import sqlalchemy as sa

revision = "a1f3c9d2b7e4"
down_revision = "8877c8286cd5"
branch_labels = None
depends_on = None

ROLE = "job_search_ro"
# Only these columns of "job" can ever be read by the job-search feature.
# NOT granted: job_description, job_link, search_vector.
ALLOWED_COLUMNS = "id, created_at, company_name, position, location, application_date, deadline, status"


def upgrade() -> None:
    password = os.getenv("JOB_SEARCH_RO_PASSWORD")
    if not password:
        raise RuntimeError("JOB_SEARCH_RO_PASSWORD must be set in the environment (.env)")

    bind = op.get_bind()

    # 1. Create the role only if it does not exist yet (safe to run twice).
    #    format(%L) quotes the password safely, so no hardcoding or injection.
    exists = bind.execute(sa.text("SELECT 1 FROM pg_roles WHERE rolname = :r"), {"r": ROLE}).scalar()
    verb = "ALTER" if exists else "CREATE"
    stmt = bind.execute(
        sa.text(f"SELECT format('{verb} ROLE %I LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS PASSWORD %L', CAST(:r AS text), CAST(:p AS text))"),
        {"r": ROLE, "p": password},
    ).scalar()
    op.execute(sa.text(stmt.replace(":", "\\:")))

    # 2. Safety defaults that follow this role everywhere it connects.
    op.execute(f"ALTER ROLE {ROLE} SET default_transaction_read_only = on")
    op.execute(f"ALTER ROLE {ROLE} SET statement_timeout = '3s'")

    # 3. Minimal access: connect + see the schema + SELECT on allowed columns only.
    db_name = bind.execute(sa.text("SELECT current_database()")).scalar()
    op.execute(f'GRANT CONNECT ON DATABASE "{db_name}" TO {ROLE}')
    op.execute(f"GRANT USAGE ON SCHEMA public TO {ROLE}")
    op.execute(f"REVOKE ALL ON ALL TABLES IN SCHEMA public FROM {ROLE}")
    op.execute(f"GRANT SELECT ({ALLOWED_COLUMNS}) ON job TO {ROLE}")

    # 4. Row-Level Security. ENABLE only (NOT FORCE): the table owner / normal app
    #    connection is not affected. The policy applies only to the read-only role.
    #    current_setting(..., true) returns NULL when unset -> no rows, no error.
    #    NULLIF handles the empty-string case.
    op.execute("ALTER TABLE job ENABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS job_search_own_rows ON job")
    op.execute(
        f"""CREATE POLICY job_search_own_rows ON job
            FOR SELECT TO {ROLE}
            USING (user_id = NULLIF(current_setting('app.user_id', true), '')::int)"""
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS job_search_own_rows ON job")
    op.execute("ALTER TABLE job DISABLE ROW LEVEL SECURITY")
    op.execute(f"DROP OWNED BY {ROLE}")
    op.execute(f"DROP ROLE IF EXISTS {ROLE}")
