# Data & Caching — Next.js (16 Cache Components line; 15 fetch-cache for old)

Never cache by habit. Every cached query needs: source, lifetime, key,
invalidation trigger. User/personal data ⇒ isolation or request scope, never
a shared cache key.

## Installed-version gate

Next 16 with `cacheComponents: true` (+ `partialPrefetching`) = explicit model:
`use cache`, cache lifetimes, tag invalidation. Next ≤15 / flag off = fetch
`cache`/`next` options + Full Route Cache defaults. Do not mix vocabularies;
read `node_modules/next/dist/docs/` for the installed version first.

## `use cache` (16)

```tsx
async function getArticle(slug: string) {
  "use cache";
  cacheTag(`article:${slug}`);           // tag for targeted invalidation
  return db.article.findUnique({ where: { slug } });
}
```
- Marks the function's result cacheable across requests; keys derived from
  args (serialize-able) — stable args or you miss silently.
- **Cache lifetime:** `cacheLife('hours')` style presets + custom
  (local docs name the exact API for the version). Choose by data churn,
  state the number in the PR.
- Personalization: per-user data ⇒ include the user id in the key args or
  keep the read outside `use cache`. Cross-user bleed through a shared key is
  a data-leak bug.

## Invalidation

| Trigger | Tool | Notes |
|---|---|---|
| entity mutated (content) | `revalidateTag(tag)` / `updateTag` (in-action) | same request = updateTag posture; read local docs |
| route content changed | `revalidatePath('/blog/[slug]')` | path-scoped |
| unknown tags | last-resort `revalidatePath('/', {layout:true})`-class sweeps | write an invalidation map instead |
| build-time data | regenerate/redeploy | CMS webhook → tag invalidation beat polling |

Every mutation site lists the tags it invalidates (code comment). Missing
invalidation = stale data; excess = cacheless with extra steps.

## Request-scope & isolation

Per-request data (cookies, headers) → component/route is dynamic for that
request; shared cache holds only shared data. `cacheLife` on a personalized
tree needs the personal part outside the cache or keyed.

## Server Components data fetching

Async in components; parallelize (`Promise.all`) independent reads;
`no-store` equivalent semantics via version-correct API only for genuinely
per-request data. Streaming holes: Suspense around slow reads (rendering.md).

## Non-Next / client data

React-only or query-library territory: TanStack Query (opt-in) for client
server-state cache with explicit `staleTime`; AbortController on unmount;
no duplicate server caches when a server cache exists.

## Cache review checklist (per cached read)

1. Whose data? (shared / per-user / per-request) → key scope.
2. Lifetime = data churn, stated.
3. Invalidation path exists and is tested (mutate → stale → fresh).
4. Secrets stripped from cached payload before client handoff.
5. Verified against installed-version docs, not memory.
