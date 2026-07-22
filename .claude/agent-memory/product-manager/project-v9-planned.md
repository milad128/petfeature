---
name: project-v9-shipped
description: v9 shipped July 2026 — Media Library + Book Link Types + Admin Books Filter + Cover Preview Fit + بلاگ→یادداشت rename
metadata:
  type: project
---

v9 PRD written and saved to `docs/product-spec-v9.md` (July 2026). Three epics, all admin-facing, no public-page changes. `product-spec.md` index already references it.

**Epic 1 — Media Library:** New `MediaFile` model + `/admin/files/` admin page. Upload any file (PDF, video, document, image), browse all assets, copy full absolute URLs to clipboard, delete files. New `static/uploads/media/` directory. Alembic migration required (`media_files` table). UUID-based filenames. Pagination at 50 rows/page.

**Epic 2 — Book Link Types:** Extend `MediaLinkType` enum with `ARTICLE = "article"` and `BOOK = "book"`. No migration. Admin book form dropdown gains "مقاله" and "کتاب" options. Book detail page renders distinct labels for each type.

**Epic 3 — Admin Books Filter:** Filter bar on `/admin/books/` with وضعیت (draft/published) and دسته‌بندی (category) dropdowns. Plain HTML GET form, no JS. Query params `status` and `category_id`. AND logic when both are set. `book_service.list_books()` extended with optional filter args; no migration required.

**Status:** Shipped July 2026. All five epics deployed. v10 is next. [[project-v8-planned]]
