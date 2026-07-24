# Product Spec v13.5 — Telegram Subscription Popup (پاپ‌آپ کانال تلگرام)

**Version:** v13.5
**Status:** Shipped
**Author:** Milad Mirzaei
**Date:** July 2026
**Depends on:** v11.5 (Telegram channel live)
**No new DB model. No auth required.**

---

## Overview

After a visitor spends 30 seconds on any public page, a modal popup appears inviting them to join the @petfeature Telegram channel. Once the visitor either closes the popup or clicks the join button, the popup never appears again — stored in `localStorage`, no server-side tracking.

This is a pure frontend feature: one JS snippet + one CSS modal. No route, no model, no migration.

---

## Problem Statement

The Telegram channel join strip in the footer (v11.5) is passive — only visitors who scroll to the bottom see it. Most visitors leave without ever noticing it. The popup creates an active, timed prompt that captures attention without blocking the initial reading experience (30-second delay = after the visitor has shown genuine interest).

---

## User Stories

- *As a visitor, I want to be invited to join the Telegram channel after I've had a chance to explore the site so that the prompt doesn't feel intrusive.*
- *As a visitor, I want the popup to never appear again once I've seen it so that it doesn't interrupt repeat visits.*
- *As the site owner, I want to grow the Telegram channel without annoying regular readers.*

---

## Acceptance Criteria

### Trigger
- [ ] Popup appears **30 seconds** after the page finishes loading (`DOMContentLoaded` + `setTimeout(30000)`)
- [ ] Popup appears on **all public pages** (home, library, book detail, blog, post detail, tools, tool detail, about, contact)
- [ ] Popup does **not** appear on any `/admin/` page
- [ ] Popup does **not** appear if `localStorage.getItem('pf_tg_popup_seen')` is set to `'1'`

### Popup content
- [ ] Modal overlay (semi-transparent dark background, RTL)
- [ ] Close button (×) in the top-left corner
- [ ] Telegram icon or logo
- [ ] Persian headline: **"در کانال تلگرام ما باشید"**
- [ ] Persian body: **"یادداشت تازه، کتاب جدید، ابزار کاربردی — اول در کانال."**
- [ ] Primary CTA button: **"عضویت در کانال @petfeature"** → opens `https://t.me/petfeature` in a new tab (`target="_blank" rel="noopener"`)
- [ ] Secondary link below button: **"بعداً"** (no styling — plain text link)

### Dismiss behaviour
- [ ] Clicking the × button → closes popup → sets `localStorage.pf_tg_popup_seen = '1'`
- [ ] Clicking "بعداً" → closes popup → sets `localStorage.pf_tg_popup_seen = '1'`
- [ ] Clicking the CTA button → opens Telegram in new tab → closes popup → sets `localStorage.pf_tg_popup_seen = '1'`
- [ ] Clicking the overlay background → closes popup → sets `localStorage.pf_tg_popup_seen = '1'`
- [ ] After any of the above, popup **never appears again** on this browser
- [ ] Pressing `Escape` key → same as clicking ×

### Accessibility & UX
- [ ] Popup traps keyboard focus while open (tabbing stays within modal)
- [ ] `aria-modal="true"` and `role="dialog"` on the modal element
- [ ] `aria-label` on close button: "بستن"
- [ ] Body scroll is locked while popup is open; restored on close
- [ ] Animation: fade-in over 200ms; fade-out over 150ms on dismiss
- [ ] Fully responsive — centred on desktop; full-width with padding on mobile

---

## Implementation

### JS (inline in `base.html` or a small `popup.js` file)

```javascript
(function () {
  const STORAGE_KEY = 'pf_tg_popup_seen';
  if (localStorage.getItem(STORAGE_KEY)) return;
  if (window.location.pathname.startsWith('/admin/')) return;

  function dismiss() {
    localStorage.setItem(STORAGE_KEY, '1');
    document.getElementById('tg-popup').classList.add('tg-popup--hidden');
    document.body.style.overflow = '';
  }

  setTimeout(function () {
    var popup = document.getElementById('tg-popup');
    popup.classList.remove('tg-popup--hidden');
    document.body.style.overflow = 'hidden';

    popup.querySelector('.tg-popup__overlay').addEventListener('click', dismiss);
    popup.querySelector('.tg-popup__close').addEventListener('click', dismiss);
    popup.querySelector('.tg-popup__later').addEventListener('click', dismiss);
    popup.querySelector('.tg-popup__join').addEventListener('click', dismiss);
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') dismiss();
    });
  }, 30000);
})();
```

### HTML (added to `base.html`, hidden by default)

```html
<div id="tg-popup" class="tg-popup tg-popup--hidden" role="dialog" aria-modal="true" aria-labelledby="tg-popup-title">
  <div class="tg-popup__overlay"></div>
  <div class="tg-popup__box">
    <button class="tg-popup__close" aria-label="بستن">×</button>
    <div class="tg-popup__icon">✈️</div>
    <h2 id="tg-popup-title" class="tg-popup__title">در کانال تلگرام ما باشید</h2>
    <p class="tg-popup__body">یادداشت تازه، کتاب جدید، ابزار کاربردی — اول در کانال.</p>
    <a class="tg-popup__join" href="https://t.me/petfeature" target="_blank" rel="noopener">
      عضویت در کانال @petfeature
    </a>
    <a class="tg-popup__later" href="#">بعداً</a>
  </div>
</div>
```

### Files to touch

| File | Change |
|------|--------|
| `app/templates/base.html` | Add popup HTML + script tag |
| `app/static/css/main.css` | Add `.tg-popup` styles |

**No new route. No new model. No migration.**

---

## Out of Scope

| Item | Reason |
|------|--------|
| Email capture in popup | User said Telegram only |
| Popup on admin pages | Admin doesn't need this prompt |
| A/B testing popup timing | Not needed at current scale |
| Server-side "seen" tracking | localStorage is sufficient — simpler, zero latency |
| Countdown timer visible to user | Unnecessary friction |
| Different copy per page type | One message covers all pages |

---

## Effort Estimate

| Task | Estimate |
|------|----------|
| HTML modal structure in `base.html` | 30 min |
| CSS (overlay, box, animations, responsive) | 1 hour |
| JS (timer, dismiss, localStorage) | 30 min |
| QA (keyboard, mobile, repeat visit) | 30 min |
| **Total** | **~2.5 hours** |
