# CI/CD security (GitHub Actions focus; lane owner for the skill)

Skill can generate additive lanes for existing pipelines — never replaces
the pipeline, thresholds configurable, gates documented. Primary target
GitHub Actions; principles map to GitLab CI/Jenkins where detected.

## Lanes (offer as opt-in, one job per stage, additive)

| Stage | Job | Gate |
|---|---|---|
| PR | `sast` (semgrep), `secrets` (gitleaks/fallback), `dep-audit`, security regression tests | new confirmed CRITICAL/HIGH ⇒ red |
| Build | artifact/build provenance, container image scan (trivy image) when images built, SBOM (CycloneDX) on request | non-blocking by default, warn |
| Release | release-gate ladder (`workflows/release-gate.md`) | BLOCKED stops publish |

## Pipeline authoring rules (hardening the CI itself)

- `permissions:` minimal per workflow/job token (contents:read at most;
  write only where the job provably needs) — least privilege for CI tokens
- Actions pinned by SHA (or exact tag + local cache) per project policy
- untrusted PR code isolation: `pull_request` (not `pull_request_target`)
  when checking out PR code; no secrets in jobs running PR sources;
  `pull_request_target` + checkout PR head = workflow-injection surface
- no eval on PR-derived files; env propagation scoped per step (secrets
  not echoed, `set -x` off around secret use)
- caches/dependencies: lockfile install, registry allowlists where possible
- artifacts: retention + no secrets baked into logs/upload bundles
- fork PRs: secrets unavailable ⇒ lanes degrade to documented gaps, not skips

## Gate behavior

New confirmed CRITICAL/HIGH ⇒ fail by default. Existing backlog ⇒ report,
don't redden the whole team's CI (baseline diff supported). Time-boxed
exceptions: id · owner · expiry · justification tracked (release-gate input 6).
Tool error in a lane ⇒ exit as gap (warning + note), never silent green.

## Generation contract (when asked to "add security to CI")

Read existing workflows first; new file(s) additive or job appended; mirror
the repo's job style; runner images/node versions from the project; probe
tool availability in CI context (installs via pipx/pipx-cached/binary
releases, versions recorded). Diff stays REVIEW REQUIRED if it changes
release-blocking behavior.
