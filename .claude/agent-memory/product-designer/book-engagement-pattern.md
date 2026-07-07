---
name: book-engagement-pattern
description: Design decisions for the star rating + comment section added to the book detail page in v4
metadata:
  type: project
---

## What was added (v4)

Two new engagement sections were added to the book detail page (`/library/{slug}/`):

1. **Star rating widget** — label «این کتاب چقدر به‌دردت خورد؟», 5 stars, average + vote count, post-vote «ممنون! ✓»
2. **Comments section** — «نظرها (N)», chronological list, empty state, form with name/email/body, post-submit success notice

## Layout decision: below the grid, full-width

The engagement sections appear BELOW the two-column `book-layout` grid (after it closes), not inside the main column. They span the full content width (1100px container).

**Why:** The book detail aside is long and sticky. Comments crammed into the main column feel narrow and secondary. Breaking below the grid gives the engagement sections proper breathing room and matches the visual weight of the content above. Also consistent with the single-column post page pattern.

**How to apply:** Any future engagement features (reactions, sharing) should also go below the grid in this full-width zone, not inside the main column.

## Star rating widget structure

```
<div style="padding:26px 28px; border-radius:14px; background:var(--surface); border:1px solid var(--border); box-shadow:var(--shadow); display:flex; align-items:center; justify-content:space-between; gap:20px; flex-wrap:wrap;">
  left: label + average line
  right: 5 star buttons + «ممنون! ✓» (sc-if)
```

- Stars: `font-size:2rem` (slightly larger than post page's 1.9rem for the wider layout)
- Default star color: `var(--border)` (gray)
- Highlighted star color: `var(--accent)`
- `applyStarStyles()` runs in `componentDidMount` and `componentDidUpdate`
- Stars are direct children of `.star-row` — `starIndex()` uses `indexOf` on `parentElement.children`

## Comment form decisions

- Name + Email: side-by-side `grid-template-columns:1fr 1fr; gap:10px` (class `comment-name-row`)
- Email field: `direction:ltr; text-align:right` — email addresses are LTR but label alignment should stay RTL-consistent
- On mobile (`max-width:820px`): `.comment-name-row` collapses to `1fr` (single column)
- Textarea: `rows="4"`, `resize:vertical`

## Post-submit comment confirmation (Option A — form stays)

- A success banner appears ABOVE the form fields: accent-bg/accent-bd styled, «نظرت ثبت شد و پس از بررسی منتشر می‌شه ✓»
- Controlled by `commentSubmitted` state boolean
- Banner auto-dismisses after 5 seconds (`clearTimeout`/`setTimeout`)
- Form fields clear on submit; form stays visible for potential second comment

**Why:** Collapsing the form after submit is frustrating if a visitor wants to submit again. Keeping the form visible with a transient success notice is the friendlier pattern.

## Empty state

- Shown via `sc-if value="{{ isEmpty }}"` when `comments.length === 0`
- Dashed border treatment: `border:1px dashed var(--border)` to signal "placeholder / inviting" vs the solid borders of populated content
- Copy: «هنوز نظری ثبت نشده — اول نفر باش!»

## Separator between grid and engagement

- `margin-top:56px; padding-top:44px; border-top:1px solid var(--border)` on the engagement wrapper
- Matches the `border-top` separator pattern used within the main column (referred books section uses `padding-top:28px; border-top:1px solid var(--border)`)

## Design file

`petfeature redesign/project/Petfeature Book Detail v4.dc.html` — preview width 1180px, height 1800px

**Related:** [[dc-file-conventions]] [[design-system-tokens]]
