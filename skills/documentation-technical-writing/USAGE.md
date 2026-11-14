# Using the `documentation-technical-writing` skill in your agents

Documentation engineering for any project (web, backend, API, CLI, games,
pipelines, infra, monorepos): CREATE READMEs, API docs, architecture docs,
ADRs, guides, troubleshooting, tutorials; AUDIT docs against real project
state (completeness, correctness, quality, links, secrets); FIX with a
P0–P4 priority ladder; SYNC drift after code changes; GATE with quality
checks. Evidence tiers VERIFIED/DOCUMENTED/PLAUSIBLE/UNKNOWN — endpoints,
commands, versions are never invented. Docs-first changes keep source out
of scope unless asked. DE/EN follows the project.

## Install (this skill only)

```bash
tools/install-skills.sh documentation-technical-writing
```

Symlinks into both host roots; remove with
`tools/uninstall-skills.sh documentation-technical-writing`.

## Claude Code

Discovered from `~/.claude/skills/`; activates on "write a README",
"document my API", "audit the docs":

```
Use the documentation-technical-writing skill: audit docs/ against src/ —
which endpoints and commands are still true? P0-P4 fix list, honest NOT
RUN for what you cannot execute.
```

## Codex

Same content via `~/.agents/skills/`:

```
Use the documentation-technical-writing skill: SYNC the changelog and
README after the v2 migration, then GATE before release.
```

## oh-my-pi (omp)

omp routes from the skill list; the zero-dep Python CLIs carry JSON
reports and exit codes:

```
Use the documentation-technical-writing skill: CREATE the ADR set for the
new caching layer — decisions against the real code, tiers labeled.
```

## Working style (all hosts)

- Every claim carries an evidence tier; unverifiable statements stay
  PLAUSIBLE/UNKNOWN.
- Direct automation:
  `python3 skills/documentation-technical-writing/scripts/docs_audit.py <project>`,
  `docs_check.py`, `docs_sync.py` (shared `docs_lib.py`).

## Examples that work verbatim

```
Use the documentation-technical-writing skill: is this README still true
after this week's refactor? Diff against code, fix drift, report tiers.
```

## Verify the skill itself

```bash
python3 skills/documentation-technical-writing/tests/test_skill.py
```

Exit 0 on PASS (static structure + fixtures validation).
