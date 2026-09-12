# v18.1 — Resource ratings (امتیاز منابع)

**Status:** In development  
**Depends on:** v17 Learning Enrollment (tracker + `ResourceProgress`), v18 Enrollment Admin (learner detail), v16 Roadmap (`RoadmapResource`), v12 User Auth  
**Audience:** logged-in learners on `/dashboard/learning/{slug}/track/`; admin on `/admin/roadmap/` and `/admin/learning/`  
**Not in this version:** public averages on `/path/` or catalog; comments on resources; ratings from guests; editing another user’s stars

---

## 1. Why this exists

v17 lets a learner mark a resource as «خوندم». That is a *progress* signal, not a *quality* signal. Milad cannot tell which resources actually help people versus which they only checked off.

When a learner finishes a resource, the product should ask for a **1–5 star score** (same scale as book/post ratings in v4/v2). Scores live with the logged-in user, not a visitor cookie. Admin sees the **mean and vote count per resource**, and that learner’s stars on the enrollment detail page.

This is a **point release on v18**, not a new epic: it extends the tracker (v17) and the admin inspection surface (v18). It does **not** change enroll rules, required-resource math, or public catalog pages.

---

## 2. Goals / non-goals

### Goals

- After a learner changes a resource status **to `DONE` («خوندم») or `ALREADY_KNEW` («قبلاً می‌دونستم»)**, prompt them to rate that resource **1–5 stars**.
- Rating is **optional**. Saving that status must succeed even if they skip the prompt.
- A learner may **change their score later** from the tracker row (same resource).
- **One score per user per `RoadmapResource`.** Re-enroll, unenroll, or leaving `DONE` does not create a second vote.
- **Admin** sees aggregate rating on the resource CMS list (and a compact summary on the resource edit form).
- **Admin** sees that learner’s stars on `/admin/learning/enrollments/{id}/` next to status.
- Works **without JavaScript** (form POST + redirect), like v15’s review prompt and v17’s status POST.
- Persian RTL copy; counts via `fa_digits`.

### Non-goals

- Showing average stars on public `/path/`, `/path/{slug}/`, or `/learn/` catalog (v18.1 is **admin + tracker only**).
- Text reviews / comments on resources.
- Rating when status becomes `STUDYING` or `SKIPPED` (prompt is only `DONE` / `ALREADY_KNEW`).
- Guest / visitor-token ratings (v4 books use a cookie; learning ratings require login).
- Admin editing or deleting a learner’s stars (read-only, same spirit as v18).
- Mixing this score with `RoadmapResource.difficulty` (author 1–3). Different meaning, different UI.
- Using ratings in required-progress % (still `(DONE + ALREADY_KNEW) / required`).
- Notifications, emails, or Telegram about ratings.

---

## 3. User stories

| As a… | I want to… | So that… |
|--------|------------|----------|
| Learner | be asked for stars right after I mark «خوندم» or «قبلاً می‌دونستم» | I rate while the resource is still in mind |
| Learner | skip the prompt and still keep that status | rating never blocks progress |
| Learner | change my stars later on the tracker | I can correct a hasty score |
| Learner | *not* be asked again if I already rated this resource | the prompt is not nagging |
| Admin | see mean + vote count per resource on `/admin/roadmap/` | I can spot weak or loved materials |
| Admin | see one learner’s stars on their enrollment detail | I can inspect a specific path without guessing |
| Guest / logged-out | see `/path/` unchanged | ratings stay private to tracker + admin |

---

## 4. Rating rules

### Scale

Integer **1–5** only. Same semantic as v4 books: 1 = ضعیف, 5 = عالی. Display filled/empty stars, not a number field, on the learner UI.

Copy on the prompt (Persian):

- Title: «این منبع چقدر به‌دردت خورد؟»
- Helper: «از ۱ تا ۵ ستاره — اختیاری است.»
- Submit: «ثبت امتیاز»
- Skip: «بعداً»

