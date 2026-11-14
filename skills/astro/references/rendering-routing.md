# Rendering & Routing

## Decision table (pick rendering per project, then per route)

| Site shape | Choice |
|---|---|
| All content known at build (portfolio, blog, docs, marketing) | `output: 'static'` (default), no adapter |
| Mostly static + a few dynamic routes (account, cart, search) | static output + adapter; dynamic routes `export const prerender = false` |
| All routes per-request (personalized portal) | `output: 'server'` + adapter; opt-in `prerender = true` per route |
| Static shell + personalized/late blocks | server islands (`server:defer`) on static pages |

7.x default: everything prerendered. `output: 'hybrid'` is gone (5.x removal):
mixed rendering = static default + per-route `prerender = false` + adapter.

## Enabling on-demand rendering

Requires an adapter (`@astrojs/node` standalone for self-host,
`@astrojs/netlify`, `@astrojs/vercel`, `@astrojs/cloudflare`...). Adapter =
host contract, not a framework choice; see integrations.md.

```ts
// src/pages/dashboard.astro
export const prerender = false;   // on-demand; needs adapter + output static default OK
```

On-demand features: `Astro.request`/`url` live, cookies, sessions
(>=5.7), `Astro.cache` (7+), actions work either side.

## Routing (advanced routing, 7+)

- File routes in `src/pages/`: `[slug]` param, `[...rest]` rest, `index`.
- `getStaticPaths()` generates static route set; returns `{params, props?}`;
  `props` = precomputed data per route (runs once at build — fetch there).
- Route-level exports: `prerender`, `partial` (page partials),
  `response` headers via `Astro.response.headers.set`.
- Endpoints: `.ts` files returning `export GET/POST` (Response/JSON).
- Middleware `src/middleware.ts` (`defineMiddleware`, `onRequest`):
  cross-cutting auth/redirects/locale; keep thin — advanced routing
  (`src/fetch.ts`) covers request-pipeline control on 7+ when needed.
- Redirects: config `redirect: { '/old': '/new' }` (static-safe) or
  middleware for dynamic.
- Streaming: on-demand responses stream by default in 7 (queue-based
  renderer); place slow fetches after early HTML where it matters.

## Route caching (7.0+)

Static routes: caching is host/CDN headers. On-demand: `Astro.cache`:

```ts
// route
Astro.cache.set({ maxAge: 120, swr: 60, tags: ['home'] });
// config routeRules for groups:
routeRules: { '/blog/[...slug]': { maxAge: 300, swr: 60 } }
```
- `cache.enabled` false in dev; test with `build`+`preview`.
- Invalidation: `cache.invalidate({tags})`; providers: memoryCache default,
  adapter CDN providers (netlify/vercel/cf) where supported — mark
  experimental per docs.
- Server islands on a cached static page: page stays aggressively cached,
  island re-renders per request — the pattern for "static + personalized".

## Sessions (5.7+) on-demand only

`Astro.session.get/set` (component), `context.session` (endpoint/middleware/
action), `session.regenerate()/destroy()`. Driver: auto on node/cf/netlify;
manual `session: { driver: sessionDrivers.lruCache(...) }` elsewhere;
`session: false` opts out (7.2+). Not in edge middleware.

## Build output check (verification)

Static: `dist/` has one `.html` per route. On-demand: `dist/server/` +
`dist/client/`. `--verbose`/timing output + Build Timing Diagnostics for slow
builds: `astro build --profile` per target docs (flag name verify per release).
Mixed: prerendered HTML files coexist with server chunk — inspect both, never
claim "fully static" after adding an adapter without checking `dist/`.
