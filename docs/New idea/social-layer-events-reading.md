# Idea Exploration — Social Layer: Events + Social Reading

> Status: Raw idea — not committed to roadmap. Thinking through feasibility, prerequisites, and strategic fit.
> Last updated: July 2026

---

## The Two Ideas

### 1. Event Management (رویدادها)
Third-party institutes, book clubs, or PM communities post book-reading events on petfeature.ir. Visitors browse, enroll, and get notified. Milad acts as a platform — not the event organizer.

**Example:** "کانون کتاب تهران" announces a 4-week group reading of *Inspired*. They post it on petfeature, set date/capacity/link. PM readers on the site discover and enroll.

### 2. Social Reading — "الان چی می‌خونم" (Now Reading)
Like Goodreads: logged-in users share what book they're currently reading. Others can see the activity. Creates a lightweight social signal ("X نفر دارن این کتاب رو می‌خونن").

**Example:** A user marks *Continuous Discovery Habits* as "در حال خواندن". Their activity appears on the book's page and in a site-wide feed.

---

## Why These Are Interesting Together

Both ideas share the same underlying need: **a community of identifiable users who interact with content socially**, not just passively.

Right now petfeature.ir is a *library* — visitors come, read, leave. These ideas would make it a *gathering place* — people show up, connect, join things, come back.

Together they form a **lightweight social layer** on top of the existing PM encyclopedia. The strategic outcome: petfeature.ir becomes the Persian-language home for PM learners — not just a resource, but a community.

---

## What Each Feature Needs

### Event Management

| Need | Notes |
|------|-------|
| **User registration** | Organizers must have accounts to post events; attendees must register to enroll |
| **Event organizer role** | Separate from regular users — either a separate account type, or Milad manually grants organizer permission |
| **Trust + moderation** | Milad must approve events before they go live — low-quality or spam events would harm the brand |
| **Event model** | Title, description, organizer, book(s) linked, date/time, capacity, enrollment link or form |
| **Notification** | Enrolled users get reminded — requires email or Telegram Bot |
| **Calendar view** | Events need a browsable `/events/` page with upcoming events sorted by date |

### Social Reading

| Need | Notes |
|------|-------|
| **User registration** | Core dependency — anonymous visitors can't have a reading state |
| **Reading List (v14/v15)** | "Now reading" is an extension of Reading List (want/reading/read statuses) |
| **Activity feed** | A page or sidebar widget showing recent reading activity across users |
| **Privacy control** | Some users may not want their reading shared publicly — opt-in vs opt-out decision |
| **Social proof on book pages** | "X نفر الان دارن این کتاب رو می‌خونن" — a simple count on the book detail page |

---

## The Hard Prerequisite: User Base

Both features have a **chicken-and-egg problem**:

> Social features are only valuable when many people use them. But people won't register unless the features are already valuable.

Goodreads solved this by importing from Amazon book purchases. petfeature.ir doesn't have that lever.

**Realistic path:**
1. Build the audience first — through content quality, Telegram channel (@petfeature), and SEO
2. Ship User Auth (v12) + Reading List (v14/v15)
3. Once a few hundred registered users exist, social reading signals become visible and meaningful
4. Only then does "now reading" have social proof worth showing
5. Events come after — they require organizers to trust the platform has an audience worth their time

**Minimum viable audience for events to feel alive:** probably 500+ registered users. For social reading to show any signal: 100+ active readers.

---

## Strategic Fit Assessment

### Social Reading — Fits well
- Directly extends the core Library epic
- Reading List (v14/v15) is already planned — "now reading" is just one status in that model
- Social proof ("X نفر می‌خونن") adds value even at low user counts
- Low moderation burden — users manage their own lists

### Event Management — Bigger bet
- Introduces a new actor: the *event organizer* (not just reader or admin)
- Requires trust infrastructure: who can post? How are events verified?
- petfeature.ir would need to be known enough that organizers want to list events here
- Could start simpler: Milad posts events himself (not third-party organizers) — no organizer role needed
- Risk: events require consistent supply; if organizers stop posting, the page looks dead

---

## Simplified Starting Points (if building)

### Minimal Social Reading (before full social network)
- Add "در حال خواندن" status to Reading List (v14/v15)
- Show count on book detail page: "X نفر الان دارن این کتاب رو می‌خونن"
- No feed, no follows, no profiles — just a number
- **Effort:** Additive to Reading List; ~0.5 extra day
- **Value:** Immediate social proof; no network needed

### Minimal Event Management (Milad-only organizer)
- Milad posts events himself via admin CMS — no organizer accounts
- `/events/` public page listing upcoming book events
- Each event: title, book link, organizer name (text field), date, enrollment URL (external link)
- No in-platform enrollment — link out to Google Form or Eventbrite
- **Effort:** ~2 days (new Event model + admin CRUD + public list page)
- **Value:** Low risk — Milad controls quality; tests if audience cares about events
- **Later:** open to third-party organizers once platform has audience

---

## Open Questions

| Question | Why It Matters |
|----------|---------------|
| What's the minimum registered user count to make "now reading" visible and meaningful? | Determines when to ship — don't launch with 5 users |
| Should event organizers be third-party from day one, or Milad-only first? | Changes the trust model and moderation complexity entirely |
| Is the goal a full social network (follows, DMs, profiles) or just shared reading signals? | Full social = years of work; signals = weeks |
| How does petfeature.ir remain a *PM encyclopedia* if it becomes a social platform? | Risk of diluting the brand and the focused value proposition |
| Should events be online, in-person, or both? | In-person events require location data and map integration |
| What happens when no events are scheduled? | Empty `/events/` page damages credibility |

---

## Dependencies (in order)

```
v12 — User Auth
  ↓
v14/v15 — Reading List ("در حال خواندن" status)
  ↓
Social Reading signals (book detail page count)
  ↓
Activity feed / social layer
  ↓
Event Management (Milad-only first → third-party later)
```

---

## What Would Need to Be True to Prioritize This

- [ ] v12 (User Auth) shipped and 100+ registered users
- [ ] Telegram channel has significant following (1000+) — built-in audience for event announcements
- [ ] At least one external PM community/institute has expressed interest in listing events
- [ ] Reading List (v14/v15) is shipped and showing engagement

Until those conditions are met, this stays in the idea file.

---

## Related

- Reading List epic → `docs/product backlog.md`
- User Registration + Auth → `docs/spec-v12-user-auth.md`
- Telegram Channel → `docs/spec-v11.5-telegram-channel.md`
