# Admin Panel — Design Specification
**petfeature.ir · پت فیچر**
*July 2026 · v1.1 — Updated for v5 (About + Contact) and v6 (Analytics)*

---

## 1. Overview

The petfeature admin panel is a private, password-protected CMS used exclusively by **Milad Mirzaei** to manage all site content. There is no public access, no user roles — single admin only.

**URL prefix:** `/admin/`
**Language:** Persian (Farsi) — RTL layout throughout
**Font:** Vazirmatn
**Tech:** Server-rendered Jinja2 templates (FastAPI) — no SPA, standard HTML forms with POST/redirect

The redesign goal is a **clean, focused, content-first CMS interface** — not a flashy dashboard. The admin spends most time in forms (writing content), not dashboards. Optimize for that.

---

## 2. Navigation Structure

```
/admin/login/                     ← Login screen (no nav)

/admin/books/                     ← Book list
/admin/books/new/                 ← New book form
/admin/books/{slug}/edit/         ← Edit book form

/admin/categories/                ← Category list
/admin/categories/new/            ← New category form
/admin/categories/{id}/edit/      ← Edit category form

/admin/books/comments/            ← Book comment moderation

/admin/posts/                     ← Post list
/admin/posts/new/                 ← New post form
/admin/posts/{slug}/edit/         ← Edit post form

/admin/posts/comments/            ← Post comment moderation

/admin/tools/                     ← Tool list
/admin/tools/new/                 ← New tool form
/admin/tools/{slug}/edit/         ← Edit tool form

/admin/about/                     ← About page editor (single form)
/admin/contact/                   ← Contact messages inbox  [NEW — v5]

/admin/analytics/                 ← Visitor analytics dashboard  [NEW — v6]
```

---

## 3. Global Shell Layout

### 3.1 Shell Structure (LTR description, but rendered RTL)

