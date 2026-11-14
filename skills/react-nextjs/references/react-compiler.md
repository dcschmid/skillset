# React Compiler & Memoization Discipline

## Decision order (binding)

1. Is the project on the React Compiler? Next 16: supported/built-in path —
   check `next.config.ts` (`reactCompiler` / experimental flag per installed
   version) and `node_modules/next/dist/docs/`. Vite: `babel-plugin-react-compiler`
   (1.0.0 stable) or `vite-plugin-react-lib` equivalents. If on: **stop writing
   useMemo/useCallback** unless optimizing a measured, remaining bottleneck.
2. If the Compiler is OFF and the project is old-ish: memoize only measured
   hot paths, per component, with a comment naming the measurement.

## What the Compiler does / doesn't

- Auto-memoizes components and hooks per its rules (fine-grained reactivity);
  replaces hand `useMemo`/`useCallback` for props-identity chains.
- Doesn't: cache server data, replace a query library, make bad architecture
  fast (fetch waterfalls, context churn, list-size problems stay).
- Requires lint-clean Rules-of-React code; it fails a component to
  non-memoization, not to wrong output — but keep components pure.

## Adoption playbook (existing project)

1. Baseline: build + a render-profile of the slow route (React DevTools
   Profiler record, commit timings saved).
2. Enable per-scope where the tooling allows; run full test suite; fix
   Rules violations surfaced by `eslint-plugin-react-hooks` compiler mode.
3. Re-measure. Ship or revert per numbers. Keep `memo()`/manual memo that the
   Compiler can't reach (exported library APIs with stable-identity contracts)
   and document why.
4. New projects: enable from scaffold when React ≥ floor; document in README.

## Hand-memoization that stays valid with the Compiler

- `useMemo` for a value whose identity is an API contract to third-party code
  (observer options object consumed by a non-React lib).
- `memo()` on leaf components in huge lists *measured* to re-render wastefully.
- Context value stabilization: Compiler helps inside, but the provider
  re-render fan-out is yours — split contexts by update frequency.

## Verification loop

```bash
npx tsc --noEmit && npm run lint         # compiler + hooks lint pass
npm run build                            # Compiler transform in CI build
# React DevTools Profiler: commit durations before/after
```

Perf claims in reports: numbers + method, or the claim is dropped.
