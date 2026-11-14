# Next.js adapter (next-intl 4.15.1 probed 2026-11-14; App Router focus)

New projects App Router + next-intl; Pages Router: i18next or next-intl
legacy setup — detect the router from `pages/` vs `app/` before wiring.

Wiring (verify the project's next-intl major against its docs first):
- `createNextIntlPlugin` in next.config; `src/i18n/request.ts` loads
  `messages/{locale}.json` (audit-compatible JSON);
  `middleware.ts` localePrefix matches the site's URL policy;
  `[locale]/` segment + `setRequestLocale` for static rendering.
- server components `getTranslations`, client `useTranslations`; namespaces
  keep bundles small (per-namespace message files).
- user choice persistence: cookie `NEXT_LOCALE` — honor over Accept-Language.

Audit hook: `i18n audit` finds `messages/` or `src/messages/` via localesDir;
run it in CI (templates/ci/github-action.yml). hreflang comes from the same
[locale] route map — one source of truth, no hand lists.
