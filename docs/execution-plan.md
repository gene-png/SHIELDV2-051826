---

# SHIELD by Kentro v2.0 — Single Execution Plan

> One continuous, dependency-ordered roadmap. No phases, no sprints, no weeks.
> Authoritative spec: `/tmp/shield-docs/Master_Spec.txt` (Master Spec).
> Companions: `/tmp/shield-docs/README.txt`, `/tmp/shield-docs/CISA_ZT_Questionnaire.txt`, `/tmp/shield-docs/DoD_ZT_Questionnaire.txt`, `/tmp/shield-docs/Design_Mockup.html`.
> AI Build Prompt (intent only; not authoritative): `git show acdb7b9:source_docs`.

---

## 1. Context

SHIELD by Kentro v2.0 is a greenfield, single-tenant, FedRAMP-targeted enterprise cybersecurity assessment platform. It runs the full lifecycle of a Kentro consulting engagement across four services (Technical Debt Review, Zero Trust Assessment under either CISA ZTMM 2.0 or DoD ZTRA, NIST CSF 2.0 Assessment using the Kentro 10-step Playbook, and MITRE ATT&CK Coverage Mapping) and produces consultant-authored, audit-defensible PDF + XLSX deliverables. This document is the single dependency-ordered execution plan that an autonomous agent will work through start-to-finish. Each item below is gated only by what it strictly requires; everything else can run in parallel.

---

## 2. Pre-flight (workspace prep)

The local workspace is currently a single-container Node 20 dev environment with empty `src/`, `input-files/`, `reference-docs/`. Master Spec requires a Next.js + FastAPI + Postgres + Redis + S3 + Keycloak stack. Local `main` (`cfeddf0`) is behind `origin/main` (`a27dfdc`); origin contains the 5 SHIELD docs.

**Step 0 — sync local with origin.**
- `git -C /workspace pull --ff-only origin main` (if it refuses fast-forward, `git fetch origin && git rebase origin/main`). Expected result: working tree gains `reference-docs/SHIELDv2_*` and the 5 SHIELD docs.
- Verify: `git log --oneline -5` shows `a27dfdc` at HEAD.

**Step 1 — repo layout (monorepo per Master_Spec.txt:2240).** Create the top-level structure as the first commit on a feature branch:
```
/workspace
  /apps
    /web              Next.js 14 App Router app
    /api              FastAPI app (Python 3.12+)
    /worker           Celery worker (shares /apps/api venv)
  /packages
    /design-system    Tailwind tokens + label maps + copy strings
    /shared-types     TS types generated from /apps/api OpenAPI
    /csf-data         108 subcategory CSV + IG metric crosswalk
    /attack-data      vendored MITRE ATT&CK Enterprise JSON
    /zt-data          CISA + DoD questionnaire seed JSON
  /infra
    /docker           dev compose, Dockerfiles
    /terraform        IaC stub for GovCloud / Azure Gov
    /keycloak         realm export / import JSON
  /docs
    architecture.md, data-model.md, security.md, runbooks/, admin-guide.md, client-guide.md
  /scripts            seed loaders, dev helpers
  CHANGELOG.md, DECISIONS.md, SECURITY.md, BUILD_REPORT.md, README.md, .env.example
```

**Step 2 — multi-service docker compose (replaces single-container `app`).**
- `/workspace/infra/docker/docker-compose.yml` services:
  - `web`  — Node 20 + pnpm; mounts `/apps/web`; port `3000`.
  - `api`  — Python 3.12; uvicorn `apps.api.app.main:app --reload`; port `8000`.
  - `worker` — same image as `api`; runs `celery -A apps.api.app.worker worker`.
  - `db`   — `postgres:16-alpine`; volume `pg_data`; port `5432`.
  - `redis` — `redis:7-alpine`; port `6379`.
  - `minio` — `minio/minio:RELEASE`; console `9001`, api `9000`; bucket `shield-artifacts`.
  - `keycloak` — `quay.io/keycloak/keycloak:24`; port `8080`; imports `/infra/keycloak/shield-realm.json`.
  - `mailhog` — dev SMTP catcher; UI `8025`, smtp `1025` (email is feature-flagged off in v1 but the wiring is scaffolded — see Master_Spec.txt:598).
- `/workspace/docker-compose.yml` becomes a thin wrapper that includes `/infra/docker/docker-compose.yml`.
- `/workspace/Dockerfile` is dropped; per-service Dockerfiles live in `/infra/docker/web.Dockerfile`, `/infra/docker/api.Dockerfile`.
- `api.Dockerfile`: `python:3.12-slim` + `weasyprint` system deps (`libpango`, `libcairo2`, `libgdk-pixbuf`), non-root user `appuser`, `POETRY_VIRTUALENVS_CREATE=false`.
- `web.Dockerfile`: `node:20-bookworm-slim`, `pnpm`, non-root.

**Step 3 — devcontainer expansion.** Update `/workspace/.devcontainer/devcontainer.json`:
- `service: web` (primary attach point for VSCode); `dockerComposeFile` lists both compose files.
- `forwardPorts`: `3000, 8000, 5432, 6379, 8080, 9000, 9001, 8025`.
- `postCreateCommand`: `pnpm install && cd /workspace/apps/api && pip install -e .[dev] && alembic upgrade head && pnpm seed:reference-data`.
- `remoteEnv` keeps `ANTHROPIC_API_KEY` for the LLM provider but adds `SHIELD_LLM_PROVIDER=anthropic` and `SHIELD_LLM_MODEL=claude-sonnet-4-7` as defaults.

**Step 4 — tooling baseline.**
- `pnpm-workspace.yaml` listing `apps/*` and `packages/*`.
- `/workspace/pyproject.toml` at repo root for `ruff`, `black`, `mypy`, `pytest` config so the same config applies to `api/` and `worker/`.
- `/workspace/.pre-commit-config.yaml`: `ruff`, `ruff-format`, `mypy` (strict-on-changes), `eslint`, `prettier`, `gitleaks`, `bandit -r apps/api`, `semgrep --config=p/owasp-top-ten`, `cyclonedx-py` SBOM generation on tags.
- `/workspace/.github/workflows/ci.yml`: matrix of `lint`, `typecheck`, `unit`, `integration` (spins up Postgres/Redis/MinIO via service containers), `e2e` (Playwright headless on built image), `accessibility` (axe-core on `/sign-in`, `/intake`, `/home`, `/admin/queue`, `/admin/services/csf/profile/high`), `security` (`pip-audit`, `npm audit --audit-level=high`, `trivy fs .`).

**Step 5 — seed `.env.example`.** Every env var the platform reads, with a placeholder. Categories: database, redis, S3, Keycloak, LLM provider, feature flags (`SHIELD_AUTH_REQUIRE_MFA=false`, `SHIELD_AUTH_REQUIRE_EMAIL_VERIFY=false`, `SHIELD_EMAIL_DELIVERY_ENABLED=false`, `SHIELD_REDACTION_MODE=strict`), JWT settings, app metadata.

> Pre-flight is complete when `docker compose up` produces a green health check on every service, `alembic upgrade head` exits 0, and the Playwright smoke test "loads the sign-in page" passes locally.

---

## 3. Foundational infrastructure (built once, used everywhere)

Order matters strictly within this block. Each item is a concrete deliverable. Items at the same indent can be done in parallel.

### 3.1 Data model — single Alembic baseline migration

File: `/workspace/apps/api/alembic/versions/0001_baseline.py`. SQLAlchemy 2.x models in `/workspace/apps/api/app/models/` — one module per logical group. Every table carries `id UUID PK`, `client_id UUID NOT NULL` (single-tenant defense-in-depth per Master_Spec.txt:1707), `created_at`, `updated_at`. Concretely:

| Table | Module | Notes from spec |
|---|---|---|
| `users` | `models/identity.py` | role enum admin/reviewer/client; `mfa_enrolled`, `email_verified_at` columns exist but unused in v1 (Master_Spec.txt:593) |
| `user_invitations` | `models/identity.py` | `token_hash`, 7-day expiry, single-use |
| `client` | `models/org.py` | singleton row per deployment; `primary_poc_user_id` FK (Master_Spec.txt:1166 — fix v1 bug where this was duplicated) |
| `service` | `models/service.py` | `type` enum + `framework` enum (CISA/DoD only for ZT) |
| `systems` | `models/service.py` | CSAM ID, FIPS 199, ATO status, CAGE code optional |
| `questionnaire_responses` | `models/questionnaire.py` | per-question rows; `not_applicable` + reason; `evidence_artifact_ids` jsonb |
| `questions` | `models/questionnaire.py` | static seed; framework, pillar, dimension tags |
| `csf_subcategories` | `models/csf.py` | 108 rows static; jsonb `ig_metrics`, `alignment`, `fisma_domain` |
| `csf_tier_profile_entries` | `models/csf.py` | per tier (HIGH/MOD/LOW); 5 score columns `dim_g/p/i/m/c`, `total_auto`, `maturity_level_auto` |
| `csf_enterprise_entries` | `models/csf.py` | rollup; `tier_driver_rule` records which of Rules 1–6 fired |
| `gaps` | `models/gap.py` | priority P1/P2/P3; `initiative_group`; `poam_ref` |
| `capability_list` / `capability_items` | `models/tech_debt.py` | versioned list; confidence pct on AI-flagged rows |
| `attack_techniques` | `models/attack.py` | static T-numbers, vendored quarterly |
| `attack_findings` | `models/attack.py` | coverage status enum; detection/prevention/response tool arrays |
| `artifacts` | `models/artifact.py` | S3 key, sha256, lineage jsonb, `origin` enum (origin immutability trigger) |
| `artifact_redactions` | `models/artifact.py` | counts per PII type stripped + FK to `llm_calls` |
| `llm_calls` | `models/ai.py` | provider, model, prompt_version, input/output tokens, mode (real/fixture), status, response_artifact_id |
| `deliverables` | `models/deliverable.py` | `version`, `pdf_artifact_id`, `xlsx_artifact_id`, `released_to_client_at`, `superseded_by` |
| `messages` | `models/messaging.py` | `thread_key` general or per-service; `read_by` jsonb |
| `notifications` | `models/notification.py` | `event_type`, `link`, `read_at` |
| `audit_entries` | `models/audit.py` | append-only; correlation_id; jsonb `details` |
| `service_requests` | `models/service_request.py` | the "I'm not sure" consultation request rows |
| `reviewer_notes` | `models/review.py` | separate from consultant notes per Master_Spec.txt:367 |
| `consultation_requests` | `models/service_request.py` | the I1B fields (Master_Spec.txt:823) |

