# Audit a shop fixture with localization drift

The runnable test project is in `../../tests/fixtures/web-shop/`. It deliberately
contains missing keys, a renamed `{name}` → `{username}` placeholder, and an
English-only entry. `defaultLocale` selects German as the reference language.

From the repository root:

```bash
node skills/ultimate-i18n-localization/scripts/i18n audit --root skills/ultimate-i18n-localization/tests/fixtures/web-shop
node skills/ultimate-i18n-localization/scripts/i18n check --root skills/ultimate-i18n-localization/tests/fixtures/web-shop
```

The audit should show drift. The check should return exit code 1 and FAIL
because those errors are intentional. Do not repair this fixture in place:
the integration tests rely on its defects.

```text
Use ultimate-i18n-localization. Explain the shop-fixture findings, then audit
our own catalogs using German as the reference language. Report only.
```

For a clean experiment, copy `../../templates/locales/` into a separate test
project. See [troubleshooting.md](../../references/troubleshooting.md) for finding
interpretation and the [skill README](../../README.md) for setup and usage.
