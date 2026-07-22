---
name: project-v10-planned
description: v10 PRD written — Post Related Books (admin widget + public display) — planned, not yet shipped
metadata:
  type: project
---

v10 PRD written and saved to `docs/product-spec-v10.md` (July 2026).

**Context:** The `Post.related_books` M2M and `post_books` join table were created in v8. The admin route (`/posts/new/`, `/posts/{slug}/edit/`) already accepts `related_book_ids` and `all_books` is passed to the template. But the template has no widget, and the public post detail page never renders them. v10 fixes both halves.

**Epic 1 — Admin Post Form Widget:** Add a book picker to `post_form.html` (same template for new and edit). No route or service changes needed — only template work. Pre-select existing associations on edit. Serialise IDs into the existing `related_book_ids` hidden input as JSON array.

**Epic 2 — Public Post Detail Display:** Render `post.related_books` on `/blog/{slug}/` below the body, above comments. Conditional — section hidden when no related books. No new DB query; data already loaded via `selectin`. Template-only change.

**Why:** v8 left the feature half-built — admin-side storage wired but no UI to set it, and no public display. v10 completes it.

**How to apply:** Both epics are template-only, zero migration, ~2–3 hours total. Ship together in one release. [[project-v9-shipped]]
