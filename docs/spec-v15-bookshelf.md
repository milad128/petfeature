# Product Spec v15 — پت فیچر (Bookshelf / قفسه کتاب)

> **Prerequisite:** [Product Spec v12](./spec-v12-user-auth.md) (User Auth) must be shipped · **Parent:** [Product overview](./spec.md)

## 1. Summary

| Field | Value |
|-------|-------|
| **Version** | v15 — Bookshelf (قفسه کتاب) |
| **Status** | Backlog |
| **Goal** | Let registered users build a personal bookshelf — saving books with a reading status — so they can track their PM learning journey |
| **Builds on** | v12 (User Auth), v1 (Book Library) |
| **Epic** | Bookshelf |

**Scope in two sentences:** Add a personal bookshelf feature where logged-in users can save any book from the library with one of three reading statuses (می‌خواهم بخوانم / در حال خواندن / خواندم). The bookshelf is private, accessible from the user's profile, and each book detail page shows a public aggregate save count as a social proof signal. When a user marks a book as "خواندم", a modal prompts them to optionally rate and comment on it — turning the status update into a natural review moment.

**Renamed from:** "Reading List" (لیست مطالعه) → **Bookshelf** (قفسه کتاب) — more evocative, matches the library metaphor already established in v1.

---

## 2. Problem & Goals

**Problem:** Users browse the book library but have no way to mark books they want to read or track what they've already read. There is no personal layer on the site — every visit starts from scratch. This limits return visits and reduces the perceived value of the library for serious PM learners.

**v15 goals:**

- **Save:** Let users add any book to their personal bookshelf with one click
- **Track:** Let users assign a reading status to each saved book (want / reading / read)
- **Review:** When a user marks a book as read, prompt them to rate and comment — capturing reviews at the moment of highest motivation
- **Revisit:** Give users a dedicated page to see and manage their bookshelf
- **Signal:** Show an aggregate save count on book detail pages as social proof for undecided readers
- **Admin insight:** Surface bookshelf save counts in the admin books list to identify high-demand titles

---

## 3. User Stories

- *As a registered user, I want to save a book to my bookshelf from the book detail page so I don't lose track of books I want to read*
- *As a registered user, I want to set a reading status (want / reading / read) for each saved book so I can track my progress*
- *As a registered user, I want to be prompted to rate and comment when I mark a book as read so I can share my thoughts while the experience is fresh*
- *As a registered user, I want to be able to skip the review prompt so I can mark a book as read without being forced to write anything*
- *As a registered user, I want to view all my saved books in one place so I can manage my reading plan*
- *As a registered user, I want to remove a book from my bookshelf so I can keep it tidy*
- *As a visitor, I want to see how many users have saved a book so I can gauge how popular it is*
- *As Milad (admin), I want to see how many users saved each book so I know which titles resonate most*

---

## 4. Feature Detail

### 4.1 "افزودن به قفسه" Button — Book Detail Page

- A button appears on every book detail page below the book metadata
- **Unauthenticated users:** Button label is "افزودن به قفسه" — clicking redirects to the login page (`/auth/login/?next=/library/{slug}/`)
- **Authenticated users, book not saved:** Button label "افزودن به قفسه" — clicking opens a status picker inline (see §4.2)
- **Authenticated users, book already saved:** Button shows the current status label (e.g. "در حال خواندن ✓") and is styled as active; clicking opens the status picker to change or remove

**Button states:**

| State | Label | Style |
|-------|-------|-------|
| Not logged in | افزودن به قفسه | Secondary/outlined |
| Logged in, not saved | افزودن به قفسه | Primary |
| Saved — می‌خواهم بخوانم | می‌خواهم بخوانم ✓ | Active/filled |
| Saved — در حال خواندن | در حال خواندن ✓ | Active/filled |
| Saved — خواندم | خواندم ✓ | Active/filled |

### 4.2 Status Picker

- Appears inline below the button (no modal, no page reload — use a small JS toggle or a form POST with redirect)
- Three options rendered as radio buttons or pill selectors:
  - می‌خواهم بخوانم
  - در حال خواندن
  - خواندم
- A "حذف از قفسه" link at the bottom of the picker removes the item entirely
- Selecting a status saves immediately (form POST); page reloads with the new button state
- **Special case — selecting "خواندم":** after the status is saved, a review modal opens (see §4.3). All other status selections (want / reading) save silently with no modal
- **No JavaScript required for core save** — form POST is the primary path; JS can enhance with no-reload update if desired. The review modal is a progressive enhancement (see §4.3 fallback)

