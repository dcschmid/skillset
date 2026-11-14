# Version Policy — React / Next.js / TypeScript

Central version config. Baselines rot; re-probe at task start.

## Central version config

```
REACT             = 19.3.1        (npm dist-tag "latest", probe 2026-11-14)
NEXT              = 16.4.6        (npm dist-tag "latest", probe 2026-11-14)
TYPESCRIPT        = 7.0.2         (probe 2026-11-14; native-compiler line)
REACT_COMPILER    = babel-plugin-react-compiler 1.0.0 (stable)
NODE_LTS          = 22.x ("Jod"), probe `node -v`
DOCS_LOCAL        = node_modules/next/dist/docs/   (ships inside the installed next; version-matched)
DOCS_REACT        = https://react.dev/reference/react  · versions: https://react.dev/versions
DOCS_NEXT         = https://nextjs.org/docs/app      · guides: /docs/app/guides
RELEASES          = https://github.com/facebook/react/releases · https://github.com/vercel/next.js/releases
MIGRATION         = https://nextjs.org/docs/app/guides/migration-guides
```

## Probing (run at task start, per project)

```bash
# installed (truth for THIS project)
node -p "require('./node_modules/react/package.json').version"
node -p "require('./node_modules/next/package.json').version"
node -p "require('./node_modules/typescript/package.json').version"
grep -E '"(react|next|typescript)"' package.json
# latest stable (truth for NEW projects)
npm view react version && npm view next version && npm view typescript version
# what did we actually get — record in the report
```

`scripts/check-versions.sh` runs this census and prints feature-floor
verdicts. Dist-tag discipline: `latest` only. React publishes `canary`,
`experimental`, `backport`, `rc` tags — installing those without an explicit
order is forbidden. Next has `latest` + `canary`; same rule.

## Documentation priority (binding)

1. **`node_modules/next/dist/docs/`** — version-matched Next docs shipped with
   the installed release (~475 md files, mirrors nextjs.org/docs structure).
   MUST be consulted before implementing relevant Next features when present:
   `ls node_modules/next/dist/docs/01-app` to orient. Highest authority for
   the installed version.
2. Official docs: nextjs.org/docs (App Router), react.dev — current-channel.
3. Official release notes + migration guides (breaking changes).
4. Official repos (facebook/react, vercel/next.js) issues/PRs.
5. Community — only to fill gaps, then mark as such.

For React: `node_modules/react/docs` does not ship; react.dev + the installed
version's changelog is the ceiling. Never invent an API: not-in-docs =
UNVERIFIED = verify before use.

## Feature floors (verify before use on older projects)

| Feature | Floor | Notes |
|---|---|---|
| `use`, `useActionState`, `useOptimistic`, `useFormStatus`, Form Actions | React 19.0 | `useActionState` replaced `useFormState` (beta name, never stable) |
| `useEffectEvent` | React 19.0 (compiler-era hook) | verify against installed version |
| `<Activity>`, `<ViewTransition>`, Fragment refs, `addTransitionType` | React 19.2+ | check `react` version before use |
| React Compiler stable (`babel-plugin-react-compiler` 1.0) | tool-level gate | Next 16 has built-in support; Vite via plugin |
| App Router default, `next build` Turbopack default | Next 16.0 | 15: opt-in |
| `proxy.ts` (replaces `middleware.ts`) | Next 16.0 | middleware.ts deprecated, still works |
| Cache Components (`cacheComponents`, `use cache`, lifetimes) | Next 16.0 | opt-in flag; pair with `partialPrefetching` |
| `updateTag`, `refresh()` (`use cache`-world invalidation) | Next 16.0 | alongside `revalidateTag`/`revalidatePath` |
| Instant navigations / partial prefetching | Next 16.x | read local docs for exact flags |
| `next dev` webpack fallback `--webpack` | Next 16.0 | 15: `--turbopack` opt-in |
| `experimental.ppr` → stable `cacheComponents` | 15 experimental → 16 | do not port 15 experimental config to 16 |
| `next/image` local images | 13.0 | |
| parallel/intercepting routes | 13.4 | |

Rule: feature used ⇒ floor met ⇒ if installed < floor: implement the
pre-floor idiom (record the reason) or upgrade decision (minor within major =
project decision; major = ordered migration per `references/migrations.md`).

## New projects

1. Probe latest stable of each core dep (above commands).
2. Cross-check compatibility: Next release notes state its React floor
   (16.x ⇒ React 19.2+; 19.3 works). TypeScript: respect Next's bundled
   types; TS 7 line is the current stable.
3. Security patches: prefer latest patch of latest minor; `npm audit`/
   `pnpm audit` after install.
4. Document chosen versions in the handoff report.

## Existing projects

- Read `package.json` + lockfile + installed `node_modules` first; installed
  wins over declared on drift.
- No automatic major upgrades. No `npm update` sweeps. Respect lockfile.
- Respect existing conventions (Pages Router stays Pages Router unless
  migration is ordered; middleware.ts stays in 15 apps).
- APIs above the installed version's floor are forbidden, not "probably fine".

## Update routine for this skill

Re-probe the config block quarterly or on any Next/React major release;
update floors from official migration guides only; re-run `tests/test_skill.py`.
