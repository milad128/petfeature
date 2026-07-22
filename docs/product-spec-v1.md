# Product Spec v1 — پت فیچر (Library Launch)

> **Status: Shipped** · **Parent:** [Product overview](./product-spec.md) · **Next:** [Product Spec v2](./product-spec-v2.md) · **Diagrams:** [Use case diagram](./use-case-diagram.md)

## 1. Summary

| Field | Value |
|--------|--------|
| **Version** | v1 — Library launch |
| **Status** | Shipped |
| **Goal** | A clean, fast book library with complete detail pages and an about-author page, managed by an admin CMS |
| **Prerequisite for** | [Product Spec v2](./product-spec-v2.md) |

**Scope in one sentence:** Book library (browse + detail), about-author page, and a session-authenticated admin CMS — no blog, no path, no newsletter.

---

## 2. Problem & Goals

**Problem:** The previous site had incomplete book pages, legacy URLs, and no dedicated admin interface.

**v1 goals**

- Full **Browse Book Library** with complete **View Book Details** (note, quotes, media links, downloads, related books)
- **Visit About Me** — clear author and site story, admin-managed
- **Admin CMS** — session-authenticated, full CRUD for books, categories, and about page content

---

## 3. Actors

| Actor | Role |
|-------|------|
| **Visitor** | Browses the book library; visits about-author page |
| **Admin (Milad Mirzaei)** | Manages all library and about-author content via CMS |

---

## 4. Target Users

| Persona | Need |
|---------|------|
| **Junior / aspiring PM** | Curated reading list with complete book notes |
| **Mid-level PM** | Book deep-dives with related resources and media links |
| **Returning reader** | Reliable library reference; downloadable PDFs |
| **Admin** | Publish and maintain book content without touching code |

---

## 5. Core Value (v1)

1. **Curated PM library** — books with categories, authors, and complete detail pages
2. **Rich book notes** — summaries, key quotes, video/podcast links, downloadable PDF, and related books
3. **Clear brand story** — about-author page explains "pet feature" and the author's mission

---

## 6. Information Architecture

```
Home (/)              → entry to library and about
├── کتابخانه         → /library/
│   └── {slug}/       → /library/{slug}/
└── درباره من        → /about/
```

**Global elements**

- Header: brand + nav (library, about)
- Footer: minimal (brand, links)

---

## 7. Feature Requirements

### 7.1 Browse Book Library

**Route:** `/library/`

- Grid of published books: cover image, title, author(s), category tags
- Category filter (client-side JS filtering by category)
- Intro section explaining the detective-reading approach
- Clean URLs — no legacy `/uncategorized/P45334-...` patterns

**Included use case → View Book Details** (`/library/{slug}/`)

| Field | Detail |
|-------|--------|
| Cover | Uploaded image |
| Title + subtitle | Full title |
| Authors | One or more authors |
| Published year | Optional |
| Categories | M2M category tags |
| Note / summary | Rich-text body (HTML/Markdown) |
| Key quotes | List of notable quotes from the book |
| Media links | Video and podcast links (sorted, with optional title) |
| Download | Downloadable PDF file (admin-uploaded) |
| Buy link | Optional external purchase link with custom label |
| Referred books | Related books from within the library |

### 7.2 Visit About Me

**Route:** `/about/`

| Item | Detail |
|------|--------|
| Pet feature definition | Body text (admin-managed) |
| Site story | Why this site exists (admin-managed) |
| Author bio | Milad Mirzaei — name, photo, bio |
| Links | Social/external links (JSON list: label + url) |

### 7.3 Home

**Route:** `/`

- Hero: پت فیچر brand + tagline
- Entry points: کتابخانه، درباره من

### 7.4 Admin CMS

**Routes:** `/admin/` (redirects to `/admin/books/`)

#### Auth
- Session-based login/logout (`/admin/login/`, `/admin/logout/`)
- Credentials from `ADMIN_USERNAME` / `ADMIN_PASSWORD` env vars
- All admin routes guarded; redirect to login if unauthenticated

#### Manage Library Content (`/admin/books/`)

