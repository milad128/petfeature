# Product Spec v9 — Media Library + Book Link Types

**Version:** v9  
**Status:** Shipped  
**Author:** Milad Mirzaei  
**Date:** July 2026  
**Depends on:** v1–v8 (all shipped)

---

## Overview

v9 delivers two independent, admin-facing features that improve content management quality without adding new public pages.

**Epic 1 — Admin Media Library:** A general-purpose file manager at `/admin/files/` where Milad can upload any file (PDF, video, document, image), browse all previously uploaded assets, copy their permanent public URLs to clipboard, and delete files that are no longer needed. This eliminates the current workaround of attaching standalone assets to unrelated content records (e.g., a PDF that belongs to a post body being uploaded as a tool file).

**Epic 2 — Book Link Types: Article + Book:** The book form's "لینک‌های مرتبط" section (renamed in v8) currently supports three link types: video, podcast, website. v9 adds two semantic types — `article` and `book` — so that admins can correctly classify external links to articles and book listings. Public visitors then see appropriately labelled links on the book detail page.

| # | Epic | Scope | Migration? |
|---|------|-------|-----------|
| 1 | Media Library | New `MediaFile` model + `/admin/files/` page | Yes — creates `media_files` table |
| 2 | Book Link Types | Extend `MediaLinkType` enum with `article` and `book` | No — column is `String(20)` |
| 3 | Admin Books Filter | Filter `/admin/books/` by status and category via query params | No — filters on existing columns |
| 4 | Cover Preview Fit | `object-fit: cover` on the book form's cover image preview | No — CSS/template only |
| 5 | بلاگ → یادداشت rename | Update public-facing "بلاگ" label to "یادداشت" in nav + blog pages | No — template copy only |

All five epics are fully independent. Epics 2–5 can ship ahead of Epic 1.

---

## Epic 1 — Admin Media Library

### Problem Statement

When writing post bodies, book notes, or tool descriptions, Milad often needs to reference a file (PDF, video, document, image) hosted on the site. Every existing upload path is tightly coupled to a specific content type:

- `static/uploads/covers/` — book cover images
- `static/uploads/post-covers/` — blog post cover images
- `static/uploads/post-images/` — inline post images (if used)
- `static/uploads/tool-covers/` — tool cover images
- `static/uploads/tool-files/` — tool downloadable files
- `static/uploads/downloads/` — book PDF downloads

There is no general-purpose path to upload an asset and get a standalone URL back. The workaround is to attach the file to a content record it does not belong to — a PDF uploaded as a tool file to be linked in a post body, for example. This pollutes content records with orphaned assets, makes auditing impossible, and creates confusion when that tool or book is later edited.

### Target User

Admin (Milad) — the sole CMS user. This is a productivity and content hygiene feature; it has no public-facing audience.

### User Stories

| # | As a… | I want to… | So that… |
|---|-------|-----------|---------|
| U1 | Admin | Upload any supported file to a central media library | I get a permanent public URL I can paste into any content field |
| U2 | Admin | Browse all previously uploaded media files in one place | I can copy a URL without re-uploading the same file |
| U3 | Admin | Delete a media file when it's no longer needed | Unused files don't accumulate and the library stays clean |
| U4 | Admin | See the file's name, type, size, and upload date at a glance | I can quickly identify the file I'm looking for |
| U5 | Admin | Copy the full absolute URL to my clipboard with one click | I can immediately paste it into a richtext editor, link field, or markdown block |
| U6 | Admin | Receive a clear error message if my upload is rejected | I understand exactly what went wrong (size, type) and can fix it |

### Data Model

**New model: `MediaFile`**

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | Integer | PK, auto-increment | |
| `original_name` | String(500) | NOT NULL | Filename as uploaded — for display only |
| `file_path` | String(1000) | NOT NULL | Stored path, e.g. `/static/uploads/media/abc123.mp4` |
| `file_size` | Integer | NOT NULL | Size in bytes |
| `mime_type` | String(100) | NOT NULL | e.g. `application/pdf`, `video/mp4`, `image/jpeg` |
| `created_at` | DateTime | NOT NULL, server_default=now() | |

