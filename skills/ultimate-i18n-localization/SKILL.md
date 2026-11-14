---
name: ultimate-i18n-localization
description: >
  Universal i18n & localization engineering for web (Astro, Next.js/next-intl,
  React/i18next, Vue/Nuxt, Svelte, vanilla) and games (Godot, Defold) plus
  JSON/YAML/CSV/PO/FTL/XLIFF catalogs. Modes: CREATE, AUDIT, FIX (additive-only, re-audited
  before reporting), TRANSLATE (plan + draft, human approves), VALIDATE, PSEUDO
  (grapheme-based expansion stress), REPORT (md/json/html). Ships a zero-dep Node CLI
  (scripts/i18n: audit|check|fix|validate|pseudo|extract|report|plan) that detects stack,
  locales dir, and reference locale, diffs key/placeholder/plural parity across locales,
  gates CI on confirmed BLOCKER/HIGH only, validates hreflang/canonical per Google rules,
  and runs Godot/Lua engine probes where the runtime exists. Languages: de/en core, any CLDR
  language addable (ar/he RTL incl.). Never overwrites existing translations, never ships
  machine text as approved, never claims an untested path - absent engines report NOT
  TESTED.
---

# Ultimate i18n & Localization

Core loop: **discover → audit → fix(additive) → re-audit → report.**
Evidence only: measured keys, versions, counts. Heuristics carry
`confirmed:false` and never block CI.

## Quick start
```bash
S=~/dev/github/skillset/skills/ultimate-i18n-localization
node $S/scripts/i18n audit  --root <project>          # full markdown report
node $S/scripts/i18n check  --root <project>          # CI gate, VERDICT + exit code
node $S/scripts/i18n check  --root <project> --fail-on BLOCKER --format json
node $S/scripts/i18n fix    --root <project>          # additive repairs + re-audit
node $S/scripts/i18n pseudo --text 'Save {count}' --expand 0.3 [--rtl]
node $S/scripts/i18n extract --root <project>         # used-key skeleton
node $S/scripts/i18n report --root <project> --format json --out i18n.json
```
Wrappers `i18n-audit|check|fix|extract|pseudo|report` take identical flags.
Key flags: `--reference de|en`, `--locales-dir`, `--fail-on`, `--format md|json|html`, `--out`.

## Workflow spine (every project task)
1. **Discover** — run `i18n audit` first; it reports stack, system, locales
   dir, reference locale (honors `defaultLocale`), libs. Do not assume regions
   (`de-AT`) unless the project declares them.
2. **Audit** — static (keys/placeholders/plurals/dup-keys/hardcoded-suspects),
   SEO for sites only (hreflang/canonical/lang/sitemap), RTL sanity. Engine
   runtime probes: Godot example probe runs here; Defold engine absent → NOT
   TESTED, state it.
3. **Plan** — severity BLOCKER>HIGH>MEDIUM>LOW>INFO; minimal diff; respect
   existing structure (`templates/` seeds for new projects only).
4. **Fix** — additive only: missing keys inserted as `TODO:<key>` scaffold;
   hreflang self-reference on static HTML. Existing values untouched.
5. **Verify** — re-audit inside `fix` (`verified:true`); CI gate rerun.
6. **Report** — `report --format json` for CI; numbers are measured, suspects
   marked `?`.

## Operating rules
- Never invent versions: re-probe npm/engine (`references/standards.md`).
- Machine translation = draft; human flips reviewed/approved; legal/safety
  text needs sign-off (`references/translation-quality.md`).
- Full sentences as keys; placeholders byte-identical across locales; no
  fragment stitching.
- Games: locale switch renames DISPLAY only — saves, input, IDs, net payloads
  frozen (`references/game-localization.md`).
- Heuristics (hardcoded-text, untranslated-identical, style) = suspicion,
  REVIEW_REQUIRED, never a CI failure and never a claimed defect.
- Pseudo expansion is a test parameter (default +30%), grapheme-based.

## Progressive disclosure
Deep docs: `references/` (standards, web-frameworks, game-localization,
testing-strategy, translation-quality, international-seo, unicode-rtl,
troubleshooting) · engine wiring: `adapters/<name>/NOTES.md` · seeds:
`templates/` · runnable proof: `tests/` (36/36 PASS incl. Godot headless probe
+ Lua core) · fixture: `tests/fixtures/web-shop` · web adapter examples point
at the fixture.
Command vs skill: this activates as skill `ultimate-i18n-localization`; the
six `i18n-*` binaries are standalone commands — no slash-command registry is
assumed.

## Activation (phrases)
"Mach dieses Projekt mehrsprachig" · "Füge Deutsch und Englisch hinzu" ·
"Prüfe/Repariere alle Übersetzungen" · "Vollständiger i18n-Audit" ·
"Prüfe Hreflang/Canonical" · "Pseudolokalisierung" · "Lokalisiere dieses
Godot-/Defold-Spiel" · "Teste de/en UI".

## Collaboration
seo-performance (hreflang ownership handoff), accessibility (lang/dir/
localized a11y names), ultimate-testing-qa (E2E lane), astro/react-nextjs/
godot/defold-development (integration), human-writing/design-authenticity
(style). Soft links only — this skill runs standalone.
