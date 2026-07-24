---
name: project-v12-user-auth
description: v12 User Auth via Google Login — Google OAuth only, no email/password, no SMTP needed; auto-registration; profile page (minimal); admin user list; backlog
metadata:
  type: project
---

v12 revised July 2026. **Google Login only** — original email/password approach dropped because no SMTP server available for password reset.

**Status:** Backlog

**Key decisions:**
- **Google OAuth 2.0 only** — no email/password, no bcrypt, no password reset flow
- No SMTP needed — Google handles all identity verification
- Auto-registration on first Google login — no separate sign-up form
- `google_id` (Google's `sub` claim) is the stable identity key — email can change but google_id won't
- Server-side sessions via signed `SECRET_KEY` cookie; 30 days always persistent (no "remember me" toggle)
- Library: `authlib` (add to requirements.txt)
- **Option C decision:** ships standalone — profile page is minimal (name, email, join date only); no Reading List bundled
- Do NOT add "ثبت‌نام کن" CTAs sitewide until Reading List (v14+) ships

**Data model:** `User` (id, name, email, google_id UNIQUE, is_active, created_at) — no hashed_password; Alembic migration required.

**New env vars:** `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`

**One-time setup:** Google Cloud Console → create project → enable Google+ API → OAuth 2.0 credentials → set redirect URI to `https://petfeature.ir/auth/google/callback/`

**Effort:** ~2 days

**Unlocks:** Reading List (v14+), personalised features. [[project-v13-newsletter-bot]]