```
┌──────────────────────────────────────────────────────────────┐
│  SIDEBAR (right side in RTL)  │  MAIN AREA (left side)       │
│  ─────────────────────────    │  ──────────────────────────── │
│  [Brand: logo + name]         │  [Topbar: page title + CTA]  │
│                               │                               │
│  [Nav Group: 📚 کتابخانه]     │  [Content area]              │
│    → کتاب‌ها                  │                               │
│    → دسته‌بندی‌ها             │                               │
│    → نظرها (badge)            │                               │
│                               │                               │
│  [Nav Group: ✍️ بلاگ]         │                               │
│    → یادداشت‌ها               │                               │
│    → نظرها (badge)            │                               │
│                               │                               │
│  [Nav Group: 🛠️ ابزارها]      │                               │
│    → قالب‌ها                  │                               │
│                               │                               │
│  [Nav Group: ⚙️ عمومی]        │                               │
│    → درباره من                │                               │
│    → پیام‌ها (badge) [NEW v5] │                               │
│                               │                               │
│  [Nav Group: 📊 آمار] [NEW v6]│                               │
│    → آنالیتیکس               │                               │
│                               │                               │
│  ─────────────────────────    │                               │
│  [مشاهده‌ی سایت ↗]            │                               │
│  [⏻ خروج]                     │                               │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 Sidebar specs
- **Fixed, full-height** — does not scroll with content
- **Width:** ~240px (collapse to icon-only on mobile — not currently implemented, nice-to-have)
- **Brand block:** logo image + product name "پت فیچر" + subtitle "پنل مدیریت"
- **Nav groups:** Each group has a label (non-clickable) + child links beneath
- **Active state:** Current section link is visually highlighted
- **Comment badge:** Pending comment counts shown as a badge on "نظرها" links (design must accommodate a count like `12`)
- **Unread message badge [v5]:** Unread contact message count on "پیام‌ها" link (same badge style as comment badges — accommodate counts like `5`)
- **Footer:** "View site" external link + logout link

### 3.3 Topbar specs
- **Height:** ~56px, sticky at top of main area
- **Left (LTR) / Right in RTL:** Page title (`<h1>`)
- **Right (LTR) / Left in RTL:** Primary CTA button (e.g. "کتاب جدید" on book list page) — not present on all pages
- **No breadcrumbs** — single level, always clear from page title

### 3.4 Content area
- Scrollable
- Has comfortable horizontal padding
- Max width constraint on form pages (see §5)

---

## 4. Login Screen (`/admin/login/`)

**Purpose:** Single credential gate — username + password.

### Layout
- Centered card on a neutral background
- No sidebar or topbar
- Logo + "پنل مدیریت" heading above the card

### Form fields
| Field | Type | Label |
|-------|------|-------|
| Username | text input | نام کاربری |
| Password | password input | رمز عبور |
| Submit | button | ورود |

### States
- **Default:** Empty form
- **Error:** Inline error message below form — "نام کاربری یا رمز عبور اشتباه است." (red/danger tone)
- No "remember me" or "forgot password" — single admin, not needed

---

## 5. Content List Pages

Three list pages share the same pattern: Books, Posts, Tools.

### 5.1 Books List (`/admin/books/`)

**Topbar CTA:** `+ کتاب جدید`

**Filter bar (below topbar):**
- Search input (text) — filters by title or author on the server side
- No other filters currently

**Table columns:**
| Column | Notes |
|--------|-------|
| Cover (thumbnail) | Small image, ~40×56px |
| Title | Book title (bold) + subtitle (muted, smaller) below |
| Authors | Comma-separated |
| Category | First category name |
| Status | Badge: **منتشر شده** (green) / **پیش‌نویس** (gray) |
| Show in Library | ✓ / — |
| بازدید [NEW v6] | All-time view count from PageView log |
| Actions | Edit button + Delete button |

**Empty state:** "هنوز کتابی ثبت نشده. اولین کتاب را اضافه کنید." + CTA button

**Delete behavior:** POST to `/admin/books/{slug}/delete/` — no JS confirm dialog currently (design can add a confirmation UI if desired)

---

### 5.2 Posts List (`/admin/posts/`)

**Topbar CTA:** `+ یادداشت جدید`

**Table columns:**
| Column | Notes |
|--------|-------|
| Cover (thumbnail) | Small, optional |
| Title | Post title |
| Status | Badge: **منتشر شده** / **پیش‌نویس** |
| Featured | ✓ / — |
| Published Date | Jalali date format |
| Read time | e.g. "۵ دقیقه" |
| بازدید (قدیمی) [UPDATED v6] | `Post.view_count` — naive counter, kept for reference, labeled "قدیمی" |
| بازدید (جدید) [NEW v6] | Deduped view count from PageView log |
| Actions | Edit + Delete |

---

### 5.3 Tools List (`/admin/tools/`)

**Topbar CTA:** `+ ابزار جدید`

**Table columns:**
| Column | Notes |
|--------|-------|
| Cover (thumbnail) | |
| Title | Tool title |
| Category | |
| Status | Badge |
| دانلود | Download count |
| بازدید [NEW v6] | All-time view count from PageView log |
| Actions | Edit + Delete |

---

### 5.4 Categories List (`/admin/categories/`)

**Topbar CTA:** `+ دسته‌بندی جدید`

Simpler than the others — categories are just a name.

**Table columns:**
| Column | Notes |
|--------|-------|
| Name | Category name |
| Book count | Number of books in this category |
| Actions | Edit + Delete (delete disabled if books are assigned) |

**Delete guard:** If category has books, delete is blocked (currently: silent redirect — design can show a disabled state or tooltip "این دسته‌بندی دارای کتاب است")

---

## 6. Comment Moderation Pages

Two moderation pages: Book Comments, Post Comments. They share the same pattern.

### 6.1 Status tabs
- **pending** (پیش فرض / default)
- **approved**
- **rejected**

Displayed as tab bar or filter chips at the top of the content area. Current status URL param: `?status=pending`

### 6.2 Comment row
Each comment is a card or table row containing:

| Field | Notes |
|-------|-------|
| Book/Post title | Link to admin edit page |
| Commenter name | Display name they entered |
| Comment text | Full text |
| Rating | Star rating (1–5), if present |
| Submitted at | Jalali date/time |
| Actions | **تأیید** (approve) / **رد** (reject) / **حذف** (delete) |

**Action availability by tab:**
- **Pending:** Show Approve + Reject + Delete
- **Approved:** Show Reject + Delete
- **Rejected:** Show Approve + Delete

All actions are POST forms (no AJAX currently).

**Empty state per tab:** "نظری در این وضعیت وجود ندارد."

---

## 7. Form Pages — Shared Patterns

All create/edit forms share these conventions:

### 7.1 Layout
- **Max content width:** ~720px centered in the content area (not full-width — wide forms are hard to read)
- **Sections:** Fields grouped into logical sections with a section heading (not collapsible)
- **Save button:** Fixed/sticky at top (topbar) or bottom of form — "ذخیره" primary button
- **Success banner:** After save, a green success banner appears at top — "با موفقیت ذخیره شد." (auto-dismisses or persists until next action)
- **Error banner:** Red banner at top — shows the validation error message
- **Delete:** Separate danger button, away from the save button (e.g., bottom of form or in topbar secondary position)

### 7.2 Field types in use
| Type | Used for |
|------|----------|
| Text input | Title, slug, subtitle, year, author name, URL |
| Textarea | Note, bio, body (plain text currently — no rich text editor) |
| File upload | Cover image, download file |
| URL input (text) | Existing cover/download URL (alternative to file upload) |
| Select / dropdown | Status (Draft/Published), Category |
| Toggle / checkbox | Show in library, Is featured |
| Dynamic list | Authors (add/remove strings), Quotes (add/remove strings), Media links (type+url+title triples), Referred books (multi-select), Related books/posts (multi-select), Tool files (file+label+description triples) |
| Dynamic structured list [v5] | Jobs (years+role+company+desc rows), Bootcamps (kind+name+status+desc+url rows) |
| Date input | Published date (YYYY-MM-DD or Jalali picker) |

### 7.3 Slug field behavior
- Auto-populated from title when creating
- Editable by admin
- Show current public URL preview below the field: `petfeature.ir/library/{slug}/`
- Warn if slug is changed on an existing item (SEO impact)

---

## 8. Book Form (`/admin/books/new/` and `/admin/books/{slug}/edit/`)

The most complex form in the admin. Organized into sections:

### Section 1: اطلاعات اصلی (Main Info)
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| عنوان (Title) | text | ✓ | |
| زیرعنوان (Subtitle) | text | — | |
| نویسنده‌ها (Authors) | dynamic string list | ✓ | Add/remove author names |
| سال انتشار (Published Year) | text | — | Integer or empty |
| دسته‌بندی (Categories) | multi-select | — | From category list |
| نامک (Slug) | text | ✓ | Auto-generated from title |

### Section 2: تصویر و فایل (Cover & Download)
| Field | Type | Notes |
|-------|------|-------|
| تصویر کاور | file upload OR URL text | Upload replaces URL field |
| فایل دانلود | file upload OR URL text | Optional book PDF/resource |
| لینک خرید — عنوان | text | e.g. "خرید از کتاب‌یار" |
| لینک خرید — URL | URL text | |

### Section 3: محتوا (Content)
| Field | Type | Notes |
|-------|------|-------|
| یادداشت (Note) | textarea (large) | Admin's personal review/notes about the book |
| نقل‌قول‌ها (Quotes) | dynamic string list | Add/remove quote strings |

### Section 4: رسانه (Media Links)
Dynamic list of media link entries, each with:
- Type (select: podcast/video/article/other)
- Title (text)
- URL (text)

### Section 5: کتاب‌های مرتبط (Related Books)
- Multi-select from all other books in the library
- Shows book title in the picker

### Section 6: تنظیمات (Settings)
| Field | Type | Notes |
|-------|------|-------|
| وضعیت (Status) | select | Draft / Published |
| نمایش در کتابخانه | toggle | Whether to show in public library listing |

---

## 9. Post Form (`/admin/posts/new/` and `/admin/posts/{slug}/edit/`)

### Section 1: اطلاعات اصلی
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| عنوان (Title) | text | ✓ | |
| نامک (Slug) | text | ✓ | |
| خلاصه (Excerpt) | textarea (short) | — | Shown in post list cards |

### Section 2: تصویر
| Field | Type | Notes |
|-------|------|-------|
| تصویر کاور | file upload OR URL text | Required to publish |

### Section 3: محتوا
| Field | Type | Notes |
|-------|------|-------|
| متن (Body) | large textarea | Plain text stored, rendered with line breaks |

### Section 4: تنظیمات
| Field | Type | Notes |
|-------|------|-------|
| وضعیت | select | Draft / Published |
| ویژه (Featured) | toggle | Appears in featured slot on homepage/blog |
| تاریخ انتشار | date input | Jalali or Gregorian, auto-set on first publish |

---

## 10. Tool Form (`/admin/tools/new/` and `/admin/tools/{slug}/edit/`)

### Section 1: اطلاعات اصلی
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| عنوان (Title) | text | ✓ | |
| نامک (Slug) | text | ✓ | |
| دسته‌بندی (Category) | single select | ✓ | One category per tool |
| توضیح کوتاه | textarea (short) | ✓ | Card description |

### Section 2: تصویر
| Field | Type | Notes |
|-------|------|-------|
| تصویر کاور | file upload OR URL text | Required to publish |

### Section 3: محتوا
| Field | Type | Notes |
|-------|------|-------|
| توضیحات کامل (Body) | large textarea | Full usage guide |

### Section 4: فایل‌ها (Tool Files)
Dynamic list of downloadable file entries, each with:
- File upload (UploadFile)
- Label (text) — e.g. "فرمت Excel"
- Description (text) — brief note

### Section 5: محتوای مرتبط (Related Content)
- Related Books: multi-select from book list
- Related Posts: multi-select from post list

### Section 6: تنظیمات
| Field | Type |
|-------|------|
| وضعیت | select: Draft / Published |

---

## 11. About Form (`/admin/about/`) — Updated for v5

Single-page editor — no list, no create/delete, always editing the one About record.

**v5 adds two new sections** (Work Experience + Bootcamps) to the existing form. The existing sections remain.

### Section 1: اطلاعات نویسنده
| Field | Type | Notes |
|-------|------|-------|
| نام (Author Name) | text | Shown in hero heading on public About page |
| تصویر (Author Photo) | URL text | Portrait image, 3:4 ratio. No live preview currently, but the redesign should add one |
| بیوگرافی کوتاه | textarea | 2-paragraph bio shown in About hero |

### Section 2: درباره پت فیچر
| Field | Type | Notes |
|-------|------|-------|
| متن (Pet Feature Body) | large textarea | Stored in DB; currently not shown in new v5 template but kept for compatibility |

### Section 3: داستان سایت
| Field | Type | Notes |
|-------|------|-------|
| متن (Site Story Body) | large textarea | Stored in DB; currently not shown in new v5 template but kept for compatibility |

### Section 4: لینک‌ها
Dynamic list of link entries, each with:
- Title (text)
- URL (text)

The LinkedIn URL from this list is used in the About hero CTA.

### Section 5: سوابق شغلی (Work Experience) [NEW — v5]

Dynamic list of job entries. Each row contains:

| Sub-field | Type | Notes |
|-----------|------|-------|
| بازه زمانی (Years) | text | e.g. "۱۴۰۲ — اکنون" |
| نقش (Role) | text | e.g. "مدیر محصول ارشد" |
| شرکت (Company) | text | e.g. "دیجی‌کالا" |
| توضیح (Desc) | text (short) | One-line description |

UI pattern: ordered list of rows, each as a contained card. `+ افزودن سابقه` button adds a new empty row. × button removes. Order is the display order on the public page.

Stored as JSON in `AboutPage.jobs` column.

### Section 6: بوت‌کمپ‌ها (Bootcamps) [NEW — v5]

Dynamic list of bootcamp/course entries. Each row contains:

| Sub-field | Type | Notes |
|-----------|------|-------|
| نوع (Kind) | text | e.g. "بوت‌کمپ" or "دوره آنلاین" |
| نام دوره (Name) | text | Course name |
| وضعیت (Status) | text | e.g. "در حال ثبت‌نام" / "تکمیل ظرفیت" |
| توضیح (Desc) | text (short) | Card description |
| لینک (URL) | URL text | External link for "اطلاعات دوره" button |

UI pattern: same ordered-row card pattern as Work Experience. `+ افزودن دوره` button. × to remove.

Stored as JSON in `AboutPage.camps` column.

---

## 12. Contact Messages — `/admin/contact/` [NEW — v5]

**Purpose:** Read-only inbox for messages submitted through the public `/contact/` form. No reply functionality in the CMS — admin reads and replies externally via email.

**Nav label:** پیام‌ها (under ⚙️ عمومی group)
**Nav badge:** Unread message count (same visual style as pending-comment badges)

### 12.1 Page layout

- **No Topbar CTA** — this is a read-only list
- **No status tabs** — all messages shown together; filter by read/unread is a nice-to-have, not required
- Messages ordered newest-first

### 12.2 Message row / card

Each message shown as a table row or card:

| Field | Notes |
|-------|-------|
| تاریخ | Jalali date + time |
| نام | Sender name (optional — may be empty) |
| ایمیل | Sender email; shown LTR (not RTL) |
| موضوع | Subject (optional — may be empty) |
| پیام | Truncated preview (~80 chars) |
| وضعیت | Badge: **خوانده نشده** (yellow/warning) / **خوانده شده** (gray muted) |
| Actions | **علامت خوانده‌شدن** (toggle read) + **حذف** |

### 12.3 Message detail

Currently no separate detail page — full message text can be shown inline in the row (expandable accordion or always-visible). Design may choose between:
- **Option A:** Always show full text inline (simple, no JS needed)
- **Option B:** Click row to expand full text (JS accordion, better for long messages)

Either is acceptable. Recommend Option A for simplicity given server-rendered stack.

### 12.4 Actions

| Action | Route | Notes |
|--------|-------|-------|
| Mark as read/unread | `POST /admin/contact/{id}/read` | Toggles `is_read` flag |
| Delete | `POST /admin/contact/{id}/delete` | Hard delete, no recovery |

Both are standard POST forms (no AJAX). After action, redirects back to `/admin/contact/`.

### 12.5 Empty state

"هنوز پیامی دریافت نشده است."

---

## 13. Analytics Dashboard — `/admin/analytics/` [NEW — v6]

**Purpose:** Private traffic dashboard. Shows site-wide page view data with period filters, top-content tables, daily breakdown, and referrer breakdown. Admin-only — never public.

**Nav label:** آنالیتیکس (under 📊 آمار group — new nav group)

### 13.1 Page Layout

Single scrollable page, four stacked sections:

```
[ Period filter tabs ]

