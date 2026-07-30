# Product Spec v10 — Post Related Books

**Version:** v10  
**Status:** Planned  
**Author:** Milad Mirzaei  
**Date:** July 2026  
**Depends on:** v1–v9 (all shipped)

---

## Overview

v10 completes a feature that was half-built in v8. The `Post.related_books` M2M relationship and the `post_books` join table were created in v8, and the admin route already accepts `related_book_ids` on both `POST /posts/new/` and `POST /posts/{slug}/edit/`. However, the admin `post_form.html` template never received a UI widget to select books, and the public post detail page never renders them.

v10 delivers both halves:

| # | Epic | Scope | Migration? |
|---|------|-------|-----------|
| 1 | Admin Post Form — Related Books Widget | Add a book picker to `post_form.html` | No — model + route already wired |
| 2 | Public Post Detail — Related Books Section | Render `post.related_books` on the post detail page | No — data already loaded via `selectin` |

Both epics are fully independent but related — ship them together.

---

## Epic 1 — Admin Post Form: Related Books Widget

### Problem Statement

The admin post form (`/admin/posts/new/` and `/admin/posts/{slug}/edit/`) has no UI to associate related books with a post. The underlying infrastructure exists — the route receives `related_book_ids`, the service saves them, and `all_books` is already passed to the template context. The template simply never renders a widget for it. Any related books set on a post were effectively invisible and un-editable from the admin.

### Target User

Admin (Milad) — sole CMS user. No direct public-facing change from this epic alone (Epic 2 handles display).

### User Stories

| # | As a… | I want to… | So that… |
|---|-------|-----------|---------|
| U1 | Admin | Select one or more books from the library when creating or editing a post | The post is associated with those books and they appear on the public post page |
| U2 | Admin | See which books are already associated with a post when I open it for editing | I can review and change the associations without losing existing data |
| U3 | Admin | Remove a book association from a post | I can correct mistakes or update associations as content evolves |

### Acceptance Criteria

**Widget placement**

1. A **"کتاب‌های مرتبط"** section appears in `post_form.html` below the body/content section and above the form action buttons.
2. The widget uses the same multi-select book picker pattern already used in the tool form — a searchable list or checkbox group of all books from `all_books`, rendered with book title and author.

**New post (`/admin/posts/new/`)**

3. All books are shown unselected by default.
4. Admin selects one or more books and saves the form.
5. The selected books are saved as `related_books` on the new post.

**Edit post (`/admin/posts/{slug}/edit/`)**

6. Books already associated with the post are pre-selected when the form loads.
7. Admin can add or remove selections and save.
8. The updated set of related books is persisted correctly (existing associations not in the new selection are removed; new ones are added).

**No books available**

9. If `all_books` is empty (no books in the library yet), the section shows: "هنوز کتابی در کتابخانه ثبت نشده."

**Hidden input**

10. The widget serialises selected book IDs into the existing `related_book_ids` hidden input as a JSON array (e.g. `[1, 3, 7]`) — consistent with how the tool form and book form handle M2M relationships. No route or service changes are needed.

### Out of Scope

- Adding related posts to a post form (separate concept, not requested).
- Reordering related books (display order is by book title or insertion order; no drag-sort in v10).

---

## Epic 2 — Public Post Detail: Related Books Section

### Problem Statement

Even when a post has related books saved, the public post detail page (`/blog/{slug}/`) never displays them. The `Post` model loads `related_books` eagerly via `lazy="selectin"`, so the data is available in the template context — it is simply never rendered. Visitors miss a key navigation path from blog content into the library.

### Target User

Visitors reading a blog post — the primary audience for this feature.

### User Stories

| # | As a… | I want to… | So that… |
|---|-------|-----------|---------|
| U4 | Visitor | See the books related to a post I'm reading | I can explore the library entries that inspired or informed the content |
| U5 | Visitor | Click a related book and go directly to its library page | I can read the full book notes without searching |

### Acceptance Criteria

**Section visibility**

1. A **"کتاب‌های مرتبط"** section is rendered on the post detail page when `post.related_books` is non-empty.
2. When `post.related_books` is empty (no associated books), the section is not rendered at all — no empty state placeholder.

**Section placement**

3. The section appears **below the post body and above the comments section**.

**Book cards**

4. Each related book is shown as a compact card containing:
   - Book cover image (with a fallback placeholder if no cover is set)
   - Book title
   - Author name(s)
   - A link to `/library/{book.slug}/`
5. Cards link to the book detail page. The entire card area is clickable (not just the title).
6. Layout: horizontal scroll row on mobile; grid (2–3 columns) on desktop — consistent with how related books appear elsewhere on the site if applicable.

**Route change**

7. No route change is needed. `post.related_books` is already loaded via `selectin` on the `Post` model and is available in the template context.

### Out of Scope

- Showing a "related posts" section on the post detail page.
- Showing the number of posts that reference a book on the book detail page (deferred — interesting but low priority).
- Filtering or sorting related books on the post detail page.

---

## Implementation Order

Recommended sequence (both should ship together in one release):

1. **Epic 1 (Admin Widget)** — ~1–2 hours. Copy the book picker pattern from an existing form (tool form or book form). No route or service changes needed — only template work.
2. **Epic 2 (Public Display)** — ~30–60 minutes. Template-only: add the related books section to `post_detail.html`, conditional on `post.related_books` being non-empty.

---

## NFRs

### RTL / Persian
- Section heading "کتاب‌های مرتبط" is Persian and RTL.
- Book cards follow the same RTL layout as library cards used elsewhere.

### Performance
- No additional DB query introduced. `related_books` is already loaded by the `selectin` loader on `Post`. Route context unchanged.

### Consistency
- The admin widget must match the existing book-picker pattern in the tool form (`post_form.html` uses the same `all_books` variable pattern as tool_form).
- The public book card design must match or closely resemble how book cards appear on `/library/`.

---

## Success Metrics

v10 is done when all of the following are true:

**Epic 1 — Admin Post Form Widget**
- [ ] "کتاب‌های مرتبط" section appears in the post form (new and edit).
- [ ] `all_books` list is rendered as a selectable widget in the section.
- [ ] On edit, books already associated with the post are pre-selected.
- [ ] Saving the form persists the selected book associations correctly.
- [ ] Removing a previously selected book and saving removes the association.
- [ ] Empty state ("هنوز کتابی در کتابخانه ثبت نشده") shown when library is empty.

**Epic 2 — Public Post Detail Display**
- [ ] "کتاب‌های مرتبط" section appears on the post detail page when related books exist.
- [ ] Section is absent when no related books are associated.
- [ ] Each book card shows cover, title, and author and links to `/library/{slug}/`.
- [ ] Section is positioned below the post body and above comments.
- [ ] No new DB query or route change introduced.

---

## Deployment Status

| Field | Value |
|-------|-------|
| **Status** | Not deployed |
| **Deploy date** | — |
| **Platform** | Hamravesh Darkube (production) |
| **Notes** | Pending implementation |

---

*July 2026 — v10 spec written. v1–v9 all shipped. v10 is next.*
