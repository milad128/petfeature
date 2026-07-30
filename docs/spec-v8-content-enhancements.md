# Product Spec v8 — Content Enhancements

**Version:** v8  
**Status:** Shipped  
**Author:** Milad Mirzaei  
**Date:** July 2026  
**Depends on:** v1 (Library), v2 (Blog), v3 (Tools) — all shipped

---

## Overview

Three targeted content-model enhancements that make existing sections richer without introducing new pages or epics. All three are admin-facing changes with minimal or no impact on the public-facing URL structure.

| # | Feature | Scope |
|---|---------|-------|
| 1 | Book media links — add **Website** type | `BookMediaLink` model + admin book form + book detail template |
| 2 | Post — **Related Books** | New `post_books` join table + admin post form + post detail template |
| 3 | Tool downloadables — support **Links** alongside file uploads | `ToolFile` model extension + admin tool form + tool detail template (client view unchanged in appearance) |

---

## Feature 1 — Book Media Links: Website Type

### Problem Statement

The "ویدیو و پادکست" section on the book form only supports two link types. Admins sometimes want to link to a webpage (author's site, article, Goodreads, etc.) but have no appropriate type for it. The workaround is mis-labelling a link as video or podcast, which pollutes the UI on the public book page.

### Target User

Admin (Milad) editing a book entry.

### User Stories

- As an admin, I want to select "وبسایت" as a link type when adding a media link to a book, so that I can link to relevant webpages without misusing the video or podcast types.
- As a visitor, I want website links to be visually distinguishable from video and podcast links on the book detail page, so that I know what I'm about to open.

### Acceptance Criteria

**Admin — Book Form (`/admin/books/new` and `/admin/books/{slug}/edit`)**

1. The type dropdown in the "ویدیو و پادکست" section gains a third option: `وبسایت` (value: `website`).
2. Existing entries with type `video` or `podcast` are unaffected — they render correctly on load and on save.
3. The section title may be renamed to **"لینک‌های مرتبط"** to reflect that it now covers websites too (not just media).
4. The `+افزودن لینک` button behavior is unchanged.

**Model — `BookMediaLink` / `MediaLinkType` enum**

5. `MediaLinkType` enum gains a third value: `WEBSITE = "website"`.
6. No migration is required — the `type` column is `String(20)`, so the new value is stored as-is.

**Public — Book Detail Page (`/library/{slug}/`)**

7. Links of type `website` render with a distinct label/icon (e.g., 🌐 or "وبسایت") — different from video (🎬) and podcast (🎙).
8. No layout change — website links follow the same row/card pattern as video and podcast links.

### Out of Scope

- Validating that a "website" URL doesn't point to a video platform — admin responsibility.
- Adding any new public filter or section for website links.

### Open Questions

- Should website links open with `rel="noopener noreferrer"` (same as current video/podcast links)? **Assumed yes.**

---

## Feature 2 — Post: Related Books

### Problem Statement

Blog posts (`/blog/{slug}/`) often discuss or reference specific books from the library. Currently there is no structured way to surface this connection — the admin must manually mention the book in the post body. Readers who finish a post have no discovery path to the referenced books.

### Target User

- **Admin:** authors linking posts to library books.
- **Reader:** a visitor who reads a post and wants to explore the books referenced in it.

### User Stories

- As an admin, I want to select related books when writing or editing a post, so that the connection between my writing and the library is structured and not buried in body text.
- As a reader, I want to see which library books are referenced by a post, so that I can click through to learn more about them.

### Data Model

**New association table:** `post_books`

| Column | Type | Notes |
|--------|------|-------|
| `post_id` | FK → `posts.id` | CASCADE DELETE |
| `book_id` | FK → `books.id` | CASCADE DELETE |

**`Post` model — new relationship:**
```python
related_books: Mapped[list["Book"]] = relationship(
    "Book", secondary=post_books, lazy="selectin"
)
```

**Helper property on `Post`:**
```python
@property
def related_book_ids(self) -> list[int]:
    return [b.id for b in self.related_books]
```

**Alembic migration required** — creates the `post_books` join table.

### Acceptance Criteria

**Admin — Post Form (`/admin/posts/new` and `/admin/posts/{slug}/edit`)**

1. A new section **"کتاب‌های مرتبط"** appears in the post form, between the existing content sections and the form actions — matching the identical section already present in the tool form.
2. The section uses the same chip + modal picker pattern as the tool form's related books section:
   - Selected books shown as chips (title + author) with a remove `×` button.
   - `+ افزودن کتاب مرتبط` button opens a searchable modal listing all published books.
   - A hidden input `related_book_ids` carries the JSON array to the backend.
3. On load (edit mode), previously saved related books are pre-populated as chips.
4. All books in the system (published + draft) are available to pick from in the modal — consistent with how tool form handles this.

**Backend**

5. `POST /admin/posts/` and `POST /admin/posts/{slug}` accept and persist `related_book_ids` (JSON array of int IDs).
6. The post service syncs the `related_books` relationship on save (replace, not append).

**Public — Post Detail Page (`/blog/{slug}/`)**

7. If a post has related books, a **"کتاب‌های مرتبط"** section is rendered at the bottom of the post page, below the post body and above the comments section.
8. Each book is displayed as a compact card containing:
   - Book cover thumbnail (if available)
   - Book title (linked to `/library/{slug}/`)
   - Authors display string
9. If a post has no related books, the section is not rendered (no empty heading).
10. Maximum display count: **no cap** — show all related books. (If this becomes unwieldy, a v9 cap can be introduced.)

### Out of Scope

- Showing related posts on the book detail page (reverse direction — backlog).
- Auto-suggesting related books based on post content.

### Open Questions

- None — requirements are clear.

---

## Feature 3 — Tool Downloadables: Link Support

### Problem Statement

The "فایل‌های قابل دانلود" section on the tool form only accepts file uploads (PDF, Excel, Word, etc.). Admins sometimes want to include an external link (e.g., a Google Docs template, a Notion page, a Miro board) as a downloadable resource. Currently there is no way to do this — admins must either skip linking or put the URL in the body text where it's not structured.

On the public tool page, all downloads should look the same — the only difference is that links show `link` as the file type indicator instead of `PDF`, `XLSX`, etc.

### Target User

- **Admin:** adding downloadable resources to a tool, some of which are hosted externally.
- **Reader/user:** accessing tool resources — they click a button and get either a file or an external link, with clear labelling.

### Data Model

**`ToolFile` model — add `item_type` discriminator column:**

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| `item_type` | `String(10)` | `"file"` | `"file"` or `"link"` |

The existing `file` column holds the uploaded file path for `item_type="file"` entries. For `item_type="link"` entries, the `file` column holds the external URL.

**Alternative considered:** Add a separate `url` column. Rejected — the `file` column already holds the "where to get it" value for file entries; reusing it for links avoids a nullable-vs-required ambiguity and keeps the data structure flat. The `item_type` discriminator makes the intent explicit.

**`files_data` property on `Tool` — update to include `item_type`:**
```python
@property
def files_data(self) -> list[dict[str, str]]:
    return [
        {
            "name": f.name,
            "description": f.description or "",
            "file": f.file,
            "item_type": f.item_type,
        }
        for f in self.files
    ]
```

**Alembic migration required** — adds `item_type VARCHAR(10) NOT NULL DEFAULT 'file'` to `tool_files`.

### Acceptance Criteria

**Admin — Tool Form (`/admin/tools/new` and `/admin/tools/{slug}/edit`)**

1. The section title changes from **"فایل‌های قابل دانلود"** to **"فایل‌ها و لینک‌های قابل دانلود"**.
2. Two separate add buttons appear below the rows:
   - `+ افزودن فایل` — adds a file-upload row (existing behavior, unchanged).
   - `+ افزودن لینک` — adds a link row (new).
3. **File row (existing):** `name` text input + `description` text input + file upload input. `item_type` defaults to `"file"`.
4. **Link row (new):** `name` text input + `description` text input + URL text input (`dir="ltr"`, `placeholder="https://..."`). `item_type` = `"link"`.
5. Both row types have the `🗑` remove button.
6. The hidden `files` JSON input serialises each row as:
   ```json
   { "name": "...", "description": "...", "file": "path-or-url", "item_type": "file|link" }
   ```
7. On load (edit mode), existing file rows render as file rows and existing link rows render as link rows based on `item_type`.
8. Validation: link rows require a non-empty URL starting with `http://` or `https://`. File rows require a file to be selected (on create) or an existing file path (on edit).

**Backend**

9. The tool service persists `item_type` alongside `name`, `description`, and `file` for each row.
10. For link rows, no file upload processing occurs — `file` is stored as the raw URL string.
11. Existing tools with no `item_type` value are treated as `"file"` (handled by DB default on migration).

**Public — Tool Detail Page (`/tools/{slug}/`)**

12. Client view is **visually unchanged** — each downloadable resource renders exactly as it does today.
13. The only difference: for `item_type="link"` entries, the file type badge/label shows **"لینک"** (or "link") instead of deriving the type from the file extension (PDF, XLSX, etc.).
14. Clicking a link-type resource opens the external URL in a new tab (`target="_blank" rel="noopener noreferrer"`).
15. Link-type resources **do** increment `tool.download_count` on click — the link points to a file hosted externally, so it counts as a download.

### Out of Scope

- Validating that the URL is reachable at save time.
- Tracking individual link clicks separately from file downloads.

### Open Questions

- None — link clicks increment `download_count` (resolved: links point to externally hosted files, so the click is semantically a download).

---

## Implementation Order

Recommended sequence (each is independent — can be parallelised):

1. **Feature 1** — smallest change; enum + template only, no migration.
2. **Feature 3** — model migration + admin form JS + minor template tweak.
3. **Feature 2** — model migration + admin form (reuse existing modal pattern from tools) + post detail template.

Feature 1 can ship in the same deploy as Features 2 and 3, or ahead of them.

---

## NFRs

- All new admin form sections follow existing RTL layout, card-section structure, and chip/modal picker patterns.
- New public-facing UI elements (post related books, tool link badges) must be RTL-compatible.
- No new public routes introduced — all changes are within existing page templates.
- Alembic migrations for Features 2 and 3 must include `server_default` values so they apply cleanly to existing data without nullability errors.

---

## Deployment Status

| Field | Value |
|-------|-------|
| **Status** | Shipped |
| **Deploy date** | July 2026 |
| **Platform** | Hamravesh Darkube (production) |
| **Notes** | — |

---

*July 2026 — v8 spec written. Features are independent; all three can be built and deployed in a single release.*
