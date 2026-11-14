# Version Gate — Astro

## Central version config

```
BASELINE          = astro 7.4.12 (stable, npm dist-tag "latest")
BASELINE_PROBE    = 2026-11-14 via `npm view astro version`
ASTRO_7_0         = 2026-06-22 (Rust compiler, Sätteri, Vite 8 + Rolldown)
DOCS              = https://docs.astro.build/ (versioned per release)
RELEASES          = https://github.com/withastro/astro/releases
UPGRADE_GUIDES    = https://docs.astro.build/en/upgrade-astro/
```

Baselines rot. Re-probe at task start; never trust a stored number over
`npm view astro version` (stable) and the release notes.

## Detecting the project version

```bash
node -p "require('./node_modules/astro/package.json').version"  # installed
grep '"astro"' package.json                                      # declared
npm view astro version            # latest stable (channel: latest only)
```

`astro` has no `--version`-style CLI guarantee; read package.json.

## Feature floors (verify before use on older projects)

| Feature | Floor | Notes |
|---|---|---|
| Content Layer (`src/content.config.ts`, loaders) | 5.0 | `src/content/config.ts` = legacy on 5+ |
| `output: 'static'` default + per-route `prerender` | 5.0 | `output: 'hybrid'` removed |
| Sessions (`Astro.session`, `sessionDrivers`) | 5.7 | driver required off node/cf/netlify |
| Actions (`astro:actions`, `defineAction`) | 4.15 | form actions + `Astro.callAction` |
| Server islands (`server:defer`) | 4.16 | adapter required; props serializable |
| `server:print` | 5.3 | |
| Advanced Routing (`src/fetch.ts`, AstroRoute data) | 7.0 | replaces most middleware needs |
| Route caching (`Astro.cache`, `routeRules`) | 7.0 | providers; Netlify/Vercel/CF CDN providers experimental |
| Fonts API (`fonts` config) | 7.0 | system/local/remote providers |
| ` paginate()` `format` option | 7.1 | |
| `session: false` opt-out | 7.2 | |
| Rust compiler / Sätteri MD / Vite 8 Rolldown | 7.0 | mostly compat; see upgrades.md |

Rule: feature used ⇒ floor met ⇒ if project's installed version < floor,
either upgrade (minor within same major, project decision) or implement the
pre-floor idiom and record the reason.

## Channel discipline

- Stable only. No `@next`, `@dev`, `@alpha`, `@beta`, nightly as a default.
- `astro@latest` == `npm view astro dist-tags.latest` (ignore the many stale
  `next--*` dist-tags on the astro package; they are branch previews).
- New features require: project version ≥ floor AND user decision on upgrade
  if an upgrade is needed. Experimental flags (`experimental.*`) ship only
  with a written risk note (build output may change between minors).

## Update routine (refresh this skill's baseline)

```bash
npm view astro version && npm view @astrojs/node version \
  && npm view @astrojs/netlify version && npm view @astrojs/vercel version \
  && npm view @astrojs/cloudflare version && npm view @astrojs/check version
```
Then diff docs for the new version's "upgrade to vX" guide, update
`BASELINE`, feature floors, and run `tests/test_skill.py`. Adapters ship with
Astro-compatible majors — an Astro major usually means adapter majors too.
