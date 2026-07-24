# Product Spec v12 — User Auth via Google Login (احراز هویت با گوگل)

**Version:** v12
**Status:** Backlog
**Author:** Milad Mirzaei
**Date:** July 2026
**Depends on:** v1–v13
**Unlocks:** Reading List (v14+), personalised features

---

## Overview

v12 introduces user authentication via **Google OAuth 2.0 only** — no email/password, no registration form, no SMTP required. Visitors click "ورود با گوگل", authorise on Google's servers, and return to petfeature.ir as a logged-in user. Their Google name and email are stored on first login (auto-registration).

**Why Google-only:**
- No SMTP server available — password reset via email is not feasible
- Persian-speaking PM audience universally has Google accounts
- Google handles identity verification — no bcrypt, no honeypot, no rate limiting on registration
- One auth method means half the code and zero password-management edge cases

**Scope decision (Option C):** v12 ships standalone — no Reading List or other personalised features bundled. The profile page will be minimal (name, email, join date). This is an accepted gap; do not promote user registration sitewide until Reading List (v14+) ships.

---

## Problem Statement

petfeature.ir has no persistent user identity. All interactions (ratings, comments) are tied to an ephemeral visitor cookie. To support personalised features — reading list, bookmarks, saved state — the site needs a real user account.

Password-based auth requires an SMTP provider for password reset, adding operational complexity. Google Login eliminates this entirely while delivering higher trust and lower friction for the target audience.

---

## Target Users

- **Visitor:** A Persian-speaking PM who wants to save their reading progress across sessions. Clicks one button to log in with their existing Google account.
- **Admin (Milad):** Needs to see the registered user base — count and join dates — without managing passwords or account issues.

---

## User Stories

| # | As a… | I want to… | So that… |
|---|-------|-----------|---------|
| U1 | Visitor | Log in with my Google account | I don't have to create yet another username and password |
| U2 | Visitor | Be automatically registered on first login | I don't have to fill out a separate sign-up form |
| U3 | Visitor | Log out | My session is cleared on shared devices |
| U4 | Registered user | See my profile page | I can confirm my account and access future personalised features |
| U5 | Registered user | See my name in the site header when logged in | I know I'm logged in |
| U6 | Admin | See a list of registered users with name, email, and join date | I have visibility into the user base |
| U7 | Admin | Deactivate a user account | I can handle abuse without deleting data |

---

## Auth Flow

```
Visitor clicks "ورود با گوگل" on /login/ or site header
    │
    ▼
Redirect to Google OAuth consent screen
    │
    ▼ (user grants permission)
Google redirects to /auth/google/callback/?code=...
    │
    ▼
Server exchanges code for tokens → gets user's email + name from Google
    │
    ├── User exists in DB? → update name if changed → log in
    │
    └── New user? → create User record → log in (auto-registration)
    │
    ▼
Set signed session cookie → redirect to /profile/
    (or to ?next= param if present)
```

---

## Data Model

### `User`

| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | |
| `name` | String(200) | From Google profile; updated on each login |
| `email` | String(300) UNIQUE | From Google; lowercased |
| `google_id` | String(200) UNIQUE | Google's `sub` claim — primary identity key |
| `is_active` | Boolean default=True | False = deactivated by admin |
| `created_at` | DateTime server_default=now() | First login = registration date |

**No `hashed_password` column** — Google handles authentication entirely.

**Session management:** Signed session cookie using existing `SECRET_KEY`. `httponly=True`, `samesite="lax"`, `secure=True` in production. Lifetime: 30 days (always persistent — no "remember me" toggle needed with OAuth).

**Migration required:** `alembic revision --autogenerate -m "add users table"`

---

## Pages & Routes

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/login/` | Login page — single "ورود با گوگل" button |
| `GET` | `/auth/google/` | Initiate OAuth flow — redirect to Google |
| `GET` | `/auth/google/callback/` | Handle OAuth callback; create/update user; set session |
| `POST` | `/logout/` | Clear session cookie; redirect to home |
| `GET` | `/profile/` | User profile page (auth required) |
| `GET` | `/admin/users/` | Admin user list |
| `POST` | `/admin/users/{id}/deactivate/` | Deactivate user |
| `POST` | `/admin/users/{id}/reactivate/` | Reactivate user |

---

## Acceptance Criteria

### Login (`/login/`)
- [ ] Page shows a single "ورود با گوگل" button; no email/password form
- [ ] If user is already logged in, redirect to `/profile/`
- [ ] "ورود" and "ثبت‌نام" links in the site header both point to `/login/` — Google handles both flows

### OAuth callback (`/auth/google/callback/`)
- [ ] Valid code → exchange for tokens → fetch email + name + google_id from Google userinfo endpoint
- [ ] If `google_id` exists in DB → update `name` if changed → create session → redirect
- [ ] If `google_id` not found → create new `User` record → create session → redirect to `/profile/`
- [ ] If user's `is_active=False` → do not create session → redirect to `/login/` with error: "حساب کاربری شما غیرفعال شده است."
- [ ] Invalid or expired OAuth state → redirect to `/login/` with error: "خطا در ورود. لطفاً دوباره امتحان کنید."
- [ ] OAuth `state` parameter used to prevent CSRF on the callback

### Logout
- [ ] `POST /logout/` clears session cookie and redirects to `/`
- [ ] Uses POST not GET (prevents logout via external link)

### Profile (`/profile/`)
- [ ] Unauthenticated visitors redirected to `/login/?next=/profile/`
- [ ] Displays: user's name, email (LTR), join date in Jalali
- [ ] A placeholder section for future features: "قابلیت‌های بیشتر به زودی اضافه می‌شن"
- [ ] Header shows user's name + "خروج" link when logged in

### Admin user list (`/admin/users/`)
- [ ] New "کاربران" entry in admin sidebar
- [ ] Table: نام, ایمیل (LTR), تاریخ عضویت (Jalali), وضعیت (فعال / غیرفعال)
- [ ] Summary: "**X** کاربر ثبت‌نام‌شده"
- [ ] Deactivate / reactivate button per row
- [ ] Pagination: 50 per page

---

## Technical Setup (one-time)

### Google Cloud Console
1. Create a project at [console.cloud.google.com](https://console.cloud.google.com)
2. Enable **Google+ API** (or People API)
3. Create OAuth 2.0 credentials → Web application
4. Add authorised redirect URI: `https://petfeature.ir/auth/google/callback/`
5. Copy `client_id` and `client_secret` → add to Hamravesh env vars

