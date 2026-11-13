#!/usr/bin/env bash
# uninstall-skills.sh — remove ONLY symlinks this installer created.
#
# Reads <repo>/.installed-manifest. A target is removed only when it is a
# symlink pointing at this repo's skills/. Foreign files/dirs/links and the
# manifest itself survive.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$REPO/.installed-manifest"
TARGETS=("$HOME/.claude/skills" "$HOME/.agents/skills")
KEEP="${1-}"   # optional: pass skill name to keep it installed

[[ -f "$MANIFEST" ]] || { echo "nothing installed (no manifest)"; exit 0; }

while IFS= read -r name; do
  [[ -n "$name" ]] || continue
  [[ -n "$KEEP" && "$name" == "$KEEP" ]] && continue
  for tgt in "${TARGETS[@]}"; do
    path="$tgt/$name"
    if [[ -L "$path" ]]; then
      dest="$(readlink -f "$path")"
      if [[ "$dest" == "$REPO/skills/$name" ]]; then
        rm "$path"
        echo "removed $path"
      else
        echo "kept    $path (foreign link -> $dest)"
      fi
    elif [[ -e "$path" ]]; then
      echo "kept    $path (not a symlink)"
    fi
  done
done < "$MANIFEST"

if [[ -z "${KEEP-}" ]]; then
  rm -f "$MANIFEST"
  echo "manifest cleared"
fi
