"""Test setup: a separate Postgres database (job_tracker_test), never the dev one.

The DATABASE_URL env var is swapped BEFORE any `src` import, so the app engine
points at the test database for the whole test run.
"""
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

load_dotenv()  # reads backend/.env (does not override vars that are already set)

TEST_DB_NAME = "job_tracker_test"
BASELINE_REVISION = "8877c8286cd5"  # last migration before the job-search feature

_dev_url = make_url(os.environ["DATABASE_URL"])
_test_url = _dev_url.set(database=TEST_DB_NAME)
TEST_DATABASE_URL = _test_url.render_as_string(hide_password=False)

# Safety: tests may only ever run against a database whose name ends in "_test".
assert _test_url.database.endswith("_test")
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
# The read-only connection must also point at the test DB.
os.environ["READONLY_DATABASE_URL"] = (
    make_url(os.environ["READONLY_DATABASE_URL"]).set(database=TEST_DB_NAME).render_as_string(hide_password=False)
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest  # noqa: E402


def _create_test_database_if_missing():
    admin_url = _dev_url.set(database="postgres")  # maintenance DB, only used for CREATE DATABASE
    admin = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": TEST_DB_NAME}
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    admin.dispose()


@pytest.fixture(scope="session")
def engine():
    """Fresh schema in the test DB, built by running the real Alembic migrations."""
    _create_test_database_if_missing()

    from alembic import command
    from alembic.config import Config

    backend_dir = os.path.join(os.path.dirname(__file__), "..")
    cfg = Config(os.path.join(backend_dir, "alembic.ini"))

    # Start clean so every run is repeatable.
    eng = create_engine(TEST_DATABASE_URL)
    with eng.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    # The old migration history cannot build a DB from zero (the first "internship"
    # table was created outside Alembic). So: build the existing schema from the
    # models, mark it as the last old migration, then run only NEW migrations.
    import src.models  # noqa: F401  (registers all tables)
    from src.database import Base

    Base.metadata.create_all(eng)
    command.stamp(cfg, BASELINE_REVISION)
    command.upgrade(cfg, "head")
    yield eng
    eng.dispose()


@pytest.fixture()
def db(engine):
    """A normal app session. Rows are wiped after each test."""
    from src.database import SessionLocal

    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.execute(text("TRUNCATE users RESTART IDENTITY CASCADE"))
        session.commit()
        session.close()


@pytest.fixture()
def two_users(db):
    """User A and user B, each with their own jobs. Returns (user_a, user_b)."""
    from src.auth.models import User
    from src.jobs.models import ApplicationStatus, Job

    a = User(email="a@example.com", hashed_password="x")
    b = User(email="b@example.com", hashed_password="x")
    db.add_all([a, b])
    db.flush()
    db.add_all([
        Job(company_name="AlphaCorp", position="Backend Intern", location="Cairo",
            status=ApplicationStatus.APPLIED, user_id=a.id),
        Job(company_name="AlphaTwo", position="Data Intern", location="Remote",
            status=ApplicationStatus.SAVED, user_id=a.id),
        Job(company_name="BetaSecret", position="ML Intern", location="Berlin",
            status=ApplicationStatus.INTERVIEW, user_id=b.id),
    ])
    db.commit()
    return a, b
