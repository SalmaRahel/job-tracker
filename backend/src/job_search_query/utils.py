from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from src.config import settings

_readonly_engine: Engine | None = None


def get_readonly_engine() -> Engine:
    """Engine that connects as the job_search_ro Postgres role (SELECT-only, RLS applies).

    Separate from src.database.engine, which the rest of the app uses.
    Created on first use so the app still starts if READONLY_DATABASE_URL is not set.
    """
    global _readonly_engine
    if _readonly_engine is None:
        if not settings.readonly_database_url:
            raise RuntimeError("READONLY_DATABASE_URL is not configured")
        _readonly_engine = create_engine(settings.readonly_database_url, pool_pre_ping=True)
    return _readonly_engine
