# Product Spec v2 — پت فیچر (Full Site + Community)

> **Prerequisite:** [Product Spec v1](./product-spec-v1.md) must be shipped first · **Parent:** [Product overview](./product-spec.md) · **Diagrams:** [Use case diagram](./use-case-diagram.md)

## 1. Summary

| Field | Value |
|--------|--------|
| **Version** | v2 — Full site + community release |
| **Goal** | Add learning path, blog, newsletter, contact, social sharing, and authenticated engagement on top of the v1 library |
| **Builds on** | [Product Spec v1](./product-spec-v1.md) |
| **New in v2** | Path, blog, newsletter, contact, share, register, auth, reactions, comments, moderation |

**Scope in one sentence:** Complete the remake (path, blog, newsletter, contact, sharing) and let registered users react and comment while the admin moderates discussion.

---

## 2. Problem & Goals

**Problem:** v1 ships only the library and about page. Readers still need the learning path, essays, newsletter, and contact — and cannot participate in discussions.

**v2 goals**

- **Browse Learning Path** with **View Path Content**
- **Browse Blog** with **Read Blog Posts** and **Share to Social Networks**
- Reliable **Subscribe to Newsletter** and **Contact** flows
- **Register** and **Authenticate** users
- **Make Reaction** and **Comment on Post** when browsing blog
- **Read Book Comments** (and post when logged in) when browsing library
- **Moderate Comments** for the admin
- Admin CMS extensions for path, blog, newsletter, and contact

---

## 3. Actors

| Actor | Role in v2 |
|-------|------------|
| **Visitor** | All v1 capabilities plus path, blog, newsletter, contact, share; may register to unlock engagement |
| **Registered user** | Authenticated visitor; can react, comment on posts, comment on books |
| **Admin (Milad Mirzaei)** | All v1 admin capabilities plus path, blog, newsletter, contact; moderates comments |
| **Email service** | Newsletter signup, contact delivery, outbound newsletter |
| **Social networks** | External share targets (LinkedIn, X, Telegram, etc.) |

---

## 4. Target Users

| Persona | Need |
|---------|------|
| **Junior / aspiring PM** | Reading lists, learning path, practical essays |
| **Mid-level PM** | Book deep-dives, cross-linked resources |
| **Returning reader** | Newsletter updates, shareable posts |
| **Engaged reader** | React to posts, join discussions |
| **Book learner** | Read and contribute book comments |
| **PM community in Iran** | Persian content, curated sources |
| **Admin** | Publish notes, grow library, collect emails, moderate community |

---

## 5. Core Value (v2)

1. **Learning path (مسیر)** — structured steps linking books and posts
2. **Personal essays (بلاگ)** — stories and lessons from real PM work
3. **Newsletter** — free updates when new resources are added
4. **Social sharing** — share posts to external networks
5. **Community** — reactions and comments on blog posts
6. **Book discussions** — comments on library pages
7. **Registered identity** — one account for all engagement actions
8. **Moderated quality** — admin controls visible discussion

---

## 6. Information Architecture (additions)

