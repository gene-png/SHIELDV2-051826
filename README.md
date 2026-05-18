# SHIELD by Kentro v2.0

Enterprise cybersecurity assessment platform. Single-tenant per deployment, FedRAMP-targeted, four-service engagement workflow (Technical Debt Review, Zero Trust Assessment under CISA ZTMM 2.0 or DoD ZTRA, NIST CSF 2.0 Assessment, MITRE ATT&CK Coverage Mapping).

> **Source of truth:** [`reference-docs/SHIELDv2_Master_Spec.txt`](reference-docs/SHIELDv2_Master_Spec.txt).
> **Execution plan:** see [`docs/execution-plan.md`](docs/execution-plan.md) for the live, dependency-ordered build plan.

## Repository layout

```
apps/
  web/              Next.js 14 App Router (TS strict, Tailwind, shadcn/ui copied in)
  api/              FastAPI (Python 3.12) — REST API + OpenAPI
  worker/           Celery worker entrypoint (shares apps/api image)
packages/
  design-system/    Tailwind tokens + shadcn components + label maps + copy
  shared-types/     TS types generated from apps/api OpenAPI
  csf-data/         CSF 2.0 subcategory CSV + IG metric crosswalk
  attack-data/      Vendored MITRE ATT&CK Enterprise JSON
  zt-data/          CISA + DoD questionnaire seed JSON
infra/
  docker/           Dev container Dockerfiles
  terraform/        IaC stub for AWS GovCloud / Azure Government
  keycloak/         Realm export imported on container start
docs/               Architecture, data model, security, runbooks, guides
scripts/            Seed loaders + dev helpers
reference-docs/     Locked SHIELD v2 reference documents (master spec, design mockup, questionnaires, README)
e2e/                Playwright end-to-end tests
```

## Prerequisites

- Docker Desktop (or Docker Engine) with Docker Compose v2
- VS Code with the Dev Containers extension (recommended)
- An `ANTHROPIC_API_KEY` if running real LLM calls (defaults to `fixture` mode otherwise)

All development happens inside the dev container. Nothing installs to the host.

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

Then open:

| Service           | URL                          |
| ----------------- | ---------------------------- |
| Web (Next.js)     | http://localhost:3000        |
| API (FastAPI)     | http://localhost:8000/docs   |
| Keycloak (admin)  | http://localhost:8080        |
| MinIO (console)   | http://localhost:9001        |
| MailHog (UI)      | http://localhost:8025        |
| Postgres          | postgres://localhost:5432    |

The first boot will install dependencies, run Alembic migrations, and seed reference data.

## Running tests

```bash
# API unit + integration tests (inside the api container)
docker compose exec api pytest

# Web lint + unit tests
docker compose exec web pnpm lint
docker compose exec web pnpm test

# End-to-end (Playwright, from host or web container)
pnpm test:e2e
```

## Documentation

- [`docs/execution-plan.md`](docs/execution-plan.md) — single dependency-ordered build plan
- [`docs/architecture.md`](docs/architecture.md) — system architecture
- [`docs/data-model.md`](docs/data-model.md) — schema overview
- [`docs/security.md`](docs/security.md) — security posture, redaction, audit
- [`docs/admin-guide.md`](docs/admin-guide.md) — Kentro consultant guide
- [`docs/client-guide.md`](docs/client-guide.md) — client-facing guide
- [`docs/runbooks/`](docs/runbooks/) — operational runbooks (incident, backup, key rotation, etc.)

## Risk acceptance log

Per the Master Spec and the SHIELD v2 README, two risks are explicitly accepted for v1:

1. **Commercial LLM provider may not be FedRAMP-authorized.** Egress may leave the FedRAMP boundary. Mandatory PII redaction (`apps/api/app/ai/redact.py`) is the primary control. See [`docs/security.md`](docs/security.md).
2. **MFA and email verification deferred for v1.** Compensating controls: 15-minute JWT lifetime, 30-minute idle timeout, daily forced re-auth, account lockout after 10 failed attempts in 15 minutes. Feature flags (`SHIELD_AUTH_REQUIRE_MFA`, `SHIELD_AUTH_REQUIRE_EMAIL_VERIFY`) flip on in v1.x with no code changes required.

## License & ownership

Proprietary. Operated by Kentro on behalf of customer engagements.
