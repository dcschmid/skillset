# Styling & Design Systems — framework-neutral

No CSS framework assumed. Choose by project; record the choice.

## Selection ladder

1. Project already styles something → extend it (tokens, class naming,
   utility lib, component kit). Consistency > personal taste.
2. New project: native CSS + custom properties is always viable; CSS Modules
   for scoped component styles without tooling; Tailwind when utility-first
   matches the team (opt-in dependency, config + content globs correct);
   CSS-in-JS only where runtime theming genuinely needs it (note RSC cost:
   runtime-injected styles vs Server Components friction — read local docs).
3. Component libraries (Radix/headless, shadcn/ui copy-in) when building
   primitives from scratch would repeat solved a11y work (menus, combobox,
   dialogs). One kit per project.

## Design tokens (the portable layer)

Custom properties define the system: `--color-*`, `--space-*`, `--radius-*`,
`--font-*`, `--shadow-*`, `--z-*`. Framework-agnostic; Tailwind theme maps to
them; light/dark = swap the token block under `[data-theme=dark]`/media query.
Components consume tokens only — no raw hex in components. Token set lives in
one file; naming stable across refactors.

## Quality bar (every delivered surface)

- Hierarchy: one h1/page; heading levels in order; readable line length;
  contrast ≥ AA (a11y.md).
- Spacing/type scale: from tokens, no magic numbers per component.
- Responsive: mobile-first; container queries where the component owns its
  box; fluid type via `clamp()` on body copy.
- States: loading, empty, error, disabled, focus-visible — every interactive
  component ships all five or the gap is named.
- Motion: purposeful, `prefers-reduced-motion` honored; layout-stable
  (CLS, performance.md).
- Touch/keyboard: hit targets ≥ 24px; `:focus-visible` styles present.

## Theming

Light/dark via tokens (never duplicate component trees). Theme switch = token
swap + `color-scheme` + no flash (inline script or framework mechanism).
Multi-brand = token files per brand.

## Reusable components

Props = behavior, variants = data (a `variant` map or CVA-style function if
the project chose one), composition over booleans (react-core.md). Library
components stay presentation-pure; data-fetching components stay feature-local.
