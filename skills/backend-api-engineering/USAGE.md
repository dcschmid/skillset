# Using the `backend-api-engineering` skill in your agents

Framework-agnostic backend and API engineering: CREATE, AUDIT, FIX,
OPTIMIZE across Node (Fastify/NestJS/Express/Hono), Python
(FastAPI/Django/Flask), Go, Rust, Java/Kotlin, C#, PHP; SQL/NoSQL;
REST/GraphQL/gRPC/WebSocket/SSE. RFC 9457 errors, OpenAPI validation,
OWASP API Top 10, expand-and-contract migrations. Detects and fixes (authz
gaps, N+1, missing indexes, unvalidated input, missing tenancy filters)
instead of only reporting. Unverified = NOT TESTED, never "working".

## Install (this skill only)

```bash
tools/install-skills.sh backend-api-engineering
```

Symlinks into both host roots; remove with
`tools/uninstall-skills.sh backend-api-engineering`.

## Claude Code

Discovered from `~/.claude/skills/`; activates on backend/API work:

```
Use the backend-api-engineering skill: audit the Fastify service in
services/api — authz on every route, N+1 in the listing endpoints,
migration safety. Fix with tests, show measurements.
```

## Codex

Same content via `~/.agents/skills/`:

```
Use the backend-api-engineering skill: design the schema + expand-contract
migration for adding multi-tenancy to this Django app; validate the
OpenAPI output afterwards.
```

## oh-my-pi (omp)

omp routes it from the skill list (inside this checkout the skills are also
visible directly); name it for determinism:

```
Use the backend-api-engineering skill: optimize the top-3 slow endpoints
of this Axum service — baseline, change, re-measure, report deltas.
```

## Working style (all hosts)

- Profile the project first, reuse its stack; deep security goes to
  ultimate-security-hardening, cross-cutting test strategy to
  ultimate-testing-qa, generic refactors to
  ultimate-code-quality-refactoring — no duplication.
- Direct automation:
  `bash skills/backend-api-engineering/scripts/detect-project.sh <project>`,
  `bash skills/backend-api-engineering/scripts/migration-review.sh <dir>`,
  `python3 skills/backend-api-engineering/scripts/validate-openapi.py <spec>`.

## Examples that work verbatim

```
Use the backend-api-engineering skill: add OAuth2/OIDC session auth with
RBAC to this Hono API, IDOR-checked on every resource route, tests green.
```

## Verify the skill itself

```bash
python3 skills/backend-api-engineering/tests/test_skill.py
```

Exit 0 on PASS (static structure + fixtures validation).
