---
name: backend-api-engineering
description: >
  Universal backend & API engineering for ANY stack and ANY project age (Node/Fastify/
  NestJS/Express/Hono, Astro endpoints, Next.js handlers, Bun/Deno; Python FastAPI/Django/
  DRF/Flask; Go, Rust Axum/Actix, Spring Boot, Ktor, ASP.NET Core, Laravel/Symfony;
  PostgreSQL/MySQL/SQLite, MongoDB/Redis/search/vector; REST/GraphQL/gRPC/WebSocket/SSE).
  Modes: CREATE new backends, AUDIT existing ones, FIX real bugs, OPTIMIZE queries/APIs/
  latency, implement AUTH (sessions/OAuth/OIDC/JWT/RBAC/ABAC/IDOR checks), engineer
  DATABASE schemas and safe MIGRATIONS, design ARCHITECTURE, prepare DEPLOY, VERIFY with
  tests. Profiles the project first, reuses its stack, ships working code, proves every
  claim with measurements or test output. Baselines: RFC 9457 errors, OpenAPI (tool-
  supported version), OWASP API Security Top 10, expand-and-contract migrations,
  baseline→change→re-measure performance. Detects and fixes (authz gaps, N+1, missing
  indexes, unvalidated input, missing tenancy filters) instead of only reporting. Hands
  deep security audits to ultimate-security-hardening, cross-cutting test strategy to
  ultimate-testing-qa, generic refactors to ultimate-code-quality-refactoring — never
  duplicates them. Unverified = NOT TESTED, never "working".
---

# Backend & API Engineering (universal)

Core loop: **PROFILE → MODE → WORK → VERIFY → REPORT**. Report-only runs on
fixable problems are a failure of the skill: confirmed + safely fixable =
fixed and re-tested.

## Prime rules

1. **Profile before touching.** Run `scripts/detect-project.sh <proj>` (or
   manual equivalent), build the architecture profile, classify the project
   (new / productive / legacy / partially modernized). Missing info =
   `unknown`, never assumed fact.
2. **Reuse the project's stack.** Existing framework/ORM/tooling stays
   unless there is a stated, measured reason to change. No framework swaps,
   no new infra (queues, microservices, JWT) without a requirement.
3. **Simplest architecture that meets the requirements.** Modular monolith
   first; microservices need a team/scale reason. Simplest auth that is safe:
   server-side sessions are a valid answer for classic web apps.
4. **Fix, don't decorate.** Replace the broken query/handler/migration with
   a minimal diff; preserve behavior that is not the target of the change.
   No security controls disabled to "make it work".
5. **Verify or say so.** Every optimization needs baseline→after under
   comparable conditions. Every fix needs a regression test or exact manual
   repro recorded. Untested = `NOT TESTED`; tool gap = `INCOMPLETE` — never
   PASS, never invented numbers.
6. **Production databases are sacred.** Never drop/reset/truncate prod data,
   run prod migrations, or copy prod data for tests without explicit
   approval. Migrations: expand-and-contract, reversible or with forward-fix
   plan, tested on a scratch DB first.
7. **Login ≠ authorization.** Every resource route gets an object-level
   (and tenant-level) ownership check; IDOR/BOLA is a first-class audit
   target.
8. **Secrets and PII stay out of logs, reports, git.** Structured findings
   cite location + kind, values masked.

## Mode gate (auto-pick from the task; state the pick)

| Task phrasing | Mode | Workflow |
|---|---|---|
| "build/create a backend/API…", new project | CREATE | `workflows/create.md` |
| "check/audit my backend", "find problems" | AUDIT | `workflows/audit.md` |
| "fix this bug/error/500", concrete failure | FIX | `workflows/fix.md` |
| "optimize", "too slow", "N+1", "p99" | OPTIMIZE | `workflows/optimize.md` |
| "login/auth/permissions/roles/tenants" | AUTH | refs: authentication + authorization |
| "schema/migrations/queries/indexes" | DATABASE | refs: database-engineering + database-migrations |
| "add/revise endpoints, OpenAPI, GraphQL" | API | ref: api-design.md |
| "architecture/monolith/services/workers" | ARCHITECTURE | ref: architecture.md |
| "dockerize/deploy/production-ready" | DEPLOY | ref: deployment.md |
| "migrate stack/DB without data loss" | MIGRATE | `workflows/migrate.md` |
| "verify tests/contracts/migrations" | VERIFY | `workflows/verify.md` |

