# Product Spec v12 — User Registration + Auth (احراز هویت کاربران)

**Version:** v12  
**Status:** Planned  
**Author:** Milad Mirzaei  
**Date:** July 2026  
**Depends on:** v1–v10  
**Unlocks:** Reading List (v13+), Bookmarks, personalised features

---

## Overview

v12 introduces a public-facing authentication system — registration, login, logout, profile page, and password reset — for site visitors. This is entirely separate from the existing admin session auth.

v12 is a **prerequisite epic**: it has no standalone user value unless paired with at least one personalised feature (Reading List, v13). Ship v12 and v13 together in the same release, or hold both until ready.

---

## Problem Statement

All current features on petfeature.ir are fully anonymous — visitor identity is tracked only by an ephemeral cookie token, used for deduplicating ratings and comments. There is no concept of a user account.

To build personalised features — a reading list, saved bookmarks, custom notification preferences — the site needs a persistent user identity. v12 creates the foundation.

---

## Target Users

- **Registered visitor:** A Persian-speaking PM professional who wants to track their reading progress and save books across sessions.
- **Admin (Milad):** Needs visibility into the registered user base — count, join dates — without managing individual accounts directly.

---

## User Stories

### Registration & Login

| # | As a… | I want to… | So that… |
|---|-------|-----------|---------|
| U1 | Visitor | Create an account with my name, email, and a password | I have a persistent identity on the site |
| U2 | Visitor | Log in with my email and password | I can access my personal data (reading list etc.) |
| U3 | Visitor | Log out | My session is cleared on shared devices |
| U4 | Visitor | Reset my password via email if I forget it | I can regain access without contacting anyone |
| U5 | Visitor | See a clear error if I try to register with an email already in use | I understand why registration failed and can log in instead |
| U6 | Visitor | Stay logged in across browser sessions | I don't have to log in every time I visit |

### Profile

| # | As a… | I want to… | So that… |
|---|-------|-----------|---------|
| U7 | Registered user | View my profile page | I can confirm my account details and access personalised features |
| U8 | Registered user | See my name displayed in the site header when logged in | I know I'm logged in |

### Admin

| # | As a… | I want to… | So that… |
|---|-------|-----------|---------|
| U9 | Admin | See a list of registered users with name, email, and join date | I have visibility into the user base |
| U10 | Admin | See the total registered user count | I can track growth |
| U11 | Admin | Deactivate a user account | I can handle abuse without deleting data |

---

## Data Model

**New model: `User`**

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | Integer | PK, auto-increment | |
| `name` | String(200) | NOT NULL | Display name |
| `email` | String(300) | NOT NULL, UNIQUE | Lowercased before save |
| `hashed_password` | String(500) | NOT NULL | bcrypt hash; plain password never stored |
| `is_active` | Boolean | NOT NULL, default=True | False = deactivated by admin |
| `created_at` | DateTime | NOT NULL, server_default=now() | |

**Session management:** Server-side sessions via signed cookie using the existing `SECRET_KEY` environment variable. No separate `UserSession` table — session data (user ID) is stored in a signed, httponly cookie consistent with the existing admin auth pattern. Session lifetime: 30 days with "remember me" enabled; browser session without.

**No JWT.** This is an SSR app; JWTs add complexity with no benefit over signed cookies in this context.

**Alembic migration required** — creates the `users` table.

**Password hashing:** `passlib[bcrypt]` — already a common FastAPI pattern; add to `requirements.txt`.

---

## Pages & Routes

| Method | Path | Name | Purpose |
|--------|------|------|---------|
| `GET` | `/register/` | `register` | Registration form |
| `POST` | `/register/` | `register_submit` | Process registration |
| `GET` | `/login/` | `login` | Login form |
| `POST` | `/login/` | `login_submit` | Process login |
| `POST` | `/logout/` | `logout` | Clear session, redirect home |
| `GET` | `/profile/` | `profile` | User profile page (auth required) |
| `GET` | `/forgot-password/` | `forgot_password` | Forgot password form |
| `POST` | `/forgot-password/` | `forgot_password_submit` | Send reset email |
| `GET` | `/reset-password/` | `reset_password` | Reset password form (token in query param) |
| `POST` | `/reset-password/` | `reset_password_submit` | Process password reset |
| `GET` | `/admin/users/` | `admin_users` | Admin user list |
| `POST` | `/admin/users/{id}/deactivate/` | `admin_user_deactivate` | Deactivate a user |

