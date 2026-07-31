# Design Brief (Temporary) — Learning Roadmap (مسیر یادگیری)

> **Purpose:** A throwaway design brief handed to **Claude Design** to design the UI for the Learning Roadmap epic — a public, browsable PM career curriculum plus its admin CMS. Delete after designs are produced.
>
> **Source of truth for content:** [pm-learning-roadmap.md](../New%20idea/pm-learning-roadmap.md) — the complete, finished content spec (~1,230 lines). Everything the designer needs to know about *what* goes on these pages is in that file.
>
> **Working prototypes already exist** in [`prototypes/`](../prototypes/) — 7 public pages + 4 admin pages, RTL, functional. They are a **starting point to improve on, not a spec to reproduce.** Open them before designing.

---

## ▶️ Prompt for Claude Design (copy-paste this)

```
You are designing UI for petfeature.ir — a Persian-language (RTL) Product
Management encyclopedia. Design the "Learning Roadmap" (مسیر یادگیری) — a
public, browsable PM career curriculum, plus the admin screens that manage it.

CONTEXT
- Product: petfeature.ir (پت فیچر) — «دانشنامه یک مدیر محصول», a curated PM
  book library + blog + tools, in Persian.
- Audience: Persian-speaking Product Managers, from aspiring APM to CPO.
  Professional, calm, content-first. They are readers, not skimmers — but they
  arrive anxious about their own career progress.
- Language & direction: ALL UI copy in Persian (Farsi), fully RTL. Book and
  resource titles stay in their original language (mostly English) and render
  LTR (dir="ltr") inside the RTL layout. URLs render LTR.
- Tech constraint: server-rendered HTML (Jinja2) + vanilla JS + CSS. NO React,
  no SPA, no charting library. Must be buildable as static HTML/CSS with light
  progressive-enhancement JS. Anything interactive needs a no-JS fallback.
- Font: Vazirmatn (already used sitewide). These are NEW pages inside an
  EXISTING design system — reuse the site's header, footer, cards, buttons.
  Not a rebrand.
- Accessibility: never encode meaning in colour alone; keyboard-navigable;
  visible focus; real semantic <table> for tabular data; touch-friendly (no
  hover-only affordances).

THE CONTENT MODEL (read this carefully — the design lives or dies on it)
- 6 career LEVELS: APM → PM → Senior PM → Product Lead → Director → CPO.
- PLUS one SEPARATE TRACK, "Roadmap 0 — Getting Hired" (مسیر استخدام), which
  sits outside the ladder. It covers résumé, portfolio, the three interview
  formats, job search and negotiation, and it ENDS when the user accepts an
  offer. It has its own four phases (آماده‌سازی / تمرین / اقدام / پذیرش) — NOT
  the Entry/Core/Supporting/Bridge structure the seniority levels use, because
  a job hunt is a campaign with an end date, not a tenure. Its phases overlap
  on purpose. Design it as a visibly different kind of page.
- 15 COMPETENCIES (e.g. کشف محصول, تحویل و اجرا, استراتژی محصول), grouped in
  4 domains.
- A DEPTH MATRIX: 15 × 6 grid. Each cell is a required depth 1–5, or "–"
  (not required). This is the centrepiece of the whole feature.
- Each level sorts its competencies into 4 CATEGORIES that form a TIMELINE
  through holding that job:
    ورود (Entry)     — what you need before you get the title
    هسته (Core)      — what you're personally accountable for, daily
    حمایتی (Supporting) — what you contribute to but don't own
    پل (Bridge)      — what you need to ask for the promotion
  Plus two passive states: «رایگان به دست می‌آید» (acquired free — no study
  assigned) and «تثبیت» (maintain — depth unchanged).
- Each competency carries THREE numbers that must never be confused:
    مطالعه (Reading)   — hours of material
    اسپرینت (Sprint)   — weeks where it's your single active project
    بلوغ (Maturation)  — months until you actually reach the depth
  Reading and Sprint sum; Maturation windows overlap and must NEVER be summed.
- Each RESOURCE (book/article/course/podcast) has: title, type, reading time,
  difficulty (1–3 stars), Persian-translation availability, required-vs-optional,
  an optional external link, and a short HOMEWORK task written for that
  specific resource.

DELIVERABLES — design these screens (details in the brief below):
PUBLIC
1. Roadmap landing (/path/) — the depth matrix, level summary, how-to-read,
   and a clear fork between "I want the job" and "I have the job"
2. Level detail (/path/{level}/) — Entry/Core/Supporting/Bridge + sequencing
2b. Getting-Hired track (/path/hiring/) — four phases, overlapping, campaign
   framing rather than tenure framing
3. Competency card — the repeating unit; collapsed + expanded states
4. Resource row + its homework — the densest repeating element
5. Sequencing table — week-by-week sprints with what's maturing alongside
ADMIN
6. Level list, level resources (grouped by category), resource edit form,
   and a "missing links" work queue

FOR EACH SCREEN, PROVIDE
- Layout for desktop AND mobile, RTL
- All Persian copy (headings, labels, empty states, help text)
- Component states (default, hover, focus, active, expanded, empty)
- Notes on reused vs new components
- Accessibility notes

STYLE
- Clean, editorial, generous whitespace, content-first. Not flashy, not gamified.
- Match the existing library/blog card aesthetic.
- Show, don't just describe: ASCII/wireframe layouts plus a component list.

There are working prototypes in prototypes/ — open them first. Improve on them;
do not just reproduce them. The hard problems are listed in section 3 of the
brief; those are what I actually want your thinking on.

Ask me clarifying questions before finalizing if anything is ambiguous.
```

