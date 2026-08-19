# Feature Spec — Learning Enrollment & Progress Tracking
**Version:** v17 (candidate)
**Status:** Draft — not yet accepted into roadmap
**Author:** PM Agent
**Date:** 2026-08-09
**Blocked on:** v12 (User Auth) → v14 (User Dashboard) → v16 (Roadmap)

---

## Problem Statement

petfeature.ir now has a structured learning roadmap (v16) with levels L0–L6, each containing ordered resources grouped by category (Entry, Core, Supporting, Bridge). But reading a roadmap and *following* it are two different things. A visitor can see what to study — they cannot track what they've done, know where they left off, or feel a sense of progress over time.

Registered users need a way to formally enroll in a level and convert a static reading list into a personal learning dashboard that reflects their actual progress.

---

## Target User

**Primary:** A Persian-speaking PM professional who has already registered on petfeature.ir, reviewed the roadmap, and is ready to commit to a structured learning path for their current or target seniority level.

**Secondary:** Managers or mentors who want to recommend a level to someone and have a shared reference point for progress.

---

## User Stories

### Enrollment
- As a registered user, I want to enroll in a roadmap level so that I have a personal learning path to follow.
- As a registered user, I want to enroll in multiple levels simultaneously so that I can prepare for a future level while still completing my current one.
- As a registered user, I want each enrollment to have its own separate dashboard so that I can track progress per level independently.

### Progress Tracking
- As a registered user, I want to see the ordered list of resources in my enrolled level so that I know the recommended sequence.
- As a registered user, I want to set a status on each resource so that I can track where I am in the path.
- As a registered user, I want to update or reset a resource's status so that I can correct a mistake or acknowledge a re-read.

### Badges & Social Proof
- As a registered user, I want to earn a badge on my profile when I enroll in a level and when I complete it so that my commitment and achievement are visible.
- As a visitor, I want to see how many users have enrolled in or completed each level so that I have a sense of which levels are most active.

---

## Resource Status Model

Five statuses, shown in Persian in the UI:

| Status Key | Persian Label | Meaning |
|---|---|---|
| `WANT_TO_STUDY` | می‌خوام بخونم | Queued — flagged for later, not yet started |
| `STUDYING` | دارم می‌خونم | Currently active — at most one per enrollment (soft limit, not enforced) |
| `DONE` | خوندم | Completed as part of this learning path |
| `ALREADY_KNEW` | قبلاً می‌دونستم | Existed in user's knowledge before enrollment; counts toward progress |
| `SKIPPED` | رد کردم | Consciously skipped; does not count toward completion |

> **Open Question (for Milad):** You listed "already studied" and "studied" as separate statuses. I've interpreted them as `ALREADY_KNEW` (pre-existing knowledge before enrollment) and `DONE` (completed during enrollment). Is that the right distinction, or were they the same state?

**Default state:** All resources start with no status set (blank). The user must actively set a status — nothing is pre-populated.

**Progress calculation:** `(DONE + ALREADY_KNEW) / total required resources` — SKIPPED and WANT_TO_STUDY do not count. Optional resources never block completion.

---

## Enrollment Rules

1. A user can enroll in **multiple levels simultaneously** — no restriction.
2. Each level enrollment is **independent** — separate dashboard, separate progress, separate badges.
3. A user can **unenroll** from a level. Progress is soft-deleted (retained in DB, not shown in UI) so re-enrollment restores history.
4. No prerequisite enforcement — a user can enroll in L4 without completing L1–L3. The roadmap itself communicates prerequisites; the system does not block.

---

## Acceptance Criteria

### Enrollment Flow
- [ ] Authenticated user sees an "شروع یادگیری" (Start Learning) CTA on each level page in `/roadmap/`.
- [ ] Clicking CTA creates an `Enrollment` record and redirects to the user's learning dashboard for that level.
- [ ] Unauthenticated users clicking the CTA are redirected to `/login/` and returned to the roadmap after auth.
- [ ] A user already enrolled in a level sees "ادامه یادگیری" (Continue Learning) instead of the CTA.

### Learning Dashboard (per enrollment)
- [ ] Dashboard is accessible at `/dashboard/learning/{level_slug}/` (e.g., `/dashboard/learning/apm/`).
- [ ] Resources are displayed in the canonical roadmap order: Entry → Core → Supporting → Bridge (same sequence as v16 roadmap page).
- [ ] Each resource row shows: title, type, reading time, difficulty, Persian availability flag, current status (or blank), and a status dropdown/selector.
- [ ] User can change a resource status via a single interaction (dropdown or button group) — no page reload required (progressive enhancement: works without JS, faster with JS).
- [ ] Progress bar at top shows `(DONE + ALREADY_KNEW) / total required` as a percentage.
- [ ] Optional resources are visually distinguished (e.g., muted styling, "اختیاری" label) and excluded from the progress denominator.

### Multi-Enrollment Dashboard Index
- [ ] `/dashboard/learning/` lists all of the user's active enrollments.
- [ ] Each enrollment card shows: level name, progress bar, enrollment date, badge status.
- [ ] Enrollments are not merged — each is a distinct card.

