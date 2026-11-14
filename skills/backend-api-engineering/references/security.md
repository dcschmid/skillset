# Backend Security (implementation layer)

Load for any mode shipping server code. Full audits, threat modeling, and
deep vulnerability work belong to `ultimate-security-hardening` — hand off
there; this file is what backend code must do by default so audits stay
clean. OWASP API Security Top 10 is the checklist.

## Input & query safety

- Validate at the boundary: schema validator (zod/pydantic/jqwt/hibernate-
  validator/…) with allowlisted fields; reject or strip unknown keys;
  bound string sizes, array lengths, page sizes (server cap).
- Parameterized queries only — ORM/placeholder style of the project.
  Dynamic identifiers (order-by, table names) from a whitelist map, never
  string-concatenated. NoSQL: query operators sanitized (`$where`, `$gt`
  objects from user JSON).
- File paths from user input resolved under a base dir (allowlist roots);
  uploads streamed with size/type limits; deserialization restricted to
  expected types (no pickle/Java-native/object graphs from clients).
- Mass assignment: DTO allowlists on every write path (API-3 style finding
  in every audit).

## Transport & config

- TLS terminating at proxy or app, HSTS where proxy-owned; secure cookie
  flags; CORS explicit origin list + verb/header allowlists (no `*` with
  credentials); response headers: `X-Content-Type-Options`, JSON API
  `Content-Type` explicit; no framework debug/error pages in prod.
- Rate limits on auth + expensive endpoints (per token+IP), 429+Retry-After.
- Secrets: env/secret-store; not in repos, logs, error bodies, or client
  payloads; `.env.example` has no real values.

## Data handling

- Passwords hashed (see authentication.md); tokens encrypted at rest where
  store supports; PII fields minimized in responses and logs
  (see observability.md redaction).
- Error responses: RFC 9457, no stack/SQL/dependency versions to clients;
  full detail to logs with request id.

## Dependencies & supply chain

- Lockfiles committed; updates within the toolchain's supported range;
  advisory scan (osv-scanner/npm audit/pip-audit/snyk — whatever project
  has) reported as findings, majors = REVIEW REQUIRED.
- Self-hosted admin surfaces (phpMyAdmin, flower, adminer, dashboard) get
  authz + network scoping, not public ports.

## Handoff rules

Confirmed/exploitable findings, crypto migrations, secret rotation, WAF/
proxy changes → `ultimate-security-hardening` (approval gates per its
rules). Backend scope keeps: writing secure-by-default code paths, adding
authz checks, regression tests, and the API-layer fixes their audit names.
Never weaken a control to unblock a test.