---

## 1. Product & Brand Context

| Field | Value |
|-------|-------|
| **Product** | پت فیچر — petfeature.ir |
| **Tagline** | دانشنامه یک مدیر محصول |
| **Language** | Persian (فارسی), fully RTL |
| **Font** | Vazirmatn |
| **Stack** | FastAPI + Jinja2, server-rendered. Vanilla JS + CSS only. |
| **Existing epics** | Library (کتابخانه), Blog (یادداشت), Tools (ابزارها) — all shipped |
| **This epic** | Roadmap (مسیر یادگیری) — the fourth founding epic, never built |
| **Public routes** | `/path/`, `/path/hiring/`, `/path/{level_slug}/` |
| **Admin routes** | `/admin/roadmap/`, `/admin/roadmap/{level}/`, resource form |

**Existing prototypes to open first** (all in [`prototypes/`](../prototypes/)):

| File | What it is |
|---|---|
| `roadmap.html` | Landing page with the matrix |
| `roadmap-level-1.html` … `-6.html` | All six level pages |
| `admin-roadmap.html` | Admin level list |
| `admin-roadmap-level-1.html` | Admin resource management, grouped by category |
| `admin-roadmap-resource.html` | Resource edit form (incl. the link field) |
| `admin-roadmap-links.html` | Missing-links work queue |
| `roadmap.css` / `admin-roadmap.css` | Current styling; admin tokens match the real panel |

---

## 2. Screens to Design

### Screen 1 — Roadmap Landing (`/path/`)

The entry point. Must answer «من کجای این مسیرم؟» within seconds.

Contains, in rough priority order:
- **The depth matrix** — 15 competencies × 6 levels. The single most important element on the site.
- Depth scale legend (۱ آگاه → ۵ تعریف می‌کند)
- Level summary table — 6 rows: required resources, reading hours, sprint weeks, tenure
- "How to read this" explainer — the three numbers, the four categories
- Reading-the-matrix insights (which competencies decline, which step-jump)
- The five-book spine
- Persian-coverage table
- Navigation into all six levels

### Screen 2 — Level Detail (`/path/{level}/`)

The workhorse page. Six of these, varying wildly in density — L3 has 6 core competencies, L4 has 2.

Structure, in order:
- Hero: level name, spec sentence, the three headline numbers, tenure
- "What this level asks of you" — competency table with depth, category, sprint, maturation
- Phase timeline nav (ورود → هسته → حمایتی → پل)
- **ورود** — reading-only, no sprint
- **هسته** — 2–6 competency cards
- **حمایتی** — table form, one resource each
- **رایگان به دست می‌آید** — what you get for free and why
- **عقب بکشید** (L4, L5 only) — competencies you deliberately *reduce*
- **توالی** — week-by-week sequencing
- **پل** — bridge resources + promotion checklist («آماده‌ی … هستید وقتی»)

