# Example 9 — production-readiness pass (DEPLOY)

Task: "make the backend production-ready." Mode DEPLOY
(deployment.md + observability.md).
Deltas landed: env schema (fail-fast boot) · `/healthz` `/readyz`
(templates/health-endpoints.md), probes in compose + proxy pass-through
· graceful shutdown drains requests (SIGTERM→finish→pool close) ·
structured+redacted logs w/ request_id · RED metrics behind same auth
posture · Dockerfile: pinned base, multi-stage, non-root, healthcheck ·
compose: named volumes, healthchecks, no published DB ports · runbook
(deploy/rollback/restore commands, restore tested once on staging).
Verify: `docker compose up` from clean volumes, migrations green, suites
green, probes 200. Scorecard.md filled with those command outputs.
