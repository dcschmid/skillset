# Audit module engine (§A–§J)

Each module runs ONLY when detection shows the technology/flow exists.
Every check emits: category · file:line · evidence · severity · CWE ·
OWASP id · fix · auto-fixable? · verification. WSTG section cited where a
generic test exists. Confirm via source before claiming (SKILL.md rule 1).

## §A Authentication (OWASP A07; ASVS V2/V6; CWE-287/384/521/613)

| Check | Look for | Confirm by | Fix class |
|---|---|---|---|
| Password handling | plaintext over HTTP, length/complexity none, compare via `==` | read login handler | SAFE: hashing/validation |
| Legacy hash algos | md5/sha1 for passwords; `crypt` DES | grep `md5|sha1` in auth paths; read context | REVIEW: algo+param change = migration |
| Session safeguards | session id in URL, no rotation on login (fixation), no idle/exp absolute timeout | read session middleware config | often SAFE |
| Cookies | session cookie without `Secure/HttpOnly/SameSite` | response header set / framework cookie opts | SAFE |
| Token storage | JWT/session in `localStorage` (XSS-readable) vs HttpOnly cookie | frontend token store + threat model | REVIEW if UX-visible |
| JWT validation | `alg:none`, missing signature verify, no `exp/aud/iss` check, secret from env absent | read verify call: `jwt.verify(token, key, {algorithms…})` | SAFE (add checks) |
| Reset flow | token guessable, not single-use, not bound to user/email enumeration diff | read reset token gen + consume | REVIEW |
| Enumeration/brute force | distinct "user not found" vs "wrong password" messages; no login rate limit | handler diffs + rate-limit middleware | SAFE (uniform msgs) |
| OAuth/OIDC | missing `state`, redirect_uri prefix-match, id_token sig unverified | provider config + callback handler | REVIEW |
| MFA | optional where privileged; TOTP replay window huge | flow inspection | REVIEW |
| Privilege escalation | role from client payload trusted server-side | trace role → query | SAFE: server-side role |

Regression tests to author: valid login passes; expired/invalid token
rejected; re-login rotates session id; reset token single-use.

## §B Authorization (OWASP A01; ASVS V4.1; CWE-639/862/863/915)

| Check | Look for | Confirm by |
|---|---|---|
| IDOR/BOLA | endpoint takes raw `id` from client, query scoped only by that id | read handler + repo/query: is owner/tenant in WHERE? |
| Missing server-side authz | permission check only in frontend/middleware list gaps | enumerate routes, diff auth-guarded vs public |
| Role errors | role escalated from request body/cookie without revalidation | trace role source |
| Admin endpoints | `/admin` public or basic-auth in prod; debug endpoints exposed | route table + env guards |
| Tenant isolation | shared queries lacking `tenant_id` | grep queries lacking tenant filter |
| Mass assignment | `Model.create(req.body)` / spread of input into persist | read model create/update |
| Object/property level | DTO returns hidden fields (role, balance) of other users | read serializer vs model |

Method: build a mini user matrix (anon/user-A/user-B/admin) and trace one
representative endpoint per level. Missing authz = CRITICAL-adjacent;
fix with explicit ownership check server-side. Tests: user-A↛user-B rows;
anon rejected; admin role via payload ignored.

## §C Injection (OWASP A05; WSTG-inp-01..; CWE-89/77/74/502/611/98/22)

| Vector | Smell | Safe fix |
|---|---|---|
| SQL | `f"…{x}…"`, `+`-built SQL, `db.query(` with template | prepared/parameterized; ORM filter args |
| NoSQL | Mongo query object straight from body; `$where` | schema-validate fields, whitelist ops |
| Command | `shell=True`, backticks with input | `execFile`/arg arrays; no shell interpolation |
| Template (SSTI) | render(user string), `eval`-ish template engines | sandboxed render / whitelist |
| LDAP | concatenated filter strings | parameterized filter builder |
| Path traversal | `join(dir, req.params.path)` no normalize+prefix check | resolve → startsWith(base) |
| XML/XXE | parser without disallow-doctype/external-entity limits | hardened parser factory |
| Deserialization | `pickle`/`ObjectInputStream`/`json` typed on untrusted bytes | JSON+schema / class whitelist |
| Dynamic exec | `eval(new Function)`, plugin loading from request | static dispatch / sandbox |

Confirm: is the tainted value actually user/system-controlled and is the
sink reachable? Test: `' OR 1=1--`, `../../etc/passwd`, `; ls` rejected or
escaped, legit input still works.

## §D XSS (OWASP A05; WSTG-CLNT-01..; CWE-79/116)

| Check | Look for | Fix |
|---|---|---|
| Reflected/Stored | server template `{{ x | safe }}`, `dangerouslySetInnerHTML`, `v-html`, `innerHTML=`, `document.write` | context output encoding / whitelist sanitizer |
| DOM-based | `location.hash|search → innerHTML/insertAdjacentHTML`; `postMessage` no origin check | textContent, template escaping, origin allowlist |
| Framework APIs | React `dangerouslySetInnerHTML`, Vue `v-html`, Svelte `{@html}` on untrusted | sanitize at sink |
| Encoding context | HTML body vs attr vs script vs URL vs CSS — one encoder for all | per-context encoder |
| Sanitizer quality | allowlist (tags/attrs) vs strip-only; re-scan after sanitize | allowlist + attribute escaping |
| Third-party scripts | CDN JS without SRI; `*` CORS on credentialed endpoint | SRI, pinned origin |
| CSP | present? nonce/hash mode? `unsafe-inline` flood? report-only first | tighten + keep output encoding |

