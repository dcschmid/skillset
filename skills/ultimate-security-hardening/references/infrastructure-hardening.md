# Infrastructure & configuration hardening (module §I + IaC)

Files detected by `detect-project.sh` gate every check: absent tech =
`Not Applicable`, not skipped silently. `trivy config`/`checkov` when
installed; manual checklist otherwise (still produces findings).

## Docker / Compose

- Base images: pinned digest or exact tag (no floating `latest` on prod images)
- User: non-root (`USER` directive or K8s `runAsNonRoot`); root only justified
- Build: multi-stage lean, secrets not baked (`--mount=type=secret`/env at runtime), `.dockerignore` present
- Runtime: `read_only` fs where feasible, `cap_drop`, no `privileged`, healthcheck present
- Ports: expose only needed; `ports:` bindings host-scoped (127.0.0.1 vs 0.0.0.0)
- Compose: env via `.env`/secrets not literal; internal networks; volumes named
- Registry: image scans in CI (trivy image), digest pin after pinning tag

## Kubernetes

`securityContext` (runAsNonRoot, readOnlyRootFilesystem, drop ALL caps),
imagePullPolicy+tag, ServiceAccount `automountServiceAccountToken:false`
default-on, NetworkPolicy present where flat-namespace, Secrets as mounted
files not env sprawl, `latest` forbidden, resource limits (availability).

## Terraform / IaC

Bucket/object public ACLs, SG `0.0.0.0/0` ingress on non-web ports, RDS
public accessibility, IAM wildcards, hardcoded provider creds, state
backends private+encrypted, plan/apply split + PR review (SSDF PW).

## Reverse proxies (nginx/Caddy/Traefik)

TLS ≥1.2 (1.3 pref), HSTS at the TLS-terminating layer, upstream header
trust (X-Forwarded-* only from trusted hops), server tokens off, static
`expires` + `no-store` for authed, upload size caps, admin/UI paths internal.

## CI/CD files (repo-local check here, generation lane → ci-cd-security.md)

Actions pinned to SHA/tag, `pull_request_target`+checkout of PR code avoided,
secrets via store not echo, token scopes minimal, artifact retention sane.

## Runtime/dotenv/configs shipped

`.env.example` shipped with placeholders · real `.env*` gitignored · config
permissions not world-writable · debug endpoints/profiler/admin UI env-gated ·
error verbosity env-gated · default creds changed · DB ports unpublished in
prod compose · health endpoints payload-minimal.

## Test-system extras

Linux services: unit files least-priv (User=, ProtectSystem=); cron payloads
no secrets in argv (visible in ps). Game backends (Defold/Godot servers):
gateway auth, client-authoritative state minimized. Local AI services: bind
localhost, request size caps, no filesystem escape from workspace roots.