**Postgres triggers** (in the same baseline migration):
- `audit_entries_no_modify` — `BEFORE UPDATE OR DELETE ON audit_entries FOR EACH ROW EXECUTE FUNCTION raise_exception('audit_entries is append-only')`. (Master_Spec.txt:468)
- `artifacts_origin_immutable` — rejects UPDATE of `origin` once non-null.
- `set_updated_at` — generic trigger on every table with `updated_at`.

**Backfill loader** for the `client` singleton row (1 per deployment) is part of `pnpm seed:reference-data`.

> **TBD flag inline:** `csf_subcategories` requires IG metric alignment metadata that is **not** in the 5-doc bundle — the Master Spec at line 1444 says "loaded once from CSV" and Master_Spec.txt:2086 references the Reference Data tab of the existing XLSX. **Owner: Eugene** to supply the CSF Reference Data CSV; the loader at `/workspace/scripts/load_csf_subcategories.py` accepts either a CSV path or a stub mode that loads NIST CSF 2.0 subcategory IDs and descriptions only, marking `ig_metrics` as `null` and surfacing a banner in `/admin/services/csf/scope` saying "Reference Data not yet loaded — Rules 1–6 roll-up may be conservative."

### 3.2 Auth + Keycloak (depends on data model existing for `users`)

- `/workspace/infra/keycloak/shield-realm.json` — realm `shield`, OIDC client `shield-web` (public, PKCE), client `shield-api` (confidential). Define flows for `mfa` and `email-verify` per Master_Spec.txt:550 but mark the executions Disabled.
- `/workspace/apps/api/app/auth/`:
  - `keycloak.py` — Authlib OIDC validator; pulls JWKS, caches keys.
  - `dependencies.py` — `require_role(Role.admin)`, `require_role(Role.reviewer | Role.client)` FastAPI dependencies. Every router uses these explicitly (no implicit access — OWASP A01 manual checklist).
  - `flags.py` — reads `SHIELD_AUTH_REQUIRE_MFA`, `SHIELD_AUTH_REQUIRE_EMAIL_VERIFY`. When false, enforcement helpers return `None` (no-op). When true, they raise `HTTPException(403, "MFA required")`. The shape is unchanged so flipping the flag never touches call sites (Master_Spec.txt:556).
  - `session.py` — 15-min access JWT, 30-min idle, daily forced re-auth, account lockout (10/15min) tracked in Redis (`shield:lockout:<email>`).
- `/workspace/apps/web/app/api/auth/[...nextauth]/route.ts` — NextAuth OIDC adapter pointing at Keycloak; custom adapter that maps Keycloak `realm_access.roles` to internal `Role`.
- **TBD flag inline:** First user → Primary POC has no pending/verification gate spec'd. Implementation: first signup on a fresh deployment writes `client.primary_poc_user_id = users.id` atomically (transaction); admin can later override via `/admin/client` (Master_Spec.txt:1213). **Owner: developer judgment per spec §1 (Q2).**

### 3.3 Redaction service (the v1 primary control)

Built before any code calls an LLM. Master_Spec.txt:1740 makes the redactor a security boundary, not a cosmetic step.

- `/workspace/apps/api/app/ai/redact.py`:
  - `redact_for_ai(text: str, mode: RedactionMode, client_org_name: str) -> RedactionResult`
  - `redact_payload(obj: Any, ...) -> RedactionResult` — recursive walk for nested dict/list.
  - `RedactionResult` = `cleaned_text`, `removed: dict[PIIKind, int]`, `confidence: float`, `needs_human_review: bool`.
  - Strips per Master_Spec.txt:1766: emails, phones (US + intl), names (curated list + Title-case heuristic), street addresses (with Suite/Floor/PO Box heuristics), client org name → `[CLIENT]`, SSN/EIN/CAGE/contract regexes, signature blocks ("Sincerely,", "Regards,", "Best,").
  - Modes: `strict | standard | off`. `off` raises if `ENVIRONMENT != "dev"`.
- `/workspace/apps/api/app/ai/redact_test_corpus.py` — adversarial fixtures (Master_Spec.txt:1742): emails embedded in URLs, names with unicode diacritics, addresses split across lines, foreign-language signature blocks. CI runs every fixture and asserts removal counts.
- "Review redaction before first LLM call per engagement" UX hook: `/workspace/apps/web/app/(admin)/admin/services/[service]/redaction-review/page.tsx` shows side-by-side original/redacted on the FIRST call per `service.id`. The `llm_calls.status` enum gets a `pending_redaction_review` state.
- If `RedactionResult.needs_human_review`, the worker enqueues with status `pending_redaction_review` and dispatches an admin notification (Master_Spec.txt:1750).

### 3.4 AI job pipeline (depends on redactor)

- `/workspace/apps/api/app/ai/providers/` — abstract `LLMProvider` ABC with `chat(messages, model, **opts) -> LLMResponse`. Concrete implementations: `anthropic.py` (default), `openai.py`, `azure_openai.py`, `bedrock.py`. Selected via `SHIELD_LLM_PROVIDER` env (Master_Spec.txt:478).
- `/workspace/apps/api/app/ai/egress.py` — the single egress point. **Every** outbound LLM call routes through here. Wraps redactor; writes `llm_calls` row pre-call and updates post-call; logs token counts and duration.
- `/workspace/apps/api/app/worker/tasks/` — Celery tasks, one per AI use case (`extract_capability_list`, `score_zt_question`, `propose_csf_narrative`, `analyze_attack_coverage`).
- `/workspace/apps/api/app/api/routers/jobs.py` — `GET /api/jobs/{id}` polling endpoint; `POST /api/jobs/{id}/approve` for consultant approval of AI drafts (Master_Spec.txt:1800).
- **TBD flag inline:** Master_Spec.txt:1677's `llm_calls` schema has `status` but no `retry_count` or `max_retries` and no stale-job TTL. **Implementation:** add `retry_count int default 0`, `max_retries int default 3`, `started_at`, `last_heartbeat_at`. Celery `acks_late=True`, `task_reject_on_worker_lost=True`, exponential backoff with jitter, max 3 attempts; stale jobs older than 30 min with no heartbeat are marked `failed` by a Celery beat sweep. **Owner: developer judgment per spec §4.4.**
- Fixture-replay mode: `SHIELD_LLM_MODE=fixture` reads from `/workspace/apps/api/tests/fixtures/llm/` keyed by prompt hash. CI uses this exclusively (no live calls).

### 3.5 Audit infrastructure (depends on `audit_entries` table)

- `/workspace/apps/api/app/spine/audit.py` — `audit(actor, action, target, details, correlation_id)` helper. Used by every state-changing route.
- `/workspace/apps/api/app/spine/correlation.py` — middleware that injects `X-Correlation-ID` (UUID4 if absent) into request state and into the logger context.
- `/workspace/apps/api/app/spine/access.py` — `check_object_access(user, obj)` IDOR defense; called by every per-id router.
- `/workspace/apps/web/middleware.ts` — propagates correlation ID to downstream API calls.

### 3.6 File storage + CMK encryption

- `/workspace/apps/api/app/storage/s3.py` — `boto3` client; uses `aws:kms` SSE with `SHIELD_KMS_KEY_ID`; in dev defaults to MinIO with a placeholder key. All artifact uploads write `sha256`, `mime_type`, `size_bytes` to `artifacts` and the actual bytes to `s3://shield-artifacts/{deployment_id}/{artifact_id}`.
- `/workspace/apps/api/app/storage/lineage.py` — `attach_lineage(artifact_id, source_artifact_ids, transform, redaction_id)` writes to `artifacts.lineage` jsonb.
- `/workspace/apps/api/app/api/routers/uploads.py` — `POST /api/uploads` with multipart streaming; rejects > 100MB without tus-resumable header (Master_Spec.txt:705 in build prompt).

### 3.7 Design system (parallel-safe with 3.1–3.6)

