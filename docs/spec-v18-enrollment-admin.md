# Product Spec v18 — Enrollment Admin & Learning Statistics (ادمین ثبت‌نام یادگیری)

> **Prerequisite:** [v17 Learning Enrollment](./spec-v17-learning-enrollment.md) must ship first · **Builds on:** [v12 User Auth](./spec-v12-user-auth.md) (admin session + `User`), [v16 Roadmap](./spec-v16-roadmap.md) (`RoadmapResource`, level slugs) · **Related:** [v6 Visitor Analytics](./spec-v6-analytics.md) (period filters, Jalali, PageView for conversion) · **Parent:** [Product overview](./spec.md)

## 1. Summary

| Field | Value |
|-------|-------|
| **Version** | v18 — Enrollment Admin & Learning Statistics |
| **Status** | In development |
| **Goal** | Give Milad a dedicated admin surface to see who enrolled, how far they got, and whether the learning path is converting |
| **Builds on** | v17 (`Enrollment`, `ResourceProgress`, public counts), v12 (`User`, admin auth), v16 (levels + resources) |
| **Epic** | Roadmap |

**Scope in two sentences:** Replace the two-column enroll snippet on `/admin/analytics/` with a real admin section under مسیر یادگیری: a statistics overview, a filterable enrollment list, and a read-only detail of one enrollment (progress formula + per-resource statuses). Admin still cannot edit a learner's statuses.

v17 already stores everything needed. v18 is query + UI. No new tables.

---

## 2. Problem & Goals

**Problem:** v17 lets people enroll and track progress, but the only admin view is a tiny read-only table on analytics (`ثبت‌نام فعال` / `تکمیل‌شده` per level). That cannot answer: who enrolled this week, who stalled at 0%, which level converts from `/path/` visits, or what a specific person has marked as خوندم.

**v18 goals:**

- **See the funnel:** visits → enrolls → in-progress → completed, per level and for a chosen period
- **See the people:** a searchable list of enrollments with progress and badge tier
- **See one learner:** read-only detail of dates, progress formula, and every resource status
- **Keep analytics light:** analytics keeps a summary + link; the dedicated page holds the full numbers
- **Stay read-only:** no admin override of `ResourceProgress`, no admin unenroll, no emailing learners

---

## 3. User Stories

- *As Milad, I want a sidebar item «ثبت‌نام‌ها» under مسیر یادگیری so I do not hunt for enroll data inside visitor analytics*
- *As Milad, I want summary cards (active, unique learners, completed, unenrolled, average progress) so I know if the path is alive*
- *As Milad, I want a per-level table with active / learning / completed / unenrolled and average progress so I can compare hiring vs APM vs PM*
- *As Milad, I want enrollments and completions over a period (۷ / ۳۰ / ۹۰ روز, Jalali) so I can see whether a launch week actually moved the numbers*
- *As Milad, I want conversion from `/path/{slug}/` views to enrolls in that period, when PageView data exists*
- *As Milad, I want a status mix (blank / دارم می‌خونم / خوندم / قبلاً می‌دونستم / رد کردم) so I know if people actually use the tracker*
- *As Milad, I want a «متوقف‌شده» list: active enrollments older than ۱۴ days with 0% progress*
- *As Milad, I want to filter the enrollment list by level, state, and name/email*
- *As Milad, I want to open one enrollment and see that user's resource statuses without being able to change them*

---

## 4. What v17 already has (do not rebuild)

| Piece | Where | v18 change |
|-------|--------|------------|
| `Enrollment` + `ResourceProgress` | `app/models/learning.py` | Query only |
| `enroll_counts_by_level()` | `app/services/learning.py` | Keep; overview uses a richer query |
| Two-column table | `/admin/analytics/` | Replace with 3–4 headline numbers + link to `/admin/learning/` |
| Public social counts | `/path/{slug}/` | Unchanged |
| Progress formula | `(DONE + ALREADY_KNEW) / required` | Same formula in admin |
| Badge tiers | enrolled &lt; 50% / in progress ≥ 50% / completed 100% | Show as Persian labels |

Enrollable slugs stay `hiring` + `FULL_PAGE_SLUGS` (today: hiring, apm, pm). Stub levels do not appear as empty rows unless they somehow have data.

---

## 5. Pages

All pages: admin auth, RTL, Persian copy, Persian digits (`fa_digits`), Jalali dates. Empty states in Persian.

### 5.1 Overview — `GET /admin/learning/`

