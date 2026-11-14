# Using the `ultimate-security-hardening` skill in your agents

Security audit, hardening, and remediation for any project (web, API, CLI,
game backends, containers, IaC; any language). Baselines: OWASP Top 10
2025, ASVS 5.0.0, API Security Top 10 2023, WSTG 4.2, CWE Top 25, SSDF,
KEV/EPSS/CVSS, CycloneDX. Spine: DISCOVER → THREAT MODEL → AUDIT → VALIDATE
→ PRIORITIZE → FIX → REGRESSION TEST → RE-SCAN → REPORT. Orchestrates
semgrep, gitleaks, osv-scanner, trivy, ZAP with zero-dep fallbacks — a
missing tool is a coverage gap, never a pass. Never claims "secure".

## Install (this skill only)

```bash
tools/install-skills.sh ultimate-security-hardening
```

Symlinks into both host roots; remove with
`tools/uninstall-skills.sh ultimate-security-hardening`.

## Claude Code

Discovered from `~/.claude/skills/`; activates on any security task:

```
Use the ultimate-security-hardening skill: audit services/api for authz,
injection, and secrets exposure; fix confirmed findings with minimal diffs
and re-scan to prove them closed.
```

## Codex

Same content via `~/.agents/skills/`:

```
Use the ultimate-security-hardening skill: threat-model the checkout
flow, then run the dependency/supply-chain lane and report with CVSS +
evidence file:line.
```

## oh-my-pi (omp)

omp routes from the skill list; Semgrep is the deterministic security lane
by profile, repository config outranks package defaults:

```
Use the ultimate-security-hardening skill: CONFIRM then FIX the OWASP Top
10 findings in this ASP.NET service; regression tests + re-scan before the
final report.
```

## Working style (all hosts)

- Only confirmed findings get fixes; errors surface as INCOMPLETE, never
  hidden. Secrets never leave the repo into reports.
- Direct automation:
  `bash skills/ultimate-security-hardening/scripts/detect-project.sh <project>`,
  `bash skills/ultimate-security-hardening/scripts/check-tools.sh`,
  `bash skills/ultimate-security-hardening/scripts/run-security-audit.sh <project>`,
  `python3 skills/ultimate-security-hardening/scripts/validate-report.py <report>`.

## Examples that work verbatim

```
Use the ultimate-security-hardening skill: audit the IaC in infra/ for
misconfig and drift before this release; patch only what you can prove.
```

## Verify the skill itself

```bash
python3 skills/ultimate-security-hardening/tests/test_skill.py
```

Exit 0 on PASS (static structure + fixtures validation).
