# Security — Astro 7 defaults, explicit controls

No untested workarounds; each control states where it lives.

## Request surface (Astro 7)

- **Trusted origins**: Astro validates the `Origin` header on Actions/fetch
  requests against the known site origin; behind proxies/CDNs verify the
  host-forwarding config against the adapter docs for the target version —
  set explicit host lists, never wildcards.
- **Proxy headers**: trust only your proxy's `X-Forwarded-*` per adapter docs;
  validate `Host` at the edge (nginx/CF/adapter) — Astro echoes nothing
  blindly.
- Dev server stays local; production serves build output only.

## Input & actions

- ALL external input crosses a Zod schema (`defineAction.input`, endpoint
  params); unknown keys stripped (`z.object` strips by default).
- Server-side authorization inside actions/handlers/middleware — client state
  is UI sugar; every mutation re-checks session (`ctx.session`) on server.
- `ActionError` messages user-safe; stack traces never in responses.

## Sessions & cookies (5.7+)

- Server-side session storage (driver); client holds only an opaque, httpOnly,
  `sameSite: 'lax'` (default) cookie; regenerate on login
  (`session.regenerate()`), destroy on logout; `session: false` if unused —
  smaller bundle.
- CSRF: same-site cookies + Origin checks cover form posts; state-changing
  GETs forbidden; for JSON APIs from islands, same-origin + `accept: 'json'`
  actions validated.

## XSS & CSP

- Astro auto-escapes templates; raw HTML only through `set:html` on
  server-generated strings (MDX/shiki output), never on user input; `is:inline`
  scripts never interpolate user data.
- CSP: middleware/adapter sets header; Astro inline styles/scripts need
  nonces/hashes — Astro emits `astro:inline` handling; if shipping strict CSP,
  start report-only (`Content-Security-Policy-Report-Only`), fix reported
  violations, then enforce. Framework hydration may need
  `'unsafe-eval'`-free builds — verify per integration.
- Headers baseline (deployment/host): `X-Content-Type-Options: nosniff`,
  `Referrer-Policy`, `X-Frame-Options: DENY`/`frame-ancestors`, HSTS on TLS,
  `Permissions-Policy` minimal.

## Secrets & deps

- `PUBLIC_` prefix = shipped to client, everything else server-only; `.env`
  gitignored, `.env.example` committed; adapters inject env at deploy.
- Lockfile committed; `npm audit`/`pnpm audit` clean or noted; integrations
  pinned (versions.md).

## Verification

- MEASURED: request with forged `Origin` rejected (actions 4xx); unauth call
  to each action returns 401/403-equivalent; cookie flags via `curl -I`; CSP
  report clean; `astro build` env bleed check: grep `dist/` for secret names.
