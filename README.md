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

## CI/CD (GitHub Actions)

Deploys to Cloud Run on push to `main`. Configure these **repository secrets** (Settings → Secrets and variables → Actions):

| Secret | Description |
|--------|-------------|
| `GCP_PROJECT_ID` | GCP project ID where Cloud Run and Artifact Registry run |
| `GCP_SA_KEY` | Full JSON key of a service account with Cloud Run Admin, Artifact Registry Writer, and Secret Manager Secret Accessor |
| `SECRETS_PROJECT_NUMBER` | Project *number* (not ID) of the project that holds Secret Manager secrets (`tripod_backend_neon_database_url`, `tripod_backend_jwt_secret`) |

If any of these are missing, the workflow fails at "Check required secrets" with an error naming the missing one.

## Local setup (GCP Secret Manager)

Local dev uses the same pattern as production: secrets come from GCP Secret Manager.

1. Authenticate with GCP:

```bash
gcloud auth application-default login
```

2. Create or update secrets in GCP Secret Manager (project: `SECRETS_PROJECT_ID`, e.g. `shemaobt-secrets`).

   **Neon DB URL for local** (use a dev/test branch so production is unaffected):

```bash
printf '%s' '<YOUR_NEON_DATABASE_URL>' | gcloud secrets create tripod_backend_neon_database_url_local --data-file=- --project <SECRETS_PROJECT_ID>
# If the secret exists, add a new version:
printf '%s' '<YOUR_NEON_DATABASE_URL>' | gcloud secrets versions add tripod_backend_neon_database_url_local --data-file=- --project <SECRETS_PROJECT_ID>
```

   **JWT secret** (shared by local and CI; create once):

```bash
printf '%s' '<JWT_SECRET>' | gcloud secrets create tripod_backend_jwt_secret --data-file=- --project <SECRETS_PROJECT_ID>
# If the secret exists:
printf '%s' '<JWT_SECRET>' | gcloud secrets versions add tripod_backend_jwt_secret --data-file=- --project <SECRETS_PROJECT_ID>
```

   **Production Neon URL** (used by Cloud Run deploy):

```bash
printf '%s' '<PRODUCTION_NEON_DATABASE_URL>' | gcloud secrets create tripod_backend_neon_database_url --data-file=- --project <SECRETS_PROJECT_ID>
```

3. Start the backend (secrets are fetched into a volume and loaded at startup):

```bash
SECRETS_PROJECT_ID=<SECRETS_PROJECT_ID> docker compose up --build backend
```

4. Run migrations, seed, or tests (same env is loaded from the secrets volume):

```bash
SECRETS_PROJECT_ID=<SECRETS_PROJECT_ID> docker compose run --rm backend sh -c "set -a && . /run/secrets/.env && set +a && uv run alembic upgrade head"
SECRETS_PROJECT_ID=<SECRETS_PROJECT_ID> docker compose run --rm backend sh -c "set -a && . /run/secrets/.env && set +a && uv run python scripts/seed_apps_roles.py"
SECRETS_PROJECT_ID=<SECRETS_PROJECT_ID> docker compose run --rm backend sh -c "set -a && . /run/secrets/.env && set +a && uv run pytest tests"
```
