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

## CI/CD (GitHub Actions)

Workflows: `.github/workflows/ci.yml` (tests and build) and `.github/workflows/deploy.yml` (deploy to EC2).

Repository secrets (Settings > Secrets and variables > Actions):

| Secret | Value |
|---|---|
| `EC2_HOST` | public IP or DNS name of the server |
| `EC2_USER` | SSH user on the server |
| `EC2_SSH_KEY` | full private key (PEM) for that user |

How a deploy runs:

1. A pull request to `main` runs CI: backend `pytest` (Postgres 16, Redis 7) and frontend `tsc --noEmit` plus `npm run build`.
2. A push to `main` runs CI again, then deploys only if it passes.
3. The deploy packs `HEAD` with `git archive`, copies it to `/opt/job-tracker`, extracts it, runs `docker compose -f docker-compose.prod.yml up -d --build api worker web`, restarts `web`, prunes images and shows `ps`.
4. A health check polls `http://EC2_HOST/api/health` for up to 90 seconds and fails the job with the last 40 `api` log lines if it does not return `{"status":"ok"}`.

The archive never contains `.env` or `backend/.env.prod`, and the pipeline never reads or writes them on the server. Only one deploy runs at a time.

Manual deploy: GitHub > Actions > Deploy > Run workflow (branch `main`), or `gh workflow run deploy.yml --ref main`.