### Screen 2b — Getting-Hired Track (`/path/hiring/`)

**A deliberately different page shape.** This is the only track that is a campaign rather than a tenure, and the design should make that legible at a glance — someone landing here should never think they are looking at a seventh seniority level.

Structure:
- Hero: framing as a 3–6 month campaign with an end condition ("ends the day you accept an offer")
- Who it's for: career-switchers, graduates, PMs changing companies
- **Four phases** — آماده‌سازی · تمرین · اقدام · پذیرش — with 8 areas across them
- Each area: sprint weeks, reading, resources, and a homework task
- Two closing checklists: «آماده‌ی اقدام هستید وقتی» (ready to apply) and the hand-off to Level 1
- An explicit "what this track excludes" table

Design problems specific to this page:
- **The phases overlap on purpose** (applying begins during practising). The sequencing metaphor used on level pages — one sprint at a time, strictly sequential — is *wrong* here and must not be reused unchanged.
- It needs an **exit**, not a bridge. The page ends with "you accepted an offer → go to Level 1."
- The three interview formats (product sense, analytical, behavioural) are parallel siblings, not a sequence.

### Screen 3 — Competency Card

The repeating unit inside هسته. Needs a collapsed and an expanded state.

Collapsed must show: order number, name, target depth, habit-vs-knowledge tag, and all three numbers.
Expanded adds: rationale prose, resource table, a «چرا این، نه آن؟» quote callout, and a practice exercise.

Currently built with native `<details>/<summary>` — no JS. Keep that property.

### Screen 4 — Resource Row + Homework

The densest element on the site. Each resource row carries seven attributes, and beneath it sits a **تکلیف** (homework) block — a short, specific task derived from that resource.

The homework must read as *attached to* its resource, not as a sibling row. There are 112 of these across the six levels.

Resource titles link out when a URL exists and are plain text when it doesn't — roughly a third currently have no link, and that state needs to not look broken.

### Screen 5 — Sequencing Table

Three columns: week range · the one sprint running · what's maturing in the background. Ends with a long "no sprints" stretch and then the bridge.

The insight this table must deliver: **most of a level is maturation, not study.** Currently a plain table; a timeline or gantt treatment may serve it better.

### Screen 6 — Admin Screens

Lower visual priority; correctness and speed matter more than polish. Uses the existing admin panel design system (orange accent `#c2410c`, sidebar shell, `.admin-table`, `.card`).

- **Level list** — 6 rows, resource counts, missing-link counts
- **Level resources** — grouped by the four categories, one table per competency, reorderable, «+ منبع جدید» per group
- **Resource form** — all attributes, plus the two mutually-exclusive link options (external URL vs. link to a library Book) and the homework field
- **Missing-links queue** — every resource without a destination, filterable

---

## 3. The Hard Problems

**This is what I actually want design thinking on.** The prototypes solve these adequately; none are solved *well*.

**3.1 The matrix on a phone.** 15 rows × 6 columns of numbers, RTL, no horizontal page scroll allowed. Current solution: scrolls inside its own container with a sticky competency column. Is there something better? Consider that the matrix is *not* mainly read cell-by-cell — people scan a **row** ("how does discovery evolve?") or a **column** ("what does Senior PM need?").

**3.2 Making declines and step-jumps visible.** The most interesting information in the matrix is not the numbers — it's that Delivery goes 3→4→4→3→2→2 (you're meant to get *less* hands-on) and People Leadership goes –→–→1→3→4→5 (a cliff). These are currently badges with `title=""` tooltips, **which never fire on touch devices.** That's a real gap, not a prototype shortcut.

**3.3 Three numbers, no legend lookup.** Reading / Sprint / Maturation appear together dozens of times. Currently three fixed icon+colour pairs (📖 / 🎯 / 🌱). Emoji is a crude solution. Users must never have to scroll back to a legend.

**3.4 Communicating that maturation ≠ homework.** The single most important idea in the whole feature: a level is ~7–13 months of deliberate study inside a 12–60 month tenure, and the gap is real work that cannot be accelerated. If a user reads "31 weeks" and thinks that's the whole level, the design has failed.

