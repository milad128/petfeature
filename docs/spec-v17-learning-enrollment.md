# Product Spec v17 — Learning Enrollment & Progress Tracking (ثبت‌نام در مسیر یادگیری)

> **Prerequisite:** [v12 User Auth](./spec-v12-user-auth.md) must ship first · **Builds on:** [v16 Roadmap](./spec-v16-roadmap.md) (shipped) · **Shell:** [v14 User Dashboard](./spec-v14-user-dashboard.md) · **Parent:** [Product overview](./spec.md) · **Idea draft:** [learning-enrollment.md](./New%20idea/learning-enrollment.md) · **Design prototype:** `prototypes/learning-dashboard.html`, `prototypes/learning-level.html`, `prototypes/learning-path.html`

## 1. Summary

| Field | Value |
|-------|-------|
| **Version** | v17 — Learning Enrollment & Progress Tracking |
| **Status** | In development |
| **Goal** | Let a visitor commit to a roadmap level with one explicit click, then track resource progress on a personal learning dashboard |
| **Builds on** | v12 (identity), v14 (user-panel shell), v16 (`RoadmapResource` + public `/path/` pages) |
| **Epic** | Roadmap |

**Scope in two sentences:** Add an explicit enroll button on the public roadmap level page and the public learning page. After enroll (or Google login), the user is sent to the **user panel** to see that level's resources and set statuses. The public learning page never shows status dropdowns or personal progress — only the enroll / continue CTA.

Enrollment is never implicit. Viewing a page does not create an `Enrollment`.

---

## 2. Problem & Goals

**Problem:** v16 tells a visitor *what* to study. It does not let them commit to a level, remember where they left off, or see progress. Without an identity-gated enroll step, there is nothing personal to attach status to.

**v17 goals:**

- **Commit:** One enroll click on the roadmap level page *or* the learning page
- **Register-then-enroll:** If the visitor has no account, they register (Google), then enroll in the same level without clicking again
- **Leave the public page:** After enroll, redirect to the user panel — do not unlock tracking on the learning page
- **Track:** Per-resource status **only in the user panel**; progress = (خوندم + قبلاً می‌دونستم) ÷ required resources
- **Parallel paths:** Multiple active enrollments, each with its own panel tracker and badge
- **Proof:** Badge on the user profile; public counts on the roadmap level page

---

## 3. User Stories

- *As a visitor on a roadmap level page or a learning page, I want an enroll button so I choose to start that path*
- *As a visitor who is not registered, I want that click to register me first and then enroll me in the same level, so I do not lose my place*
- *As a registered user, I want to enroll in more than one level at once so I can study current and target seniority in parallel*
- *As an enrolled user, I want to land in my panel after enroll so I track resources there — not on the public learning page*
- *As an enrolled user, I want the ordered resource list with a status on each row in my panel so I know where I am*
- *As an enrolled user, I want to change a resource status in one interaction so tracking is cheap*
- *As an enrolled user, I want a progress bar that ignores skipped and optional items so completion means required work*
- *As an enrolled user, I want a «مسیرهای من» index so I can jump between enrollments*
- *As an enrolled user, I want a badge that upgrades from enrolled → in progress → completed*
- *As a visitor, I want to see how many people are learning or have finished a level*

---

## 4. Enrollment flow

Button lives in **both** places, same behaviour:

1. Public roadmap level page — `/path/{level_slug}/` (and `/path/hiring/`)
2. Learning page — `/dashboard/learning/{level_slug}/`

```
Visitor clicks «شروع یادگیری» on /path/{slug}/ or /dashboard/learning/{slug}/
        │
        ├── Authenticated, not enrolled
        │     POST enroll → 303 to /dashboard/learning/{slug}/track/
        │
        ├── Authenticated, already enrolled
        │     no second row → 303 to /dashboard/learning/{slug}/track/ («ادامه یادگیری»)
        │
        └── Not authenticated
              GET /login/?next=/dashboard/learning/{slug}/enroll/
              → Google OAuth (v12: first login creates User)
              → GET enroll (auth required, idempotent get-or-create)
              → 303 to /dashboard/learning/{slug}/track/
```

**Rules**

