# Health & readiness endpoints (adapt to project router idiom)

GET /healthz — process liveness. No deps, no payload detail:
200 {"status":"ok"} (+ build sha/version if policy allows). Never dependency
versions or PII.

GET /readyz — traffic gate. Bounded pings (each ≤ ~1s, parallel):
200 {"status":"ready"} | 503 {"status":"unavailable"} when DB/cache ping
fails. Body stays tiny: state only, never error strings/stacks/DSNs.

Wiring: exclude from auth+rate-limit, but network-scope or same auth posture
as API; proxy passes through without buffering; orchestrator probes point
here (liveness=/healthz, readiness=/readyz).

Rules: no writes, no logs per hit beyond debug level, timeouts per dependency,
first failure = 503 with Retry-After absent (caller polls).
