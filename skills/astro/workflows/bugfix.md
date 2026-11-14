# Workflow: Bugfix (Astro site/build/render)

Symptom → cause → minimal fix → proof.

1. **Reproduce deterministically**: exact command (`dev`/`build`/`preview`),
   route, env (Node version, adapter, data). No repro → gather: error text,
   `astro build --verbose`, dist inspection, browser console.
2. **Classify** (routes diagnosis): build-time (config, collections,
   getStaticPaths, loaders) vs render (prerender flag, adapter presence,
   sessions on static) vs hydration (client:*, serialization of props) vs
   runtime/data (actions, endpoints, env) vs host (headers, cache, paths).
   Feature floor check if API is version-gated (versions.md).
3. **Find the cause in code**, not folklore: read the failing file + its data
   source + the relevant reference (rendering-routing / islands / content).
   7.x specials: markup now strict (Rust compiler), whitespace JSX-collapse,
   Sätteri markdown, Rolldown plugin compat (upgrades.md).
4. **Fix minimally** — no refactor tax. Regression test if the repo has the
   lane (testing.md) and the bug is user-visible: it must fail pre-fix.
5. **Verify**: repro command passes; `astro check` + `astro build`; preview
   the affected route + one neighbor.
6. **Report**: symptom, cause, fix, proof levels, related risk.
