# Workflow: create (new backend / API / feature)

Input: requirements (functional + at least: scale guess, data shape, auth
need). Output: working, tested, integrated code + spec.

1. **Decide stack (only if new).** One table: language/framework per team
   knowledge + hosting + data shape. Simplest sufficient option; state the
   reason in README. Reuse project defaults if anything exists.
2. **Design contracts before code.** Resources/schema/tenants →
   `references/api-design.md` bar; write/commit spec (OpenAPI/proto/schema)
   + `scripts/validate-openapi.py` green. Error shape RFC 9457 from the
   first route.
3. **Data layer.** `references/database-engineering.md`: keys/FKs/
   constraints/tenant column; migration in the project's tool, up+down
   tested on scratch DB (database-migrations.md protocol).
4. **AuthN/AuthZ.** Pick per authentication.md table; authz = ownership
   check in the service layer (authorization.md), wired before the first
   handler ships.
5. **Handlers → service → repo.** Validation at edge, DTOs out; project
   error/DI/config idioms reused (prime rule 2). One vertical slice
   end-to-end before breadth.
6. **Tests with the slice.** testing.md layer map + mandatory scenarios;
   authz matrix green; migrations tested; CI lane extended so green is
   automatic, not promised.
7. **Ops floor.** health/readiness, structured+redacted logs, RED metrics
   (observability.md); Docker/procfile per deployment.md *only* if the
   project ships them; docs updated.
8. **Verify.** full suite + spec validation + boot check → report files,
   commands, score if requested (quality-gates.md). No "created" without
   a green run.
