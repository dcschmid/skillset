#!/usr/bin/env bash
# headless_check.sh — run the Godot verification ladder on a project dir.
# Levels: STATIC (script parse) -> IMPORTED (--import) -> RUNTIME (boot).
# No engine on PATH -> SKIP verdicts with exact commands (never fake passes).
# Non-destructive; reads only. Exit 0 = every executed level passed.
#
# Usage: headless_check.sh <project_dir> [quit_frames]
set -uo pipefail

PROJ="${1:-.}"
FRAMES="${2:-120}"
GODOT="${GODOT_BIN:-$(command -v godot || true)}"

[[ -f "$PROJ/project.godot" ]] || { echo "FAIL no project.godot in $PROJ"; exit 1; }
cd "$PROJ" || exit 1

if [[ -z "$GODOT" ]]; then
  echo "SKIP no godot binary (set GODOT_BIN or PATH)"
  echo "RUN: godot --headless --path . --import"
  echo "RUN: find . -name '*.gd' -exec godot --headless --check-only --script {} ';'"
  echo "RUN: godot --headless --path . --quit-after $FRAMES"
  echo "VERDICT UNVERIFIED (engine absent)"
  exit 0
fi

rc=0
echo "== STATIC: parse every .gd =="
parse_fail=0
while IFS= read -r -d '' f; do
  out="$("$GODOT" --headless --path . --check-only --script "res://${f#./}" 2>&1)" \
    || { echo "PARSE FAIL $f"; echo "$out" | tail -3; parse_fail=$((parse_fail+1)); rc=1; }
done < <(find . -name '*.gd' -not -path './.godot/*' -print0)
[[ $parse_fail -eq 0 ]] && echo "STATIC PASS ($(find . -name '*.gd' -not -path './.godot/*' | wc -l | tr -d ' ') scripts)"

echo "== IMPORTED: project import =="
if out="$("$GODOT" --headless --path . --import 2>&1)"; then
  echo "$out" | grep -qE '^ERROR' && { echo "IMPORT errors:"; echo "$out" | grep '^ERROR' | head; rc=1; } \
    || echo "IMPORTED PASS"
else
  echo "IMPORT FAIL (exit $?)"; echo "$out" | tail -5; rc=1
fi

echo "== RUNTIME: boot $FRAMES frames =="
if out="$("$GODOT" --headless --path . --quit-after "$FRAMES" 2>&1)"; then
  echo "$out" | grep -qE '^SCRIPT ERROR|^ERROR' && { echo "RUNTIME errors:"; echo "$out" | grep -E '^SCRIPT ERROR|^ERROR' | head; rc=1; } \
    || { echo "RUNTIME PASS"; echo "$out" | grep -v '^$' | tail -3; }
else
  echo "RUNTIME FAIL (exit $?)"; echo "$out" | tail -5; rc=1
fi

[[ $rc -eq 0 ]] && echo "VERDICT PASS (STATIC+IMPORTED+RUNTIME; BUILT/VISUAL: run workflows/release-build.md)" \
                || echo "VERDICT FAIL (see level outputs above)"
exit $rc