**New upload directory:** `app/static/uploads/media/`  
**Public URL prefix:** `/static/uploads/media/`  
**Alembic migration required** — creates the `media_files` table.

**Service additions (`app/services/uploads.py` or equivalent):**

| Function | Behaviour |
|----------|-----------|
| `save_media_upload(file)` | Validates type + size, saves to `MEDIA_DIR` with a UUID-based filename, returns the stored path |
| `delete_media_file(file_path)` | Removes from disk; handles `FileNotFoundError` gracefully (does not raise, logs warning) |
| `ensure_upload_dirs()` | Updated to include `MEDIA_DIR` |

**Why UUID filenames?** Uploaded filenames from the browser may collide (e.g., two files both named `notes.pdf`). UUID-based storage names eliminate collisions; `original_name` in the DB preserves the human-readable name for display.

### Allowed File Types and Limits

| Category | Allowed Extensions | Max Size | Notes |
|----------|--------------------|---------|-------|
| PDF | `.pdf` | 50 MB | Most common use case |
| Video | `.mp4`, `.webm`, `.mov` | 200 MB | Largest allowed; see storage note below |
| Document | `.xlsx`, `.docx`, `.pptx`, `.csv` | 25 MB | |
| Image | `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif` | 10 MB | |

**Validation:** Performed server-side (MIME type + extension check + size). Client-side `accept=` attribute on the file input provides a first-pass hint but is not relied upon for security.

**Storage note:** All files land in the same `static/uploads/` volume used by all other uploads on Hamravesh Darkube. Large video uploads will consume container storage. This is acceptable for v9 given current content volume. If video upload becomes heavy, migrating to Arvan Cloud Object Storage is the right long-term solution — explicitly out of scope for v9.

### Acceptance Criteria

**Sidebar navigation**

1. A new **"رسانه"** entry appears in the admin sidebar, grouped with other content sections, linking to `/admin/files/`.

**Media Library page (`GET /admin/files/`)**

2. The page renders a table of all uploaded files sorted by `created_at` descending (newest first). Columns:

   | Column header | Content |
   |---------------|---------|
   | نام فایل | `original_name` — plain text |
   | نوع | Type badge derived from `mime_type` (PDF, ویدیو, تصویر, سند) |
   | حجم | Human-readable size: `< 1 MB` → `{n} KB`; `≥ 1 MB` → `{n.n} MB` |
   | تاریخ آپلود | Jalali formatted date (same utility used across admin) |
   | لینک | Full absolute URL (e.g. `https://petfeature.ir/static/uploads/media/…`) + **کپی** button |
   | عملیات | **حذف** button |

3. Empty state: when no files exist, show a centered message — "هنوز فایلی آپلود نشده. اولین فایل خود را آپلود کنید." — above the upload button.

4. Pagination: if the file count exceeds 50, paginate with standard admin pagination (next/prev page links). Default page size: 50 rows.

**Upload flow**

5. An **"آپلود فایل"** button is displayed at the top of the page (above the table).
6. Clicking it reveals an inline upload form containing: a single `<input type="file">` with the allowed `accept=` types and a **آپلود** submit button.
7. On successful upload:
   - File is saved to disk.
   - `MediaFile` record is inserted.
   - Page redirects back to `GET /admin/files/` with the new file at the top.
8. On rejected upload (size or type violation):
   - No file is saved to disk.
   - No DB record is created.
   - Page re-renders with an inline Persian error message:
     - Size: "حجم فایل از حد مجاز بیشتر است ({limit} MB)."
     - Type: "نوع فایل مجاز نیست. فرمت‌های پشتیبانی‌شده: PDF، MP4، WEBM، MOV، XLSX، DOCX، PPTX، CSV، JPG، PNG، WEBP، GIF"

**Copy-to-clipboard**

9. Each file row has a **کپی** button next to its URL.
10. Clicking **کپی** writes the full absolute URL to the system clipboard using the browser Clipboard API (`navigator.clipboard.writeText`).
11. On success: button label changes to **کپی شد ✓** for 2 seconds, then reverts to **کپی**. No server round-trip.
12. If the Clipboard API is unavailable (non-HTTPS context in dev), the URL is selected in an input field so the user can copy manually — this is acceptable fallback behaviour.

