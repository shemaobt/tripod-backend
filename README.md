# tripod-backend

Shared API backend for Tripod — a platform powering multiple language and translation tools. Handles authentication (JWT), app-scoped RBAC, and core data (languages, projects, organizations, phases).

**Stack:** FastAPI · SQLAlchemy 2 async · Alembic · PostgreSQL (Neon) · uv · Docker · Cloud Run

## Architecture

```
app/
├── api/           # FastAPI routers (auth, languages, orgs, projects, phases, roles, rag, bhsa)
├── core/          # Config, database engine, middleware, exceptions
├── db/
│   └── models/    # SQLAlchemy ORM models (auth · language · org · phase · project)
├── models/        # Pydantic request/response schemas
└── services/      # Business logic, one package per domain:
                   #   auth/ · authorization/ · language/ · org/ · phase/ · project/
                   #   rag/ (document upload, query, embeddings)
                   #   bhsa/ (Hebrew text-fabric passage extraction)
alembic/           # Database migrations
scripts/           # One-off scripts (e.g. seed_apps_roles.py)
tests/             # Async pytest suite, one file per service domain
http/              # .http request examples (VS Code REST Client / JetBrains)
```

Each layer has a single responsibility: routers call services, services use db models, Pydantic models handle serialization. No business logic lives in routers; no DB calls live outside services.

## CI/CD (GitHub Actions)

| Trigger | What happens |
|---|---|
| Pull request | ruff check + ruff format + pytest |
| Push to `main` | Build image → `alembic upgrade head` → deploy to Cloud Run |

Config is pulled from GCP Secret Manager at container startup — no env vars are set manually in production or CI.

## Local development

Secrets are stored in GCP Secret Manager (project `shemaobt-secrets`) and fetched at startup by a Docker Compose sidecar.

### Prerequisites

1. **Install the [gcloud CLI](https://cloud.google.com/sdk/docs/install).**

2. **Request secret access.** Ask a project admin to add you on the project.

3. **Authenticate your local gcloud:**
   ```bash
   gcloud auth login                       # interactive login with the email that was granted access
   gcloud auth application-default login   # sets Application Default Credentials (used by Docker)
   ```

4. **Verify access works** (optional but recommended):
   ```bash
   gcloud secrets versions access latest \
     --secret=tripod_backend_jwt_secret \
     --project=shemaobt-secrets
   ```
   If this prints a value, you're good. If it fails, double-check that step 2 was done for your email and that you logged in with the correct account in step 3.

### Running the stack

```bash
# Start the backend (defaults to project shemaobt-secrets)
SECRETS_PROJECT_ID=shemaobt-secrets docker compose up --build backend

# In another terminal — apply migrations, seed, run tests
docker compose exec backend sh -c "set -a && . /run/secrets/.env && set +a && uv run alembic upgrade head"
docker compose exec backend sh -c "set -a && . /run/secrets/.env && set +a && uv run python scripts/seed_apps_roles.py"
docker compose exec backend sh -c "set -a && . /run/secrets/.env && set +a && uv run pytest tests"
```

> Use a Neon dev branch for local work to avoid touching production data.

### BHSA (Hebrew text data)

BHSA passage extraction requires text-fabric data (~300MB download on first run). Use the `bhsa` Docker profile:

```bash
# Start backend + download BHSA data + auto-load into memory
docker compose --profile bhsa up -d --build

# Check status
curl http://localhost:8000/api/bhsa/status

# Fetch a passage
curl 'http://localhost:8000/api/bhsa/passage?ref=Ruth%201:1-6'
```

The `bhsa-fetcher` sidecar downloads text-fabric data into a shared volume (`tf_data`), then `bhsa-load` triggers the backend to load it into memory. Data persists across restarts via the Docker volume.

## Migrations

```bash
# Create (after changing models)
docker compose exec backend sh -c "set -a && . /run/secrets/.env && set +a && uv run alembic revision --autogenerate -m 'short description'"

# Apply locally (manual — never run automatically against local DB)
docker compose exec backend sh -c "set -a && . /run/secrets/.env && set +a && uv run alembic upgrade head"
```

Production migrations run automatically on deploy (after merge to `main`).

## Lint

```bash
uv run ruff check . --fix
uv run ruff format .
```

Or via Docker: `docker compose --profile lint run --rm lint`

## API examples

[`http/`](http/) contains `.http` request files for health, auth, and roles. See [`http/README.md`](http/README.md) for token usage.
