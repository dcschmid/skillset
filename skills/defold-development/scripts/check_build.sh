#!/usr/bin/env bash
# check_build.sh — verify a build output actually exists and is coherent.
# A build is "successful" only when this exits 0; a bob.jar exit 0 alone is
# necessary, not sufficient. Read-only.
# Usage: check_build.sh <output_dir_or_zip> [--platform desktop|web]
set -uo pipefail
T="${1:?usage: check_build.sh <build_output> [--platform desktop|web]}"; P="${2:-desktop}"
[[ -e "$T" ]] || { echo "FAIL missing build output: $T"; exit 1; }

files=0
if [[ -d "$T" ]]; then files=$(find "$T" -type f | wc -l | tr -d ' ')
elif [[ "$T" == *.zip ]]; then files=$(unzip -Z1 "$T" 2>/dev/null | wc -l | tr -d ' ')
else echo "FAIL not a dir/zip: $T"; exit 1; fi

[[ "$files" -gt 0 ]] || { echo "FAIL empty build output: $T"; exit 1; }
echo "output: $T ($files files)"
case "$P" in
  web)
    grep -qiE '\.html?|index' <(unzip -Z1 "$T" 2>/dev/null || find "$T" -type f) \
      || { echo "WARN no html entry found for web build"; } ;;
  desktop)
    found=$(find "$T" -maxdepth 3 -type f -perm -u+x 2>/dev/null | head -3; \
            unzip -Z1 "$T" 2>/dev/null | grep -v '/$' | head -3)
    [[ -n "$found" ]] || { echo "FAIL no executable/payload files — unpack and inspect"; exit 1; }
    printf 'payload: %s\n' $(echo "$found" | head -3) ;;
esac
# archive integrity where checkable
[[ "$T" == *.zip ]] && ! unzip -tq "$T" >/dev/null 2>&1 && { echo "FAIL zip corrupt"; exit 1; }
echo "BUILT: $files files, ${P} shape ok — runtime/visual checks still pending (truth ladder)"