Modes compose (AUDIT→FIX→VERIFY is the default for "repair my backend"),
but never load all references at once — load the ones the mode names.

## Work sequence (binding)

1. **PROFILE.** Detection output → architecture profile (§ Profile format).
   For existing projects `git status` first; uncommitted user changes stay.
2. **LOAD.** SKILL.md + mode workflow + the 1–3 references it names. Deep
   security → `ultimate-security-hardening`; site-wide test strategy →
   `ultimate-testing-qa`; non-backend refactor → `ultimate-code-quality-refactoring`.
3. **WORK.** Smallest coherent change set. New features integrate into the
   project's existing routes, DI, config, error handling, test runner —
   never beside them.
4. **VERIFY.** Run the project's checks on touched code: unit → integration
   → API/migration tests → build. Add regression tests for bugs fixed.
   Fresh measurement for perf work. Failures loop back to 3.
5. **REPORT.** Findings/change list with evidence, score when asked (rubric
   below), open items as `NOT TESTED`/`INCOMPLETE`.

## Profile format (compact, from detect-project.sh + reading)

`root · languages+versions · frameworks · package managers/lockfiles ·
runtime · API surfaces (REST/GraphQL/gRPC/ws, spec files) · DB engines +
ORM + migration tool · auth (session/JWT/OAuth lib) · jobs/queues · deploy
(Dockerfile/compose/systemd/proxy/k8s) · CI · test runners + coverage
gaps · config/env layout · known risks`. Classify: `new | productive |
legacy | partially-modernized` — evidence, not vibes.

## Audit findings & score

Findings: severity `CRITICAL|HIGH|MEDIUM|LOW`, each with file+component,
concrete defect, evidence, root cause, impact, fix, change risk, validation
method (see `templates/finding.json`). Score on request (rubric in
`references/quality-gates.md`): Architecture 15 · API 15 · DB 15 · AuthN/
AuthZ 15 · Security 15 · Perf/Reliability 10 · Testing 10 · Observability/
Docs 5. Score only what was checked; N/A sections marked; prod-readiness
target ≥ 90/100 **plus** all hard gates — a confirmed critical vuln, proven
data loss, or failed required check blocks a positive verdict regardless of
points.

## Hard stops (approval required, never auto-applied)

Prod DB drops/resets/destructive DDL · prod migration execution · prod
deploys · secrets rotation · deleting lockfiles/tests · framework swaps ·
new infrastructure (broker, cache, k8s) without stated need · API-breaking
contract changes without deprecation path · copying prod data into test
environments.

## Stack ground truth (probe live; these are orientation, not law)

Re-check versions against the project's lockfiles and official docs when
online. Deep guidance per area, loaded per mode (progressive disclosure):
`references/api-design.md` · `references/authentication.md` ·
`references/authorization.md` · `references/database-engineering.md` ·
`references/database-migrations.md` · `references/architecture.md` ·
`references/security.md` · `references/performance.md` ·
`references/observability.md` · `references/testing.md` ·
`references/deployment.md` · `references/background-jobs-messaging.md` ·
`references/quality-gates.md` (scoring rubric).

Scripts (run from this skill dir): `scripts/detect-project.sh <proj>`
(profile, read-only), `scripts/validate-openapi.py <spec> [--baseline old]`
(structure + breaking-change diff), `scripts/migration-review.sh <dir>`
(destructive-DDL/order/reversibility lint). Self-test:
`python3 tests/test_skill.py`.
