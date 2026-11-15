# Lean Engineering

Cross-cutting engineering mode for AI coding agents: the simplest COMPLETE,
correct, maintainable solution — not the shortest code. Works in any
language/stack (JS/TS, React/Next, Astro, Python, backends, CLIs,
Lua/Defold, GDScript/Godot, Blender Python, DBs; unknown stacks → cautious
generic mode). Kills needless complexity, premature abstraction, gratuitous
dependencies and config surface; never sacrifices functionality, security,
validation, a11y, tests, performance or necessary architecture.

Concepts distilled from the MIT-licensed [ponytail](https://github.com/DietrichGebert/ponytail)
skill (decision ladder, session modes, shortcut markers, debt ledger) —
redeveloped, extended with audit/simplify workflows, the never-cut floor,
per-platform activation notes, and wired to this repo's conventions. No
code or text copied verbatim.

## Tasks

write/fix/refactor any code lean · `/lean review` (diff) · `/lean audit`
(whole repo) · `/lean simplify` (behavior-preserving) · `/lean debt`
(shortcut ledger) · mode switching lite/full/ultra/off.

## Requirements

- None beyond a skill-capable agent host (Claude Code, OpenAI Codex,
  oh-my-pi, or any host reading `SKILL.md`).
- `python3` (stdlib, no installs) only to run the self-test.
- Git recommended for review/simplify diffing; non-git projects work with
  named-file scope.

## Install / activate

```bash
tools/install-skills.sh lean-engineering      # symlink into agent roots
tools/uninstall-skills.sh lean-engineering    # remove the managed link
```

Symlinks land in `~/.claude/skills/` (Claude Code) and `~/.agents/skills/`
(Codex); oh-my-pi loads both roots. Routing scope: `both` (default in
`tools/profile-map.tsv` — unlisted). Activation: name `lean-engineering`,
say "lean mode"/"yagni", or type `/lean <mode>`; without slash-command
support the same phrases work as plain text.

## Modes & commands

| Command | Effect |
|---|---|
| `/lean lite` | asked-for build, existing code preferred, smaller option named |
| `/lean full` | default: ladder + understand-before-edit + floor + proportionate tests |
| `/lean ultra` | full + critique the request; cut unrequested features, never requested ones |
| `/lean off` | lean rules silent; project/safety rules stay |
| `/lean review` | lean pass over the current diff, verdict SHIP/TRIM |
| `/lean audit` | read-only whole-project scan, 7-field findings |
| `/lean simplify` | behavior-preserving simplification, baseline→step→verify |
| `/lean debt` | harvest `shortcut:` markers + ledger, KEEP/RIPENED/STALE |
| `/lean status` | active mode + open debt summary |
| `/lean help` | cheat sheet |

Session-scoped modes; hosts without session state restate the mode per turn.

## Examples

```text
Use the lean-engineering skill: add CSV export to /api/reports — leanest
complete solution, no new dependencies, tests for new logic.
```

```text
Use the lean-engineering skill: /lean audit src/ — over-engineering scan,
7-field findings table, KEEP rows for architecture that earns its keep.
```

```text
Use the lean-engineering skill: /lean simplify packages/core/pricing.ts —
identical behavior, public API frozen, run the project tests per step.
```

## Structure

`SKILL.md` (binding core) · `references/engineering-ladder.md` (ladder +
floor) · `references/modes.md` (mode semantics + platforms) ·
`references/audit-and-review.md` · `references/simplify.md` ·
`references/debt.md` · `references/scenarios.md` (S1–S10 acceptance cases) ·
`tests/test_skill.py`. No scripts, no assets, no runtime — instructions
plus a stdlib self-test; adding more would violate the skill's own rules.

## Collaboration & limits

Decides simplicity/scope; domain skills keep domain checks
(ultimate-code-review, ultimate-code-quality-refactoring,
ultimate-testing-qa, ultimate-security-hardening, framework/engine skills).
Works standalone when they're absent; never imports them. Not for: learning
exercises where verbosity is the point, code-golf contests, or "off"
sessions. Known limits: LLM mode-adherence verified manually via
S1–S10, not scriptable; audit coverage on huge repos is stated, not total;
`/lean status` reports debt from files, no background state exists between
sessions.

Troubleshooting: skill not firing → name it exactly (`lean-engineering`);
mode lost → restate "lean: full"; findings feel wrong → rerun scoped to the
module ("audit only src/api"); a domain skill and lean conflict → lean sets
scope, domain skill sets checks.

Verify: `python3 skills/lean-engineering/tests/test_skill.py`
