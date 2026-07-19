# Product Spec v5 — پت فیچر (About Redesign + Contact Page)

> **Prerequisite:** [Product Spec v4](./product-spec-v4.md) must be shipped · **Parent:** [Product overview](./product-spec.md)

## 1. Summary

| Field | Value |
|-------|-------|
| **Version** | v5 — About Redesign + Contact |
| **Status** | Shipped |
| **Goal** | Redesign the About page with a richer personal profile layout, and add a working Contact page with form submissions stored in the admin panel |
| **Design source** | `petfeature fable redesign/project/Petfeature About.dc.html` · `petfeature fable redesign/project/Petfeature Contact.dc.html` |
| **Epics** | (A) About Page Redesign · (B) Contact Page |

**Scope in two sentences:** Replace the current minimal About page with a three-section layout (hero, work experience, bootcamps) where experience and bootcamps are managed via the admin CMS. Add a new `/contact/` page with a form that saves messages to the database and displays them in the admin panel — no email service required.

---

## 2. Problem & Goals

**Problem:** The current About page is a simple text block with no personal context about Milad's experience or teaching work. There is no Contact page at all — visitors who want to reach out have no structured way to do so.

**v5 goals:**

- **Redesigned About** — a credibility-building page with portrait, bio, work timeline, and bootcamp listings managed from the admin CMS
- **Contact form** — visitors can send a message (name, email, subject, body); messages go to the admin panel
- **Admin inbox** — a simple read-only list of contact messages in the admin panel

---

## 3. Epic A — About Page Redesign

### 3.1 Page Layout (mirrors Fable design)

Three sections within a single `/about/` page:

| Section | Description |
|---------|-------------|
| **Hero** | 2-column grid: left = name, title, 2-paragraph bio, CTA button ("تماس با من") + LinkedIn link; right = portrait photo (3:4 aspect ratio) |
| **Work Experience** | Timeline list: each row = date range · role · company · short description |
| **Bootcamps** | 3-column card grid: each card = kind badge · name · status chip · short description · "اطلاعات دوره" link |

Responsive breakpoints (from Fable design):
- ≤ 860px: hero becomes single-column, bootcamps become single-column, experience date column narrows to 90px
- ≤ 640px: nav links shrink, footer stacks vertically

### 3.2 Data Model Changes — `AboutPage`

Extend the existing `AboutPage` model with two new JSON columns. All existing columns are retained for backward compatibility.

**New columns:**

```python
jobs: Mapped[list] = mapped_column(JSON, default=list)
# Shape: [{ "years": "۱۴۰۲ — اکنون", "role": "...", "company": "...", "desc": "..." }, ...]

camps: Mapped[list] = mapped_column(JSON, default=list)
# Shape: [{ "kind": "بوت‌کمپ", "name": "...", "status": "در حال ثبت‌نام", "desc": "...", "url": "https://..." }, ...]
```

**Existing columns — usage in new template:**

| Column | v5 usage |
|--------|----------|
| `author_name` | Hero heading |
| `author_photo` | Portrait image (right side of hero) |
| `author_bio` | Bio paragraph block in hero |
| `links` | LinkedIn URL used in hero CTA |
| `pet_feature_body` | Not shown in new template (kept in DB, not deleted) |
| `site_story_body` | Not shown in new template (kept in DB, not deleted) |

### 3.3 Admin CMS Changes — About

Extend the existing admin About edit form with:

1. **Work experience editor** — add/remove/reorder job entries (JSON textarea or structured rows); fields: years, role, company, desc
2. **Bootcamps editor** — add/remove/reorder camp entries; fields: kind, name, status, desc, url
3. Portrait photo upload — already exists, no change needed

### 3.4 User Stories — About

- *As a visitor, I want to see Milad's work history so I can assess his credibility as a PM resource author*
- *As a visitor, I want to see bootcamp listings so I can find structured PM education opportunities*
- *As Milad (admin), I want to add or update job entries without touching code so I can keep the page current*
- *As Milad (admin), I want to add, update, and link bootcamp cards without touching code*

