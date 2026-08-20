---
name: project-shipped-versions
description: Which versions of petfeature.ir are shipped vs planned, and key architectural decisions per version
metadata:
  type: project
---

## Shipped: v1–v9, v11.5 (partial), v13 (partial)

- v1–v9: all shipped (library, blog, tools, engagement, contact, analytics, replies, content enhancements, media library)
- v11 (email newsletter): REMOVED FROM THE PRODUCT (July 2026). Telegram is the only subscription channel — never re-add an email form.
- v11.5: Telegram channel CTA in footer + contact page sidebar (no bot, no email — just a join link)
- v13: Telegram digest AI draft agent — admin composes newsletters, copies manually to Telegram. No bot sending (Telegram API blocked in Iran on prod). Uses GapGPT proxy. Campaign log at /admin/newsletters/.

## Key v13 decisions
- No auto-post, no per-item send buttons
- Admin copies text → pastes to Telegram manually → clicks "ثبت به عنوان ارسال‌شده" to record cutoff date
- AI prompt generates plain text (no HTML tags) — suitable for manual paste
- GapGPT API key in .env as GAPGPT_API_KEY (never in config.py defaults)

## Shipped locally (pending deploy): v12, v14

### v12 — User Auth (Google OAuth)
- UserAuthMiddleware, Google OIDC, /login/ /profile/ /auth/google/callback/, admin user list
- JWK patch: `StarletteOAuth2App.parse_id_token` patched to fall back to raw JWT decode when googleapis.com/oauth2/v3/certs returns 403 (Hamravesh Iran blocks it)
- Middleware order: Analytics (outer) → Session → UserAuth (inner) → App
- Google credentials: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI in .env
- Accent color swatch on profile page: stored in localStorage as `pf-accent`

### v14 — User Dashboard
- Newsletter: STILL TO REMOVE — `Subscriber` model, `POST /profile/newsletter/subscribe|unsubscribe/` routes, admin subscribers page, and the `subscribers` table (needs a drop-table migration). Keep `NewsletterCampaign` — v13 uses it.
- My Comments: PostComment + BookComment got nullable user_id FK (migration 29be8a288138, SQLite-safe — FK constraints only applied on PostgreSQL)
- Comment attribution: web routes for book_comment and post_comment now call get_current_user(request) and pass user_id to service
- get_user_comments() merges PostComment + BookComment queries in Python, sorts by created_at DESC, paginates 10/page
- UserComment dataclass with kind, status_label, body_truncated computed properties

### v15 — Bookshelf (قفسه کتاب)
- New model: ReadingListItem (reading_list_items table) with unique constraint on (user_id, book_id); migration 26fbca410424
- Service: app/services/bookshelf.py — upsert_item returns (item, newly_read) to trigger review modal on first "read" transition
- Routes in auth_routes.py: GET /profile/bookshelf/, POST /profile/bookshelf/add/, POST /profile/bookshelf/remove/
- book_detail route now passes shelf_item, save_count, open_review to template
- Review modal: triggered by ?review=<book_id> param; reuses v4 book_rate + book_comment endpoints; no new models
- Admin: books_list now shows "در قفسه" save count column via get_all_book_save_counts()
- SQLite note: reading_list_items migration was hand-written (autogenerate kept re-detecting v14 FK gaps)
