# design-system-ui

Design-system and UI-component engineering for any web project (plus
game-UI token concepts for Godot/Defold). CREATE token systems, AUDIT
existing projects, FIX inconsistencies, MIGRATE toward a system, VALIDATE
tokens/themes, DOCUMENT components — the system serves the project's
identity, it never replaces it.

Entry point: [`SKILL.md`](SKILL.md) (workflow spine + mode gate).

## Use (Claude Code & Codex — same trigger, no slash registry)

```
Use design-system-ui to audit this project's design consistency.
Use design-system-ui to create a token system for this new app.
Use design-system-ui to fix the duplicate buttons and broken dark mode.
```

`/design-system audit|fix|tokens|component|themes|migrate|docs|validate|report|init`
≡ run the skill in that workflow (table in SKILL.md). Triggers: design
system/tokens, UI consistency, component library, dark mode broken,
duplicate components, token refactor.

## Tooling (zero deps, node ≥18)

```bash
node scripts/ds.mjs detect <dir>                      # stack facts
node scripts/ds.mjs tokens t.json --themes light,dark # validate; exit 1 on P0
node scripts/ds.mjs audit <dir> --format md           # P0..P3, file:line
node scripts/ds.mjs report f.json --format html       # non-destructive
node assets/ds-tokens-build.mjs t.json --out build --themes light,dark  # CSS/TS emit
```

## Layout

- `references/` — tokens(DTCG v2025.10)/components/theming/audit-rules/
  migration/testing/framework-adapters/accessibility/anti-ai-boundary
- `assets/` — token build script + source/doc templates
- `examples/fixture-messy|fixture-clean/` — before/after pair, asserted by tests
- `tests/run.mjs` — `node tests/run.mjs` → VERDICT line

Cooperates with (degrades gracefully when absent): accessibility,
design-authenticity, ultimate-testing-qa, react-nextjs, astro,
ultimate-i18n-localization, ultimate-code-quality-refactoring.
