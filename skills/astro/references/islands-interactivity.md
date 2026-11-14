# Islands & Interactivity — minimal JS, explicit hydration

## The ladder (use the first rung that works)

1. HTML/CSS only: `<details>`, `:target`, CSS `:has()`, scroll-snap, radio
   tabs, native form validation, `dialog` + `popover` attributes.
2. Small inline script in `.astro` `<script>` (bundled, hoisted) or
   `<script is:inline>` for trivial glue (theme toggle, nav toggle).
3. Server island (`server:defer`) when content is dynamic but UI is not.
4. Client island (framework component + `client:*`) only when there is real
   client state (search-as-you-type, drag, canvas).

Each rung up: state the reason in one line. No framework for accordions.

## Hydration directives (client islands)

| Directive | Use |
|---|---|
| `client:load` | critical interactive-now (hero carousel controls) |
| `client:idle` | non-critical (comment box, share menu) |
| `client:visible` | below-fold/deferred (gallery, chart) — default guess |
| `client:media={q}` | viewport-dependent (mobile nav on small screens) |
| `client:only="react"` | SSR-broken lib; skips server render |

Rules:
- Directive on the component tag, per-island — never a global "hydrate all".
- Props must be serializable (JSON-ish); pass ids/data, not functions.
- Framework ships per-island bundle: check output size after adding one.
- `client:visible` needs stable layout: fallback/skeleton with final
  dimensions (CLS).

## Forms → Actions (4.15+) — typed server functions

```ts
// src/actions/index.ts
import { defineAction } from 'astro:actions';
import { z } from 'astro/zod';

export const server = {
  newsletter: defineAction({
    accept: 'form',                    // 'form' | 'json'
    input: z.object({ email: z.string().email() }),
    handler: async (data, ctx) => {    // ctx: ctx.session, ctx.cookies, ctx.callAction
      return await subscribe(data.email);
    },
  }),
};
```

- Progressive-enhancement form: `<form method="POST" action={actions.newsletter}>`
  works with JS off; read result via `Astro.getActionResult(Astro.request)`
  server-side for errors/redirect.
- JSON calls from islands: `await actions.newsletter({ email })` → `{data, error}`.
- Server-side reuse: `await Astro.callAction(actions.newsletter, input)`.
- Validation errors are typed; throw `new ActionError({ code, message })`
  for user-safe failures. No hand-rolled POST endpoints for typed calls.

## Search/filter patterns

- Static site + tiny JSON: build-time `getCollection` → `/search.json` +
  1-2 KB filter script. Default for blogs/docs.
- Or FlexSearch/lunr inside a `client:visible` island when index >~100 KB.
- SSR: action + debounced input, results server-rendered into the island.
- Never: instant search over the whole site shipped as JS on every page.

## Theme switching (no flash)

`<script is:inline>` in `<head>` reads `localStorage` +
`prefers-color-scheme`, sets `class`/`data-theme` on `<html>` before paint;
tokens in CSS vars. Not an island; 20 lines, zero hydration cost.

## Minimal-JS budget

Target: zero JS on content routes; islands only where interaction exists;
framework bundle only per island. Check `dist/` chunk sizes after every
interactivity addition — bundle growth is the review signal.
