# Authentication & Authorization deep checks (modules §A–§B, ASVS V2/V4.1)

`audit-modules.md` §A/§B is the checklist; this file is the judgment layer
for the tricky calls. Framework skills own idioms; this skill owns the
verification bar.

## Decision table: what counts as a real auth system here

| Detected | Audit depth |
|---|---|
| Login form + server sessions | full §A (rotation, fixation, timeouts, cookie flags) |
| JWT bearer flow | signature+exp+aud+iss verified server-side; alg pinned; clock skew sane; refresh rotation |
| OAuth/OIDC (passport/authlib/auth.js/OIDC libs) | state nonce, redirect exact-match, id_token verified, userinfo trust boundary |
| API keys/header tokens | storage hash, rotation story, per-key scope |
| No auth surface (static site) | §A/§B = Not Applicable — record it, audit client-side surface only |

## The confirmations people skip (do them)

1. Session fixation: id generated fresh AFTER credential success, not before.
2. Idle + absolute timeouts both exist and are enforced server-side.
3. Logout invalidates server-side state (token header client caches irrelevant).
4. Password compare constant-time where the language exposes raw compare.
5. Reset tokens: ≥128-bit entropy, single-use, expiry, bound to account.
6. Enumeration: identical response shape/timing budget for user exists/denied.
7. Privilege source: roles come from server store per request, never from
   client-sent claims/body/cookie alone (JWT payload user-editable unless signed AND verified).
8. Tenant boundary predicate inside the query, not in app code after fetch.
9. Mass-assignment: persist receives DTO/whitelist, not raw request body.
10. Property level: DTO/serializer hides internal fields of others.

## Auth regression test bar (fix verification)

- happy path: real login/authorized call still succeeds (function preserved)
- anon 401, wrong-user 403/404, expired/invalid token rejected, role via
  payload ignored
- run project's suite: no functional regressions (Minimal Disruption)

## Migration-shaped fixes = REVIEW REQUIRED

Algo changes (md5→argon2), session store swaps, token lifetime edits,
cookie scope flips (Strict), provider config. Ship diff + rollout note +
rollback command; wait.

## MFA/OAuth/OIDC extras

MFA: enforced on privileged paths, replay-window sane, backup codes hashed,
enrollment doesn't bypass re-auth. OAuth: PKCE for public clients, `state`
required, `nonce` for OIDC, issuer/audience checked, JWKS cache refreshed.
