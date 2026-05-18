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

### Option A — VS Code Dev Containers (recommended)

1. Open the repo in VS Code with the **Dev Containers** extension installed.
2. When prompted, **Reopen in Container**. VS Code builds the `web` service and brings up all 8 compose services (db, redis, minio, keycloak, mailhog, api, worker, web).
3. Once VS Code attaches, open the integrated terminal and run:
   ```bash
   bash scripts/dev-web.sh
   ```
   First run installs pnpm dependencies (~3–5 minutes). Subsequent runs start Next.js immediately.
4. In a second terminal:
   ```bash
   docker compose logs -f api
   ```
   to watch the API service install + migrate + start (~2–3 minutes first run).
5. Open http://localhost:3000 once you see `▲ Next.js 14.2.x` and `- Local: http://0.0.0.0:3000` in the web terminal.

### Option B — plain Docker Compose

If you don't use VS Code Dev Containers, you can still run the stack from a host shell:

```bash
cp .env.example .env
docker compose up -d db redis minio keycloak mailhog
docker compose up -d --build api worker
# Wait until http://localhost:8000/health returns 200
docker compose run --service-ports --rm web bash scripts/dev-web.sh
```

### URLs once everything is up

| Service           | URL                          |
| ----------------- | ---------------------------- |
| Web (Next.js)     | http://localhost:3000        |
| API (FastAPI)     | http://localhost:8000/docs   |
| Keycloak (admin)  | http://localhost:8080        |
| MinIO (console)   | http://localhost:9001        |
| MailHog (UI)      | http://localhost:8025        |
| Postgres          | postgres://localhost:5432    |

## Troubleshooting

- **`http://localhost:3000` blank or "site can't be reached":** the web container is sleeping by design. Run `bash scripts/dev-web.sh` inside the web container (VS Code terminal). Wait for the `Local: http://0.0.0.0:3000` line.
- **`http://localhost:8000/health` refused:** api container is still installing or running migrations. `docker compose logs -f api` will show progress; first run takes 2–3 minutes for pip install + WeasyPrint deps.
- **`alembic` fails on first migration:** confirm `db` is healthy first — `docker compose ps db` should show `healthy`.
- **Stale `node_modules` after a dependency change:** `docker compose down -v` clears the named volume; re-run `bash scripts/dev-web.sh`.
- **Keycloak login loop:** the realm imports admin/admin on first boot; full OIDC sign-in via Keycloak ships in a follow-up, so v1 uses SHIELD-issued JWTs (Credentials provider). You shouldn't need Keycloak to sign in for v1.

## Running tests

```bash
# API unit tests (inside the api container)
docker compose exec api pytest -m unit
```

End-to-end + accessibility tests land with §13 of the execution plan.

## Documentation

- [`docs/execution-plan.md`](docs/execution-plan.md) — single dependency-ordered build plan
- [`docs/qa-checklist.md`](docs/qa-checklist.md) — **must run before claiming a feature is done**
- [`docs/architecture.md`](docs/architecture.md) — system architecture
- [`docs/data-model.md`](docs/data-model.md) — schema overview
- [`docs/security.md`](docs/security.md) — security posture, redaction, audit
- [`docs/admin-guide.md`](docs/admin-guide.md) — Kentro consultant guide
- [`docs/client-guide.md`](docs/client-guide.md) — client-facing guide
- [`docs/runbooks/`](docs/runbooks/) — operational runbooks (incident, backup, key rotation, etc.)

## Development discipline

Every feature commit must:

1. **Code-trace** the full call path (UI handler → API client → router → service → DB → response → render). Note silent-failure points (disabled buttons, swallowed errors, early-return guards).
2. **Smoke test** by running the relevant section of [`docs/qa-checklist.md`](docs/qa-checklist.md).
3. **Unit-test** at minimum the route surface — `docker compose exec api pytest -m unit` must stay green; new endpoints must show up in `apps/api/tests/unit/test_routes_smoke.py`.
4. **Linkrot search** — every `<Link href=…>` must resolve to a real route. Commands at the bottom of the QA checklist.

If a feature can't pass all four, the commit message says "partial" — not "done".

## Risk acceptance log

Per the Master Spec and the SHIELD v2 README, two risks are explicitly accepted for v1:

1. **Commercial LLM provider may not be FedRAMP-authorized.** Egress may leave the FedRAMP boundary. Mandatory PII redaction (`apps/api/app/ai/redact.py`) is the primary control. See [`docs/security.md`](docs/security.md).
2. **MFA and email verification deferred for v1.** Compensating controls: 15-minute JWT lifetime, 30-minute idle timeout, daily forced re-auth, account lockout after 10 failed attempts in 15 minutes. Feature flags (`SHIELD_AUTH_REQUIRE_MFA`, `SHIELD_AUTH_REQUIRE_EMAIL_VERIFY`) flip on in v1.x with no code changes required.

## License & ownership

Proprietary. Operated by Kentro on behalf of customer engagements.
