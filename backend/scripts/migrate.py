import os

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

import src.models  # noqa: F401
from src.database import Base

BASELINE_REVISION = "8877c8286cd5"


def main() -> None:
    config = Config("alembic.ini")
    engine = create_engine(os.environ["DATABASE_URL"])
    fresh = "alembic_version" not in inspect(engine).get_table_names()
    if fresh:
        Base.metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_search_vector ON job USING GIN (search_vector)"))
        command.stamp(config, BASELINE_REVISION)
    engine.dispose()
    command.upgrade(config, "head")


if __name__ == "__main__":
    main()