- First-time Google login *is* registration (v12). There is no separate sign-up form.
- After auth, enrollment is created automatically for the `next` level. Do not drop the user on `/profile/` with no enrollment.
- `GET …/enroll/` exists only as the OAuth return target. It is idempotent (get-or-create) and always redirects. Logged-in users on the page itself use `POST`.
- No prerequisite lock: a user may enroll in L4 without L1–L3.
- Multiple levels at once are allowed. Each enrollment is independent.
- Enroll is offered only on levels that have a full public page with resources (today: hiring, apm, and any other shipped full page). Stub levels stay without a button until their page ships.

**Button labels**

| State | Label | Action |
|-------|--------|--------|
| Not logged in, or logged in and not enrolled | شروع یادگیری | Enroll flow above |
| Enrolled in this level | ادامه یادگیری | Go to `/dashboard/learning/{slug}/track/` — do not create another row |

Unenroll is a quiet control on the **panel** tracker footer («لغو ثبت‌نام از این سطح»), not on the public learning page or `/path/`.

---

## 5. Pages

### 5.1 Learning page — `GET /dashboard/learning/{level_slug}/`

Public. Readable **without** login. This page is a catalog + enroll, not a tracker.

- Same resource order as v16: ورود → هسته → حمایتی → پل
- Each row: title, type, reading time, difficulty, Persian flag, الزامی / اختیاری
- Enroll / continue button in the hero (same CTA on `/path/{slug}/`)
- **No status `<select>`.** No `STUDYING` / `DONE` / `ALREADY_KNEW` / `SKIPPED` on this page
- **No personal progress bar**, no «الان کجا هستید», no unenroll
- After a successful enroll, **always leave this page** → panel tracker
- If already enrolled, the button is «ادامه یادگیری» and goes to the panel tracker

**Prototype:** `prototypes/learning-level.html`

### 5.2 User panel — index `GET /dashboard/learning/` and tracker `GET /dashboard/learning/{level_slug}/track/`

Auth required. Lives in the v14 user-panel shell (تب «یادگیری» next to نظرات / تلگرام).

**Index**

- One card per active enrollment: level name, progress bar, Jalali enroll date, badge tier, «ادامه یادگیری»
- Cards are not merged
- Empty state: «هنوز در هیچ سطحی ثبت‌نام نکرده‌اید» + link to `/path/`
- Optional dashed card: «سطح دیگری شروع کنید» → `/path/`

**Tracker (this is where statuses live)**

- Progress panel: percentage, bar, counts (done / required / studying / blank)
- Formula shown in UI: پیشرفت = (خوندم + قبلاً می‌دونستم) ÷ منابع الزامی. اختیاری و «رد کردم» حساب نمی‌شوند.
- «الان کجا هستید» card if one or more resources are `STUDYING` (pin the first)
- Status `<select>` on every row — form POST without JS; JS may update without reload
- Title is a link to the same URL as v16 (`/library/{slug}/` or external). Unlinked rows show «هنوز لینکی ندارد»
- Soft hint if more than one resource is `STUDYING` (not enforced)
- Link back to the public learning / `/path/` text
- Unenroll control at the bottom

**Prototype:** `prototypes/learning-dashboard.html` (index + tracker view)

### 5.3 Roadmap level page — existing `/path/{level_slug}/`

- Add the enroll / continue CTA (hero or aside)
- Public aggregates when count ≥ 1: «X نفر در حال یادگیری» and «Y نفر این سطح را تکمیل کرده‌اند»
- Hide a count when it is 0

### 5.4 Profile badges (v12/v14 profile)

One badge per enrolled level, single current tier:

| Tier | When | Persian |
|------|------|---------|
| Enrolled | Row exists, progress < 50% | ثبت‌نام شده |
| In progress | Progress ≥ 50% and < 100% | در حال یادگیری |
| Completed | Progress = 100% (`completed_at` set) | تکمیل‌شده |

Higher tier replaces the lower one. No extra badge table — compute from enrollment + progress.

---

## 6. Resource status model

Default is **blank**. Nothing is pre-filled on enroll.

Four statuses + blank. The path is already the queue — there is no «می‌خوام بخونم».

| Key | Persian | Counts toward progress? |
|-----|---------|-------------------------|
| *(none)* | وضعیت ندارد | No |
| `STUDYING` | دارم می‌خونم | No |
| `DONE` | خوندم | Yes |
| `ALREADY_KNEW` | قبلاً می‌دونستم | Yes |
| `SKIPPED` | رد کردم | No |

Optional resources never enter the denominator. `SKIPPED` on a required resource also does not count as done (user must `DONE` or `ALREADY_KNEW` to complete).

