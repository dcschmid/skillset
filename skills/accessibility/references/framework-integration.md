# Framework integration — React/Next.js, Astro (compact; others later)

Baseline: never rebuild native HTML features. Semantic HTML ships the a11y
tree; frameworks only add wiring for navigation and portals.

## Shared rules (all frameworks)

- component APIs accept `id`, `label`, `describedBy` pass-through; no hardcoded ids (SSR collisions → `useId()` / framework equivalents)
- client-side nav: manage focus on route change (heading tabindex="-1" + focus(), or live region page-announce)
- portals/dialogs: keep within trap (dialog) or `inert` the background; restore focus to opener
- forms: native validation attrs + server error map → `aria-describedby`/`aria-invalid` in render, not imperative DOM hacks
- lint: `eslint-plugin-jsx-a11y` (React) / `@astrojs` + stylelint-a11y; CI-gate `a11y audit` on preview URL

## React / Next.js specifics

- Server Components render static semantics free — put interactive islands where state demands (client boundary), not everywhere
- Suspense fallbacks: reserve layout (`min-height`) so SR reading position survives swap; fallbacks need no live-region noise
- `next/link`/`<Link>` inherits `<a>` semantics; keep `prefetch` caveats out of a11y
- route change announcements: use routing events (App Router: `usePathname` effect) to focus `#main-heading`
- hydration: identical server/client markup or SR sees ghosts; `aria-pressed` etc. state must survive hydration
- component tests: Vitest + Testing Library queries by role/name (assert the contract, not DOM)

## Astro specifics

- content-first pages get semantics from Markdown/MDX headings — enforce one h1 via rehype or template
- islands: minimal client boundaries; `client:idle` fine for a11y, but keep labels server-rendered inside island
- Actions: form renders `aria-invalid`/`aria-describedby` from server result; focus first error field after rerender (effect keyed on errors)
- `astro check` no a11y rules — rely on eslint style + `a11y audit` in CI against `astro preview`
- view transitions (`transition:navigate`): observe `astro:after-swap` → focus main heading; skip-link target must exist per page

## Component libraries / design systems

Ship a11y contract as tests: every Button/Input/Dialog exports a
Playwright/CT test covering keyboard + name/role/state. Docs site =
the tool's own audit target (`a11y audit` on Storybook/Ladle).

## Regression prevention

- per PR: `a11y audit` on changed routes (CI job exits 1 on AA blockers)
- component stories in both light/dark, desktop/mobile viewport
- new widget → must add keyboard-testing.md checklist item to PR template
