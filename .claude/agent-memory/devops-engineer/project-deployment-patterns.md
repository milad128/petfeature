---
name: project-deployment-patterns
description: Deployment workflow, migration policy, and file exclusion rules for petfeature.ir on Hamravesh Darkube
metadata:
  type: project
---

Deployment is triggered by `git push origin main`. Darkube automatically rebuilds the Docker image and redeploys to K8s — no manual steps needed in the dashboard for code-only changes.

**Why:** Hamravesh Darkube watches the configured branch; push = build + deploy.

**How to apply:** Always push to `main`. Never force-push main. Never skip git hooks.

## Files that must never be committed

- `app/static/uploads/media/` — user-uploaded binary files (images, etc.); grows unboundedly and would bloat the image
- `.env` — secrets; use Darkube env vars panel for production

## Migration policy

No Alembic migration is needed when changes are limited to:
- Python dataclasses in `app/services/roadmap_data.py`
- Service logic, templates, routes, docs, agent memory files

A migration IS needed when:
- New SQLAlchemy model added to `app/models/`
- New column added to an existing model
- Index, constraint, or table dropped

When migration is needed: run `alembic revision --autogenerate -m "..."` locally, commit the migration file, then after deploying run `alembic upgrade head` as a one-off job in the Darkube dashboard (or init container). Cannot run migrations remotely from the local machine.

## Staging pattern

Stage named files explicitly — never `git add .` or `git add -A`. This prevents accidentally including uploads or `.env`.

## Health check

After push, check `GET https://petfeature.ir/api/v1/health` returns 200 once Darkube finishes the build (visible in the Darkube dashboard build log).