### 3.5 Acceptance Criteria — About

- [ ] `/about/` renders the three-section Fable layout (hero, experience, bootcamps)
- [ ] Hero shows `author_name`, `author_photo`, `author_bio`, LinkedIn link from `links` JSON, and "تماس با من" button linking to `/contact/`
- [ ] If `author_photo` is not set, the portrait area shows a styled placeholder (no broken image)
- [ ] Work experience rows render from `jobs` JSON in correct RTL timeline layout
- [ ] Bootcamp cards render from `camps` JSON with correct link href from `url` field
- [ ] If `jobs` is empty, the experience section is hidden (not shown with empty state)
- [ ] If `camps` is empty, the bootcamps section is hidden
- [ ] Admin CMS form saves `jobs` and `camps` fields and reflects immediately on `/about/`
- [ ] Page is fully responsive at 860px and 640px breakpoints per Fable design
- [ ] Alembic migration adds `jobs` and `camps` columns without dropping existing data

### 3.6 Out of Scope — About

- Rich text / Markdown in bio (plain text is fine)
- Drag-and-drop reordering in admin (JSON textarea order is acceptable for v5)
- Multiple authors

---

## 4. Epic B — Contact Page

### 4.1 Page Layout (mirrors Fable design)

URL: `/contact/`

2-column layout:

| Column | Contents |
|--------|----------|
| **Main (left in RTL)** | Page heading "بنویسید، می‌خوانم." · short description · form (name, email, subject, message) · submit button · inline feedback |
| **Sidebar (right in RTL)** | "راه‌های مستقیم" card with hardcoded email/LinkedIn/Telegram links · info note about book suggestion feature |

**Hardcoded contact channels (in template, not in DB):**

| Channel | Value |
|---------|-------|
| ایمیل | hello@petfeature.ir |
| لینکدین | linkedin.com/in/milad-hajmirzaei/ |
| تلگرام | @petfeature |

### 4.2 Form Fields

| Field | Required | Notes |
|-------|----------|-------|
| name | No | Placeholder: "نام" |
| email | **Yes** | Placeholder: "ایمیل"; `direction:ltr` in input |
| subject | No | Placeholder: "موضوع" |
| message | **Yes** | Textarea, placeholder: "پیام شما…" |

**Validation (server-side):**
- `email` missing → return error "ایمیل را بنویسید تا بتوانم جواب بدهم."
- `message` empty → return error "متن پیام خالی است."
- On success → show confirmation "پیام شما رسید — ممنون! به‌زودی جواب می‌دهم."

Form submits as standard HTML POST (no JS required; graceful enhancement acceptable).

### 4.3 Data Model — `ContactMessage` (new)

```python
class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    email: Mapped[str] = mapped_column(String(500))
    subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
```

### 4.4 Routes

| Method | Path | Handler | Notes |
|--------|------|---------|-------|
| GET | `/contact/` | `web/routes.py` | Render empty form |
| POST | `/contact/` | `web/routes.py` | Validate → save → re-render with success/error |
| GET | `/admin/contact/` | `admin/routes.py` | List all messages, newest first |
| POST | `/admin/contact/{id}/read` | `admin/routes.py` | Toggle `is_read` flag |
| POST | `/admin/contact/{id}/delete` | `admin/routes.py` | Delete a message |

### 4.5 Admin Inbox

- List view at `/admin/contact/` — table with columns: date, name, email, subject, message preview, read/unread badge, actions
- "Mark as read" toggle per message
- "Delete" action per message
- Unread count badge on the admin nav sidebar (if implementable without major effort; otherwise defer)
- No reply functionality — admin reads message, replies externally via email

### 4.6 Nav link

Add "تماس" link to the main site nav (header) pointing to `/contact/`. This link already appears in the Fable design on all pages.

### 4.7 User Stories — Contact

