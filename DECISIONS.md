# Decision Log

A running list of architectural decisions made during the SHIELD v2.0 build. Each entry: date, decision, alternatives considered, reason. Decisions locked by the Master Spec are recorded as references to the spec, not relitigated here.

---

## 2026-05-18 · Pre-flight stack assembly

**Decision:** Adopt the locked stack from Master Spec §1 / §4 as-is.

- **Frontend:** Next.js 14+ App Router, TypeScript strict, Tailwind self-hosted, shadcn/ui copied into `packages/design-system`.
- **Backend:** FastAPI on Python 3.12, SQLAlchemy 2.x, Alembic, Pydantic v2, Celery on Redis.
- **Data:** PostgreSQL 16, MinIO in dev (S3 + KMS in prod), Redis for queue + ephemeral cache only.
- **Auth:** Keycloak default IdP, NextAuth OIDC adapter on web side.
- **LLM:** Anthropic Claude as default provider (`SHIELD_LLM_PROVIDER=anthropic`, model `claude-opus-4-7`). Configurable.

**Reason:** All locked in the Master Spec. No alternative considered.

---

## 2026-05-18 · `docker-compose.yml` at repo root vs. `include:` from `infra/docker/`

**Decision:** Keep the full multi-service compose file at the repo root (`docker-compose.yml`). Per-service Dockerfiles still live at `infra/docker/{web,api}.Dockerfile`.

**Alternatives considered:**
- Compose `include:` directive to split into `infra/docker/docker-compose.yml` (per plan §2 step 2). Rejected for v1: `include` adoption varies across Compose versions in the field and adds a layer of indirection. The devcontainer references the root file directly, which is simpler.

**Reason:** Reliability over aesthetic split. Easy to refactor later if the team prefers the wrapper pattern.

---

## 2026-05-18 · LLM default model = `claude-opus-4-7`

**Decision:** Default `SHIELD_LLM_MODEL` to Claude Opus 4.7 (the most capable model in the Claude 4.x family as of the build date).

**Alternatives considered:**
- Claude Sonnet 4.6 — faster/cheaper but less accurate on the long-form reasoning the spec requires (CSF narrative, ATT&CK coverage rationale).
- Claude Haiku 4.5 — too small for the analysis depth required.

**Reason:** Quality matters more than latency for consultant-driven AI drafts (all marked draft until approved per Master Spec §12). Cost is acceptable because every call is gated by consultant approval before client release.

CI runs with `SHIELD_LLM_MODE=fixture` so no real calls are made during tests.

---

## 2026-05-18 · WeasyPrint over ReportLab

**Decision:** Use WeasyPrint for PDF deliverable generation.

**Reason:** HTML/CSS templates can reuse the design system tokens; ReportLab would require reimplementing layout. Per plan §11. WeasyPrint system deps are added to `infra/docker/api.Dockerfile`.

---

## TBDs awaiting Eugene's input

These are gated until Eugene supplies missing reference data (per plan §19):

1. CSF Reference Data CSV (IG metric alignment, Core vs. Supplemental, Primary vs. Supporting). Without it, CSF rollup Rules 1–6 run in conservative mode.
2. ATT&CK curated subset (33–40 technique IDs) and tool-to-technique seed mappings.
3. CSF "Column C in Working Profile" CSV template column order.
4. "Choose services anyway" lifecycle for consultation requests.
5. Reviewer assignment v1 scope confirmation (deployment-wide only).
6. "Not applicable" handling in CSF rollup math.

When answered, each TBD will be closed out with a dated entry here.