Empty / no vote yet: do not show a fake «0 ستاره». Tracker row shows «امتیاز بده» (or the current stars) only when the user is enrolled.

### When to prompt

Prompt **only** when **all** of these are true:

1. The status POST (or equivalent) **succeeds** and the new status is **`DONE` or `ALREADY_KNEW`**.
2. The previous status was **not** already that same value (transition *into* it — not a no-op re-save). Switching `DONE` ↔ `ALREADY_KNEW` **does** prompt if they still have no rating (they just committed to “I’m done with this resource”).
3. This user has **no** `ResourceRating` row yet for that `roadmap_resource_id`.

Do **not** prompt for:

| Status | Why |
|--------|-----|
| `STUDYING` | not finished |
| `SKIPPED` | they declined the resource |
| Clearing to blank | leaving the resource |
| `DONE` → `DONE` or `ALREADY_KNEW` → `ALREADY_KNEW` | already set; if they have no rating they can use the row control, not a modal every save |

Optional resources (`is_required = false`) **are** ratable when marked `DONE` or `ALREADY_KNEW`. Same prompt.

### Skip and later rate

1. Persist `DONE` or `ALREADY_KNEW` first.
2. Then show the prompt (query flag on redirect, or JSON `{ "prompt_rating": true, "resource_id": N }` for the fetch path).
3. Skip (`بعداً`) returns to the tracker; status stays as saved; no rating row.
4. The tracker row then shows a compact star control (or «امتیاز بده») so they can rate without changing status again.

### Changing and keeping scores

| Event | Rating |
|-------|--------|
| First 1–5 submit | Insert `ResourceRating` |
| Later 1–5 submit | Update same row (`updated_at`) |
| Status leaves `DONE` / `ALREADY_KNEW` | **Keep** the rating |
| Unenroll / re-enroll | **Keep** the rating (keyed by user + resource, not enrollment) |
| User never rated | No row; aggregates ignore them |

There is **no** “clear my stars” in v18.1 (can add later). Changing 5 → 1 is the correction path.

### Who can rate

- Must be **logged in** (v12) and **enrolled** in that level (`Enrollment` exists, including `unenrolled_at IS NOT NULL` is **not** enough — they need an active enrollment to POST from the tracker).
- If they unenrolled, they cannot open the tracker; their historical stars still count in admin averages.
- `resource_id` must belong to that level’s published (or admin-visible) resources — same ownership check as `set_resource_status`.

---

## 5. Data model

### New table: `resource_ratings`

Do **not** hang stars on `ResourceProgress`. Progress is per enrollment; a score is “this user judged this catalog row.” That keeps averages stable if they drop and rejoin a level.

| Column | Type | Notes |
|--------|------|--------|
| `id` | PK | |
| `user_id` | FK → `users.id` | `ON DELETE CASCADE` |
| `roadmap_resource_id` | FK → `roadmap_resources.id` | `ON DELETE CASCADE` (resource deleted → votes go with it) |
| `stars` | `SmallInteger` | **1–5**, CHECK constraint |
| `created_at` | DateTime(tz) | first vote |
| `updated_at` | DateTime(tz) | last change |

**Unique:** `(user_id, roadmap_resource_id)`.

Indexes: unique constraint covers lookups; add index on `roadmap_resource_id` for admin `AVG` / `COUNT`.

No `enrollment_id` in v18.1. Admin detail joins `ResourceRating` on `(user_id, roadmap_resource_id)` while listing that enrollment’s resources.

### What we do **not** store

- Comment / review text
- Visitor token
- Separate “prompt dismissed” flag — absence of a row + `DONE` or `ALREADY_KNEW` is enough to show «امتیاز بده» on the row

### Aggregates (computed, not cached in v18.1)

```
avg_stars = AVG(stars)          -- float, one decimal in UI
rating_count = COUNT(*)         -- raters, not page views
```

