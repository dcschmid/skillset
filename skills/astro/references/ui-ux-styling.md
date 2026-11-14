# UI/UX & Styling

Design language belongs to the project. This file fixes mechanics only.

## CSS strategy ladder

1. Scoped `<style>` in `.astro` — default; component-local, zero config.
2. Global tokens + utilities: `src/styles/global.css` imported in root layout;
   tokens as `:root` custom properties.
3. Tailwind — only if the project/team already uses it or breadth of bespoke
   UI makes utility CSS faster. Integration/version pairing per current docs.
4. CSS Modules for shared non-Astro TSX islands.
Never ship both a utility framework and heavy hand-written CSS doing the same job.

## Design tokens (mandatory structure, per-project values)

```css
:root {
  --color-bg: ...; --color-fg: ...; --color-accent: ...;  /* palette */
  --font-display: ...; --font-body: ...;                   /* stacks */
  --step-0: clamp(1rem, .95rem + .25vw, 1.125rem);         /* fluid scale */
  --space-2: .5rem; --space-3: 1rem;                       /* spacing scale */
  --radius: ...; --shadow: ...;
}
[data-theme='dark'] { /* overrides of the same tokens */ }
```
Components consume tokens only — no raw hex outside `tokens.css`; themes and
project re-skins then touch one file. Contrast check on token pairs, not on
components (accessibility.md).

## Layout rules

- Mobile-first; `min-width` queries. Container queries for reusable blocks
  (`container-type: inline-size`) — components adapt to slot, not viewport.
- Grid for page/section layout, flex for intra-component. Both native; no libs.
- Fluid type via `clamp()` in tokens; no JS resize handlers for type.
- Breakpoints from content, not device lists; usually 2 (nav collapse, grid
  columns) suffice.
- Stable sizing everywhere images/canvas live: `width`/`height` or
  `aspect-ratio` (CLS).

## Responsive nav / interaction, HTML-first

- `<details>` or CSS-only patterns for small nav; `dialog`+`popover` for
  modals/menus when JS allowed; Esc + focus-return handled natively or in ≤20
  lines.
- Touch: 44×44px targets, `scroll-snap` carousels (native, no JS),
  `touch-action` where gestures exist.
- Dark mode: token flip via `data-theme` (theme-switch snippet in
  islands-interactivity.md); respect `prefers-color-scheme` as default.

## Motion

- Animate `transform`/`opacity` only; wrap in
  `@media (prefers-reduced-motion: no-preference)` or provide a
  reduced-motion override block. Page transitions via `astro:transitions`
  ClientRouter when SPA-like feel is wanted (adds router JS — a decision,
  not a default).

## Fonts (Fonts API, 7.0)

`fonts` config with system/local/remote providers (verify per docs; pre-7:
manual `<link>` + `font-display: swap` + preload LCP font). Self-host files,
subsetted woff2, ≤2 families per site, fallback stack close in metrics
(`size-adjust`).

## Images in design

`astro:assets` `<Image/>`/`<Picture>` everywhere raster: srcset+sizes auto,
AVIF/WebP, `width`/`height` required, `alt` required ('' when decorative).
SVG stays inline/`<img>` for logos/icons. Hero: `loading="eager"` +
`fetchpriority="high"`; below-fold lazy (default).
