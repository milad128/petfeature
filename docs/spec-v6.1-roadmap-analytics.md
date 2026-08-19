# Product Spec v6.1 — پت فیچر (Roadmap Analytics Extension)

> **Prerequisite:** [Product Spec v6](./spec-v6-analytics.md) must be shipped · **Parent:** [Product overview](./spec.md)

## 1. Summary

| Field | Value |
|-------|-------|
| **Version** | v6.1 — Roadmap Analytics Extension |
| **Status** | Planned |
| **Goal** | Classify roadmap page visits properly in the analytics middleware and surface a roadmap traffic section in the admin dashboard |
| **Builds on** | `PageView` model and middleware (v6), Roadmap pages (v16) |
| **Effort** | ~3–4 hours |
| **Epic** | Visitor Analytics |

**Scope in two sentences:** The three roadmap pages (`/path/`, `/path/hiring/`, `/path/{level_slug}/`) shipped in v16 currently fall into the `"other"` analytics bucket, making them invisible in the admin dashboard. This spec classifies them with proper `page_type` values in the middleware and adds a "مسیر یادگیری" section to `/admin/analytics/` showing total roadmap traffic and a per-level leaderboard.

---

## 2. Problem & Goals

**Problem:** v16 added the roadmap section (`/path/*`) but the analytics middleware (`_classify_path`) was not updated. All roadmap visits are stored as `page_type = "other"` with no slug — indistinguishable from any other unclassified route. Milad cannot answer "how much traffic is the roadmap getting?", "which level is most popular?", or "is the hiring page driving engagement?" — all of which directly inform whether L2–L6 full pages should be prioritized.

**v6.1 goals:**

- **Classify** roadmap paths into distinct `page_type` values so they leave the `"other"` bucket
- **Track** per-level slug so individual level pages can be ranked by popularity
- **Surface** roadmap traffic in the admin analytics dashboard with a period-filtered leaderboard
- **No migration** — the existing `PageView` schema is sufficient

---

## 3. Tracking Layer Changes

### 3.1 `_classify_path` additions (`app/core/analytics.py`)

Add the following cases to `_classify_path` **before** the `"other"` fallback:

| Path pattern | `page_type` | `slug` |
|---|---|---|
| `/path/` (exact) | `roadmap` | `None` |
| `/path/hiring/` (exact) | `roadmap_hiring` | `None` |
| `/path/{level_slug}/` | `roadmap_level` | `level_slug` value |

The roadmap level regex to add:

```python
_ROADMAP_LEVEL_RE = re.compile(r"^/path/([^/]+)/$")
```

Classification order in `_classify_path`:

```python
if path == "/path/":
    return "roadmap", None
if path == "/path/hiring/":
    return "roadmap_hiring", None
m = _ROADMAP_LEVEL_RE.match(path)
if m:
    return "roadmap_level", m.group(1)
```

### 3.2 `entity_id` handling

Roadmap levels are static data (defined in `roadmap_data.py`) — there is no `RoadmapLevel` DB model with an integer PK. Therefore `entity_id` stays `NULL` for all three roadmap `page_type` values. The `slug` (level identifier) is captured via the existing `path` column and the new slug classification.

**No change to `_resolve_entity_id`** — it only resolves `book`, `post`, and `tool` types; roadmap types are simply skipped.

### 3.3 Historical data

Existing `"other"` rows written before this change are **not backfilled**. They remain as `"other"` — acceptable, since v16 shipped recently and traffic volume is low.

---

## 4. Service Layer

### 4.1 New function — `top_roadmap_levels` (`app/services/analytics.py`)

```python
async def top_roadmap_levels(
    session: AsyncSession,
    period: Optional[str] = None,
    limit: int = 10,
) -> list[dict]:
    """
    Return top roadmap level pages by view count for the given period.
    Only page_type='roadmap_level' rows are included (excludes landing + hiring).
    Each result: {slug, views, unique_views}
    """
```

- Filters on `page_type = "roadmap_level"`
- Groups by `path` (which carries the full `/path/{slug}/` value — extract slug via string split or store it from the regex match)
- Orders by `COUNT(*)` descending
- Returns at most `limit` rows

> **Note to engineer:** The slug can be derived from the `path` column by stripping `/path/` prefix and trailing `/`, or alternatively the classification middleware can store the slug in a dedicated field. Since no schema change is in scope, derive from `path` in the query.

### 4.2 New function — `roadmap_summary` (`app/services/analytics.py`)

```python
async def roadmap_summary(
    session: AsyncSession,
    period: Optional[str] = None,
) -> dict:
    """
    Return {total_views, unique_views, hiring_views, landing_views}
    for all roadmap page_types combined and individually.
    """
```

- `total_views`: COUNT(*) where `page_type IN ('roadmap', 'roadmap_hiring', 'roadmap_level')`
- `unique_views`: COUNT(DISTINCT visitor_token) same filter
- `hiring_views`: COUNT(*) where `page_type = 'roadmap_hiring'`
- `landing_views`: COUNT(*) where `page_type = 'roadmap'`

---

## 5. Admin Dashboard Changes (`/admin/analytics/`)

### 5.1 New section — "مسیر یادگیری"

Add a new section **below the Tools leaderboard**, consistent with the existing section style.

**Layout:**

