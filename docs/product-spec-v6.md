# Product Spec v6 — پت فیچر (Visitor Analytics)

> **Prerequisite:** [Product Spec v5](./product-spec-v5.md) must be shipped · **Parent:** [Product overview](./product-spec.md)

## 1. Summary

| Field | Value |
|-------|-------|
| **Version** | v6 — Visitor Analytics |
| **Status** | Shipped |
| **Goal** | Give the admin a private dashboard to understand site traffic — which content gets read, how the site is growing, and where readers come from |
| **Builds on** | Existing `visitor_token` cookie (v4), `Post.view_count` (v2) |
| **Epic** | Visitor Analytics |

**Scope in two sentences:** Add a `PageView` event log captured automatically by FastAPI middleware on every public page visit, with bot filtering and visitor dedup via the existing `visitor_token` cookie. Surface this data in a private admin dashboard (`/admin/analytics/`) with period filters, top-content tables, and referrer breakdown — all in Jalali dates.

**`Post.view_count` strategy (Option B):** Keep the existing `Post.view_count` column and its public display on blog pages unchanged. `PageView` is additive — it powers the admin dashboard only. No breaking migration, no change to public UX.

---

## 2. Problem & Goals

**Problem:** The site has no visibility into traffic. `Post.view_count` is a naive counter (no dedup, no bot filtering, blogs only). Books and tools have zero tracking. There is no way to answer "is the site growing?", "what content resonates?", or "where do readers come from?"

**v6 goals:**

- **Track** every public page visit automatically, with bot filtering and visitor dedup
- **Surface** top content (books, posts, tools) by view count in the admin
- **Show** traffic trend over time with Jalali date labels
- **Identify** top referrer domains to understand which channels drive traffic
- **Augment** existing admin list pages (books, tools, posts) with view count columns

---

## 3. Data Collection

### 3.1 `PageView` Model (new)

```python
class PageView(Base):
    __tablename__ = "page_views"

    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String(500))
    page_type: Mapped[str] = mapped_column(String(50))
    # page_type values: "home" | "library" | "book" | "blog" | "post"
    #                   | "tools" | "tool" | "about" | "contact" | "other"
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # FK-less int pointing to book.id / post.id / tool.id depending on page_type
    visitor_token: Mapped[str] = mapped_column(String(64), index=True)
    referrer_domain: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    # Domain only (e.g. "google.com", "t.me") — never the full URL
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
```

**Indexes:** `created_at` (period filtering), `visitor_token` (unique visitor count), `(page_type, entity_id)` (top-content queries), `path` (per-page breakdown).

### 3.2 Middleware — Automatic Capture

A FastAPI middleware (`app/core/analytics.py`) intercepts every request to public routes and writes a `PageView` row **after** the response is sent (so it never slows down page load).

**What gets tracked:** All routes under `web/routes.py` — home, library, book detail, blog, post detail, tools, tool detail, about, contact.

**What is excluded:**
- Any path starting with `/admin/` or `/api/`
- Static files (`/static/`)
- Requests from known bot User-Agents (see §3.3)
- HTTP error responses (4xx, 5xx)

**`visitor_token` sourcing:** Read from the existing visitor cookie (`peek_visitor_token`). If the cookie is absent (first visit before any rating interaction), derive a fallback token by hashing `IP + User-Agent` — this is never stored as PII, only as a hash. The cookie-based token is preferred when available.

**Referrer extraction:** Read the `Referer` HTTP header, extract domain only via `urllib.parse.urlparse`. Store `None` for direct traffic (no Referer header).

### 3.3 Bot Filtering

Exclude requests whose `User-Agent` matches any of the following substrings (case-insensitive):

```
bot, crawler, spider, scraper, curl, wget, python-requests,
python-httpx, go-http-client, java/, ahrefsbot, semrushbot,
mj12bot, dotbot, bingbot, googlebot, yandexbot, baiduspider
```

This list lives in `app/core/analytics.py` as a module-level constant so it can be extended without touching the middleware logic.

---

## 4. Admin Dashboard — `/admin/analytics/`

### 4.1 Layout

Single page with four sections, stacked vertically:

```
[ Period filter tabs ]

[ Summary cards row ]

[ Top Content — Books | Posts | Tools ]

[ Traffic over time table ]

[ Top Referrers table ]
```

### 4.2 Period Filter

Tab-style selector at the top of the page. Options:

| Label (Persian) | Value | Range |
|-----------------|-------|-------|
| امروز | `today` | Current Jalali day (00:00 → now) |
| ۷ روز اخیر | `7d` | Last 7 calendar days |
| ۳۰ روز اخیر | `30d` | Last 30 calendar days |
| همه‌وقت | `all` | No date filter |

Implemented as query param (`?period=7d`). Default: `7d`.

### 4.3 Summary Cards

Three cards in a row:

| Card | Metric | Query |
|------|--------|-------|
| کل بازدید | Total `PageView` rows in period | `COUNT(*)` |
| بازدیدکننده‌های یکتا | Distinct `visitor_token` values in period | `COUNT(DISTINCT visitor_token)` |
| پربازدیدترین روز | Date with highest view count in period | `GROUP BY DATE(created_at) ORDER BY count DESC LIMIT 1` |

### 4.4 Top Content Tables

Three side-by-side (or tabbed) tables. Each shows the top 10 items for the selected period.

**Top Books:**

| Column | Source |
|--------|--------|
| عنوان | `Book.title` |
| بازدید | `COUNT(*)` where `page_type='book'` and `entity_id=book.id` |
| بازدید یکتا | `COUNT(DISTINCT visitor_token)` same filter |

**Top Posts:**

| Column | Source |
|--------|--------|
| عنوان | `Post.title` |
| بازدید | COUNT from `PageView` where `page_type='post'` |
| بازدید یکتا | DISTINCT visitor_token |
| شمارنده‌ی قدیمی | `Post.view_count` (shown for reference, labeled "شمارنده‌ی قدیمی") |

**Top Tools:**

| Column | Source |
|--------|--------|
| عنوان | `Tool.title` |
| بازدید | COUNT from `PageView` where `page_type='tool'` |
| بازدید یکتا | DISTINCT visitor_token |

### 4.5 Traffic Over Time Table

A simple table showing daily view counts for the selected period. For "همه‌وقت", limit to the last 90 days.

| Column | Notes |
|--------|-------|
| تاریخ | Jalali date (using existing `jalali.py` utility) |
| کل بازدید | Total `PageView` rows for that day |
| بازدیدکننده‌ی یکتا | Distinct visitor_tokens for that day |

Rows ordered newest-first. No chart in v6 — a table is sufficient. Chart can be added later without changing the data model.

### 4.6 Top Referrers Table

Top 10 referrer domains for the selected period.

| Column | Notes |
|--------|-------|
| منبع | `referrer_domain` value; null shown as "مستقیم" (direct) |
| بازدید | COUNT(*) for that domain |

---

## 5. Per-Entity View Counts in Admin List Pages

Surface `PageView` counts on existing admin list pages by querying aggregates. These are "all time" counts (no period filter — keeps the list pages fast and simple).

| Admin page | Change |
|------------|--------|
| `/admin/books/` | Add "بازدید" column (all-time view count from `PageView`) |
| `/admin/tools/` | Add "بازدید" column (all-time view count from `PageView`) |
| `/admin/posts/` | Replace existing `Post.view_count` column label with "بازدید (قدیمی)" and add a second "بازدید (جدید)" column from `PageView` |

**Performance note:** These counts are aggregate queries joined at page load. Acceptable for low-traffic admin use. If the admin list pages become slow under large data volumes, add a `view_count` cache column — but do not pre-optimize for v6.

---

## 6. User Stories

- *As Milad (admin), I want to see total site traffic over the last 7 and 30 days so I know if the site is growing*
- *As Milad (admin), I want to see which books get the most views so I can prioritize adding notes and improving those pages*
- *As Milad (admin), I want to see which posts get the most traffic so I know what topics resonate*
- *As Milad (admin), I want to see where my traffic comes from so I know which channels are worth investing in*
- *As Milad (admin), I want all dates shown in Jalali so I can read the data naturally*

---

## 7. Acceptance Criteria