**Delete flow**

13. Each row has a **حذف** button.
14. Clicking **حذف** shows a browser `confirm()` dialog: "این فایل حذف شود؟"
15. On confirm:
    - File is removed from disk (`delete_media_file`).
    - `MediaFile` record is deleted from DB.
    - Page redirects back to `GET /admin/files/`.
    - If the file was already missing from disk (e.g., manually deleted), the route handles `FileNotFoundError` gracefully, deletes the DB record, and proceeds — no 500 error.
16. On cancel: nothing happens.

### Routes

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/admin/files/` | Render media library page (paginated file list + upload form) |
| `POST` | `/admin/files/upload` | Receive file upload; validate, save, insert DB record; redirect to list |
| `POST` | `/admin/files/{id}/delete` | Delete file from disk + DB; redirect to list |

All routes require admin authentication (same session guard as all other admin routes).

### Admin UX Flow — Upload

1. Admin navigates to `/admin/files/` via the **رسانه** sidebar link.
2. Admin clicks **آپلود فایل**; the inline upload form expands.
3. Admin selects a file from their local filesystem.
4. Admin clicks **آپلود**.
5. Server validates type and size.
   - **Success path:** file saved to disk, DB record inserted, redirect to `/admin/files/` — the new file appears at the top of the list with its URL and a **کپی** button.
   - **Error path:** page re-renders with an inline Persian error message; admin corrects the file and retries.
6. Admin clicks **کپی** next to the new file's URL.
7. Admin pastes the URL into the desired location (richtext editor, link field, etc.).

### Admin UX Flow — Delete

1. Admin identifies a file in the list they no longer need.
2. Admin clicks **حذف** in that file's row.
3. Browser shows: "این فایل حذف شود؟"
4. Admin confirms.
5. File is deleted from disk and DB. Page reloads; the file no longer appears in the list.

### Out of Scope

- Folder or tag organisation of files.
- Search or filter within the media library (deferred — low value until file count grows; see Open Questions).
- Bulk delete.
- Inserting files directly into a richtext editor from the media library (v10+ — requires editor plugin integration).
- CDN or object storage integration.
- Public access control — all uploaded files are publicly accessible via their static URL. Admin is responsible for not uploading sensitive material.
- Preview thumbnails for images in the list (deferred).
- File rename after upload.

### Open Questions

| Question | Decision |
|----------|----------|
| Should the media library support search/filter? | Deferred — not needed until file count grows to 100+. The table is sortable by date (newest first) and pagination handles scale. Revisit in v10. |
| Should all file types be allowed in a single upload input, or should users pick a category first? | Single `<input type="file">` with a combined `accept=` attribute — simpler UX for a single-user admin. |
| Should `POST /admin/files/upload` stream large video files or buffer entirely? | Buffer entirely for v9 (consistent with all other file uploads in this codebase). For video files near 200 MB, this may need revisiting if Hamravesh imposes request size limits. |

---

## Epic 2 — Book Link Types: Article + Book

### Problem Statement

The book form's "لینک‌های مرتبط" section (renamed in v8 from "ویدیو و پادکست") supports three link types: video, podcast, website. In practice, Milad often links to:

- An article that provides context for the book (e.g., a blog post, a review).
- An external book listing (e.g., Goodreads, Ketabrah, Amazon).

Currently both are filed under "website", which loses the semantic distinction. On the book detail page, all website-type links render with the same 🌐 label — visitors cannot tell if they are about to read an article or view a book listing.

### Target User

- **Admin (Milad):** tagging links correctly when adding them to a book.
- **Visitor:** reading a book detail page and understanding at a glance what kind of resource each link leads to.

### User Stories

| # | As a… | I want to… | So that… |
|---|-------|-----------|---------|
| U7 | Admin | Select "مقاله" when the linked resource is an article | The book detail page shows it with an appropriate article label |
| U8 | Admin | Select "کتاب" when linking to an external book listing | Visitors see a distinct "کتاب" label and know it's a purchase or listing link |
| U9 | Visitor | See clearly labelled link types on a book detail page | I know whether I'm about to read an article or visit a book listing before clicking |

### Data Model

**`MediaLinkType` enum — two new values:**

```python
class MediaLinkType(str, enum.Enum):
    VIDEO   = "video"
    PODCAST = "podcast"
    WEBSITE = "website"   # added v8
    ARTICLE = "article"   # added v9
    BOOK    = "book"      # added v9
