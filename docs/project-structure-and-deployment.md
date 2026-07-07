# Project Structure & Deployment

> **Maintained doc:** Update this file whenever the project layout, stack, env vars, or Hamravesh deploy steps change.
>
> **Parent:** [Product overview](./product-spec.md)

## Changelog

| Date | Change |
|------|--------|
| 2026-07-07 | Updated to reflect shipped v4 Book Engagement: BookRating/BookComment models, book engagement routes, admin book comments, migration 008 |
| 2026-07-07 | Updated to reflect shipped v2 Blog and v3 Tools: models, routes, admin CMS, migrations 006–007 |
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
│   │   └── routes.py                   # Public pages: /, /library/, /blog/, /tools/, /about/
│   ├── admin/
│   │   ├── auth.py                     # Session-based admin authentication
│   │   └── routes.py                   # Admin CMS: books, categories, posts, comments, tools, about
│   ├── api/
│   │   └── v1/
│   │       └── router.py               # REST API (health check)
│   ├── models/
│   │   ├── book.py                     # Book, BookMediaLink, book_references, book_categories, BookRating, BookComment (v4)
│   │   ├── category.py                 # Category, book_categories join table
│   │   ├── about.py                    # AboutPage (singleton)
│   │   ├── post.py                     # Post, PostRating, PostComment (v2)
│   │   └── tool.py                     # Tool, ToolFile, tool_books, tool_posts (v3)
│   ├── schemas/
│   │   ├── book.py                     # BookForm, MediaLinkInput
│   │   ├── category.py                 # CategoryForm
│   │   ├── about.py                    # AboutForm, LinkInput
│   │   ├── post.py                     # PostForm (v2)
│   │   └── tool.py                     # ToolForm (v3)
│   ├── services/
│   │   ├── books.py                    # Book CRUD, list, slug lookup, JSON parsers; rate_book, add_book_comment, list_book_comments, set_book_comment_status, delete_book_comment (v4)
│   │   ├── categories.py               # Category CRUD, list
│   │   ├── about.py                    # AboutPage get/update
│   │   ├── posts.py                    # Post CRUD, ratings, comments, view counts (v2)
│   │   ├── tools.py                    # Tool CRUD, file handling (v3)
│   │   └── uploads.py                  # Cover, PDF, post-cover, tool-file uploads
│   ├── templates/
│   │   ├── base.html                   # Public layout (RTL, nav, footer)
│   │   ├── pages/
│   │   │   ├── home.html
│   │   │   ├── library.html            # Grid + category filter
│   │   │   ├── book_detail.html        # Full book detail
│   │   │   ├── blog.html               # Blog list + featured (v2)
│   │   │   ├── post_detail.html        # Post detail + rating + comments (v2)
│   │   │   ├── tools.html              # Tools grid + category filter (v3)
│   │   │   ├── tool_detail.html        # Tool detail + downloads (v3)
│   │   │   └── about.html
│   │   ├── admin/
│   │   │   ├── base.html               # Admin layout
│   │   │   ├── login.html
│   │   │   ├── books_list.html
│   │   │   ├── book_form.html          # Create/edit book (all fields)
│   │   │   ├── categories_list.html
│   │   │   ├── category_form.html
│   │   │   ├── posts_list.html         # (v2)
│   │   │   ├── post_form.html          # (v2)
│   │   │   ├── post_comments_list.html # (v2)
│   │   │   ├── tools_list.html         # (v3)
│   │   │   ├── tool_form.html          # (v3)
│   │   │   ├── book_comments_list.html # (v4)
│   │   │   └── about_form.html
│   │   └── partials/
│   │       └── note_fonts.html
│   └── static/
│       ├── css/
│       │   ├── main.css                # Public site styles
│       │   └── admin.css               # Admin panel styles
│       ├── js/
│       │   ├── library.js              # Client-side category filtering
│       │   ├── blog.js                 # Copy link, rating UI (v2)
│       │   ├── tools.js                # Client-side category filtering (v3)
│       │   └── admin.js                # Admin form JS (dynamic fields)
│       └── uploads/
│           ├── covers/                 # Book cover images
│           ├── downloads/              # Book PDF files
│           ├── post-covers/            # Post cover images (v2)
│           ├── tool-covers/            # Tool cover images (v3)
│           └── tool-files/             # Tool downloadable files (v3)
└── docs/                               # Product specs + this file
```

---

## 3. Routes (shipped — v1 + v2 + v3 + v4)

### Public (`app/web/routes.py`)

| Route | Description |
|-------|-------------|
| `GET /` | Home page |
| `GET /library/` | Book list (published + show_in_library only) |
| `GET /library/{slug}/` | Book detail (published only) |
| `GET /about/` | About page |
| `GET /blog/` | Blog list + featured post (v2) |
| `GET /blog/{slug}/` | Post detail; increments view count (v2) |
| `POST /blog/{slug}/rate/` | Star rating submit (v2) |
| `POST /blog/{slug}/comment/` | Comment submit (v2) |
| `GET /tools/` | Tools grid + category filter (v3) |
| `GET /tools/{slug}/` | Tool detail + downloads (v3) |
| `POST /library/{slug}/rate/` | Book star rating submit (v4) |
| `POST /library/{slug}/comment/` | Book comment submit — goes to pending queue (v4) |

### Admin (`app/admin/routes.py`, prefix `/admin`)

| Route | Description |
|-------|-------------|
| `GET /` | Redirects to `/admin/books/` |
| `GET/POST /login/`, `GET /logout/` | Session auth |
| `GET/POST /books/`, `/books/new/`, `/books/{slug}/edit/`, `POST .../delete/` | Book CRUD (v1) |
| `GET/POST /categories/`, CRUD | Category management (v1) |
| `GET/POST /posts/`, CRUD | Post management (v2) |
| `GET /posts/comments/`, approve/reject/delete | Comment moderation (v2) |
| `GET/POST /tools/`, CRUD | Tool management (v3) |
| `GET /books/comments/`, approve/reject/delete | Book comment moderation (v4) |
| `GET/POST /about/` | About page CMS (v1) |

### API & static

| Route | Description |
|-------|-------------|
| `GET /api/v1/health` | Health check for deploy |
| `/static/*` | CSS, JS, uploaded files |

**Not yet built:** `/path/` (Roadmap), `/newsletter/`, `/contact/`, `/admin/analytics/`.

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

| Phase | Scope | Status |
|-------|-------|--------|
| **v1** | Library + About + admin CMS (`Book`, `Category`, `AboutPage`) | **Shipped** |
| **v2** | Blog (`Post`, `PostRating`, `PostComment`), post admin + comment moderation | **Shipped** |
| **v3** | Tools (`Tool`, `ToolFile`), tool admin, cross-links to books/posts | **Shipped** |
| **v4** | Book Engagement (`BookRating`, `BookComment`), rating widget, comment moderation | **Shipped** |
| **Backlog** | Roadmap (`PathStep`), newsletter/contact, analytics dashboard | Unscheduled |

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
| [product-spec-v2.md](./product-spec-v2.md) | v2 scope: blog (shipped) |
| [product-spec-v3.md](./product-spec-v3.md) | v3 scope: tools (shipped) |
| [product backlog.md](./product%20backlog.md) | Unscheduled: roadmap, newsletter, analytics |
| [use-case-diagram.md](./use-case-diagram.md) | UML use cases (v1 + v2 + v3) |

---

*Last updated: 2026-07-07*
