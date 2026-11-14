# Security — web app binding rules (OWASP-aligned)

Threat surface = anything a client controls: URLs, forms, actions payloads,
headers, cookies, uploads, webhooks, localStorage.

## Perimeter rules

- **Every Server Function and Route Handler is public API**: validate input
  (schema, `unknown` first), authn+authz inside the handler, ownership-filter
  every client-supplied id (IDOR), return minimal DTO (security.md of
  actions = server-actions.md §mandatory).
- **Output encoding**: React escapes by default; `dangerouslySetInnerHTML`
  only with a sanitizer (DOMPurify or equivalent) on trusted-enough content;
  user content in `href`/`style`/attributes stays attribute-safe.
- **SSRF**: fetches of user-supplied URLs → allowlist hosts/protocols
  server-side; internal network ranges blocked.
- **SQL/DB injection**: ORM parameterization everywhere; raw SQL only with
  placeholders; `ORDER BY`/identifiers from a fixed map.
- **XSS via data-in-HTML**: metadata, OG builders, email templates re-escape.
- **CSRF**: framework forms/actions carry origin protection; Route Handlers
  mutating via GET forbidden; token or SameSite=Lax/Strict cookies.

## Session & auth

Cookies: `httpOnly`+`secure`+`sameSite`; session rotation on privilege
change; logout kills server session. JWTs short-lived, server session for
web UI. RBAC checks server-side per request; client route guards = decoration.

## Secrets & bundles

Env naming: `NEXT_PUBLIC_*`/`VITE_*` = public by design — server-only secrets
stay unprefixed. Check: any secret that reaches the browser bundle is public
afterwards (source maps too). `.env` files never committed.

## Headers & transport (ship defaults)

CSP (nonce-based, no `unsafe-inline` for scripts unless tooling forces a
documented exception), HSTS, `X-Content-Type-Options`, Referrer-Policy,
frame-ancestors per embedding needs. Via hosting headers or `headers()`/
`next.config` (read local docs).

## Caching & isolation

Per-user cache keys include user/tenant scope; no personal data in
shared/static cache (data-caching.md). Static generation of personalized
pages = leak risk — verify.

## Rate limiting & abuse

Edge/handler-level limits on auth, search, upload, webhook-replay windows;
idempotency keys for money mutations.

## Dependencies & supply chain

`npm audit` / lockfile pinning; updates via changelog-reviewed steps
(migrations.md); no unpinned installs in CI lockfile churn.

## Verification loop

Perimeter endpoints have authz + invalid-input tests (testing.md); report
notes security-relevant assumptions checked (auth provider behavior, hosting
header support) — unverified stays UNVERIFIED.
