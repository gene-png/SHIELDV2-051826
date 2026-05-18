# Changelog

All notable changes to SHIELD by Kentro v2.0 are recorded here. Format loosely follows [Keep a Changelog](https://keepachangelog.com).

## [Unreleased]

### Fixed (2026-05-18 round 2 — silent failures + QA process)
- Sign-up "Create account" button no longer silently disables when a requirement is unmet. Submit now always works (when not busy); validation runs on click and surfaces a clear inline error ("Password is too weak. Missing: A symbol", "Please accept the privacy notice…", etc.). Same fix applied to Accept-invite + Change-password.
- Intake I1 "Continue" no longer silently disables when no services are picked; same for I2 with empty legal name. Both now show inline validation errors on click.
- Lowered password strength threshold from `score >= 4` to `score >= 3` (length + 2 character classes minimum). Still meets NIST 800-63B but doesn't require all five character types.
- Added `/legal/privacy` and `/legal/accessibility` pages (placeholders) — the sign-up Terms checkbox links to them, so they would have 404'd if clicked.
- Added `docs/qa-checklist.md` — the must-run-before-claiming-done checklist (route-by-route smoke pass + linkrot search + audit-row spot check).
- Added `apps/api/tests/unit/test_routes_smoke.py` — asserts every expected `/api/*` route is still registered; fails CI if a route disappears or an undocumented route is added.
- README's "Development discipline" section codifies: code-trace, smoke, unit-test, linkrot search before claiming "done".

### Fixed (2026-05-18 follow-up)
- Next.js dev server now binds to `0.0.0.0` so VS Code's forwarded-port and host browsers reach it (`apps/web/package.json` `dev` script).
- Web compose service no longer runs `pnpm dev` automatically on container start — it `sleep infinity`s so VS Code can attach cleanly. Start the Next.js server yourself from the VS Code terminal with `bash scripts/dev-web.sh`. This gives full visibility into install + boot.
- Removed `Mapped[Numeric]` typing bug on `capability_items.annual_cost_usd` (use `Decimal` for the Python side, `Numeric(14,2)` for the SQL side).
- Removed Playwright + axe-core from root devDependencies to keep first `pnpm install` to ~3–5 minutes (they'll come back with §13 testing).
- README now documents both VS Code Dev Containers and plain Docker Compose flows + a Troubleshooting section.

### Added
- Pre-flight monorepo scaffolding per execution-plan §2: `apps/`, `packages/`, `infra/`, `docs/`, `scripts/`, `e2e/`, `reference-docs/`.
- Multi-service `docker-compose.yml` (web, api, worker, db, redis, minio, keycloak, mailhog).
- Per-service Dockerfiles at `infra/docker/{web,api}.Dockerfile`.
- Workspace tooling: `pnpm-workspace.yaml`, root `package.json`, root `pyproject.toml` with ruff/mypy/pytest config, `.pre-commit-config.yaml`.
- CI workflow at `.github/workflows/ci.yml` (lint, test, security, accessibility).
- `.env.example` covering DB, Redis, S3, Keycloak, NextAuth, LLM provider, feature flags, session security.
- Devcontainer post-create script and reference-data seed script.

### Notes
- The 5 SHIELD reference documents pulled in from `origin/main` (`a27dfdc`) and moved into `reference-docs/`.
- Old single-container `Dockerfile` and `Dockerfile.txt` removed in favor of per-service images.