```
[ مسیر یادگیری ]

  کل بازدید بخش: X   |   بازدیدکننده‌ی یکتا: Y

  صفحه‌ی اصلی مسیر: X بازدید
  صفحه استخدام: X بازدید

  [ جدول: پربازدیدترین سطح‌ها ]
  | سطح              | بازدید | بازدید یکتا |
  | مدیر محصول APM   |  ...   |     ...     |
  | سطح صفر (L0)     |  ...   |     ...     |
  | سطح یک (L1)      |  ...   |     ...     |
  | ...               |        |             |
```

### 5.2 Slug → Persian label mapping

Mapping is done in the **Jinja2 template** (not in the service). The service returns raw slugs; the template maps them to display names.

| Slug | Persian label |
|---|---|
| `apm` | مدیر محصول APM |
| `hiring` | مسیر استخدامی |
| `l0` | سطح صفر — ورود به مدیریت محصول |
| `l1` | سطح یک — مدیر محصول جونیور |
| `l2` | سطح دو — مدیر محصول میانی |
| `l3` | سطح سه — مدیر محصول ارشد |
| `l4` | سطح چهار — اصول محصول |
| `l5` | سطح پنج — استراتژی محصول |
| `l6` | سطح شش — رهبری محصول |

> Confirm exact slug values against `roadmap_data.py` before implementing the template map. Add any missing slugs to this table.

### 5.3 Period filter

The roadmap section respects the same period filter (`?period=`) as the rest of the dashboard. No separate filter needed.

### 5.4 Global KPI card

Roadmap visits already roll into the global "کل بازدید" and "بازدیدکننده‌های یکتا" KPI cards — they are recorded by the middleware like any other page visit. No change to the KPI card queries.

---

## 6. User Stories

- *As Milad (admin), I want roadmap page visits classified separately so they don't pollute the "other" bucket*
- *As Milad (admin), I want to see total roadmap section traffic for the selected period so I know how much interest the feature is getting*
- *As Milad (admin), I want a per-level leaderboard so I know which roadmap levels users visit most*
- *As Milad (admin), I want the hiring page tracked separately so I can measure its traffic independently*

---

## 7. Acceptance Criteria

### Tracking layer
- [ ] `/path/` visits are stored with `page_type = "roadmap"`
- [ ] `/path/hiring/` visits are stored with `page_type = "roadmap_hiring"`
- [ ] `/path/{slug}/` visits are stored with `page_type = "roadmap_level"` and correct slug derivable from `path`
- [ ] No roadmap path falls into `page_type = "other"` after this change
- [ ] `entity_id` remains `NULL` for all roadmap page types (no resolution attempted)
- [ ] Existing classification logic for `home`, `library`, `book`, `blog`, `post`, `tools`, `tool`, `about`, `contact` is unchanged

### Service layer
- [ ] `top_roadmap_levels()` returns correct results filtered by period
- [ ] `roadmap_summary()` returns correct totals and per-page-type breakdowns
- [ ] Both functions handle the `"all"` period (no date filter) correctly

### Admin dashboard
- [ ] "مسیر یادگیری" section renders below the Tools leaderboard
- [ ] Section respects the active period filter
- [ ] Total roadmap views and unique visitors display correctly
- [ ] Landing and hiring page individual stats display correctly
- [ ] Per-level leaderboard shows up to 10 rows, ordered by views descending
- [ ] Raw slugs are mapped to Persian display names in the template
- [ ] Unknown slugs (not in the map) fall back to displaying the raw slug

---

## 8. Out of Scope for v6.1

| Feature | Reason |
|---|---|
| Historical backfill of "other" rows | Low traffic volume; not worth the complexity |
| Referrer breakdown per roadmap level | Overkill at current scale |
| Per-level entity FK (RoadmapLevel model) | Levels are static data; no DB model with integer PK exists |
| Chart/graph for roadmap traffic | Table is sufficient; chart deferred |
| Public view count display on roadmap pages | Admin-only analytics |

---

## 9. Technical Notes for Engineer

### Changed files

| File | Change |
|---|---|
| `app/core/analytics.py` | Add `_ROADMAP_LEVEL_RE` regex; add 3 new cases to `_classify_path` |
| `app/services/analytics.py` | Add `top_roadmap_levels()` and `roadmap_summary()` functions |
| `app/admin/routes.py` | Call new service functions and pass results to analytics template |
| `app/templates/admin/analytics.html` | Add "مسیر یادگیری" section with slug→label Jinja2 mapping |

### No migration required

The `page_views` table schema is unchanged. New `page_type` string values (`roadmap`, `roadmap_hiring`, `roadmap_level`) are stored in the existing `VARCHAR(50)` column — well within capacity.

### Slug derivation from `path`

Since `entity_id` is `NULL` for roadmap levels, the slug must be derived from the `path` column in the service query:

```sql
-- Example: extract slug from path '/path/l1/'
TRIM(BOTH '/' FROM REPLACE(path, '/path/', ''))
```

Or handle in Python after fetching rows — either approach is acceptable.

---

## 10. Open Questions

| Question | Owner | Status |
|---|---|---|
| Confirm exact slug values in `roadmap_data.py` match the label map in §5.2 | Engineer | Open — verify before implementing template map |

---

## Deployment Notes

| Field | Value |
|---|---|
| **Migration required** | No |
| **Downtime required** | No |
| **Rollback risk** | Low — additive change only; existing data unaffected |
