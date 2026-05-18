# QA Checklist — pre-merge / pre-handoff

> Goal: nothing reaches "ready to test" without passing this checklist. Every
> commit message claiming a feature is "done" must reference which sections
> were exercised.

Maintainer: keep this checklist short enough that running it every time is
realistic. When a section grows past one screen, split it into its own page.

---

## Process for every feature

For any commit that ships UI or an API endpoint:

1. **Code-trace pass** — read the full call path end-to-end. For UI: trigger →
   handler → API client → router → service → DB → response → render.
   Note any silent-failure points (disabled buttons, swallowed errors,
   `if (!x) return` early-exits).
2. **Smoke pass** — start the stack locally (`bash scripts/dev-web.sh` + API
   container running) and click through the relevant section of this file.
   Tick the boxes. Paste outputs into the commit message under a `## QA`
   heading.
3. **Test pass** — at minimum, `docker compose exec api pytest -m unit` must
   still be green. If the feature touched a router, add a smoke test in
   `apps/api/tests/unit/test_routes_smoke.py` so a future rename doesn't
   silently break the contract.
4. **Linkrot pass** — every `<Link href=...>` and `<a href=...>` introduced
   must resolve to a real route. Run the search at the bottom of this file.

If any box can't be ticked, mark the feature as "partial" in the commit and
the build report — don't claim done.

---

## Per-route checklist (run after stack is up)

### Auth surface (Master Spec §6.1 / §5)

- [ ] `/` — placeholder landing page renders.
- [ ] `/sign-up` — page loads, all fields editable, password meter updates as
      you type. With **empty fields + click**: a clear inline error appears
      (no silent disabled button). With **valid input**: account is created
      and you land on `/intake`. With **duplicate email**: error from API is
      surfaced.
- [ ] `/sign-in` — page loads, empty submit shows API "invalid email or
      password" (not a 500). Valid creds redirect to `/home`. 10 wrong
      passwords in 15 min triggers lockout (HTTP 429) and the message says
      so.
- [ ] `/accept-invite/<token>` — same UX rules as `/sign-up`. With an invalid
      token, the API returns a clear error and the form surfaces it.
- [ ] `/verify/<token>` — renders the v1 no-op explanation.
- [ ] `/mfa/enroll` — renders null (intentional for v1). Linking here from
      another page shouldn't 404; it should render empty.
- [ ] `/sign-out` — redirects to `/sign-in` and writes an `audit_entries` row
      with `action='user.sign_out'`.

### Client chrome (Master Spec §5.1)

- [ ] Sidebar entries: Home / My services / Documents / Messages / Team /
      Settings — every one resolves to a 200 OK page (no 404s).
- [ ] Sign-out link in sidebar footer fires the GET handler.
- [ ] Top utility area shows the user's display name + email.

### Intake wizard (Master Spec §6.2)

- [ ] `/intake` → redirects to `/intake/i1-services`.
- [ ] **I1**: clicking each service card toggles selection. Selecting Zero
      Trust reveals the framework radio. Clicking "I'm not sure" disables
      the four service cards visually. Empty submit shows the validation
      error inline.
- [ ] **I1B**: form renders only when reached from I1's "I'm not sure". On
      submit, you land at `/home?consultation=submitted` and a
      `consultation_requests` row exists.
- [ ] **I2**: autosave indicator updates to "Saved N seconds ago" after a
      blur. Empty legal name + click shows the validation error.
- [ ] **I3**: "Add another system" appends a card. "Remove" works on any
      card except the last. Continue with at least one named system.
- [ ] **I4**: placeholder; Continue moves to I5.
- [ ] **I5**: placeholder with the redaction-disclosure copy; Continue
      moves to I6.
- [ ] **I6**: Submit transitions all NEW services to INTAKE_PENDING, writes
      an `intake.submitted` audit row, redirects to `/home?intake=submitted`.

### Services + dashboards

- [ ] `/home` empty state (no services yet): renders "Up next: intake" CTA.
- [ ] `/home` with at least one service: renders the service grid with
      status pills. With at least one released service: renders the gradient
      hero band.
- [ ] `/services` lists every service; empty state shows CTA to intake.
- [ ] `/services/tech-debt`, `/services/zero-trust`, `/services/csf`,
      `/services/attack-surface` all render the shell.
- [ ] `/documents`, `/messages`, `/team` render placeholders without errors.
- [ ] `/settings` shows the current user's name/email/role.
- [ ] `/settings/password` rejects mismatch / weak passwords with inline
      errors. Accepts a valid rotation and lands back on `/settings`.

### API surface (run via `docker compose exec api pytest -m unit`)

- [ ] `tests/unit/test_routes_smoke.py` passes.
- [ ] `tests/unit/test_health.py` passes.
- [ ] `tests/unit/test_redactor.py` passes.

### Backend audit trail

- [ ] Every state-changing endpoint writes an `audit_entries` row. Check:
      ```sql
      SELECT action, target_type, count(*) FROM audit_entries GROUP BY 1,2;
      ```
- [ ] `UPDATE audit_entries SET action='tampered'` raises an exception
      (Postgres trigger).

---

## Linkrot search

Run from the repo root before every commit that touches the web app:

```bash
# Every Link/anchor target should be a known route or external URL.
grep -RoE 'href="(/[^"]*)"' apps/web/app apps/web/components 2>/dev/null \
  | sort -u

# Every API client call should target an existing FastAPI route.
grep -RoE '"/api/[^"]*"' apps/web/lib 2>/dev/null | sort -u
```

Compare against:

```bash
# Known web routes (page.tsx + route.ts under apps/web/app)
find apps/web/app -name 'page.tsx' -o -name 'route.ts' \
  | sed 's|apps/web/app||; s|/page.tsx||; s|/route.ts||' | sort

# Known API routes
grep -RoE '@router\.(get|post|put|delete|patch)\("[^"]+"' apps/api/app/api/routers \
  | sed 's|.*("|"|' | sort -u
```

If a `href=` or `/api/...` reference doesn't show up in the known-routes
output, fix it before merging.