No denormalized columns on `roadmap_resources` unless a later version proves the list query is slow.

### Migration

One Alembic revision. No backfill (feature is new). SQLite tests create the table via metadata like other models.

---

## 6. Learner UX

### Tracker only

Ratings UI lives on **`/dashboard/learning/{slug}/track/`** (and the status POST that page already uses).

**Do not** add stars to:

- `/learn/` catalog
- `/path/` hub
- `/path/{slug}/` public level pages (including hiring / APM / PM)
- `learn_enroll_cta.html`

Public pages stay enroll-only, as in v17.

### Prompt after «خوندم» or «قبلاً می‌دونستم»

**With JS** (existing `learning.js` fetch): after a successful status response with `prompt_rating`, open a small **modal** (RTL, focus trap light: heading + skip + star radios + submit). Do not block the status update already applied in the DOM.

**Without JS:** status form POSTs as today; redirect to  
`/dashboard/learning/{slug}/track/?rate={resource_id}`  
(or `#resource-{id}&rate=1`). Page renders an **inline card** above that row (or a `<dialog>` with `open`) with the same star form. Skip is a GET back to the tracker without the query param.

Star input: reuse the v4 **radio group** pattern (five radios, visually stars). `name="stars"`, values 1–5. CSRF hidden field required.

Invalid stars (missing, 0, 6) → 422, stay on tracker, flash «امتیاز نامعتبر است», status unchanged (already saved).

### Row after rating / skip

Each resource row (`learn_resource_row.html`):

- Status `<select>` unchanged.
- **If rated:** show the learner’s stars (read-only glyphs + visually hidden text «امتیاز شما: N از ۵») and a control to **change** (same radios, or click-to-edit). Changing stars does **not** change status.
- **If `DONE` or `ALREADY_KNEW` and not rated:** text button «امتیاز بده» → same form as the prompt (inline expand or `?rate=`).
- **If neither `DONE` nor `ALREADY_KNEW`:** hide the rate CTA. If they already have a historical rating (e.g. they moved to `SKIPPED` after rating), still show the stars as read-only + change — the score is about the resource, not the current status.

Do not show **site-wide average** on the learner row in v18.1 (avoids social pressure and keeps the public/private split clean).

### Profile

No new badge. Completing a level is still the only v17 badge. Optional later: «N منبع را امتیاز دادی» — out of scope.

---

## 7. Admin UX

### 7.1 Resource list — `/admin/roadmap/`

Add a column **امتیاز** after سختی (or before ترتیب):

| Votes | Display |
|-------|---------|
| 0 | `—` |
| ≥ 1 | `N.N ★` + `N رای` (Persian digits). Mean rounded to **one decimal**. |

Tooltip or visually hidden text: «میانگین امتیاز یادگیرنده‌ها».

Do **not** sort by rating in v18.1 (keep existing level / type filters). Can add `?sort=rating` later.

### 7.2 Resource edit — `/admin/roadmap/{id}/edit/`

Read-only line under the form (not an editable field):

«امتیاز یادگیرنده‌ها: میانگین N.N از ۵ · N رای»  
or «هنوز امتیازی ثبت نشده.»

Admin does **not** set or override stars here. `difficulty` stays the authoring field.

### 7.3 Enrollment detail — `/admin/learning/enrollments/{id}/`

In the resource table, add column **امتیاز این کاربر**:

- Has vote: `★` × N (or `N از ۵`)
- No vote: `—`

This is **that user’s** score, not the resource average. Average remains on the CMS list.

### 7.4 Overview / analytics

v18.1 does **not** add a new admin nav item. Optional compact line on `/admin/learning/` overview (not required to ship): «کم‌امتیازترین منابع الزامی (حداقل ۳ رای)» — **defer** unless cheap. Default: **omit** from first slice so the resource list is the source of truth.

Do **not** put learner ratings on the public-facing analytics strip.