[ Summary cards row ]

[ Top Content — three tables side by side or tabbed ]

[ Traffic over time — daily table ]

[ Top Referrers — table ]
```

No charts in v6 — tables only. Chart enhancement is post-v6.

### 13.2 Period Filter Tabs

Tab bar at the top of the content area. Implemented as query param `?period=X`. Default: `7d`.

| Tab label | Value | Range |
|-----------|-------|-------|
| امروز | `today` | Current Jalali day |
| ۷ روز اخیر | `7d` | Last 7 days |
| ۳۰ روز اخیر | `30d` | Last 30 days |
| همه‌وقت | `all` | No date filter |

Active tab is visually highlighted. All four dashboard sections update to reflect the selected period.

### 13.3 Summary Cards

Three metric cards in a horizontal row:

| Card title | Metric | Notes |
|------------|--------|-------|
| کل بازدید | Total page view rows in period | Large number display |
| بازدیدکننده‌های یکتا | Distinct visitor tokens in period | Large number display |
| پربازدیدترین روز | Date with highest view count in period | Shown as Jalali date + count |

Design note: these are read-only stat cards — no interactivity. Large number, smaller label below.

### 13.4 Top Content Tables

Three tables, one per content type. Can be displayed:
- **Side by side** (3-column grid) — good if content is short
- **Tabbed** (Books / Posts / Tools tabs) — better if each table has 10 rows

Each table shows top 10 items for the selected period.

**Top Books:**
| Column | Notes |
|--------|-------|
| # | Rank (۱–۱۰) |
| عنوان | Book title |
| بازدید | Total views (PageView count) |
| بازدید یکتا | Distinct visitor count |

**Top Posts:**
| Column | Notes |
|--------|-------|
| # | Rank |
| عنوان | Post title |
| بازدید | Total views from PageView |
| بازدید یکتا | Distinct visitor count |
| شمارنده‌ی قدیمی | `Post.view_count` value — labeled "قدیمی", muted style |

**Top Tools:**
| Column | Notes |
|--------|-------|
| # | Rank |
| عنوان | Tool title |
| بازدید | Total views |
| بازدید یکتا | Distinct visitor count |

Empty state per table: "داده‌ای برای این بازه وجود ندارد."

### 13.5 Traffic Over Time Table

Daily breakdown table. For `all` period: limited to last 90 days. Newest first.

| Column | Notes |
|--------|-------|
| تاریخ | Jalali date (using existing `jalali.py` utility) |
| کل بازدید | Total PageView rows for that day |
| بازدیدکننده‌ی یکتا | Distinct visitor tokens for that day |

Design note: this is a dense data table — use a compact row height. Alternating row background or subtle border helps readability.

### 13.6 Top Referrers Table

Top 10 referrer domains for the selected period.

| Column | Notes |
|--------|-------|
| منبع | `referrer_domain`; null shown as **مستقیم** (direct) — muted badge |
| بازدید | View count from that domain |

---

## 14. Design Constraints & Requirements

### 14.1 RTL & Persian
- **All layout is RTL.** `<html dir="rtl" lang="fa">`
- Font: Vazirmatn (already loaded via Google Fonts)
- Numbers: Persian numerals (`۱، ۲، ۳`) preferred in displayed content; form inputs accept Latin digits
- Dates: Jalali calendar (Shamsi) for display; stored as Gregorian
- Text direction in textareas: RTL (Persian prose)
- **Exception:** Email addresses and URLs are always LTR (`direction: ltr; text-align: right` — aligned to right edge but read LTR)

### 14.2 No rich text editor
Currently all body/note fields are plain text stored as-is. The admin is the sole user — no need for a WYSIWYG. A monospace textarea with comfortable line height is sufficient. (Markdown rendering is not currently implemented server-side, so don't assume it.)

### 14.3 File uploads
- Cover images: JPG/PNG, stored in `/static/uploads/covers/` or `/static/uploads/post-covers/` or `/static/uploads/tool-covers/`
- Download files: stored in `/static/uploads/downloads/`
- Tool files: stored in `/static/uploads/tool-files/`
- Each upload input has an "OR paste URL" fallback — both should be clearly presented as alternatives

### 14.4 Form submission
All forms are standard HTML `<form method="POST" enctype="multipart/form-data">`. No AJAX. After successful save, the page reloads with `?saved=1` and shows a success banner. Error states reload the form with the error message and preserve entered values.

### 14.5 Dynamic list fields
Fields like Authors, Quotes, Media Links, Tool Files, Related Books/Posts, Jobs (v5), and Bootcamps (v5) are JavaScript-driven — add/remove rows without page reload. The JS serializes them to JSON hidden fields before form submit.

### 14.6 No mobile requirement
Admin is desktop-only. Minimum supported width: 1024px. No responsive breakpoints required for the redesign.

### 14.7 Performance
Static assets served via FastAPI's StaticFiles. Admin CSS/JS are separate from the public-facing `main.css`. Keep admin stylesheet self-contained.

### 14.8 Security / noindex
Admin pages must include `<meta name="robots" content="noindex, nofollow">`. No SEO concerns.

---

## 15. Status & Badge Vocabulary

| Status | Persian label | Color intent |
|--------|--------------|--------------|
| published | منتشر شده | Green |
| draft | پیش‌نویس | Gray / neutral |
| pending (comment) | در انتظار بررسی | Yellow / warning |
| approved (comment) | تأیید شده | Green |
| rejected (comment) | رد شده | Red / danger |
| unread (contact) [v5] | خوانده نشده | Yellow / warning |
| read (contact) [v5] | خوانده شده | Gray / muted |
| direct referrer (analytics) [v6] | مستقیم | Muted/neutral badge |

---

## 16. Action Vocabulary

| Action | Persian label | Style |
|--------|--------------|-------|
| Save | ذخیره | Primary button |
| Create new | + [entity name] | Primary button (topbar CTA) |
| Edit | ویرایش | Secondary/outline button |
| Delete | حذف | Danger button |
| Approve comment | تأیید | Success/green button |
| Reject comment | رد | Danger/red button |
| Mark as read [v5] | علامت خوانده‌شدن | Secondary button |
| Mark as unread [v5] | علامت نخوانده | Secondary button |
| View site | مشاهده‌ی سایت | Tertiary link (sidebar footer) |
| Logout | خروج | Tertiary link (sidebar footer) |
| Add row (dynamic list) | + افزودن | Small secondary button |
| Remove row | × | Icon button, inline with row |

---

## 17. Current Pain Points (for redesign to address)

1. **Forms are very long without visual grouping.** Section breaks with headings + optional visual cards per section would help the admin scan and navigate. This is especially important now that About form has 6 sections (v5).

2. **Save button is below the fold on long forms.** Sticky save button in topbar or floating at bottom of form would eliminate unnecessary scrolling.

3. **Dynamic list fields (Authors, Quotes, Media Links, Tool Files, Jobs, Bootcamps) have minimal UI.** The add/remove interaction is functional but bare. Clearer row containers with drag-to-reorder (nice-to-have) would improve the editing experience.

4. **Success/error feedback is banner-only.** Currently a top banner that stays until next navigation. An auto-dismiss toast or inline field-level errors would feel more polished.

5. **No dashboard home.** `/admin/` redirects to `/admin/books/`. Now that there are analytics (v6), a minimal home dashboard with content counts + unread counts + a mini traffic summary would make the home redirect worth keeping as a real page.

6. **Comment moderation UX is list-heavy.** Each comment action requires a full POST + page reload. The current list is readable, but the moderation flow could benefit from inline approve/reject with optimistic UI (enhancement, not required for redesign).

7. **Cover image preview is absent.** When a URL is entered in the cover field, there's no preview. A live image preview next to the upload/URL field would reduce errors.

8. **Analytics tables need strong visual hierarchy.** The v6 dashboard has many data tables on one page. Clear section headings, visual separation, and a visually distinct period-filter tab bar are important to prevent the page from feeling like a data dump.

9. **Contact inbox unread state must be scannable at a glance.** Unread messages should visually stand out from read ones — bold row text, colored dot, or background difference.

---

## 18. Pages Summary Table

| Page | Route | Has Form | Has List | Version | Primary Action |
|------|-------|----------|----------|---------|----------------|
| Login | `/admin/login/` | ✓ | — | — | ورود |
| Books | `/admin/books/` | — | ✓ | — | + کتاب جدید |
| Book Form | `/admin/books/new/` | ✓ | — | — | ذخیره |
| Book Form | `/admin/books/{slug}/edit/` | ✓ | — | — | ذخیره |
| Categories | `/admin/categories/` | — | ✓ | — | + دسته‌بندی جدید |
| Category Form | `/admin/categories/new/` | ✓ | — | — | ذخیره |
| Category Form | `/admin/categories/{id}/edit/` | ✓ | — | — | ذخیره |
| Book Comments | `/admin/books/comments/` | — | ✓ | — | تأیید / رد |
| Posts | `/admin/posts/` | — | ✓ | — | + یادداشت جدید |
| Post Form | `/admin/posts/new/` | ✓ | — | — | ذخیره |
| Post Form | `/admin/posts/{slug}/edit/` | ✓ | — | — | ذخیره |
| Post Comments | `/admin/posts/comments/` | — | ✓ | — | تأیید / رد |
| Tools | `/admin/tools/` | — | ✓ | — | + ابزار جدید |
| Tool Form | `/admin/tools/new/` | ✓ | — | — | ذخیره |
| Tool Form | `/admin/tools/{slug}/edit/` | ✓ | — | — | ذخیره |
| About | `/admin/about/` | ✓ | — | — → v5 | ذخیره |
| Contact Inbox | `/admin/contact/` | — | ✓ | **v5 NEW** | علامت خوانده‌شدن / حذف |
| Analytics | `/admin/analytics/` | — | ✓ | **v6 NEW** | — (read-only) |

---

## 19. Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | July 2026 | Initial spec — covers v1–v4 admin (Library, Blog, Tools, Book Engagement) |
| 1.1 | July 2026 | Added v5 additions: Contact Inbox (§12), About Form extensions (§11 sections 5–6), nav badge for unread messages; Added v6 additions: Analytics Dashboard (§13), view count columns on Books/Posts/Tools list pages (§5), analytics nav group, updated pain points (§17) |

---

*Spec version: 1.1 · July 2026 · Audience: Visual redesign (Claude Design handoff)*
