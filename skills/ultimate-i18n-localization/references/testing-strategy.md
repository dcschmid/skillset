# Testing strategy — evidence-first, no fake PASS

## What is actually tested on this machine (run: `node tests/run.mjs`)
36/36 PASS as of 2026-11-14: locales (normalize/validity/RTL/CLDR plurals),
catalogs (JSON+nesting, YAML, CSV Godot layout, PO, FTL, XLIFF, flatten/unflatten),
placeholders (named/numeric/ICU/sprintf/multiset), pseudo (accent+expansion+
placeholder-preservation+graphemes+mojibake), CLI integration (audit, check
exit-code, validate, fix verify-loop, extract, pseudo dir-mode, report JSON),
Godot headless TranslationServer probe (PROBE PASS + pseudo_braces_ok=true),
Defold i18n.lua pure-Lua core via luajit (LUA PASS). NOT TESTED: any browser/
Playwright run (engine-agnostic layer is CLI-only by design); Defold engine
runtime; Godot editor GUI; font rendering.

## Layered plan for a target project
1. Static (always): `i18n-check` — key parity, placeholders, plurals, hreflang,
   canonical, coverage, blocking-severity gate.
2. Engine runtime (only with engine installed): Godot `-s probe_*.gd` pattern
   (see examples/game/godot); Defold in-repo headless bootstrap or mark
   NOT TESTED.
3. Browser E2E (sites, if Playwright present): locale switch persists, URL
   locale routing, `<html lang>`/dir per locale, RTL isolate rendering,
   screenshot overflow checks under pseudo locale; Firefox default per profile.
4. Regression after each fix: re-run the narrowest failing check first, then
   full `i18n-check`.

## Pseudolocalization protocol
- expansion is a TEST parameter (default +30%, configurable); report the value.
- run grapheme-based length math (`Intl.Segmenter`); codepoints lie for
  combining marks and emoji sequences.
- screenshot set: narrowest container (button, nav item, HUD chip) + one page;
  diff against same locale baseline.
- RTL pseudo run = bidi-isolate wrapped; a flipped screenshot is NOT enough —
  check pivot/flow direction per component.

## Honest verdicts
PASS = executed with measured output. REVIEW_REQUIRED = heuristic/visual
suspect (untranslated-identical, RTL-isolation, style) — never CI-blocking.
NOT TESTED = environment lacks the capability; state what is missing, never
borrow a PASS from an adjacent layer.
