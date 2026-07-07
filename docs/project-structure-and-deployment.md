# Project Structure & Deployment

> **Maintained doc:** Update this file whenever the project layout, stack, env vars, or Hamravesh deploy steps change.
>
> **Parent:** [Product overview](./product-spec.md)

## Changelog

| Date | Change |
|------|--------|
| 2026-07-06 | Updated to reflect shipped v1: full models, admin CMS, upload service, category management |
| 2026-06-24 | Initial structure: FastAPI + Jinja2 + PostgreSQL + Docker; Hamravesh Darkube deploy guide |

---

## 1. Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Language | Python 3.12 | Familiar ecosystem; strong Hamravesh examples |
| Web framework | FastAPI | Fast, async, good for API + SSR |
| Templates | Jinja2 | Server-rendered RTL pages; one container to deploy |
| Database | PostgreSQL | Hamravesh managed addon; async via SQLAlchemy + asyncpg |
| ORM | SQLAlchemy async (`asyncpg`) | Async-native; works well with FastAPI |
| Migrations | Alembic | Safe schema changes on deploy |
| Config | Pydantic-settings | `.env`-based; same image dev and prod |
| Container | Docker | Required by Hamravesh Darkube |
| File storage | Local filesystem | Covers + PDFs in `static/uploads/` |

---

## 2. Directory layout

```
petfeature/
├── Dockerfile                          # Production image for Hamravesh Darkube
├── docker-compose.yml                  # Local dev: web + PostgreSQL
├── requirements.txt                    # Python dependencies
├── .env.example                        # Template for local / Hamravesh env vars
├── alembic.ini                         # Alembic config
├── alembic/
│   ├── env.py                          # Migration environment (wired to app settings)
│   ├── script.py.mako                  # Migration template
│   └── versions/                       # Generated migration files
├── app/
│   ├── main.py                         # FastAPI entry point — wires all routers
│   ├── core/
│   │   ├── config.py                   # Settings singleton (lru_cache)
│   │   ├── database.py                 # Base, engine, async_session_factory, get_db()
│   │   ├── sqlite_migrations.py        # SQLite migration helper (local dev only)
│   │   └── templates.py               # Jinja2 template environment setup
│   ├── web/
│   │   └── routes.py                   # Public pages: /, /library/, /library/{slug}/, /about/
│   ├── admin/
│   │   ├── auth.py                     # Session-based admin authentication
│   │   └── routes.py                   # Admin CMS: books, categories, about
│   ├── api/
│   │   └── v1/
│   │       └── router.py               # REST API (health check)
│   ├── models/
│   │   ├── book.py                     # Book, BookMediaLink, book_references, book_categories
│   │   ├── category.py                 # Category, book_categories join table
│   │   └── about.py                    # AboutPage (singleton)
│   ├── schemas/
│   │   ├── book.py                     # BookForm, MediaLinkInput
│   │   ├── category.py                 # CategoryForm
│   │   └── about.py                    # AboutForm, LinkInput
│   ├── services/
│   │   ├── books.py                    # Book CRUD, list, slug lookup, JSON parsers
│   │   ├── categories.py               # Category CRUD, list
│   │   ├── about.py                    # AboutPage get/update
│   │   └── uploads.py                  # Cover and PDF upload resolution
│   ├── templates/
│   │   ├── base.html                   # Public layout (RTL, nav, footer)
│   │   ├── pages/
│   │   │   ├── home.html
│   │   │   ├── library.html            # Grid + category filter
│   │   │   ├── book_detail.html        # Full book detail
│   │   │   └── about.html
│   │   ├── admin/
│   │   │   ├── base.html               # Admin layout
│   │   │   ├── login.html
│   │   │   ├── books_list.html
│   │   │   ├── book_form.html          # Create/edit book (all fields)
│   │   │   ├── categories_list.html
│   │   │   ├── category_form.html
│   │   │   └── about_form.html
│   │   └── partials/
│   │       └── note_fonts.html
│   └── static/
│       ├── css/
│       │   ├── main.css                # Public site styles
│       │   └── admin.css               # Admin panel styles
│       ├── js/
│       │   ├── library.js              # Client-side category filtering
│       │   └── admin.js                # Admin form JS (dynamic fields)
│       └── uploads/
│           ├── covers/                 # Uploaded book cover images
│           └── downloads/              # Uploaded book PDF files
└── docs/                               # Product specs + this file
```

---

## 3. Routes (v1 — shipped)

