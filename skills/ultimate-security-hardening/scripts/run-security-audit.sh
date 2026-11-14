#!/usr/bin/env bash
# run-security-audit.sh — zero-dependency fallback security scanner +
# tool dispatcher. Lanes: secrets | deps | config | headers | all.
# Works WITHOUT external scanners (regex/heuristic); where semgrep/gitleaks/
# auditors exist, delegates and merges. Findings = candidates: every hit
# needs VALIDATE before "confirmed". Secret VALUES are masked in output.
# Exit: 0 clean|hits, 1 lane/tool error (gap), 2 bad usage.
set -uo pipefail
LANE="${1:-all}"; PROJ="${2:-.}"
case "$LANE" in -h|--help) sed -n '2,9p' "$0"; exit 0;; esac
[[ -d "$PROJ" ]] || { echo "error: not a directory: $PROJ" >&2; exit 2; }
PROJ="$(cd "$PROJ" && pwd)"
command -v rg >/dev/null 2>&1 && GREP="rg --no-heading -n --max-columns 160 -g" || GREP="grep -rn --color=never"
gsearch() { # pattern [globs...] -> file:line:content
  local pat="$1"; shift
  if [[ "$GREP" == rg* ]]; then
    local args=(); for g in "$@"; do args+=(-g "$g"); done
    rg --no-heading -n --no-messages --max-columns 160 "${args[@]}" -e "$pat" "$PROJ" 2>/dev/null | head -200
  else
    grep -rn --color=never -E "$pat" "$PROJ" \
      --include="${1:-*.py}" "${@:2}" 2>/dev/null | head -200
  fi
}
mask() { sed -E 's/(.{12}).{4,}(.{4})$/\1***MASKED***\2/'; }
emit() { printf 'FINDING [%s] %s:%s :: %s\n' "$1" "${2#"$PROJ"/}" "${3:-?}" "$4"; }
hits=0; gaps=""
count_out() { wc -l | tr -d ' '; }

report_scan() { # lane pattern desc globs...   (code excerpts stay visible)
  local lane="$1" pat="$2" desc="$3"; shift 3
  local out; out="$(gsearch "$pat" "$@" | grep -vE '/(node_modules|\.git|dist|build|\.venv|venv|target|vendor)/' | grep -vE '\.(min\.js|map|lock)$' || true)"
  local n; n="$(printf '%s' "$out" | grep -c . || true)"
  if [[ "$n" -gt 0 ]]; then
    while IFS= read -r line; do
      [[ -z "$line" ]] && continue
      local f l c; f="${line%%:*}"; l="$(echo "$line" | cut -d: -f2)"; c="$(echo "$line" | cut -d: -f3- | sed -E 's/^ +//' | cut -c1-120)"
      emit "$lane" "$f" "$l" "$desc | $c"; hits=$((hits+1))
    done <<<"$out"
  fi
  return 0
}
report_scan_masked() { # same, but content passes through mask() (secret lane)
  local lane="$1" pat="$2" desc="$3"; shift 3
  local out; out="$(gsearch "$pat" "$@" | grep -vE '/(node_modules|\.git|dist|build|\.venv|venv|target|vendor)/' | grep -vE '\.(min\.js|map|lock)$' || true)"
  local n; n="$(printf '%s' "$out" | grep -c . || true)"
  if [[ "$n" -gt 0 ]]; then
    while IFS= read -r line; do
      [[ -z "$line" ]] && continue
      local f l c; f="${line%%:*}"; l="$(echo "$line" | cut -d: -f2)"; c="$(echo "$line" | cut -d: -f3- | sed -E 's/^ +//' | cut -c1-120)"
      emit "$lane" "$f" "$l" "$(printf '%s' "$desc | $c" | mask)"; hits=$((hits+1))
    done <<<"$out"
  fi
  return 0
}

