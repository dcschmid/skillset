# Example 3 — verify an OAuth/OIDC integration

Task: "review our login against OIDC." Mode AUTH (authentication.md).
Read the flow: discovery doc fetch, `state`+`nonce` checks, token exchange,
user-info, session mint.

Checks: state compared (session-fixation + CSRF) · PKCE on public client ·
redirect URIs exact-match allowlist · `id_token` validation (iss/aud/exp,
JWKS kid rotation handled) · tokens encrypted at rest, absent from logs ·
refresh rotation + revocation store · logout invalidates server session.
Result example: PKCE missing on mobile client (HIGH, fix in place, test
added asserting `code_verifier` sent); no user enumeration on /login.
Vuln hunting beyond flow correctness → ultimate-security-hardening.