**Completion:** when progress hits 100%, set `Enrollment.completed_at` once. No extra «تکمیل کردم» button in v17.

---

## 7. Data model

### `Enrollment`

| Field | Type | Notes |
|-------|------|--------|
| `id` | PK | |
| `user_id` | FK → `users.id` | v12 User |
| `level_slug` | str | `hiring`, `apm`, `pm`, … — same slugs as v16 |
| `enrolled_at` | datetime | |
| `completed_at` | datetime, nullable | Set when progress first reaches 100% |
| `unenrolled_at` | datetime, nullable | Soft delete |

Unique **active** enrollment: one row per `(user_id, level_slug)` with `unenrolled_at IS NULL`. Re-enroll after unenroll: clear `unenrolled_at` and restore existing `ResourceProgress` rows (do not reset).

### `ResourceProgress`

| Field | Type | Notes |
|-------|------|--------|
| `id` | PK | |
| `enrollment_id` | FK → Enrollment | |
| `roadmap_resource_id` | FK → `RoadmapResource` | v16 |
| `status` | enum / str | four keys above; row omitted means blank |
| `updated_at` | datetime | |

Unique: `(enrollment_id, roadmap_resource_id)`.

**Migration:** one Alembic revision creating both tables. No changes to `RoadmapResource`.

---

## 8. Routes

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| `GET` | `/dashboard/learning/` | Required | Panel index |
| `GET` | `/dashboard/learning/{level_slug}/` | Public | Learning page — enroll CTA only, no statuses |
| `GET` | `/dashboard/learning/{level_slug}/track/` | Required | Panel tracker — statuses + progress |
| `POST` | `/dashboard/learning/{level_slug}/enroll/` | Required | Create enrollment (form) → 303 to `…/track/` |
| `GET` | `/dashboard/learning/{level_slug}/enroll/` | Required | OAuth `next` target — get-or-create, then 303 to `…/track/` |
| `POST` | `/dashboard/learning/{level_slug}/unenroll/` | Required | Soft-delete own enrollment |
| `POST` | `/dashboard/learning/{level_slug}/progress/` | Required | Form POST: `resource_id` + `status` (empty string = clear) |
| `POST` | `/api/v1/learning/{level_slug}/progress/` | Required | Same update as JSON for the async UI |

Unknown `level_slug` → 404. Progress / unenroll without an active enrollment → 403 or redirect to the public learning page with the enroll button. Tracker without auth → `/login/?next=/dashboard/learning/{slug}/track/`.

v12 callback already honours `?next=`. Wire enroll clicks for guests to `/login/?next=/dashboard/learning/{slug}/enroll/`.

---

## 9. Service layer — `app/services/learning.py`

| Function | Purpose |
|----------|---------|
| `get_or_create_enrollment(user_id, level_slug)` | Idempotent enroll; restores a soft-deleted row |
| `unenroll(user_id, level_slug)` | Set `unenrolled_at` |
| `get_active_enrollments(user_id)` | Index cards + computed progress + badge tier |
| `get_enrollment(user_id, level_slug)` | Active row or `None` |
| `list_resources_with_status(level_slug, enrollment)` | v16 order + optional status; one query for all progress rows |
| `set_resource_status(enrollment_id, resource_id, status)` | Upsert / delete-if-blank; recompute `completed_at` |
| `compute_progress(enrollment)` | `(DONE + ALREADY_KNEW) / required` |
| `level_social_counts(level_slug)` | active learners + completers for the roadmap page |

Keep web routes thin. Reuse `roadmap_data` / `RoadmapResource` for titles, order, and required flags.

---

## 10. Acceptance criteria

### Enroll button
- [x] «شروع یادگیری» on `/path/{slug}/` and `/dashboard/learning/{slug}/` when the viewer is not enrolled
- [x] Logged-in click creates one `Enrollment` and **redirects to** `/dashboard/learning/{slug}/track/`
- [x] The public learning page never renders a status `<select>` or personal progress, including after enroll
- [x] Logged-out click goes to `/login/?next=/dashboard/learning/{slug}/enroll/`
- [x] After Google login / first-time registration, the user is enrolled in **that** level and lands on the **panel tracker** — not on a bare `/profile/`, not back on the learning page
- [x] Second click does not insert a second row; label is «ادامه یادگیری» → panel tracker
- [x] Stub levels have no enroll button

