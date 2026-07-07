---
name: project-v4-shipped
description: v4 Book Engagement is shipped — BookRating/BookComment models, rating widget, moderated comments, admin book comments section
metadata:
  type: project
---

v4 Book Engagement is fully implemented and shipped as of July 2026.

**What shipped:**
- `BookRating` and `BookComment` models in `app/models/book.py`
- Alembic migration `008_add_book_engagement.py`
- Service functions in `app/services/books.py`: `rate_book`, `has_rated_book`, `add_book_comment`, `list_book_comments`, `get_book_comment`, `set_book_comment_status`, `delete_book_comment`
- Web routes: `POST /library/{slug}/rate/` and `POST /library/{slug}/comment/`
- Admin routes: `GET /admin/books/comments/`, approve/reject/delete POSTs
- Templates: `book_detail.html` (rating widget + comments section), `admin/book_comments_list.html`
- Admin nav restructured into 4 groups: کتابخانه (کتاب‌ها، دسته‌بندی‌ها، نظرها), بلاگ (یادداشت‌ها، نظرها), ابزارها (قالب‌ها), عمومی (درباره من)

**Why:** Completes the engagement loop for library books, mirroring the v2 Blog pattern.

**How to apply:** v4 is done — next recommended priority is v5 Newsletter + Contact. Do not treat Book Engagement as backlog or planned when giving roadmap guidance.

**Related:** [[project-overview]]
