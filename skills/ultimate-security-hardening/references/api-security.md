# API security audit (REST · GraphQL · WebSocket · webhooks)

Module §F is the checklist; this is the walk procedure. Applies to HTTP
APIs, BFF routes, server actions, tRPC/trpc-like layers, mobile backends,
game backends.

## Walk procedure

1. Enumerate routes: routers/controllers/openapi/graphql schema/route
   folders (`pages/api`, `app/**/route.*`, Fastify/Nest/Express routers,
   FastAPI/DRF views, net/http handlers, axum/actix, controllers).
2. Per route: guard present? input schema? output shape bounded? owner/tenant
   predicate? limits? error body generic?
3. Sample one endpoint per auth level and trace full path (anon/user/other-user/admin).
4. Cross-cutting: global middleware coverage — auth, validation, rate limit,
   payload size, CORS, compression (zip-bomb), pagination caps.

## Per-protocol notes

**REST/RPC**: method-level authz (GET ≠ free), header vs body id consistency,
PATCH mass-assignment, batch endpoints (bulk ids → per-item authz), file
upload path/size/type, idempotency keys on money paths.
**GraphQL**: introspection prod policy, depth+complexity+batch caps, field
authz (resolver-level), DataLoader batching can't skip owner filter, persisted-query/alias-abuse limits.
**WebSocket**: auth at handshake (subprotocol/header/first-frame), origin
allowlist, message size/queue caps, per-connection authz refresh on long lives.
**Webhooks (in)**: HMAC + timestamp window + replay dedupe; **Webhooks (out)**:
signed, retries idempotent, destination allowlist (SSRF via stored URLs).

## Evidence patterns (confirm, don't assume)

Guard list vs route list diffed · validation import exists AND applied per
handler (global middleware ≠ auto-registered) · serialization shape read from
code · limit default enforced even when client omits params.

## Fix bar

Every fix keeps contract additive: new caps/limits within existing envelope,
error shapes preserved. Breaking shape change ⇒ REVIEW REQUIRED. Regression:
authz matrix + limit behavior + happy paths against the running project
tests; if none exist, minimal harness via project runner.
