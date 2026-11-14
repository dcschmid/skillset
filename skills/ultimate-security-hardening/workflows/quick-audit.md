# Workflow: quick-audit (incl. DIFF MODE)

Scope: small change surface, PR review, "check this quickly". Depth dial:
ASVS L1. Still runs the full spine compressed — never report-only.

1. **DISCOVER** `bash scripts/detect-project.sh <dir>` + `git status`
   + `git log -1 --format=%H`. DIFF MODE: base ref (arg or HEAD~n/branch);
   `git diff --name-only <base>...` narrows step 2 to changed files, with
   the caveat that shared helpers/configs changed count too.
2. **THREAT MODEL (60s)**: changed files = which trust boundaries? which
   user input reaches which sink here?
3. **AUDIT**: modules for detected techs, limited to changed files +
   their direct callers. SAST if semgrep present (scope = changed paths).
   Deps: only if lockfiles changed. Secrets: changed files + adjacent config.
4. **VALIDATE** each candidate against source; kill FPs with reason.
5. **PRIORITIZE** per risk-scoring.md; quick audits still rank honestly.
6. **FIX** SAFE AUTO-FIX items now; REVIEW/HIGH-RISK → proposed diffs.
7. **REGRESSION TEST**: project's existing tests covering touched code
   must pass; add a micro-test for a fixed flaw when cheap.
8. **RE-SCAN**: detector that found it, rerun on touched files.
9. **REPORT**: `security-reports/quick-audit-<date>.md` (+ findings.json).
   Compact form: findings table + ledger + verdict; skip full template.

Exit codes / verdicts identical to full audit. Incomplete when tool gaps
hit the changed surface. Timebox never cancels step 4 or 9.
