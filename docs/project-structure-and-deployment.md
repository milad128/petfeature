# Project Structure & Deployment

> **Maintained doc:** Update this file whenever the project layout, stack, env vars, or Hamravesh deploy steps change.
>
> **Parent:** [Product overview](./product-spec.md)

## Changelog

| Date | Change |
|------|--------|
| 2026-06-24 | Initial structure: FastAPI + Jinja2 + PostgreSQL + Docker; Hamravesh Darkube deploy guide |

---

## 1. Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Language | Python 3.12 | Familiar ecosystem; strong Hamravesh examples |
| Web framework | FastAPI | Fast, async, good for API + SSR |
| Templates | Jinja2 | Server-rendered RTL pages; one container to deploy |
| Database | PostgreSQL | Hamravesh managed addon; async via SQLAlchemy + asyncpg |
| Migrations | Alembic | Safe schema changes on deploy |
| Container | Docker | Required by Hamravesh Darkube |

---

## 2. Directory layout

```
petfeature/
├── Dockerfile                 # Production image for Hamravesh Darkube
├── docker-compose.yml         # Local dev: web + PostgreSQL
├── requirements.txt           # Python dependencies
├── .env.example               # Template for local / Hamravesh env vars
├── alembic.ini                # Alembic config
├── alembic/
│   ├── env.py                 # Migration environment (wired to app settings)
│   ├── script.py.mako         # Migration template
│   └── versions/              # Migration files (empty until models exist)
├── app/
│   ├── main.py                # FastAPI entry point — wires all routers
│   ├── core/
│   │   ├── config.py          # Settings from environment variables
│   │   └── database.py        # SQLAlchemy engine + session
│   ├── web/
│   │   └── routes.py          # Public pages (home, library, about)
│   ├── admin/
│   │   └── routes.py          # Admin CMS (placeholder)
│   ├── api/
│   │   └── v1/
│   │       └── router.py      # REST API (health check; more later)
│   ├── models/                # SQLAlchemy ORM (empty until data layer)
│   ├── schemas/               # Pydantic request/response schemas
│   ├── services/              # Business logic shared by web, admin, API
│   ├── templates/             # Jinja2 HTML (RTL)
│   │   ├── base.html
│   │   └── pages/
│   │       ├── home.html
│   │       ├── library.html
│   │       ├── book_detail.html
│   │       └── about.html
│   └── static/
│       ├── css/main.css
│       └── js/
└── docs/                      # Product specs + this file
```

---

## 3. Routes (current)

| Route | Module | Status |
|-------|--------|--------|
| `/` | `app/web/routes.py` | Placeholder home |
| `/library/` | `app/web/routes.py` | Placeholder book list |
| `/library/{slug}/` | `app/web/routes.py` | Placeholder book detail |
| `/about/` | `app/web/routes.py` | Placeholder about page |
| `/admin/` | `app/admin/routes.py` | Stub — CMS coming next |
| `/api/v1/health` | `app/api/v1/router.py` | Health check for deploy |
| `/static/*` | `app/main.py` | CSS, JS, images |

---

## 4. Why this structure?

### Hamravesh Darkube compatibility

