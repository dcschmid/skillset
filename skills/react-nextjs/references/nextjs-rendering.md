# Rendering — Server/Client boundary, strategies, hydration

## Boundary rule (binding)

**Server Components by default. `"use client"` only where browser APIs,
state, or event handling must live in the browser.** A file boundary is the
contract: `"use client"` at the top ships the module + imports to the bundle;
everything without it stays server-side (unless a client parent drags it in).

Decision list per component:
1. Needs DOM/`window`, `useState`, `onClick`, `useEffect`, refs? → client.
2. Needs to render on server for SEO/streaming/data locality? → server.
3. Both? Split: server shell fetches, smallest client leaf interactive.
4. Neither forced → server (smaller bundle, no hydration cost).

Verify split: build output client bundle size (`performance.md`) — every
accidental client component above a big tree inflates it.

## Strategies (choose by requirement, document the choice)

| Strategy | When | Mechanism |
|---|---|---|
| Static rendering | content known at build/deploy | default for non-dynamic data; `generateStaticParams` |
| On-demand (dynamic) | per-request data, auth-personalized | `dynamic = 'force-dynamic'` (segments) or dynamic APIs (`cookies`, `headers`, `await request.*`) |
| Streaming | slow subtrees behind fast shell | `Suspense` + async Server Components |
| PPR / cache-components posture | mix static shell + dynamic holes, instant nav | `cacheComponents` + `partialPrefetching` (16; read local docs) |
| CSR-only | app-shell tools, no SEO need | client components + client fetching (rare in App Router) |

Hydration: server HTML + client islands. Hydration errors: mismatched
markup (browser extensions aside — legit causes: `Date.now()`/`Math.random`
in render, `window` conditionals, invalid nesting). No unexplained hydration
errors in shipped work.

## Suspense & streaming discipline

- Boundaries where the fallback belongs visually; not one root boundary.
- Async Server Component + Suspense = streamed holes; ensure the awaited work
  isn't a waterfall (`performance.md`: parallelize with `Promise.all` at the
  fetch layer).
- `loading.tsx` = route-level first-load fallback; Suspense = component-level.

## Server/Client data handoff

Server → client: serializable props (strings, dates-as-strings, plain
objects). Functions, class instances, DB handles don't cross. Keep secrets
server-side; client bundles are public.

## Migration note (Pages → App rendering)

`getServerSideProps` → async Server Component fetch; `getStaticProps` →
static rendering + `generateStaticParams`; `_app` providers → root layout.
Per-route, verify each with the 10-point gate before the next.
