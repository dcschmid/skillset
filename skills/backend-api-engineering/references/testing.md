# Backend Testing

Load for VERIFY / CREATE / FIX. Cross-cutting test *strategy* (suite
architecture, CI lanes, E2E across frontend+backend) is
`ultimate-testing-qa`'s; this file is the backend layers' share and must
not re-invent their harness — extend the project's runner.

## Layer map (project runner of record: pytest / vitest / jest / go test /
cargo test / JUnit / PHPUnit)

| Layer | Backend obligation |
|---|---|
| Unit | pure domain/service logic, validation, mappers; no I/O; fast |
| Integration | real DB via Testcontainers/embedded/docker-compose or CI service; repositories, transactions, constraints |
| API contract | requests/responses against OpenAPI/handler; status codes, error shape (RFC 9457), auth failures |
| Migration | up/down on empty+populated fixture; parity counts; see database-migrations.md |
| Auth/AuthZ | matrix per route: anon/user/other-user/other-tenant/admin (see authorization.md tests) |
| Concurrency | race on unique/indexed writes, idempotency replay, optimistic conflict |
| Load | k6/Gatling/autocannon smoke thresholds, not tuning, unless OPTIMIZE |

## Mandatory scenario list (audit against existing suite)

happy path per endpoint · validation failure (422 shape) · 404/403 split ·
expired/invalid token · pagination bounds · empty result · duplicate
submit/idempotency · rollback on mid-transaction failure · queue retry +
DLQ · timeout/duplicate delivery handling (consumer idempotent) ·
tenant isolation · large payload caps. Missing scenario = test finding,
`NOT TESTED` in score.

## Quality bar

isolated+reseeded fixtures, deterministic time, no prod data/creds
(ever), factories over copies, one assert-theme per test, test names state
behavior, failures show before/after state. Flaky test = finding, isolate
root cause (order, sleep, shared state, seed).

## Regression protocol (FIX mode)

failing repro test first (fails on bug) → fix → passes → run neighboring
suite (no new breaks) → keep the test in the suite. Without a runner
available: exact manual payload + expected/actual recorded in the change
note, status `NOT TESTED (manual)`.

## Handoffs

web/E2E/console/network → ultimate-testing-qa (they own Playwright/Vitest
browser lanes; backend provides seed + API fakes contract). Security
regressions (injection payloads, authz bypasses) may join backend tests;
deep attack-surface scans → ultimate-security-hardening. Load *reports*
shared with performance lane (performance.md reporting format).