**3.5 L4 must not look trivial.** Product Lead has the fewest resources (8), the least reading (~49h), the shortest sprint load (~4.5 months) — and is the level people most often fail, because ~75% of it is habit-competency maturation on feedback loops you don't control. A page that is visibly the thinnest currently implies "easy". It should imply "there is nothing to read here, and that's the problem."

**3.6 The empty states are the honest ones.** «رایگان به دست می‌آید» means a competency gets *no resources at all*, deliberately. «عقب بکشید» means a competency you should get *worse* at. Both are content, not absence — they must not read as unfinished sections.

**3.7 Progressive disclosure without hiding the answer.** Someone asking "what do I study first?" should get it in seconds. Someone reading deeply wants the rationale quotes and homework. Currently native `<details>`; the trade-off is that closed cards hide the resource list entirely.

**3.8 The fork on the landing page.** Two audiences arrive at `/path/`: people who want a PM job and people who have one. They need different first clicks. The matrix is meaningless to someone who has never held the role — she needs Roadmap 0, not a depth self-assessment. Getting this fork right without cluttering the landing page is unsolved in the current prototypes, which do not include Roadmap 0 at all.

**3.9 Unlinked resources.** ~39 of 112 resources have no destination. They render as plain text today. They should look intentional rather than broken — and ideally hint that the Persian book note is coming.

---

## 4. Cross-Cutting Requirements

- **RTL throughout.** Resource titles, URLs, and English book names render LTR inside the RTL flow (`dir="ltr"`, `unicode-bidi: embed`).
- **Numerals:** Persian digits (۰–۹) in all UI chrome. Latin digits acceptable inside English resource titles.
- **No colour-only meaning.** Depth, required-vs-optional, jumps and declines all need a text or shape carrier alongside colour.
- **Touch-first affordances.** No information that exists only in a hover tooltip.
- **Wide content scrolls inside its own container** — the page body never scrolls horizontally.
- **Light + dark.** Use `prefers-color-scheme` plus a `data-theme` override.
- **No JS required for core reading.** JS may enhance; it may not gate content.
- **Jalali dates** if any dates appear.

---

## 5. What NOT to Design

| Out of scope | Why |
|---|---|
| Personalized paths, self-assessment quiz, résumé upload | A later phase; needs user auth (v12) first |
| Progress tracking, "mark as read", progress bars | Needs auth + the Bookshelf feature (v15) |
| User accounts, login, profile | Separate brief — see [design-brief-user-features.md](./design-brief-user-features.md) |
| Certificates, badges, leaderboards, streaks | Explicitly rejected — this is not a gamified product |
| Book detail pages, library, blog | Already shipped; only *link into* them |
| Creating new roadmap content | The content is finished and frozen |
| Job board, application tracking, CV upload | Roadmap 0 teaches the job hunt; it does not run it |

---

## 6. Reference Map

| Need | Where |
|---|---|
| **All content** — levels, competencies, resources, numbers, Persian copy source | [pm-learning-roadmap.md](../New%20idea/pm-learning-roadmap.md) |
| Working public prototypes | [`prototypes/roadmap*.html`](../prototypes/) |
| Working admin prototypes | [`prototypes/admin-roadmap*.html`](../prototypes/) |
| Existing public site design system | `app/static/css/main.css`, `app/templates/base.html` |
| Existing admin design system | `app/static/css/admin.css`, `app/templates/admin/base.html` |
| How this epic fits the roadmap | [spec.md](../spec.md) · [product backlog.md](../product%20backlog.md) |

---

## 7. Handing the Designs Back

When designs come back, they go straight to implementation. To make that clean, the deliverable should include:

- Wireframes or layouts for **desktop and mobile**, for every screen in section 2
- **Complete Persian copy** — not lorem, not English placeholders
- A **component inventory**: what's reused from the existing design system vs. genuinely new
- **States** for every interactive element
- Explicit answers to the section 3 problems, with reasoning — including where a problem was deliberately left unsolved and why

*Temporary document. Delete once designs are produced and implemented.*
