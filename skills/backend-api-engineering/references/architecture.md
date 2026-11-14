# Server Architecture & System Design

Load for modes ARCHITECTURE / CREATE / AUDIT. Choose the simplest shape
that meets functional + operational requirements.

## Shapes (escalation ladder — climb only on stated need)

1. **Modular monolith** — modules with private interfaces, one deployable,
   one DB. Default for small→medium and most teams. Module boundaries in
   directories + import rules, enforced by tests/lint.
2. **Layered/hexagonal** — inside modules: handlers → service → repository;
   domain types at the center; adapters (HTTP/queue/mail) implement ports.
   Use when testability and swap-ability of I/O matter.
3. **Background workers** — when work outgrows a request (email,
   transforms, retries): add the queue the project can operate; see
   background-jobs-messaging.md.
4. **Service extraction** — only with a named driver: independent scaling
   profile, team ownership boundary, language/runtime need. Each extraction
   ships contract + own data + deployment + observability. Microservices
   are not a default for small apps.
5. **Event-driven / outbox** — when consumers must react to state changes
   transactionally: transactional outbox → publisher → consumers idempotent.
   Exactly-once is not promised; at-least-once + dedupe is the honest term.

## Cross-cutting requirements (any shape)

- **Config:** typed, validated at boot (env schema), secrets from the
  platform store, not files.
- **Errors:** one mapping (domain → transport, RFC 9457); no swallowed
  exceptions; request ids propagated to logs and downstream calls.
- **Graceful lifecycle:** health+readiness endpoints; SIGTERM drains
  requests + closes pools; startup fails fast on config/DB checks.
- **Resilience on outbound calls:** timeouts everywhere, retries only on
  idempotent ops (backoff+jitter, budgets), circuit breaker where a slow
  dependency can cascade.
- **Boundaries:** DTOs at edges (validation in, encoding out); domain never
  leaks; no ORM entities as API responses.

## Analysis workflow (AUDIT/ARCHITECTURE)

1. Map deployables, data stores, sync + async edges (from detect-project.sh
   + reading entrypoints/routes/worker defs).
2. List coupling hotspots (shared tables, god-services, cross-module
   imports), failure amplifiers (no timeout, unbounded queues, cache
   stampede), scaling ceilings (singletons, in-memory state, file writes).
3. Propose the smallest move that removes the binding constraint; each
   proposal names trigger metric for the next step ("extract when p95 of
   X exceeds Y under load Z").

## DDD / clean notes

Aggregates only when invariants span entities and concurrent edits are
real; repositories where persistence is swappable; otherwise plain service
functions with explicit dependencies beat ceremony. Follow the project's
existing naming; don't graft new vocabulary onto a working codebase.
