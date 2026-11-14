# accessibility — skill guide (human-facing)

Agent entry point is `SKILL.md`; this file is for people.

Universal WCAG 2.2 engineering + auditing skill with a real audit tool.
WCAG 2.2 A/AA binding · AAA advisory · WCAG-EM 2.0 audits · EN 301 549/BFSG/
BITV mapping · WCAG2ICT for native. Baseline probe: 2026-11-14.

## Layout

```
SKILL.md                     agent workflow spine (build/audit/remediate/advise)
references/                  standards.md wcag-aa.md wcag-aaa.md do-dont.md
  aria-patterns.md screenreaders.md keyboard-testing.md framework-integration.md
  native-platforms.md legal-context.md audit-methodology.md
tooling/a11y-audit/          the tool: src/ (TS, node 22 type-strip) fixtures/ tests/
  bin/a11y.mjs               launcher — audit|keyboard|report|compare|check
scripts/setup-check.sh       prerequisite probe (installs nothing)
scripts/check-standards.mjs  standards drift report
examples/README.md           patterns quick-ref
tests/test_skill.py          validation entry (VERDICT parse)
```

## Quick start (in any project)

```bash
cd <skill>/tooling/a11y-audit && npm install && npx playwright install chromium firefox
node bin/a11y.mjs check                                  # capabilities
node bin/a11y.mjs audit --url http://localhost:3000 --level aa
node bin/a11y.mjs audit --config a11y.config.json --level aaa --format json,html,junit,sarif
node bin/a11y.mjs keyboard --url http://localhost:3000
node bin/a11y.mjs compare --before before.json --after after.json
```

CI: exit 0 = gate pass, 1 = blocking AA violations, 2 = usage error.
Config `routes[].scenarios` drive dialogs/errors/menus; credentials stay in
`${A11Y_USER}` env placeholders. Reports: JSON+HTML(self-a11y)+JUnit+SARIF.

## Validation

```bash
python3 tests/test_skill.py          # full suite, VERDICT PASS/FAIL
node tooling/a11y-audit/tests/run.mjs
node tooling/a11y-audit/tests/screenreader-orca.ts   # real Orca where supported
```

## Environment truth (Fedora KDE Wayland, 2026-11-14)

Orca 50.3 + AT-SPI2 2.60.7 + Guidepup 0.40 (project-scoped assets). SR
automation blocked headless (no audio sink for speech capture) — harness
reports SR_ENV_FAIL + manual fallback, never fabricates. Keyboard/DOM/axe
lanes run fully. Details: `references/screenreaders.md`.

## Maintenance

- standards drift: `scripts/check-standards.mjs` quarterly; edit only
  `references/standards.md` pins after review.
- tool deps: axe-core/Playwright pinned exact; bump deliberately.
- new framework → add `references/framework-integration.md` section, not a
  new skill; new SR platform → screenreaders.md matrix.
