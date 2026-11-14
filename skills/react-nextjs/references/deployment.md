# Deployment & Production Readiness — platform-neutral

Next.js is platform-neutral (Vercel is one option among several).
Feature-support audit on the target BEFORE the feature list is frozen.

## Target selection

| Target | Notes |
|---|---|
| Node server (`next start`/custom server) | full feature set incl. image opt, ISR/cache APIs, proxy; needs Node runtime, fs for cache |
| Docker / self-host | same as node; `output: 'standalone'` small image; runtime env injection at start |
| Static (`output: 'export'`) | no Server Functions/proxy/dynamic APIs — verify feature matrix (read local docs) before committing; SPA+CDN |
| Vercel | platform defaults, env, image CDN |
| Cloudflare / Netlify / other clouds | runtime support matrix per platform docs (node vs edge runtimes, caching layer support) |

## Pre-deploy matrix (binding)

1. `npm run build` passes on the target's Node version.
2. Every used Next feature supported on target (static export vs
   `use cache`/image/proxy/server runtime).
3. Env: all `NEXT_PUBLIC_*` set at BUILD, server env at RUNTIME; validation
   module fails fast (architecture.md).
4. Caching: cache backend/paths available (fs cache on ephemeral containers ⇒
   mount or accept cold); CDN rules don't fight framework headers.
5. Logging/monitoring: request logs + error tracking (Sentry-class) with
   server-source-maps decision; health endpoint route.
6. Rollback: previous build/artifact kept; migrations reversible
   (migrations.md); cache revalidate strategy post-deploy.
7. Asset caching: immutable hashed assets; HTML revalidate policy per caching
   posture (data-caching.md).

## Operations

Backup: DB migrations versioned; cache = rebuildable, not backed up. Scaling:
stateless server instances + shared cache/session store; realtime connections
counted. Docs: runbook = build/start/env/health/rollback commands.

## Reporting

Report names target, matrix result, and UNVERIFIED platform specifics rather
than assuming cloud parity.
