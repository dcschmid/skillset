# Remediation guidelines (Autofix engine rules + per-module recipes)

Classify every fix BEFORE editing (SKILL.md Step 5):
**SAFE AUTO-FIX** local, reversible, no compat risk → do it now.
**REVIEW REQUIRED** auth flows, API contracts, token lifetimes, complex
infra → concrete diff + stop for approval.
**HIGH-RISK** prod secrets, DBs, network, deploy env, wide security
policies → plan first, approval first.

## Inviolable fix rules

1. `git status --porcelain` first; foreign/uncommitted edits in touched
   files stay intact (read current content, edit smallest region).
2. Smallest diff that removes the flaw — no drive-by refactors, no
   reformatting sweeps, no renames bundled into security fixes.
3. No API-breaking changes, no data-losing migrations, no weakened crypto,
   no disabled checks, no blanket ignore rules, no substitute hardcoded
   secrets, no major dependency jumps.
4. Every fix ships with: what changed, why, how verified (test/re-scan),
   residual risk. Fix status ladder: FIXED → PARTIALLY FIXED (no re-scan
   yet) → REQUIRES REVIEW → NOT FIXED → FALSE POSITIVE.

## Recipe: SQL injection → parameterized

```python
# before  cur.execute(f"SELECT * FROM items WHERE owner = '{user_id}'")
# after   cur.execute("SELECT * FROM items WHERE owner = %s", (user_id,))
```
Same shape everywhere: `?`/`$1` placeholders, ORM filter args, driver
param APIs. Never string-concat identifiers/values; for dynamic identifiers
whitelist-map. Verify: quote-bearing legit input still round-trips;
`' OR 1=1--` returns scoped/empty set.

## Recipe: XSS → context output handling

HTML text nodes: framework default escaping (keep it). Raw HTML sinks
(`dangerouslySetInnerHTML`, `v-html`, `{@html}`, `innerHTML`) → allowlist
sanitizer (DOMPurify-style tags/attrs) or rewrite to escaped nodes.
Encoding context per slot (attr vs script vs URL); CSP added as layer,
encoder stays. Verify: payload renders inert, legit markup survives.

## Recipe: missing authz → explicit server-side check

Add ownership/role predicate where the handler resolves the resource:
`get_by_id(id)` → `get_by_id_and_owner(id, principal.id)`; admin routes get
the guard middleware/decorator already used by siblings (project pattern,
not new invention). Tests: user A vs B vs anon matrix on the fixed route.

## Recipe: secrets → configuration boundary

Real value out of code; `process.env.X` / `os.environ["X"]` / settings
module in; placeholder in `.env.example`; shipped `.env*` added to
`.gitignore` (only if not already tracked-and-required). Masked everywhere.
Rotation = recommendation to owner. If committed+pushed: history note in
report; rewrite only on approval.

## Recipe: cookies/headers → framework config

Session cookies: `Secure+HttpOnly+SameSite=Lax` (+`Strict` when UX allows)
via framework cookie options, not manual header string surgery. Security
headers at the existing middleware/proxy layer; HSTS only behind TLS; CSP
report-only first where inline scripts exist (name the follow-up).

## Recipe: dependencies → patched compatible version

Read advisory range → smallest upgrade within current major. Lockfile
updated via the project's package manager (never hand-edit beyond the
manager, never delete). Conflict? Investigate, don't downgrade the scanner.
No safe version? Document risk + mitigation (code-level gate, feature flag
off, upgrade plan) — `PARTIALLY FIXED` at best until deps land.

## Recipe: API hardening

Schema-validate at edge (existing validator lib), DTO project fields,
pagination caps + default limit, rate-limit middleware on costly routes,
webhook HMAC+timestamp verify, SSRF allowlist+no-redirect fetch. Each is
additive; contract additions (error shape) go through REVIEW.

## Recipe: error/info leaks

Catch at boundary → log detail server-side, return generic body +
correlation id. Keep status codes. No stack/SQL/paths in response.

## When NOT to fix

Tool result unverified · fix needs runtime/prod access · migration needed ·
behavior change beyond flaw removal · coverage gap would be papered over.
Output the diff proposal + exact verification command instead.
