# Full-Stack & Backend Integration — project-type aware

## First classify the project

- **Frontend-only:** talks to an external backend/API. No DB layer here.
  Typed API client + auth token handling + env config.
- **Backend-for-frontend:** Next Route Handlers or own handlers own the
  aggregation/auth/session edge; DB access optional and thin.
- **Full-stack:** app + DB + jobs in one repo (Next + Prisma/Drizzle/driver).

## Data layer (any of; one, chosen with a reason)

Prisma / Drizzle / raw driver / external API. Selection: team skill,
migration story, query control, deploy target (serverless drivers).
Access pattern: feature → repository/service fn (typed) → layer. Components
never import the ORM. Migrations run in deploy pipeline, not `next dev`.

## Server boundary map (Next 16)

| Need | Surface |
|---|---|
| UI-driven mutation | Server Function (server-actions.md) |
| HTTP contract / external caller | `app/**/route.ts` Route Handler |
| webhook ingest | Route Handler + signature verify (security.md) |
| realtime push | WebSocket/SSE endpoint or external provider (Convex/Ably/etc. opt-in) |
| background job | external worker/queue — not in-render, not in-action |
| file upload | direct-to-storage signed URL preferred; handler-streamed for small |

## AuthN/AuthZ

Provider-neutral: session cookie or tokens; middleware/proxy does coarse
routing, actions/handlers do authoritative checks (never proxy-only auth).
RBAC evaluated server-side per request; roles from trusted source, not
client payload. `useSession`-style client views are display-only.

## Realtime & streaming

SSE for one-way server push (cheap, proxy-friendly); WS for duplex
(keepalive/ping, reconnect w/ backoff, serverless caveats — read hosting
docs). Invalidate caches on server-push updates where the client also reads
cached queries (data-caching.md).

## Uploads & files

Validate type/size server-side (not just `accept=`); store outside web root
or object storage; serve via signed/expiring URLs. Image pipeline:
`next/image` for local/known hosts (app-router.md).

## Error & retry posture

Typed client errors (network vs 4xx vs 5xx); user-facing retry only where
idempotent; AbortController on unmount in client fetches.
