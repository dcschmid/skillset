# Game localization — scope, invariants, storefront

## Content classes (translate vs freeze)
translate: menus, settings, HUD labels, tutorials, quest/mission text, story,
subtitles, achievements, error toasts, controller hints, localized art/fonts,
per-locale audio if produced.
freeze: internal object IDs, savegame fields, input bindings, network payloads,
gameplay numbers, brand/product names, seeds/hash strings. Display names are
never technical IDs — a locale switch renames what the player READS only.

## Invariants a locale change must never break
savegames, controls/mappings, gameplay logic, multiplayer state, protocols,
stable IDs. Persist the player's language in save/settings; in-game switch via
settings menu; restart only when the engine/asset pipeline forces it.

## Font/layout pipeline
per-script fonts (Arabic/Japanese) loaded via proxies/collections so inactive
fonts free RAM (Defold pattern: collectionproxy + font.add_font; Godot:
ResourceImporter + locale remap). Glyph prewarm before first paint
(`font.prewarm_text`). Subtitle boxes sized by LONGEST locale string, not the
source.

## Adapter status
godot/: runtime PROBE PASS on 4.7.2 headless (this machine).
defold/: engine NOT installed here — engine runs NOT TESTED; the pure-Lua core
(examples/game/defold/i18n.lua) passes under luajit and is the pattern to wire
into `sys.load_resource` catalogs.

## Storefront (Steam/itch)
store text and game localization are DIFFERENT deliverables: label reports
"store localized", "game localized", or both; never imply one from the other.
itch/Steam locale lists must match shipped in-game locales.
