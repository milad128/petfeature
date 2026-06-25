# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

**petfeature.ir** — a personal PM encyclopedia (Product Management). v1 ships a book library and about page. Deployed on [Hamravesh Darkube](https://hamravesh.com/darkube) (Kubernetes PaaS) as a single Docker container with a managed PostgreSQL addon.

## Stack

- **FastAPI** + **Jinja2** — server-rendered HTML (no separate frontend build)
- **SQLAlchemy async** (`asyncpg`) — database access; `Base` lives in `app/core/database.py`
- **Alembic** — migrations; uses a sync URL derived from `DATABASE_URL` (strips `+asyncpg`)
- **Pydantic-settings** — all config read from `.env` via `app/core/config.py`
- Pages are RTL (Persian/Farsi); `page_title` context is always in Persian

## Development commands

```bash
# Setup
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run (hot reload)
uvicorn app.main:app --reload --proxy-headers

# Or via Docker Compose (web + PostgreSQL)
docker compose up --build

# Migrations (once models exist)
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

App runs at http://localhost:8000. Health check: `GET /api/v1/health`.

## Architecture

```
app/
  main.py          # Mounts /static, wires web + admin + api/v1 routers
  core/
    config.py      # Settings singleton (lru_cache); settings.database_url_sync for Alembic
    database.py    # Base, engine, async_session_factory, get_db() dependency
  web/routes.py    # Public SSR pages: /, /library/, /library/{slug}/, /about/
  admin/routes.py  # Admin CMS (stub — auth + CRUD coming)
  api/v1/router.py # REST API (health only; future SPA/integrations)
  models/          # SQLAlchemy ORM models go here; import them in alembic/env.py
  schemas/         # Pydantic request/response schemas
  services/        # Business logic shared by web/, admin/, api/ — keeps routes thin
  templates/       # Jinja2 HTML; base.html + pages/*.html
  static/          # css/main.css, js/
```

**Key pattern:** routes stay thin; business logic goes in `services/`. Web and admin call the same service layer to avoid duplication.

**Adding a model:** define in `app/models/`, import it in `alembic/env.py` (see the commented import block), then run `alembic revision --autogenerate`.

## Build sequence (v1 roadmap)

1. Front pages — templates + static assets
2. Data models (`Book`, `Resource`, `AboutPage`) + Alembic migrations
3. Services — load data for `web/` routes
4. Admin CMS — auth + CRUD in `admin/`
5. Deploy to Hamravesh Darkube

v2 (path, blog, newsletter, community) is tracked in `docs/product-spec-v2.md`.

## Environment variables

| Variable | Notes |
|----------|-------|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host:5432/db` |
| `SECRET_KEY` | Required in production |
| `DEBUG` | `true` locally, `false` in prod |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | When admin CMS is live |
| `PORT` | Default `8000`; Hamravesh may override |

## Deployment (Hamravesh Darkube)

Push to Git → Darkube builds the `Dockerfile` → runs container on K8s. The `CMD` in the Dockerfile uses `${PORT}` and `--proxy-headers` (required behind Hamravesh reverse proxy). Run `alembic upgrade head` as an init container / one-off job before serving traffic.
