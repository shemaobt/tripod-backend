# Backend Agent Guidelines (tripod-backend)

This file defines backend-specific conventions for agents working in this repository. It follows the structure and intent of `reference-agents-md/BACKEND.md`, adapted to FastAPI + SQLAlchemy + Alembic and GCP Secret Manager.

---

## 1. Stack and Runtime

- **Framework**: FastAPI
- **Server**: Uvicorn (dev) / Gunicorn (production)
- **Package manager**: `uv` (`pyproject.toml` + `uv.lock`)
- **Database**: PostgreSQL (Neon) via SQLAlchemy 2 async engine + `asyncpg`
- **Migrations**: Alembic
- **Validation / schemas**: Pydantic v2
- **Auth**: JWT (`python-jose`) + passlib (`pbkdf2_sha256`)

Use these stack choices and existing project patterns. Do not introduce an alternative framework, ORM, or migration tool.

### Package management with uv

- Add dependency: `uv add <package>`
- Add dev dependency: `uv add --dev <package>`
- Sync environment: `uv sync`
- Run commands: `uv run <command>`
- Regenerate lockfile: `uv lock`

---

## 2. Project Structure

```text
tripod-backend/
├── app/
│   ├── main.py
│   ├── api/
│   ├── core/
│   ├── db/models/
│   ├── models/
│   ├── services/
│   └── utils/
├── alembic/
├── scripts/
├── tests/
├── pyproject.toml
├── uv.lock
├── Dockerfile
├── Dockerfile.dev
└── docker-compose.yml
```

### API layer: access only

- `app/api` is an access layer for HTTP only.
- Routers parse/validate input, call services, map expected business exceptions to `HTTPException`.
- Do not put SQLAlchemy queries, business rules, or orchestration logic in routers.

### Services, core, models

- `app/services`: business logic and data access.
- `app/core`: config, DB session management, auth dependencies.
- `app/models`: request/response schemas and typed DTOs.
- `app/db/models`: SQLAlchemy table models only.

---

## 3. API and Error Conventions

- Keep one router per domain area and register in `app/main.py`.
- Protected routes use shared auth dependencies in `app/core/auth_middleware.py`.
- Raise specific exceptions for business cases in services; map them in API layer.
- For infrastructure/unexpected failures, use default framework behavior (avoid over-wrapping all exceptions).

---

## 4. Database and Alembic

- Use injected `AsyncSession` from `get_db`; do not create ad-hoc engines/sessions in routers/services.
- Keep database I/O async (`await session.execute(...)`, `await session.commit()`).
- Every schema change must be reflected in Alembic migration files under `alembic/versions`.
- Do not apply manual schema changes outside Alembic workflow.

---

## 5. Code Style

- Prefer async end-to-end in API and service paths.
- Keep strong typing on public functions (params + return type).
- Prefer explicit typed models over generic `dict` when shape is known.
- Keep services function-oriented and composable.
- Keep public service function docstrings present and concise.
- Keep code self-documenting; avoid comments that restate code.

---

## 6. Runtime Secrets

- Do not rely on committed local `.env` files for runtime secrets.
- Runtime secrets are stored in GCP Secret Manager and loaded in:
  - local Docker Compose via `gcp-secrets` service
  - Cloud Run via `--set-secrets` in deploy workflow
- Required secrets:
  - **Local (docker-compose):** `tripod_backend_neon_database_url_local` (Neon DB for dev/test), `tripod_backend_jwt_secret`
  - **Production (Cloud Run):** `tripod_backend_neon_database_url`, `tripod_backend_jwt_secret`

---

## 7. Docker-only Commands

- Start backend:
  - `SECRETS_PROJECT_ID=<SECRETS_PROJECT_ID> docker compose up --build backend`
- Run migrations:
  - `SECRETS_PROJECT_ID=<SECRETS_PROJECT_ID> docker compose run --rm backend sh -c "set -a && . /run/secrets/.env && set +a && uv run alembic upgrade head"`
- Run tests:
  - `SECRETS_PROJECT_ID=<SECRETS_PROJECT_ID> docker compose run --rm backend sh -c "set -a && . /run/secrets/.env && set +a && uv run pytest tests"`

---

## 8. Summary Checklist

- [ ] Keep `app/api` thin and service-driven.
- [ ] Keep SQLAlchemy usage async and session-injected.
- [ ] Keep schema changes tracked with Alembic migrations.
- [ ] Keep runtime secrets in GCP Secret Manager.
- [ ] Keep backend commands running inside Docker Compose.
- [ ] Keep strong typing and concise service docstrings.
