# Workflow: Existing Astro Project (any change)

Applies: change inside a live Astro repo. Extend what exists.

1. **Read before write**: `package.json` (+lockfile, package manager),
   `astro.config.*`, `tsconfig`, `src/` tree, existing components/tokens/
   conventions, CI. `node scripts/audit_astro_project.mjs .` for the census.
2. **Version gate**: installed Astro + adapter/integration versions
   (versions.md). Feature floor check before using 5.x/7.x-only APIs.
3. **Match conventions**: naming, folder tier, token names, import style,
   existing layout/props patterns, test layout, lint/format config. Existing
   beats skill preference — always.
4. **Change plan**: files touched, routes affected, rendering implications
   (new route = static or not?), dependency additions (none by default).
5. **Implement**: smallest coherent diff; reuse components/lib; no parallel
   systems; no drive-by refactors.
6. **Verify**: lanes that exist in the repo (testing.md) — minimum
   `astro check` + `astro build`; run repo tests; preview smoke the touched
   routes.
7. **Report**: what changed, levels run + results, risk left. A green check
   you did not run is never claimed.