---

## Acceptance Criteria

### Registration (`/register/`)

1. Form fields: نام (required), ایمیل (required), رمز عبور (required, min 8 chars), تکرار رمز عبور (required, must match).
2. Email is lowercased and trimmed before validation.
3. On success: user record created with bcrypt-hashed password; user is logged in immediately; redirected to `/profile/` with a welcome message: "خوش آمدی، {name}!"
4. Duplicate email: form re-renders with error "این ایمیل قبلاً ثبت شده. وارد شوید."
5. Password too short: "رمز عبور باید حداقل ۸ کاراکتر باشد."
6. Passwords don't match: "تکرار رمز عبور مطابقت ندارد."
7. Honeypot field present to block bot registrations.
8. Rate limiting: max 5 registration attempts per IP per hour.

### Login (`/login/`)

9. Form fields: ایمیل (required), رمز عبور (required), checkbox "مرا به خاطر بسپار" (remember me, default unchecked).
10. On success: session cookie set; user redirected to `next` query param if present, otherwise to `/profile/`.
11. Invalid email or wrong password: "ایمیل یا رمز عبور اشتباه است." — no distinction between the two (prevents user enumeration).
12. Deactivated account: "حساب کاربری شما غیرفعال شده است."
13. "مرا به خاطر بسپار" unchecked: session cookie expires at browser close. Checked: cookie lifetime 30 days.
14. Rate limiting: max 10 login attempts per IP per 15 minutes; after limit exceeded: "تعداد تلاش‌های ورود بیش از حد مجاز است. لطفاً ۱۵ دقیقه صبر کنید."

### Logout

15. `POST /logout/` clears the session cookie and redirects to home (`/`).
16. Logout uses POST (not GET) to prevent CSRF-triggered logouts from external links.

### Profile (`/profile/`)

17. Accessible only when logged in. Unauthenticated visitors are redirected to `/login/?next=/profile/`.
18. Displays: user's name, email, join date (Jalali formatted).
19. Entry point for personalised features — in v12 this is a simple info page; reading list link added in v13.
20. Header nav: when logged in, the auth nav area shows the user's name + a "خروج" link. When logged out, it shows "ورود" and "ثبت‌نام" links.

### Password Reset

21. `GET /forgot-password/`: form with a single ایمیل field and a "ارسال لینک بازیابی" button.
22. On submit: if the email exists, a password reset email is sent with a time-limited signed token (1 hour expiry). If the email does not exist, the same success message is shown — no email enumeration.
23. Success message: "اگر این ایمیل در سیستم ثبت شده باشد، لینک بازیابی رمز عبور برایتان ارسال شد."
24. Reset token: a signed, time-limited token (HMAC using `SECRET_KEY`); stored in the reset URL as a query parameter. No separate DB table needed.
25. `GET /reset-password/?token=…`: renders the new password form (رمز عبور جدید + تکرار). Invalid or expired token shows: "لینک بازیابی نامعتبر یا منقضی شده است."
26. On valid reset: password updated, token invalidated (by expiry — single-use not enforced in v12), user redirected to `/login/` with: "رمز عبور با موفقیت تغییر یافت. وارد شوید."
27. **Password reset requires an email provider.** See Open Questions. If no email provider is configured, this feature is disabled and the forgot-password form shows: "بازیابی رمز عبور در حال حاضر در دسترس نیست."

### Admin User List (`/admin/users/`)

28. New **"کاربران"** entry appears in the admin sidebar.
29. Table columns: نام, ایمیل (LTR), تاریخ عضویت (Jalali), وضعیت (فعال / غیرفعال).
30. Summary line: "**X** کاربر ثبت‌نام‌شده".
31. Deactivate button per row (active users only); reactivate button for deactivated users.
32. Pagination: 50 rows per page.
33. No password reset or edit actions from the admin panel — admin is not a user manager beyond activation status.

---

## Auth Guard

A dependency `get_current_user(request)` is added to `app/core/` — mirrors the existing `_guard_admin` pattern but for public users:

- Reads the signed session cookie.
- Returns the `User` record if valid and active.
- Returns `None` if no session or session is invalid.
- Routes that require auth redirect to `/login/?next={current_path}` if `get_current_user` returns `None`.

The existing admin auth is completely unchanged.

