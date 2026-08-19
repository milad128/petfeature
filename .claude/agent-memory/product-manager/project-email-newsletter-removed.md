---
name: project-email-newsletter-removed
description: Email newsletter removed from petfeature.ir in July 2026 — no Subscriber model, no email collection; Telegram is the only subscription channel
metadata:
  type: project
---

The **email newsletter is removed from the product** (decided July 2026). There is no email subscriber form, no `Subscriber` model, and no `/admin/subscribers/` page. `@petfeature` on Telegram is the single subscription channel.

**Why:** Iranian market open rates on Telegram are ~60–80% vs ~15–25% for email, with no deliverability problems and no list to maintain. Running both channels was overhead for the weaker one.

**What stays:** v11.5 (Telegram join strip in the footer) and v13 (AI-drafted Telegram digest, `NewsletterCampaign` model). v13 never depended on email — it composes a digest and sends it to Telegram. Its version name still says "Newsletter"; read that as *Telegram digest*.

**What changed in docs:** `spec-v11-newsletter.md` deleted · v14 dashboard lost its email subscribe/unsubscribe section, leaving a Telegram link + My Comments · backlog epic renamed to "Subscription → Telegram only".

**Code not yet removed at the time of the decision:** `Subscriber` model (re-created after the earlier v11 revert — the table survived), subscribe/unsubscribe routes at `POST /profile/newsletter/subscribe|unsubscribe/`, the admin subscribers page, and the `subscribers` DB table. Removing these needs a drop-table migration. See [[project-v11.5-telegram-channel]].
