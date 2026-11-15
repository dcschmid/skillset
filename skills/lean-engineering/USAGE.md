# Using the `lean-engineering` skill in your agents

Cross-cutting lean engineering mode for ANY coding task in any stack:
implement the simplest COMPLETE, correct, maintainable solution — not the
shortest code. Ladder before new code (need it? reuse? extend? stdlib?
installed dep? few edits? abstraction last), a never-cut floor (security,
validation, error handling, a11y, tests, perf, requested features), session
modes lite/full/ultra/off, and workflows /lean review, /lean audit,
/lean simplify, /lean debt. Never an excuse to cut functionality.

## Install (this skill only)

```bash
tools/install-skills.sh lean-engineering
```

Symlinks into both host roots; remove with
`tools/uninstall-skills.sh lean-engineering`.

## Claude Code

Discovered from `~/.claude/skills/`; activates on coding asks and on
"lean", "yagni", "over-engineered", "/lean ...":

```
Use the lean-engineering skill: add CSV export to /api/reports — leanest
complete solution, no new dependencies, tests for new logic.
/lean audit src/   ·   /lean simplify packages/core/pricing.ts
```

## Codex

Same content via `~/.agents/skills/`; slash-phrases are matched as text:

```
Use the lean-engineering skill in ultra mode: the settings module grew a
factory + registry for one consumer — name the over-engineering, propose
the leaner shape, keep behavior.
```

## oh-my-pi (omp)

Loaded from the shared roots plus managed skills; name it or say
"lean mode: full". Session mode is sticky until `/lean off`; hosts without
session state restate the mode line per turn.

Verify: `python3 skills/lean-engineering/tests/test_skill.py`
