# Product Spec v1 — پت فیچر (Library Launch)

> **Parent:** [Product overview](./product-spec.md) · **Next:** [Product Spec v2](./product-spec-v2.md) · **Diagrams:** [Use case diagram](./use-case-diagram.md)

## 1. Summary

| Field | Value |
|--------|--------|
| **Version** | v1 — Library launch |
| **Goal** | Ship a clean, fast book library with complete detail pages and an about-author page |
| **Baseline** | Current live site (library parity + improvements) |
| **Prerequisite for** | [Product Spec v2](./product-spec-v2.md) |

**Scope in one sentence:** Ship the book library and about-author page only — no learning path, blog, newsletter, contact, or community features.

---

## 2. Problem & Goals

**Problem:** The current site has incomplete book pages and legacy URLs in the library section.

**v1 goals**

- Full **Browse Book Library** with complete **View Book Details**
- **Visit About Me** — clear author and site story
- Author CMS for books and about-author content

---

## 3. Actors

| Actor | Role in v1 |
|-------|------------|
| **Visitor** | Reads book content; visits about-author page |
| **Admin (Milad Mirzaei)** | Manages library content and about-author content |

---

## 4. Target Users

| Persona | Need |
|---------|------|
| **Junior / aspiring PM** | Curated reading list with complete book notes |
| **Mid-level PM** | Book deep-dives with related resources |
| **Returning reader** | Reliable library reference |
| **Admin** | Publish and maintain book content and author bio |

---

## 5. Core Value (v1)

1. **Curated PM library** — books with topics, authors, and complete detail pages
2. **Detective-style linking** — connect books to articles, video, podcast (link out)
3. **Clear brand story** — about-author page explains "pet feature" and the author

---

## 6. Information Architecture

```
Home (/)              → entry to library and about
├── کتابخانه         → /library/
└── درباره من        → /about/
```

**Global elements**

- Header: brand + nav (library, about)
- Footer: minimal (brand, links)

---

## 7. Feature Requirements

Aligned with [use case diagram](./use-case-diagram.md) — v1 use cases only.

### 7.1 Browse Book Library

**Route:** `/library/`

| Included use case | Requirements |
|-------------------|--------------|
| **View Book Details** | Title, author, tags, summary, takeaways, related resources (book, article, video, podcast) |

**Page requirements**

- Intro explaining detective-reading approach
- Grid/list with title, author, topic tags
- Clean URLs (no legacy `/uncategorized/P45334-...` pattern)

**Sample books to migrate:** الهام گرفته، قلاب، صفر به یک، اندازه‌گیری آنچه مهم است، تحلیل ناب، استراتژی محصول، و غیره.

### 7.2 Visit About Me

**Route:** `/about/`

| Item | Detail |
|------|--------|
| **Content** | Pet feature definition, about site, about author (Milad Mirzaei) |
| **Managed by** | Admin via CMS |
| **Includes** | Author bio, site mission, optional photo/links |

### 7.3 Home

- Hero: پت فیچر + tagline
- Entry points: کتابخانه، درباره من
- Brief pet feature definition (or link to about page)

### 7.4 Admin (backend / CMS)

| Feature | Description |
|---------|-------------|
| **Manage Library Content** | CRUD books, tags, related resources |
| **Manage About Author Content** | Edit about-author page content (bio, mission, site story) |

---

## 8. Content Model (v1)

| Entity | Key fields |
|--------|------------|
| **Book** | title, author, slug, cover, tags[], status, body, related_resources[] |
| **Resource** | type (book/article/video/podcast/file), title, url, linked_books[] |
| **About page** | sections[] (title, body), author_name, author_bio, optional_links[] |

**Relationship principle:** Books ↔ resources form a knowledge graph within the library.

---

## 9. Non-Functional Requirements

| Area | Requirement |
|------|-------------|
| **RTL & Persian typography** | Native RTL; readable Farsi fonts |
| **SEO** | Title: `{Page} \| پت فیچر \| دانشنامه یک مدیر محصول`; basic meta for book pages |
| **Performance** | Fast static/SSR pages; optimized images |
| **Mobile** | Fully responsive |
| **Accessibility** | Semantic HTML, contrast |
| **Authoring** | MDX, headless CMS, or admin |
| **Analytics** | Traffic, time on book pages |

---

## 10. Out of Scope (v1)

Deferred to [v2](./product-spec-v2.md) or later:

- Learning path (مسیر)
- Blog and social sharing
- Newsletter subscription
- Contact form
- User registration / login
- Post reactions and comments
- Book comments
- Comment moderation
- Full-text search
- Paid content / paywall
- English version
- Podcast/video hosting (link out only in book resources)
- Mobile app

---

## 11. Gaps Fixed from Current Site

| Current gap | v1 fix |
|-------------|--------|
| Incomplete book detail pages | Full View Book Details |
| Legacy book URLs | Clean slugs |
| Scattered about/author info | Dedicated Visit About Me page |
| Sitemap / routing errors in library | Greenfield library rebuild |

---

## 12. Success Metrics

| Metric | Why it matters |
|--------|----------------|
| Return visitors | Useful reference site |
| Time on book pages | Content resonates |
| Library completeness | % of books with full detail + links |

---

## 13. Technical Direction (TBD)

- Framework: Next.js / Astro + MDX or CMS
- Design: Persian RTL design system
- Migration: curated books from current site

---

## 14. Open Questions (v1)

1. **Stack** — Next.js + MDX, Astro, or other?
2. **Migration scope** — all current books or curated subset?
3. **About page structure** — single page vs tabbed sections?
4. **Home page depth** — minimal landing vs richer preview of library?

---

*v1 spec — June 2026*
