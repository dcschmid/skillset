# Quality Gates & Scoring

Score only what was verified. Each category: points per check with cited
evidence (file/test/command output). Unevaluated ⇒ `NOT TESTED`, excluded
from denominator, noted in report. Target for "production-ready" claim:
**≥ 90/100 + all hard gates green.**

## Rubric

| Category | Pts | Checked items (evidence required) |
|---|---:|---|
| Architecture & maintainability | 15 | clear module boundaries (3) · no god-modules/duplication of policy (3) · config validated at boot (3) · deps direction one-way (3) · docs/runbook current (3) |
| API design & contracts | 15 | resource+status discipline (3) · RFC 9457 errors everywhere (3) · pagination/bounds (3) · spec exists+CI-checked+client-gen builds (3) · versioning/deprecation path (3) |
| Database design & integrity | 15 | FKs/constraints in DB (3) · indexes match queries, plans clean (3) · txn+concurrency strategy stated (3) · migrations expand-contract+tested (3) · tenancy scoping in schema (3) |
| AuthN & AuthZ | 15 | modern auth lib+flows per authentication.md (5) · object/tenant checks every route, tests pass (5) · session/token lifecycle incl. revocation (5) |
| Security | 15 | injection-free data access (3) · input validation+mass-assignment guard (3) · secrets out of repo/logs (3) · TLS/headers/CORS/CSP surface (3) · deps scanned, majors tracked (3) |
| Performance & reliability | 10 | baselines+after measured (4) · timeouts/retries/breakers on outbound (3) · pools/queues bounded+observed (3) |
| Testing | 10 | unit+integration+API+migration+authz matrix green (5) · fixes carry regression tests (3) · CI runs them (2) |
| Observability & docs | 5 | structured+redacted logs, request ids (2) · RED metrics+health/readiness (2) · README/runbook accurate (1) |

## Hard gates (block positive release verdict regardless of score)

1. confirmed exploitable vuln unfixed (hand ultimate-security-hardening result)
2. proven or probable data loss (migration/backfill/undeclared nullable)
3. required suite failing or absent where required (migrations untested,
   authz matrix missing)
4. prod mutation executed without approval / secrets leaked in output
5. unverified perf claim presented as verified

## Verdict ladder

`PASS` = ≥90 + gates green + every category has evidence · `CONDITIONAL`
= ≥75, gaps listed with exact next command · `FAIL` = gates red ·
`INCOMPLETE` = tool/env missing ⇒ category NOT TESTED, never upgraded to
pass. Never score a category whose runner couldn't execute.