### Badges
- [ ] **Enrolled Badge:** Awarded immediately on enrollment. One badge per level. Displayed on user profile page.
- [ ] **In Progress Badge:** Awarded when progress ≥ 50%. Replaces Enrolled badge.
- [ ] **Completed Badge:** Awarded when progress = 100%. Replaces In Progress badge.
- [ ] Badge display on public profile page (if v14 profile is public): shows level name + badge tier.
- [ ] Badge display on the level's roadmap page: aggregate count "X نفر در حال یادگیری" and "Y نفر این سطح را تکمیل کرده‌اند".

---

## Data Model

### `Enrollment`
| Field | Type | Notes |
|---|---|---|
| `id` | UUID / int PK | |
| `user_id` | FK → User | |
| `level_slug` | str | e.g. `apm`, `pm`, `senior-pm` — matches v16 level identifiers |
| `enrolled_at` | datetime | |
| `completed_at` | datetime, nullable | Set when progress hits 100% |
| `unenrolled_at` | datetime, nullable | Soft delete |

### `ResourceProgress`
| Field | Type | Notes |
|---|---|---|
| `id` | PK | |
| `enrollment_id` | FK → Enrollment | |
| `roadmap_resource_id` | FK → RoadmapResource | Reuses v16 model |
| `status` | enum | `WANT_TO_STUDY`, `STUDYING`, `DONE`, `ALREADY_KNEW`, `SKIPPED` |
| `updated_at` | datetime | Last status change |

**Unique constraint:** `(enrollment_id, roadmap_resource_id)` — one status row per resource per enrollment.

---

## Pages & Routes

| Route | Description |
|---|---|
| `GET /dashboard/learning/` | Enrollment index — all of the user's active enrollments |
| `GET /dashboard/learning/{level_slug}/` | Per-level learning dashboard |
| `POST /dashboard/learning/{level_slug}/enroll/` | Create enrollment (form action or AJAX) |
| `POST /dashboard/learning/{level_slug}/unenroll/` | Soft-delete enrollment |
| `POST /api/v1/learning/{level_slug}/progress/` | Update a single resource status (JSON, for async UI) |

---

## Out of Scope (v17)

- **Deadline / timeline generation** — the user requested order-only, no date math. Scheduling is a v18+ consideration if there is demand.
- **Social sharing** of individual progress — aggregate counts on the level page are the only social surface. No public progress timelines.
- **Notifications / reminders** — Telegram reminders for stalled enrollments are a separate feature.
- **Prerequisite enforcement** — no blocking; the roadmap text handles guidance.
- **Cohort / group learning** — no shared enrollment or group dashboards.
- **Admin CMS for enrollments** — read-only analytics (count of enrollments per level) visible in the existing admin analytics dashboard; no manual override of user progress.

---

## NFRs

- **RTL / Persian:** all labels, status names, and CTA text in Persian. Level names match v16 exactly.
- **Performance:** `/dashboard/learning/{level_slug}/` must load within 300ms on a warm DB. Avoid N+1 on resource status lookups — fetch all `ResourceProgress` rows for the enrollment in one query.
- **Accessibility:** status selectors must be keyboard-navigable and screen-reader labelled.
- **Auth:** all `/dashboard/learning/` routes require authentication; redirect to `/login/` if unauthenticated.

---

## Open Questions

1. **Status ambiguity:** Confirm that `ALREADY_KNEW` (قبلاً می‌دونستم) and `DONE` (خوندم) are the intended split for "already studied" vs "studied." If they are the same, we collapse to four statuses.
2. **Profile visibility:** Should the badge and enrollment be visible on a public-facing profile page, or private by default? (Relevant to v14 scope.)
3. **Completion definition:** Is 100% required resources = completed, or should the user explicitly click a "تکمیل کردم" button? An explicit confirmation prevents accidental auto-completion.
4. **Re-enrollment:** If a user unenrolls and re-enrolls, should prior progress be restored or reset?
5. **Aggregate counts on roadmap pages:** "X نفر در حال یادگیری" — should this be real-time from DB or a cached/periodic count? Real-time is trivial at low scale; cache it if the roadmap page becomes high-traffic.

---

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| v12 — User Auth | Backlog | Required: no enrollment without a user identity |
| v14 — User Dashboard | Backlog | Required: learning dashboard lives inside the user dashboard shell |
| v16 — Roadmap + RoadmapResource | **Shipped** | The `RoadmapResource` model is the source of truth for resources and their order |

**Earliest possible start:** after v12 and v14 ship.

---

## Effort Estimate (rough)

| Area | Estimate |
|---|---|
| DB models + migration (Enrollment, ResourceProgress, status enum) | 2h |
| Enrollment create/unenroll routes + service | 2h |
| Learning dashboard template (per-level) | 4h |
| Enrollment index page | 1.5h |
| Status update API endpoint + async JS | 3h |
| Badge logic + profile display | 2.5h |
| Aggregate counts on roadmap level pages | 1h |
| Admin analytics read-only count | 1h |
| **Total** | **~17h (~2.5 days)** |

---

## Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-08-09 | Order-only, no timeline/date math | Milad confirmed: sequence is sufficient; date scheduling adds complexity with low marginal value |
| 2026-08-09 | Multi-level enrollment allowed, separate dashboards | Milad confirmed: users may study for current + target level in parallel |
| 2026-08-09 | Badges on user profile | Milad confirmed: social proof element wanted |
| 2026-08-09 | Resources = v16 RoadmapResource | Confirmed assumption; no new content type needed |
