# Use Case Diagram — petfeature.ir

UML use case diagram for **petfeature.ir** — **v1** library scope plus planned **v2** capabilities.

**Specs:** [v1](./product-spec-v1.md) · [v2](./product-spec-v2.md) · [Overview](./product-spec.md)

## Diagram

Render `use-case-diagram.puml` with the [PlantUML](https://plantuml.com/use-case-diagram) extension (`Option+D` in Cursor/VS Code).

## Visitor use cases

| Use case | Included sub-use cases | Version |
|----------|------------------------|---------|
| **Browse Book Library** | View Book Details; Read Book Comments | Library: v1; Comments: v2 |
| **Visit About Me** | — | v1 |
| **Subscribe to Newsletter** | Validate Form, Show Success | v2 |
| **Contact** | Validate Form, Show Success | v2 |
| **Browse Learning Path** | View Path Content | v2 |
| **Browse Blog** | Read Blog Posts; Make Reaction; Comment on Post; Share to Social Networks | v2 |
| **Register** | Authenticate | v2 |

## Structure (UML)

```
Visitor
├── Browse Book Library (v1)
│   ├── <<include>> View Book Details (v1)
│   └── <<include>> Read Book Comments (v2)
├── Visit About Me (v1)
├── Subscribe to Newsletter (v2)
├── Contact (v2)
├── Browse Learning Path (v2)
│   └── <<include>> View Path Content
├── Browse Blog (v2)
│   ├── <<include>> Read Blog Posts
│   ├── <<include>> Make Reaction
│   ├── <<include>> Comment on Post
│   └── <<include>> Share to Social Networks
└── Register (v2)
```

**Authentication (v2):** Register includes Authenticate. Make Reaction, Comment on Post, and Read Book Comments extend Authenticate when the user is not logged in.

## Actors

| Actor | Role |
|-------|------|
| **Visitor** | Reads books and about page (v1); browses path/blog, subscribes, contacts, shares (v2); registers in v2 |
| **Admin (Milad Mirzaei)** | Manages books and about-author content (v1); path, blog, newsletter, contact, moderation (v2) |
| **Email Service** | Newsletter signup, contact delivery, outbound newsletter (v2) |
| **Social Networks** | External targets for share action (v2) |

## Admin use cases

| Use case | Version |
|----------|---------|
| Manage Library Content | v1 |
| Manage About Author Content | v1 |
| Manage Learning Path | v2 |
| Manage Blog Posts | v2 |
| Moderate Comments | v2 |
| Receive Contact Messages | v2 |
| Send Newsletter | v2 |

## UML relationships

| Relationship | Usage in this diagram |
|--------------|-------------------------|
| **Association** | Actor initiates a top-level use case |
| **`<<include>>`** | Parent browse/engagement use case always involves the child (e.g. Browse Blog includes Read Posts) |
| **`<<extend>>`** | Reaction, comment, and book comments extend Authenticate when login is required |
| **`<<v2>>`** | Planned for version 2 |

## Version legend

| Label | Meaning |
|-------|---------|
| **v1** | Library launch: books, about me, admin content management |
| **v2** | Full site + community: path, blog, newsletter, contact, share, auth, reactions, comments, moderation |

---

*See also: [product-spec.md](./product-spec.md) · [product-spec-v1.md](./product-spec-v1.md) · [product-spec-v2.md](./product-spec-v2.md)*
