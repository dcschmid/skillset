# ultimate-i18n-localization

Universal i18n/localization skill: builds, audits, repairs, tests, and
guards multilingual setups for web frameworks and games. The engine is a
zero-dependency Node CLI; everything else is progressive-disclosure docs.

## Activate (skill) vs run (commands)
- Skill: reference `ultimate-i18n-localization` in a prompt from Claude
  Code, Codex, or oh-my-pi ("Mach dieses Projekt mehrsprachig", "Führe einen
  i18n-Audit durch", "Lokalisiere dieses Godot-Spiel"). The agent follows
  SKILL.md's loop:
  ```text
  Use the ultimate-i18n-localization skill: audit locales/de.json vs
  en.json parity — keys, placeholders, plurals — and fix drift additively.
  ```
- Commands (no registry needed, always available on the shell):
  `scripts/i18n <audit|check|fix|validate|pseudo|extract|report|plan>` and
  wrappers `scripts/i18n-audit|check|fix|extract|pseudo|report`.
  Skill activation ≠ slash command; slash commands were not assumed.

## Try it in 30 seconds
```bash
S=~/dev/github/skillset/skills/ultimate-i18n-localization
node $S/scripts/i18n audit --root $S/tests/fixtures/web-shop   # drifted fixture
node $S/scripts/i18n check --root $S/tests/fixtures/web-shop   # CI gate, exit 1
node $S/tests/run.mjs                                          # 36/36 PASS
godot --headless --path $S/examples/game/godot -s probe_i18n.gd # PROBE PASS
```

## On a real project
```bash
node $S/scripts/i18n audit  --root /path/to/proj            # full report
node $S/scripts/i18n check  --root /path/to/proj --format json --out i18n.json
node $S/scripts/i18n fix    --root /path/to/proj --reference de
node $S/scripts/i18n pseudo --text 'Save {count} items' --expand 0.4
```
CI: templates/ci/github-action.yml. New projects: templates/{locales,glossary,
styleguide}. Deep rules: references/*.md. Engine wiring: adapters/*.

## Guarantees
- additive fixes only; existing translations are never rewritten
- CI blocks only on confirmed BLOCKER/HIGH; heuristics are REPORT-only
- untested layers (Defold engine here) are stated NOT TESTED, never borrowed
