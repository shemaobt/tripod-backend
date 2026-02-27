# tripod-backend

Shared API backend for Tripod: a platform that powers multiple language and translation tools. This service handles authentication (signup, login, JWT), app-scoped roles (RBAC), and core data such as languages, projects, and organizations. Frontend apps (e.g. Tripod Studio) call this API and rely on it for identity and access control.

**Stack:** FastAPI, SQLAlchemy 2 (async + asyncpg), Alembic, PostgreSQL (Neon), uv, Docker, Cloud Run.

## CI/CD (GitHub Actions)

Deploys to Cloud Run on push to `main`. Set these repository secrets (Settings → Secrets and variables → Actions):

| Secret | Purpose |
|--------|---------|
| `GCP_PROJECT_ID` | Cloud Run and Artifact Registry project |
| `GCP_SA_KEY` | Service account JSON (Cloud Run Admin, Artifact Registry Writer, Secret Manager Secret Accessor) |
| `SECRETS_PROJECT_NUMBER` | Project *number* for the project holding Secret Manager secrets (`tripod_backend_neon_database_url`, `tripod_backend_jwt_secret`) |

The workflow fails with a clear error if any secret is missing.

## Local setup (GCP Secret Manager)

Secrets are loaded from GCP Secret Manager (same pattern as production).

1. **Authenticate:** `gcloud auth application-default login`

2. **Create/update secrets** in the secrets project (e.g. `shemaobt-secrets`):

   **Neon DB (local):** use a dev branch to avoid touching production.

   ```bash
   printf '%s' '<YOUR_NEON_DATABASE_URL>' | gcloud secrets create tripod_backend_neon_database_url_local --data-file=- --project <SECRETS_PROJECT_ID>
   # Or add a new version if it exists:
   printf '%s' '<YOUR_NEON_DATABASE_URL>' | gcloud secrets versions add tripod_backend_neon_database_url_local --data-file=- --project <SECRETS_PROJECT_ID>
   ```

   **JWT secret:**

   ```bash
   printf '%s' '<JWT_SECRET>' | gcloud secrets create tripod_backend_jwt_secret --data-file=- --project <SECRETS_PROJECT_ID>
   # Or: gcloud secrets versions add tripod_backend_jwt_secret --data-file=- ...
   ```

   **Production Neon URL** (for Cloud Run): create/update `tripod_backend_neon_database_url` in the same project.

3. **Start the backend:** `SECRETS_PROJECT_ID=<ID> docker compose up --build backend`

   `SECRETS_PROJECT_ID` is only used when the stack starts: the `gcp-secrets` container reads it and fetches `DATABASE_URL` and `JWT_SECRET_KEY` from that GCP project into a shared volume. The backend then loads them at startup. You don’t need it for one-off commands.

4. **Migrations, seed, tests** — with the backend running, in another terminal:

   ```bash
   docker compose exec backend sh -c "set -a && . /run/secrets/.env && set +a && uv run alembic upgrade head"
   docker compose exec backend sh -c "set -a && . /run/secrets/.env && set +a && uv run python scripts/seed_apps_roles.py"
   docker compose exec backend sh -c "set -a && . /run/secrets/.env && set +a && uv run pytest tests"
   ```

   The `set -a && . /run/secrets/.env && set +a` loads the same env file the backend uses (from the volume) into the shell before running the command. If you prefer not to have the backend running, use `SECRETS_PROJECT_ID=<ID> docker compose run --rm backend sh -c "..."` so `gcp-secrets` can run first and fill the volume.

## Lint (Ruff)

`docker compose --profile lint run --rm lint` runs `ruff check` and `ruff format --check`. To fix locally: `uv run ruff check . --fix` and `uv run ruff format .`.

## API examples (.http)

[`http/`](http/) contains request examples (health, auth, roles). Use with VS Code REST Client or JetBrains HTTP Client. See `http/README.md` for layout and token usage.
