# Product Spec v3 — پت فیچر (Tools / Template Library)

> **Status: Shipped** · **Prerequisite:** [Product Spec v2](./product-spec-v2.md) · **Parent:** [Product overview](./product-spec.md) · **Diagrams:** [Use case diagram](./use-case-diagram.md)
> **Design files:** `petfeature redesign/project/Petfeature Tools.dc.html`, `Petfeature Tool Detail.dc.html`

## 1. Summary

| Field | Value |
|--------|--------|
| **Version** | v3 — Tools |
| **Status** | Shipped |
| **Goal** | A curated Persian PM template library — ready-to-use downloadable artifacts with usage guides, cross-linked to books and posts |
| **Builds on** | [Product Spec v2](./product-spec-v2.md) |
| **Epic** | Tools |
| **Migration source** | Old petfeature.ir `/Templates/` section (3 categories) |

**Scope in one sentence:** A template library at `/tools/` where each entry has a cover image, a usage guide, one or more downloadable files, and cross-links to related books and posts — no interactive calculators, no external links.

---

## 2. Problem & Goals

**Problem:** Persian PMs lack ready-to-use, high-quality PM artifacts in their language. The old site had a `/Templates/` section but it was disconnected from the library and blog. The new site can unify them.

**v3 goals**

- **Browse Tools** — visitors discover templates filtered by category
- **View a Tool** — visitors read a usage guide and download one or more files
- **Cross-linked** — each tool surfaces related books and related posts
- **Admin manages** — full CRUD for tools via the admin CMS; no deploy needed to add a new template

---

## 3. Actors

| Actor | Role |
|-------|------|
| **Visitor** | Browses tools, downloads files, follows cross-links to books and posts |
| **Admin (Milad Mirzaei)** | Creates, edits, publishes, and deletes tool entries and their downloadable files |

---

## 4. Information Architecture (additions)

Extends v2 IA:

```
Home (/)
├── ابزارها (Tools)   → /tools/          (new in v3)
│   └── {slug}/        → /tools/{slug}/   (new in v3)
├── بلاگ              → /blog/            (from v2)
├── کتابخانه          → /library/         (from v1)
└── درباره من         → /about/            (from v1)
```

**Global additions**

- **ابزارها** added to main nav (nav: کتابخانه | بلاگ | ابزارها | درباره من)

---

## 5. Categories

Tools use the **same `Category` model as the book library** — no separate category system. Categories are created and managed at `/admin/categories/` (already built in v1).

Admin assigns exactly one category to each tool from the existing category list. The category filter pills on `/tools/` are derived dynamically from categories used by published tools.

**Initial categories to create in admin** (seed data, not hardcoded):

| Category (FA) | Notes |
|---------------|-------|
| رزومه و مصاحبه | Resume + interview templates |
| مستندات محصول | PRD, one-pager, spec templates |
| استراتژی | Roadmap, vision board, OKR |
| اولویت‌بندی | RICE, ICE, scoring sheets |
| متریک‌ها | North Star, dashboard templates |

---

## 6. Feature Requirements

### 6.1 Browse Tools — `/tools/`

**Hero section** (static copy — not admin-editable)
- Badge: "مستقیم قابل استفاده"
- Title: ابزارهای پت فیچر
- Description: "قالب‌ها و چارچوب‌های آماده‌ی مدیریت محصول — رزومه، PRD، روم‌مپ، ماتریس اولویت‌بندی و متریک — برای استفاده‌ی مستقیم در کارت."
- Count badge: 🛠 N ابزار (published tools count)

**Category filter**
- Client-side JS filter pills — one per category + "همه" pill
- Same pattern as library and blog tag filter
- Empty state: "🛠 ابزاری در این دسته نیست — دسته‌ی دیگری را امتحان کنید یا به همه‌ی ابزارها برگردید"

**Tool grid**

Each card shows:

| Element | Detail |
|---------|--------|
| Cover image | Uploaded image (like book covers) |
| Category tag | e.g., اولویت‌بندی |
| Title | Tool title |
| Short description | 1–2 sentence summary |

---

### 6.2 View a Tool — `/tools/{slug}/`

**Header**

| Element | Detail |
|---------|--------|
| Breadcrumb | ابزارها ‹ {tool title} |
| Category tag | e.g., اولویت‌بندی |
| Cover image | Large — same image as shown on card |
| Title | Tool title |
| Subtitle | One-line description of this specific tool (shown below title) |

**"دریافت ابزار" section**

A dynamic list of downloadable files — admin adds as many as needed per tool (e.g., PDF version + Excel version + Persian version + English version).

Each download entry shows:

| Element | Detail |
|---------|--------|
| Name | Version name (e.g., "نسخه‌ی PDF", "نسخه‌ی Google Sheets فارسی") |
| Description | 1–2 sentences on when/how to use this version |
| Download button | "دانلود ↓" — serves the uploaded file |

**"راهنمای استفاده" section**

- Rich-text body (HTML)
- Explains what the tool is, when to use it, how to fill it in
- May include blockquote highlights

**"کتاب‌های مرتبط" section**

- Cards linking to library books (admin selects)
- Shows: book emoji icon, title, author
- Hidden if no related books assigned

**"یادداشت‌های مرتبط" section**

