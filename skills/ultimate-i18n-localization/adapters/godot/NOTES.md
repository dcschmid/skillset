# Godot adapter — verified against Godot 4.7.2-stable (ed1daf0bf), probed on
# this machine 2026-11-14 via `godot --headless --script`. All API claims
# below were executed headless; anything else is marked UNVERIFIED.

## Verified runtime facts (Godot 4.7.2, `godot --headless --script`)
- `TranslationServer` is an engine SINGLETON — `TranslationServer.new()` is a
  parse error. `extends SceneTree` + `quit()` in `_init()` for probe scripts.
- Working set (executed): `add_translation`, `remove_translation`,
  `translate(key)`, `translate_plural`, `tr`, `tr_n`, `has_translation`,
  `set_locale`, `get_locale`, `get_loaded_locales`, `find_translations`,
  `get_translations`, `get_or_add_domain`, `has_domain`, `remove_domain`,
  `get_translation_domain`, `set_translation_domain`, `compare_locales`,
  `standardize_locale`, `get_language_name` (ONE argument),
  `get_plural_rules(locale)`, `pseudolocalize`,
  `set_pseudolocalization_enabled(bool)`, `is_pseudolocalization_enabled`,
  `reload_pseudolocalization`, `format_number`, `parse_number`.
- NOT present on 4.7.2: `translate_key` (pre-4.4 name), `translate_context`,
  `get_fallback_locale`/`set_fallback_locale`, `OS.get_locales()` style
  accessors on TS. Do not emit them.
- The `PseudoTranslation` CLASS is absent from ClassDB, BUT the engine
  pseudo-localization FEATURE exists as singleton methods:
  `TranslationServer.pseudolocalize("Hello {name}")` -> `"[Ĥéłłô {ήám̀é}]"`
  (accent map + brackets; placeholder BRACES survive, the identifier inside is
  transformed too — assert brace structure, not token identity).
  Toggle: `set_pseudolocalization_enabled(true)` + `reload_pseudolocalization()`.
- `standardize_locale("de_DE")` -> `"de_DE"` (keeps underscore; engine locale
  strings use underscores, BCP-47/CLDR docs use hyphens — convert at the edge).
- `get_plural_rules("ar")` -> `"nplurals=6; plural=(n==0 ? 0 : n==1 ? 1 :
  n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 && n%100<=99 ? 4 : 5);"`
  (gettext-style; matches CLDR ar exactly — the skill's tables match this).
- `Translation` resource: `locale`, `add_message(key, msg)`; keys/messages are
  parallel `PackedStringArray`s. `tr_n(singular, plural, count)` is the
  in-code plural call (verified returns the translated plural form).
- `translate_plural(context,key,plural,n)` exists but argument order is
  StringName-based; prefer `tr()`/`tr_n()` + `set_locale` in scripts.
- Editor classes (`EditorTranslationParserPlugin`,
  `ResourceImporterCSVTranslation`) are editor-only; absent at `--script` time.

## project.godot keys (documented, not headless-executable)
```
[internationalization]
locale/translations=PackedStringArray("res://locale/de.csv", "res://locale/en.csv")
locale/fallback="en"
locale/translations_allow_csv_import=true
rendering/right_to_left_mode=1   ; auto
```
CSV import is editor/bake-driven: first row locale codes, first column keys:
```csv
keys,en,de
nav/home,Home,Startseite
actions/save,Save,Speichern
```

## Runtime switch pattern (verified primitives)
```gdscript
TranslationServer.set_locale("de")
var s := TranslationServer.translate("nav/home")     # "Startseite"
var p := TranslationServer.tr_n("{n} item", "{n} items", n)
```
Missing key falls back to fallback locale then the key itself; check
`has_translation` before rendering if empty-vs-key matters.

## Resource remap for localized art/fonts
`ResourceTranslator`/remap maps are documented; headless-untested. Treat
locale-specific textures/fonts as a build-time remap, IDs stay stable.

## RTL
`rendering/right_to_left_mode` + Control auto-mirroring; do NOT mirror
sprites/HUD art, coordinate arrows, or media controls — judge per asset.

## Probe self-test (RUNS on this machine)
`examples/game/godot/` — `godot --headless --path <dir> -s probe_i18n.gd`
prints `PROBE PASS` + measured counts. That is the adapter's proof.

## Explicitly NOT TESTED on this machine
- Editor GUI locale editor, live CSV import into a running editor
- Visual font swap / RTL rendering (no display), `PseudoTranslation` class
  (feature is via singleton methods above)
