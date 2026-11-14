# Using the `ultimate-code-quality-refactoring` skill in your agents

Code quality audit and controlled refactoring for any codebase (JS/TS,
React/Next, Astro, Vue/Svelte, Python, Go, Rust, Java/Kotlin, C#, PHP,
Lua/Defold, GDScript/Godot, Blender Python, C/C++; unknown languages get a
cautious generic mode). Audits tech debt, smells, duplication, complexity
hotspots, dead code, architecture boundaries, perf suspects; refactors
behavior-preservingly with baselines and per-step verification through the
project's own lint/typecheck/test tools. Risk-tiered autonomy: LOW
auto-fixes, HIGH requires approval; rollback protects uncommitted work.
Read-only AUDIT is the default.

## Install (this skill only)

```bash
tools/install-skills.sh ultimate-code-quality-refactoring
```

Symlinks into both host roots; remove with
`tools/uninstall-skills.sh ultimate-code-quality-refactoring`.

## Claude Code

Discovered from `~/.claude/skills/`; triggers on quality/refactor asks
("quality audit", "find technical debt", "/quality-audit"):

```
Use the ultimate-code-quality-refactoring skill: audit packages/core for
complexity hotspots and dead code; PASS/FAIL/UNVERIFIED only, no invented
scores.
```

## Codex

Same content via `~/.agents/skills/`:

```
Use the ultimate-code-quality-refactoring skill: refactor the pricing
module without changing behavior — baseline, per-step verify, evidence
report, keep my uncommitted changes intact.
```

## oh-my-pi (omp)

omp routes from the skill list; the project's own tools are the verification
lane:

```
Use the ultimate-code-quality-refactoring skill: reduce duplication in the
reporting layer across these two services and show the before/after
metrics.
```

## Working style (all hosts)

- BUG FIX and FEATURE CHANGE refactors are separate lanes; reports carry
  evidence only.
- Direct automation:
  `python3 skills/ultimate-code-quality-refactoring/scripts/detect_project.py <project>`,
  `run_audit.py`, `collect_metrics.py`, `detect_duplicates.py`,
  `compare_baseline.py`, `verify_changes.py`, `generate_report.py`
  (same directory).

## Examples that work verbatim

```
Use the ultimate-code-quality-refactoring skill: /quality-verify — check
the staged diff against baseline before merge; FAIL the lane on behavior
drift.
```

## Verify the skill itself

```bash
python3 skills/ultimate-code-quality-refactoring/tests/test_skill.py
```

Exit 0 on PASS (static structure + fixtures validation).
