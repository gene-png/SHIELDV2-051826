# Data model

> Stub. The full SQLAlchemy schema and Alembic baseline land in §3.1.

Source of truth: [`../reference-docs/SHIELDv2_Master_Spec.txt`](../reference-docs/SHIELDv2_Master_Spec.txt) §11.

## Entities (planned)

| Table | Purpose |
|---|---|
| `users` | Identities. Role enum (admin/reviewer/client). MFA + email-verify columns present but unused in v1. |
| `user_invitations` | Hashed tokens with 7-day expiry, single-use. |
| `client` | Singleton row per deployment. Primary POC is a FK to `users`. |
| `service` | Engagement records. Type enum + framework enum (CISA/DoD for Zero Trust). |
| `systems` | In-scope systems (CSF / ZT). CSAM id, FIPS 199, ATO status. |
| `questionnaire_responses` | Per-question answers; evidence artifact IDs; N/A flag + reason. |
| `questions` | Static seed (CISA, DoD, CSF tier questionnaires). |
| `csf_subcategories` | 108-row static reference; IG metric alignment loaded from CSV. |
| `csf_tier_profile_entries` | Per-tier (HIGH/MOD/LOW) per-subcategory 5-dim scoring. |
| `csf_enterprise_entries` | Rollup via weighted-floor Rules 1–6. |
| `gaps` | Prioritized P1/P2/P3 with POA&M linkage. |
| `capability_list` / `capability_items` | Tech Debt inventory + AI extraction confidence. |
| `attack_techniques` | Vendored MITRE ATT&CK reference. |
| `attack_findings` | Per-technique coverage status + tool mappings. |
| `artifacts` | S3 keys with lineage JSONB. Origin immutability trigger. |
| `artifact_redactions` | PII strip counts per redaction event + FK to LLM call. |
| `llm_calls` | Provider, model, prompt version, tokens, status, mode (real/fixture). |
| `deliverables` | PDF + XLSX bundles, version, supersession. |
| `messages` | Thread-keyed (general or per-service). |
| `notifications` | Per-user inbox + read state. |
| `audit_entries` | Append-only via Postgres trigger. Correlation ID on every row. |
| `service_requests` / `consultation_requests` | "I'm not sure" intake path. |
| `reviewer_notes` | Separate store from consultant notes; reviewer-only visibility. |

Full ERD lands when §3.1 commits.