Primary landing. Period filter matches analytics: **۷ روز / ۳۰ روز / ۹۰ روز / همه** (default ۳۰ روز). Period applies to *new enrollments*, *new completions*, *new unenrolls*, the time-series, and conversion. Snapshot cards (active now, unique learners now) are **current state**, labelled «الان».

**A. Snapshot cards (current state)**

| Card | Definition |
|------|------------|
| ثبت‌نام فعال | `unenrolled_at IS NULL` |
| در حال یادگیری | active and `completed_at IS NULL` |
| تکمیل‌شده | active and `completed_at IS NOT NULL` |
| لغوشده | `unenrolled_at IS NOT NULL` (all-time, not period) |
| یادگیرنده یکتا | distinct `user_id` with ≥ 1 active enrollment |
| میانگین پیشرفت | mean of `compute_progress` over active incomplete enrollments; «—» if none |

**B. Period cards (selected range)**

| Card | Definition |
|------|------------|
| ثبت‌نام جدید | rows with `enrolled_at` in range (include later-unenrolled; this is intake) |
| تکمیل جدید | rows whose `completed_at` falls in range |
| لغو جدید | rows whose `unenrolled_at` falls in range |

**C. Per-level table**

One row per enrollable level (hiring, apm, pm, …). Columns:

| Column | Persian | Notes |
|--------|---------|--------|
| Level | سطح | `lv.fa` |
| Path views (period) | بازدید صفحه | Count of `PageView` where path is `/path/{slug}/` or `/path/hiring/` in range. Hide the column if PageView cannot classify these paths. |
| New enrolls (period) | ثبت‌نام جدید | |
| Conversion | تبدیل | `new enrolls / path views` as Persian percent; «—» if views = 0 |
| Active now | فعال | |
| Learning now | در حال یادگیری | active, not completed |
| Completed now | تکمیل‌شده | |
| Unenrolled (all-time) | لغوشده | |
| Avg progress | میانگین پیشرفت | among active incomplete; Persian percent |

**D. Time series**

One simple bar/line block (same visual language as analytics daily traffic, no new chart library):

- ثبت‌نام per Jalali day in the period
- تکمیل per Jalali day in the period

If period is «همه» and the range is huge, bucket by Jalali month instead of day.

**E. Tracker usage (all-time, among active enrollments)**

Counts of `ResourceProgress.status` plus implied blanks:

| Bucket | Persian |
|--------|---------|
| no row | بدون وضعیت |
| `STUDYING` | دارم می‌خونم |
| `DONE` | خوندم |
| `ALREADY_KNEW` | قبلاً می‌دونستم |
| `SKIPPED` | رد کردم |

Denominator for «بدون وضعیت» = required+optional resources on that level minus rows that exist. Show as a compact table, not a pie chart.

**F. Stalled list**

Active, not completed, `enrolled_at` older than **۱۴ days**, progress = 0%. Max 20 rows. Columns: user name, level, Jalali enroll date, link to detail. Empty copy: «ثبت‌نام متوقف‌شده‌ای نیست.»

**G. Jump**

Button/link: «همه ثبت‌نام‌ها» → `/admin/learning/enrollments/`

### 5.2 Enrollment list — `GET /admin/learning/enrollments/`

Table of enrollments. Default: active only, newest `enrolled_at` first. Pagination **۵۰** per page (same as `/admin/users/`).

**Filters (GET query params, no JS required)**

| Param | Values |
|-------|--------|
| `level` | `hiring` / `apm` / `pm` / … or empty = all |
| `state` | `active` (default) / `learning` / `completed` / `unenrolled` / `all` |
| `q` | trim, match user `name` or `email` (case-insensitive) |

**Columns**

| Column | Persian | Notes |
|--------|---------|--------|
| Name | نام | Link to detail |
| Email | ایمیل | LTR |
| Level | سطح | |
| Enrolled | تاریخ ثبت‌نام | Jalali |
| Last progress | آخرین وضعیت | `max(ResourceProgress.updated_at)` or «—» |
| Progress | پیشرفت | Persian percent + thin bar |
| Badge | نشان | ثبت‌نام شده / در حال یادگیری / تکمیل‌شده (hidden if unenrolled) |
| State | وضعیت | فعال / در حال یادگیری / تکمیل‌شده / لغوشده |

Summary line above the table: «**X** ثبت‌نام» for the current filter.

Empty: «ثبت‌نامی با این فیلتر نیست.»

