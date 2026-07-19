# Product Spec v9 — Media Library + Book Link Types

**Version:** v9  
**Status:** Planned  
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

Both epics are fully independent. Feature 2 can ship ahead of Feature 1.

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

## Implementation Order

The two epics are fully independent. Recommended sequence:

1. **Epic 2 (Book Link Types)** — ~30 minutes; enum extension + template tweak, zero risk, no migration. Can ship immediately.
2. **Epic 1 (Media Library)** — new model, migration, service functions, new admin route + template + JS clipboard logic. Estimated 1–2 days.

Both can deploy in a single release. If time-boxing is needed, Epic 2 can ship first.

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

---

## Deployment Status

| Field | Value |
|-------|-------|
| **Status** | Not deployed |
| **Deploy date** | — |
| **Platform** | Hamravesh Darkube (production) |
| **Notes** | Pending implementation |

---

*July 2026 — v9 spec written and enhanced. v1–v8 all shipped. v9 is next.*
