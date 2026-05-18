#!/usr/bin/env bash
# Start the FastAPI server inside the `api` dev container.
# Run this from a `docker compose exec api bash` shell, or as the api service's
# command (already wired in docker-compose.yml).
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> pip install (editable) ..."
pip install -e apps/api[dev]

echo "==> Running migrations ..."
alembic -c apps/api/alembic.ini upgrade head

echo "==> Starting uvicorn on http://localhost:8000 ..."
exec uvicorn apps.api.app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir apps/api
