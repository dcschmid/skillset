# Next.js App Router — structure, routes, conventions (Next 16 line)

Authoritative for the installed version: `node_modules/next/dist/docs/01-app/`
(read before implementing anything non-trivial). Pages Router = existing
projects only; keep its model, don't mix.

## Project shape (App Router)

```
app/
  layout.tsx        root layout: html/body, providers, metadata
  page.tsx          route UI (Server Component by default)
  loading.tsx       route-segment loading UI (Suspense fallback)
  error.tsx         segment error boundary (client component, takes `error`)
  global-error.tsx  root error boundary (must render own html/body)
  not-found.tsx     404 UI for segment
  template.tsx      re-mounted on navigation (state reset — use rarely)
  (marketing)/      route group: URL-neutral sectioning
  blog/[slug]/page.tsx
  dashboard/@modal/(.)post/[id]/   parallel + intercepting
api/route.ts        Route Handlers (REST endpoints)
proxy.ts            request interception (Next 16; replaces middleware.ts)
```

Component conventions: `page`/`layout`/`default` default-exported; typed
params via `params: Promise<…>` (async params since 15; await in Server
Components). Dynamic segments, search params likewise awaited when read.

## Route decisions

| Need | Mechanism |
|---|---|
| sectioning without URL change | route groups `(name)` |
| dynamic URL segment | `[seg]` + `generateStaticParams` for known-at-build |
| catch-all | `[...seg]` / optional `[[...seg]]` |
| same-level simultaneous views | parallel routes `@slot` + layout slot props |
| modal-over-route overlays | intercepting `(.)seg` + parallel slot + `<Link>`-driven close |
| data for many routes | fetch in Server Components + cache policy (data-caching.md) |
| REST/webhook endpoints | `app/**/route.ts` handlers |
| redirects/rewrites/headers/i18n at edge of request | `proxy.ts` (read local docs; Node runtime caveats differ from old middleware) |

## Metadata & navigation

- Metadata: export `metadata` const or `generateMetadata({params})`; OG via
  `openGraph`, icons, `title.template`. Static `sitemap.ts`, `robots.ts`,
  manifest conventions over hand-rolled `<head>`.
- Navigation: `<Link>` (client-side + prefetch) for app-internal;
  `next/navigation` `useRouter`/`usePathname`/`useSearchParams` in client
  components; `redirect`/`notFound` from Server Components.
- Prefetch on 16: instant-navigation posture — Link prefetch defaults
  aggressive; partial prefetching under `cacheComponents`; budget for it
  (`performance.md`). Read local docs before tuning flags.

## Route Handlers

```ts
// app/api/health/route.ts
export async function GET() {
  return Response.json({ ok: true });
}
```
They are public HTTP surface: validate, auth-check, rate-limit like any
endpoint (security.md). Runtime/config exports per file, no pages-router
`getServerSideProps` porting.

## Pages Router (existing projects)

`pages/`, `_app`, `_document`, `getServerSideProps`/`getStaticProps` stay as
is. Migration = ordered project (`migrations.md`), route-by-route, not
big-bang.

## Version traps (16 line)

- `proxy.ts` over `middleware.ts` for new code (deprecated ≠ removed: 15 apps
  keep middleware.ts).
- Turbopack default for dev AND build (16); webpack fallback via flag — read
  local docs for the installed version's exact escape hatch.
- Cache model changes ride `cacheComponents` opt-in — never assume a 15
  fetch-cache question has a 16 answer (data-caching.md).
- React 19.2+ features (`<Activity>` etc.) ride the bundled React; check floor.
