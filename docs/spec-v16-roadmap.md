# Product Spec v16 — پت فیچر (Roadmap / مسیر یادگیری)

> **Parent:** [Product overview](./spec.md) · **Content source:** [pm-learning-roadmap.md](./New%20idea/pm-learning-roadmap.md) · **Design reference:** `petfeature fable redesign/project/v16/`

## 1. Summary

| Field | Value |
|-------|-------|
| **Version** | v16 — Roadmap (مسیر یادگیری) |
| **Status** | Shipped |
| **Goal** | Ship the fourth founding epic — a public, browsable PM career curriculum for Persian-speaking PMs, with an admin CMS to manage resource links and metadata |
| **Builds on** | v1 (Library — books are linkable from resources), v9 (Media Library) |
| **Epic** | Roadmap |

**Scope in two sentences:** Publish the complete PM Learning Roadmap as a set of server-rendered pages — landing page with depth matrix and fork, L0 Getting Hired track, and L1 APM detail page — using the current site theme and design system. L2–L6 levels show as "در دسترس نیست" / disabled on the landing until a future version ships them; an admin CMS lets Milad manage the resource rows (links, metadata) and immigration video links for all levels without touching code.

**Shipped July 2026.** All routes, templates, model, migrations, seed script, and admin CMS live in production.

**v16 ships:** L0 (مسیر استخدام) + L1 (APM) as full pages, L2–L6 as disabled cards on the landing.

---

## 2. Problem & Goals

**Problem:** The Roadmap epic has been in the product vision since day one and is the fourth tab in the nav, but no content exists behind it. Persian-speaking PMs have nowhere to go on petfeature.ir to answer "what do I study at my current career stage?" — the library has the books but no opinionated sequence.

**v16 goals:**

- **Orient:** Let any visitor understand where they are on the PM career ladder within seconds of landing on `/path/`
- **Fork:** Route the two distinct audiences — "I want a PM job" vs "I have a PM job" — to the right track immediately
- **Teach the model:** Explain the three numbers (مطالعه / اسپرینت / بلوغ), the depth scale (1–5), and the four categories (ورود / هسته / حمایتی / پل) so users can self-serve without confusion
- **Show the matrix:** Render the 15-competency × 6-level depth matrix so PMs can self-assess their gaps
- **L0 complete:** Full Getting Hired track — 4 phases, 8 areas, overlapping Gantt, 2 checklists, exclusions table
- **L1 complete:** Full APM level page — hero stats, competency table, all phase sections (Entry, Core, Supporting, Passive, Sequence, Bridge)
- **Admin CMS:** Milad can add/edit/delete resource rows (title, type, time, difficulty, Persian flag, required/optional, external URL, library book link, homework text) without touching code

---

## 3. User Stories

**Visitors:**
- *As a visitor, I want to land on /path/ and immediately understand whether I need Roadmap 0 or the level ladder, so I go to the right place*
- *As a visitor, I want to see the depth matrix so I can assess which competencies I'm behind on at my target level*
- *As a visitor, I want to read the "three numbers" explanation so I never confuse sprint weeks with total level duration*
- *As a visitor on /path/hiring/, I want to see the four overlapping phases as a visual timeline so I understand that applying starts while I'm still practising*
- *As a visitor on /path/hiring/, I want to read each of the 8 areas with its resources and homework so I have a concrete action for each*
- *As a visitor on /path/apm/, I want to read each Core competency card so I know what to study, in what order, and what homework to do*
- *As a visitor, I want to click a resource title and land on the library book or an external page, so I can act on the recommendation immediately*
- *As a visitor, I want unlinked resources to look intentional (not broken), so I trust the content even when a Persian review isn't ready yet*
- *As a visitor who clicks L2–L6 on the landing, I want a clear "coming soon" signal so I understand it's planned, not broken*

**Admin (Milad):**
- *As Milad, I want to add an external URL to a resource so that resource title becomes a link on the public page*
- *As Milad, I want to link a resource to a library book so clicking the title takes the user to the book detail page*
- *As Milad, I want to edit a resource's homework text so I can refine the Persian copy without a deployment*
- *As Milad, I want to delete a resource row so I can remove content that no longer fits*
- *As Milad, I want to see all resources grouped by level and category so I can quickly find what to edit*

