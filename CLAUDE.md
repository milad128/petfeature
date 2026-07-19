# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

**petfeature.ir** — a personal PM encyclopedia (Product Management). **v1–v8 are all shipped.** Deployed on [Hamravesh Darkube](https://hamravesh.com/darkube) (Kubernetes PaaS) as a single Docker container with a managed PostgreSQL addon.

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
    visitor.py     # Visitor token for ratings/comments dedup
    jalali.py      # Jalali date formatting
    rate_limit.py  # Comment rate limiting
  web/routes.py    # Public SSR: /, /library/, /blog/, /tools/, /about/, /contact/
  admin/routes.py  # Admin CMS: books, categories, posts, comments, tools, about, contact, analytics
  api/v1/router.py # REST API (health only; future SPA/integrations)
  models/          # Book, Category, AboutPage, Post, PostRating, PostComment, Tool, ToolFile, ContactMessage, PageView
  schemas/         # Pydantic request/response schemas
  services/        # Business logic shared by web/, admin/, api/ — keeps routes thin
  templates/       # Jinja2 HTML; base.html + pages/*.html + admin/*
  static/          # css/, js/, uploads/ (covers, downloads, post-covers, tool-covers, tool-files)
```

**Key pattern:** routes stay thin; business logic goes in `services/`. Web and admin call the same service layer to avoid duplication.

**Adding a model:** define in `app/models/`, import it in `alembic/env.py` (see the commented import block), then run `alembic revision --autogenerate`.

## Build sequence

| Version | Epic | Status |
|---------|------|--------|
| v1 | Library + About + admin CMS | **Shipped** |
| v2 | Blog (posts, ratings, comments, sharing) | **Shipped** |
| v3 | Tools (template library) | **Shipped** |
| v4 | Book Engagement (star ratings + comments on books) | **Shipped** |
| v5 | About Redesign + Contact (jobs/camps CMS, contact form + admin inbox) | **Shipped** |
| v6 | Visitor Analytics (PageView log, bot filtering, admin dashboard) | **Shipped** |
| v7 | Post & Book Comment Replies (admin richtext reply, public display) | **Shipped** |
| v8 | Content Enhancements (book website links, post related books, tool link downloads) | **Shipped** |
| v9 | Media Library (admin file manager + URL copy) + Book link types article/book | **Planned** |
| Backlog | Newsletter, Roadmap | Unscheduled — see `docs/product backlog.md` |

Product specs: `docs/product-spec.md` (index), `docs/product-spec-v1.md` through `docs/product-spec-v8.md`.

## Environment variables

| Variable | Notes |
|----------|-------|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host:5432/db` |
| `SECRET_KEY` | Required in production |
| `DEBUG` | `true` locally, `false` in prod |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Admin CMS login |
| `PORT` | Default `8000`; Hamravesh may override |

## Deployment (Hamravesh Darkube)

Push to Git → Darkube builds the `Dockerfile` → runs container on K8s. The `CMD` in the Dockerfile uses `${PORT}` and `--proxy-headers` (required behind Hamravesh reverse proxy). Run `alembic upgrade head` as an init container / one-off job before serving traffic.
