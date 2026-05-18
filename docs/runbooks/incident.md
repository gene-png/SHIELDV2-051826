# Runbook — Incident response

> Stub. Lands during §16 (documentation) before first production deployment.

## When this fires

- A security event detected by audit log, alerting, or external report.
- A data-handling anomaly (unexpected egress, redaction bypass, audit-log write failure).

## First five minutes

1. Acknowledge the page. Set incident status in the on-call tracker.
2. Stop the bleeding — pause Celery workers if AI egress is suspect:
   ```bash
   docker compose stop worker
   ```
3. Preserve evidence — snapshot the audit log:
   ```bash
   docker compose exec api python -m app.scripts.snapshot_audit
   ```
4. Page Kentro security lead.

## Diagnose

- Audit log (`audit_entries`, append-only).
- Structured JSON logs with correlation IDs.
- LLM call records (`llm_calls`) — provider, model, tokens, redaction summary.

## Remediate

Track every action in the audit log. Update this runbook with the post-mortem.