---

## 4. Content Model

### 4.1 What is hardcoded (never in DB)

The following is authored once in Python constants (or a JSON seed file) and embedded in templates. It changes only via a code deploy:

| Data | Details |
|------|---------|
| **Levels** (L0–L6) | slug, Farsi name, English name, spec sentence, required count, reading hours, sprint weeks, tenure string |
| **Competencies** (15) | slug, Farsi name, domain group (4 domains), habit vs knowledge flag |
| **Depth matrix** | 15 × 6 grid of integers (0–5); 0 means "–" (not required) |
| **Category assignments** | For each (competency, level) pair: Entry / Core / Supporting / Passive / Step-back |
| **Sprint & maturation numbers** | Per (competency, level): sprint weeks, maturation months, reading hours |
| **Level metadata** | thesis sentence, section notes (entryNote, coreNote, etc.), quotes, practice exercises |
| **L0 phase metadata** | Phase names (آماده‌سازی / تمرین / اقدام / پذیرش), sprint windows for the Gantt chart |
| **L0 area metadata** | Area name, phase FK, sprint weeks, maturation, habit flag, body text, homework, Persian market note |
| **Checklists** | "آماده‌ی اقدام" items, "آماده‌ی سطح ۱" item (hardcoded — these never change) |
| **Exclusions table** | "این مسیر عمداً چه چیزی را ندارد" rows |

### 4.2 What lives in the database (`RoadmapResource` model)

One table for all resource rows across all levels and areas. Each row:

| Column | Type | Notes |
|--------|------|-------|
| `id` | int PK | |
| `level_slug` | varchar | `hiring`, `apm`, `pm`, `senior-pm`, `lead`, `director`, `cpo` |
| `competency_slug` | varchar | e.g. `product-discovery`; `null` for L0 area resources |
| `area_slug` | varchar | e.g. `role-clarity`; `null` for level resources |
| `category` | varchar | `entry`, `core`, `supporting`, `bridge`; `null` for L0 |
| `title` | varchar(300) | English title (renders `dir="ltr"`) |
| `subtitle` | varchar(300) | nullable; free-text shown in parens after resource type, e.g. "رایگان" |
| `resource_type` | varchar | `book`, `article`, `podcast`, `course`, `tool`, `guide`, `video`, `practice-tool` |
| `reading_time` | varchar(30) | Display string, e.g. `"3h"`, `"20m"`, `"ongoing"` |
| `difficulty` | smallint | 1, 2, or 3 (stars) |
| `has_persian` | boolean | True if Persian translation exists |
| `is_required` | boolean | True = اجباری, False = اختیاری |
| `external_url` | varchar(500) | nullable; external link |
| `book_id` | FK → Book | nullable; links to library book detail (`ondelete="SET NULL"`) |
| `sort_order` | int | Display order within its group |
| `created_at` | datetime | |
| `updated_at` | datetime | |

**Link resolution rule (public pages):** If `book_id` is set, the title links to `/library/{book.slug}/`. If only `external_url` is set, the title links to that URL in a new tab. If neither is set, the title renders as plain text with the "هنوز لینکی ندارد — یادداشت فارسی در راه است" badge.

**Constraint:** A resource cannot have both `book_id` and `external_url` set — admin form enforces mutual exclusivity.

---

## 5. Public Pages

### 5.1 Landing — `/path/`

**Template:** `app/templates/pages/roadmap.html`  
**Route:** `GET /path/`  
**Page title (Persian):** `مسیر یادگیری | پت فیچر`

Sections, in order:

#### Hero
- Headline: **"بدانید کجای مسیرید، و بعدش چه بخوانید."**
- Subline: description of the 15-competency, 6-level structure
- Three stats: منابع اجباری (96) · مطالعه (~452h) · زمان واقعی (10–17 سال)

