# API Design (REST · GraphQL · gRPC · Real-Time)

Load for modes API / CREATE / AUDIT. Project's existing style wins; this is
the quality bar for new or revised surfaces.

## REST

- **Resources:** nouns, plural, stable hierarchy (`/orders/{id}/items`).
  Verbs only for genuine actions (`/reports/{id}/export`). One owner per
  collection.
- **Methods/status:** GET idempotent-safe; POST 201+Location; PUT full /
  PATCH partial (Merge Patch or JSON Patch, pick one per API); DELETE 204 or
  200+body, repeat DELETE = 404 or 204 (documented). Validation 422, not
  found 404, authz 403 vs 401, conflict 409, rate limit 429+Retry-After.
- **Errors: RFC 9457 (`application/problem+json`)** — `type,title,status,
  detail,instance` + extensions. Same shape for every error path; never
  leak stack traces. `scripts/validate-openapi.py` checks spec error
  schemas exist.
- **Collections:** `limit` (bounded default) + `cursor` (preferred) or
  page/offset for small stable sets. Sort via `sort=field:dir` whitelist.
  Filter params documented with operators. Responses carry `total`/`next`
  only when cheap. Broken pagination (offset beyond end) = defined empty,
  not 500.
- **Versioning:** header or path, one scheme per API. Deprecation:
  `Deprecation`/`Sunset` headers + changelog; breaking changes need a
  baseline diff (`validate-openapi.py --baseline`).
- **Writes:** idempotency keys (`Idempotency-Key` header, stored response
  replay window) for POST that create value; optimistic concurrency via
  `If-Match`/ETag.
- **Caching:** `ETag`+`Cache-Control` on GETs; `304` handling; private
  per-user data → `Cache-Control: private, no-store` unless intentional.
- **Uploads:** size caps, content-type allowlist, storage outside web root
  or object storage, streamed not buffered, virus-scan/DLQ where required.
- **Webhooks:** HMAC signature over timestamp+body, replay window, retry
  with backoff, consumer must be idempotent; document the payload contract.

## GraphQL

- Schema: object types mirror domain, not tables; `Node`/cursor connections
  for lists (`first/after`). Mutations return affected types + errors as
  data (`errors` union or payload fields).
- Resolvers: batch via DataLoader per-request; never query in loops (N+1).
  Persisted queries / GET only with CDN in front. Limits: depth, complexity,
  timeout, alias count — enforced at gateway.
- AuthZ at resolver/field level against the same service layer REST uses;
  introspection off in prod if public.
- Subscriptions: document transport (ws), auth re-use, backpressure.

## gRPC / RPC

- `.proto` files versioned with service; fields appended, never renumbered;
  `optional`/wrappers for presence. Deadlines client-set, server respects
  cancellation. Errors → `google.rpc.Status` details, not prose. Streaming:
  document ordering and resume semantics. Generated code committed or
  reproducibly generated in build — pick one, follow project.

## Real-time (WS / SSE)

- Handshake auth = same credential system as REST (no parallel auth stack).
- Heartbeat interval + pong timeout; client exponential-backoff reconnect
  with jitter + resume token/last-event-id. SSE for one-way server→client
  (simpler, proxy-friendly); WS for bidirectional.
- Ordering: per-session sequence number; multi-instance fan-out via the
  project's pub/sub (Redis etc.) — state the delivery guarantee honestly
  (at-least-once + client dedupe, exactly-once is not promised).
- Backpressure: bounded send queues, drop/degrade policy documented.
  Session state external (Redis/DB) so any instance can serve any client.

## Documentation & contracts

- REST → OpenAPI. Use the version your tooling round-trips (probe: parser,
  generator, gateway). Spec = CI-checked artifact:
  `validate-openapi.py` for structure + breaking-change diff against the
  previous release. Contracts tested: request/response against spec via
  schemathesis/dredd/spector where runner exists; else spec-derived snapshot
  tests in the project's runner.
- Generated clients/docs must build in CI; drift between code and spec is a
  release blocker.