# ---------------- SECRETS lane ----------------
secrets_lane() {
  echo "== lane: secrets (heuristic; masked) =="
  report_scan_masked secrets '(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|sk-[A-Za-z0-9]{20,})' "cloud/api-key-shaped literal" '*.py' '*.js' '*.ts' '*.json' '*.yml' '*.yaml' '*.md' '*.env'
  report_scan_masked secrets '(password|passwd|secret|api_?key|token)[[:space:]]*[:=][[:space:]]*["'"'"'][^"'"'"']{8,}["'"'"']' "hardcoded credential-shaped assignment" '*.py' '*.js' '*.ts' '*.yml' '*.yaml'
  report_scan secrets '-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----' "private key block" '*'
  if command -v gitleaks >/dev/null 2>&1; then
    gitleaks detect --source "$PROJ" --no-banner --report-format json --report-path /tmp/.ush-gitleaks.json >/dev/null 2>&1 \
      && echo "(gitleaks ran: $(jq -r 'length' /tmp/.ush-gitleaks.json 2>/dev/null || echo '?') findings — merge into secrets lane)" \
      || gaps="$gaps gitleaks-error"
  else gaps="$gaps gitleaks-missing"; fi
  # shipped env files
  find "$PROJ" -maxdepth 3 -name '.env*' ! -name '*.example*' ! -name '*.sample*' \
    -not -path '*/node_modules/*' 2>/dev/null | while read -r f; do
      git -C "$PROJ" check-ignore -q "$f" 2>/dev/null || emit secrets "$f" 1 "shipped env file (verify tracked+gitignored)" | mask; done
}

# ---------------- DEPS lane ----------------
deps_lane() {
  echo "== lane: deps (inventory + auditor delegate; CVE verdicts need osv/pip-audit when present) =="
  if [[ -f "$PROJ/package.json" ]]; then
    echo "npm: manifest $(wc -l <"$PROJ/package.json") lines; lockfiles: $(ls "$PROJ" | grep -E 'lock' | tr '\n' ' ')"
    (cd "$PROJ" && { command -v pnpm >/dev/null && [[ -f pnpm-lock.yaml ]] && pnpm audit --json 2>/dev/null | jq -r '.advisories // . | keys | length' 2>/dev/null | sed 's/^/pnpm audit advisories: /' \
      || npm audit --json 2>/dev/null | jq -r '.metadata.vulnerabilities // empty | tostring' 2>/dev/null | sed 's/^/npm audit: /'; }) || gaps="$gaps npm-audit-fail"
    grep -oE '"[^"]+": *"(latest|\*)"?' "$PROJ/package.json" 2>/dev/null | head -10 | sed 's/^/UNPINNED: /'
  fi
  for lf in requirements.txt uv.lock poetry.lock Pipfile.lock; do [[ -f "$PROJ/$lf" ]] && echo "python: $lf present"; done
  command -v pip-audit >/dev/null 2>&1 && [[ -f "$PROJ/requirements.txt" ]] \
    && (cd "$PROJ" && pip-audit -r requirements.txt 2>/dev/null | sed 's/^/pip-audit: /') || gaps="${gaps} pip-audit-$(command -v pip-audit >/dev/null 2>&1 && echo idle || echo missing)"
  [[ -f "$PROJ/Cargo.lock" ]] && echo "rust: Cargo.lock present; run cargo audit for CVEs" 
  [[ -f "$PROJ/go.mod" ]] && echo "go: go.mod present; run govulncheck for CVEs"
  # unpinned/major drift smell in python
  grep -hE '^[a-zA-Z0-9_.-]+==[0-9]' "$PROJ"/requirements*.txt 2>/dev/null | head -5 | sed 's/^/pinned: /' >/dev/null
  echo "(heuristic deps lane: inventory complete, CVE verdicts = coverage-gap unless an auditor ran; document in ledger)"
}