- Cards linking to blog posts (admin selects)
- Shows: post title, "مطالعه ←" link
- Hidden if no related posts assigned

**Footer**
- Back link: "→ همه‌ی ابزارها"

---

### 6.3 Admin CMS — v3 additions

All routes under `/admin/`.

#### Manage Tools — `/admin/tools/`

**Tool list**

| Column | Detail |
|--------|--------|
| Cover | Thumbnail |
| Title | Tool title |
| Category | Category tag |
| Files | Count of downloadable files |
| Status | Draft / Published |
| Actions | Edit, Delete |

**Create / Edit Tool — `/admin/tools/new/` and `/admin/tools/{slug}/edit/`**

| Field | Detail |
|-------|--------|
| Title | Text input |
| Slug | Auto-generated from title; editable; uniqueness validated |
| Cover image | File upload (JPG/PNG); **required**; stored in `static/uploads/tool-covers/` |
| Category | Single-select from fixed category list |
| Short description | 1–2 sentences — shown on grid card and as subtitle on detail page |
| Body | Rich-text usage guide (HTML) — "راهنمای استفاده" |
| Status | Draft / Published |
| Downloadable files | Dynamic list (see below) |
| Related books | Multi-select from library books |
| Related posts | Multi-select from blog posts |

**Downloadable files — dynamic list (like media links on books)**

Admin adds one or more download entries per tool. Each entry:

| Sub-field | Detail |
|-----------|--------|
| Name | Version label (e.g., "نسخه‌ی PDF", "نسخه‌ی اکسل فارسی") |
| Description | Short context (e.g., "فایل آماده‌ی چاپ، برای پر کردن دستی یا استفاده‌ی آفلاین") |
| File upload | Upload file; stored in `static/uploads/tool-files/`; replaces existing on re-upload |
| Sort order | Controls display order in "دریافت ابزار" section |

**Delete tool** — removes tool entry, cover image, and all uploaded tool files.

---

## 7. Content Model (v3 additions)

| Entity | Key fields |
|--------|------------|
| **Tool** | id, title, slug (unique), cover (path), category, short_description, body (text), status (draft/published), created_at, updated_at |
| **ToolFile** | id, tool_id (FK, cascade delete), name, description, file (path), sort_order |
| **tool_books** | tool_id ↔ book_id (M2M) |
| **tool_posts** | tool_id ↔ post_id (M2M) |

**Relationships**

- Tool → many ToolFile (cascade delete; ordered by sort_order)
- Tool ↔ Book (many-to-many via tool_books)
- Tool ↔ Post (many-to-many via tool_posts)

---

## 8. Template Inventory (Phase 1 — migrate from old site)

| Title | Category | Files |
|-------|----------|-------|
| قالب رزومه مدیر محصول (فارسی) | رزومه و مصاحبه | PDF + Editable |
| قالب رزومه مدیر محصول (English) | رزومه و مصاحبه | PDF + Editable |
| راهنمای مصاحبه PM | رزومه و مصاحبه | PDF |
| قالب PRD | مستندات محصول | PDF + Editable |
| قالب One-Pager محصول | مستندات محصول | PDF + Editable |
| قالب Roadmap | استراتژی | PDF + Editable |
| Vision Board | استراتژی | PDF + Editable |
| قالب OKR | استراتژی | PDF + Editable |
| ماتریس RICE | اولویت‌بندی | PDF + Editable |
| ماتریس ICE | اولویت‌بندی | PDF + Editable |
| قالب North Star Metric | متریک‌ها | PDF + Editable |
| قالب Dashboard متریک | متریک‌ها | PDF + Editable |

---

## 9. Non-Functional Requirements (v3)

| Area | Requirement |
|------|-------------|
| **Cover image** | Required to publish; shown on both grid card and detail page |
| **File downloads** | Served as static files from `static/uploads/tool-files/`; correct Content-Type header; opens download dialog |
| **Category filter** | Client-side JS — no page reload on filter change |
| **Mobile** | Tool grid, detail page, download buttons, and related sections all fully responsive |
| **Empty sections** | "کتاب‌های مرتبط" and "یادداشت‌های مرتبط" hidden if no items assigned |

---

## 10. Out of Scope (v3)

| Item | Notes |
|------|-------|
| External links (Google Docs, Notion, Figma) | All resources are uploaded files — no external links |
| Interactive calculators | Not in v3 |
| Tool ratings or comments | Not in v3 |
| User uploads | Visitors cannot upload their own templates |
| Tool versioning history | Admin replaces files directly |
| Full-text search | Not in v3 |

---

## 11. Dependency on v2

v3 assumes v2 provides:

- Blog with published posts (for "یادداشت‌های مرتبط" cross-links)
- Full production deployment stable

---

## 12. Success Metrics

| Metric | Why it matters |
|--------|----------------|
| Tool page views | Adoption |
| File downloads | Visitors actually use the templates |
| Related book click-through | Cross-linking drives library engagement |
| Related post click-through | Cross-linking drives blog engagement |

---

## Deployment Status

| Field | Value |
|-------|-------|
| **Status** | Shipped |
| **Deploy date** | July 2026 |
| **Platform** | Hamravesh Darkube (production) |
| **Notes** | — |

---

*v3 spec — July 2026 · Updated from design files: Petfeature Tools.dc.html, Petfeature Tool Detail.dc.html · **Shipped***
