# پت فیچر (petfeature.ir)

Personal PM encyclopedia — v1 ships the book library and about page.

## Quick start

```bash
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --proxy-headers
```

Open http://localhost:8000

## Documentation

| Doc | Purpose |
|-----|---------|
| **[docs/project-structure-and-deployment.md](./docs/project-structure-and-deployment.md)** | Project layout, why it fits Hamravesh, local dev, deploy steps |
| [docs/product-spec.md](./docs/product-spec.md) | Product overview and version roadmap |
| [docs/product-spec-v1.md](./docs/product-spec-v1.md) | v1 scope: library + about |
| [docs/product-spec-v2.md](./docs/product-spec-v2.md) | v2 scope: full site + community |
