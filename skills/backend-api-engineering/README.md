# backend-api-engineering

Universal backend & API engineering skill for AI coding agents (Claude Code,
Codex, any SKILL.md consumer). Builds and repairs backends on ANY stack
(Node/Fastify/Nest/Astro, Python FastAPI/Django, Go, Rust, JVM, .NET, PHP),
ANY database (SQL/NoSQL/Redis/search/vector), ANY interface style (REST,
GraphQL, gRPC, WebSocket/SSE). Profiles the project, reuses its stack,
fixes real defects (IDOR gaps, N+1, unvalidated input, missing indexes),
verifies with tests and measurements, reports honestly (`NOT TESTED` when
unverified, never PASS on vibes).

Spine: `PROFILE → MODE → WORK → VERIFY → REPORT`.

## Structure

```
SKILL.md                mode gate + prime rules + score rubric (start here)
references/             load per mode: api-design · authentication ·
                        authorization · database-engineering ·
                        database-migrations · architecture · security ·
                        performance · observability · testing · deployment ·
                        background-jobs-messaging · quality-gates
workflows/              6 runnable procedures: create · audit · fix ·
                        optimize · migrate · verify
scripts/                executable: detect-project.sh (profile, read-only) ·
                        validate-openapi.py (spec + breaking-change diff) ·
                        migration-review.sh (destructive-DDL lint)
templates/              finding.json · scorecard.md · api-spec.yaml ·
                        migration.sql · health-endpoints.md
tests/                  self-test (structure, scripts, fixtures, evals)
evals/                  8 scenario rubrics (A–H) with pass criteria
examples/               10 worked scenarios (create→audit→fix→optimize…)
```

## Use

Invoke by phrase — "build a REST API for…", "audit my backend", "fix the
500 on /orders", "optimize these Postgres queries", "make the login
production-ready", "migrate the schema without data loss". The mode gate in
SKILL.md picks the workflow; load only the references that workflow names.

Run the tooling from this directory against a target project:

```bash
scripts/detect-project.sh ../my-api            # architecture profile
scripts/validate-openapi.py openapi.json       # structure gate
scripts/validate-openapi.py new.yaml --baseline old.yaml   # breaking diff
scripts/migration-review.sh ../my-api/migrations           # DDL lint
python3 tests/test_skill.py                    # skill self-test
```

## Boundaries (skill-collection contract)

- Deep vulnerability audits and hardening passes → `ultimate-security-hardening`
  (this skill ships secure-by-default code and hands findings over).
- Cross-cutting test strategy/E2E/browser lanes → `ultimate-testing-qa`
  (this skill owns backend unit/integration/API/migration layers).
- Generic non-backend refactors → `ultimate-code-quality-refactoring`.
- Fullstack split: `react-nextjs` / `astro` own client + SSR surface;
  server handlers, DB, jobs stay here. Game backends (defold/godot):
  auth/leaderboards/save-sync APIs here, only when the game needs them.

## Ground rules

Approval gates never auto-run: prod DB execution, prod deploys, secrets
rotation, framework swaps, new infrastructure, contract breaks. Score is
evidence-based; `PASS` needs ≥90/100 plus all hard gates green — a critical
vuln or data-loss finding blocks release regardless of points.
