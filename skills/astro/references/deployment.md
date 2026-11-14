# Deployment & Hosting — adapter, headers, gate

Hosting is a decision with evidence, not a default. Static vs on-demand
changes what you deploy.

## Pick the target (deployment decision table)

| Target | Astro setup | Output |
|---|---|---|
| Static hosts (GH Pages, S3, CF Pages static) | `output: 'static'`, no adapter | `dist/` HTML |
| Node self-host / Docker | `@astrojs/node` standalone | `dist/` server bundle |
| Netlify / Vercel / Cloudflare | matching adapter | platform contract |
| Behind nginx on a VPS | node standalone + proxy | same as node |

`astro build` output differs: static = flat `dist/`; adapter = server +
client chunks. Deploy the right tree; verify on the host (SERVED level).

## Production gate (run before every deploy)

```bash
npx astro check && npm run build   # types + build
# preview smoke: serve, fetch key routes, assert 200 + title
npx astro preview & curl -sf localhost:4321 | grep -q '<title'
```

## Host mechanics

- Env: build-time `PUBLIC_*` vs runtime; adapters map platform env; secrets
  never in the bundle (grep `dist/` for keys before ship).
- Compression: Astro compresses output by default (`compressDefault`); hosts
  may re-compress — fine; static hosts keep brotli on.
- Headers baseline in security.md; immutable cache for hashed `_astro/*`,
  short/no-cache for HTML on on-demand routes (route caching.md covers the
  app-side layer).
- Redirects: config `redirect` map (static-safe) or host rules; old URLs keep
  301s.
- Node/Docker: `node ./dist/server/entry.mjs` (adapter docs), healthcheck on
  a route; restart policy owned by orchestrator.

## CI/CD (GitHub Actions reference)

```
npm ci → astro check → build → (tests) → deploy (platform CLI/action)
```
Cache `node_modules` + playwright browsers; deploy only on green build;
`SITE_URL` env matches the canonical URL.

## Rollback & monitoring

- Platform instant rollback (keep last N builds) or redeploy prior artifact;
  DB/CMS-side changes need a written back-out note.
- Post-deploy: hit `/` + 2 key routes + sitemap on production; log status +
  Lighthouse run saved as artifact; compare to pre-deploy baseline.