#### The Fork
- Section heading: "اول یک سؤال، بعد بقیه‌ی صفحه"
- Two side-by-side cards:
  - **L0 card** (green accent): مسیر استخدام · "بیرون از نردبان" badge · description · stats (13 منبع · ~35h · 18 هفته) · CTA: "مسیر استخدام را ببینم ←" → `/path/hiring/`
  - **Ladder card** (amber accent): "سطح ۱ تا ۶ · نردبان" · description · stats (96 منبع · ~452h · 276 هفته) · CTA: "سطح خودم را پیدا کنم ←" → anchors to the matrix below
- Mobile: stack vertically

#### Three Numbers
- Heading: "سه عدد که هرگز جمع نمی‌شوند"
- Three explanation cards: مطالعه (ساعت) · اسپرینت (هفته) · بلوغ (ماه)
- Each card: coloured left border, icon-equivalent (coloured square/circle), name, unit, one-sentence explanation
- Example paragraph below

#### Four Categories
- Heading: "چهار دسته، به ترتیب قوسِ نگه‌داشتن شغل"
- Ordered list: ورود · هسته · حمایتی · پل — each with question it answers and timing
- Three passive-state chips below: رایگان به دست می‌آید · تثبیت · عقب بکشید

#### The Depth Matrix
- Heading: "ماتریس عمق شایستگی"
- Depth legend: 6 chips (۱ آگاه → ۵ تعریف می‌کند, plus —)
- Scrollable table (overflow-x inside container; page never scrolls horizontally)
  - Sticky RTL first column: competency name
  - 6 level header columns; L1 header links to `/path/apm/`; L2–L6 headers are plain text (no link, no `aria-disabled`) — the column label alone signals it's just a level name
  - Domain group header rows (پیشه‌ی محصول / تحلیل و کسب‌وکار / استراتژی / رهبری و نفوذ)
  - Cells: depth number chip (coloured by depth 1–5; "—" for 0)
  - SVG spark-line inside each cell connecting to the next level's depth (accent line = rise, fall colour = intentional decline, dashed = not-required segment)
- Legend: صعود / افت عمدی / ثابت / هنوز لازم نیست

#### Level Summary Cards
- Heading: "یک مسیر جدا، بعد شش سطح"
- Subline explaining the sprint vs maturation bar
- L0 card first (dashed green border, "کمپین است، نه سطح" flag), then L1–L6
- Each card: level number · Farsi name · English name · spec sentence · stats chips (مطالعه / اسپرینت / تصدی / منابع اجباری) · sprint-vs-maturation progress bar
- **L1 card:** links to `/path/apm/`; **L0 card:** links to `/path/hiring/`
- **L2–L6 cards:** rendered with "به زودی" badge, no link, `opacity: 0.6`, `cursor: default`

---

### 5.2 Getting Hired — `/path/hiring/`

**Template:** `app/templates/pages/roadmap-hiring.html`  
**Route:** `GET /path/hiring/`  
**Page title:** `مسیر استخدام | مسیر یادگیری | پت فیچر`  
**Accent colour on this page:** green (`--sprout` or equivalent CSS var) instead of amber — visually distinguishes L0 from the ladder

Sections, in order:

#### Breadcrumb
`مسیر یادگیری / مسیر ۰ — مسیر استخدام` + "سطح شغلی نیست · بیرون از نردبان" chip

#### Hero (two-column)
- Left: headline "مسیر استخدام" + campaign framing paragraph + "روزی که آفر کار را قبول کنید تمام می‌شود" callout
- Right: "شرط پایان" card — end condition sentence + link card to L1 (amber)
- 4-stat bar below: منابع اجباری (13) · مطالعه (~35h) · اسپرینت (18 هفته) · مدت کمپین (3–6 ماه)

#### Who It's For
- Three audience cards: career switchers · recent graduates · PMs changing companies

#### Overlapping Phases — The Gantt
- Heading: "چهار فاز که هم‌پوشانی دارند"
- Explanation paragraph (critical: phases overlap deliberately; applying starts mid-Practice)
- Scrollable Gantt chart — 24-week grid, 4 phase bars overlapping:
  - آماده‌سازی: weeks 1–6
  - تمرین: weeks 4–12
  - اقدام: weeks 10–24 (ongoing, hatched)
  - پذیرش: week 17–18
