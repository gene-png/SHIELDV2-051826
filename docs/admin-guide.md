# Admin guide (Kentro consultants)

> Stub. Lands during §9 (admin + reviewer surfaces).

## Daily flow (planned)

1. **`/admin/queue`** — triage: New leads, Waiting on us, Active. Failed jobs banner at top.
2. **`/admin/client`** — open the client profile, review intake.
3. **`/admin/services/<type>`** — work the active engagement (Tech Debt, Zero Trust, CSF, ATT&CK).
4. **`/admin/deliverables`** — release when ready. Reviewer must approve before release.
5. **`/admin/audit`** — append-only audit log; UTC + local timestamps.

## Operational notes

- All AI output is marked draft until you approve it. Drafts never reach the client.
- Mandatory redaction preview runs on the first LLM call per engagement.
- Filenames are generated centrally — never hand-type a deliverable filename.