| Feature | Detail |
|---------|--------|
| List books | All books (draft + published); searchable by title or author |
| Create book | Full form with all fields; slug uniqueness validated |
| Edit book | Pre-filled form; slug change validated against conflicts |
| Delete book | Removes book and associated media links |
| Cover upload | Upload JPG/PNG; stored in `static/uploads/covers/` |
| Download upload | Upload PDF; stored in `static/uploads/downloads/` |
| Categories | Multi-select from existing categories; M2M |
| Authors | Dynamic multi-value input (JSON) |
| Quotes | Dynamic list of quote strings (JSON) |
| Media links | Dynamic list of {type, url, title} — video or podcast |
| Referred books | Multi-select from other books (self-referential M2M) |
| Status | Draft / Published toggle |
| Show in library | Toggle visibility on public library page |

#### Manage Categories (`/admin/categories/`)

| Feature | Detail |
|---------|--------|
| List categories | All categories with book count |
| Create category | Name; uniqueness validated |
| Edit category | Rename; uniqueness validated against others |
| Delete category | Removes category (books retain other categories) |

#### Manage About Author Content (`/admin/about/`)

| Field | Detail |
|-------|--------|
| Author name | Text |
| Author photo | URL to photo |
| Author bio | Rich-text body |
| Pet feature body | Body text for pet feature definition |
| Site story body | Body text for site origin story |
| Links | Dynamic list of {label, url} |

---

## 8. Content Model (v1)

| Entity | Key fields |
|--------|------------|
| **Book** | id, title, subtitle, authors (JSON list), published_year, slug, cover (path), status (draft/published), show_in_library, note (text), quotes (JSON list), buy_link_title, buy_link_url, download_file (path), created_at, updated_at |
| **BookMediaLink** | id, book_id (FK), type (video/podcast), url, title, sort_order |
| **Category** | id, name (unique), created_at |
| **book_categories** | book_id ↔ category_id (M2M join table) |
| **book_references** | book_id ↔ referred_book_id (self-referential M2M join table) |
| **AboutPage** | id, author_name, author_photo, author_bio, pet_feature_body, site_story_body, links (JSON list), updated_at |

**Relationships**

- Book → many BookMediaLink (cascade delete)
- Book ↔ Category (many-to-many via book_categories)
- Book ↔ Book (many-to-many via book_references — "referred books")
- AboutPage is a singleton (one row)

---

## 9. Non-Functional Requirements

| Area | Requirement |
|------|-------------|
| **RTL & Persian typography** | Native RTL; readable Farsi fonts |
| **SEO** | Title pattern: `{Page} \| پت فیچر \| دانشنامه یک مدیر محصول`; basic meta |
| **Performance** | Fast SSR pages; optimized cover images |
| **Mobile** | Fully responsive |
| **Accessibility** | Semantic HTML, sufficient contrast |
| **Analytics** | Traffic, time on book pages |

---

## 10. Out of Scope (v1)

Deferred to [v2](./product-spec-v2.md) or [v3](./product-spec-v3.md):

- Blog / notes (یادداشت) → v2
- Newsletter subscription → v2
- Contact form → v2
- Learning path (مسیر) → v3
- User registration / login
- Post reactions and comments
- Book comments
- Full-text search
- Paid content / paywall
- English version
- Mobile app

---

## 11. Technical Stack

| Layer | Choice |
|-------|--------|
| Language | Python 3.12 |
| Web framework | FastAPI |
| Templates | Jinja2 (server-rendered HTML) |
| ORM | SQLAlchemy async (`asyncpg`) |
| Migrations | Alembic |
| Database | PostgreSQL (Hamravesh managed addon) |
| Config | Pydantic-settings (.env) |
| Container | Docker (Hamravesh Darkube) |
| File storage | Local filesystem (`static/uploads/`) |

---

## 12. Success Metrics

| Metric | Why it matters |
|--------|----------------|
| Return visitors | Useful reference site |
| Time on book pages | Content resonates |
| Library completeness | % of books with full detail + links |

---

## Deployment Status

| Field | Value |
|-------|-------|
| **Status** | Shipped |
| **Deploy date** | July 2026 |
| **Platform** | Hamravesh Darkube (production) |
| **Notes** | — |

---

*v1 spec — July 2026*
