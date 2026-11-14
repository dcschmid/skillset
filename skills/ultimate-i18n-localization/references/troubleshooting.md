# Troubleshooting — observed failure modes and their fixes

| symptom | cause | fix |
|---|---|---|
| `Reference locale: en` but project default is `de` | discovery can't see config | pass `--reference de` (audit flag) or add `defaultLocale` to config scan list in `scripts/lib/discover.mjs` |
| CSV values empty in Godot layout | header row treated as data | parser skips `keys/en/identifier/term` header; custom header → pass `valueColumn` |
| pseudo output missing `{name}` braces | engine pseudo (`TranslationServer.pseudolocalize`) accents identifiers too | assert brace STRUCTURE not token identity; use this CLI's pseudo for exact preservation |
| translations "missing" but files exist | dir not in candidate list (e.g. `content/i18n`) | `--locales-dir`, or extend candidates in discover.mjs |
| `de_DE` and `de-DE` both appear | mixed conventions | normalizeLocale at every boundary; catalogs keep the file's own convention |
| check exits 1 though everything translated | LOW/INFO findings exist but a HIGH confirmed (e.g. duplicate-key) remains | read `VERDICT` line `blocking=` count; tune `--fail-on` only with reason |
| CI noise from `hardcoded-text` | heuristic suspects are MEDIUM/unconfirmed | never fail CI on confirmed:false; gate is `f.confirmed && severity<=failOn` |
| Godot probe fails on newer engine | API surface drift | re-probe: dump `TranslationServer.get_method_list()`, update adapters/godot/NOTES.md |
| Defold claims break | engine absent, docs-era claims | mark NOT TESTED; verify `text.*`/i18n section against the project's engine version |

## Extending
- new format: parser branch in catalog.mjs + a test case
- new locale-specific plural rule: PLURAL_CATEGORIES + pluralCategory branch
  (+ unit test with 3+ counts)
- new framework: detection in discover.mjs + adapter NOTES with probe-or-NOT-TESTED
