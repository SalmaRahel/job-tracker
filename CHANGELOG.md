# Changelog

## [Unreleased]

### Added
- Ask your job search: POST /job-search/ask turns a plain-English question into a checked, read-only SQL query and returns a short answer.
- Read-only Postgres role job_search_ro with column grants and row-level security (run alembic upgrade head).
- Env vars JOB_SEARCH_RO_PASSWORD and READONLY_DATABASE_URL.
- Optional ttl_seconds argument on check_and_set_cooldown (existing callers unchanged).
- docs/job-search-security.md and pytest tests on a separate job_tracker_test database.

### Known issues
- set_config can switch the user at the database level, so the validator is required. See docs/job-search-security.md.
