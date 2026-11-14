#!/usr/bin/env bash
# install-skills.sh — symlink managed skills into Claude Code and Codex.
#
# Usage:
#   tools/install-skills.sh                # install ALL skills
#   tools/install-skills.sh godot astro    # install ONLY these skills
#
# Skills are named by directory under <repo>/skills/. Unknown names abort
# before any change is made.
#
# Idempotent. Foreign (non-managed) skills in target dirs are never touched.
# Conflicts (a real directory or foreign link where a managed link belongs)
# are reported and skipped, not overwritten.
#
# Managed links are recorded in <repo>/.installed-manifest as
# "<skill-name><TAB><target-root>", one link per line, so uninstall removes
# ONLY what this installer created. Legacy manifest lines without a target
# column are still understood by the uninstaller.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$REPO/.installed-manifest"
# Serialize all manifest and link mutations across both commands.
command -v flock >/dev/null || { echo "error: flock is required" >&2; exit 1; }
exec 9>"$MANIFEST.lock"
flock -x 9
TARGETS=("$HOME/.claude/skills" "$HOME/.agents/skills")
SKILLS_SRC="$REPO/skills"

die() { echo "error: $*" >&2; exit 1; }

link_skill() { # $1 = skill dir, $2 = target root
  local src="$1" dst="$2/$(basename "$1")" name; name="$(basename "$1")"

  mkdir -p "$2"
  if [[ -L "$dst" ]]; then
    local cur; cur="$(readlink -f "$dst")"
    if [[ "$cur" == "$src" ]]; then
      printf '%s\t%s\n' "$name" "$2" >> "$MANIFEST_TMP"
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
  printf '%s\t%s\n' "$name" "$2" >> "$MANIFEST_TMP"
  echo "installed $name -> ${2}"
}

# Resolve requested skill dirs (all, or the named subset). Validate before
# touching anything so a typo can never half-install.
requested=("$@")
if [[ ${#requested[@]} -eq 0 ]]; then
  for skill_dir in "$SKILLS_SRC"/*/; do
    [[ -f "$skill_dir/SKILL.md" ]] || continue
    requested+=("$(basename "${skill_dir%/}")")
  done
else
  for name in "${requested[@]}"; do
    [[ -f "$SKILLS_SRC/$name/SKILL.md" ]] \
      || die "no such skill: $name (expected skills/$name/SKILL.md)"
  done
fi

rc=0
touch "$MANIFEST"
MANIFEST_TMP=$(mktemp "$MANIFEST.tmp.XXXXXX")
trap 'rm -f "$MANIFEST_TMP"' EXIT
cp "$MANIFEST" "$MANIFEST_TMP"
for name in "${requested[@]}"; do
  for tgt in "${TARGETS[@]}"; do
    link_skill "$SKILLS_SRC/$name" "$tgt" || rc=1
  done
done

sort -u "$MANIFEST_TMP" -o "$MANIFEST_TMP"
mv "$MANIFEST_TMP" "$MANIFEST"

echo "manifest: $MANIFEST"
exit $rc
