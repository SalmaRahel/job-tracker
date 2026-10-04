# src/models.py
"""Import every model module so SQLAlchemy registers all tables at startup."""

import src.auth.models  # noqa: F401
import src.jobs.models  # noqa: F401
import src.profile.models  # noqa: F401
import src.matching.models  # noqa: F401
import src.cv_generation.models  # noqa: F401
import src.background_jobs.models  # noqa: F401