### 5.3 Enrollment detail — `GET /admin/learning/enrollments/{id}/`

Read-only. 404 if id missing.

**Header**

- User name, email (LTR), link to `/admin/users/` if that list can deep-link; otherwise name only
- Level fa + link to public `/path/{slug}/` (or hiring)
- Jalali `enrolled_at`, `completed_at` or «هنوز تکمیل نشده», `unenrolled_at` if set
- Progress percent, formula reminder: پیشرفت = (خوندم + قبلاً می‌دونستم) ÷ منابع الزامی
- Counts: done / required / studying / blank / skipped (same semantics as the user tracker)
- Badge tier

**Resource table** — v16 order: ورود → هسته → حمایتی → پل. Columns: title, category, الزامی/اختیاری, status (Persian or «وضعیت ندارد»), `updated_at` Jalali or «—». Titles are not editable. No `<select>`.

Footer: «بازگشت به فهرست».

### 5.4 Analytics snippet (existing `/admin/analytics/`)

Remove the full per-level enroll table added in v17. Replace with:

- One line: فعال **X** · تکمیل‌شده **Y** · یادگیرنده یکتا **Z**
- Link: «آمار ثبت‌نام یادگیری ←» to `/admin/learning/`

Visitor analytics (PageView) stays on analytics. Learning enrollments live on the new pages.

---

## 6. Navigation

In `admin/base.html`, under گروه **🗺️ مسیر یادگیری**, add after the existing resource links:

| Label | URL | `active_nav` |
|-------|-----|----------------|
| ثبت‌نام‌ها | `/admin/learning/` | `learning` (also active on list + detail) |

Do not add a second top-level group.

---

## 7. Routes

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| `GET` | `/admin/learning/` | Admin | Overview + stats |
| `GET` | `/admin/learning/enrollments/` | Admin | Filterable list |
| `GET` | `/admin/learning/enrollments/{id}/` | Admin | Read-only detail |

Query params on overview: `period=7|30|90|all` (default `30`).  
Query params on list: `level`, `state`, `q`, `page`.

Unknown id → 404. Unauthenticated admin → existing admin login.

No POST in v18. No CSV in v18 (see out of scope).

---

## 8. Service layer

Extend `app/services/learning.py` (keep routes thin). Suggested functions — names can match the codebase style:

| Function | Purpose |
|----------|---------|
| `admin_overview(db, period_days \| None)` | Snapshot cards + period cards + per-level rows + daily series + status mix + stalled list |
| `admin_list_enrollments(db, *, level, state, q, page, per_page=50)` | Paginated rows with user, progress, badge, last activity |
| `admin_get_enrollment(db, enrollment_id)` | Header + `list_resources_with_status` for that row; include unenrolled (admin may inspect soft-deleted) |

Reuse `compute_progress` and badge-tier helper from v17. Join `User` in one query. Do not N+1 progress for the list: either a grouped subquery on `ResourceProgress` or a single progress map keyed by `enrollment_id`.

Path-view conversion: if `PageView` rows exist for `/path/hiring/` and `/path/{slug}/`, count them in the period. If the v6.1 path classifier is missing, match `path` prefix instead of inventing a new `page_type`. If counting is unreliable, omit the بازدید / تبدیل columns rather than showing wrong numbers.

---

## 9. Data rules

- **Active** = `unenrolled_at IS NULL`
- **Learning** = active and `completed_at IS NULL`
- **Completed** = active and `completed_at IS NOT NULL` (v17 sets this at 100%)
- **Unenrolled** rows stay in the database; they appear in لغوشده stats and in the list when `state=unenrolled` or `all`
- Progress and badge on unenrolled rows: still compute from remaining `ResourceProgress` (v17 restores on re-enroll) but hide the badge column or show «لغوشده» only
- Period for «ثبت‌نام جدید» uses `enrolled_at`, even if the user later unenrolled
- No caching in v18 (same default as v17 public counts)

---

## 10. Acceptance criteria

### Overview
- [ ] `/admin/learning/` is linked from the مسیر یادگیری sidebar as «ثبت‌نام‌ها»
- [ ] Snapshot cards match SQL definitions above
- [ ] Period filter ۷ / ۳۰ / ۹۰ / همه changes period cards and the time series
- [ ] Per-level table lists every enrollable level, including zeros
- [ ] Digits are Persian; dates on the chart are Jalali
- [ ] Stalled list uses ۱۴ days and 0% progress
- [ ] Empty database: cards show ۰, tables show empty copy, page is still 200 RTL

