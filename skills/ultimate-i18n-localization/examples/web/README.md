# Web example

The canonical runnable example is `tests/fixtures/web-shop/` (Astro 7 layout,
`src/locales/{de,en}.json` with deliberate drift: missing keys, placeholder
rename `{name}`→`{username}`, en-only key). It powers the integration tests.

```bash
S=~/dev/github/skillset/skills/ultimate-i18n-localization
node $S/scripts/i18n audit --root $S/tests/fixtures/web-shop
# Reference locale: de (honors defaultLocale), missing-key: 2, placeholder-mismatch, coverage measured
node $S/scripts/i18n check --root $S/tests/fixtures/web-shop   # exit 1 + VERDICT FAIL (expected drift present)
```
Expected findings and their meaning: see `references/troubleshooting.md`.
A clean-project run: copy `templates/locales/*.json` into a scratch project —
`check` exits 0 with `VERDICT PASS`.
