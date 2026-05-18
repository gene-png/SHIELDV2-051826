# Security

> Companion to top-level [`../SECURITY.md`](../SECURITY.md). Operational detail below.

## Controls (current vs. target)

| Control | v1 | v1.x |
|---|---|---|
| Single-tenant per deployment | ✅ | ✅ |
| OIDC auth via Keycloak | ✅ | ✅ |
| Email + password sign-in | ✅ | ✅ |
| MFA enrollment | feature-flag off | flag on |
| Email verification | feature-flag off | flag on |
| 15-min access JWT | ✅ | ✅ |
| 30-min idle timeout | ✅ | ✅ |
| Daily forced re-auth | ✅ | ✅ |
| Account lockout (10 in 15 min) | ✅ | ✅ |
| Append-only audit log | ✅ (Postgres trigger) | ✅ |
| PII redaction before every LLM call | ✅ (mandatory) | ✅ |
| CMK-encrypted object storage | ✅ (MinIO dev / KMS prod) | ✅ |
| FedRAMP Moderate authorization | risk-accepted gap | required |
| No stack traces to user | ✅ | ✅ |
| CSP / HSTS / Frame-Options / Referrer-Policy | ✅ | ✅ |
| Dependency scan in CI | ✅ | ✅ |

## Risk acceptance log

See [`../DECISIONS.md`](../DECISIONS.md) and [`../reference-docs/SHIELDv2_README.docx`](../reference-docs/SHIELDv2_README.docx). Two risks explicitly accepted by Eugene Powell for v1: commercial LLM provider may not be FedRAMP-authorized; no MFA / email-verify in v1. Both have compensating controls + flip paths.

## Reporting

Private channels to Kentro operations. Do not open public GitHub issues for vulnerabilities.
