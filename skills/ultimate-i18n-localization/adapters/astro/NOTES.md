# Astro adapter — native i18n routing (astro 7.4.12 probed 2026-11-14)

Prefer Astro built-ins; no library unless the project needs translation
tooling beyond routing. Details: references/web-frameworks.md.

Integration order for a new project:
1. `astro.config.mjs` → `i18n: { locales, defaultLocale, routing }` (codes
   canonical `de`/`en`; `de_DE` style gets normalized by discovery — keep
   files consistent with what you declare).
2. Catalogs `src/i18n/locales/{de,en}.json` (audit auto-finds them; else
   `--locales-dir src/i18n/locales`).
3. Links via `getRelativeLocaleUrl(locale, path)`; never hand-build locale
   paths. `<html lang={Astro.props.locale}>` per render + `dir` for RTL.
4. hreflang alternates from the same route map (`i18n audit` enforces).
5. Persisted user choice beats Accept-Language — Astro's auto-redirect runs
   only pre-choice; add a small middleware/pref cookie if the product needs
   sticky locale.

Verification on a project: `i18n check --root <project>` (keys/placeholders/
SEO) + component test that locale change re-renders text. Engine execution:
no separate runtime — Astro is Node; CLI checks cover static truth.
