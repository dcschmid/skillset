# Ultimate Security & Hardening

Universal security audit + remediation skill for AI coding agents (Claude
Code, Codex, any SKILL.md-consumer). Audits any project against
OWASP Top 10:2025 / ASVS 5.0.0 / API-Top10 / WSTG / CWE, CONFIRMS findings
with code evidence, applies safe fixes, verifies each fix with regression
tests + re-scan, and reports honestly (tool gap = INCOMPLETE, never PASS).

Spine: `DISCOVER → THREAT MODEL → AUDIT → VALIDATE → PRIORITIZE → FIX →
REGRESSION TEST → RE-SCAN → REPORT`.

## Structure

```
SKILL.md              workflow spine + mode gate (start here)
references/           load per module: standards, audit-modules §A–§J,
                      auth/api/frontend/deps/infra, tooling, remediation,
                      risk-scoring, ci-cd — progressive disclosure
workflows/            6 runnable procedures (audit/fix/verify/gate/threat-model/quick)
scripts/              executable: detect-project.sh · check-tools.sh ·
                      run-security-audit.sh (fallback scanner) · validate-report.py
templates/            report · finding · remediation-plan · security-config.yml
tests/                self-test + vulnerable/clean fixture apps (synthetic only)
```

## Use

Invoke by name or phrase ("audit this project for vulnerabilities", "fix
the security issues", "pre-release security check"). Pick a mode from the
SKILL.md gate; run the scripts from the skill dir against the target:

```bash
bash scripts/detect-project.sh /path/to/project     # stack + surfaces
bash scripts/check-tools.sh /path/to/project        # tool ledger
bash scripts/run-security-audit.sh all /path/to/project   # heuristic lanes
python3 scripts/validate-report.py --dir /path/to/project/security-reports
python3 tests/test_skill.py                          # skill self-test
```

Autofix ladder: SAFE AUTO-FIX applied in-session · REVIEW REQUIRED proposed
as diff · HIGH-RISK blocked for approval. Secrets masked in every output;
user changes never reverted; scanner errors surface as coverage gaps.

## Install (Claude Code + Codex)

```bash
tools/install-skills.sh   # repo installer symlinks into ~/.claude/skills + ~/.agents/skills
```

## Report contract

`security-reports/{security-report.md, security-findings.json,
security-fixes.md, security-test-results.md}` — verdicts
PASS/PASS WITH WARNINGS/BLOCKED/INCOMPLETE, fix statuses
FIXED→FALSE POSITIVE, finding statuses Confirmed→Not-Applicable.
Schema enforced by `validate-report.py` (secrets-in-report = fail).

## Skill interop

Independent. QA/Testing skill runs functional tests, framework skills own
idioms, Accessibility stays separate — no hard dependencies; missing skills
never block this workflow. Security regression tests join the project's
existing runner.

## Maintenance

- Re-verify standards table (`references/security-standards.md`) annually
  or on OWASP/CWE release; update versions + probe dates.
- Re-probe tool CLIs (`check-tools.sh`) when adding scanners; syntax via
  `--help` before documenting.
- New module → `audit-modules.md` section + SKILL.md mode gate row + test
  fixture + run `python3 tests/test_skill.py`.
- Fallback scanner patterns live in `run-security-audit.sh`; extend
  patterns with a fixture pair (vulnerable + clean) to keep FP pressure low.
