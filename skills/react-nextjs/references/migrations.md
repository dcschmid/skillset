# Migrations & Legacy — stepped, reversible, verified

Scope: React/Next version bumps, JS→TS, Pages→App, old→current APIs
(middleware→proxy, fetch-cache→Cache Components), tooling refresh,
component refactors.

## Protocol (every migration)

1. **Inventory:** installed versions, lockfile, config surface, affected
   files (count), test coverage state. `scripts/check-versions.sh`.
2. **Read the official migration guide** for the exact step
   (nextjs.org/docs/app/guides/migration-guides; React releases) + local
   `node_modules/next/dist/docs/` after bump for the new truth.
3. **Risk note** before touching code: breaking changes list, blast radius,
   rollback plan (branch/commit + lockfile pair).
4. **Small steps:** one concern per commit — dep bump, then codemod-verified
   edits (reviewed hunks, never blind `npx @next/codemod` on the tree), then
   config, then tests green. Gate per testing.md between steps.
5. **Record:** before/after versions, decisions, leftovers marked.

## Known paths (verify against installed floors first)

- **React 18→19:** `ref` as prop (drop forwardRef on touched files),
  `useActionState` over removed beta `useFormState`, effects/refs timing
  strictness; test suites for legacy lifacles.
- **Next 13/14/15→16:** async `params`/`searchParams` awaited; App Router
  defaults; `proxy.ts` new code, `middleware.ts` stays until ordered
  (deprecated ≠ removed); fetch-cache → `cacheComponents`+`use cache` only
  as ordered project; Turbopack default dev/build.
- **Pages→App:** route-by-route (rendering.md mapping table); shared data
  layer moves first; parallel/intercepting routes last.
- **JS→TS:** per module: tsconfig strict ramp, types at boundaries, no
  `any`-wall conversion; `.tsx` rename per commit.
- **Old patterns:** class components→functions where touched; context
  reshapes per react-core; barrel-file untangling when build perf demands.

## Refactoring (mode C, no version change)

Same protocol minus version steps; measure before/after (performance.md);
delete obsolete code in the same commit (no dual paths kept "for safety" —
git history is the safety).

## Never

Big-bang upgrades across majors with features; codemods without reading
diffs; migrations without tests green at each step; parallel rewrites of
working subsystems.
