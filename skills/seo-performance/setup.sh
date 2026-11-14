#!/usr/bin/env bash
# setup.sh — install seo-performance for Claude Code + Codex via symlinks.
# Idempotent; foreign dirs never overwritten. Works from any cwd.
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME="$(basename "$SRC")"

link() { # $1 target root
  local dst="$1/$NAME"
  mkdir -p "$1"
  if [[ -L "$dst" ]]; then
    [[ "$(readlink -f "$dst")" == "$SRC" ]] && { echo "ok      $NAME -> $1"; return 0; }
    echo "conflict $NAME @ $1 (existing link elsewhere, left alone)"; return 1
  elif [[ -e "$dst" ]]; then
    echo "conflict $NAME @ $1 (real directory, left alone)"; return 1
  fi
  ln -s "$SRC" "$dst" && echo "installed $NAME -> $1"
}

rc=0
link "$HOME/.claude/skills" || rc=1     # Claude Code
link "$HOME/.agents/skills" || rc=1     # Codex / agents convention
[[ -d "$HOME/.codex/skills" ]] && link "$HOME/.codex/skills" || true
echo "source: $SRC"
[[ $rc -eq 0 ]] && echo "VERDICT PASS" || echo "VERDICT PASS (with conflicts reported above)"
exit $rc
