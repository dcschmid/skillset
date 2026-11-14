# Observability

Load for CREATE / DEPLOY / AUDIT and any "make it production-ready".

## Logs (structured, the project's lib: pino/winston/structlog/loguru/stdlib)

- JSON lines, one request = one `request_id` (accept `X-Request-Id`/
  `traceparent`, else mint) propagated to DB/HTTP/queue logs; level from
  env; no logging in loops over request payloads.
- **Redaction is a feature:** passwords, tokens, session ids, API keys,
  one-time codes, PII fields — masked at the logger config or via the lib's
  redact map, not by hand-editing message strings. Tests assert redaction.
- Each log line: ts, level, msg, request_id, route, status, dur_ms — the
  minimum for the RED metrics below from logs alone.

## Metrics (Prometheus exposition / OTel SDK / platform — follow the project)

Four golden signals per service: request rate, error rate (4xx/5xx split),
latency histogram (buckets cover p50–p99 of the SLI), saturation (CPU, mem,
pool, queue depth). Plus: DB query duration histogram, cache hit ratio,
queue oldest-job age + retry count, worker uptime, in-flight requests.
`/metrics` behind the same auth posture as the rest or network-scoped.

## Traces (OTel when the project runs more than one process)

Context propagation headers (`traceparent`) through HTTP + queues + DB
comments; spans per handler, per DB call, per external call; sample rate
env-controlled; exporters to the project's collector, no-op fallback when
absent (never crash on missing collector).

## Endpoints & SLO

- `/healthz` (process up, cheap) + `/readyz` (deps reachable: DB ping,
  cache ping, timeout-bounded) — used by LB/orchestrator; both unauth but
  payload-free (no dependency versions/PII).
- SLI: bounded latency + availability from the metrics above; SLO stated in
  the runbook; error budget burn = alert, alert = page only if user-facing.

## Dashboards & alerts (when the platform exists)

RED per endpoint, golden signals per service, DB (pool, slow queries),
queues (lag, DLQ size), deploys (rate, error delta). Alert on symptoms
(error budget, p95, saturation) not causes-only. Follow ultimate-testing-qa
for synthetic checks, ultimate-security-hardening for security telemetry
(findings never feed raw user data to dashboards).

## Rules

unbounded metric label cardinality is a bug · metrics without units lie ·
logs carry no secrets (prime rule 8) · new service without health+metrics
is not production-ready.
