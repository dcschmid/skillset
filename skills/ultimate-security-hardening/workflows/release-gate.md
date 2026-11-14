# Workflow: release-gate (RELEASE MODE)

Pre-release security verdict. Reads current findings + verification state;
emits PASS / PASS WITH WARNINGS / BLOCKED / INCOMPLETE. Configurable via
project's `security-config.yml` thresholds (templates/).

## Gate inputs

1. latest `security-findings.json` (+ this session's audit deltas)
2. verification state (`security-test-results.md`) — FIXED needs re-scan proof
3. dependency re-audit on current lockfiles (fresh advisories arrive daily)
4. secret re-scan of tracked files + staged history
5. tool ledger: every required lane RAN or gap documented
6. open-exception list: time-boxed, owner, expiry (configurable policy)

## Decision (first match wins)

| Verdict | Condition |
|---|---|
| **BLOCKED** | confirmed CRITICAL/HIGH open · fix failed re-test · CRITICAL dep KEV hit on deployed path · live secret in VCS unresolved |
| **INCOMPLETE** | required lane missing/errored (scanner absent, app not startable, offline advisories) — never launder into PASS |
| **PASS WITH WARNINGS** | only MEDIUM/LOW open · PARTIALLY FIXED items with named next step · exceptions unexpired with owner |
| **PASS** | zero open confirmed findings, all lanes green, re-scans clean |

## Output (report + decision file)

verdict · checked commit · findings by severity/status · fixes shipped vs
pending · tests run · lanes skipped · residual-risk one-liner each ·
next action per open item. Blocking findings carry the approval path
(owner + what unblocks). No release-blocking on draft standards or
unconfirmed (`Likely`+) findings; `Confirmed`+ only (risk-scoring.md).

## Optional automation

Emit a CI job that runs the same ladder (ci-cd-security.md lane `release`)
— additive, threshold-configurable, never silently loosens to green.
