# Internationalization — Astro i18n routing

i18n is a project decision; one-locale sites never add locale plumbing.

## Config (docs: guides/internationalization)

```ts
i18n: {
  locales: ['en', 'de'],
  defaultLocale: 'en',
  routing: { prefixDefaultLocale: false }, // /about vs /de/about
}
```
Routes with `src/pages/[...locale]/` or per-locale dirs; `Astro.currentLocale`
in components; `getRelativeLocaleUrl` for internal links (locale-aware).
Redirects from root for default locale per config (`redirectToDefaultLocale`).

## Content

- Locales inside collection schemas (`locale: z.enum([...])`) with per-locale
  entries, or one collection per locale dir (`content/<loc>/blog/...`).
- Query filters by `Astro.currentLocale`; index pages enumerate
  `i18n.locales` for alternates.

## SEO

- hreflang cluster per logical page: loop locales →
  `<link rel="alternate" hreflang="de" href={...}>` + `x-default` → default
  locale; absolute URLs via `site`; localized titles/descriptions per entry.
- `lang` attr on `<html>` = `Astro.currentLocale`; sitemap emits all locales.

## UX

- Language switcher: server-rendered links to sibling URLs (never JS-only);
  current locale marked (`aria-current="true"`).
- Dates: `Intl.DateTimeFormat(locale, ...)` server-side (build/request);
  numbers/units same mechanism.
- Translation dictionaries: plain typed TS objects for chrome strings
  (`src/i18n/ui.ts` pattern); no i18n framework until string count demands one.

## Verify

- MEASURED: every locale's routes 200; hreflang targets exist and are mutual;
  switcher round-trips; lang attr matches content language.