### 7.5 Permissions

Same as v18: session admin only. Read-only stars. No bulk delete of votes in v18.1.

---

## 8. Routes & service

Keep routes thin; logic in `app/services/learning.py`.

### Learner

| Method | Path | Purpose |
|--------|------|---------|
| POST (existing) | `/dashboard/learning/{slug}/progress/` | Status; response/redirect may include rating prompt |
| POST (new) | `/dashboard/learning/{slug}/rate/` | Body: `resource_id`, `stars` (1–5), CSRF. Upsert `ResourceRating`. Redirect tracker. |

JSON (logged-in, same CSRF as progress):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/learning/{slug}/rate` | `{ "resource_id", "stars" }` → `{ "ok", "stars", "avg_stars"? }` — **do not return avg to the learner UI** in v18.1 even if the API computes it for admin later. Learner response: `{ "ok": true, "stars": 4 }`. |

`GET` rate is unnecessary.

Auth: 401/redirect login if anonymous. 403 if not enrolled. 404 if resource not in that level.

### Admin

No new URLs. Extend existing:

- `admin_roadmap_resources` — attach `avg_stars`, `rating_count` per row (query or annotated list).
- `admin_roadmap_edit` GET — pass the same aggregates.
- `admin_learning_enrollment_detail` — map `resource_id → stars` for that enrollment’s user.

---

## 9. Implementation notes

- Import `ResourceRating` in `app/models/__init__.py` and `alembic/env.py`.
- `set_resource_status`: after commit, if transitioned to `DONE` or `ALREADY_KNEW` and no rating, set `prompt_rating` on the return dict / redirect query.
- `upsert_resource_rating(db, user_id, slug, resource_id, stars) -> ResourceRating`.
- Admin helpers: `rating_stats_by_resource_ids(db, ids) -> dict[int, tuple[float, int]]`.
- CSRF: both HTML POSTs must use the same token helper as enroll/progress.
- `fa_digits` for counts and the one-decimal mean (e.g. `۴.۲`).
- CSS: tracker prompt + row stars in `main.css`; admin column in `admin.css`. Do not reuse `.difficulty` dots as rating stars.
- Accessibility: radio group `fieldset` / `legend` «امتیاز از ۱ تا ۵»; skip control is a real button/link, not `div`+click only.

---

## 10. Tests (`tests/test_learning.py`, `tests/test_admin_learning.py`, `tests/test_admin_roadmap.py`)

| Case | Expect |
|------|--------|
| POST `DONE` first time, no rating | Redirect or JSON includes prompt; status is `DONE` |
| POST `ALREADY_KNEW` first time, no rating | Same prompt; status is `ALREADY_KNEW` |
| Skip prompt | Status unchanged; no `ResourceRating` |
| POST rate 1–5 while enrolled | Row saved; unique upsert |
| POST rate 0 / 6 / missing | 422; no row |
| POST rate anonymous | Login redirect / 401 |
| POST rate not enrolled | 403 |
| Resource from another level | 404 |
| Second `DONE` or `ALREADY_KNEW` save after already rated | No prompt |
| `SKIPPED` / `STUDYING` | No prompt |
| Change stars 5 → 2 | One row, `updated_at` changes |
| Unenroll then admin list | Average still includes that vote |
| Tracker HTML | Has rate form or «امتیاز بده» when `DONE` / `ALREADY_KNEW` unrated; has CSRF |
| `/path/apm/` HTML | **No** «میانگین امتیاز» / star radios |
| Admin resource list | `—` when 0 votes; mean + `رای` when ≥1 |
| Admin enrollment detail | Shows that user’s stars or `—` |
| Admin cannot POST a fake rate URL as that user | N/A — no admin write API |

---

## 11. Acceptance criteria

- [ ] Marking a resource «خوندم» or «قبلاً می‌دونستم» asks for 1–5 stars without blocking the status save.
- [ ] Skip / invalid stars never revert the saved status.
- [ ] One vote per user per `RoadmapResource`; change is an update, not a second row.
- [ ] `SKIPPED` and `STUDYING` do not open the prompt.
- [ ] Tracker works with JS off (rate query param + form POST).
- [ ] `/admin/roadmap/` shows mean + count; zero votes show `—`.
- [ ] `/admin/learning/enrollments/{id}/` shows that learner’s stars per resource.
- [ ] Public path/catalog pages have no rating UI and no averages.
- [ ] `difficulty` on the resource form is unchanged and not shown as “learner score”.
- [ ] Persian copy + `fa_digits`; CSRF on rate POST.
- [ ] Tests above pass on SQLite.

---

## 12. Out of scope / later

| Idea | Why later |
|------|-----------|
| Public average on `/path/{slug}/` | Social proof vs honesty tradeoff; not requested |
| Sort admin list by rating | Nice-to-have after the column exists |
| «کم‌امتیازترین منابع» on v18 overview | Extra query; list page is enough |
| Comments / «چرا این امتیاز» | Support load |
| Clear-my-rating | Rare; change-stars is enough |
| Weight ratings by `DONE` only | All votes already come from enrolled users; filtering to current `DONE` would drop people who rated then skipped |
| Telegram digest of new ratings | Noise |

---

## 13. Dependencies & sequencing

| Dependency | Status | Notes |
|------------|--------|--------|
| v17 tracker + `ResourceProgress` | Required | Prompt hooks the existing status POST |
| v18 enrollment detail | Required for “see this learner’s stars” | Resource-list column can ship even if v18 slips, but the story includes both |
| v16 `RoadmapResource` | Shipped | FK target |
| v12 `User` | Shipped | Rater identity |
| v4 star widget | Shipped | Copy the radio/star pattern, not the visitor-token model |

Ship **after** v17 is on production (otherwise there is nothing to rate). Can ship in the same release train as v18.

---

## 14. Open questions — decided

| Question | Decision | Status |
|----------|----------|--------|
| Prompt on `ALREADY_KNEW`? | **Yes** — same prompt as `DONE` | Decided |
| Separate table vs `stars` on `ResourceProgress`? | **`resource_ratings` table** — vote survives unenroll / re-enroll | Decided |
| Show average to the learner? | **No** in v18.1 — own stars only | Decided |
| Show average on public path pages? | **No** in v18.1 — tracker + admin only | Decided |
| Allow rating before `DONE`? | **No** — «امتیاز بده» only when `DONE` or `ALREADY_KNEW`, unless a rating already exists (edit). Unrated + `STUDYING` / `SKIPPED` / blank → no CTA | Decided |
| Minimum votes before showing mean in admin? | **Show mean from 1 vote**; `—` only at 0 | Decided |
| Overview “worst resources” widget? | **Defer** — `/admin/roadmap/` column is enough | Decided |

---

## 15. Effort estimate

| Area | Estimate |
|------|----------|
| Model + migration + service upsert/stats | 2h |
| Prompt + tracker row + `learning.js` + no-JS redirect | 3h |
| Admin list + edit summary + enrollment detail column | 2h |
| CSS / RTL / a11y | 1h |
| Tests | 2h |
| **Total** | **~10h (~1–1.5 days)** |

---

## Decision log

| Date | Decision | Source |
|------|----------|--------|
| 2026-09-11 | v18.1 = 1–5 resource stars on `DONE`, optional prompt, admin aggregates + per-learner stars; no public averages | Milad |
| 2026-09-11 | Also prompt on `ALREADY_KNEW`. Separate `resource_ratings` table. Learner sees own stars only. No public averages. Rate CTA only after `DONE` / `ALREADY_KNEW` (or to edit). Admin mean from 1 vote. No overview “worst resources” widget. | Milad |

---

*September 2026 — in development.*
