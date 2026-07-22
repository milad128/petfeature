---
name: project-v8-planned
description: v8 Content Enhancements shipped July 2026 — three independent admin/model improvements
metadata:
  type: project
---

v8 spec written July 2026. Three independent features, all buildable in one release.

1. **Book media links — website type:** Add `WEBSITE = "website"` to `MediaLinkType` enum + option in book form dropdown. Section title changes to "لینک‌های مرتبط". No migration needed (String column). Public book page renders website links with distinct label/icon.

2. **Post related books:** New `post_books` join table. `Post` model gets `related_books` relationship (mirrors `tool_books` pattern). Admin post form gains a "کتاب‌های مرتبط" section using the same chip + modal picker pattern from the tool form. Post detail page shows related book cards (cover, title, author) below body, above comments. Alembic migration required.

3. **Tool downloadable links:** `ToolFile` gets `item_type VARCHAR(10) DEFAULT 'file'` column (`"file"` or `"link"`). For link entries, the existing `file` column stores the external URL. Admin form adds `+ افزودن لینک` button; link rows show a URL input instead of file upload. Public tool page visually unchanged except link entries show "لینک" as the type badge. Links DO increment `download_count` (confirmed — links point to externally hosted files, so the click is semantically a download). Alembic migration required.

**Why:** All three fill gaps in existing shipped features without adding new pages or epics. Scope is narrow and well-defined.

**How to apply:** Treat features as independent — can be built in parallel or sequenced (Feature 1 first, no migration; then 3, then 2). Spec at `docs/product-spec-v8.md`. Index updated in `docs/product-spec.md`.
