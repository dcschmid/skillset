#!/usr/bin/env bash
# setup-check.sh — audit tooling prerequisites probe (Fedora/Linux focus).
# Read-only: installs nothing, changes no session settings (per repo rules).
set -u
ok=0; warn=0
line() { printf '  %-28s %s\n' "$1" "$2"; }
have() { command -v "$1" >/dev/null 2>&1; }

echo "a11y tooling prerequisites"
v=$(node --version 2>/dev/null) && line node "$v" || { line node MISSING; warn=1; }
case "$v" in v2[2-9]*) : ;; v1[0-9]*) ;; *) line "node>=22.18 (TS strip)" "have ${v:-none}"; warn=1 ;; esac
have npm && line npm "$(npm --version)" || { line npm MISSING; warn=1; }
browsers=$(ls "${HOME}/.cache/ms-playwright" 2>/dev/null | grep -cE '^(chromium|firefox)')
line "playwright browsers" "${browsers:-0} cached (npx playwright install chromium firefox)"
[ "${browsers:-0}" -ge 2 ] || warn=1
line "firefox system" "$(firefox --version 2>/dev/null | head -1 || echo MISSING)"
line "orca" "$(orca --version 2>/dev/null | head -1 || echo MISSING)"
line "speech-dispatcher" "$(have speech-dispatcher && echo present || echo MISSING)"
line "desktop" "${XDG_SESSION_TYPE:-?}/${XDG_CURRENT_DESKTOP:-?}"
if have python3 && python3 - <<'PY' 2>/dev/null
import gi; gi.require_version('Atspi','2.0'); from gi.repository import Atspi; Atspi.init()
raise SystemExit(0 if Atspi.get_desktop(0).get_child_count()>0 else 1)
PY
then line "AT-SPI bus" "alive"; else line "AT-SPI bus" "unreachable (SR automation impossible; manual workflows in references/screenreaders.md)"; warn=1; fi
gp=$(ls "${HOME}/.cache/guidepup/orca" 2>/dev/null | head -1)
line "guidepup assets" "${gp:-not installed (npx @guidepup/setup install — project scope)}"
echo "result: $([ $warn = 0 ] && echo READY || echo 'READY-WITH-WARNINGS (SR automation may be degraded — documented, never fabricated)')"
