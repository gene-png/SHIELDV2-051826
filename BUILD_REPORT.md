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

---

## 2026-05-18 — §5 Auth + onboarding (substantial)

**Backend (`apps/api/app/api/routers/auth.py`)**
- [x] `POST /api/auth/signup` — Argon2id password hash, atomic first-user-as-Primary-POC, client singleton provisioning, audit row.
- [x] `POST /api/auth/sign-in` — credential check, Redis-backed lockout enforcement, audit on success + failure, 15-min JWT.
- [x] `POST /api/auth/sign-out` — audit row + stateless JWT expiry.
- [x] `POST /api/auth/accept-invite` — hashed-token validation, 7-day expiry check, new-user creation, immediate sign-in.
- [x] `POST /api/auth/change-password` — verify current + Argon2id rehash.
- [x] `app/auth/jwt.py` — HS256 SHIELD-issued access token, signed with `NEXTAUTH_SECRET` (shared with web). Validator wired into `get_current_user`.

**Web (`apps/web/`)**
- [x] NextAuth v5 Credentials provider (`lib/auth.ts`) — posts to SHIELD `/api/auth/sign-in`, stashes the access token on the session.
- [x] Route handler at `app/api/auth/[...nextauth]/route.ts` re-exports `GET` + `POST`.
- [x] `middleware.ts` route protection — public routes (`/`, `/sign-in`, `/sign-up`, `/verify`, `/accept-invite`) open; everything else requires auth.
- [x] `app/(public)/sign-in/page.tsx` — polygonal SVG background (`PolygonalBackdrop`), bottom-border-only fields, "SHIELD by Kentro" wordmark + "by Kentro" subline.
- [x] `app/(public)/sign-up/page.tsx` — name + email + password (with `PasswordStrengthMeter` — 5-bin heuristic) + confirm + Terms checkbox; on success, hands off to NextAuth and redirects to `/intake`.
- [x] `app/(public)/accept-invite/[token]/page.tsx`.
- [x] `app/(public)/verify/[token]/page.tsx` — explanatory no-op for v1.
- [x] `app/(public)/mfa/enroll/page.tsx` — renders `null` for v1.
- [x] `app/welcome/page.tsx` — between sign-up and intake.
- [x] `app/sign-out/route.ts` — GET handler that POSTs the audit ping to SHIELD before calling NextAuth `signOut`.
- [x] `app/(client)/layout.tsx` — left-rail nav matching design mockup; pulls session via `auth()` server helper.
- [x] `app/(client)/settings/page.tsx` + `app/(client)/settings/password/page.tsx`.
- [x] `app/(client)/home/page.tsx` + `app/(client)/intake/page.tsx` placeholders so post-sign-in redirects resolve.
- [x] TypeScript module augmentation in `types/next-auth.d.ts` for `session.accessToken`, `user.role`, `user.isPrimaryPoc`.

**Closed inline:**
- First-user-as-Primary-POC TBD — implemented as an atomic transaction in `/api/auth/signup` (Master Spec §1 Q2 — developer judgment).

---

## 2026-05-18 — §4 Reference data load (complete)

**Seed files** (live in `packages/`)
- [x] `packages/zt-data/cisa_questions.json` — full 12-question CISA ZTMM 2.0 questionnaire (Z-Q1..Z-Q12) extracted verbatim from `reference-docs/SHIELDv2_CISA_ZT_Questionnaire.docx`. 5 pillars + 3 cross-cutting; Traditional/Initial/Advanced/Optimal maturity ladder.
- [x] `packages/zt-data/dod_questions.json` — full 12-question DoD ZTRA questionnaire (D-Q1..D-Q12) extracted from `reference-docs/SHIELDv2_DoD_ZT_Questionnaire.docx`. 7 pillars; phase-tagged Target / Advanced per the 45+107 activity model; DoD-specific context (CAC/PIV, mission partner, classified/CUI, DISA STIG, ICAM, CMMC/DFARS).
- [x] `packages/csf-data/csf_2_0_subcategories.csv` — 104-row NIST CSF 2.0 subcategory reference (all 6 functions: GV / ID / PR / DE / RS / RC). **STUB caveat:** IG metric alignment, FISMA domain, and interview-topic-family columns are null pending Eugene's full Reference Data CSV — rollup Rules 2 and 5 short-circuit until populated (see `DECISIONS.md` TBD #1).
- [x] `packages/csf-data/csf_tier_questionnaires.json` — one representative HIGH / MOD / LOW question per tier. **STUB** until Eugene supplies the full 15Q / 12Q / 8Q banks.
- [x] `packages/attack-data/curated_subset.json` — 33 ATT&CK techniques across the 11 enterprise tactics. **STUB** based on CISA Top-25 + ATT&CK Evaluations "most observed" until Eugene confirms the Kentro-approved subset.
- [x] `packages/design-system/enums.yaml` — single source of truth for every enum → display-label pair. Cross-checked against `packages/design-system/labels.ts` and `app/models/enums.py` by `load_label_map.py`.

**Loader scripts** (`apps/api/scripts/`)
- [x] `load_csf_subcategories.py` — parses the CSV, upserts by primary key (e.g. `GV.OC-01`). Idempotent.
- [x] `load_cisa_zt_questions.py` — parses CISA JSON, upserts by `(framework_key, external_id)`.
- [x] `load_dod_zt_questions.py` — parses DoD JSON, upserts by `(framework_key, external_id)`.
- [x] `load_csf_tier_questionnaires.py` — loads the HIGH / MOD / LOW stub questions.
- [x] `load_attack_techniques.py` — prefers full STIX bundle at `packages/attack-data/enterprise-attack.json`; falls back to the curated subset when absent.
- [x] `load_attack_curated.py` — thin alias; will flag the 33 curated within the full bundle once vendored.
- [x] `load_label_map.py` — invariant check: every enum value in `app/models/enums.py` must have a key in both `enums.yaml` and `labels.ts`. Fails CI when out of sync.
- [x] `scripts/seed-reference-data.sh` runs the chain end-to-end; idempotent so re-runs are safe.

**Module layout adjustments**
- [x] Added empty `apps/__init__.py` and `apps/api/__init__.py` so `python -m apps.api.scripts.*` resolves cleanly from `/workspace`.
- [x] Added `pyyaml>=6.0.2` to api deps for `load_label_map.py`.

## What's next

§7 Intake wizard (6-step flow) — biggest remaining user-facing block. All four service workspaces in §8 depend on it for the questionnaire-rendering UX it establishes.
