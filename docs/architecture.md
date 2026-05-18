# Architecture

> Stub. Fleshes out during §3 (foundational infrastructure). See [`execution-plan.md`](execution-plan.md) for the live build plan.

## Service map

```
                     ┌─────────┐
   User browser ───▶ │  web    │ Next.js 14 App Router
                     └────┬────┘
                          │ REST + OIDC bearer
                     ┌────▼────┐
                     │  api    │ FastAPI / Python 3.12
                     └────┬────┘
              ┌───────────┼───────────┬───────────┐
              ▼           ▼           ▼           ▼
         ┌────────┐  ┌────────┐  ┌────────┐  ┌──────────┐
         │   db   │  │ redis  │  │ minio  │  │ keycloak │
         │ pg 16  │  │ queue+ │  │ s3+kms │  │   oidc   │
         │        │  │ cache  │  │ stub   │  │          │
         └────────┘  └───┬────┘  └────────┘  └──────────┘
                         │
                    ┌────▼────┐
                    │ worker  │ Celery — AI jobs, exports, redaction
                    └─────────┘
```

## Key boundaries

- **Single-tenant per deployment.** Each deployment is its own FedRAMP boundary. `client_id` carried on every row for defense-in-depth and future multi-tenancy. No cross-deployment data path.
- **Redaction is a security boundary, not a step.** Every outbound LLM call routes through `apps/api/app/ai/egress.py`, which wraps `redact.py`. The redaction event is logged in `artifact_redactions`.
- **Append-only audit log.** Postgres trigger rejects `UPDATE`/`DELETE` on `audit_entries`. Every state change writes a row.
- **AI output starts as draft.** Marked `consultant_approved` only after a consultant explicitly approves it. Released to the client only when the consultant releases the deliverable.

Detailed layering, request flow, and component contracts will land here as §3 ships.