- Legend: sprint window (solid bar) vs ongoing/open-ended (hatched bar)
- **No-JS fallback:** render as an accessible `<table>` with week ranges as text

#### The Eight Areas
- Heading: "هشت حوزه‌ی کاری"
- Intro: one resource each, sprint weeks, homework; habit areas flagged
- Grouped by phase (آماده‌سازی / تمرین / اقدام / پذیرش), each group with phase header
- Each area: `<details>/<summary>` card (no JS required)
  - Collapsed: area number chip · name · habit badge (if applicable) · three numbers chips
  - Expanded: body text · resource rows (from DB) · homework block · Persian market note (if any)
- Resource rows: title (linked/unlinked) · type · reading time · difficulty (stars) · Persian flag · required/optional badge

#### Two Checklists
- Left card: "آماده‌ی اقدام هستید وقتی:" — 6 checkbox-styled list items (visual, not interactive)
- Right card: "آماده‌ی سطح ۱ هستید وقتی:" — single answer ("یک پیشنهاد کاری را قبول کرده‌اید") + link card to L1

#### Exclusions Table
- "این مسیر عمداً چه چیزی را ندارد" — 5 rows: what · why

#### Footer nav
- ← مسیر یادگیری | سطح ۱ — مبتدی (APM) →

---

### 5.3 Level Detail — `/path/apm/`

**Template:** `app/templates/pages/roadmap-level.html`  
**Route:** `GET /path/{level_slug}/`  
**v16:** Only `apm` resolves to a full page. All other slugs (pm, senior-pm, lead, director, cpo) return a stub response — see §5.4.  
**Page title:** `سطح ۱ — مبتدی (APM) | مسیر یادگیری | پت فیچر`

#### Level Strip (sub-nav)
Horizontal scrollable strip above hero: pill buttons for L0 and L1–L6. L0 links to `/path/hiring/`. L1 (current) is active. L2–L6: disabled pills with "به زودی" label, `aria-disabled="true"`.

#### Hero
- "سطح ۱" eyebrow + level name (مبتدی (APM)) + English name (`dir="ltr"`)
- Spec sentence (Farsi) · Thesis sentence
- 4-stat grid: مطالعه (15 منبع · ~53h) · اسپرینت (31 هفته · ~7 ماه) · بلوغ (longest maturation window) · تصدی (12–24 ماه)
- **Tenure bar:** visual progress bar showing sprint proportion vs maturation proportion of tenure; sprint block labelled "اسپرینت"; maturation block labelled "بلوغ — بدون مطالعه‌ی جدید"
- Explanatory paragraph below bar

#### What This Level Asks — Competency Table
- Scrollable table (overflow inside container)
- Columns: شایستگی · عمق · دسته · اسپرینت · بلوغ · مطالعه
- Rows: all competencies relevant to this level (Core, Supporting, Passive/Free)
- Depth cell: coloured chip + optional ⇈ jump badge
- Category cell: coloured chip (ورود / هسته / حمایتی / passive variants)

#### Sticky Phase Nav
Position sticky, scrolls with page. Links: #entry · #core · #supporting · #passive · #sequence · #bridge  
(Section `#stepback` added only for levels that have it — L4, L5; not L1)

#### Section: ورود (Entry) — `id="entry"`
- Section subline: "پیش از آن‌که عنوان را داشته باشید"
- Intro note + callout referencing مسیر ۰ (linked to `/path/hiring/`)
- Resource list (from DB, `category = 'entry'`, sorted by `sort_order`)
  - Each resource: title (linked/unlinked) · type label · required/optional badge · reading time · difficulty stars · Persian flag
  - Unlinked resources show "هنوز لینکی ندارد — یادداشت فارسی در راه است" badge
- Quote callout (hardcoded)
- Homework block (hardcoded per level, not per resource)

