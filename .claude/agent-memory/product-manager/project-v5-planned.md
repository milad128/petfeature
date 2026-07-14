---
name: project-v5-planned
description: v5 About Redesign + Contact Page spec decisions — July 2026
metadata:
  type: project
---

v5 spec written July 2026. Two epics: About page redesign and new Contact page.

**Key decisions made:**
- About experience/bootcamps: CMS-editable via `jobs` (JSON) and `camps` (JSON) columns added to existing `AboutPage` model
- Contact form delivery: DB only (no email) — messages stored in `ContactMessage` table, visible in admin panel at `/admin/contact/`
- Contact channels sidebar (email, LinkedIn, Telegram): hardcoded in template, not CMS-managed
- "تماس با من" CTA on About hero links to `/contact/`

**Open questions before build:**
- Confirm Telegram handle is `@petfeature`
- Confirm bootcamp cards link externally (`target="_blank"`)
- Admin unread badge on nav: implement only if straightforward

**Why:** Fable redesign file (`petfeature fable redesign/project/`) provided the exact HTML/CSS for both pages. Milad confirmed decisions via Q&A.

**How to apply:** When engineer asks about model changes, point to `AboutPage` extension (`jobs`, `camps` JSON columns) and new `ContactMessage` model. Contact page has no email service dependency — DB-only.

See: `docs/product-spec-v5.md`

[[project-v4-shipped]]
