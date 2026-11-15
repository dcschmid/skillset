# Using the `ultimate-code-review` skill in your agents

Multi-axis review/PR audit of diffs and whole projects — Standards, Spec,
Bugs, Security, Testing, Performance kept independent; evidence-backed,
severity×confidence findings; read-only by default; `--fix` only on explicit
ask; gates treat skipped checks as gaps, never passes.

## Install (this skill only)

```bash
tools/install-skills.sh ultimate-code-review
```

Symlinks into both host roots; remove with
`tools/uninstall-skills.sh ultimate-code-review`.

## Claude Code

Discovered from `~/.claude/skills/`; slash-style or plain requests:

```
/code-review --base main --gate high
Use the ultimate-code-review skill: review my uncommitted changes, spec is
docs/sprint-14.md; findings only, read-only.
```

## Codex

Same content via `~/.agents/skills/`:

```
Use the ultimate-code-review skill: audit PR 231 against its base, all six
axes separate, JSON+md into reports/code-review/, no fixes.
```

## oh-my-pi (omp)

Routes from the skill list; sub-agents available so axis agents run
isolated (sequential fallback is labeled):

```
Use the ultimate-code-review skill: /code-review --full on this repo,
prioritized batches, PARTIAL over fake-complete.
```

## Working style (all hosts)

- Read-only until `--fix`; `--safe-only` caps at low-risk fixes.
- No baseline + ambiguous → candidates listed, no arbitrary pick.
- Untracked files counted once, listed separately.
- Reports cite commands + real output; unrun checks say NOT EXECUTED.

## Examples that work verbatim

```
Use the ultimate-code-review skill: /code-review --commit HEAD --gate
critical — block the merge only on confirmed criticals, list skips honestly.
```

## Direct automation

```bash
S=skills/ultimate-code-review/scripts
python3 $S/prepare_review.py -w /tmp/ws . -- --staged
python3 $S/prepare_review.py --finish /tmp/ws --gate high
```

## Verify the skill itself

```bash
python3 skills/ultimate-code-review/tests/test_skill.py
```

Exit 0 on PASS (deterministic script layer; axis judgment = host model).