#### Section: هسته (Core) — `id="core"`
- Section subline: "کاری که روزانه شخصاً پاسخ‌گویش هستید"
- Intro note
- One `<details>` card per Core competency (APM has 4: Delivery & Execution, Product Discovery, Communication & Writing, Technical Literacy)
  - **Collapsed state:** order number chip · competency name · target depth chip · ⇈ jump badge (if applicable) · habit/knowledge tag · three-number chips (مطالعه / اسپرینت / بلوغ) · resource titles preview line
  - **Expanded state:** rationale body text · resource rows (from DB) with homework row per resource · "چرا این، نه آن؟" quote block (hardcoded) · practice exercise (hardcoded)
  - First card open by default; others collapsed

#### Section: حمایتی (Supporting) — `id="supporting"`
- Section subline: "سهم دارید، اما مالکش کسِ دیگری است"
- Intro note
- One card per Supporting competency (APM has 2: Stakeholder & Exec Influence, Prioritization & Tradeoffs)
  - Each card: name · three numbers · owner note (hardcoded) · single resource row (from DB, required) + homework · optional resource mention (text only)

#### Section: بدون مطالعه (Passive / Free) — `id="passive"`
- Section subline: "بدون منبع — و این تصمیم است، نه جای خالی"
- Intro note explaining "acquired free" and "maintain" states
- Dashed-border table: competency name · depth chip · how-it's-acquired explanation (hardcoded)
- Competencies: Data · Business · Experimentation · Strategy · Vision · Market (all depth 1, acquired free at L1)
- People Leadership · Coaching · Org Design (not applicable at L1)
- Quote callout

#### Section: توالی (Sequence) — `id="sequence"`
- Section subline: week range summary
- Intro paragraph
- Scrollable Gantt chart (same visual pattern as L0 phases):
  - 31-week grid (the sprint total for APM)
  - One bar per Core competency sprint, in sequence
  - Below each bar: week range + maturation windows running concurrently
- **No-JS fallback:** accessible `<table>` with week · sprint · maturing columns
- Body paragraph: "بیشتر یک سطح بلوغ است، نه مطالعه"

#### Section: پل (Bridge) — `id="bridge"`
- Section subline: "برای درخواستِ ارتقا چه نیاز دارید"
- Intro note
- Resource list (from DB, `category = 'bridge'`, sorted by `sort_order`)
- Promotion checklist: "آماده‌ی سطح ۲ هستید وقتی:" — bulleted list of conditions (hardcoded)
- Link card to L2 (disabled / "به زودی" in v16)

---

### 5.4 Stub Response for L2–L6

**Route:** `GET /path/{level_slug}/` where slug ∈ {pm, senior-pm, lead, director, cpo}

**Behaviour:** Returns a full page (not 404) with:
- Site header + nav (مسیر یادگیری active)
- Level name + "در دسترس نیست" notice
- Short note: "این بخش در دسترس نیست — به زودی منتشر می‌شود"
- Back link: "← برگشت به مسیر یادگیری"
- Site footer

**No redirect.** The URL resolves; the page just signals it isn't built yet.

---

## 6. Admin Pages

All admin pages use the existing admin shell (`app/templates/admin/base.html`), orange accent, `.admin-table`, `.card` classes.

### 6.1 Resource List — `/admin/roadmap/`

- Page title: "مسیر یادگیری — منابع"
- Filter row: dropdown filter by level (L0–L6)
- Table columns: عنوان (title) · نوع · سطح · دسته/حوزه · لینک · اجباری · ویرایش
- "لینک" column: shows "📚 کتابخانه", "🔗 خارجی", or "— ندارد"
- Row actions: ویرایش | حذف (with confirmation)
- "+ منبع جدید" button → `/admin/roadmap/new/`
- Count badge per level when filter is active

### 6.2 Resource Form — `/admin/roadmap/new/` and `/admin/roadmap/{id}/edit/`

Fields:

