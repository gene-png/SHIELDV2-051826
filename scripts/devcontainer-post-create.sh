#!/usr/bin/env bash
# Post-create hook for the SHIELD dev container.
# Runs once after the container is built. Intentionally minimal — heavy lifting
# (installs, migrations, seed) happens lazily on first service start so this
# script can succeed even when individual services are still initializing.
set -euo pipefail

echo "[devcontainer] SHIELD by Kentro v2.0 — post-create"
echo "[devcontainer] workspace at $(pwd)"

if command -v git >/dev/null 2>&1; then
  git config --global --add safe.directory /workspace || true
fi

echo "[devcontainer] post-create done. Bring services up with: docker compose up"
