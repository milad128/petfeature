# Use Case Diagram — petfeature.ir

UML use case diagram for **petfeature.ir** — v1 Library (shipped), v2 Blog, v3 Tools. Backlog epics (Roadmap, newsletter, engagement, analytics) are not shown here until scoped into a version.

**Specs:** [v1](./product-spec-v1.md) · [v2](./product-spec-v2.md) · [v3](./product-spec-v3.md) · [Backlog](./idea-backlog.md) · [Overview](./product-spec.md)

## Diagram

Render `use-case-diagram.puml` with the [PlantUML](https://plantuml.com/use-case-diagram) extension (`Option+D` in Cursor/VS Code).

## Visitor use cases

| Use case | Included sub-use cases | Version |
|----------|------------------------|---------|
| **Browse Book Library** | View Book Details | v1 |
| **Visit About Me** | — | v1 |
| **Browse Blog** | Read Post; Rate Post (stars); Comment on Post; Share to Social Networks; Copy Link | v2 |
| **Browse Tools** | Use a Tool | v3 |

## Structure (UML)

```
Visitor
├── Browse Book Library (v1)
│   └── <<include>> View Book Details (v1)
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
| **Visitor** | Reads books and about page (v1); reads/rates/comments on posts, shares (v2); uses tools (v3) |
| **Admin (Milad Mirzaei)** | Manages books, categories, about (v1); publishes posts, moderates comments (v2); manages tools (v3) |
| **Social Networks** | External share targets for blog posts (v2) |

## Admin use cases

| Use case | Version |
|----------|---------|
| Manage Library Content (books, categories, uploads) | v1 |
| Manage About Author Content | v1 |
| Manage Blog Posts (CRUD, featured, tags) | v2 |
| Moderate Post Comments | v2 |
| Manage Tools | v3 |

## Version legend

| Label | Meaning |
|-------|---------|
| **v1** | Library — books, about me, admin CMS (shipped) |
| **v2** | Blog — posts, ratings, comments, sharing |
| **v3** | Tools — downloadable PM template library |
| **Backlog** | Roadmap, newsletter, contact, book engagement, analytics — unscheduled |

---

*See also: [product-spec.md](./product-spec.md) · [idea-backlog.md](./idea-backlog.md)*