# ---------------- CONFIG lane ----------------
config_lane() {
  echo "== lane: config =="
  report_scan config 'DEBUG[[:space:]]*=[[:space:]]*(True|true)' "DEBUG on (verify env split)" '*.py'
  report_scan config 'django-debug-toolbar|debug_toolbar' "debug toolbar (verify prod off)" '*.py'
  report_scan config 'showDevTools|hot:[[:space:]]*true' "dev tooling on" '*.js' '*.ts'
  report_scan config 'verify[[:space:]]*=[[:space:]]*(False|false)|rejectUnauthorized[[:space:]]*:[[:space:]]*false|SSL_VERIFY_NONE|rejectUnauthorized' "TLS verification disabled" '*.py' '*.js' '*.ts'
  report_scan config 'docker build --privileged|--privileged|privileged:[[:space:]]*true' "privileged container" '*'
  report_scan config '(^|[^a-z])USER root|runAsNonRoot[[:space:]]*:[[:space:]]*false' "container root user" 'Dockerfile' '*.yaml'
  report_scan config 'md5\(|sha1\(|createHash\(["'"'"'](md5|sha1)["'"'"']\)' "legacy hash algo (context: password/integrity?)" '*.py' '*.js' '*.ts'
  report_scan config 'Math\.random\(\)|random\.(random|randint|choice|getrandbits|shuffle)\(|rand\.(Intn|Read|Float64)' "default RNG — verify secret material use (tokens/keys/IVs)" '*.py' '*.js' '*.ts'
  report_scan config 'pickle\.loads|eval\(|new Function\(' "deser/dynamic exec on possibly-untrusted data" '*.py' '*.js' '*.ts'
  report_scan config 'dangerouslySetInnerHTML|v-html|\{@html\}|innerHTML[[:space:]]*=' "raw HTML sink" '*.jsx' '*.tsx' '*.vue' '*.svelte' '*.js' '*.ts'
  report_scan config 'f"[^"]*(SELECT|INSERT INTO|DELETE FROM|UPDATE)[^"]*\{|["'"'"'](SELECT|INSERT INTO|UPDATE|DELETE)[^"'"'"']*\+' "SQL built by f-string/concat — parameterize" '*.py' '*.js' '*.ts'
  report_scan config 'exec\(|shell=True|child_process\.exec\(' "shell exec (input-traced?)" '*.py' '*.js' '*.ts'
  if [[ -f "$PROJ/Dockerfile" ]]; then
    grep -qE '^FROM [^ ]+:latest|^FROM .*:latest' "$PROJ/Dockerfile" && emit config Dockerfile ? "floating :latest base"
    grep -qE '^USER ' "$PROJ/Dockerfile" || emit config Dockerfile ? "no USER directive (runs root)"
    grep -qE '^[[:space:]]*EXPOSE 80$|EXPOSE 80 ' "$PROJ/Dockerfile" >/dev/null && true
  fi
  command -v trivy >/dev/null 2>&1 && (trivy config "$PROJ" 2>/dev/null | sed 's/^/trivy-cfg: /' | head -40) || gaps="${gaps} trivy-missing"
}

# ---------------- HEADERS lane (needs running target: static config probe) ----------------
headers_lane() {
  echo "== lane: headers (static config probe; runtime probe = curl when app runs) =="
  gsearch 'helmet|Content-Security-Policy|Strict-Transport-Security|X-Frame-Options|SameSite|frame-ancestors' -g '*.ts' -g '*.js' -g '*.py' -g '*.conf' -g '*.yml' 2>/dev/null \
    | grep -vE '/(node_modules|dist)/' | head -30 | while IFS= read -r l; do emit headers "${l%%:*}" "$(echo "$l"|cut -d: -f2)" "header-control present: $(echo "$l" | cut -d: -f3- | sed 's/^ *//' | cut -c1-100)"; done
  [[ -z "$gaps" && ! -s "$PROJ/security-reports/.headers-probed" ]] && echo "(runtime header check requires a running target; record NOT-RUN if app absent)"
}

case "$LANE" in
  secrets) secrets_lane ;;
  deps)    deps_lane ;;
  config)  config_lane ;;
  headers) headers_lane ;;
  all)     secrets_lane; deps_lane; config_lane; headers_lane ;;
  *) echo "error: unknown lane '$LANE' (secrets|deps|config|headers|all)" >&2; exit 2 ;;
esac

echo "== summary: $hits candidate(s) | gaps:${gaps:- none} =="
echo "(all findings = candidates: VALIDATE against source before confirmed; gaps = INCOMPLETE not pass)"
[[ -n "${FORCE_FAIL:-}" ]] && exit 1
exit 0