| Route | Module | Description |
|-------|--------|-------------|
| `GET /` | `app/web/routes.py` | Home page |
| `GET /library/` | `app/web/routes.py` | Book list (published + show_in_library only) |
| `GET /library/{slug}/` | `app/web/routes.py` | Book detail (published only) |
| `GET /about/` | `app/web/routes.py` | About page |
| `GET /admin/` | `app/admin/routes.py` | Redirects to /admin/books/ |
| `GET /admin/login/` | `app/admin/routes.py` | Admin login form |
| `POST /admin/login/` | `app/admin/routes.py` | Admin login submit |
| `GET /admin/logout/` | `app/admin/routes.py` | Admin logout |
| `GET /admin/books/` | `app/admin/routes.py` | Books list (all statuses, searchable) |
| `GET /admin/books/new/` | `app/admin/routes.py` | New book form |
| `POST /admin/books/new/` | `app/admin/routes.py` | Create book |
| `GET /admin/books/{slug}/edit/` | `app/admin/routes.py` | Edit book form |
| `POST /admin/books/{slug}/edit/` | `app/admin/routes.py` | Update book |
| `POST /admin/books/{slug}/delete/` | `app/admin/routes.py` | Delete book |
| `GET /admin/categories/` | `app/admin/routes.py` | Categories list with book count |
| `GET /admin/categories/new/` | `app/admin/routes.py` | New category form |
| `POST /admin/categories/new/` | `app/admin/routes.py` | Create category |
| `GET /admin/categories/{id}/edit/` | `app/admin/routes.py` | Edit category form |
| `POST /admin/categories/{id}/edit/` | `app/admin/routes.py` | Update category |
| `POST /admin/categories/{id}/delete/` | `app/admin/routes.py` | Delete category |
| `GET /admin/about/` | `app/admin/routes.py` | About page edit form |
| `POST /admin/about/` | `app/admin/routes.py` | Update about page |
| `GET /api/v1/health` | `app/api/v1/router.py` | Health check for deploy |
| `/static/*` | `app/main.py` | CSS, JS, uploaded files |

---

## 4. Why this structure?

### Hamravesh Darkube compatibility

[Hamravesh Darkube](https://hamravesh.com/darkube) is a Kubernetes-based PaaS. You connect a Git repo; it builds a **Docker image** and runs it. Managed **PostgreSQL** is a separate addon connected via env vars.

This layout matches that model:

1. **One Dockerfile** → one deployable unit
2. **Config from env vars** → no secrets in code; same image for dev and prod
3. **PostgreSQL as external service** → stateless app container
4. **`--proxy-headers`** on Uvicorn → correct behavior behind Hamravesh reverse proxy (HTTPS, domain)

### Layered folders = version build order

| Phase | Folder | Status |
|-------|--------|--------|
| **v1** | `web/` + `admin/` + `models/` + `services/` + `templates/` + `static/` | Shipped |
| **v2** | New models (Post, Subscriber, ContactMessage), new routes, new templates | Planned |
| **v3** | New model (PathStep), new admin routes, new public template | Planned |

Routes stay thin; logic lives in `services/` so web and admin do not duplicate code.

### FastAPI + Jinja2 (not a separate React app)

Server-rendered HTML means **one container** — no second frontend build step. An API layer exists at `/api/v1/` and can be extended for future integrations.

---

## 5. Environment variables

Copy `.env.example` to `.env` for local development.

| Variable | Required | Description |
|----------|----------|-------------|
| `APP_NAME` | No | App label (default: `petfeature`) |
| `DEBUG` | No | `true` locally; `false` in production |
| `SECRET_KEY` | Yes (prod) | Random string for session signing |
| `PORT` | No | Server port (default: `8000`; Hamravesh may set this) |
| `DATABASE_URL` | Yes | `postgresql+asyncpg://user:pass@host:5432/db` |
| `ADMIN_USERNAME` | Yes | CMS login username |
| `ADMIN_PASSWORD` | Yes | CMS login password |

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

### Database migrations

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

Convert for this app:

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

### Step 3 — Set environment variables

| Variable | Production value |
|----------|------------------|
| `DATABASE_URL` | From PostgreSQL addon |
| `SECRET_KEY` | Long random string |
| `DEBUG` | `false` |
| `ADMIN_USERNAME` | Your admin user |
| `ADMIN_PASSWORD` | Strong password |

### Step 4 — Run migrations on deploy

```bash
alembic upgrade head
```

Run before serving traffic via a one-off job or init container in the Darkube pipeline.

### Step 5 — Domain & SSL

Attach `petfeature.ir` in the panel. SSL is handled by Hamravesh.

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

## 9. Related docs

| Doc | Purpose |
|-----|---------|
| [product-spec.md](./product-spec.md) | Product overview and version roadmap |
| [product-spec-v1.md](./product-spec-v1.md) | v1 scope: library + about (shipped) |
| [product-spec-v2.md](./product-spec-v2.md) | v2 scope: blog + newsletter + contact |
| [product-spec-v3.md](./product-spec-v3.md) | v3 scope: product road |
| [use-case-diagram.md](./use-case-diagram.md) | UML use cases (v1 + v2 + v3) |

---

*Last updated: 2026-07-06*
