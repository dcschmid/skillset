# React (Vite/SPA) adapter — i18next 27.1.1 / react-i18next 18.0.1 (probed)

Framework-level: i18next + react-i18next only when the project is a SPA
without a router-level locale system; Astro/Next get native paths (their
adapter NOTES). Lazy namespaces + Suspense to avoid bundle bloat.

Wiring: `i18n.init({ lng, fallbackLng, resources|backend })`; namespaces per
domain; `useTranslation('ns')`; interpolation stays `{name}`-style = the CLI's
placeholder grammar (audit parity holds). Locale persistence: localStorage +
`changeLanguage` re-renders; no full reload.

Tests: component render under two locales, key parity via `i18n check`.
RTL: i18next dir handled app-side; CSS logical properties + `dir` on root.
