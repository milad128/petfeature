---
name: project-v13.5-telegram-popup
description: v13.5 Telegram Popup — 30s delay modal inviting visitors to join @petfeature; localStorage dismiss (pf_tg_popup_seen); pure JS+CSS; no DB; ~2.5 hours; backlog
metadata:
  type: project
---

v13.5 adds a timed Telegram channel subscription popup to all public pages.

**Status:** Backlog

**Key decisions:**
- 30 second delay after DOMContentLoaded (visitor has shown genuine interest)
- `localStorage.pf_tg_popup_seen = '1'` on any dismiss — never shows again on that browser
- Dismiss triggers: × button, "بعداً" link, overlay click, CTA button click, Escape key
- CTA opens `https://t.me/petfeature` in new tab AND dismisses popup
- No DB, no server, no migration — pure frontend
- Does NOT show on `/admin/` pages
- Body scroll locked while popup is open

**Files to touch:** `app/templates/base.html`, `app/static/css/main.css`

**Effort:** ~2.5 hours

**Depends on:** v11.5 (channel must exist). [[project-v11.5-telegram-channel]]
