# Design Brief (Temporary) — User Features: Registration, Dashboard & Bookshelf

> **Purpose:** A throwaway design brief handed to **Claude Design** to design the UI for three linked features: User Registration (v12), User Dashboard (v14), and Bookshelf (v15). Delete after designs are produced. Source of truth remains the individual specs: [v12](../spec-v12-user-auth.md) · [v14](../spec-v14-user-dashboard.md) · [v15](../spec-v15-bookshelf.md).

---

## ▶️ Prompt for Claude Design (copy-paste this)

```
You are designing UI for petfeature.ir — a Persian-language (RTL) Product
Management encyclopedia. Design a cohesive set of screens for three connected
features: Google login, a user dashboard, and a personal "bookshelf".

CONTEXT
- Product: petfeature.ir (پت فیچر) — «دانشنامه یک مدیر محصول», a curated PM
  book library + blog + tools, in Persian.
- Audience: Persian-speaking Product Managers. Professional, calm, content-first.
- Language & direction: ALL copy in Persian (Farsi), fully RTL. Emails and URLs
  render LTR (dir="ltr") even inside RTL layout.
- Tech constraint: server-rendered HTML (Jinja2) + vanilla JS + CSS. NO React,
  no SPA, no heavy client framework. Design must be buildable as static HTML/CSS
  with light progressive-enhancement JS. Modals must have a no-JS fallback.
- Font: Vazirmatn (already used sitewide). Keep the existing site's visual
  language — reuse existing header, footer, cards, and button styles. These are
  NEW pages inside an EXISTING design system, not a rebrand.
- Dates: Jalali (شمسی) calendar everywhere.
- Accessibility: status colors must pair with text/icons (not color alone);
  keyboard-navigable; visible focus states.

DELIVERABLES — design these screens (details in the brief below):
1. Login page (single «ورود با گوگل» button)
2. Header auth states (logged out vs logged in)
3. User Dashboard (/profile/) — user info + Telegram section + My Comments section
4. Bookshelf page (/profile/bookshelf/) — summary bar + book cards + empty state
5. Book detail additions — save-to-shelf button, status picker, social-proof count
6. "خواندم" review modal — star rating + optional comment
7. Admin: user list table + books-list «در قفسه» column (low priority, simple)

FOR EACH SCREEN, PROVIDE
- Layout (desktop + mobile, RTL)
- All Persian copy (headings, labels, buttons, empty states, success/error msgs)
- Component states (default, hover, active, disabled, loading, empty, error)
- Notes on reused vs new components
- Accessibility notes

STYLE
- Clean, editorial, generous whitespace, content-first. Not flashy.
- Match the existing library/blog card aesthetic.
- Show, don't just describe: include ASCII/wireframe layouts and a component list.

Ask me clarifying questions before finalizing if anything about the existing
design system is ambiguous.
```

---

## 1. Product & Brand Context

| Field | Value |
|-------|-------|
| Product | petfeature.ir (پت فیچر) |
| Tagline | دانشنامه یک مدیر محصول |
| Audience | Persian-speaking Product Managers |
| Language | Persian (Farsi), fully RTL |
| Font | Vazirmatn (incl. Bold) |
| Tone | Professional, calm, editorial, content-first |
| Tech | FastAPI + Jinja2 SSR, vanilla JS + CSS. No SPA framework. |
| Calendar | Jalali (شمسی) |

**Critical:** these are new pages *inside* an existing design system. Reuse the current header, footer, buttons, cards, and color palette. Do not redesign the brand.

---

## 2. Screens to Design

### Screen 1 — Login Page (`/login/`)  [v12]

- **Single action:** one «ورود با گوگل» button (Google logo + text). No email/password form, no separate sign-up.
- Short reassurance copy: why log in (e.g. «برای ساختن قفسه کتاب شخصی و پیگیری نظرات خود وارد شوید»).
- Small print: «با ورود، حساب شما به‌صورت خودکار ساخته می‌شود.»
- Error state (shown on redirect back): «خطا در ورود. لطفاً دوباره امتحان کنید.» and «حساب کاربری شما غیرفعال شده است.»
- If already logged in → this page isn't shown (redirect). Design the logged-out state only.

**States:** default · button hover/active · error banner.

---

### Screen 2 — Header Auth States  [v12]

Two variants of the existing site header:
- **Logged out:** a «ورود» link/button in the header nav.
- **Logged in:** user's name shown + a «خروج» action (logout is a POST — design as a button/menu item, not a bare link). Consider a small dropdown containing: «داشبورد من», «قفسه کتاب من», «خروج».

**States:** logged out · logged in (name short) · logged in (name long — truncation) · mobile menu versions.

---

### Screen 3 — User Dashboard (`/profile/`)  [v14]

Logged-in only. Structure top to bottom:

1. **User info header:** name, email (`dir="ltr"`), join date (Jalali).
2. **Section A — تلگرام (Telegram):**
   - A single «عضویت در کانال تلگرام @petfeature» button (opens `https://t.me/petfeature` in a new tab) + one-line description.
   - **No subscription state to design.** The email newsletter was removed from the product (July 2026) — there is no subscribe/unsubscribe toggle, no email field, and no `Subscriber` record. Telegram is the only channel and joining happens on Telegram's side.