---

## NFRs

### Security
- Passwords hashed with bcrypt (cost factor ≥ 12).
- Session cookie: `httponly=True`, `samesite="lax"`, `secure=True` in production (`DEBUG=False`).
- Reset tokens are HMAC-signed and time-limited (1 hour). No plain tokens stored in the DB.
- Rate limiting on register and login endpoints.
- Honeypot on registration form.
- Email enumeration prevented on login, forgot-password, and duplicate registration responses.

### RTL / Persian
- All public-facing copy, error messages, and form labels are in Persian and RTL.
- Emails and dates rendered `dir="ltr"`.
- Auth pages (`/register/`, `/login/`, `/profile/`, `/forgot-password/`) follow the same layout and RTL conventions as all other public pages.

### Performance
- Auth check (session cookie read + user DB lookup) adds one DB query per request on authenticated routes. Acceptable at current scale.
- No caching of user sessions in v12 — straightforward DB lookup.

---

## Out of Scope (v12)

- Social login (Google, GitHub) — deferred; adds OAuth complexity.
- Email verification / confirm-your-email flow — deferred; adds friction. Revisit if spam accounts become a problem.
- Two-factor authentication.
- User-editable profile (change name, email, password) — deferred to v13+.
- Account deletion / right-to-erasure flow — deferred.
- Reading list, bookmarks, or any other personalised feature — those are v13+; v12 is auth infrastructure only.
- Admin: editing user data, resetting passwords, viewing user activity.

---

## Open Questions

| Question | Decision |
|----------|----------|
| Email provider for password reset? | Resend is recommended — simplest API, Persian-friendly SMTP, generous free tier. Coordinate with Newsletter epic (v11) to share the same provider. If no provider is set up when v12 ships, disable the forgot-password flow gracefully. |
| Social login (Google)? | Deferred — email-only for v12. Social can be added as a parallel login path in v13+ without breaking the email-password flow. |
| Should registration require email verification? | No for v12 — single step, lower friction. Add if spam accounts become a problem. |
| Display logged-in user name in the header nav? | Yes — show name + logout link. Decision: show the full name or just "حساب من"? Recommend full name for personal feel. |
| Should the admin see when a user last logged in? | Deferred — would require a `last_login_at` column and update on every login. Not needed for v12. |

---

## Dependencies

| Dependency | Notes |
|------------|-------|
| `passlib[bcrypt]` | Add to `requirements.txt` |
| Email provider (Resend or equivalent) | Required for password reset only; rest of v12 works without it |
| `SECRET_KEY` env var | Already present in production; used for signing session cookies and reset tokens |

---

## Success Metrics

v12 is done when all of the following are true:

- [ ] `users` table exists in production (migration applied).
- [ ] Visitor can register at `/register/` with name, email, and password; is logged in immediately on success.
- [ ] Duplicate email registration shows the correct Persian error without creating a duplicate record.
- [ ] Visitor can log in at `/login/` with correct credentials; session cookie is set.
- [ ] Wrong credentials show the combined error message (no email/password distinction).
- [ ] "مرا به خاطر بسپار" sets a 30-day cookie; unchecked sets a session cookie.
- [ ] Logout at `POST /logout/` clears the session and redirects to home.
- [ ] `/profile/` is accessible only when logged in; unauthenticated visitors are redirected to `/login/?next=/profile/`.
- [ ] Logged-in user's name and logout link appear in the site header.
- [ ] Forgot-password form sends a reset email (or shows the graceful disabled message if no provider is configured).
- [ ] Valid reset token allows setting a new password; expired/invalid token shows the correct error.
- [ ] Admin **"کاربران"** sidebar link renders the user list with name, email, Jalali join date, and active status.
- [ ] Admin can deactivate and reactivate a user.
- [ ] Deactivated user cannot log in.
- [ ] Rate limiting is active on register and login endpoints.
- [ ] Honeypot field is present on the registration form.

---

## Deployment Status

| Field | Value |
|-------|-------|
| **Status** | Not deployed |
| **Deploy date** | — |
| **Platform** | Hamravesh Darkube (production) |
| **Notes** | Unscheduled backlog item. Ship together with v13 (Reading List) — auth alone provides no user-visible value. |

---

*July 2026 — v12 spec written. Unscheduled backlog item. Must ship with v13 (Reading List) to deliver visible user value.*
