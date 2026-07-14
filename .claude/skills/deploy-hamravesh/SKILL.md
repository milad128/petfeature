---
description: Deploy petfeature.ir changes to Hamravesh Darkube (Kubernetes PaaS) via git push, including pre-flight checks, migration awareness, and post-deploy health verification.
---

# Deploy to Hamravesh Darkube

Deployment is triggered by `git push origin main`. Darkube builds the Dockerfile and rolls out the new container automatically. Migrations run automatically on startup via `start.sh` (`alembic upgrade head` → `uvicorn`).

## Pre-flight checklist

Run these checks before pushing:

### 1. Check for uncommitted changes
```bash
git status --short
git diff --stat HEAD
```

### 2. Check for new/pending migration files
```bash
ls alembic/versions/
alembic history --verbose 2>/dev/null | head -20
```
If there are new migration files (`*.py`) that haven't been committed, stage and commit them.

### 3. Verify no secrets in staged files
```bash
git diff --cached | grep -iE "(SECRET|PASSWORD|TOKEN|KEY)\s*=" | grep -v ".example"
```
Abort if any secrets appear.

### 4. Ensure new models are registered in alembic/env.py
```bash
grep "import" alembic/env.py | grep "models"
```
If a new model file was added in `app/models/`, verify it's imported in `alembic/env.py`.

### 5. Check Dockerfile integrity
```bash
grep -E "(CMD|start\.sh|proxy-headers)" Dockerfile
```
Must contain `start.sh` as CMD and `--proxy-headers` in start.sh.

## Commit and push

Stage only relevant files (never `.env`, never `petfeature fable redesign/`):
```bash
git add <specific files>
git commit -m "descriptive message"
git push origin main
```

## Post-deploy verification

Darkube typically takes 2–4 minutes to build and deploy. Then verify:

```bash
# Health check
curl -s https://petfeature.ir/api/v1/health
# Expected: {"status":"ok"}

# Home page loads
curl -s -o /dev/null -w "%{http_code}" https://petfeature.ir/
# Expected: 200
```

## If migrations fail in production

The production DB is on an **internal K8s hostname** — not reachable from local:
`petfeature-db-proxy.petfeature.svc:5432`

To run migrations manually:
1. Go to **Darkube dashboard → app → Terminal**
2. Run: `alembic upgrade head`

## Key facts
- **Repo:** https://github.com/milad128/petfeature.git
- **Branch:** `main`
- **Health endpoint:** `GET https://petfeature.ir/api/v1/health`
- **Startup:** `start.sh` runs `alembic upgrade head` then `uvicorn`
- **Proxy:** `--proxy-headers` required (Hamravesh reverse proxy terminates HTTPS)
- **Port:** `${PORT}` env var (default 8000, Darkube may override)
- **DB URL pattern:** `postgresql+asyncpg://...` for app; Alembic strips `+asyncpg` for sync URL
- **Never commit:** `.env`, `petfeature fable redesign/`
- **Static uploads:** stored in `app/static/uploads/` — not persisted across redeploys unless a volume is mounted (currently no volume; uploads are ephemeral in prod)
