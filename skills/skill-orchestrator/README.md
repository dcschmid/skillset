# skill-orchestrator

Quality and orchestration manager for the skillset repository: discovery,
catalog, validation, routing plans, overlap truth, 100-point scoring,
test tiers, regression snapshots, safe repair. Python 3.10+, stdlib only
(PyYAML optional).

## Install / invoke

No install required. From the repository root:

```bash
skills/skill-orchestrator/scripts/skill-orchestrator doctor
```

Or put `skills/skill-orchestrator/scripts` on PATH and call
`skill-orchestrator …`. `pip install skills/skill-orchestrator` works too
(provides the console script). Repo root auto-detects from CWD;
`SKILL_ORCHESTRATOR_ROOT` overrides; `--root PATH` per call.
Global flags (`--json --verbose --profile --output`) go before OR after
the subcommand.

## Commands

| Command | Does | Exit |
|---|---|---|
| `scan` | discover skills → `skill-catalog.json` (`--output` dir) | 0 |
| `audit --all \| --skill X \| --changed [--save] [--report]` | validate + score + blockers | 1 on findings |
| `overlap [--skill X]` | classified overlaps with file evidence | 1 on conflict |
| `route "<task>" [--skill X]` | auditable routing plan, read-only | 0 |
| `plan "<task>"` | same as route (orchestration framing) | 0 |
| `test --all` | static/routing/conflict/integration tiers | 1 on FAIL |
| `eval --skill X [--prompt P] [--expect E]` | behavior eval via installed agent CLI | 1 on FAIL |
| `fix [--skill X] [--apply]` | repair proposals / minimal apply | 0/1 |
| `report` | Markdown + JSON report of current audit | 0 |
| `doctor` | environment health (python, yaml, agents, git) | 0 |

Reports/canvas: `--output DIR` or default `<repo>/.artifacts/skill-orchestrator/`.

## Claude Code / Codex

Both hosts read `SKILL.md` here directly (symlinked by the repo installer).
Invocation from a host session:

> Use skill-orchestrator to audit the collection and list P0 issues.

Or run the CLI yourself and paste the report. Codex additionally gets
`agents/openai.yaml`. No global agent configs are touched.

## Workflows

**Add a new skill:** create `skills/<name>/SKILL.md` — discovery finds it,
zero registration. Then `scan && audit --skill <name>`.

**Audit everything:** `audit --all --report` → `.artifacts/…/audit-report.md`
with scores, blockers, overlaps, P0–P3 task list, regressions vs last
snapshot (`--save` to store a baseline).

**Compare two skills:** `overlap --skill a --skill b`.

**Repair a skill:** `fix --skill X` (read-only diff) → review →
`fix --skill X --apply` → re-audit. Revert: `git checkout -- skills/X/…`.

**Routing plan:** `route "Erstelle eine barrierefreie Astro-Website"` →
selection + reasons + order + gates + rejected-with-reasons.

## Layout

```
SKILL.md                     router (this file links out)
README.md                    this doc
agents/openai.yaml           Codex host metadata
references/validation.md     rule tables, tiers, profiles
references/routing.md        scoring, exclusions, integration limits
references/quality-scoring.md weights, grades, blockers
references/orchestration.md  graph sources, example plans, recursion limit
references/compatibility.md  profiles × hosts field table
scripts/skill-orchestrator   launcher (no install needed)
src/skill_orchestrator/      cli discovery catalog validator router overlap
                             dependencies scoring auditor evaluator fixer reporting
tests/test_orchestrator.py   21 self-tests: python3 tests/test_orchestrator.py
pyproject.toml               optional pip install
```

## Truths and limits

- Plans, not execution: routing outputs a plan; hosts execute with their
  own skills. A skill cannot force-load in another agent — trigger
  descriptions and explicit invocation are the supported surfaces.
- Unchecked ≠ full marks: scoring credits only verified findings; the
  rest is listed `unchecked`.
- No fabricated runs: missing agent CLI → agent-eval `UNAVAILABLE`;
  missing PyYAML → built-in subset parser, both announced by `doctor`.
- No CI shipped: the repository has none; `audit --changed --json` plugs
  into any future pipeline (exit codes: 0 ok, 1 findings, 2 technical).
- Score ≠ test: numeric grades accompany test tiers, never replace them.
```