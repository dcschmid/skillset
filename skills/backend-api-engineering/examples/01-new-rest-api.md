# Example 1 — new REST API (notes, SQLite, Fastify)

Task: "Create a secure notes REST API." Mode CREATE.

Profile → `new`, no stack yet → pick Fastify+SQLite (single-host, team JS,
zero external DB ops). Slice order: schema → validation → error shape →
routes → tests → OpenAPI.

1. `db.ts`: `CREATE TABLE notes (id text pk, user_id text not null refs
   users, body text not null check(length<10000), created_at int)`,
   `CREATE INDEX idx_notes_user ON notes(user_id, created_at desc)` —
   tenant column from day one (database-engineering.md).
2. Routes: `GET /notes?limit&cursor` (limit≤200 schema-check), `POST` with
   `Idempotency-Key`, `PATCH` ETag `If-Match`. Errors via one
   `setErrorHandler` → RFC 9457; 404 vs 403: get → scope check.
3. Auth: session cookie (HttpOnly/SameSite=Lax) — single app, no JWT need.
4. Tests (vitest, in-memory DB): happy+422+404+403(cross-user)+pagination
   bounds. `validate-openapi.py openapi.yaml` in CI pre-merge.
Verify: `npm test` green, boot + `/healthz` 200. Report: files, commands,
NOT-TESTED: none.