Extends [v1 IA](./product-spec-v1.md#6-information-architecture):

```
Home (/)
├── مسیر          → /path/          (new in v2)
├── بلاگ          → /blog/          (new in v2)
├── کتابخانه     → /library/       (from v1)
├── درباره من    → /about/          (from v1)
├── خبرنامه       → /newsletter/    (new in v2)
└── تماس          → /contact/       (new in v2)

/register/     → Create account
/login/        → Sign in
/logout/       → End session
/account/      → Profile (optional v2.1)
```

**Global additions**

- Expanded nav: مسیر، بلاگ، خبرنامه، تماس
- Footer newsletter CTA (single strong CTA; avoid repeating on every section)
- Auth entry in header: login / register
- Reaction and comment UI on blog post pages
- Comment section on book detail pages

---

## 7. Feature Requirements

Aligned with [use case diagram](./use-case-diagram.md) — v2 use cases only.

### 7.1 Subscribe to Newsletter

| Item | Detail |
|------|--------|
| **Route** | `/newsletter/` + footer CTA |
| **Fields** | نام و نام‌خانوادگی، ایمیل |
| **Includes** | Validate form, show success message |
| **Integration** | Email service (provider TBD) |
| **Success copy** | «با موفقیت در خبرنامه عضو شدید» |

### 7.2 Contact

| Item | Detail |
|------|--------|
| **Route** | `/contact/` |
| **Fields** | نام، ایمیل، پیام |
| **Includes** | Validate form, show success message |
| **Extras** | LinkedIn link to author; optional book-tip messages |
| **Admin** | Receive via email/admin |

### 7.3 Browse Learning Path

**Route:** `/path/`

| Included use case | Requirements |
|-------------------|--------------|
| **View Path Content** | Ordered steps, descriptions, links to books and posts |

**Page requirements**

- Dedicated route (replaces unclear current nav destination)
- Admin-managed steps via CMS
- Links into library and blog content

### 7.4 Browse Blog

**Route:** `/blog/`

| Included use case | Requirements |
|-------------------|--------------|
| **Read Blog Posts** | List + full post; Jalali dates |
| **Share to Social Networks** | Share buttons; Open Graph metadata |

**Page requirements**

- Reverse-chronological list: title, date, excerpt
- Post page: full essay, clean slug URLs
- Share to LinkedIn, X, Telegram, etc.

**Sample posts to migrate:**

- تارگت 10X رو دیدی، کدو رو ندیدی؟
- کتابی که داشت جون منو نجات میداد
- فرمول تبدیل شدن به بدترین مدیر محصول!
- با این تکنیک کتاب بعدی را برای خواندن انتخاب کنید

### 7.5 Home (v2 expansion)

- Entry points: مسیر، بلاگ، کتابخانه، درباره من
- Pet feature definition
- Newsletter CTA

### 7.6 Register

| Item | Detail |
|------|--------|
| **Route** | `/register/` |
| **Includes** | Authenticate (session created on success) |
| **Fields** | TBD: email + password, magic link, or OAuth |
| **Acceptance** | User can sign up and land logged in |

### 7.7 Authenticate

| Item | Detail |
|------|--------|
| **Routes** | `/login/`, `/logout/` |
| **Required for** | Make Reaction, Comment on Post, post Book Comments |
| **Extend behavior** | Unauthenticated users prompted to login when attempting these actions |
| **Acceptance** | Secure session; persisted across visits |

### 7.8 Browse Book Library — v2 additions

Extends v1 **Browse Book Library**:

| Included use case | Requirements |
|-------------------|--------------|
| **Read Book Comments** | Display comments on book detail pages |
| **Post book comment** | Logged-in users can add comments (extends Authenticate) |

**Rules**

- Reading comments: public (or public when approved only — TBD)
- Posting comments: requires auth
- New comments: pre-moderation or post-moderation (TBD)

### 7.9 Browse Blog — v2 additions

Extends **Browse Blog** (Read Posts + Share):

| Included use case | Requirements |
|-------------------|--------------|
| **Make Reaction** | Lightweight reaction on post (like / helpful — type TBD) |
| **Comment on Post** | User comment on essay |

**Rules**

- Both require auth (extend Authenticate)
- One reaction per user per post (TBD)
- Comments subject to moderation policy

### 7.10 Moderate Comments (Admin)

| Item | Detail |
|------|--------|
| **Access** | Admin-only |
| **Actions** | Approve, reject, delete comments |
| **Targets** | Book comments and post comments |
| **Queue** | Pending comments if pre-moderation |

### 7.11 Admin (backend / CMS) — v2 additions

Extends v1 admin capabilities:

| Feature | Description |
|---------|-------------|
| **Manage Learning Path** | CRUD path steps and links |
| **Manage Blog Posts** | CRUD posts |
| **Receive Contact Messages** | Inbound contact via email/admin |
| **Send Newsletter** | Email subscribers when content is added |

---

## 8. Content Model (v2 additions)

New entities on top of [v1 content model](./product-spec-v1.md#8-content-model-v1):

| Entity | Key fields |
|--------|------------|
| **Post** | title, slug, date, excerpt, body, tags[], related_books[] |
| **Path step** | title, order, description, linked_books[], linked_posts[] |
| **Subscriber** | name, email, subscribed_at |
| **Message** | name, email, body, type (contact/tip), created_at |
| **User** | name, email, password_hash, created_at |
| **Comment** | user_id, target_type (book \| post), target_id, body, status (pending \| approved \| rejected), created_at |
| **Reaction** | user_id, post_id, type, created_at |

**Relationships**

- Books ↔ resources ↔ posts ↔ path steps form a knowledge graph
- User → many Comments, many Reactions
- Comment → Book or Post (polymorphic target)
- Reaction → Post (unique per user per post, TBD)

---

## 9. Non-Functional Requirements (v2)

| Area | Requirement |
|------|-------------|
| **SEO** | OG tags for blog share |
| **Analytics** | Newsletter conversion, share clicks |
| **Auth security** | Hashed passwords, secure cookies/JWT, CSRF protection |
| **Rate limiting** | Throttle comment and registration endpoints |
| **Spam protection** | Honeypot, rate limits; optional CAPTCHA |
| **Moderation** | Admin queue; audit log for approve/delete |
| **Privacy** | Minimal PII; clear data retention policy |

---

## 10. Out of Scope (v2)

| Item | Notes |
|------|-------|
| Full-text search | Post-v2 |
| Real-time chat | Not planned |
| User profiles / avatars | Optional v2.1 |
| Nested comment threads | Flat comments in v2; threading later |
| Email notifications on reply | Optional v2.1 |
| English version | Unless requested |
| Mobile app | Web only |

---

## 11. Gaps Fixed from Current Site (v2)

| Current gap | v2 fix |
|-------------|--------|
| مسیر nav with no clear page | `/path/` with View Path Content |
| Repeated newsletter forms | Consolidated CTA strategy |
| Legacy blog URLs | Clean slugs |
| No share flow | Share to Social Networks on blog |

---

## 12. Success Metrics

| Metric | Why it matters |
|--------|----------------|
| Newsletter signups | Core growth loop |
| Return visitors | Useful reference site |
| Time on book/post pages | Content resonates |
| Share clicks | Organic reach |
| Registered users | Community adoption |
| Comments per post / book | Engagement depth |
| Reactions per post | Low-friction engagement |
| Moderation queue clearance time | Healthy community |
| Spam / abuse rate | Safety |

---

## 13. Technical Direction (TBD)

- Email: Buttondown, Mailchimp, Resend, etc.
- Auth: session cookies or JWT
- Database tables: users, comments, reactions, subscribers, messages
- Admin UI: moderation queue in CMS or custom panel
- API routes: register, login, comment CRUD, reaction toggle, newsletter, contact
- Migration: posts, path content from current site; no user data (greenfield)

---

## 14. Dependency on v1

v2 assumes v1 provides:

- Book library with full detail pages
- About-author page and CMS
- Production deployment and domain

Do not start v2 implementation until v1 is live and stable.

---

## 15. Open Questions (v2)

1. **Learning path shape** — skill map, reading order, or career timeline?
2. **Newsletter tool** — which provider?
3. **Newsletter CTA placement** — footer only vs dedicated page + one inline CTA?
4. **Auth method** — email/password, magic link, or OAuth (Google/LinkedIn)?
5. **Comment policy** — pre-moderation vs post-moderation?
6. **Reaction types** — single like or multiple types?
7. **Book comments** — public read of pending comments or approved-only?
8. **User display name** — real name, nickname, or email-derived?
9. **Account deletion** — self-service or contact admin?

---

*v2 spec — June 2026*
