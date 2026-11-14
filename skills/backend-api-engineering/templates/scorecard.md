# Backend score — <project> @ <date>  (evidence required per line)

| Category | Pts | Evidence (file/cmd/test) | Status |
|---|--:|---|---|
| Architecture & maintainability | /15 | | PASS/GAP/NOT TESTED |
| API design & contracts | /15 | | |
| Database design & integrity | /15 | | |
| AuthN & AuthZ | /15 | | |
| Security | /15 | | |
| Performance & reliability | /10 | | |
| Testing | /10 | | |
| Observability & docs | /5 | | |

**Score: N/100** (N/A excluded from denominator) · Target for prod: ≥90.

## Hard gates (verdict-blocking)
- [ ] no confirmed exploitable vuln open · [ ] no proven/probable data loss
- [ ] required suites green · [ ] no unapproved prod mutation · [ ] no unverified perf claims

## Verdict
PASS ≥90+gates · CONDITIONAL ≥75 + next commands · FAIL gates red · INCOMPLETE env gaps

## Open items (exact next command each)
1. <cmd> — <why>