### List
- [ ] Default shows active enrollments, newest first
- [ ] Filters work without JavaScript
- [ ] Search matches name or email
- [ ] Progress percent matches the v17 tracker for the same enrollment
- [ ] Pagination at ۵۰

### Detail
- [ ] Shows formula, counts, and every resource status in v16 order
- [ ] No status `<select>`, no save, no unenroll button
- [ ] Unenrolled enrollment is still viewable
- [ ] Unknown id → 404

### Analytics
- [ ] Full enroll table is gone from `/admin/analytics/`
- [ ] Summary line + link to `/admin/learning/` remain

### Auth & RTL
- [ ] All three pages require admin login
- [ ] `dir="rtl"` on the admin shell (existing)

---

## 11. Out of scope (v18)

| Item | Reason |
|------|--------|
| Admin edit / clear of a user's statuses | Still out of scope (v17 decision); inspect only |
| Admin unenroll or force-complete | User owns that action on the panel |
| Email, Telegram, or reminder to stalled learners | Separate feature |
| CSV / Excel export | Can follow if the list is actually used |
| Cohort comparison (week-over-week cohorts) | Overview + period is enough |
| Charts beyond the existing analytics bar style | No new JS chart library |
| Public admin numbers | Counts on `/path/` stay as v17 |
| New models or migrations | Not needed |
| Changing enroll / progress behaviour | v17 stays the source of truth |

---

## 12. NFRs

- Persian UI; level names match v16 (`مسیر استخدام`, `مبتدی (APM)`, `مدیر محصول`, …)
- One round-trip for overview aggregates (or a small fixed number of grouped queries — no per-enrollment loop in Python)
- List page: one query for the page of enrollments + one grouped progress query
- Warm-DB target for overview: 400ms
- Do not log emails in extra places; email is already on `User`
- CSRF unused (GET only)

---

## 13. Files (expected)

| Path | Role |
|------|------|
| `app/services/learning.py` | Overview / list / detail queries |
| `app/admin/routes.py` | Three GET handlers |
| `app/templates/admin/base.html` | Nav link |
| `app/templates/admin/learning_overview.html` | Stats page |
| `app/templates/admin/learning_enrollments.html` | List |
| `app/templates/admin/learning_enrollment_detail.html` | Detail |
| `app/templates/admin/analytics.html` | Shrink enroll block to summary + link |
| `tests/test_learning.py` (or `tests/test_admin_learning.py`) | Stats definitions, filters, 404, admin auth |

Reuse admin table / card / period-filter CSS. Do not add a public-facing template.

---

## 14. Dependencies & sequencing

| Dependency | Status | Notes |
|------------|--------|--------|
| v17 Learning Enrollment | **In development** | Must ship models + public enroll before this page has meaning |
| v12 User Auth | Present | `User` name/email; admin is still `ADMIN_USERNAME` / session, not Google |
| v16 Roadmap | Shipped | Level labels + resource order |
| v6 PageView | Shipped | Optional conversion column |

Ship v18 after v17 is usable in production (at least one real enrollment is enough to sanity-check the list).

---

## 15. Open questions

| Question | Recommended default | Status |
|----------|---------------------|--------|
| Include unenrolled in «ثبت‌نام جدید»? | Yes — intake, not net | Proposed |
| Stalled threshold ۱۴ days vs ۳۰? | ۱۴ | Proposed |
| Show conversion from PageView? | Yes when path counts exist; hide column otherwise | Proposed |
| Admin may open unenrolled detail? | Yes, read-only | Proposed |
| CSV export? | No in v18 | Proposed |

---

## 16. Effort estimate

| Area | Estimate |
|------|----------|
| Overview queries + period cards + per-level table | 3h |
| Time series + status mix + stalled list | 2h |
| List + filters + pagination | 2.5h |
| Detail (reuse tracker resource order) | 1.5h |
| Nav + analytics snippet shrink | 0.5h |
| Tests | 2h |
| **Total** | **~11.5h (~1.5 days)** after v17 |

---

## Decision log

| Date | Decision | Source |
|------|----------|--------|
| 2026-09-06 | v17 admin = read-only counts on analytics; no status editor | spec v17 |
| 2026-09-09 | v18 = dedicated enrollment admin + statistics; still no status editor | Milad |

---

*September 2026 — v18 in development. Statistics and inspection only; learners still own their statuses on `/dashboard/learning/{slug}/track/`.*
