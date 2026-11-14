# Risk scoring and prioritization

Priority = f(technical severity, reachability, exploit preconditions,
existing mitigations, KEV/EPSS, business context) — never CVSS alone.

## Severity ladder

| Level | Meaning here | Fix bar |
|---|---|---|
| CRITICAL | Unauth RCE, bulk data exposure, auth bypass on prod path | fix before release, blocking |
| HIGH | Authz gap on real path, injectable reachable query, secret in shipped artifact | fix now (safe) / approve diff |
| MEDIUM | Header gaps, weak-but-bounded issues, missing rate limits | fix in cycle |
| LOW | Defense-in-depth misses, informational leaks w/o data | backlog, note |
| INFORMATIONAL | Hardening advice, no direct vector | note |

## Confirmability statuses (mandatory per finding)

- **Confirmed** — evidence in code/scan + reachability traced. May drive fixes.
- **Likely** — pattern is wrong but reachability/exploit unproven. Fix if safe; never claim exploit.
- **Needs Manual Review** — needs runtime/data/approval to judge.
- **False Positive** — verified harmless; record the reason (prevents re-noise).
- **Not Applicable** — technology/flow absent from this project.

## Scoring procedure (per finding)

1. Base: CWE/OWASP category typical severity + CVSS if a CVE exists.
2. Modifiers:
   - reachability: deployed path ×1, dev-only ÷2, unreachable dep ÷4
   - preconditions: unauth ×1, user interaction ÷2, auth+privilege ÷4
   - existing compensating control (WAF, framework escaping, gateway authz): downgrade one step, name it
   - KEV hit or EPSS ≥ 0.9: upgrade one step (active exploitation beats paper score)
3. Business context: user data, payments, multi-tenancy ⇒ upgrade one step on confirmed authz/data findings.
4. Result: severity + one-line justification. Both go in the report; a score without justification is invalid.

## Tie-breaks (what gets fixed first)

1. Confirmed reachable authz/auth break in prod path
2. Confirmed injection in prod path
3. Live secret in VCS + committed (rotation needed)
4. KEV/EPSS-high dependency on deployed path
5. Everything else by severity, then fix-cost.

Real rule: a confirmed IDOR at CVSS 7 out of the door beats a CVSS 9.8 dep
whose vulnerable function this project never calls. Write the reachability
argument into the finding.

## Release gate mapping

| State | Verdict |
|---|---|
| 0 confirmed CRITICAL/HIGH open, all critical checks ran | PASS |
| LOW/MEDIUM open, or fixed-awaiting-retest remains | PASS WITH WARNINGS |
| Confirmed CRITICAL/HIGH open or fix failed retest | BLOCKED |
| Scanner/tool gap on required coverage | INCOMPLETE |
