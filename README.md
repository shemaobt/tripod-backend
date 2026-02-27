# tripod-backend

Shared backend platform for Tripod systems using FastAPI, SQLAlchemy async, Alembic, JWT auth, and app-scoped RBAC.

## Stack

- FastAPI
- SQLAlchemy 2.0 async + asyncpg
- Alembic
- PostgreSQL (Neon)
- uv package management
- Docker + docker-compose
- Cloud Run deploy (GCP)

## Local setup

1. Ensure GCP auth is configured locally:

```bash
gcloud auth application-default login
```

2. Register backend secrets in GCP Secret Manager.

   **Local runs (docker-compose)** use a dedicated Neon DB secret so you can point at a test/dev database without affecting production:

```bash
printf '%s' '<YOUR_NEON_DATABASE_URL>' | gcloud secrets create tripod_backend_neon_database_url_local --data-file=- --project <SECRETS_PROJECT_ID>
```

   If the secret already exists, add a new version:

```bash
printf '%s' '<YOUR_NEON_DATABASE_URL>' | gcloud secrets versions add tripod_backend_neon_database_url_local --data-file=- --project <SECRETS_PROJECT_ID>
```

   **JWT secret** (used both locally and in CI; create once):

```bash
printf '%s' '<JWT_SECRET>' | gcloud secrets create tripod_backend_jwt_secret --data-file=- --project <SECRETS_PROJECT_ID>
```

   **Production (Cloud Run)** uses a separate DB secret. Configure it in the same project (or the one used in deploy workflow):

```bash
printf '%s' '<PRODUCTION_NEON_DATABASE_URL>' | gcloud secrets create tripod_backend_neon_database_url --data-file=- --project <SECRETS_PROJECT_ID>
```

   Use `gcloud secrets versions add ...` instead of `create` if the secret already exists.

3. Start backend with docker compose:

```bash
SECRETS_PROJECT_ID=<SECRETS_PROJECT_ID> docker compose up --build backend
```

4. Run migrations and seed roles:

```bash
SECRETS_PROJECT_ID=<SECRETS_PROJECT_ID> docker compose run --rm backend sh -c "set -a && . /run/secrets/.env && set +a && uv run alembic upgrade head"
SECRETS_PROJECT_ID=<SECRETS_PROJECT_ID> docker compose run --rm backend sh -c "set -a && . /run/secrets/.env && set +a && uv run python scripts/seed_apps_roles.py"
```

5. Run tests:

```bash
SECRETS_PROJECT_ID=<SECRETS_PROJECT_ID> docker compose run --rm backend sh -c "set -a && . /run/secrets/.env && set +a && uv run pytest tests"
```
