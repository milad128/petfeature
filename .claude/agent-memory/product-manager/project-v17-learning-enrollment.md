---
name: project-v17-learning-enrollment
description: v17 Learning Enrollment & Progress Tracking — users enroll in roadmap levels, track resource status, earn badges; blocked on v12+v14
metadata:
  type: project
---

v17 is a candidate feature for Learning Enrollment & Progress Tracking (ثبت‌نام یادگیری).

**Why:** Roadmap (v16) shows users *what* to study but gives no way to track progress. Registered users need a personal learning dashboard.

**Core decisions (2026-08-09):**
- Resources = existing `RoadmapResource` (v16) — no new content type
- Timeline = order-only, no date math (user confirmed)
- Multi-level enrollment allowed; separate dashboards per level, never merged
- 5 resource statuses: WANT_TO_STUDY, STUDYING, DONE, ALREADY_KNEW, SKIPPED
- Badges on user profile (Enrolled → In Progress → Completed per level)
- Aggregate counts on roadmap level pages ("X نفر در حال یادگیری")
- Completion = 100% of required resources with DONE or ALREADY_KNEW

**Open question:** Is ALREADY_KNEW vs DONE the right split for "already studied" vs "studied"? Needs Milad confirmation.

**Effort:** ~17h (~2.5 days)

**Spec:** `docs/New idea/learning-enrollment.md`

**Blocked on:** v12 (User Auth) → v14 (User Dashboard). Can't start until both ship.

**How to apply:** When discussing v17 scope or auth-gated features, reference this as the next major feature after v14 ships. [[project-v12-user-auth]] [[project-v14-user-dashboard]] [[project-v16-roadmap]]
