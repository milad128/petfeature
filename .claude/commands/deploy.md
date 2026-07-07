# Deploy to Hamravesh Darkube

Deploy the petfeature app to production on Hamravesh Darkube (petfeature.ir).

## How it works

Hamravesh Darkube watches the connected Git repo. A `git push` triggers an automatic Docker build and rolling deploy on its Kubernetes cluster. Your job is to get a clean, tested commit pushed — Darkube handles the rest.

## Steps

### 1 — Verify working tree

Run `git status` and `git diff` to understand what's uncommitted.

- If there are untracked or modified files the user has not staged, **ask whether they should be committed** before deploying. Do not `git add .` silently.
- If the tree is already clean, skip to step 2.
- If there are staged changes waiting for a commit message, draft one and ask for approval before committing.

### 2 — Confirm migration changes

Check whether any new Alembic migration files exist in `alembic/versions/` that have not been committed yet. Remind the user:

> Alembic migrations must be committed and pushed **before** they can run on production.
> On Hamravesh, run `alembic upgrade head` as a one-off job or init container after the new image is live.

### 3 — Push to Git

Run:
```bash
git push origin main
```

Confirm the push succeeded and report the commit SHA that was pushed.

### 4 — Check Hamravesh build

After pushing, remind the user to:

1. Open the **Hamravesh Darkube panel** for the `petfeature` app.
2. Watch the build log — the image build typically takes 1–3 minutes.
3. Once the container is running, hit `GET /api/v1/health` to confirm the app is up:
   ```bash
   curl https://petfeature.ir/api/v1/health
   ```

### 5 — Run migrations (if schema changed)

If any migration files were pushed in this deploy, remind the user to run the migration as a one-off job in the Darkube panel:

```bash
alembic upgrade head
```

This must run **after** the new image is deployed (so the new migration files exist in the container).

### 6 — Smoke test

Suggest these quick checks:

- [ ] Home page loads: `https://petfeature.ir/`
- [ ] Library page loads: `https://petfeature.ir/library/`
- [ ] Admin login works: `https://petfeature.ir/admin/login/`
- [ ] Health check: `https://petfeature.ir/api/v1/health`

---

## Environment variables checklist (first deploy or new vars)

If this is a first deploy or new env vars were added, verify these are set in the Darkube panel:

| Variable | Notes |
|----------|-------|
| `DATABASE_URL` | `postgresql+asyncpg://USER:PASS@HOST:5432/DB` from PostgreSQL addon |
| `SECRET_KEY` | Long random string |
| `DEBUG` | `false` |
| `ADMIN_USERNAME` | Admin CMS username |
| `ADMIN_PASSWORD` | Strong password |

---

## Rollback

If the deploy is broken, Darkube supports rolling back to a previous image version from the panel. No `git revert` needed unless the bad code also ran a destructive migration.
