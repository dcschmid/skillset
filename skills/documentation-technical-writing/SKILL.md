---
name: documentation-technical-writing
description: >
    Universal documentation engineering for ANY project (web, Astro/React/Next,
    Node/Python/Rust backends, REST/GraphQL/gRPC/event APIs, databases, CLIs,
    desktop/mobile, Godot/Defold games, Blender pipelines, AI services, Docker/
    Linux infra, monorepos): CREATE READMEs, API docs, architecture docs, ADRs,
    developer guides, troubleshooting, tutorials; AUDIT docs against real project
    state (completeness, correctness, quality, links, secrets); FIX with P0-P4
    priority ladder; SYNC drift after code changes; GATE with quality checks.
    Ships zero-dep Python CLIs (scripts/docs_audit.py, docs_check.py, docs_sync.py)
    with JSON reports, exit codes, PASS/WARN/FAIL/REVIEW_REQUIRED/NOT RUN verdicts;
    evidence tiers VERIFIED/DOCUMENTED/PLAUSIBLE/UNKNOWN — never invented
    endpoints, commands or versions. Docs-first changes: source edits are out of
    scope unless asked. Language DE/EN follows the project. Use for: "create a
    README", "document my API", "audit the docs", "sync docs after this change",
    "write a dev guide", "is the documentation still true", "set up a docs site".
---

# Ultimate Documentation & Technical Writing

Code is the source of truth; docs follow it. Extend existing doc systems and
toolchains — never impose a new one. Every claim carries an evidence tier; a
check that never ran is NOT RUN, never a fake PASS.

## Mode gate (pick the spine first)

| Action | Trigger | Spine |
|---|---|---|
| `/docs-audit` | "audit/check the docs" | inventory → evidence-tiered findings → report (read `references/documentation-audit.md`) |
| `/docs-create` | new project needs docs | stack detect → required answers only → verify commands → `documentation-standards.md` |
| `/docs-fix` | known/just-found defects | P0-P4 ladder, minimal diffs, re-check |
| `/docs-sync` | after code changes | `scripts/docs_sync.py` plan → verify → edit only VERIFIED facts |
| `/docs-readme` | README create/revise | `assets/README.template.md`, answers from manifests |
| `/docs-api` | API docs | `references/api-documentation.md`, probe validator version first |
| `/docs-architecture` | arch docs/diagrams | `references/architecture-documentation.md` + `assets/ARCHITECTURE.template.md` |
| `/docs-guide` | dev guide/onboarding | `assets/DEVELOPER_GUIDE.template.md`, run commands when safe |
| `/docs-adr` | record a decision | `assets/ADR.template.md`, real history only |
| `/docs-check` | quality gates | `scripts/docs_check.py` + probes; verdicts honest |
| `/docs-site` | docs website | `references/quality-gates.md` §sites; no platform without need |

Slash syntax is naming, not registration: match the action by intent if the
host does not dispatch slashes.

## Loop (every mode)

1. **Detect stack** from real files: manifests, lockfiles, configs, routes,
   schemas, CI, existing docs. No stack assumption survives a missing manifest —
   say UNKNOWN.
2. **Read before write.** Commands copied from scripts/CI, run when the
   environment is safe. Never invent endpoints, params, versions, metrics.
3. **Tier every claim**: VERIFIED / DOCUMENTED / PLAUSIBLE / UNKNOWN. PLAUSIBLE
   and below ship as open questions, not facts.
4. **Write minimal, structured** (`references/documentation-standards.md`):
   one Diátaxis mode per doc; templates in `assets/` are scaffolds, not quotas.
5. **Check** `python3 scripts/docs_check.py <root>`; fix P0/P1; re-run.
6. **Report** verdicts PASS/WARN/FAIL/NOT RUN + what remains unverified.

## Binding rules

- Docs task = docs files + own tooling only. Code bugs found: hand to the
  owning engineering skill with the evidence.
- Preserve working docs and existing API contracts; no full rewrites to apply
  one fix; no productive config edits to make checks pass.
- Secrets never echoed: report file:line + placeholder advice.
- Existing docs/CI/generators win over new tooling; absent tools = NOT RUN
  with wiring advice, not simulated passes.
- Prose quality delegates to human-writing; a11y to accessibility; API design
  to backend-api-engineering; translation to i18n — this skill owns structure,
  truth, sync and gates of documentation.

## Scripts (Python 3.10+, stdlib, non-destructive)

```
python3 scripts/docs_audit.py [--json --out R --scope readme|api|config|setup|ci] ROOT
python3 scripts/docs_check.py [--json --out R] ROOT
python3 scripts/docs_sync.py  [--range main..HEAD --json --out R] ROOT
```
Exit 0 pass/warn, 1 review, 2 fail. Reports collision → dated suffix, never
overwrite. Deep guidance: `references/` (standards, audit, api, architecture,
quality-gates). Validation: `python3 tests/test_skill.py`.
