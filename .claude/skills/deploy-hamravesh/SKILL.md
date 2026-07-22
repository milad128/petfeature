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

Stage only relevant files (never `.env`, never `petfeature fable redesign/`, never `app/static/uploads/media/`):
```bash
git add <specific files>
git commit -m "descriptive message"
git push origin main
```

> **Git identity:** The repo has no global git config set on this machine. If `git commit` fails with "Author identity unknown", set it first:
> ```bash
> git config --global user.email "hmirzaei.m@gmail.com"
> git config --global user.name "Milad Hajimirzaei"
> ```

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
- **Never commit:** `.env`, `petfeature fable redesign/`, `app/static/uploads/media/`
- **Static uploads:** stored in `app/static/uploads/` — not persisted across redeploys unless a volume is mounted (currently no volume; uploads are ephemeral in prod)

## DNS & domain setup (petfeature.ir)

### Stack
- **Registrar:** nic.ir (account: mh15843-irnic / Milad Hajimirzaei) — only manages NS records, no A/CNAME management
- **DNS provider:** ArvanCloud (`panel.arvancloud.ir/cdn/petfeature.ir/dns`) — full DNS record management
- **Hamravesh ingress:** `c13.hamravesh.onhamravesh.ir` (server c13)

### Correct ArvanCloud DNS records (full table)

| Type | Name | Value | Proxy |
|------|------|-------|-------|
| `ANAME` | `@` | `c13.hamravesh.onhamravesh.ir` | Off |
| `CNAME` | `www` | `c13.hamravesh.onhamravesh.ir` | Off |
| `CNAME` | `_acme-challenge` | `qwz9g130-9nxf-kxwkvn71.acme-dns.onhamravesh.ir` | Off |
| `NS` | `@` | `r.ns.arvancdn.ir` | — |
| `NS` | `@` | `j.ns.arvancdn.ir` | — |

> ⚠️ **ANAME not CNAME at root:** ArvanCloud does NOT allow `CNAME` for `@` (root domain) — RFC violation. Use `ANAME` instead. ANAME behaves identically (CNAME flattening) but is valid at the apex.

### nic.ir nameserver settings
Must point to ArvanCloud:
- NS1: `r.ns.arvancdn.ir`
- NS2: `j.ns.arvancdn.ir`
- Leave all other NS slots blank / clear them

### SSL certificate (Hamravesh)
- Hamravesh uses **ACME DNS-01 challenge** to issue SSL
- Requires the `_acme-challenge` CNAME above to be present in ArvanCloud
- After adding it, go to **Hamravesh → آدرس دامنه → ذخیره تغییرات** to trigger issuance
- Cert is valid for **3 months** — Hamravesh should auto-renew via the same CNAME; if not, repeat the DNS challenge step
- After SSL is issued, Hamravesh DNS checker will show **"No Record"** — this is a **false negative** (it can't detect ANAME records). Ignore it as long as the site loads.

### Known incidents
- ⚠️ **(2026-07-20):** `c13.hamravesh.onhamravesh.ir` entered as NS1 nameserver in nic.ir instead of as a DNS record → `SERVFAIL` everywhere. Fix: restore ArvanCloud nameservers in nic.ir.
- ⚠️ **(2026-07-21):** Used `A` record with hardcoded IP `193.189.122.16` at root → caused timeouts (IP may have been wrong). Fix: replaced with `ANAME` pointing to `c13.hamravesh.onhamravesh.ir`.
