# documentation-technical-writing

Universal documentation skill for the skillset collection: create, audit,
repair, and sync technical documentation against real project state — any
stack, any project size.

Host invocation — install with `tools/install-skills.sh
documentation-technical-writing` (symlinks into `~/.claude/skills` for
Claude Code, `~/.agents/skills` for Codex; oh-my-pi loads both roots), then
invoke by name:

```text
Use the documentation-technical-writing skill: audit docs/ against src/ —
which endpoints and commands are still true? P0-P4 fix list, honest NOT RUN
for what you cannot execute.
Use the documentation-technical-writing skill: CREATE the ADR set for the
new caching layer — decisions against the real code, tiers labeled.
```

- `SKILL.md` — activation + mode spine (11 actions, `/docs-*`).
- `references/` — standards, audit procedure, API/architecture/quality-gates.
- `assets/` — fill-in templates (README, CONTRIBUTING, ARCHITECTURE, API,
  DEVELOPER_GUIDE, ADR, TROUBLESHOOTING).
- `scripts/` — three zero-dep Python CLIs with JSON output and honest
  verdicts (`docs_audit.py`, `docs_check.py`, `docs_sync.py`, shared
  `docs_lib.py`).
- `tests/test_skill.py` — static + dynamic validation, exit-0 = PASS.

Principle: code is the source of truth; claims carry evidence tiers
(VERIFIED/DOCUMENTED/PLAUSIBLE/UNKNOWN); checks that never ran report
NOT RUN. Run `python3 tests/test_skill.py` to validate.