3. **Section B — نظرات من (My Comments):**
   - List of the user's comments across books + posts, newest first.
   - **Comment card:** content-type badge («یادداشت» / «کتاب»), linked title, comment text (truncate >200 chars with «بیشتر»), Jalali date, status badge.
   - **Status badges (text + color + icon):** «در انتظار تأیید» (yellow) · «تأیید شده» (green) · «رد شده» (red).
   - **Admin reply block** (when present): labeled «پاسخ پت فیچر:», full reply text + Jalali date, visually nested under the comment.
   - **Empty state:** «هنوز نظری ثبت نکردی. کتاب‌ها و یادداشت‌ها رو بخون و نظرت رو بنویس.»
   - Pagination: 10 per page.

**States:** subscribed/unsubscribed · comments list populated · comment with reply · comment without reply · rejected comment · empty state · paginated.

---

### Screen 4 — Bookshelf Page (`/profile/bookshelf/`)  [v15]

Logged-in only. Title: «قفسه کتاب من».

- **Summary bar:** «X کتاب در قفسه» · «Y خواندم» · «Z در حال خواندن».
- **Book cards (newest added first):** cover thumbnail, title (links to book), author, **status badge**, inline **status changer** (3 pill options), added date (Jalali), remove action.
- **Reading statuses:** «می‌خواهم بخوانم» · «در حال خواندن» · «خواندم». Give "خواندم" a subtle done treatment (check/muted).
- **Empty state:** «هنوز کتابی به قفسه‌ات اضافه نکردی. از کتابخانه شروع کن.» + link «رفتن به کتابخانه →».

**States:** populated · single item · empty · status-change interaction · remove confirm.

---

### Screen 5 — Book Detail Additions  [v15]

Add to the *existing* book detail page (design these additions in-context):

- **Save button** with 5 states:
  | State | Label | Style |
  |-------|-------|-------|
  | Not logged in | افزودن به قفسه | secondary/outlined (click → login) |
  | Logged in, not saved | افزودن به قفسه | primary |
  | Saved — می‌خواهم بخوانم | می‌خواهم بخوانم ✓ | active/filled |
  | Saved — در حال خواندن | در حال خواندن ✓ | active/filled |
  | Saved — خواندم | خواندم ✓ | active/filled |
- **Status picker:** appears on click (inline, below button) — 3 options + «حذف از قفسه» link.
- **Social-proof counter:** «X نفر این کتاب را در قفسه‌شان دارند» — shown only when count ≥ 2.

**States:** all 5 button states · picker open · social proof shown/hidden.

---

### Screen 6 — "خواندم" Review Modal  [v15]

Opens when a user marks a book as **خواندم** (only on the transition to read).

- **Headline:** «کتاب را خواندی! نظرت چیه؟»
- Book title + cover thumbnail.
- **Star rating:** interactive 1–5 (reuse existing v4 book-rating stars).
- **Comment textarea:** optional, label «نظر شما (اختیاری)».
- **Primary CTA:** «ثبت نظر» — disabled until a rating OR comment is entered.
- **Dismiss:** «بعداً» link, × icon, overlay click, Escape. Dismissing keeps the "read" status.
- **Success after comment:** «نظر شما ثبت شد و پس از تأیید نمایش داده می‌شود» (comments are moderated).
- **No-JS fallback:** if the modal can't run, the read status still saves and the user uses the normal rating/comment forms already on the page. Design should not depend on JS for the core action.

**States:** open (empty) · rating selected · comment typed · CTA enabled/disabled · submitting · success · dismissed.

---

### Screen 7 — Admin Screens (low priority, simple)  [v12 + v15]

Match the existing admin panel styling.

- **Admin user list (`/admin/users/`):** table — نام · ایمیل (LTR) · تاریخ عضویت (Jalali) · وضعیت (فعال/غیرفعال) · action (غیرفعال‌سازی / فعال‌سازی). Summary line «X کاربر ثبت‌نام‌شده». Pagination 50/page.
- **Admin books list `در قفسه` column:** add one sortable numeric column to the existing books table showing per-book save count. Trivial — no new layout.

---

## 3. Cross-Cutting Design Requirements

- **RTL everything.** Emails + URLs in `dir="ltr"`.
- **Reuse the existing design system** — header, footer, cards, buttons, palette, Vazirmatn.
- **Jalali dates** everywhere user-facing.
- **Status colors need text + icon**, not color alone (colour-blind safe).
- **Modals need a no-JS fallback** and must be keyboard-navigable (focus trap, Escape to close, visible focus).
- **Mobile + desktop** layouts for every screen.
- **Progressive enhancement:** core actions work via plain form POST; JS only enhances.
- **Empty states** should be friendly and push users toward content.

---

## 4. What NOT to Design (out of scope)

- Email/password forms, password reset, email verification (Google handles auth).
- User-editable profile (name/email come from Google).
- Public/shareable bookshelf or public profile pages.
- Notes-per-book, reading progress bars, Goodreads import.
- Notification UIs (email/Telegram on reply).
- Any brand/identity redesign.

---

## 5. Feature → Spec Map (for reference)

| Screen | Feature | Spec |
|--------|---------|------|
| Login, Header auth, Admin users | v12 User Auth | [spec-v12-user-auth.md](../spec-v12-user-auth.md) |
| Dashboard (Telegram + My Comments) | v14 User Dashboard | [spec-v14-user-dashboard.md](../spec-v14-user-dashboard.md) |
| Bookshelf, Book detail additions, Review modal, Admin column | v15 Bookshelf | [spec-v15-bookshelf.md](../spec-v15-bookshelf.md) |

---

*Temporary brief — July 2026. Delete once designs are delivered. Specs remain the source of truth.*
