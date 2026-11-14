# Using the `skill-orchestrator` skill in your agents

Quality and orchestration manager for this skillset repository itself:
discovery, inventory, validation, audit, scoring, routing plans, overlap
truth, regression snapshots, repair proposals. Deterministic Python 3 CLI
over real files — discovery never invents skills, scoring never credits
unchecked areas, agent-evals report UNAVAILABLE instead of faking passes.
Read-only by default; repairs are proposals until approved. Coordinates
other skills without duplicating their domains.

## Install (this skill only)

```bash
tools/install-skills.sh skill-orchestrator
```

Symlinks into both host roots; note that inside this checkout the CLI runs
directly from `skills/skill-orchestrator/scripts/skill-orchestrator`
regardless of installation state.

## Claude Code

Discovered from `~/.claude/skills/`; activates on repo-level questions
("audit my skill collection", "is skill X valid?", "which skills serve
this task?"):

```
Use the skill-orchestrator skill: audit the collection, profile portable,
and show the regression diff against the stored baseline.
```

## Codex

Same content via `~/.agents/skills/`:

```
Use the skill-orchestrator skill: overlap check between accessibility and
design-system-ui — report shared territory and handoff boundaries.
```

## oh-my-pi (omp)

omp routes from the skill list; plans stay honest about what was evaluated:

```
Use the skill-orchestrator skill: route "accessible Astro marketing site
with i18n and SEO gates" — which skills, in which order, why.
```

## Working style (all hosts)

- Commands: `scan|audit|overlap|route|plan|test|eval|fix|report|doctor`,
  profiles `portable|claude|codex`, `--json` for machine output:
  `python3 skills/skill-orchestrator/scripts/skill-orchestrator audit
  --profile portable`.
- `fix` produces proposals; nothing is rewritten without approval.

## Examples that work verbatim

```
Use the skill-orchestrator skill: doctor — what is broken in the
collection right now, and what would each repair cost?
```

## Verify the skill itself

```bash
python3 skills/skill-orchestrator/tests/test_orchestrator.py
```

Exit 0 on PASS (fixtures-based, deterministic).

This suite also validates collection metadata with the shared validator.
Static audits award at most 5/15 test points for test structure; test
execution and behavior remain NOT RUN and earn no points until verified.
