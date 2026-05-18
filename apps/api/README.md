# `apps/api` — SHIELD backend

FastAPI + SQLAlchemy 2.x + Celery. Python 3.12+. Source of truth for data, scoring, AI orchestration, deliverable generation.

Run locally via the dev container:

```bash
docker compose up api
# OpenAPI docs at http://localhost:8000/docs
```

Run migrations:

```bash
docker compose exec api alembic -c apps/api/alembic.ini upgrade head
```

Run tests:

```bash
docker compose exec api pytest
```

See [`docs/architecture.md`](../../docs/architecture.md) for the full layering map.
