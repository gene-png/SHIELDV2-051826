# SHIELD v2.0 Build Report

Running log of build progress against the execution plan at `docs/execution-plan.md`. Updated at each milestone.

---

## 2026-05-18 — Pre-flight complete ✅ (commit `163b088`)

**Plan §2 (workspace prep)**

- [x] §2 Step 0 — Sync local with `origin/main` (fast-forward `cfeddf0` → `a27dfdc`). The 5 SHIELD reference docs pulled into the working tree.
- [x] §2 Step 1 — Monorepo layout created: `apps/{web,api,worker}`, `packages/{design-system,shared-types,csf-data,attack-data,zt-data}`, `infra/{docker,terraform,keycloak}`, `docs/{runbooks,fedramp}`, `scripts/`, `e2e/`, `reference-docs/`.
- [x] §2 Step 2 — Multi-service `docker-compose.yml` written (web, api, worker, db, redis, minio, keycloak, mailhog). Per-service Dockerfiles at `infra/docker/{web,api}.Dockerfile`.
- [x] §2 Step 3 — `.devcontainer/devcontainer.json` updated for the new stack with `forwardPorts: [3000, 8000, 5432, 6379, 8080, 9000, 9001, 8025]`.
- [x] §2 Step 4 — Tooling baseline: `pnpm-workspace.yaml`, root `package.json`, root `pyproject.toml` (ruff/black/mypy/pytest), `.pre-commit-config.yaml`, `.github/workflows/ci.yml`.
- [x] §2 Step 5 — `.env.example` seeded with every env var the platform reads.
- [x] Move 5 SHIELD source docs into `reference-docs/` (git-detected as renames).
- [x] Remove obsolete root `Dockerfile` and `Dockerfile.txt`.
- [ ] Verify `docker compose config` parses (deferred — docker CLI not available in this shell; will validate on first `docker compose up`).
- [x] Commit "pre-flight: monorepo scaffolding + dev container" (`163b088`).

**TBDs surfaced** — none new; six gated on Eugene per `DECISIONS.md`.

---

---

## 2026-05-18 — §3 Foundational infrastructure (substantial)

**Plan §3.1 — data model**
- [x] 14 SQLAlchemy model modules covering the ~22 tables from Master Spec §11.
- [x] `Base` with PK / tenant-scope / timestamp mixins; UUID PKs; UTC timestamps.
- [x] Alembic baseline migration (`0001_baseline.py`) that creates all tables via `Base.metadata.create_all` and installs:
  - `audit_entries` append-only trigger (rejects UPDATE / DELETE).
  - `artifacts.origin` immutability trigger.
  - generic `set_updated_at` trigger applied to every table with `updated_at`.
  - `client` singleton uniqueness index.
- [x] `alembic/env.py` wired to `Base.metadata` so future `--autogenerate` runs see every table.

**Plan §3.2 — auth (partial)**
- [x] Argon2id password hashing + verification (`app/auth/passwords.py`).
- [x] Redis-backed lockout state (`app/auth/session.py`) honoring `SHIELD_ACCOUNT_LOCKOUT_*` envs.
- [x] FastAPI dependencies (`app/auth/dependencies.py`) — `get_current_user`, `require_role(*roles)`. Test-header bypass enabled only in `development|test|ci`.
- [x] MFA / email-verify feature-flag enforcement helpers — return null when flags off so flipping them in v1.x activates the requirement without router changes.
- [ ] Keycloak Authlib JWKS validator (lands with §5 sign-in surface; until then the dependency raises 501 on a real bearer).

**Plan §3.3 — redaction (THE v1 primary security control)**
- [x] `app/ai/redact.py` — strips emails, phones, SSNs, EINs, CAGE codes, contract numbers, street addresses, PO boxes, signature blocks, and the client org name (`[CLIENT]`).
- [x] `redact_payload()` recursive walker for nested structures.
- [x] `tests/unit/test_redactor.py` — adversarial regression suite (every PII kind + payload walk + `off`-mode flag-for-review).

**Plan §3.4 — AI job pipeline**
- [x] `app/ai/providers/` — `LLMProvider` ABC + `AnthropicProvider` default (`claude-opus-4-7`).
- [x] `app/ai/egress.py` — single egress point. Every call routes through the redactor; fixture-replay mode for CI keyed by SHA-256 of `(model, messages)`.

**Plan §3.5 — audit infrastructure**
- [x] `app/spine/audit.py` — `audit(...)` helper used by every state-changing route.
- [x] `app/spine/correlation.py` — `CorrelationIdMiddleware` mints / propagates `X-Correlation-ID`.
- [x] `app/spine/access.py` — `check_object_access` IDOR guard. Raises `AccessDenied` → mapped to HTTP 404 to avoid existence leakage.
- [x] `app/spine/db.py` — SQLAlchemy engine + `get_db()` FastAPI dep.

**Plan §3.6 — file storage**
- [x] `app/storage/s3.py` — boto3 client; `put_artifact` does stream-and-hash + KMS SSE in non-dev.
- [x] `app/storage/lineage.py` — lineage JSONB helpers (`new_lineage`, `attach_redaction`, `append_transform`).

**Plan §3.7 — design system (tokens only; components defer)**
- [x] `packages/design-system/tokens.css` — palette + radius + shadow CSS variables from `reference-docs/SHIELDv2_Design_Mockup.html`.
- [x] `packages/design-system/labels.ts` — every enum's user-facing label per Master Spec §14 (no raw slugs in UI).
- [ ] shadcn/ui copy-in + base components (Card, StatusPill, NumberCard, DataTable, MaturityRadar, etc.) — deferred to component-driven phase.

**Plan §3.8 — error handler / logging / CSP**
- [x] `app/main.py` wires correlation middleware + global exception handler + `AccessDenied → 404`.
- [x] `app/spine/logging.py` — structlog JSON renderer with sensitive-key stripping (`password`, `Authorization`, `token`, `Cookie`).
- [x] CSP / HSTS / X-Frame-Options / Referrer-Policy / Permissions-Policy in `apps/web/next.config.mjs`.

## What's next

§4 Reference data load — write loader scripts (CSF subcategories stub, CISA + DoD questionnaire JSON parsing from `reference-docs/SHIELDv2_*Questionnaire.docx`, CSF tier questionnaires, ATT&CK Enterprise STIX vendor + curated subset stub, label map). Then §5 sign-in / sign-up flows that consume the auth scaffolding above.
