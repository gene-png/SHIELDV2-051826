# Security

## Reporting

Security issues are reported privately to the SHIELD operations team at Kentro. Do not open public GitHub issues for vulnerabilities.

## Security posture summary

Full detail lives in [`docs/security.md`](docs/security.md). Highlights:

- **Single-tenant per deployment.** Each deployment is its own FedRAMP boundary. There is no cross-tenant data path.
- **Append-only audit log.** `audit_entries` is enforced append-only by a Postgres trigger that rejects `UPDATE` and `DELETE`. Every state change writes a row.
- **Mandatory PII redaction before every LLM call.** Implemented in `apps/api/app/ai/redact.py`; bypassing it is impossible (every outbound LLM call routes through `apps/api/app/ai/egress.py`). Redaction events are logged in `artifact_redactions` with counts per PII kind.
- **Encryption.** S3 (or MinIO in dev) uses CMK-style server-side encryption. Postgres uses TLS in transit; volume encryption is environment-provided.
- **Auth.** Keycloak-based OIDC. 15-minute access JWT, 30-minute idle timeout, daily forced re-auth. Account lockout after 10 failed attempts in 15 minutes. MFA and email verification are feature-flagged off for v1 (compensating controls listed) and flip on in v1.x with no code changes.
- **No stack traces to users.** A global FastAPI exception handler returns `{error, correlation_id}` JSON. `DEBUG=True` is refused outside `127.0.0.1`.
- **CSP, HSTS, X-Frame-Options, Referrer-Policy, Permissions-Policy** all set via `apps/web/next.config.mjs`.
- **CI gates.** `gitleaks`, `bandit`, `pip-audit`, `npm audit`, `trivy` run on every PR.

## Risks explicitly accepted by the customer for v1

Documented in `reference-docs/SHIELDv2_README.docx` and the Master Spec §1 / §4.4 / §4.5:

1. **Commercial LLM provider may not be FedRAMP-authorized.** Egress may leave the FedRAMP boundary. Mandatory PII redaction is the primary compensating control.
2. **MFA and email verification deferred for v1.** Compensating controls listed above.

## Secret handling

- `.env` is gitignored. Never commit real keys.
- The repository is scanned by `gitleaks` on every commit and PR.
- API keys are read from environment variables at process start. Never logged. The structured logger has an allowlist that strips `password`, `Authorization`, `token`, and `Cookie`.
