# Running the production stack locally

Services: postgres, redis, migrate (one-shot), api, worker, web (nginx). Only `web` publishes a port (80).

## First-time setup

    cp .env.example .env
    cp backend/.env.prod.example backend/.env.prod

Generate URL-safe secrets (letters and digits only):

    python -c "import secrets; print(secrets.token_hex(16))"

Values that must match:

| root `.env` | `backend/.env.prod` |
|---|---|
| `POSTGRES_USER` | user in `DATABASE_URL` |
| `POSTGRES_PASSWORD` | password in `DATABASE_URL` |
| `POSTGRES_DB` | database name in `DATABASE_URL` and `READONLY_DATABASE_URL` |
| | `JOB_SEARCH_RO_PASSWORD` = password in `READONLY_DATABASE_URL` |

The migration creates the `job_search_ro` role with `JOB_SEARCH_RO_PASSWORD`; the Ask feature logs in with `READONLY_DATABASE_URL`. `READONLY_DATABASE_URL` must keep the user `job_search_ro`, otherwise row level security is bypassed.

Also set `GEMINI_API_KEY` and `BUCKET_NAME`. There are no AWS keys: on EC2 the IAM role is used. Locally CV generation fails at the S3 step.

`VITE_API_URL` is baked into the frontend at build time. Local value: `http://localhost/api`.

## Commands

Build:

    docker compose -f docker-compose.prod.yml build

Run:

    docker compose -f docker-compose.prod.yml up -d

Status:

    docker compose -f docker-compose.prod.yml ps -a

Logs:

    docker compose -f docker-compose.prod.yml logs -f api worker
    docker compose -f docker-compose.prod.yml logs migrate

Stop (keeps data):

    docker compose -f docker-compose.prod.yml down

Reset (deletes the database and Redis data):

    docker compose -f docker-compose.prod.yml down -v

Open http://localhost and check http://localhost/api/health.

## Migrations

`migrate` runs `python -m scripts.migrate` on every `up`. On an empty database it builds the schema from the models, stamps revision `8877c8286cd5`, then runs `alembic upgrade head`. On an existing database it only runs `alembic upgrade head`. It is safe to run repeatedly.