- `/workspace/packages/design-system/tokens.css` — colors exactly from Design_Mockup.html:8 (`--navy: #1B3A5B`, `--gov-blue: #005EA2`, `--green: #2E7D32`, `--amber: #F57C00`, `--red: #C62828`, neutral scale `#F8FAFC → #0F172A`).
- `/workspace/packages/design-system/tailwind.preset.ts` — Tailwind preset re-exporting tokens as theme extensions; consumed by `apps/web/tailwind.config.ts`.
- `/workspace/packages/design-system/components/` — shadcn/ui components **copied** (not CDN'd) per Master_Spec.txt:425. Build out the inventory the spec requires (Master_Spec.txt:2025): `Card`, `StatusPill` (6 colors per Master_Spec.txt:1893), `NumberCard`, `DataTable` (sticky header, sticky first col, inline edit with explicit save, column resize, row checkbox), `Toast` (sonner; live region), `Modal` (destructive confirm only), `SlideOver` (right drawer), `EmptyState`, `ProgressBar`, `MaturityRadar` (Recharts), `ScoreDonut`, `MaturityHeatmap` (CSF function × maturity grid), `BarChart`, `Sparkline`. Each ships with axe-tested keyboard nav and visible focus.
- `/workspace/packages/design-system/labels.ts` — central enum→display map. Master_Spec.txt:1953 forbids exposing enum slugs; every API response runs `apply_labels()` last in the serializer.
- `/workspace/packages/design-system/copy.ts` — i18n-aware copy strings keyed by message ID; English locale only at v1 per Master_Spec.txt:2326.

### 3.8 Error handler, structured logging, CSP, CI gates (parallel with 3.7)

- `/workspace/apps/api/app/main.py` — global exception handler returns `{error: "...", correlation_id: "..."}` JSON, status 500, no traceback. Refuses to start if `DEBUG=True` is bound to anything other than `127.0.0.1` (Master_Spec.txt:1961).
- `/workspace/apps/api/app/spine/logging.py` — `structlog` JSON renderer; PII-aware (configured to never log `password`, `Authorization`, `token`, full request bodies for `/auth/*`).
- `/workspace/apps/web/next.config.mjs` — CSP `default-src 'self'`, no `unsafe-inline` (move all inline styles into the design system), HSTS preload, X-Frame-Options DENY, X-Content-Type-Options nosniff, Referrer-Policy strict-origin-when-cross-origin, Permissions-Policy strict.
- CI: matrix from §2 step 4 plus a "smoke" job that runs `playwright test smoke/` against a `docker compose up -d`'d stack.

---

## 4. Reference data load (depends on 3.1)

Loader scripts at `/workspace/scripts/`, runnable via `pnpm seed:reference-data` (which calls them in sequence) and pinned in CI as a fixture-load step.

- **`load_csf_subcategories.py`** — reads `/workspace/packages/csf-data/csf_2_0_subcategories.csv` (108 rows). Columns: `id, function, category, description, ig_metric_refs, alignment_primary_or_supporting, fisma_domain, interview_topic_family, question_summary`. **TBD flag inline:** the IG metric alignment columns require Eugene's source CSV; until then the loader accepts a `--stub` mode that loads only the 108 IDs + descriptions from the public NIST CSF 2.0 release (vendored at `/workspace/packages/csf-data/csf_2_0_public.csv`), nulls IG metrics, and writes a `csf_reference_data_status` row.
- **`load_cisa_zt_questions.py`** — reads `/workspace/packages/zt-data/cisa_questions.json` derived from `/tmp/shield-docs/CISA_ZT_Questionnaire.txt`. 12 questions Z-Q1..Z-Q12, each with `pillar` (Identity / Devices / Networks / Applications & Workloads / Data / cross-cutting Visibility / Automation / Governance), `stems`, `cues` (the italic prompts), `framework_functions` (the bottom-right column), and `maturity_levels = ['Traditional','Initial','Advanced','Optimal']`.
- **`load_dod_zt_questions.py`** — reads `/workspace/packages/zt-data/dod_questions.json` from `/tmp/shield-docs/DoD_ZT_Questionnaire.txt`. 12 questions D-Q1..D-Q12, 7 pillars (User / Device / Network/Environment / Application/Workload / Data / Visibility & Analytics / Automation & Orchestration), `phases = ['Target','Advanced']`, 152 activities (45 Target + 107 Advanced).
- **`load_csf_tier_questionnaires.py`** — Step 1.1/1.2/1.3 questions for HIGH(15)/MOD(12)/LOW(8). Master_Spec.txt:923 says all three cover the same 108 subcategories.
- **`load_attack_techniques.py`** — vendors MITRE ATT&CK Enterprise STIX JSON to `/workspace/packages/attack-data/enterprise-attack.json` (refresh quarterly per Master_Spec.txt:1551). Loads ~600+ technique + sub-technique rows.
- **`load_attack_curated.py`** — loads the curated 33–40 default subset and the tool-to-technique mapping seed. **TBD flag inline:** the curated subset list and tool→technique mappings are not specified anywhere in the 5-doc bundle. **Owner: Eugene** to supply the 33–40 curated technique IDs (recommended sources per Master_Spec.txt:1563: MITRE Engenuity ATT&CK Evaluations, NIST CSF crosswalk, vendor detection libraries). Stub mode loads the CISA "Top 25 Most-Exploited" list with a banner: "Curated ATT&CK subset using interim CISA Top 25 — replace with Kentro-approved subset before first client release."
- **`load_label_map.py`** — populates `packages/design-system/labels.ts` from a single source of truth (enum YAML at `/workspace/packages/design-system/enums.yaml`).

---

## 5. Authentication & onboarding (depends on 3.2)

Routes and components, all under `/workspace/apps/web/app/(public)/`:

- `/sign-up` (`page.tsx`) — single-page form per Master_Spec.txt:749. Fields: display_name, email, password (with strength meter component `/packages/design-system/components/PasswordStrength.tsx`), confirm, Terms checkbox. Posts to `/api/auth/signup`. On success, NextAuth signs in immediately and redirects to `/intake`.
- `/sign-in` (`page.tsx`) — Design_Mockup.html section 1 (line 579): polygonal SVG background; bottom-border-only field style; "SHIELD by Kentro" wordmark with "by Kentro" subline.
- `/accept-invite/[token]` — looks up `user_invitations.token_hash`, validates not-expired/not-revoked, prompts new user signup pre-filled with invited email, marks invitation `accepted_at`. Master_Spec.txt:597 specifies 7-day expiry, single-use, hashed.
- `/verify/[token]` — exists, currently no-op (only fires if `SHIELD_AUTH_REQUIRE_EMAIL_VERIFY=true`).
- `/mfa/enroll` — exists, returns 404 in v1 (component mounts but renders `null`) per Master_Spec.txt:559.
- `/sign-out` — clears session, audit row, redirect to `/`.
- `/(client)/settings/page.tsx` — user profile: display_name, title, phone, timezone, notification prefs. Master_Spec.txt:1167 mandates: Primary POC display reads through the `users` FK; updating profile updates POC display. There is no separate POC store.
- `/(client)/settings/password/page.tsx` — password change with current+new+confirm; bcrypt (Argon2id preferred, per OWASP A02).

Welcome screen S4 (Master_Spec.txt:780) is `/welcome/page.tsx`, shown once if `users.intake_started_at IS NULL`, then routes to `/intake`.

---

## 6. Client surface — the 14 routes (depends on 3.7 design system + 3.2 auth)

All under `/workspace/apps/web/app/(client)/`. Left rail + top utility bar shared via `/(client)/layout.tsx`.

| Route | What's on it | Mockup ref |
|---|---|---|
| `/home` | Greeting; hero band (if any deliverable ready); status grid (one card per selected service with pill, headline, big number, next action); "What's waiting on you" list; "Recent activity"; "Recent messages"; cross-service value loop band (§10) | Design_Mockup.html:753–895 |
| `/services` | All four service cards side-by-side with status pills and "Open" CTA | — |
| `/services/tech-debt` | Service detail (executive style) | Design_Mockup.html:902–1064 pattern |
| `/services/zero-trust` | Headline maturity sentence; per-pillar radar chart; "What's next"; expandable "Show me how this is calculated" methodology blurb | Design_Mockup.html:902–1064 |
| `/services/csf` | Function-by-function maturity heatmap; tier-by-tier breakdown thumbnail; methodology expandable | — |
| `/services/attack-surface` | Three big number cards (Covered/Partial/Uncovered); top 5 blind spots in plain English; tactic heatmap; cross-service bridge paragraph | Design_Mockup.html:1535–1631 |
| `/intake` | Wizard (see §7) | Design_Mockup.html:677–746 |
| `/documents` | Two stacks: "What you've shared" + "What you've received" — both as `DataTable`. Delete-within-24h affordance on uploads. | — |
| `/documents/[id]` | Single document or deliverable detail; download buttons calling centralized filename builder | — |
| `/messages` | List of threads (general + per-service) | — |
| `/messages/[thread]` | Plaintext-rendered thread; post box; audit row fires on post | — |
| `/team` | Invite-colleague form (email + optional message), table of existing colleagues with revoke + executive-viewer toggle | — |
| `/settings` | (already in §5) | — |

Cross-cutting: left rail nav config in `/(client)/layout.tsx`; notification bell points to a real `/notifications` page (Master_Spec.txt:1998 — never `/`).

---

## 7. Intake wizard (depends on 3.7 + 6 chrome)

`/workspace/apps/web/app/(client)/intake/` — six-step wizard with progress bar and conditional N based on Master_Spec.txt:797. Each step writes to `service_requests` initially and creates `service` rows only on submit (Master_Spec.txt:1976 forbids partial creation).

- **I1 — Pick your services.** Four checkboxes + fifth radio ("I'm not sure"). When fifth is selected, the four checkboxes deselect AND disable; button label flips to "Request a call ->". (Design_Mockup.html:677–746 verbatim.) On submit with fifth selected, route to I1B and short-circuit the rest of the wizard.
- **I1B — Consultation request.** Form per Master_Spec.txt:822: role/title, organization name, "What's prompting this", contact preference radio, phone (optional), preferred time, anything-else. Posts to `/api/consultation-requests`, writes `consultation_requests` row, fires `notifications` for admins, lands on a thank-you screen. **TBD flag inline:** Master_Spec.txt's spec on transitioning from "consultation pending" back to actual service intake is incomplete. **Implementation:** `/home` for users with `consultation_requests.status = pending` and no `service` rows shows "Your consultation request is being reviewed. [Edit request] [Choose services anyway]" — "Choose services anyway" re-enters the wizard at I1 with the consultation request preserved as `context_consultation_request_id` so the consultant can see both. **Owner: Eugene** to confirm whether "choose services anyway" should close the consultation request or leave it open.
- **I2 — About your organization.** Universal fields per Master_Spec.txt:858 (legal name, DBA, website, size, industry, address). Primary POC pre-filled from session user. Optional compliance deadline.
- **I3 — System scope** (conditional on CSF or ZT selected). Add-card pattern with full Master_Spec.txt:884 fields; ZT-CISA shape vs ZT-DoD shape (CAGE, impact level, mission program) handled by conditional sub-forms.
- **I4 — Service-specific questionnaires.** Section-tabbed renderer (one tab per pillar/function); CSF triggers Step 1.1/1.2/1.3 per FIPS 199 tier present in I3; CISA ZT renders Z-Q1..Z-Q12; DoD ZT renders D-Q1..D-Q12. **Auto-save on blur** via `usePersistOnBlur(field, value)` hook posting to `/api/questionnaire-responses/:id` (debounced 500ms). Visible "Saved 2 seconds ago" indicator. "Not applicable" toggle with reason field per question.
- **I5 — Upload artifacts.** `react-dropzone` drag-and-drop with per-file progress (Master_Spec.txt:1988 forbids native file input). Redaction disclosure block from Master_Spec.txt:1789 displayed prominently. CSF clients see the 16-document checklist with [Have it]/[Requested]/[Doesn't exist]/[N/A] per row.
- **I6 — Confirm and submit.** Summary screen; "Submit" creates `service` rows for **every** checked service (Master_Spec.txt:1975), creates `messages` thread, fires admin notification "<Name> from <Org> completed intake" (Master_Spec.txt:1980 calls this out as a v1 bug to avoid), routes to `/home`.

**TBD flag inline:** Master_Spec.txt does not specify CSF "Column C in Working Profile" scope-inclusion bulk CSV template. **Implementation:** the CSV template at `/workspace/packages/csf-data/scope_template.csv` has columns `subcategory_id, in_scope (Y/N), rationale`. Upload route at I5 (when CSF chosen) accepts this CSV and pre-populates `/admin/services/csf/scope`. **Owner: Eugene** to confirm column order matches existing toolkit.

---

## 8. Service workspaces — each end-to-end (depends on 3 + 4 + 7)

### 8.1 Technical Debt Review

- **Client surface:** `/services/tech-debt` (already in §6).
- **Admin workspace:** `/admin/services/tech-debt/page.tsx` — single page, four vertical steps per Master_Spec.txt:1228 (uploaded inventories list with "Run automated review" button; editable extraction table with `DataTable` inline edit; overlap dashboard with NumberCards + per-overlap finding Cards + bar chart; final consolidation narrative + "Release to client" button). Sidebar AI chat with per-exchange "Add to final plan" button (Master_Spec.txt:1258). **No `<pre>` JSON, anywhere** (Master_Spec.txt:1260).
- **Scoring/calculation engine:** `/workspace/apps/api/app/services/tech_debt/overlap.py` — `compute_overlap(capability_items) -> OverlapReport(categories, savings_per_category, top3_recommendations)`. Pure function, fully unit-tested.
- **AI tasks (with redaction wrapper):**
  - `worker/tasks/extract_capability_list.py` — input: raw uploaded Excel/PDF/image bytes; output: `capability_items` rows with `confidence_pct`. Calls `egress.chat()` which routes through redactor.
  - `worker/tasks/draft_consolidation_recommendation.py` — input: approved capability_list + organization context (redacted); output: 2–3 paragraph narrative.
- **Deliverable generation:** PDF (8–12 pages) + XLSX (3 sheets: Capability List, Overlap Analysis, Consolidation Plan).
- **Reviewer audit walk:** `/reviewer/walk/tech-debt` shows capability_list versions, AI-flagged confidence rows, consultant overrides.

### 8.2 Zero Trust Assessment (one engine, two frameworks)

- **Client surface:** `/services/zero-trust` (already in §6).
- **Admin workspace:** `/admin/services/zero-trust/page.tsx` — Summary tab + N pillar tabs. Per-pillar tab shows client's questionnaire answer (read-only), evidence files, consultant scoring panel (`current_maturity`, `target_maturity`, rationale, gap description, recommendation), "Help me score this" AI button. Master_Spec.txt:1264.
- **One engine, parameterized by `service.framework`:**
  - `services/zero_trust/engine.py` — `compute_pillar_scores(framework, responses) -> dict[pillar, ScoreCard]`. CISA branch uses 5 pillars + 3 cross-cutting with Traditional/Initial/Advanced/Optimal ladder. DoD branch uses 7 pillars with Target/Advanced phase ladder and per-activity Yes/Partial/No/Planned (Master_Spec.txt:1534).
  - `services/zero_trust/roadmap.py` — current→target gap sequencing, 12-month timeline.
- **AI tasks:** `worker/tasks/score_zt_question.py` per Master_Spec.txt:1276; consultant always approves before it lands in the deliverable.
- **Deliverable:** PDF (10–15 pages with executive summary, pillar-by-pillar, top-5 gaps, roadmap) + XLSX (per-pillar scoring + gap/roadmap).
- **Reviewer audit walk:** `/reviewer/walk/zero-trust` — per-pillar walk: client claim → evidence → consultant score → gap → remediation.
- **Cross-reference to CSF:** every ZT function row carries `csf_subcategory_ids` (jsonb) for the value-loop computation in §10. Master_Spec.txt:1521.

### 8.3 NIST CSF 2.0 Assessment — the full Playbook

Largest workspace. Eight sub-pages mounted under `/admin/services/csf/`:

| Route | Playbook step | Implementation |
|---|---|---|
| `/admin/services/csf` | Landing | Project status; current step; "what's next" |
| `/admin/services/csf/scope` | Step 1+4 | Profile architecture decision (tiered HIGH/MOD/LOW + Enterprise); 108 subcategory in_scope toggles + rationale; bulk CSV import |
| `/admin/services/csf/systems` | Step 2 | System inventory (mirrors intake; admin can edit) |
| `/admin/services/csf/artifacts` | Step 3 + ongoing | Artifact tracker — replaces the existing XLSX; status per artifact per system |
| `/admin/services/csf/profile/high` | Step 2.1 | Tier Working Profile HIGH; 108 rows; 5-dim scoring G/P/I/M/C 0–2 each; total 0–10 → maturity 1–5; IG metric side panel; "Draft" toggle |
| `/admin/services/csf/profile/moderate` | Step 2.2 | same shape, MODERATE |
| `/admin/services/csf/profile/low` | Step 2.3 | same shape, LOW |
| `/admin/services/csf/enterprise-profile` | Step 8 | Rolled-up Enterprise Profile; per-subcategory rollup with `tier_driver_rule` shown |
| `/admin/services/csf/gap-analysis` | Step 10 + Gap Methodology | List of GAP-flagged subcategories; characterize, P1/P2/P3, action items, POA&M linkage |
| `/admin/services/csf/action-plan` | Action plan | Initiative grouping; timeline visualization |

- **Scoring engine:** `services/csf/scoring.py`:
  - `score_subcategory(g, p, i, m, c) -> (total, maturity_level)` with the 0–2/0–10 mapping from Master_Spec.txt:1422.
  - **Evidence rule:** if `evidence_artifact_ids == []`, clamp `Implementation <= 1` and `maturity_level <= 2` (Master_Spec.txt:1436). Unit-tested.
- **Weighted-floor roll-up:** `services/csf/rollup.py` — implements Rules 1–6 from Master_Spec.txt:1450:
  1. All tiers same → that score
  2. Primary alignment to a Core metric AND any tier has a gap → strict floor (lowest)
  3. HIGH is the lowest → HIGH
  4. MODERATE is lowest, HIGH higher → MOD
  5. Only LOW is lowest AND subcategory is Supporting-aligned or Supplemental → HIGH/MOD score with documented exception (Rule 2 overrides this)
  6. Mixed otherwise → lower + reasoning
  Records `tier_driver_rule` on each `csf_enterprise_entries` row.
  - **TBD flag inline:** Rules 2 and 5 depend on `csf_subcategories.alignment` (Primary/Supporting) and `csf_subcategories.ig_metrics` Core/Supplemental — both come from Eugene's Reference Data CSV that's not in the 5-doc bundle. If running in stub mode, Rules 2 and 5 short-circuit (treated as not-applicable) and the engine emits a warning row in `csf_enterprise_entries.notes`. **Owner: Eugene** to deliver CSV before first real engagement.
- **Gap detection:** `current < target → GAP`. **Prioritization:** P1 (Core + HIGH + multi-system), P2 (Core OR HIGH), P3 (other). Master_Spec.txt:1464.
- **TBD flag inline:** Master_Spec.txt:944 treats "Not applicable" answers as silent — does it filter from the rollup denominator or score as 0? **Implementation:** treat as filtered (excluded from denominator), record `not_applicable=true` and `not_applicable_reason` on the entry, and surface a count on the Enterprise Profile narrative ("8 of 108 subcategories marked N/A"). **Owner: Eugene**.
- **Reference Data side panel:** `<CsfReferencePanel subcategoryId={...} />` renders IG metrics, alignment, FISMA domain, interview topic family, question summary from `csf_subcategories.ig_metrics` jsonb. Mounts on every profile/enterprise/gap page so the consultant never has to flip files (Master_Spec.txt:1361).
- **AI tasks:** `propose_csf_narrative` (per subcategory; the consultant reviews); `summarize_gap` (per gap; consultant approves).
- **Deliverable:** PDF 20–30 pages (executive summary, function-by-function heatmap, tier breakdown, gap analysis, action plan, methodology appendix) + XLSX matching Step 2.1/2.2/2.3 and Step 3.2.1 shapes **byte-equivalent** (Master_Spec.txt:2093).
- **Reviewer audit walk:** `/reviewer/walk/csf` — per-subcategory chain: client claim → evidence → consultant assessment → gap → remediation.

### 8.4 MITRE ATT&CK Coverage Mapping

- **Client surface:** `/services/attack-surface` (already in §6); Design_Mockup.html:1535 is the executive view.
- **Admin workspace:** `/admin/services/attack-surface/page.tsx` — tactic-tabbed Coverage view; per-technique row with detection/prevention/response tool selectors driven by the approved capability_list; rationale field; AI confidence pill.
- **Coverage engine:** `services/attack/coverage.py` — per Master_Spec.txt:1570:
  - Covered = detection ∧ prevention ∧ response.
  - Partial = 1 or 2 of 3.
  - Uncovered = none.
- **AI tasks:** `analyze_attack_coverage` proposes initial tool→technique mappings against the curated subset; consultant adjusts.
- **Deliverable:** PDF 8–15 pages (executive summary with three big-number cards + top 5 blind spots + tactic heatmap + value-loop bridge paragraph) + XLSX 3 sheets (Summary, Findings, Methodology).
- **TBD flag inline:** The curated subset and tool-to-technique seed mappings are unspecified (already flagged in §4). Until Eugene supplies, ship with stub data.

---

## 9. Admin & reviewer surfaces (depends on 8)

All routes under `/workspace/apps/web/app/(admin)/admin/...` and `/workspace/apps/web/app/(reviewer)/reviewer/...`.

### Admin (~25 routes)
- `/admin/queue` — three-bucket triage (New / Waiting on us / Active) with timestamps everywhere (Master_Spec.txt:1995); persistent "FAILED JOBS" banner if any `llm_calls.status = failed`; "ALERTS" banner for compliance deadlines within 30 days. Design_Mockup.html:1216.
- `/admin/client` — the singleton client profile; editable industry/notes/service-assignments.
- `/admin/services` — overview grid linking to the four service workspaces.
- `/admin/services/tech-debt` (§8.1), `/admin/services/zero-trust` (§8.2), `/admin/services/csf/*` (§8.3), `/admin/services/attack-surface` (§8.4).
- `/admin/documents` — all artifacts; filter by category, system, service; bulk-tag.
- `/admin/documents/[id]` — single artifact with lineage tree (rendered, never `<pre>`-JSON), redaction summary, version history.
- `/admin/deliverables` — release management; status (Draft / Final / Released / Superseded); approval flow.
- `/admin/messages` — all threads.
- `/admin/audit` — append-only log with filters by actor/action/target/date; shows local + UTC timestamps (Master_Spec.txt:1722).
- `/admin/activity` — async jobs (running/failed/recent complete); admin can retry a failed job; Flower mounted at `/admin/activity/flower` behind admin auth.
- `/admin/team` — invite reviewer, add admin (per Master_Spec.txt:706).
- `/admin/settings` — deployment-level: LLM endpoint, redaction mode, retention policy, branding.

### Reviewer (mirror + 4 unique)
- `/reviewer/home` — assigned walks + queue.
- `/reviewer/walk/[service]` — audit walk surface per service (CSF per-subcategory chain, ZT per-pillar, ATT&CK per-technique, Tech Debt per-overlap).
- `/reviewer/audit` — read-only audit log.
- `/reviewer/notes` — reviewer's own notes (separate store; never visible to consultants — Master_Spec.txt:368).
- **Read-only mirror of every `/admin/*` page:** implemented by a `ReadOnlyShell` HOC that strips action buttons and replaces them with "Approve" / "Decline" with reason fields where applicable. Master_Spec.txt:733.
- **TBD flag inline:** Master_Spec.txt:2295 says reviewer assignment is deployment-wide for v1; per-service assignment is a future enhancement. **Implementation:** `users` carries `reviewer_scope = 'deployment'` (only value in v1). **Owner: Eugene** to confirm v1 cap.

---

## 10. Cross-service value loop (depends on 8)

`/workspace/apps/web/app/(client)/home/components/ValueLoopBand.tsx` — visible only when ≥ 2 services are released-to-client. Synthesizes:
- Tech Debt savings → "redirected funding pool" number ($X)
- Zero Trust gaps → top 3 capability investments
- ATT&CK uncovered → detection/prevention/response shortlist
- CSF maturity → compliance framing one-liner

Backed by `/workspace/apps/api/app/services/value_loop.py::compute(client_id)` which joins `capability_list.savings_estimate`, `gaps where framework=zt`, `attack_findings where coverage_status=uncovered`, `csf_enterprise_entries where gap_auto`. Output cached in Redis with 5-min TTL; invalidated on any deliverable release. Master_Spec.txt:317.

---

## 11. Deliverable generation (depends on 8)

- **Engine choice:** WeasyPrint over ReportLab. **Why:** HTML/CSS templates match the design system 1:1 (re-uses Tailwind tokens via inline `<style>` blocks in print stylesheet); ReportLab would require re-implementing the entire layout system. WeasyPrint also handles paged media, page breaks, and TOC out-of-the-box. The system deps are added to `api.Dockerfile` (§2).
- **PDF templates:** `/workspace/apps/api/app/deliverables/templates/` — Jinja2 HTML templates per service: `tech_debt_report.html.j2`, `zt_posture_report.html.j2`, `csf_enterprise_action_plan.html.j2`, `attack_coverage_report.html.j2`. Cover page renders "SHIELD by Kentro" wordmark per Master_Spec.txt:89.
- **XLSX exporters:** `/workspace/apps/api/app/deliverables/xlsx/` — `openpyxl`-based, one module per export: `tier_working_profile.py` (Step 2.1/2.2/2.3 byte-equivalent shape), `enterprise_profile.py` (Step 3.2.1), `gap_analysis.py`, `tech_debt_overlap.py`, `attack_findings.py`. Each ships with a golden-file test that diffs against a checked-in reference XLSX from `/workspace/reference-docs/`.
- **Filename builder:** `/workspace/apps/api/app/services/filename.py::build_filename(client_legal_name, service_type, extension, version=None, working=False)`. Implements slugification per Master_Spec.txt:2154 exactly: trim, whitespace→underscore, strip non-`[A-Za-z0-9_]`, collapse runs, trim, preserve case, "Unknown" fallback. Format: `{Company}_{Service}{MMDDYY}.{ext}`; versioned: `_{Company}_{Service}{MMDDYY}_v2.{ext}`; working: `WORKING_{Company}_{Service}{MMDDYY}.{xlsx}`. Date from deployment server local time at URL request time, not at finalization. 200-char cap with Company truncate-to-150 / Service truncate-to-50 strategy. Centralized — **every** download route calls only this function (Master_Spec.txt:2223). Unit tests cover Eugene's mock-data set: "Nexus Federal Solutions Inc.", "Atlas Defense Solutions, Inc.", "Acme & Co., LLC", "U.S. Department of Anything", "ABC123Org".

---

## 12. Notifications (depends on 3.5 audit + 6 chrome)

- `/workspace/apps/api/app/services/notify.py::dispatch(user_ids, event_type, title, body, link)` — writes `notifications` rows; pushes to a Redis pubsub channel `shield:notifications:{user_id}` for in-app live updates via SSE.
- `/workspace/apps/web/app/components/NotificationBell.tsx` — counts unread; clicks open `/notifications`. Master_Spec.txt:1998 forbids pointing the bell at `/`.
- `/workspace/apps/web/app/(client)/notifications/page.tsx` — list with read/unread filter; links to source page.
- **Trigger points** (each writes audit + notification):
  - New client signup → all admin users.
  - Intake complete → all admin users (Master_Spec.txt:1980 — v1 bug, must work).
  - New message from client → assigned admin(s).
  - Failed background job → all admin users; persistent banner on `/admin/queue` per Master_Spec.txt:1199.
  - Deliverable released to client → primary POC + all client users.
  - Consultation request created → all admin users.
  - Reviewer approves/declines a deliverable → assigned admin.
  - Account lockout → user + all admin users.
- **Email delivery is feature-flagged off in v1** per Master_Spec.txt:598. SMTP wiring exists (`SHIELD_SMTP_HOST`, MailHog in dev compose), the `EmailNotifier` is plumbed but `dispatch_email()` short-circuits to `pass` when `SHIELD_EMAIL_DELIVERY_ENABLED=false`. The **one** exception is the invite token email (Master_Spec.txt:598), which always sends regardless of flag.

---

## 13. Testing strategy

Test pyramid runs in CI on every PR.

- **Unit (fast).** pytest for API (`apps/api/tests/unit/`) and vitest for web (`apps/web/tests/unit/`). Mandatory coverage on:
  - filename slugifier (Eugene's test cases)
  - redactor (every PII type + adversarial fixtures)
  - CSF 5-dimension scoring + maturity mapping
  - CSF weighted-floor Rules 1–6 (one test per rule + edge cases)
  - Tech Debt overlap engine
  - ZT pillar aggregation (CISA + DoD branches)
  - ATT&CK coverage classifier
  - date formatter / timezone renderer
- **Integration (testcontainers Postgres + Redis + MinIO).** `apps/api/tests/integration/` — spins up real services in Docker. Tests every API route with realistic auth tokens.
- **E2E (Playwright).** `e2e/` at repo root. Three role journeys:
  - **Client:** signup → intake (all 4 services + consultation path) → questionnaire (auto-save survives page reload) → upload → home dashboard → view released deliverable → message thread.
  - **Admin:** sign-in via Keycloak → queue → open new lead → drive Tech Debt service end-to-end → release deliverable.
  - **Reviewer:** sign-in → walk surface → record notes → approve deliverable.
- **LLM tests with fixture replay.** CI runs every worker task in `SHIELD_LLM_MODE=fixture` against `apps/api/tests/fixtures/llm/`. Real-mode runs are gated to a separate manual workflow that requires explicit token.
- **Accessibility.** Playwright + `@axe-core/playwright` on `/sign-in`, `/sign-up`, `/intake`, `/home`, `/services/csf`, `/admin/queue`, `/admin/services/csf/profile/high`, `/admin/services/csf/enterprise-profile`, `/reviewer/walk/csf`, `/documents`. Zero serious violations.
- **Load tests.** `k6` script at `/workspace/scripts/load/ai_pipeline.js` — 50 concurrent jobs; asserts p95 < 30s for `extract_capability_list` in fixture mode.
- **Security tests.** `apps/api/tests/security/`:
  - CSP headers, HSTS, X-Frame-Options on every response (`test_headers.py`).
  - SQL injection probes against every search/filter param.
  - IDOR probes: as client A, hit every per-id route with client B's ids → expect 404 (not 403, Master_Spec.txt:4.1).
  - Stack-trace check: forced 500 returns generic message + correlation ID, no traceback in body.
  - Account lockout enforces 10/15min.
  - Audit append-only: try `UPDATE audit_entries` → expect Postgres error.
  - Origin immutability: try `UPDATE artifacts SET origin = ...` → expect Postgres error.

---

## 14. Security & compliance hardening (parallel-safe with later sections)

- **Headers (CSP, HSTS preload, X-Frame-Options DENY, X-Content-Type-Options nosniff, Referrer-Policy strict-origin-when-cross-origin, Permissions-Policy strict).** Configured in `next.config.mjs` + FastAPI `SecurityHeadersMiddleware`. Tested per §13.
- **Secure cookies:** `__Host-` prefix, `Secure`, `HttpOnly`, `SameSite=Strict` on session cookies.
- **CSRF:** Next.js Server Actions use built-in CSRF; FastAPI uses double-submit token on cookie-auth routes.
- **Rate limiting:** `slowapi` middleware. Defaults: 60/min/user, 10/min for `/api/auth/*`, 5/min for `/api/uploads`. Account lockout: 10 failed `POST /api/auth/login` in 15 min per email (Master_Spec.txt:787) tracked in Redis.
- **Daily forced re-auth:** JWT carries `iat`; backend rejects if `now - iat > 24h` even with refresh token (Master_Spec.txt:572).
- **Password policy:** Argon2id; minimum 12 chars; complexity (upper + lower + digit + symbol) enforced; reject top 10k breached (`pwnedpasswords` offline list shipped at `/workspace/packages/wordlists/`).
- **Secrets:** never committed. `.env.example` only. Production reads from AWS Secrets Manager / Azure Key Vault via `boto3` / `azure-keyvault-secrets`.
- **Dependency scanning:** `pip-audit --strict`, `npm audit --audit-level=high`, `trivy fs`, Renovate at `/workspace/renovate.json` (daily schedule).
- **Container hardening:** non-root user, read-only root filesystem (`tmpfs /tmp`), no `latest` tags, `cosign` signs every image, SBOM via `cyclonedx-py` attached to release artifacts.
- **OWASP Top 10 review** runs on every PR per the AI Build Prompt §4 (bandit, semgrep p/sqli + p/xss + p/ssrf, IDOR tests).
- **Egress allowlist.** Worker container `iptables` rule (or AWS SG in prod) limits outbound to: Anthropic API endpoint, MinIO/S3, Keycloak. No general internet.

---

## 15. Observability

- **Logs.** Structured JSON to stdout. Every log line has `correlation_id`, `actor_user_id` (if known), `route`, `latency_ms`. No PII (passwords/tokens redacted by `structlog` processor).
- **Correlation across web → API → worker.** Web sets `X-Correlation-ID` on every fetch; FastAPI middleware reads or generates; Celery task receives via headers; worker logs and audit rows carry the same ID.
- **OpenTelemetry traces (optional, env-gated).** `SHIELD_OTEL_ENDPOINT` env enables OTLP exporter. Spans on every request and every Celery task.
- **Audit-walk UI.** Already covered in §9 reviewer routes; pulls from `audit_entries`, not from logs (different audience: reviewers see business-event chain; logs are for operators).
- **Health endpoints.** `GET /api/healthz` (liveness) and `GET /api/readyz` (checks DB, Redis, S3, Keycloak reachable). Used by docker-compose healthchecks and prod orchestrator.

---

## 16. Documentation

- `/workspace/README.md` — rewrite covering: project overview, prerequisites (Docker), one-command run (`docker compose up`), test commands, deploy notes, env-var index.
- `/workspace/docs/architecture.md` — high-level diagram (mermaid) + service responsibilities.
- `/workspace/docs/data-model.md` — every table with column reference and FK graph.
- `/workspace/docs/security.md` — threat model, OWASP review process, redactor as primary control rationale, risk acceptance log mirroring `/tmp/shield-docs/README.txt:34`.
- `/workspace/docs/runbooks/` — `incident.md`, `backup-restore.md`, `key-rotation.md`, `redactor-tuning.md`, `llm-provider-flip.md` (how to flip from Anthropic to Bedrock without code change), `failed-jobs.md`.
- `/workspace/docs/admin-guide.md` — workflow per service from the consultant's perspective.
- `/workspace/docs/client-guide.md` — sign-up through receiving a deliverable.
- `/workspace/docs/api/` — FastAPI auto-generates OpenAPI at `/api/openapi.json`; `redoc` UI at `/api/docs` is admin-gated.
- `/workspace/docs/fedramp/` — SSP scaffolding, SAR template, POA&M skeleton — placeholders to fill at hardening.

---

## 17. Pre-release hardening

- **Third-party accessibility audit.** WCAG 2.1 AA verification on the 10 routes in §13. Remediate findings.
- **Third-party security audit + pen test.** Acceptance: no HIGH or CRITICAL findings (Master_Spec.txt:2369). Re-test after fixes.
- **Performance pass.** Next.js bundle analyzer; route-level code splitting; image optimization (`next/image` with self-hosted images, no third-party CDN); `EXPLAIN ANALYZE` on every query that joins `csf_*` tables; add indexes on `(service_id, subcategory_id)`, `(client_id, created_at)`, `(actor_user_id, at)` for audit search.
- **Production deployment runbook.** `/workspace/docs/runbooks/deploy.md` — Terraform plan/apply order; secrets bootstrap; Keycloak realm import; first-admin bootstrap; smoke tests; rollback plan (Alembic downgrade, blue/green container swap).
- **Disaster recovery drill.** Run a documented restore-from-backup against a staging deployment.

---

## 18. Verification / acceptance

A concrete end-to-end checklist. Each item lists how to verify.

**Client experience**
- [ ] New client signs up, completes intake (any combo of 4 services + "I'm not sure"), reaches `/home` in < 30 minutes. **Verify:** `playwright test e2e/client-journey.spec.ts`.
- [ ] Every client page uses plain English; no enum slugs, no spec citations. **Verify:** snapshot test `tests/copy/no_slug_leak.test.ts` greps rendered HTML for blocklist `(extraction_review|ai_extraction|primary_poc|tech_debt|zero_trust|attack_surface)` outside designated icon-only contexts.
- [ ] Every analytic output renders as dashboard/cards/charts, never `<pre>JSON</pre>`. **Verify:** Playwright assertion `expect(page.locator('pre')).toHaveCount(0)` on every client route.
- [ ] Auto-save on blur works on every wizard / questionnaire field. **Verify:** `playwright test e2e/intake-autosave.spec.ts` — fill 5 fields, kill page, reopen, assert all 5 persisted.
- [ ] Notifications fire reliably and link to the right page. **Verify:** `pytest apps/api/tests/integration/test_notifications.py`.

**Admin experience**
- [ ] Admin queue surfaces new clients, waiting actions, failed jobs. **Verify:** seed 3 of each, refresh-free observation via SSE.
- [ ] CSF workspace runs the full 10-step Playbook against a client with HIGH + MOD + LOW systems. **Verify:** `playwright test e2e/csf-full-engagement.spec.ts`.
- [ ] Roll-up math matches the methodology for every test case. **Verify:** `pytest apps/api/tests/unit/test_csf_rollup.py` with 1 test per Rule 1–6 + 5 edge cases.
- [ ] Enterprise Profile XLSX matches Step 3.2.1 byte-equivalent. **Verify:** golden-file diff `tests/golden/test_enterprise_profile_xlsx.py`.
- [ ] Both ZT frameworks (CISA and DoD) complete end-to-end. **Verify:** `playwright test e2e/zt-cisa.spec.ts e2e/zt-dod.spec.ts`.
- [ ] ATT&CK Coverage Report generated from approved capability list. **Verify:** E2E test.
- [ ] Every deliverable exportable as PDF and XLSX with correct filename. **Verify:** `pytest tests/test_filename.py` covers Eugene's mock-data set; E2E asserts the download response `Content-Disposition` matches the format.

**Reviewer experience**
- [ ] Reviewer can walk audit chain on every subcategory/pillar and record notes. **Verify:** E2E.
- [ ] Reviewer can approve/decline a final deliverable. **Verify:** E2E.

**Architecture**
- [ ] Single-tenant per deployment. **Verify:** `client_id` is present on every row (introspection test); cross-deployment URL probe returns 404.
- [ ] OIDC federation works against an arbitrary IdP. **Verify:** swap Keycloak for a second instance configured as Entra ID stub; sign-in succeeds.
- [ ] PII redaction wired to every LLM call; audit proves it. **Verify:** `pytest tests/security/test_redaction_coverage.py` asserts every code path that calls `egress.chat()` does so via the redactor; integration test fires an LLM call and confirms an `artifact_redactions` row exists.
- [ ] WCAG 2.1 AA passes axe-core on every key page. **Verify:** CI accessibility job green.
- [ ] OWASP Top 10 manual review documented for every PR. **Verify:** PR template requires section completion.
- [ ] No HIGH/CRITICAL security findings. **Verify:** `trivy`, `pip-audit`, `npm audit` clean.

**Reliability**
- [ ] No stack trace surfaces to user under any forced error. **Verify:** `pytest tests/security/test_no_stacktrace.py` forces a `1/0` in every router and asserts response body.
- [ ] All async jobs have status, retries, failure notifications. **Verify:** integration test forces a worker failure and asserts notification + retry counter.
- [ ] All state changes write an audit row. **Verify:** integration test enumerates every router with `dependencies=[require_role(...)]` and hits each; asserts `audit_entries.count` increases.

---

## 19. Open TBDs to resolve mid-build

Each TBD is also flagged inline at the section where it blocks/affects work.

| # | TBD | Owner | Mitigation while open |
|---|---|---|---|
| 1 | CSF Rules 1–6 require IG metric alignment metadata; reference CSV not in 5-doc bundle | **Eugene** | Stub loader runs; banner on `/admin/services/csf/scope`; Rules 2 & 5 short-circuit |
| 2 | ATT&CK curated 33–40 subset + tool-to-technique seed not specified | **Eugene** | Stub uses CISA Top 25 with explicit banner; consultant manually maps tools at the engagement |
| 3 | "Consultation pending" → service intake transition path incomplete | **Eugene** | "Choose services anyway" CTA on `/home`; consultation request retained as context_id on resulting `service` rows |
| 4 | First user → Primary POC has no pending/verification gate | Developer judgment per spec §1 Q2 | First-signup atomic write; admin override at `/admin/client` |
| 5 | CSF Column C "scope inclusion" bulk CSV template not provided | **Eugene** | `/workspace/packages/csf-data/scope_template.csv` with `subcategory_id, in_scope, rationale` — confirm column order |
| 6 | `llm_calls` lacks `retry_count`, `max_retries`, stale-job TTL | Developer judgment per spec §4.4 | Schema additions documented; Celery beat sweep marks > 30-min stale as failed |
| 7 | "Not applicable" answers' effect on rollup math (treated as 0 vs filtered) | **Eugene** | Filtered (excluded from denominator); count surfaced on Enterprise Profile narrative |
| 8 | Reviewer assignment is deployment-wide only in v1 | **Eugene** to confirm v1 cap | `users.reviewer_scope='deployment'` single-value enum |
| 9 | Whether deliverable approval requires reviewer (spec §17 Q4) | Developer judgment | Default: admin marks Final → reviewer approves if assigned → admin releases. Bypasses reviewer if none assigned |
| 10 | Bypassed via `--no-verify` commits require follow-up fix | Developer policy | Mandatory; tracked in DECISIONS.md |

---

## 20. Critical files to be created or modified

Flat reference list, grouped by area. Every path is absolute.

**Infrastructure & dev env**
- `/workspace/docker-compose.yml` — thin wrapper including `/infra/docker/docker-compose.yml`
- `/workspace/infra/docker/docker-compose.yml` — multi-service: web, api, worker, db, redis, minio, keycloak, mailhog
- `/workspace/infra/docker/api.Dockerfile` — Python 3.12 + WeasyPrint system deps, non-root
- `/workspace/infra/docker/web.Dockerfile` — Node 20 + pnpm, non-root
- `/workspace/infra/keycloak/shield-realm.json` — realm with MFA + email-verify flows defined but disabled
- `/workspace/.devcontainer/devcontainer.json` — multi-service, expanded forwardPorts
- `/workspace/pnpm-workspace.yaml`
- `/workspace/pyproject.toml` — root ruff/black/mypy/pytest config
- `/workspace/.pre-commit-config.yaml` — ruff, mypy, eslint, prettier, gitleaks, bandit, semgrep
- `/workspace/.github/workflows/ci.yml` — lint, typecheck, unit, integration, e2e, accessibility, security matrix
- `/workspace/.env.example` — every env var documented
- `/workspace/renovate.json`

**Backend foundations**
- `/workspace/apps/api/app/main.py` — FastAPI app, global exception handler, no-DEBUG-in-prod guard
- `/workspace/apps/api/alembic/versions/0001_baseline.py` — every table + audit/origin triggers
- `/workspace/apps/api/app/models/identity.py` — users, user_invitations
- `/workspace/apps/api/app/models/org.py` — client (singleton)
- `/workspace/apps/api/app/models/service.py` — service, systems
- `/workspace/apps/api/app/models/questionnaire.py` — questions, questionnaire_responses
- `/workspace/apps/api/app/models/csf.py` — csf_subcategories, csf_tier_profile_entries, csf_enterprise_entries
- `/workspace/apps/api/app/models/gap.py`
- `/workspace/apps/api/app/models/tech_debt.py` — capability_list, capability_items
- `/workspace/apps/api/app/models/attack.py` — attack_techniques, attack_findings
- `/workspace/apps/api/app/models/artifact.py` — artifacts, artifact_redactions
- `/workspace/apps/api/app/models/ai.py` — llm_calls
- `/workspace/apps/api/app/models/deliverable.py`
- `/workspace/apps/api/app/models/messaging.py`
- `/workspace/apps/api/app/models/notification.py`
- `/workspace/apps/api/app/models/audit.py` — audit_entries with append-only trigger
- `/workspace/apps/api/app/models/service_request.py` — consultation_requests, service_requests
- `/workspace/apps/api/app/models/review.py` — reviewer_notes

**Auth & spine**
- `/workspace/apps/api/app/auth/keycloak.py`
- `/workspace/apps/api/app/auth/dependencies.py` — role guards
- `/workspace/apps/api/app/auth/flags.py` — MFA / email-verify feature flags
- `/workspace/apps/api/app/auth/session.py` — JWT, lockout, idle, daily re-auth
- `/workspace/apps/api/app/spine/audit.py`
- `/workspace/apps/api/app/spine/correlation.py`
- `/workspace/apps/api/app/spine/access.py` — IDOR helper
- `/workspace/apps/api/app/spine/logging.py` — structlog config

**AI pipeline (primary control)**
- `/workspace/apps/api/app/ai/redact.py` — redactor (treated as security boundary)
- `/workspace/apps/api/app/ai/redact_test_corpus.py`
- `/workspace/apps/api/app/ai/egress.py` — single LLM egress point
- `/workspace/apps/api/app/ai/providers/anthropic.py` — default
- `/workspace/apps/api/app/ai/providers/{openai,azure_openai,bedrock}.py` — alternates
- `/workspace/apps/api/app/ai/prompts/` — versioned prompt templates per use case
- `/workspace/apps/api/app/worker/tasks/extract_capability_list.py`
- `/workspace/apps/api/app/worker/tasks/score_zt_question.py`
- `/workspace/apps/api/app/worker/tasks/propose_csf_narrative.py`
- `/workspace/apps/api/app/worker/tasks/analyze_attack_coverage.py`

**Storage & deliverables**
- `/workspace/apps/api/app/storage/s3.py` — CMK-encrypted S3/MinIO client
- `/workspace/apps/api/app/storage/lineage.py`
- `/workspace/apps/api/app/services/filename.py` — centralized slugifier + filename builder
- `/workspace/apps/api/app/deliverables/templates/{tech_debt_report,zt_posture_report,csf_enterprise_action_plan,attack_coverage_report}.html.j2`
- `/workspace/apps/api/app/deliverables/xlsx/{tier_working_profile,enterprise_profile,gap_analysis,tech_debt_overlap,attack_findings}.py`

**Service engines**
- `/workspace/apps/api/app/services/csf/scoring.py` — 5-dim → maturity + evidence rule
- `/workspace/apps/api/app/services/csf/rollup.py` — Rules 1–6 weighted floor
- `/workspace/apps/api/app/services/csf/gap.py` — P1/P2/P3 prioritization
- `/workspace/apps/api/app/services/zero_trust/engine.py` — CISA + DoD branches
- `/workspace/apps/api/app/services/zero_trust/roadmap.py`
- `/workspace/apps/api/app/services/tech_debt/overlap.py`
- `/workspace/apps/api/app/services/attack/coverage.py`
- `/workspace/apps/api/app/services/value_loop.py` — cross-service synthesis
- `/workspace/apps/api/app/services/notify.py`

**API routers (one per resource)**
- `/workspace/apps/api/app/api/routers/auth.py`
- `/workspace/apps/api/app/api/routers/client.py`
- `/workspace/apps/api/app/api/routers/services.py`
- `/workspace/apps/api/app/api/routers/systems.py`
- `/workspace/apps/api/app/api/routers/questionnaires.py`
- `/workspace/apps/api/app/api/routers/csf.py`
- `/workspace/apps/api/app/api/routers/zero_trust.py`
- `/workspace/apps/api/app/api/routers/tech_debt.py`
- `/workspace/apps/api/app/api/routers/attack.py`
- `/workspace/apps/api/app/api/routers/uploads.py`
- `/workspace/apps/api/app/api/routers/jobs.py`
- `/workspace/apps/api/app/api/routers/deliverables.py`
- `/workspace/apps/api/app/api/routers/messages.py`
- `/workspace/apps/api/app/api/routers/notifications.py`
- `/workspace/apps/api/app/api/routers/audit.py`
- `/workspace/apps/api/app/api/routers/reviewer.py`
- `/workspace/apps/api/app/api/routers/admin.py`

**Frontend (Next.js App Router)**
- `/workspace/apps/web/app/layout.tsx` — root layout, fonts, providers
- `/workspace/apps/web/app/(public)/layout.tsx`
- `/workspace/apps/web/app/(public)/page.tsx` — marketing landing
- `/workspace/apps/web/app/(public)/sign-in/page.tsx`
- `/workspace/apps/web/app/(public)/sign-up/page.tsx`
- `/workspace/apps/web/app/(public)/accept-invite/[token]/page.tsx`
- `/workspace/apps/web/app/(client)/layout.tsx` — left rail + top bar
- `/workspace/apps/web/app/(client)/home/page.tsx`
- `/workspace/apps/web/app/(client)/home/components/ValueLoopBand.tsx`
- `/workspace/apps/web/app/(client)/intake/page.tsx` — wizard host
- `/workspace/apps/web/app/(client)/intake/components/{Step1Services,Step1BConsultation,Step2Org,Step3Systems,Step4Questionnaires,Step5Uploads,Step6Confirm}.tsx`
- `/workspace/apps/web/app/(client)/services/{tech-debt,zero-trust,csf,attack-surface}/page.tsx`
- `/workspace/apps/web/app/(client)/documents/page.tsx`
- `/workspace/apps/web/app/(client)/documents/[id]/page.tsx`
- `/workspace/apps/web/app/(client)/messages/{page,[thread]/page}.tsx`
- `/workspace/apps/web/app/(client)/team/page.tsx`
- `/workspace/apps/web/app/(client)/settings/page.tsx`
- `/workspace/apps/web/app/(client)/notifications/page.tsx`
- `/workspace/apps/web/app/(admin)/admin/queue/page.tsx`
- `/workspace/apps/web/app/(admin)/admin/client/page.tsx`
- `/workspace/apps/web/app/(admin)/admin/services/tech-debt/page.tsx`
- `/workspace/apps/web/app/(admin)/admin/services/zero-trust/page.tsx`
- `/workspace/apps/web/app/(admin)/admin/services/csf/{page,scope/page,systems/page,artifacts/page,profile/[tier]/page,enterprise-profile/page,gap-analysis/page,action-plan/page}.tsx`
- `/workspace/apps/web/app/(admin)/admin/services/attack-surface/page.tsx`
- `/workspace/apps/web/app/(admin)/admin/{documents,deliverables,messages,audit,activity,team,settings}/page.tsx`
- `/workspace/apps/web/app/(reviewer)/reviewer/home/page.tsx`
- `/workspace/apps/web/app/(reviewer)/reviewer/walk/[service]/page.tsx`
- `/workspace/apps/web/app/(reviewer)/reviewer/audit/page.tsx`
- `/workspace/apps/web/app/(reviewer)/reviewer/notes/page.tsx`
- `/workspace/apps/web/middleware.ts` — correlation ID + auth gate
- `/workspace/apps/web/next.config.mjs` — CSP, HSTS, etc.
- `/workspace/apps/web/tailwind.config.ts`

**Design system & shared**
- `/workspace/packages/design-system/tokens.css`
- `/workspace/packages/design-system/tailwind.preset.ts`
- `/workspace/packages/design-system/components/{Card,StatusPill,NumberCard,DataTable,Toast,Modal,SlideOver,EmptyState,ProgressBar,MaturityRadar,ScoreDonut,MaturityHeatmap,PasswordStrength,NotificationBell}.tsx`
- `/workspace/packages/design-system/labels.ts` — enum → display map
- `/workspace/packages/design-system/copy.ts` — i18n-aware strings
- `/workspace/packages/design-system/enums.yaml` — single source of truth

**Reference data**
- `/workspace/packages/csf-data/csf_2_0_subcategories.csv` (or stub)
- `/workspace/packages/csf-data/scope_template.csv`
- `/workspace/packages/zt-data/cisa_questions.json`
- `/workspace/packages/zt-data/dod_questions.json`
- `/workspace/packages/attack-data/enterprise-attack.json` — vendored MITRE ATT&CK
- `/workspace/packages/attack-data/curated_subset.json` — Kentro 33–40 (or stub)
- `/workspace/scripts/load_csf_subcategories.py`
- `/workspace/scripts/load_cisa_zt_questions.py`
- `/workspace/scripts/load_dod_zt_questions.py`
- `/workspace/scripts/load_csf_tier_questionnaires.py`
- `/workspace/scripts/load_attack_techniques.py`
- `/workspace/scripts/load_attack_curated.py`
- `/workspace/scripts/load_label_map.py`

**Tests (illustrative; the full set is much wider)**
- `/workspace/apps/api/tests/unit/test_filename.py` — Eugene's mock-data slugifier cases
- `/workspace/apps/api/tests/unit/test_redactor.py` — every PII type + adversarial fixtures
- `/workspace/apps/api/tests/unit/test_csf_rollup.py` — Rules 1–6 + edge cases
- `/workspace/apps/api/tests/unit/test_csf_scoring.py` — 5-dim + evidence rule
- `/workspace/apps/api/tests/integration/test_intake_e2e.py`
- `/workspace/apps/api/tests/integration/test_csf_full_engagement.py`
- `/workspace/apps/api/tests/integration/test_redaction_coverage.py`
- `/workspace/apps/api/tests/integration/test_idor.py`
- `/workspace/apps/api/tests/security/test_headers.py`
- `/workspace/apps/api/tests/security/test_no_stacktrace.py`
- `/workspace/apps/api/tests/security/test_audit_append_only.py`
- `/workspace/apps/api/tests/golden/test_enterprise_profile_xlsx.py`
- `/workspace/e2e/client-journey.spec.ts`
- `/workspace/e2e/admin-journey.spec.ts`
- `/workspace/e2e/reviewer-journey.spec.ts`
- `/workspace/e2e/csf-full-engagement.spec.ts`
- `/workspace/e2e/intake-autosave.spec.ts`
- `/workspace/e2e/zt-cisa.spec.ts`
- `/workspace/e2e/zt-dod.spec.ts`

**Docs & meta**
- `/workspace/README.md`
- `/workspace/CHANGELOG.md`
- `/workspace/DECISIONS.md`
- `/workspace/SECURITY.md`
- `/workspace/BUILD_REPORT.md` (final output)
- `/workspace/docs/architecture.md`
- `/workspace/docs/data-model.md`
- `/workspace/docs/security.md`
- `/workspace/docs/admin-guide.md`
- `/workspace/docs/client-guide.md`
- `/workspace/docs/development.md`
- `/workspace/docs/operations.md`
- `/workspace/docs/runbooks/{incident,backup-restore,key-rotation,redactor-tuning,llm-provider-flip,failed-jobs,deploy}.md`
- `/workspace/docs/fedramp/{ssp_scaffolding,sar_template,poam_skeleton}.md`

---

**End of plan.** Total scope per Master Spec acceptance criteria (§18): ~14 client routes, ~25 admin routes, ~4 reviewer routes (plus the read-only mirror), ~20 SQLAlchemy tables, 4 service engines, 4 deliverable pipelines, single redactor security boundary, fixture-replay LLM tests, single centralized filename builder, single audit spine. Dependency-ordered as written — items at the same indent are parallel-safe.