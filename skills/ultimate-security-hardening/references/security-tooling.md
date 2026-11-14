# Security tooling orchestration (probe CLI before running)

Order: run `scripts/check-tools.sh` first — it reports what actually runs
here. Tools upgrade coverage; fallback scanners never depend on them. A
tool error surfaces as a coverage gap, never as PASS (SKILL.md rule 4).
All tools local-first; sources/secrets/results stay on the machine; cloud or
licensed features are opt-in, never silent.

## Installed-here truth (probe 2026-11-14)

| Tool | Role | Status here | Run syntax (verify `--help` live) |
|---|---|---|---|
| semgrep | SAST | **1.183.0** | `semgrep scan --config auto <dir>` / `--config <rules.yaml> --json` |
| node/npx | runners | v22 | `npx semgrep` etc. via project runner |
| python3 | validators | 3.14 | `python3 scripts/validate-report.py …` |
| jq | json glue | 1.8 | present |
| gitleaks/betterleaks | secret scan | absent → fallback regex scanner | install doc below |
| osv-scanner/trivy | SCA | absent → `npm/pnpm audit` + lockfile parse fallback | install doc below |
| checkov | IaC | absent → manual IaC checks | — |
| zap-baseline.py | DAST | absent → documented manual path | — |
| pip-audit/govulncheck/cargo audit | per-ecosystem | probe per project | run only if ecosystem present |

## SAST lane

```bash
semgrep scan --config auto --metrics=off --json --output semgrep.json <dir>   # CE, local rules
semgrep scan --config p/owasp-top-10 --config p/security-audit --json <dir>   # focused packs
```
Pitfalls: first run fetches registry rules (network, allowed with purpose);
offline ⇒ `--config <local.yaml>`; huge monorepo ⇒ scope to source dirs;
`--metrics=off` keeps code local. Every hit = candidate → VALIDATE step.

## SCA / dependency lane

Ecosystem dispatcher (fallback scanner `deps` does this without tools):
npm `npm audit --json`/`pnpm audit --json`; python `pip-audit -r lock
--format json`; rust `cargo audit`; go `govulncheck ./...`. Enrich: KEV +
EPSS for CVEs (cite snapshot date), direct-vs-transitive, fix availability,
reachable-in-deploy judgment → `dependency-security.md`.

## Secret lane

`gitleaks detect --source <dir> --report-format json --report-path out.json`
(work tree; `--no-git` for flat); betterleaks equivalent where preferred.
Fallback: `run-security-audit.sh secrets` (heuristic + entropy). Masked
output always; history scan: `git log -p` piped through same matcher.

## DAST lane (only authorized, ideally isolated targets)

`zap-baseline.py -t <url> -r report.md -I` = passive baseline; automation
framework for suites. Passive crawling still issues requests: exclude
writes/destructive endpoints, never target foreign/unknown systems, prod
gets extra care, no exploiting to read user data. No ZAP here ⇒ fallback:
header/cookie inspection via curl + module §E checks; record coverage gap.

## Config/IaC lane

`trivy config <dir>`, `checkov -d <dir> --output json` (IaC present only);
fallback: IaC manual checklist (infrastructure-hardening.md).

## Test runners (regression lane)

Reuse project's: vitest/jest/pytest/playwright — security tests join the
existing suite, never a parallel private framework.

## Install appendix (only with apt/pipx; never silent)

gitleaks: GitHub releases binary → `~/.local/bin`; osv-scanner: GitHub
release binary or `go install github.com/google/osv-scanner/cmd/osv-scanner@latest`;
trivy: release binary; zap-baseline: `pipx install zaproxy` or OWASP docker
image; pip-audit `pipx install pip-audit`; govulncheck `go install
golang.org/x/vuln/cmd/govulncheck@latest`; checkov `pipx install checkov`.
Recommend → wait for approval → install → re-probe with `--version`.
Versions recorded in report header.

## Non-negotiables

1. Verify `--help` syntax before invoking anything unverified.
2. No tool output forwarded to external/cloud endpoints.
3. One lane's failure = gap report, not a full-scan claim.
4. Duplicate detectors: skip (no value), note once.
