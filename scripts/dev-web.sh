#!/usr/bin/env bash
# Start the Next.js dev server inside the `web` dev container.
# First run installs pnpm dependencies (~3-5 minutes); subsequent runs are fast.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d node_modules ] || [ ! -d apps/web/node_modules ]; then
  echo "==> First-time pnpm install (this takes a few minutes)..."
  pnpm install
fi

# Sanity-check the api container is reachable. Without this you can spend
# 5 minutes wondering why sign-up "does nothing" — the rewrite proxies into
# http://api:8000 and gets a connect-refused when the api is still booting.
echo "==> Checking api service health ..."
if command -v curl >/dev/null 2>&1; then
  for i in 1 2 3 4 5; do
    if curl -fsS http://api:8000/health >/dev/null 2>&1; then
      echo "    api OK"
      break
    fi
    echo "    api not ready yet (attempt $i/5) — sleeping 3s ..."
    sleep 3
    if [ "$i" = "5" ]; then
      echo "    api still not reachable. Check: docker compose logs api"
      echo "    (continuing anyway — sign-up etc. will fail until api is up)"
    fi
  done
else
  echo "    curl not installed; skipping api health check"
fi

echo "==> Starting Next.js dev server on http://localhost:3000 ..."
exec pnpm --filter @shield/web dev
