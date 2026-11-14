# Performance — measured, not assumed

Loop: baseline → change → re-measure → report deltas. No optimization without
a named budget miss; no claim without numbers.

## Budgets (Core Web Vitals, p75 field or lab proxy)

LCP ≤ 2.5s · INP ≤ 200ms · CLS ≤ 0.1. State the target for the project;
devtools/Lighthouse/lab runs vs baseline committed.

## React/Next levers (ordered by payoff)

1. **Server/Client split** (rendering.md): every accidental client component
   adds bundle + hydration. Build output: client JS per route.
2. **Boundary discipline**: Suspense where fallback belongs; async server
   fetches parallel (`Promise.all`), no per-component waterfalls; stream the
   slow hole, ship the shell.
3. **Caching posture** (data-caching.md): right lifetimes ⇒ fewer DB/network
   round trips; wrong ones ⇒ stale UI bug debt.
4. **Compiler** on before hand-memo (react-compiler.md).
5. **Images/fonts**: `next/image` sizes matching layout; `next/font`
   self-hosted subsets; preloads only for the above-fold hero.
6. **Code-splitting**: `lazy` at route/heavy-modal; vendor chunks only where
   measured; check `.next`/dist sizes after.
7. **Lists**: virtualization above ~200 rows (react-window-class, opt-in);
   pagination/cursor server-side.
8. **Realtime/IO**: debounce/abort per state-management; SSE over WS when
   one-way.

## Measuring

```bash
npm run build                      # report: bundle + route sizes
# React DevTools Profiler: commit durations (before/after per change)
# Chrome/Lighthouse CI or `npx lighthouse <url>` lab runs, device throttled
```

INP: long tasks in handlers → move compute off the input path
(`useTransition`, server, workers). CLS: dimensioned media, font-display
strategy, no injected late banners.

## Hydration cost

Client components re-render server HTML: keep islands small; measure
hydration by component tree size (Profiler). Suspense streaming shifts
perceived latency; verify with throttled network.

## Anti-patterns (drop or justify)

memo-everything (Compiler era); store-everything; barrel files pulling whole
libs into routes; polling where push/invalidation exists; cache-everything
(data-caching.md); prefetch budgets ignored on mobile (app-router.md).
