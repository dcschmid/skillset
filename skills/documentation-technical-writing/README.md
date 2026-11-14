# documentation-technical-writing

Universal documentation skill for the skillset collection: create, audit,
repair, and sync technical documentation against real project state — any
stack, any project size.

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