### New env vars

| Variable | Notes |
|----------|-------|
| `GOOGLE_CLIENT_ID` | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | From Google Cloud Console |
| `GOOGLE_REDIRECT_URI` | `https://petfeature.ir/auth/google/callback/` |

### Library

**`authlib`** — the standard OAuth library for FastAPI/Starlette. Add to `requirements.txt`:
```
authlib>=1.3.0
```

### Auth guard

`get_current_user(request) -> User | None` dependency in `app/core/`:
- Reads signed session cookie → looks up `User` by id
- Returns `User` if valid and active, `None` otherwise
- Protected routes redirect to `/login/?next={path}` if `None`
- Existing admin auth (`_guard_admin`) is completely unchanged

---

## New Files

| File | Purpose |
|------|---------|
| `app/models/user.py` | `User` model |
| `app/services/users.py` | `get_or_create_user(google_id, email, name)`, `get_user_by_id()` |
| `app/core/auth.py` | `get_current_user()` dependency; session read/write helpers |
| `app/web/auth_routes.py` | `/login/`, `/logout/`, `/profile/`, `/auth/google/`, `/auth/google/callback/` |
| `app/templates/pages/login.html` | Login page with Google button |
| `app/templates/pages/profile.html` | User profile page |
| `app/templates/admin/users_list.html` | Admin user list |

## Modified Files

| File | Change |
|------|--------|
| `app/core/config.py` | Add `google_client_id`, `google_client_secret`, `google_redirect_uri` |
| `app/main.py` | Register auth router |
| `app/templates/base.html` | Auth nav area — show name + logout when logged in; "ورود" when logged out |
| `app/templates/admin/base.html` | Add "کاربران" nav item |
| `alembic/env.py` | Import `User` model |

---

## Out of Scope (v12)

| Item | Reason |
|------|--------|
| Email/password login | No SMTP; Google Login eliminates the need |
| Password reset | Not applicable — no passwords |
| Email verification | Google already verified the email |
| Reading List, bookmarks, personalised features | v14+ — v12 is auth infrastructure only |
| User-editable profile (change name/email) | Name + email come from Google; changing them here has no value |
| Account deletion / right-to-erasure | Deferred |
| Social login beyond Google (GitHub, etc.) | One provider is enough for this audience |
| Two-factor authentication | Google handles 2FA on their side |

---

## NFRs

- `GOOGLE_CLIENT_SECRET` must never appear in templates, logs, or HTML responses
- OAuth `state` parameter must be validated on callback to prevent CSRF
- Session cookie: `httponly=True`, `samesite="lax"`, `secure=True` in production
- All public-facing copy is in Persian, RTL; emails displayed `dir="ltr"`
- Auth check adds one DB query per request on protected routes — acceptable at current scale

---

## Open Questions

| Question | Decision |
|----------|---------|
| Should the header show "ورود" or both "ورود" + "ثبت‌نام"? | One "ورود با گوگل" button is enough — Google handles both new and returning users |
| Should login persist across sessions always, or ask user? | Always persistent (30 days) — no toggle needed with OAuth |
| What if Google changes the user's email? | Update email on each login using `google_id` as the stable key |

---

## Known Gap (Option C decision)

The profile page in v12 is minimal — name, email, join date, and a placeholder. Users who register will see no personalised features. This is an accepted trade-off.

**Do not add "ثبت‌نام کن" CTAs across the site until Reading List (v14+) ships.** Registration without a reason to register creates a poor first impression that is hard to recover from.

---

## Effort Estimate

| Task | Estimate |
|------|----------|
| Google Cloud Console setup | 30 min (one-time) |
| `User` model + migration | 1 hour |
| `authlib` OAuth flow (initiate + callback) | 4 hours |
| Session management (`get_current_user` dependency) | 2 hours |
| Login page + header auth nav | 2 hours |
| Profile page | 1 hour |
| Logout | 30 min |
| Admin user list + deactivate/reactivate | 2 hours |
| Config + env vars + wiring | 1 hour |
| **Total** | **~2 days** |

---

*July 2026 — v12 revised: Google Login only (no email/password, no SMTP needed). Ships standalone (Option C); profile page is minimal until Reading List (v14+).*
