# Defold adapter — documentation-grade facts. The Defold engine is NOT
# installed on this machine, so every engine-execution path here is
# UNTESTED locally; facts marked (verified docs) come from official
# defold.com pages fetched 2026-11-14. Facts marked UNVERIFIED must be
# re-checked against the project's engine version before shipping.

## Verified docs (defold.com llms/manuals + localization example, 2026-11-14)
- Official example `examples/gui/localization` ("Localization (RTL/LTR)"):
  localized strings live in JSON files (`text_en.json`, `text_ar.json`, …)
  bundled via game.project `[project] custom_resources` (comma-separated
  list; directories recursive) and read at runtime with `sys.load_resource()`
  (verified in manual + example README).
- Runtime font switching: `font.add_font()` / `font.remove_font()`; language
  fonts loaded through collection proxies (`ar_proxy` -> `lang_ar.collection`)
  so inactive fonts release their memory (documented best practice).
- Glyph prewarming: `font.prewarm_text()` before first render.
- Text layout stack: HarfBuzz, SheenBidi, libunibreak, SkriBidi (manuals)
  — so bidi/RTL shaping works engine-side with the right fonts.
- RTL needs an App Manifest with `Use full font layout system` enabled
  (example README) and Font `Runtime Generation` in game.project.
- GUI text node alignment is PIVOT-driven: pivot West=left-align,
  East=right-align, Center=Center. RTL alignment = swap node pivot
  (West<->East) at language switch, plus anchor math. `gui.set_line_break`,
  `gui.set_text`, `gui.set_font` verified in gui-text manual.
- iOS: `[project] languages` must list every shipped locale or `sys.get_info()`
  never reports them (localization checklist, manuals).

## UNVERIFIED locally (verify against project's engine version)
- `text.translate()`, `text.load_translations()`, `.translation` resource
  files: absent from the llms-full.txt dump this machine could fetch; the
  gui-text-translations manual could not be retrieved (404 at probe time).
  If the project's engine ships them (1.99+ era docs mention them), prefer
  the native path — check `defold.com/ref/text/` for that version.
- `[i18n]` game.project section: not found in project-settings docs dump;
  do not emit these keys without confirming the engine version.

## Community option
- `defold-lang` (Insality) — free localization helper lib (assets.defold.com,
  release 5, 2026-06-14, verified listed). Library choice stays the project's;
  the skill never installs dependencies silently.

## Recommended portable pattern (fixture: examples/game/defold/)
1. `locales/de.json`, `locales/en.json` (+ per-locale font .font resources)
   in `[project] custom_resources`.
2. `i18n.lua` module: `load(locale)` reads JSON via `sys.load_resource` +
   `json.decode`; `t(key, params)` interpolates `{name}` placeholders;
   `set_locale(l)` swaps GUI fonts via font.add_font/remove_font, flips
   text-node pivots for RTL, calls font.prewarm_text on HUD strings, then
   re-renders open screens. Persist the choice in saved game data.
3. Savegames keep numeric/string IDs; translations are display-only — a
   locale change MUST NOT rename object ids, input bindings, or net payloads.

## Storefront
Translate store pages (Steam/itch) separately: store text localized does
NOT mean the game is localized — label both states distinctly in reports.
