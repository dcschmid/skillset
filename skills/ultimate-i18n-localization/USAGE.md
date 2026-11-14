# Using the `ultimate-i18n-localization` skill in your agents

i18n and localization engineering for web (Astro, Next.js/next-intl,
React/i18next, Vue/Nuxt, Svelte, vanilla) and games (Godot, Defold), plus
JSON/YAML/CSV/PO/FTL/XLIFF catalogs. Modes: CREATE, AUDIT, FIX
(additive-only, re-audited), TRANSLATE (plan + draft, human approves),
VALIDATE, PSEUDO (grapheme-based expansion stress), REPORT. Key/
placeholder/plural parity across locales, hreflang per Google rules, engine
probes where the runtime exists. de/en core, any CLDR language addable
(ar/he RTL included). Never overwrites existing translations, never ships
machine text as approved, absent engines report NOT TESTED.

## Install (this skill only)

```bash
tools/install-skills.sh ultimate-i18n-localization
```

Symlinks into both host roots; remove with
`tools/uninstall-skills.sh ultimate-i18n-localization`.

## Claude Code

Discovered from `~/.claude/skills/`; activates on i18n/l10n tasks:

```
Use the ultimate-i18n-localization skill: audit locales/de.json vs
locales/en.json parity — keys, placeholders, plurals — and fix drift
additively.
```

## Codex

Same content via `~/.agents/skills/`:

```
Use the ultimate-i18n-localization skill: CREATE the i18n stack for this
Astro site (de/en, hreflang, routing) and gate CI on confirmed blockers.
```

## oh-my-pi (omp)

omp routes from the skill list; the `i18n` CLI is the deterministic lane:

```
Use the ultimate-i18n-localization skill: run PSEUDO on the UI strings to
stress-test layout, then REPORT the overflow list.
```

## Working style (all hosts)

- TRANSLATE output is a draft until a human approves; engine-dependent
  paths without the runtime are NOT TESTED.
- Direct automation:
  `node skills/ultimate-i18n-localization/scripts/i18n audit <project>` —
  plus `check|fix|validate|pseudo|extract|report|plan` (stack detection,
  locale dir + reference locale, Godot/Lua probes where the runtime
  exists).

## Examples that work verbatim

```
Use the ultimate-i18n-localization skill: add Hebrew as RTL locale —
parity plan, pseudo stress, hreflang update, nothing shipped untranslated.
```

## Verify the skill itself

```bash
node skills/ultimate-i18n-localization/tests/run.mjs
```

Exit 0 on PASS (zero-dep runner, unit + integration fixtures).