[Hamravesh Darkube](https://hamravesh.com/darkube) is a Kubernetes-based PaaS. You connect a Git repo; it builds a **Docker image** and runs it. Managed **PostgreSQL** is a separate addon connected via env vars.

This layout matches that model:

1. **One Dockerfile** → one deployable unit
2. **Config from env vars** → no secrets in code; same image for dev and prod
3. **PostgreSQL as external service** → stateless app container
4. **`--proxy-headers`** on Uvicorn → correct behavior behind Hamravesh reverse proxy (HTTPS, domain)

### Layered folders = build order

| Phase | Folder | Purpose |
|-------|--------|---------|
| **1 (now)** | `web/` + `templates/` + `static/` | Public front pages |
| **2 (next)** | `admin/` | CMS for books and about content |
| **3** | `models/` + `alembic/versions/` | Data model + migrations |
| **4** | `services/` | Business logic shared across layers |
| **5 (optional)** | `api/v1/` | JSON API for future SPA or integrations |

Routes stay thin; logic lives in `services/` so web and admin do not duplicate code.

### FastAPI + Jinja2 (not a separate React app)

For v1 (library + about), server-rendered HTML means **one container** — no second frontend build step. An API layer can be added later without rewriting the site.

---

## 5. Environment variables

Copy `.env.example` to `.env` for local development.

| Variable | Required | Description |
|----------|----------|-------------|
| `APP_NAME` | No | App label (default: `petfeature`) |
| `DEBUG` | No | `true` locally; `false` in production |
| `SECRET_KEY` | Yes (prod) | Random string for sessions/signing |
| `PORT` | No | Server port (default: `8000`; Hamravesh may set this) |
| `DATABASE_URL` | Yes (when DB used) | `postgresql+asyncpg://user:pass@host:5432/db` |
| `ADMIN_USERNAME` | Yes (when admin live) | CMS login username |
| `ADMIN_PASSWORD` | Yes (when admin live) | CMS login password |

**Note:** Alembic uses a sync URL derived from `DATABASE_URL` (replaces `+asyncpg` with nothing).

---

## 6. Local development

### Option A — Python virtualenv

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --proxy-headers
```

Open http://localhost:8000

### Option B — Docker Compose (web + PostgreSQL)

```bash
cp .env.example .env
docker compose up --build
```

- App: http://localhost:8000
- PostgreSQL: `localhost:5432` (user/pass/db: `petfeature`)

### Database migrations (after models exist)

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

---

## 7. Deploy to Hamravesh (Darkube)

### Deployment flow

```mermaid
flowchart LR
  Git[Git push] --> Darkube[Hamravesh Darkube]
  Darkube --> Build[Docker build]
  Build --> Image[Container on K8s]
  PG[(PostgreSQL addon)] --> Image
  Image --> Domain[petfeature.ir]
```

### Step 1 — Create PostgreSQL

In the Darkube panel, create a **PostgreSQL** app. Copy the connection URL.

Convert for this app if needed:

```
postgresql+asyncpg://USER:PASSWORD@HOST:5432/DATABASE
```

### Step 2 — Create a Git-repo app

| Darkube setting | Value |
|-----------------|--------|
| Source | Git repo (GitHub / Hamgit / GitLab) |
| Build context | `.` |
| Dockerfile path | `Dockerfile` |
| Service port | `8000` |
| Execute command | `uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers` |

The `Dockerfile` `CMD` already runs the same command; the panel setting can override it.

### Step 3 — Set environment variables

In the app panel, add at minimum:

| Variable | Production value |
|----------|------------------|
| `DATABASE_URL` | From PostgreSQL addon |
| `SECRET_KEY` | Long random string |
| `DEBUG` | `false` |
| `ADMIN_USERNAME` | Your admin user |
| `ADMIN_PASSWORD` | Strong password |

### Step 4 — Run migrations on deploy

After models and migrations exist, run before serving traffic:

```bash
alembic upgrade head
```

Options on Hamravesh:

- One-off job / init container in the deploy pipeline
- Manual run via kubectl or a temporary shell (if available)

### Step 5 — Domain & SSL

Attach your domain (`petfeature.ir`) or a `darkube.app` subdomain in the panel. SSL is handled by Hamravesh.

---

## 8. Dockerfile reference

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .
EXPOSE 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers
```

---

## 9. Planned build sequence

Aligned with [Product Spec v1](./product-spec-v1.md):

1. **Front pages** — design and content in `templates/` and `static/`
2. **Data model** — `Book`, `Resource`, `AboutPage` in `models/`; Alembic migrations
3. **Services** — `services/` loads data for `web/` routes
4. **Admin CMS** — auth + CRUD in `admin/` for books and about content
5. **Deploy** — push to Git; configure Darkube app + PostgreSQL

v2 features (path, blog, newsletter, community) are in [Product Spec v2](./product-spec-v2.md).

---

## 10. Related docs

| Doc | Purpose |
|-----|---------|
| [product-spec.md](./product-spec.md) | Product overview and version roadmap |
| [product-spec-v1.md](./product-spec-v1.md) | v1 scope: library + about |
| [product-spec-v2.md](./product-spec-v2.md) | v2 scope: full site + community |
| [use-case-diagram.md](./use-case-diagram.md) | UML use cases |

---

*Last updated: 2026-06-24*
