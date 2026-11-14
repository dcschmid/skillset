#!/usr/bin/env bash
# check-tools.sh — scanner/tool availability ledger for this machine+project.
# Lanes: sast sca secrets dast iac runtime tests glue. Every line is
# found(name version) | missing | optional. Missing tool = coverage gap,
# NEVER a skipped-as-pass. Exit: 0 always (a ledger, not a gate).
set -uo pipefail
[[ "${1:-}" == "-h" || "${1:-}" == "--help" ]] && { sed -n '2,6p' "$0"; exit 0; }
PROJ="${1:-.}"; [[ -d "$PROJ" ]] || { echo "warn: project dir missing: $PROJ (ledger = host-only)" >&2; PROJ=.; }

row() { # lane tool
  local lane="$1" tool="$2" ver="?"
  if command -v "$tool" >/dev/null 2>&1; then
    ver="$("$tool" --version 2>/dev/null | head -1 | tr -d '\r' | cut -c1-40)"
    printf '%-6s %-14s found    %-40s\n' "$lane" "$tool" "${ver:-?}"
  else
    printf '%-6s %-14s missing  (fallback scanner covers; install per references/security-tooling.md)\n' "$lane" "$tool"
  fi
}

echo "# security tool ledger $(date -u +%FT%TZ) — run against $PROJ"
printf '%-6s %-14s %-8s %s\n' LANE TOOL STATE DETAIL
row sast     semgrep
row sast     codeql
row sca      osv-scanner
row sca      trivy
row sca      pip-audit
row sca      cargo
row sca      govulncheck
row secrets  gitleaks
row secrets  betterleaks
row iac      checkov
row dast     zap-baseline.py
echo "tests   vitest/jest     $( command -v npx >/dev/null 2>&1 && echo 'via npx' || echo missing )"
echo "runtime node            $(command -v node >/dev/null 2>&1 && node --version || echo missing)"
echo "runtime python3         $(command -v python3 >/dev/null 2>&1 && python3 --version || echo missing)"
echo "glue    jq              $(command -v jq >/dev/null 2>&1 && jq --version || echo missing)"
echo "glue    git             $(command -v git >/dev/null 2>&1 && git --version | head -1 || echo missing)"
echo "---"
echo "lanes covered natively here: sast(semgrep) fallback(secrets/deps/config heuristic)."
echo "lanes needing install for depth: sca(osv/trivy), dast(zap), iac(checkov), gitleaks."
exit 0
