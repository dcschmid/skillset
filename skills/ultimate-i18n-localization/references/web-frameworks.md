# Web framework integration — verify against the project's lockfile first

Baselines (probe 2026-11-14): astro 7.4.12, next-intl 4.15.1, i18next 27.1.1,
react-i18next 18.0.1, vue-i18n 11.4.20, @nuxtjs/i18n 10.6.0, svelte-i18n 4.0.1,
intl-messageformat 12.1.5. Never emit config for a major you didn't check.

## Astro (prefer native, no lib)
`astro.config.mjs`:
```js
i18n: { locales: ['de','en'], defaultLocale: 'de', routing: { prefixDefaultLocale: true } }
```
Middleware auto-redirects by Accept-Language only when no explicit locale is
chosen; user choice must win (persist + honor it). `getRelativeLocaleUrl`,
`getAbsoluteLocaleUrl` for links. Catalogs: plain JSON/TS in `src/i18n/` or
content collections for pages. `<html lang>` from the locale; dir for RTL
locales. SEO: emit hreflang alternates per locale route (self + all siblings).

## Next.js App Router
next-intl 4.x: `next.config → createNextIntlPlugin`, `src/i18n/request.ts`,
`middleware` with matcher, `[locale]` segment, `setRequestLocale` for static
rendering. Messages as JSON/TS, per-namespace `getMessages()`. Don't hand-roll
a locale detector that overrides a persisted user choice.

## React (SPA/Vite) + i18next
`i18next` + `react-i18next`, namespaces, `Suspense` lazy loads, backend only
when catalogs are runtime-served. Key rules identical to skill core.

## Vue/Nuxt
@nuxtjs/i18n 10: `i18n` key in nuxt.config, locales files, `localePath`,
strategy `prefix_and_default` mirrors the Astro prefix choice. vue-i18n 11
composition mode (`useI18n`) for components.

## Svelte/SvelteKit
svelte-i18n 4 or paraglide-js; init in `+$lib`, await in `+layout`. Route
locale via `[lang]` param + handle hook.

## Coherence rules (every framework)
- Locale codes canonical in config, tolerant on disk (`de_DE`→`de-DE`).
- One default, explicit fallback chain, persisted user choice beats
  Accept-Language.
- hreflang: every locale page self+siblings, absolute URLs, valid codes
  (audit enforces). Canonical = own URL per locale.
- No machine translations silently shipped as final; mark draft until
  human-reviewed.
- Tests: switch locale → assert rendered text, dir, lang attr; pseudo locale
  for overflow (references/testing-strategy.md).