```

**No migration required.** `BookMediaLink.type` is `String(20)`. The new string values are stored as-is; no schema change.

**Caution:** The `BOOK = "book"` value must not collide with any other enum or model field named `book`. In the Python enum namespace this is unambiguous; in templates, render via `link.type == "book"` (string comparison) to avoid any shadow issues.

### Acceptance Criteria

**Admin — Book Form (`/admin/books/new` and `/admin/books/{slug}/edit`)**

1. The type dropdown in the "لینک‌های مرتبط" section gains two new options:
   - `مقاله` with value `article`
   - `کتاب` with value `book`
2. Final dropdown option order: ویدیو — پادکست — وبسایت — مقاله — کتاب.
3. Existing links with type `video`, `podcast`, or `website` are unaffected on load and on save.
4. The `+افزودن لینک` button behaviour is unchanged.

**Public — Book Detail Page (`/library/{slug}/`)**

5. Links of type `article` render with a distinct label (e.g., "مقاله" or icon 📄) — different from all other types.
6. Links of type `book` render with a distinct label (e.g., "کتاب" or icon 📖).
7. All link types use the same existing row/card layout — no new layout introduced.
8. All five link types open in a new tab with `target="_blank" rel="noopener noreferrer"`.

### Admin UX Flow — Adding an Article Link to a Book

1. Admin opens `/admin/books/{slug}/edit`.
2. Admin scrolls to the **"لینک‌های مرتبط"** section and clicks **+ افزودن لینک**.
3. A new row appears with a type dropdown and a URL input.
4. Admin selects **مقاله** from the dropdown.
5. Admin enters the article URL.
6. Admin saves the form.
7. On the public book detail page, the link renders with the "مقاله" label.

### Public UX Impact

Before v9, all non-video, non-podcast external links on a book detail page displayed with the "وبسایت" label, regardless of whether they pointed to an article or a book listing. After v9:

- A link to a Virgool article about the book → labelled "مقاله".
- A link to the book's Ketabrah listing → labelled "کتاب".
- An author's homepage → labelled "وبسایت" (unchanged).

Visitors can scan the links section and understand the content type before clicking. The visual distinction is purely label-based (text or emoji) — no new layout is introduced.

### Out of Scope

- Adding `article` or `book` link types to the post or tool forms (not needed — post bodies handle links inline; tool links are download-oriented).
- Filtering or grouping book detail links by type (deferred — low value given typical link counts per book).

### Open Questions

| Question | Decision |
|----------|----------|
| Should `article` and `book` links open in a new tab? | Yes — consistent with all other link types on the book detail page. |
| Icon vs text label? | Use text labels in Persian ("مقاله", "کتاب") consistent with v8's "وبسایت" label. Emoji optional and left to template implementation. |

---

---

## Epic 3 — Admin Books Filter (by Status and Category)

### Problem Statement

The `/admin/books/` list currently loads all books with no filtering. As the library grows, finding a specific book requires scrolling the entire list. Milad commonly needs to view "all draft books" to see what still needs publishing, or "all books in a specific category" to audit coverage. Without filters, this requires visual scanning of the full list.

### Target User

Admin (Milad) — sole CMS user. No public-facing impact.

### User Stories

| # | As a… | I want to… | So that… |
|---|-------|-----------|---------|
| U10 | Admin | Filter the books list by status (draft / published) | I can see at a glance which books are still unpublished |
| U11 | Admin | Filter the books list by category | I can audit coverage across topic areas |
| U12 | Admin | Combine status + category filters | I can find "all draft books in the strategy category" without scrolling |
| U13 | Admin | Clear filters with one click | I can return to the full list quickly |

### Data Model

No model changes required. `Book.status` is an existing `String(20)` column. Categories are already joined via the `book_categories` M2M table. Filters are applied at the service/query level via optional WHERE clauses.

### Acceptance Criteria

**Filter bar on `/admin/books/`**

1. A filter bar appears above the books table containing:
   - A **وضعیت** dropdown with options: "همه" (default), "منتشرشده" (`published`), "پیش‌نویس" (`draft`).
   - A **دسته‌بندی** dropdown populated with all existing categories (from `category_service.list_categories`); first option is "همه دسته‌ها" (default).
   - A **اعمال فیلتر** submit button.
   - A **حذف فیلتر** link (only visible when any filter is active) that navigates back to `/admin/books/` with no query params.
2. The filter bar is a plain HTML `<form method="GET">` — no JavaScript required.
3. Selecting values and submitting the form navigates to `/admin/books/?status=draft&category_id=3` (query params).
4. On page load with active query params, the dropdowns reflect the currently applied values (selected state).

**Filtered results**

5. When `status` is set, only books with that status value are shown.
6. When `category_id` is set, only books that belong to that category are shown.
7. When both are set, both filters apply (AND logic — only books matching both conditions).
8. When neither is set (default), all books are shown (current behaviour, unchanged).
9. The page title or a subtitle line indicates the active filter state, e.g.: "نمایش: پیش‌نویس — استراتژی".
10. The books count shown in the page header (if present) reflects the filtered count, not total.

**Route changes**

11. `GET /admin/books/` accepts two optional query params: `status: str | None` and `category_id: int | None`.
12. Invalid values (e.g., `status=foo`) are silently ignored — the route falls back to "no filter" for that param.

**Service changes**

13. `book_service.list_books()` is extended to accept `status: str | None = None` and `category_id: int | None = None` and applies them as optional WHERE clauses. Existing callers that pass no arguments continue to work unchanged.

### Out of Scope

- Free-text search within the admin books list (deferred — separate feature).
- Sorting by columns (deferred).
- Saved filter presets.
- Filter on the public `/library/` page — this spec is admin-only.

### Open Questions

| Question | Decision |
|----------|----------|
| Should filters persist across page navigations (e.g., stored in session)? | No — query-param-only. Simple, stateless, no server-side session needed. |
| Should the category dropdown show only categories that have at least one book? | No — show all categories. Filtering to non-empty categories adds complexity; admin knows the categories they've defined. |

---

---

## Epic 4 — Admin Book Cover Preview: Fit to Frame

### Problem Statement

When uploading a cover image on the book create/edit form (`/admin/books/new`, `/admin/books/{slug}/edit`), the preview image stretches or overflows its container if the uploaded image dimensions don't match the frame's aspect ratio. This makes it hard to judge crop and composition before saving.

### Target User

Admin (Milad) — affects only the admin book form. No public-facing change.

### User Story

| # | As a… | I want to… | So that… |
|---|-------|-----------|---------|
| U14 | Admin | See the uploaded cover image correctly fitted inside the preview frame | I can judge the image composition without it being stretched or clipped unexpectedly |

### Acceptance Criteria

1. The cover image preview container on the book form has a fixed aspect ratio consistent with how covers are displayed publicly (portrait, approximately 3:4).
2. The preview `<img>` uses `object-fit: cover` so the image fills the frame without distortion, cropping from the centre if needed — the same behaviour as the public library card.
3. The preview container has `overflow: hidden` so no image content bleeds outside the frame boundary.
4. The fix applies both to:
   - **New image selected** — the live JS preview shown immediately after the user picks a file.
   - **Existing cover on edit** — the `<img>` rendered server-side when loading an existing book for editing.
5. No change to how the image is stored or served — this is purely a CSS/template fix.

### Out of Scope

- Changing the actual image dimensions at upload time (cropping server-side).
- A drag-to-reposition crop tool.

---

---

## Epic 5 — Rename "بلاگ" to "یادداشت" (Public Pages)

### Problem Statement

The blog section is currently labelled "بلاگ" everywhere in the public-facing UI. The word "یادداشت" (note / memo) better reflects the nature of the content — short, personal reflections from a PM's perspective — and fits the site's tone as a personal encyclopedia rather than a generic blog.

### Target User

All public visitors — the change is purely copy/label; no behaviour changes.

### Acceptance Criteria

The following locations must be updated from "بلاگ" to "یادداشت". Admin-panel labels are **out of scope** — admin-side copy stays unchanged.

| Location | File | Current text | New text |
|----------|------|-------------|---------|
| Main nav link (all public pages) | `templates/base.html` | `بلاگ` | `یادداشت` |
| Blog list page heading | `templates/pages/blog.html` | `<h1>بلاگ</h1>` | `<h1>یادداشت</h1>` |
| Post detail breadcrumb | `templates/pages/post_detail.html` | `بلاگ` | `یادداشت` |
| Post detail back link | `templates/pages/post_detail.html` | `بازگشت به بلاگ` | `بازگشت به یادداشت‌ها` |

### Out of Scope

- URL path `/blog/` — keep unchanged. Renaming the route breaks existing links, SEO, and all internal `url_for('blog')` references. Label change only.
- Admin navigation label (`✍️ بلاگ` in `admin/base.html`) — admin copy is internal; no visitor impact.
- Admin form hint text that mentions "بلاگ" inline — low visibility, no visitor impact.
- `page_title` context values passed from routes — update only if they appear visibly in the `<title>` tag or page headings seen by visitors.

### Open Questions

| Question | Decision |
|----------|----------|
| Should `/blog/` route be renamed to `/notes/` or `/yaddasht/`? | No — deferred indefinitely. URL changes break SEO and require redirects; label-only change delivers the copy intent with zero risk. |
| Should the `<title>` tag on the blog list page say "یادداشت"? | Yes — if `page_title` is rendered in the browser `<title>`, update it to match. |

---

## Implementation Order

All five epics are fully independent. Recommended sequence:

1. **Epic 5 (بلاگ → یادداشت rename)** — ~10 minutes; 4 string replacements across 2 template files. Zero risk, zero migration.
2. **Epic 4 (Cover Preview Fit)** — ~15 minutes; two CSS properties on the preview `<img>` and container. Zero risk, zero migration.
3. **Epic 2 (Book Link Types)** — ~30 minutes; enum extension + template tweak, zero risk, no migration.
4. **Epic 3 (Admin Books Filter)** — ~2–3 hours; query param routing, service filter args, template filter bar. No migration, no new model.
5. **Epic 1 (Media Library)** — new model, migration, service functions, new admin route + template + JS clipboard logic. Estimated 1–2 days.

All five can deploy in a single release. Epics 2–5 can ship first if Epic 1 needs more time.

---

## NFRs

### Layout and RTL

- The `/admin/files/` page follows the existing admin card/table layout and RTL conventions — same component structure as `/admin/contact/`, `/admin/tools/`, etc.
- The upload form, table, and error messages are all RTL.
- The URL display in the **لینک** column is LTR (URLs are LTR by nature); apply `dir="ltr"` inline or via a utility class to prevent RTL rendering of the URL string.

### File Upload Security

- Server-side validation is mandatory: MIME type, file extension, and size checked before saving to disk.
- Files are saved with UUID-based names — original filenames are never used as filesystem paths.
- Uploaded files are served as static assets; they are not executed server-side.
- No `.html`, `.js`, `.php`, `.py`, or other executable extensions are permitted, even if accidentally passed.

### Performance

- The `/admin/files/` page paginates at 50 rows per page. The underlying query uses `LIMIT`/`OFFSET` and does not load all `MediaFile` rows into memory.
- File upload is synchronous (no async upload progress bar in v9); for files under ~50 MB the UX is acceptable. For large videos (up to 200 MB), the form may take several seconds to submit — no explicit timeout.
- The copy-to-clipboard action is purely client-side — zero server round-trips.

### Data Integrity

- `MediaFile` records and disk files must stay in sync. The delete route must:
  1. Attempt disk file removal first.
  2. Handle `FileNotFoundError` gracefully (log a warning, do not raise 500).
  3. Delete the DB record regardless of whether the disk file was found.
- If upload fails mid-stream (e.g., disk full), no partial DB record should be inserted.

### Mobile Friendliness

- The admin panel is primarily a desktop tool. The `/admin/files/` page must be usable on a tablet-sized screen (the table may scroll horizontally on narrow viewports). No specific mobile breakpoint work required.

---

## Success Metrics

v9 is done when all of the following are true:

**Epic 1 — Media Library**
- [ ] `media_files` table exists in production (migration applied).
- [ ] `static/uploads/media/` directory exists and is writable.
- [ ] Uploading a valid file from `/admin/files/` saves it to disk, creates a DB record, and returns a working public URL.
- [ ] Uploading a file that exceeds the size limit returns a Persian error message; no file is saved.
- [ ] Uploading a disallowed extension returns a Persian error message; no file is saved.
- [ ] The **کپی** button copies the full absolute URL to clipboard and shows the "کپی شد ✓" confirmation.
- [ ] The **حذف** button with confirmation deletes the file from disk and DB.
- [ ] Deleting a file whose disk record is already missing does not raise a 500 error.
- [ ] The **"رسانه"** link appears in the admin sidebar.
- [ ] The empty state renders correctly when no files have been uploaded.
- [ ] Pagination renders correctly when more than 50 files exist.

**Epic 2 — Book Link Types**
- [ ] `MediaLinkType.ARTICLE` and `MediaLinkType.BOOK` exist in the Python enum.
- [ ] The book form type dropdown shows "مقاله" and "کتاب" options in the correct order.
- [ ] Saving a book with an `article` or `book` link persists the correct type value.
- [ ] The book detail page renders "مقاله" and "کتاب" labels distinctly from "وبسایت", "ویدیو", and "پادکست".
- [ ] Existing books with `video`, `podcast`, or `website` links are unaffected.

**Epic 3 — Admin Books Filter**
- [ ] Filter bar appears on `/admin/books/` with وضعیت and دسته‌بندی dropdowns.
- [ ] Submitting the filter bar appends `status` and/or `category_id` as GET query params.
- [ ] Active filter values are reflected in the dropdown selected state on page load.
- [ ] Filtering by `status=draft` returns only draft books.
- [ ] Filtering by `status=published` returns only published books.
- [ ] Filtering by `category_id` returns only books in that category.
- [ ] Combined status + category filter applies AND logic.
- [ ] No-filter default returns all books (existing behaviour unchanged).
- [ ] "حذف فیلتر" link is visible when a filter is active and clears all filters on click.
- [ ] Invalid query param values (e.g., `status=foo`) are silently ignored — full list shown.
- [ ] `book_service.list_books()` existing callers with no arguments are unaffected.

**Epic 5 — بلاگ → یادداشت Rename**
- [ ] Main nav link on all public pages shows "یادداشت" (not "بلاگ").
- [ ] Blog list page `<h1>` reads "یادداشت".
- [ ] Post detail breadcrumb reads "یادداشت".
- [ ] Post detail back link reads "بازگشت به یادداشت‌ها".
- [ ] `/blog/` URL and all `url_for('blog')` references are unchanged.
- [ ] Admin navigation label is unchanged.

**Epic 4 — Admin Book Cover Preview**
- [ ] Cover preview container has a fixed portrait aspect ratio (~3:4) consistent with public library cards.
- [ ] Preview `<img>` uses `object-fit: cover` — no stretching regardless of uploaded image dimensions.
- [ ] Preview container has `overflow: hidden` — no image bleed outside the frame.
- [ ] Fix applies to the live JS preview (new file selected) and the server-rendered existing cover (edit form).
- [ ] Image storage and public serving are unchanged.

---

## Deployment Status

| Field | Value |
|-------|-------|
| **Status** | Shipped |
| **Deploy date** | July 2026 |
| **Platform** | Hamravesh Darkube (production) |
| **Notes** | All five epics deployed |

---

*July 2026 — v9 shipped. v1–v9 all shipped. v10 is next.*
