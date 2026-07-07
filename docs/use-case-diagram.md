# Use Case Diagram — petfeature.ir

UML use case diagram for **petfeature.ir** — v1 Library, v2 Blog, v3 Tools, and v4 Book Engagement (all shipped). Backlog epics (Roadmap, newsletter, analytics) are not shown here until scoped into a version.

**Specs:** [v1](./product-spec-v1.md) · [v2](./product-spec-v2.md) · [v3](./product-spec-v3.md) · [v4](./product-spec-v4.md) · [Backlog](./product%20backlog.md) · [Overview](./product-spec.md)

## Diagram

Render `use-case-diagram.puml` with the [PlantUML](https://plantuml.com/use-case-diagram) extension (`Option+D` in Cursor/VS Code).

## Visitor use cases

| Use case | Included sub-use cases | Version |
|----------|------------------------|---------|
| **Browse Book Library** | View Book Details; Rate a Book (stars); Comment on a Book | v1 + v4 |
| **Visit About Me** | — | v1 |
| **Browse Blog** | Read Post; Rate Post (stars); Comment on Post; Share to Social Networks; Copy Link | v2 |
| **Browse Tools** | Use a Tool | v3 |

## Structure (UML)

```
Visitor
├── Browse Book Library (v1 + v4)
│   ├── <<include>> View Book Details (v1)
│   ├── <<include>> Rate a Book (v4)
│   └── <<include>> Comment on a Book (v4)
├── Visit About Me (v1)
├── Browse Blog (v2)
│   ├── <<include>> Read Post
│   ├── <<include>> Rate Post (stars)
│   ├── <<include>> Comment on Post
│   ├── <<include>> Share to Social Networks
│   └── <<include>> Copy Link
└── Browse Tools (v3)
    └── <<include>> Use a Tool
```

## Actors

| Actor | Role |
|-------|------|
| **Visitor** | Reads books and about page (v1); reads/rates/comments on posts, shares (v2); uses tools (v3); rates and comments on books (v4) |
| **Admin (Milad Mirzaei)** | Manages books, categories, about (v1); publishes posts, moderates comments (v2); manages tools (v3); moderates book comments (v4) |
| **Social Networks** | External share targets for blog posts (v2) |

## Admin use cases

| Use case | Version |
|----------|---------|
| Manage Library Content (books, categories, uploads) | v1 |
| Manage About Author Content | v1 |
| Manage Blog Posts (CRUD, featured, tags) | v2 |
| Moderate Post Comments | v2 |
| Manage Tools | v3 |
| Moderate Book Comments | v4 |

## Version legend

| Label | Meaning |
|-------|---------|
| **v1** | Library — books, about me, admin CMS (shipped) |
| **v2** | Blog — posts, ratings, comments, sharing (shipped) |
| **v3** | Tools — downloadable PM template library (shipped) |
| **v4** | Book Engagement — star ratings + moderated comments on books (shipped) |
| **Backlog** | Roadmap, newsletter, contact, analytics — unscheduled |

---

*See also: [product-spec.md](./product-spec.md) · [product backlog.md](./product%20backlog.md)*
