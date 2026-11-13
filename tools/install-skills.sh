#!/usr/bin/env bash
# install-skills.sh — symlink managed skills into Claude Code and Codex.
#
# Idempotent. Foreign (non-managed) skills in target dirs are never touched.
# Conflicts (a real directory or foreign link where a managed link belongs)
# are reported and skipped, not overwritten.
#
# Managed links are recorded in <repo>/.installed-manifest (one skill name per
# line) so uninstall removes ONLY what this installer created.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$REPO/.installed-manifest"
TARGETS=("$HOME/.claude/skills" "$HOME/.agents/skills")
SKILLS_SRC="$REPO/skills"

touch "$MANIFEST"

link_skill() { # $1 = skill dir, $2 = target root
  local src="$1" dst="$2/$(basename "$1")" name; name="$(basename "$1")"

  mkdir -p "$2"
  if [[ -L "$dst" ]]; then
    local cur; cur="$(readlink -f "$dst")"
    if [[ "$cur" == "$src" ]]; then
      echo "ok      $name -> ${2}  (already linked)"
      return 0
    fi
    echo "conflict $name @ ${2}: existing link points to $cur (left alone)"
    return 1
  elif [[ -e "$dst" ]]; then
    echo "conflict $name @ ${2}: real directory/file present (left alone)"
    return 1
  fi

  ln -s "$src" "$dst"
  echo "installed $name -> ${2}"
}

rc=0
for skill_dir in "$SKILLS_SRC"/*/; do
  [[ -f "$skill_dir/SKILL.md" ]] || continue
  name="$(basename "$skill_dir")"
  printf '%s\n' "$name" >> "$MANIFEST.tmp" && mv "$MANIFEST.tmp" "$MANIFEST"
  for tgt in "${TARGETS[@]}"; do
    link_skill "${skill_dir%/}" "$tgt" || rc=1
  done
done

if [[ ! -f "$MANIFEST" ]]; then : > "$MANIFEST"; fi
sort -u "$MANIFEST" -o "$MANIFEST"

echo "manifest: $MANIFEST"
exit $rc