CSP = defense-in-depth only; it NEVER replaces output encoding. Test:
`<img src=x onerror=…>` stored+reflected renders inert; legit rich content
survives.

## §E Browser / CSRF / headers (WSTG-CLNT/SESS; CWE-352/1021/942)

Decide CSRF need from architecture first: cookie-session browser app → CSRF
required; stateless token header APIs → CSRF mostly N/A. Never add tokens
that break a working API client.

| Check | Right answer |
|---|---|
| CSRF token | double-submit/synchronizer on state-changing cookie-authed POST/PUT/DELETE |
| Cookies | `Secure`, `HttpOnly`, `SameSite=Lax/Strict` on session cookies |
| CORS | explicit origin list + `Allow-Credentials` parity; no `*` with creds; preflight cached |
| Clickjacking | `X-Frame-Options: SAMEORIGIN` or CSP `frame-ancestors` |
| CSP | present, non-`unsafe-inline` for scripts, report-only rollout noted |
| HSTS | `max-age≥31536000; includeSubDomains` on HTTPS hosts |
| Referrer-Policy | `strict-origin-when-cross-origin` |
| Permissions-Policy | reduced feature surface |
| COOP/COEP/COEP | only if isolation needed (don't break embeds) |
| Cache | `no-store` on authed responses with sensitive data |

Fix class: header config = SAFE if framework-supported, REVIEW when proxy/
CDN owned. Verify via response headers in tests/re-scan.

## §F API security (API Top 10 2023; ASVS V5)

| Check | Smell / gap | Fix |
|---|---|---|
| Unauth endpoints | route table walk: handler without guard | guard + integration test per level |
| BOLA in APIs | `/:id` without owner scope (see §B) | owner-scoped query |
| Input validation | missing schema (zod/pydantic/joi) at boundary | schema at edge, reject unknown |
| Over-exposure | whole ORM object serialized; `SELECT *` in DTO | DTO projection |
| Rate limits | no limiter on auth/search/LLM-cost endpoints | middleware with sensible bucket |
| Pagination/resource caps | unbounded `?limit=` and list sizes | cap + default page size |
| GraphQL | introspection public, no query depth/cost limit, batch depth unbounded | depth/complexity limits, hide introspection in prod |
| WebSocket | no auth on connect, no origin check | handshake auth + origin allowlist |
| Webhooks | signature verify absent, no timestamp/replay window, no idempotency key | HMAC verify + ts + dedupe |
| Uploads | no size/type cap, name→path join unvalidated | validate, rename, store outside webroot |
| SSRF | fetch(user URL) without allowlist/redirect-disable | URL allowlist, no internal ranges, no redirect follow |
| Error leaks | stack/SQL in 500 bodies; debug endpoints prod | generic error body + logged detail |

Regression tests: anon→401/403; foreign id→404/403; oversized payload→413;
signed webhook passes/unsigned rejected; legit path unchanged.

## §G Secrets management (CWE-798/312/540)

Scanner: `scripts/run-security-audit.sh secrets <dir>` (regex heuristics +
gitleaks if present). Checks: keys/passwords/tokens/private keys in code,
config, tests, fixtures, `.env*` shipped, git history, logs printing creds.

Secret lifecycle (never break these):
1. locate finding → 2. MASK value in all output (`AKIA…****masked`) →
3. assess publication (git log / pushed?) → 4. remove from code →
5. move to env/vault + provide `.env.example` with placeholders →
6. recommend rotation (NEVER rotate live creds yourself) →
7. judge history residue (rewrite only with approval) → 8. re-scan clean.
Committed-but-pushed secret ⇒ rotation REQUIRED even after code fix.

## §H Cryptography (OWASP A04; ASVS V6; CWE-326/327/324/312/330)

Check: legacy hashes/ciphers (md5/sha1 for integrity, DES/RC4, ECB),
`Math.random`/`rand()` for tokens/keys, hardcoded keys/IVs, TLS (min 1.2,
cert verify off, pinned stale), password params (bcrypt cost, PBKDF2 iters,
argon2), nonce/IV reuse in GCM/CBC, key storage/rotation. Prefer stdlib
platform crypto; inventing schemes forbidden. Algo swaps = REVIEW (migration).

## §I Configuration hardening (OWASP A02; CWE-1188/16)

DEBUG/`APP_ENV` off in prod, verbose errors/page traces off, `/debug`/
`/_profiler`/admin-ui public, default creds/ports, file perms (world-writable
config), Docker: `latest` tags, root user, no `--read-only`, secrets baked in
image, published ports excess, Compose env leakage, K8s missing
`securityContext`, Terraform public buckets, reverse proxy passthrough
headers trusted. Details: `infrastructure-hardening.md`.

## §J Error handling & logging (OWASP A09/A10; CWE-703/778/1009)

Stack traces to clients? secrets in structured logs? security events
(login fail, authz deny) logged + alertable? fail-open (`try/catch` around
authz that swallows and proceeds)? partial transaction on error (no
rollback/atomicity)? audit trail on admin mutations? Fix: generic client
errors + server-side logging; authz catch re-raises deny. Tests: forced
error → no internals leaked; denied action appears in log stream.
