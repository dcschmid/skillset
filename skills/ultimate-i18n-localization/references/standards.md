# Standards & live-probed versions (probe date 2026-11-14, npm registry + engine CLIs on this machine)

## Library baselines (npm `latest` at probe time — RE-PROBE against the project lockfile before use)
| lib | version | role |
|---|---|---|
| i18next / react-i18next | 27.1.1 / 18.0.1 | framework-agnostic / React |
| next-intl | 4.15.1 | Next.js App Router |
| intl-messageformat / @formatjs/* | 12.1.5 | ICU MessageFormat runtime |
| vue-i18n | 11.4.20 | Vue/Nuxt |
| @nuxtjs/i18n | 10.6.0 | Nuxt routing+i18n |
| svelte-i18n | 4.0.1 | Svelte |
| astro | 7.4.12 | native i18n routing (no lib needed) |

Never claim a version works that was not probed. Verify maintenance, license
and bundle size on the project's own constraints first (skillset rule: no
unnecessary dependencies).

## Engine truths (verified on this machine, see adapters/*/NOTES.md)
- Godot 4.7.2-stable ed1daf0bf: `TranslationServer` singleton surface probed;
  `PseudoTranslation` class ABSENT; `get_plural_rules("ar")` returns gettext
  nplurals=6 (matches CLDR).
- Defold: engine not installed → runtime claims are docs-verified only
  (`sys.load_resource` + JSON catalogs, `font.add_font/remove_font/prewarm_text`,
  SheenBidi bidi stack, pivot-based alignment, `custom_resources`, iOS
  `languages` list). Mark engine runs NOT TESTED.

## Locale identifiers
- BCP-47 `language-Script-REGION` (`de-DE`, `zh-Hans-CN`); canonical case
  language=lower, script=Title, region=UPPER. Files frequently use `_`
  (`de_DE`): normalize at every boundary; keep the engine's convention inside
  its files (Godot uses `_`, web uses `-`).
- Region sets are NEVER assumed: ship only regions the project declares
  (`de-AT`, `de-CH`, `en-GB`… add per project need).

## Formats
JSON (flat/nested), YAML subset, CSV (Godot key + locale-columns layout),
PO/POT (gettext, msgctxt, plural msgstr[n]), Fluent FTL (messages, selectors),
XLIFF 1.2 (`trans-unit id`, source/target). ICU MessageFormat vs MessageFormat
2.0: MF2 is not yet the default in the probed libs above; use what the runtime
parses.

## CLDR plurals (cldr.unicode.org/plurals, matches engine probes)
zero/one/two/few/many/other — sets per language in `scripts/lib/locales.mjs`
(`PLURAL_CATEGORIES`); ar=6, en/de/es/it/pt/nl/sv…=2, ja/ko/zh/tr/th=1,
ru/uk/pl=3, cs=3, he=4, fr: one(0,1)/many(≥1M)/other, lv/ga variants.
Unknown language → report INFO, never guess.

## Standards owners
Unicode UTS#35 (CLDR), UTS#9 (bidi), RFC 5646 (tags), Google localized-and-
regional docs, W3C i18n. Cite version/date in deliverables.
