# Changelog

All notable changes to SHIELD by Kentro v2.0 are recorded here. Format loosely follows [Keep a Changelog](https://keepachangelog.com).

## [Unreleased]

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