- *As a visitor, I want to send a message to Milad without needing to open my email client*
- *As a visitor, I want to know my message was received so I'm not left wondering*
- *As Milad (admin), I want to see all contact messages in one place so I can reply at my own pace*
- *As Milad (admin), I want to mark messages as read so I can track what I've already seen*

### 4.8 Acceptance Criteria — Contact

- [ ] `/contact/` renders the Fable 2-column layout (form + sidebar) in RTL
- [ ] Form submission with valid email + message saves a `ContactMessage` row and shows success message on same page
- [ ] Submitting with empty message field shows Persian error message inline
- [ ] Submitting with empty email field shows Persian error message inline
- [ ] Sidebar shows hardcoded email, LinkedIn, Telegram links (email as `mailto:`, LinkedIn/Telegram as `target="_blank"`)
- [ ] `/admin/contact/` lists all messages newest-first with name, email, subject, truncated message, date, and read status
- [ ] Admin can mark a message as read/unread
- [ ] Admin can delete a message
- [ ] Alembic migration creates `contact_messages` table
- [ ] "تماس" link appears in site header nav on all pages

### 4.9 Out of Scope — Contact

- Email notifications to Milad on new message (can be added in v6 if desired)
- Spam/CAPTCHA protection (low traffic; acceptable for v5)
- Rate limiting on the contact form (low priority; can add later)
- Admin reply via the CMS

---

## 5. Technical Notes for Engineer

### Stack alignment
- Follows existing FastAPI + Jinja2 SSR pattern — no JS framework
- Form POST uses standard HTML form submit; success/error state passed via Jinja2 context (same pattern as admin forms)
- `ContactMessage` follows the same model conventions as `BookComment` / `PostComment`
- Service layer: `app/services/contact.py` for save + list logic; `app/services/about.py` already exists, extend it

### Migration plan
1. Add `jobs` and `camps` columns to `about_pages` (nullable, default `[]`)
2. Create `contact_messages` table
3. Single Alembic revision covers both changes

### Template files
| Template | Action |
|----------|--------|
| `app/templates/pages/about.html` | **Replace** with Fable layout |
| `app/templates/pages/contact.html` | **Create new** |
| `app/templates/admin/contact_list.html` | **Create new** |
| `app/templates/base.html` | Add "تماس" to nav |

### CSS
The Fable design is self-contained with inline styles and CSS variables. Extract shared variables into the existing CSS approach. Key design tokens:
- `--bg: #171210` · `--surface: #1e1813` · `--raise: #241d16`
- `--border: rgba(236,229,220,.08)` · `--border-2: rgba(236,229,220,.15)`
- `--text: #ece5dc` · `--muted: #8f8378` · `--faint: #63594e` · `--accent: #a6c3a0`

---

## 6. NFRs

- **RTL:** All layouts must be `direction:rtl`; email input uses `direction:ltr; text-align:right`
- **Persian font:** Vazirmatn (already loaded via Google Fonts in base template)
- **Responsive:** About hero + bootcamps stack at ≤ 860px; contact form stacks at ≤ 860px
- **Accessibility:** Form inputs must have `placeholder` text (Persian); submit button must be keyboard-accessible
- **Performance:** No new JS dependencies; page load stays server-rendered

---

## 7. Open Questions

| Question | Owner | Status |
|----------|-------|--------|
| What is Milad's exact Telegram handle for `/contact/` sidebar? (design shows `@petfeature`) | Milad | ⏳ Confirm before template is hardcoded |
| Should the "تماس با من" button in the About hero link to `/contact/`? | Milad | Assumed yes — confirm |
| Do bootcamp cards link to external URLs? (assumed yes, `target="_blank"`) | Milad | Assumed yes |
| Should admin nav show an unread message badge/count? | Milad | Nice-to-have; implement only if straightforward |

---

## Deployment Status

| Field | Value |
|-------|-------|
| **Status** | Shipped |
| **Deploy date** | July 2026 |
| **Platform** | Hamravesh Darkube (production) |
| **Notes** | — |
