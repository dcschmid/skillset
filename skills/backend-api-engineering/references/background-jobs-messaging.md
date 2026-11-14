# Background Jobs & Messaging

Load when work leaves the request: email, transforms, exports, fan-out,
scheduled tasks, or when a broker (Redis/RabbitMQ/Kafka/NATS) already
exists. New broker = stated need only (prime rule 2).

## Choosing

| Need | Pick |
|---|---|
| "later, small scale, app already has Redis/DB" | project's existing store (BullMQ, Celery, Sidekiq, laravel queues, Hangfire, asgi/ASGI task, or `pgmq`/`SELECT FOR UPDATE SKIP LOCKED` on Postgres) |
| durable event log / replay, many consumers | Kafka/NATS JetStream — only with ops capacity |
| classic broker already present | RabbitMQ queues per consumer group |
| "just nightly" | cron/systemd timer with lock + retries, no broker |

Simplest broker the team can operate wins. No Kafka for one worker.

## Job contract (every job, no exceptions)

- **Idempotent:** replay of the same job = same end state (dedupe key or
  natural idempotency stated). Delivery is at-least-once; exactly-once is
  not promised to callers.
- **Timeout + bounded retries:** exponential backoff + jitter, attempt
  limit; exhausted → DLQ (or failed set) with the payload+error preserved.
- **Poison message:** handler errors on bad payload → DLQ, not infinite
  requeue.
- **Ordering:** only within a partitioned/keyed queue when declared;
  otherwise design assumes reordering.
- **Schema:** versioned JSON envelope (`id`, `type`, `payload`, `meta`,
  `attempts`); consumers ignore unknown fields.

## Producer (transactional outbox)

DB transaction + outbox insert atomically; publisher (worker/poller) ships
with at-least-once + dedupe key. Never publish-then-commit: crash between
⇒ consumer saw an event that never committed.

## Worker ops

Pool sized to I/O not CPU by default; graceful shutdown finishes current
job (bounded), requeues rest; heartbeats+metrics: oldest-job age, queue
depth, processing p95, retry rate, DLQ size (observability.md). Overload
⇒ bounded queues + backpressure (reject-fast or shed, documented), not
unbounded RAM.

## Checks (findings in AUDIT)

jobs without timeout/retry policy · consumer not idempotent · DLQ missing
or never inspected · broker in compose without password · publish inside
txn-less codepath on money flow · cron without lock (double-run) · tests
hitting real broker/prod creds (forbidden — fake or ephemeral).