### 4.3 "خواندم" Review Modal — Rate & Comment

When a user marks a book as **خواندم** (read), prompt them to rate and comment on it. This captures reviews at the moment of highest motivation — right after they finish a book.

**Trigger:**
- Fires only when the status transitions **to** `read` (from the book detail status picker)
- Does **not** fire when re-selecting `read` on a book already marked read (avoids nagging)
- Does **not** fire for `want` or `reading` selections
- Also available from the Bookshelf page when changing a book's status to `read`

**Modal content:**

```
┌─────────────────────────────────────────┐
│  کتاب را خواندی! نظرت چیه؟            ✕ │
│                                           │
│  [ book title + cover thumbnail ]         │
│                                           │
│  امتیاز شما:   ☆ ☆ ☆ ☆ ☆                │
│                                           │
│  نظر شما (اختیاری):                       │
│  ┌─────────────────────────────────────┐ │
│  │                                     │ │
│  └─────────────────────────────────────┘ │
│                                           │
│  [ ثبت نظر ]        [ بعداً / رد کردن ]  │
└─────────────────────────────────────────┘
```

- **Headline:** «کتاب را خواندی! نظرت چیه؟»
- **Star rating:** 1–5 interactive stars — reuses the existing v4 book rating component
- **Comment textarea:** optional, labeled «نظر شما (اختیاری)»
- **Primary CTA:** «ثبت نظر» — submits rating + comment
- **Dismiss:** «بعداً» link, × icon, overlay click, or Escape — closes without saving a review (the `read` status is already saved regardless)

**Reuses existing v4 infrastructure — no new rating/comment models:**
- **Rating** → existing `BookRating` model (v4). One rating per visitor/user per book; upsert on the existing dedup key
- **Comment** → existing `BookComment` model (v4). Submitting the comment goes through the **existing moderation queue** — it is **not** auto-approved. Standard v4 rate limiting and moderation apply
- The modal is a convenient entry point into v4 features, not a parallel system

**Submission rules:**
- Both fields are optional, but at least one (rating **or** comment) must be provided for «ثبت نظر» to submit; if both are empty, the button is disabled
- Rating submits immediately and appears in the book's average (v4 behaviour — ratings are not moderated)
- Comment enters the moderation queue → shows «نظر شما ثبت شد و پس از تأیید نمایش داده می‌شود» on success
- If the user already rated/commented this book previously, pre-fill the modal with their existing rating and show a note that a new comment will replace the pending one (or add another — follow existing v4 comment behaviour)

**No-JavaScript fallback:**
- The core `read` status still saves via form POST without the modal
- Users without JS can still rate/comment through the existing v4 rating and comment forms already present on the book detail page
- The modal is an enhancement layered on top — it never blocks the status change

### 4.4 Social Proof Counter — Book Detail Page

- Displayed near the save button: **«X نفر این کتاب را در قفسه‌شان دارند»**
- Only shown when count ≥ 2 (hide at 0 or 1 to avoid showing empty signal)
- Count = total distinct `user_id` values with a `ReadingListItem` for this book
- Updates on every page load (no caching needed at current traffic scale)

### 4.5 Bookshelf Page — `/profile/bookshelf/`

- Requires authentication — redirect to login if unauthenticated
- Accessible from the user profile nav (added in v12/v14)

**Layout:**

```
[ قفسه کتاب من ]

[ Summary: X کتاب در قفسه | Y خواندم | Z در حال خواندن ]

[ Book card list — sorted by date added, newest first ]

[ Empty state if no books saved ]
```

**Book card on Bookshelf page:**

| Element | Notes |
|---------|-------|
| Cover thumbnail | Same as library list |
| عنوان | Links to `/library/{slug}/` |
| نویسنده | Plain text |
| وضعیت | Status badge (می‌خواهم بخوانم / در حال خواندن / خواندم) |
| تغییر وضعیت | Inline status change — three pill options |
| تاریخ افزودن | Jalali date (using `jalali.py`) |
| حذف | Small remove link/button; confirms via standard form POST |

**Empty state:**
> «هنوز کتابی به قفسه‌ات اضافه نکردی. از کتابخانه شروع کن.»
> [رفتن به کتابخانه →]

**Summary bar:** Three counts at the top of the page — total books, read count, currently reading count. Computed from the user's `ReadingListItem` rows.

### 4.6 Admin — Books List Enhancement

