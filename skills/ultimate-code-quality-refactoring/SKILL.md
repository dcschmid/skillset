---
name: ultimate-code-quality-refactoring
description: >
  Code quality audit and controlled refactoring for ANY codebase (JS/TS, React/Next, Astro,
  Vue/Svelte, Python, Go, Rust, Java/Kotlin, C#, PHP, Lua/Defold, GDScript/Godot, Blender
  Python, C/C++, CLI, APIs, monorepos; unknown languages get a cautious generic mode). Use
  to audit projects for technical debt, code smells, duplication, complexity hotspots, dead
  code, architecture/boundary problems, perf suspects; and to refactor safely
  (behavior-preserving, BUG FIX and FEATURE CHANGE separate) with before/after baselines,
  per-step verification via the project's own lint/typecheck/test tools, risk-tiered
  autonomy (LOW auto-fix, HIGH requires approval), safe rollback protecting the user's
  uncommitted work, evidence-only reports (PASS/FAIL/UNVERIFIED, nothing faked, no invented
  scores). Read-only AUDIT is the default. Triggers: 'quality audit', 'find technical debt',
  'analyze architecture', 'refactor without changing behavior', 'verify changes before
  merge', 'reduce complexity', '/quality-audit', '/quality-verify'.
---

# Ultimate Code Quality & Refactoring

Pipeline (binding): **Understand → Baseline → Detect → Prioritize → Refactor →
Verify → Compare → Report**. Correctness and maintainability beat cosmetics.
Not every finding is a defect; not every duplicate earns abstraction; simple
projects stay simple.

## Scripts (stdlib Python 3, zero deps, read-only toward the project)

All from `scripts/`, run against the target project root:

- `detect_project.py [dir] -o f.json` — languages, frameworks, manifests,
  declared test/check commands, CI, monorepo packages, git state.
- `collect_metrics.py [dir] -o f.json` — lines, nesting depth, complexity
  PROXY, long functions/params, TODO/FIXME debt markers, hotspots.
- `detect_duplicates.py [dir] -o f.json` — normalized clone candidate groups.
- `run_audit.py [dir] -o DIR` — orchestrates the three above + external-tool
  inventory into one `quality-audit.json` bundle (`--quick` = no dup scan).
- `verify_changes.py [dir] --save-baseline|--baseline f.json --cmd "<check>"` —
  runs project checks, diffs vs baseline; verdict PASS/FAIL/UNVERIFIED; exit
  0/1/2. Baseline failures stay attributed to the baseline.
- `generate_report.py audit.json --verify v.json --delta d.md` — Markdown
  report from measured data only.
- `compare_baseline.py before.json after.json` — measured delta table, N/A
  for unmeasured.

## Modes

| Mode | Edits? | Entry |
|---|---|---|
| AUDIT | never | default; bundle + report only |
| QUICK AUDIT | never | `run_audit.py --quick` on diff scope + callers |
| SAFE AUTOFIX | LOW-risk only | per-step verify each change |
| DEEP REFACTOR | after baseline+tests | characterization first for untested code |
| ARCHITECTURE REVIEW | proposal first | evidence, alternatives, incremental plan |
| DEBT CLEANUP | approved packages | priorities P0–P3 with evidence |
| PRE-MERGE GATE | never | changed files vs merge base + verify |
| CONTINUOUS QUALITY | project CI only when asked | wire existing pipelines |

## Per-change loop (fix modes)

1. `git status` → user's dirty files are untouchable; collision = stop+report.
2. Baseline: `verify_changes.py --save-baseline --cmd "<project checks>"`.
3. One controlled change (one pattern, commit-sized, no format noise mixed).
4. `verify_changes.py --baseline ...` → PASS next; FAIL → revert own hunks only.
5. End of package: full relevant suite + `compare_baseline.py` delta.

Risk tiers: LOW auto (provable behavior-preserving), MEDIUM needs
characterization/regression tests first, HIGH (architecture, public API, DB,
concurrency, permissions, production logic) = written proposal + approval.

## Hard rules

- AUDIT default read-only; edits only in fix modes. Never commit/push without
  being asked. No installs, no CI activation, no lockfile churn unasked.
- Report findings only with `file:line` evidence; unavailable metric = N/A;
  complexity from `collect_metrics.py` is a labeled PROXY; green tests ≠
  behavior proof — residual risk always stated.
- Existing failures are baseline, listed per test, never hidden, never
  blamed on your change. Flaky ≠ passing.
- Untested + uncharactizable code → do not edit blind: tests first, else
  UNVERIFIED.
- REFACTOR / BUG FIX / FEATURE CHANGE never mixed in one step.
- Missing tool = documented gap ("UNVERIFIED: <check> (no <tool>)"), never a
  simulated result.

## References (load on demand)

- `references/audit-methodology.md` — phase contracts, evidence rules
- `references/code-smells.md` — detection signals + non-smells + P0–P3
- `references/architecture-review.md` — boundaries, cycles, migration discipline
- `references/refactoring-patterns.md` — pattern table, when NOT to refactor
- `references/behavior-preservation.md` — inventory, characterization, ladders
- `references/testing-strategy.md` — runner discovery, missing-layer handling
- `references/performance-analysis.md` — hypotheses vs measurements
- `references/technical-debt.md` — finding schema, roadmap rules
- `references/quality-metrics.md` — measured vs proxy, gates, baseline workflow
- `references/language-adapters.md` — per-stack verify/refactor tools, games
- `references/tool-integration.md` — presence gates, version-probe-first
- `references/safety-and-rollback.md` — risk tiers, revert protocol
- `references/reporting.md` — report anatomy

Templates: `assets/audit-report.md`, `assets/refactoring-plan.md`,
`assets/technical-debt-backlog.md`, `assets/before-after-report.md`.
Self-test: `python3 tests/test_skill.py` (structure + fixtures A–J + E2E).

## Invocation

Natural: "Prüfe dieses Projekt auf Codequalität", "Refaktoriere dieses Modul,
ohne Verhalten zu verändern", "Finde technische Schulden", "Behebe sichere
Code Smells und teste anschließend". Slash-style (documented shorthands —
agents without slash support use the phrases): `/quality-audit` AUDIT,
`/quality-quick` QUICK AUDIT, `/quality-fix` SAFE AUTOFIX,
`/quality-refactor` DEEP REFACTOR, `/quality-architecture` ARCHITECTURE
REVIEW, `/quality-debt` DEBT CLEANUP, `/quality-verify` PRE-MERGE GATE.

Integration (no hard deps): testing/QA, security, a11y, astro/react/defold/
godot skills may take over domain verification — hand them the changed-file
list + baseline; absent skills change nothing here.
