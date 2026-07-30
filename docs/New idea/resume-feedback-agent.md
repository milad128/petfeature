# Idea — Resume Feedback Agent (بازخورد رزومه)

> **Status:** Raw idea — not scoped, not versioned. Captured July 2026.
> **Depends on:** v12 User Auth (logged-in users only).
> **Related:** [Personalized Learning Path](./pm-learning-roadmap.md#idea--resume-based-seniority-assessment--personalized-learning-path) — the sibling idea that reuses the same resume upload to generate a learning path.

---

## One-liner

A logged-in user uploads their resume (CV), an AI agent evaluates it, and returns structured, actionable feedback on how to improve it — as a Product Manager résumé specifically.

---

## Problem

Persian-speaking PMs (and aspiring PMs) have no trusted, PM-specific place to get honest résumé feedback. Generic resume tools aren't tuned for product roles, and asking a senior PM for a review is high-friction. petfeature.ir already has the PM audience and the content authority to fill this gap.

---

## Who it's for

- Logged-in users who are job-hunting or preparing to level up
- Aspiring PMs transitioning from adjacent roles who want to know if their résumé reads as "PM"

---

## Sketch of the flow

```
User (logged in) → /profile/resume/ → uploads résumé (PDF/DOCX)
    │
    ▼
Agent parses résumé text → evaluates against PM résumé rubric
    │
    ▼
Returns structured feedback:
    • Overall impression (1 paragraph)
    • Strengths (bullet list)
    • Gaps & weaknesses (bullet list)
    • Specific rewrite suggestions (before → after examples)
    • Missing PM signals (metrics, outcomes, scope, discovery language)
    │
    ▼
Feedback shown on-page; optionally saved to the user's dashboard to revisit
```

---

## What the agent evaluates (draft rubric)

- **Outcome language** — does it show impact/metrics, or just list responsibilities?
- **Scope signals** — team size, product surface, user scale, revenue
- **PM craft evidence** — discovery, prioritization, experimentation, cross-functional leadership
- **Clarity & structure** — readability, length, formatting for busy readers
- **Seniority framing** — does the résumé position the person at the right level?
- **Red flags** — vague buzzwords, no metrics, project-manager framing instead of product

---

## Open questions (for when this gets scoped)

- **File handling:** accept PDF + DOCX? Max size? Where are uploads stored — disk, object storage, or parsed-and-discarded (no retention, privacy-friendly)?
- **Privacy:** résumés are sensitive PII. Do we store the file, store only the extracted text, or store nothing after generating feedback? Strong lean toward **not retaining the file**.
- **Model:** which agent/model powers evaluation? Claude Haiku (cheap, fast) vs a larger model for deeper critique. Persian + English résumés both supported?
- **Language:** feedback in Persian regardless of résumé language?
- **Cost control:** rate-limit per user (e.g. N evaluations/day) to bound API cost.
- **Output persistence:** save the feedback to the user dashboard, or ephemeral single-view?
- **Abuse:** prevent non-résumé uploads / prompt injection via uploaded content.
- **Scope creep:** does this stay "feedback only", or eventually offer a rewritten résumé draft?

---

## Why it fits petfeature

- Reinforces the "دانشنامه یک مدیر محصول" positioning — not just books, but career growth.
- Natural reason to register and return (ties into v12 auth + dashboard value).
- Reuses the same résumé-upload primitive as the [Personalized Learning Path](./pm-learning-roadmap.md#idea--resume-based-seniority-assessment--personalized-learning-path) idea — build the upload + parse once, power two features.

---

## Not in scope for this idea

- Résumé hosting / public résumé pages
- Job board or job matching
- Human (Milad) manual review — this is agent-only
- Automatic résumé rewriting/generation (possible follow-up, not v1 of the idea)

---

*Raw idea — needs a PRD before any build. Blocked on v12 User Auth.*
