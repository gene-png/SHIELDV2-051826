#!/usr/bin/env bash
# Start the Next.js dev server inside the `web` dev container.
# First run installs pnpm dependencies (~3-5 minutes); subsequent runs are fast.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d node_modules ] || [ ! -d apps/web/node_modules ]; then
  echo "==> First-time pnpm install (this takes a few minutes)..."
  pnpm install
fi

echo "==> Starting Next.js dev server on http://localhost:3000 ..."
exec pnpm --filter @shield/web dev
