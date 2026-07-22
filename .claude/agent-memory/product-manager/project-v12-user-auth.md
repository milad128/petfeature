---
name: project-v12-user-auth
description: v12 User Registration + Auth spec written July 2026 — email/password auth, sessions, profile, password reset, admin user list
metadata:
  type: project
---

v12 PRD written and saved to `docs/product-spec-v12.md` (July 2026). Backlog item, unscheduled. Prerequisite for v13 Reading List.

**Scope:** Register, login, logout, profile page, forgot/reset password, admin user list + deactivate.

**Key decisions:**
- Email + password only — no social login (Google deferred; adds OAuth complexity)
- No email verification on registration — single step, lower friction
- Server-side sessions via signed `SECRET_KEY` cookie — consistent with existing admin auth; no JWT
- "مرا به خاطر بسپار" = 30-day cookie; unchecked = session cookie
- Password hashing: bcrypt via `passlib[bcrypt]` (add to requirements.txt)
- Password reset requires email provider (Resend recommended — share with v11 Newsletter); graceful disable if unconfigured
- No email enumeration on login or forgot-password — combined error messages
- Rate limiting: 5 register attempts/IP/hour; 10 login attempts/IP/15min
- Admin user list is read-only except for activate/deactivate — no edit or password reset from admin

**Data model:** `User` (id, name, email, hashed_password, is_active, created_at); UNIQUE on email; Alembic migration required.

**Critical:** Ship v12 together with v13 Reading List — auth alone provides no user-visible value. [[project-v11-newsletter]]
