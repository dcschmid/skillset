#!/usr/bin/env bash
# uninstall-skills.sh — remove ONLY symlinks this installer created.
#
# Usage:
#   tools/uninstall-skills.sh                 # remove ALL managed links
#   tools/uninstall-skills.sh godot astro     # remove ONLY these skills
#
# Reads <repo>/.installed-manifest ("<skill-name><TAB><target-root>" lines;
# legacy name-only lines are also honored, checked against the default
# targets). A target is removed only when it is a symlink pointing at this
# repo's skills/. Foreign files/dirs/links survive. The manifest keeps the
# entries of skills that remain installed.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$REPO/.installed-manifest"
DEFAULT_TARGETS=("$HOME/.claude/skills" "$HOME/.agents/skills")

[[ -f "$MANIFEST" ]] || { echo "nothing installed (no manifest)"; exit 0; }

selected() { # $1 = name; true when uninstall-all or name in "$@"
  local name="$1"; shift
  [[ $# -eq 0 ]] && return 0
  local n; for n in "$@"; do [[ "$n" == "$name" ]] && return 0; done
  return 1
}

remove_link() { # $1 = name, $2 = target root
  local path="$2/$1" dest
  if [[ -L "$path" ]]; then
    dest="$(readlink -f "$path")"
    if [[ "$dest" == "$REPO/skills/$1" ]]; then
      rm "$path"
      echo "removed $path"
    else
      echo "kept    $path (foreign link -> $dest)"
    fi
  elif [[ -e "$path" ]]; then
    echo "kept    $path (not a symlink)"
  fi
}

remaining=""
while IFS=$'\t' read -r name tgt _; do
  [[ -n "${name-}" ]] || continue
  if selected "$name" "$@"; then
    if [[ -n "${tgt-}" ]]; then
      remove_link "$name" "$tgt"
    else  # legacy manifest: no target recorded, scan the defaults
      for tgt in "${DEFAULT_TARGETS[@]}"; do remove_link "$name" "$tgt"; done
    fi
  else
    if [[ -n "${tgt-}" ]]; then remaining+="$name"$'\t'"$tgt"$'\n'
    else remaining+="$name"$'\n'; fi
  fi
done < "$MANIFEST"

printf '%s' "$remaining" > "$MANIFEST"
[[ -s "$MANIFEST" ]] && echo "manifest: $MANIFEST" || { rm -f "$MANIFEST"; echo "manifest cleared"; }
