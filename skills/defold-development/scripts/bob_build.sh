#!/usr/bin/env bash
# bob_build.sh — Defold bob.jar build wrapper. DRY-RUN by default: prints the
# exact command and exits 0. Add --run to execute. Never deletes outputs;
# existing --output dirs get a dated suffix appended on collision.
# Usage: bob_build.sh [--run] [--profile debug|release] [--platform <p>]
#                    [--output-dir <dir>] [--project <dir>] [--bob <jar>]
# Valid platform/profile flags per /manuals/bob/; check `java -jar bob.jar help`
# for the pinned version — do not pass flags you have not seen in that help.
set -euo pipefail

RUN=0; PROFILE=debug; PLATFORM=""; OUT="build"; PROJECT="."; BOB="${BOB_JAR:-}"
while [[ $# -gt 0 ]]; do case "$1" in
  --run) RUN=1; shift;; --profile) PROFILE="$2"; shift 2;; --platform) PLATFORM="$2"; shift 2;;
  --output-dir) OUT="$2"; shift 2;; --project) PROJECT="$2"; shift 2;; --bob) BOB="$2"; shift 2;;
  *) echo "unknown arg: $1" >&2; exit 2;;
esac; done

[[ -f "$PROJECT/game.project" ]] || { echo "no game.project in $PROJECT" >&2; exit 1; }
if [[ -z "$BOB" ]]; then
  for c in "$PROJECT/../SDK/bob.jar" "$HOME/defold/SDK/bob.jar" ./bob.jar; do
    [[ -f "$c" ]] && { BOB="$c"; break; }; done
fi
[[ -n "$BOB" && -f "$BOB" ]] || { echo "bob.jar not found; pass --bob <path> or set BOB_JAR" >&2; exit 1; }

TARGET="$OUT/$PROFILE${PLATFORM:+-$PLATFORM}"
if [[ -d "$TARGET" ]]; then TARGET="$TARGET-$(date +%Y%m%d-%H%M%S)"; fi
CMD=(java -jar "$BOB" build "$PROFILE" --project-dir "$PROJECT" --output "$TARGET")
[[ -n "$PLATFORM" ]] && CMD+=(--platform "$PLATFORM")

printf '%q ' "${CMD[@]}"; echo
if [[ $RUN -eq 0 ]]; then
  echo "DRY-RUN (add --run). Verify with scripts/check_build.sh after building."
  exit 0
fi
"${CMD[@]}"
rc=$?
echo "build exit=$rc output=$TARGET"
[[ $rc -eq 0 ]] || { echo "BUILD FAILED — do not report success"; exit "$rc"; }
echo "now run: scripts/check_build.sh $TARGET"
