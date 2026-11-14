# Authentication

Load for modes AUTH / CREATE / AUDIT. Deep vulnerability hunting and full
hardening passes belong to `ultimate-security-hardening`; this file is the
implementation bar.

## Choosing the mechanism

| Situation | Default |
|---|---|
| Classic server-rendered / same-origin SPA | Server-side sessions in store (cookie: HttpOnly, Secure, SameSite=Lax/Strict) |
| Multi-service / mobile / third-party API | OAuth 2.0 Authorization Code + PKCE; access tokens short-lived |
| Stateless edge/CDN validation truly needed | JWT RS256/ES256, short TTL, JWKS rotation — justify, don't default |
| Machine-to-machine | mTLS or client credentials + scoped API keys, hashed at rest |
| Passwordless web | WebAuthn/passkeys via a maintained lib |

Sessions are a legitimate, simpler answer for one-app-one-database.
Never bolt JWTs on because they are trendy; justify with a requirement.

## Implementation bar

- **Passwords:** Argon2id (or bcrypt/scrypt when lib-bound); per-user salt;
  verify against library defaults, no parameter hand-tuning without a
  measured reason.
- **Flows:** registration → email verification token (single-use, hashed,
  short TTL); password reset → single-use hashed token, no user enumeration
  (identical response whether or not the account exists).
- **Sessions:** regenerate id on login (fixation); server-side store with
  idle+absolute expiry; logout + password change + refresh rotation all
  invalidate; concurrent-session policy stated.
- **Tokens:** access TTL minutes, refresh rotation with reuse-detection;
  revocation list or store; JWT validation pins `alg` allowlist, verifies
  `exp/iat/nbf/aud/iss`, rejects `none` and HMAC/RSA confusion.
- **Cookies:** `HttpOnly; Secure; SameSite=Lax` (+ CSRF token or
  double-submit for POST-capable cookie auth); `__Host-` prefix where
  deployment allows.
- **MFA:** TOTP via lib; recovery codes single-use; MFA state required for
  sensitive ops (email change, password change, key rotation).
- **OAuth/OIDC:** validate `state`, `nonce`; redirect URIs exact-match
  allowlist; store tokens encrypted at rest; `kid`-based key rotation.
- **Rate limiting** on login/reset/MFA endpoints per account+IP; lockout
  with backoff, not permanent.
- **API keys:** high-entropy, stored hashed, scoped, expiring, revocable;
  prefix for tooling detection.

## Verification checklist (run as tests)

login/logout round-trip · expired+tampered token rejected · refresh reuse
detected · session fixation (id changes on login) · logout invalidates ·
password change invalidates old sessions · CSRF enforced on cookie auth ·
brute-force limited · no user enumeration · token absent from logs.