### Data collection
- [ ] Every public page visit writes one `PageView` row after response is sent
- [ ] Requests matching known bot User-Agents are silently skipped (no row written)
- [ ] HTTP 4xx/5xx responses are not tracked
- [ ] `/admin/`, `/api/`, and `/static/` paths are never tracked
- [ ] `referrer_domain` stores domain only — never a full URL
- [ ] `visitor_token` uses the cookie value when present; falls back to hashed IP+UA

### Dashboard
- [ ] `/admin/analytics/` renders with default period `7d`
- [ ] Period tabs switch correctly; selected period is reflected in all four sections
- [ ] Summary cards show correct counts for selected period
- [ ] Top Books/Posts/Tools tables show top 10 for selected period with view + unique visitor counts
- [ ] Posts table shows both new (`PageView`) and old (`Post.view_count`) counts, clearly labeled
- [ ] Traffic over time table shows daily rows in Jalali dates, newest first
- [ ] Referrer table shows top 10 domains; null referrer displayed as "مستقیم"

### Admin list pages
- [ ] Books admin list shows all-time view count column
- [ ] Tools admin list shows all-time view count column
- [ ] Posts admin list shows both old and new view count columns

### Compatibility
- [ ] `Post.view_count` is still incremented on post visits (existing public blog behavior unchanged)
- [ ] Alembic migration creates `page_views` table with correct indexes
- [ ] No change to any public-facing template

---

## 8. Out of Scope for v6

| Feature | Reason |
|---------|--------|
| Traffic chart (bar/line graph) | Needs JS charting lib or SVG generation — table is sufficient for v6 |
| "New vs returning" visitor breakdown | Adds query complexity; low value at current traffic scale |
| UTM / campaign parameter tracking | No paid campaigns running |
| Geographic breakdown | Audience is almost entirely Iran — not actionable |
| Real-time dashboard | Low traffic; not needed |
| Public view counts on books/tools | Admin-only for now |
| Data export (CSV) | Post-v6 |
| Data retention / pruning policy | Low volume; keep all data for now |
| Removing `Post.view_count` | Deferred — keep both as per Option B decision |

---

## 9. Technical Notes for Engineer

### New files
| File | Purpose |
|------|---------|
| `app/core/analytics.py` | Middleware class + bot UA list + `referrer_domain` extractor |
| `app/models/page_view.py` | `PageView` model |
| `app/services/analytics.py` | Query functions: period aggregates, top content, daily breakdown, referrers |
| `app/templates/admin/analytics.html` | Dashboard template |

### Changed files
| File | Change |
|------|--------|
| `app/main.py` | Register analytics middleware |
| `app/models/__init__.py` | Import `PageView` |
| `alembic/env.py` | Import `PageView` model |
| `app/admin/routes.py` | Add `/admin/analytics/` route; update books/posts/tools list routes to pass view counts |
| `app/templates/admin/books_list.html` | Add view count column |
| `app/templates/admin/tools_list.html` | Add view count column |
| `app/templates/admin/posts_list.html` | Update view count columns |

### Middleware registration order
Register the analytics middleware **after** the session middleware and **before** routing — so `visitor_token` cookie is readable but the route handler hasn't run yet. Write the `PageView` row in a `background_task` or using `starlette.background.BackgroundTask` to avoid adding latency to the response.

### Jalali dates
Use the existing `app/core/jalali.py` utility. The daily breakdown table needs a `to_jalali(date)` call per row in the service layer, not in the template.

---

## 10. Open Questions

| Question | Owner | Status |
|----------|-------|--------|
| Should the analytics nav link appear in the admin sidebar? (Assumed yes) | Milad | Assumed yes — confirm |
| Bot UA list — use a hardcoded constant or a DB-configurable list? | Engineer | Hardcoded constant recommended for v6 |
| If `visitor_token` cookie is absent, use hashed IP+UA fallback or skip tracking entirely? | Engineer | Fallback recommended — otherwise first visits to non-rating pages are lost |

---

## Deployment Status

| Field | Value |
|-------|-------|
| **Status** | Shipped |
| **Deploy date** | July 2026 |
| **Platform** | Hamravesh Darkube (production) |
| **Notes** | — |