| Field | Input | Notes |
|-------|-------|-------|
| سطح | Select | L0 (مسیر استخدام) through L6 (CPO) |
| حوزه / شایستگی | Select | Filtered by selected level. L0 shows area slugs; L1–L6 show competency slugs |
| دسته | Select | entry / core / supporting / bridge (hidden for L0) |
| عنوان | Text | English title; renders LTR on public pages |
| نوع | Select | book / article / podcast / course / tool / guide |
| زمان مطالعه | Text | e.g. "3h", "20m", "ongoing" |
| سختی | Radio (1–3 stars) | |
| نسخه‌ی فارسی | Checkbox | دارد / ندارد |
| اجباری | Radio | اجباری / اختیاری |
| **لینک خارجی** | URL input | Optional; mutually exclusive with book link |
| **کتاب از کتابخانه** | Searchable select | FK to Book; optional; mutually exclusive with external URL |
| متن تکلیف | Textarea | Farsi homework text; optional |
| ترتیب نمایش | Number | Sort order within group |

**Mutual exclusivity:** If both external URL and book are filled, form shows inline error: "یا لینک خارجی یا کتاب از کتابخانه — نه هر دو." Submit blocked until resolved.

**Save actions:** "ذخیره" (save + return to list) | "ذخیره و جدید" (save + open blank form)

### 6.3 Missing Links Queue — `/admin/roadmap/missing-links/`

- Lists all RoadmapResource rows where `external_url IS NULL AND book_id IS NULL`
- Grouped by level
- Each row: title · level · competency/area · quick "افزودن لینک" inline action → opens edit form pre-filled
- Count badge in sidebar nav: shows number of unlinked resources (e.g. "منابع بدون لینک (39)")
- This helps Milad progressively fill in links as books get reviewed

---

## 7. Data Model

### New model: `RoadmapResource`

```python
# app/models/roadmap.py

class RoadmapResource(Base):
    __tablename__ = "roadmap_resources"

    id = Column(Integer, primary_key=True)
    level_slug = Column(String(20), nullable=False, index=True)
        # 'hiring' | 'apm' | 'pm' | 'senior-pm' | 'lead' | 'director' | 'cpo'
    competency_slug = Column(String(50), nullable=True)
        # e.g. 'product-discovery'; null for L0 area resources
    area_slug = Column(String(50), nullable=True)
        # e.g. 'role-clarity'; null for level resources
    category = Column(String(20), nullable=True)
        # 'entry' | 'core' | 'supporting' | 'bridge'; null for L0
    title = Column(String(300), nullable=False)
    resource_type = Column(String(20), nullable=False)
        # 'book' | 'article' | 'podcast' | 'course' | 'tool' | 'guide'
    reading_time = Column(String(30), nullable=True)  # e.g. "3h", "20m"
    difficulty = Column(SmallInteger, nullable=True)  # 1 | 2 | 3
    has_persian = Column(Boolean, default=False)
    is_required = Column(Boolean, default=True)
    external_url = Column(String(500), nullable=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=True)
    homework_text = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    book = relationship("Book", lazy="joined")
```

**Computed properties (on the ORM model):** `link_url`, `is_linked`, `link_type` (book/external/none), `reading_time_display`, `difficulty_stars`, `resource_type_fa`, `type_display` — all derived, not stored.

**Note:** `homework_text` was removed from the DB model during implementation. Homework text lives in the hardcoded `roadmap_data.py` constants per level/competency, not per resource row.

### New model: `ImmigrationVideo`

A second model added during implementation to support the hiring page's immigration section:

| Column | Type | Notes |
|--------|------|-------|
| `id` | int PK | |
| `title` | varchar(300) | Video title |
| `where` | varchar(200) | nullable; context label, e.g. "گفت‌وگو با یک مدیر محصول مهاجرت‌کرده" |
| `url` | varchar(500) | Video URL (YouTube etc.) |
| `sort_order` | int | Display order |
| `created_at` | datetime | |

**Migration:** `alembic revision --autogenerate -m "add roadmap_resources table"`

**Seeding:** A one-time seed script (`scripts/seed_roadmap.py`) populates all known resources from the markdown spec — with `external_url = None` and `book_id = None` for every row. Milad fills all links via the admin CMS after seeding. No pre-linking in the seed script. Script is idempotent (skip if title+level_slug+competency_slug already exists).