- Add a **"در قفسه"** column to `/admin/books/` showing the all-time save count per book (distinct user count from `ReadingListItem`)
- Column is sortable (descending) so Milad can see the most-saved books at a glance
- Count is all-time, no period filter (consistent with existing analytics columns on admin list pages)

---

## 5. Data Model

### New model: `ReadingListItem`

```python
class ReadingListItem(Base):
    __tablename__ = "reading_list_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="want"
    )
    # status values: "want" | "reading" | "read"
    # Persian labels: "می‌خواهم بخوانم" | "در حال خواندن" | "خواندم"
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="uq_reading_list_user_book"),
    )
```

**Relationships:**
- `user_id` → `users.id` (v12 User model)
- `book_id` → `books.id` (existing Book model)
- Unique constraint on `(user_id, book_id)` — one entry per user per book; update status via upsert

**Status ENUM values (stored as strings):**

| DB value | Persian label |
|----------|---------------|
| `want` | می‌خواهم بخوانم |
| `reading` | در حال خواندن |
| `read` | خواندم |

### Migration

One Alembic migration: create `reading_list_items` table with the unique constraint and indexes on `user_id`, `book_id`, and `added_at`.

---

## 6. Routes

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/profile/bookshelf/` | Required | User's bookshelf page |
| `POST` | `/profile/bookshelf/add/` | Required | Add or update a book's status |
| `POST` | `/profile/bookshelf/remove/` | Required | Remove a book from the bookshelf |

All three routes live in `app/web/routes.py`. Business logic in `app/services/bookshelf.py` (new file).

**POST body for add/update:**
```
book_id=<int>&status=<want|reading|read>
```
Uses SQLAlchemy upsert (INSERT … ON CONFLICT DO UPDATE) on the unique constraint.

**POST body for remove:**
```
book_id=<int>
```

Both POST routes redirect back to the referring page (book detail or bookshelf) after the action — standard PRG pattern.

**Review modal trigger:** When `status=read` is newly set (status transitions to `read`), the add/update route redirects back with a query flag (e.g. `?review=<book_id>`) so the book detail page opens the review modal on load. The modal itself submits to the **existing v4 rating and comment endpoints** — no new routes are added for rating or commenting.

**Review submission:** Reuses existing v4 endpoints:
- Rating → existing book rating POST endpoint (v4)
- Comment → existing book comment POST endpoint (v4), with existing moderation + rate limiting

---

## 7. Service Layer — `app/services/bookshelf.py`

New functions:

| Function | Purpose |
|----------|---------|
| `get_user_bookshelf(user_id)` | Returns all `ReadingListItem` rows for user, ordered by `added_at DESC`, joined with `Book` |
| `get_item_for_book(user_id, book_id)` | Returns the single `ReadingListItem` or `None` — used to set button state on book detail |
| `upsert_item(user_id, book_id, status)` | Insert or update status; raises `ValueError` if status not in allowed set; returns whether the status newly transitioned to `read` (so the route can trigger the review modal) |
| `remove_item(user_id, book_id)` | Delete the item; no-op if not found |
| `get_book_save_count(book_id)` | Returns distinct user count — used for social proof counter on book detail |
| `get_all_book_save_counts()` | Returns `{book_id: count}` dict — used for admin books list column |
| `get_bookshelf_summary(user_id)` | Returns `{total, want, reading, read}` counts — used for summary bar |

---

## 8. Template Changes

| Template | Change |
|----------|--------|
| `app/templates/pages/book_detail.html` | Add save button + status picker + social proof counter + review modal (opens when `?review=<book_id>`); modal reuses v4 rating + comment forms |
| `app/templates/pages/profile_bookshelf.html` | New page — bookshelf list + summary bar + empty state; status change to `read` opens the same review modal |
| `app/templates/admin/books_list.html` | Add "در قفسه" column |

**Note:** The review modal reuses the existing v4 `BookRating` and `BookComment` forms/endpoints — no new rating or comment templates, models, or migrations are introduced.

---

## 9. Acceptance Criteria

### Save button — book detail
- [ ] Unauthenticated users see the button; clicking redirects to login with `?next=` param
- [ ] Authenticated users see correct button state based on whether book is in their bookshelf
- [ ] Selecting a status saves correctly; page reloads with updated state
- [ ] "حذف از قفسه" removes the item; page reloads with default button state
- [ ] Social proof counter shows when count ≥ 2; hidden when count is 0 or 1

### Review modal ("خواندم")
- [ ] Marking a book as `read` (new transition) opens the review modal
- [ ] Re-selecting `read` on an already-read book does NOT open the modal
- [ ] Selecting `want` or `reading` never opens the modal
- [ ] Modal shows interactive 1–5 star rating (reusing v4 component) and an optional comment textarea
- [ ] «ثبت نظر» is disabled until at least a rating or a comment is provided
- [ ] Submitting a rating updates the book's average immediately (v4 behaviour — not moderated)
- [ ] Submitting a comment enters the v4 moderation queue and shows the pending-approval message
- [ ] «بعداً» / × / overlay / Escape all dismiss the modal without saving a review; the `read` status remains saved
- [ ] With JavaScript disabled, marking `read` still saves; user can still rate/comment via the existing v4 forms on the page
- [ ] The `read` status is saved regardless of whether the user submits or dismisses the review

### Bookshelf page
- [ ] `/profile/bookshelf/` redirects unauthenticated users to login
- [ ] Authenticated user sees all saved books, newest first
- [ ] Summary bar shows correct total, read, and reading counts
- [ ] Status change inline form updates correctly
- [ ] Remove action works; page reflects removal
- [ ] Empty state shown when bookshelf has no items
- [ ] Jalali dates displayed throughout

### Admin
- [ ] "در قفسه" column visible on `/admin/books/`
- [ ] Count reflects distinct user saves (all-time)

### Data integrity
- [ ] Duplicate saves (same user, same book) update the status rather than creating a second row
- [ ] Invalid status values are rejected with a 400 error
- [ ] Alembic migration creates table with correct unique constraint and indexes

---

## 10. Out of Scope for v15

| Feature | Reason |
|---------|--------|
| Public/shareable bookshelf URL | Private only (per scope decision) |
| Sort options beyond date added | Date added is sufficient for v15; add later if users request |
| Bookshelf visibility on book detail (e.g. "your friends saved this") | No social graph |
| Import from Goodreads | Post-v15 |
| Notes per book | Post-v15 |
| Reading progress (pages read) | Out of scope — status (want/reading/read) is sufficient |
| Email/push notifications ("you haven't updated your status in 30 days") | Post-v15 |
| Admin: view individual user bookshelves | Post-v15; aggregate counts in admin list are sufficient |
| Reading List on public profile page | Private; no public profile in v15 |

---

## 11. NFRs

- **Authentication:** All bookshelf write actions require a valid session — no anonymous saves
- **Performance:** Save count query on book detail is a single aggregate; acceptable at current traffic. No caching needed for v15
- **RTL:** All labels, buttons, status names in Persian; layout fully RTL-compatible
- **Accessibility:** Status picker must be keyboard-navigable; button states must have distinct ARIA labels
- **No JavaScript required for core functionality:** All save/update/remove actions work via form POST. JS enhancement for no-reload status updates is optional and additive
- **Migration safety:** Alembic migration only adds a new table — no changes to existing tables

---

## 12. Dependencies & Sequencing

| Dependency | Why |
|------------|-----|
| **v12 User Auth** | `ReadingListItem.user_id` requires the `User` model and session auth middleware — cannot build without it |
| **v1 Book Library** | Already shipped — `Book` model and `/library/{slug}/` routes are in place |
| **v4 Book Engagement** | Already shipped — the review modal reuses the existing `BookRating` + `BookComment` models, endpoints, moderation queue, and rating UI component. No new review infrastructure is built |

v15 can be built immediately after v12 ships. It does not depend on v14 (User Dashboard), though the bookshelf page link naturally lives in the profile nav introduced in v12/v14.

---

## 13. Open Questions

| Question | Recommended default | Status |
|----------|---------------------|--------|
| Where does the bookshelf link appear in the nav? | Inside the profile dropdown (introduced in v12) | Decide when v12 nav is designed |
| Should status change on the bookshelf page be a full form POST or AJAX? | Form POST (PRG) for v15; AJAX enhancement is optional | Resolved: form POST |
| Should "خواندم" books be visually distinct (e.g. greyed out or checked) on the bookshelf page? | Yes — add a subtle visual distinction (checkmark icon or muted style) | Engineer to decide at implementation |

---

## Deployment Status

| Field | Value |
|-------|-------|
| **Status** | Backlog |
| **Blocked by** | v12 User Auth |
| **Estimated effort** | ~2.5 dev days (1 migration + service layer + 2 templates + book detail update + review modal wiring to existing v4 rating/comment endpoints) |