### Panel tracker
- [x] Resources in Entry → Core → Supporting → Bridge order
- [x] Row shows title, type, time, difficulty, Persian flag, required/optional, status (or blank)
- [x] Status change works without JS (form POST); JS path does not require a full reload
- [x] Progress bar matches the formula; optional resources excluded
- [x] Blank is the default; user must set a status
- [x] Unenroll soft-deletes; re-enroll restores progress

### Index
- [x] `/dashboard/learning/` lists each active enrollment as its own card
- [x] Empty state points at `/path/`
- [x] Unauthenticated visit redirects to `/login/?next=/dashboard/learning/`

### Badges & counts
- [x] Profile shows current badge tier per enrolled level
- [x] Roadmap level page shows learner / completer counts when ≥ 1
- [x] Admin analytics: read-only enroll count per level (no progress editor)

---

## 11. Out of scope (v17)

| Item | Reason |
|------|--------|
| Deadlines / date math | Sequence only (confirmed) |
| Public progress timelines | Aggregates on the level page only |
| Telegram reminders | Separate feature |
| Prerequisite enforcement | Roadmap copy, not the system |
| Cohort / group dashboards | Out of scope → [v18](./spec-v18-enrollment-admin.md) |
| Admin override of a user's statuses | Read-only counts only (v17); inspect-only detail in v18 |
| Email/password registration | v12 is Google-only |

---

## 12. NFRs

- All CTA and status copy in Persian; level names match v16
- Status controls keyboard-accessible and labelled
- One query for all `ResourceProgress` rows of an enrollment (no N+1)
- Learning page warm-DB target: 300ms
- `GOOGLE` / session rules stay as v12; enroll `GET` must be idempotent
- CSRF on POST enroll / unenroll / progress

---

## 13. Dependencies & sequencing

| Dependency | Status | Notes |
|------------|--------|--------|
| v12 User Auth | Present in repo | Enrollment uses `User` + session `?next=` |
| v14 User Dashboard | Present in repo | Index and tracker use the profile shell; profile also lists learning cards |
| v16 Roadmap | **Shipped** | Resources and `/path/` pages |

v12's "do not add sitewide ثبت‌نام CTAs until there is a reason" is satisfied here: the reason is this enroll button.

---

## 14. Open questions

| Question | Recommended default | Status |
|----------|---------------------|--------|
| `ALREADY_KNEW` vs `DONE` — keep both? | Keep both (pre-existing knowledge vs finished during enrollment) | Resolved |
| Queue status `WANT_TO_STUDY`? | Drop — blank is the queue on an ordered path | Resolved |
| Public profile badges? | Private on `/profile/` until a public profile exists | Open — follows v14 |
| Auto-complete at 100% vs explicit button? | Auto-set `completed_at` at 100% | Resolved for v17 |
| Re-enroll: restore or reset? | Restore | Resolved |
| Aggregate counts real-time or cached? | Real-time until `/path/` traffic needs a cache | Resolved for v17 |

---

## 15. Effort estimate

| Area | Estimate |
|------|----------|
| Models + migration | 2h |
| Enroll / unenroll + OAuth `next` get-or-create | 3h |
| Learning page (public enroll CTA, no statuses) | 2.5h |
| Panel index + tracker | 3h |
| Status POST + optional async JS | 3h |
| Badges on profile + counts on `/path/` | 2.5h |
| Admin read-only counts | 1h |
| **Total** | **~17h (~2.5 days)** after v12 |

---

## Decision log

| Date | Decision | Source |
|------|----------|--------|
| 2026-08-09 | Order-only, no timeline | Idea draft / Milad |
| 2026-08-09 | Multi-level enroll, separate dashboards | Idea draft / Milad |
| 2026-08-09 | Badges on profile | Idea draft / Milad |
| 2026-08-09 | Resources = v16 `RoadmapResource` | Idea draft |
| 2026-09-06 | Enroll button on **both** learning page and roadmap level page | Milad |
| 2026-09-06 | After Google login / first registration, **auto-enroll** that level and open its dashboard | Milad |
| 2026-09-06 | Official spec covers full v17 (enroll + dashboard + badges), not enroll-only | Milad |
| 2026-09-06 | Public learning page = enroll only; statuses live in the user panel; after enroll redirect to panel tracker | Milad |
| 2026-09-06 | Statuses = blank + STUDYING / DONE / ALREADY_KNEW / SKIPPED. No WANT_TO_STUDY | Milad |

---

*September 2026 — v17 in development. Public catalog is enroll-only; statuses live on `/dashboard/learning/{slug}/track/`.*