### Hardcoded content structure

All non-DB content lives in `app/services/roadmap_data.py` — a single Python module with typed dicts/dataclasses:

- `LEVELS: list[Level]` — 7 entries (L0–L6), all metadata
- `COMPETENCIES: list[Competency]` — 15 entries
- `DEPTH_MATRIX: dict[str, list[int]]` — keyed by competency_slug, 6-item list
- `LEVEL_COMPETENCY_DATA: dict[str, dict[str, CompetencyLevelData]]` — sprint, mat, reading, category per (level, competency)
- `L0_AREAS: list[Area]` — 8 areas with body text, homework, market note
- `L0_PHASES: list[Phase]` — 4 phases with Gantt windows
- Level-specific section texts (entryNote, coreNote, quotes, practices, thesis, etc.) nested under each level entry

This module is imported by the service layer and passed as context to templates. No DB queries touch it.

---

## 8. Service Layer

**New file:** `app/services/roadmap_service.py`

```python
async def get_landing_context(db) -> dict
    # Returns: LEVELS, COMPETENCIES, DEPTH_MATRIX, level summary cards with sprint bars

async def get_hiring_context(db) -> dict
    # Returns: L0 static data + resources from DB for all 8 areas + immigration videos

async def get_level_context(db, level_slug: str) -> dict | None
    # Returns None if slug not in ('apm',) for v16 (triggers stub render)
    # Returns full context: level metadata + all DB resources grouped by competency/category

async def get_roadmap_resources(db, level_slug: str | None = None) -> list[RoadmapResource]
    # Admin list, optionally filtered by level

async def get_resource(db, resource_id: int) -> RoadmapResource
async def create_resource(db, data: dict) -> RoadmapResource
async def update_resource(db, resource_id: int, data: dict) -> RoadmapResource
async def delete_resource(db, resource_id: int) -> None
async def get_missing_links(db) -> list[RoadmapResource]
async def count_missing_links(db) -> int          # used for admin sidebar badge

async def get_immigration_videos(db) -> list[ImmigrationVideo]
async def get_immigration_video(db, video_id: int) -> ImmigrationVideo
async def create_immigration_video(db, data: dict) -> ImmigrationVideo
async def update_immigration_video(db, video_id: int, data: dict) -> ImmigrationVideo
async def delete_immigration_video(db, video_id: int) -> None

# Internal helpers (not called by routes directly):
# _build_matrix_rows() -> list[dict]
# _build_asks_table(level_slug, comp_data) -> list[dict]
# _build_sequence_gantt(level_slug, comp_data) -> list[dict]
```

---

## 9. Routes

### Public routes (add to `app/web/routes.py`)

```python
GET  /path/                    → roadmap landing
GET  /path/hiring/             → L0 Getting Hired
GET  /path/{level_slug}/       → L1 full page (apm) | stub page (pm, senior-pm, lead, director, cpo)
```

### Admin routes (add to `app/admin/routes.py`)

```python
GET  /admin/roadmap/                         → resource list (with level filter)
GET  /admin/roadmap/missing-links/           → unlinked resources queue
GET  /admin/roadmap/new/                     → create resource form
POST /admin/roadmap/new/                     → create resource action
GET  /admin/roadmap/{id}/edit/               → edit resource form
POST /admin/roadmap/{id}/edit/               → update resource action
POST /admin/roadmap/{id}/delete/             → delete resource (POST for CSRF safety)

GET  /admin/immigration-videos/              → immigration video list
GET  /admin/immigration-videos/new/          → create video form
POST /admin/immigration-videos/new/          → create video action
GET  /admin/immigration-videos/{id}/edit/    → edit video form
POST /admin/immigration-videos/{id}/edit/    → update video action
POST /admin/immigration-videos/{id}/delete/  → delete video
```

---

## 10. NFRs

