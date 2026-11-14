# Deployment & Operations

Load for DEPLOY / "production-ready". Infra only as far as the project's
operating reality requires; never deploy to prod unprompted.

## Runtime

- **Container:** distroless/slim base matching runtime version; multi-stage
  build (deps cached from lockfiles); non-root user; `CMD`/entrypoint =
  server + `docker start-period`/healthcheck; `.dockerignore` excludes
  .git/tests/docs. Compose for local: app + DB + cache + migrations run as
  an init step, named volumes, healthchecks + `depends_on: condition`.
- **systemd (VMs):** `Type=notify`/`ExecStart` with `Restart=on-failure`,
  `WatchdogSec`, `EnvironmentFile`, resource limits; migrations in a
  one-shot unit before service start.
- **Proxy:** Nginx/Caddy in front; TLS at proxy or app per project;
  `proxy_read_timeout` > handler timeout; request body limits; static/
  asset caching headers; websockets/SSE need `proxy_buffering off` + long
  read timeout — verify per route class, not globally.
- **K8s:** only when the project already runs there; then probes from
  observability.md, PDB, resource requests/limits, HPA on CPU/custom
  metric, ConfigMap/Secret split.

## Config & release

- 12-factor: config via env, schema-validated at boot (fail-fast);
  per-env values in the platform; secrets never baked into image.
- **Migrations are a deploy step, not app boot** (unless single-instance
  + documented): run before/at cutover, expand-and-contract (see
  database-migrations.md); release order: DB-backward-compatible → app →
  contract cleanup.
- Zero-downtime where the shape allows: old+new code coexist during
  rollout; readiness gates traffic; graceful shutdown drains (SIGTERM →
  finish requests → close pools → exit; terminationGracePeriod > max req).

## Backups & recovery (state the plan in the runbook)

- DB scheduled dump/PITR; tested restore command in runbook (untested
  backup doesn't exist); object storage versioning for uploads.
- Rollback: previous image tag kept; down-migration or forward-fix
  documented before rollout (database-migrations.md).
- Runbook: deploy, rollback, migrate, restore, incident triage commands —
  copy-pastable, not prose.

## Verification before calling DEPLOY done

compose up from clean volumes green · migrations on fresh+seeded DB pass ·
`/healthz` `/readyz` 200 · TLS+headers probed · resource limits set ·
logs structured+redacted · CI runs tests against the same image · rollback
steps executed once on staging. Anything skipped ⇒ `INCOMPLETE`, list the
exact command for the owner.
