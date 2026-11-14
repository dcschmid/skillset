# Integrations & Frameworks — opt-in, versioned

Official integrations ship separate packages; pin to the Astro baseline
(versions.md). Every integration = build cost + bundle surface: install with a
reason, list the reason.

## UI frameworks (react/vue/svelte/solid integrations)

Install only for real client-state islands (islands-interactivity.md ladder
rung 4). One framework per project unless proven otherwise. Component islands
with `client:*`; the framework runtime appears ONLY on routes rendering them.
Server-side: framework components render in SSR/prerender; `client:only` skips.
`@astrojs/react` 19-compatible pairs etc.: check pairing tables per release.

## Hosting adapters

Adapter = deploy contract for on-demand rendering; static sites often need
none. `@astrojs/node` (standalone server), `@astrojs/netlify`,
`@astrojs/vercel` (incl. edge), `@astrojs/cloudflare` (workers),
`@astrojs/static`-style hosts need no adapter. Adapter choice answers
deployment.md's hosting question; sessions/image/CDN-cache defaults differ
per adapter (read its docs section).

## Common helpers

- `@astrojs/rss`, `@astrojs/sitemap`, `@astrojs/mdx` (MDX content; Sätteri
  pipeline on 7), `@astrojs/check` (type-check .astro),
  `@astrojs/tailwind`/Tailwind Vite plugin (styling choice),
  `@astrojs/partytown` (third-party offload) — each: needed? yes → pinned.
- Image service: default sharp; `serviceConfig` per docs for density/formats.

## CMS/SDKs

Loaders (content-cms.md) wrap HTTP directly — SDK only if typed queries are
worth the dependency (Sanity client etc.). SDK init server-side only; keys
from env; responses validated with the collection's Zod schemas or mapped at
the loader boundary.

## Game/3D assets (skill-collection combo, optional)

Blender/Godot/Defold skills may produce web assets (glb, sprites, wasm builds).
Consumption stays Astro-native: static assets via `src/assets` + `astro:assets`
or `public/`; embed via iframe/canvas in a `client:visible` island only when
interaction is required; bundle-size check applies (game wasm ≠ free JS).
No dependency on those skills existing — assets arrive as files.