| Requirement | Detail |
|-------------|--------|
| **RTL** | All pages fully RTL. Resource titles (English) render `dir="ltr"` with `unicode-bidi:embed` |
| **Persian numerals** | All UI chrome uses ۰–۹. Latin numerals acceptable inside English resource titles |
| **No-JS core** | All content readable without JS. `<details>/<summary>` for competency cards — no JS required. Gantt charts degrade to accessible `<table>` |
| **No colour-only meaning** | Depth, required/optional, jump/decline always carry text or shape alongside colour |
| **Touch-friendly** | No hover-only affordances. Competency cards use native `<details>` — no hover tooltip for information |
| **Matrix overflow** | Depth matrix scrolls inside its own container — page body never scrolls horizontally |
| **Existing design system** | Uses current site theme (light), existing `main.css`, existing `base.html` header/footer. No new design tokens introduced |
| **Performance** | Landing page makes 1 DB query (resources count per level for summary cards). Level detail makes 1 DB query (all resources for that level). No N+1 |
| **Admin security** | All admin routes protected by existing admin session auth. CSRF-safe (POST for mutations) |
| **Accessibility** | Semantic `<table>` for matrix and sequencing. `scope="col"/"row"` on headers. `aria-disabled` on disabled level links. Visible focus on all interactive elements |

---

## 11. Out of Scope for v16

| Item | Reason |
|------|--------|
| L2–L6 full pages | Scheduled for v17+ when content is Persian-reviewed |
| Progress tracking / "mark as read" | Requires v12 User Auth + v15 Bookshelf |
| Personalized level detection / self-assessment quiz | Requires auth; future phase |
| Dark theme from the design files | Current site theme used; dark theme is a separate rebrand decision |
| Competency metadata editing in admin | Hardcoded; changes via code deploy only |
| Sprint/maturation number editing | Hardcoded |
| Persian translations of resource homework text | Milad authors these via the admin form; content is not blocked on the developer |
| Job board, CV upload, certificate | Explicitly not part of this product |
| Gamification (badges, streaks, leaderboards) | Explicitly rejected |

---

## 12. Open Questions

| Question | Owner | Notes |
|----------|-------|-------|
| When does v17 (L2 PM) get built? | Milad | Helps decide when to invest in L2+ content |

**Resolved (July 2026):**

| Question | Decision |
|----------|----------|
| Seed script pre-links | No pre-linking — seed creates all resource rows with links null; Milad fills all links via admin |
| Habit/knowledge badge wording | "عادتی" / "دانشی" confirmed |
| Depth matrix L2–L6 column headers | Unlinked — plain text, no href |
| Persian copy for L1 section texts | Milad authors all body text, quotes, and practice exercises in Persian directly in `roadmap_data.py` — no English placeholders |
| `homework_text` on resource rows | Moved to hardcoded constants in `roadmap_data.py` per level/competency — not stored per resource in DB |
| Immigration video content | Added `ImmigrationVideo` model + admin CRUD for hiring page's immigration section — not in original spec |
| `subtitle` field on resources | Added to display extra free-text context (e.g. "رایگان") in parens after resource type |

---

## 13. Build Sequence

Recommended implementation order within v16:

1. **Data layer:** `RoadmapResource` model + Alembic migration + `roadmap_data.py` constants
2. **Seed script:** `scripts/seed_roadmap.py` — populates all known resources (links null)
3. **Service layer:** `roadmap_service.py` with all query functions
4. **Admin CMS:** resource list + form + missing-links queue (unblocks Milad to start filling links in parallel)
5. **Landing page:** `/path/` — matrix + fork + level cards (no DB, just constants + counts)
6. **L0 Hiring page:** `/path/hiring/` — full page with Gantt + 8 area cards + DB resources
7. **L1 APM page:** `/path/apm/` — full page with all sections + DB resources
8. **Stub pages:** `/path/{slug}/` for L2–L6
9. **Nav update:** add "مسیر یادگیری" to public nav linking to `/path/`
10. **QA & deploy**

**Estimate:** ~10–14 working days for one developer (backend + templates + seed data).

---

*July 2026 · v16 spec written and shipped. Status: Shipped. Prerequisite: none (independent of v12–v15).*
