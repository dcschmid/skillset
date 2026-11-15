#!/usr/bin/env bash
# install-skills.sh — symlink managed skills into the agent roots, profile-routed.
#
# Usage:
#   tools/install-skills.sh                     # install ALL skills (durable routing)
#   tools/install-skills.sh godot astro         # install ONLY the named skills
#   tools/install-skills.sh --claude private    # launch-sync Claude's shared root to Private
#   tools/install-skills.sh --claude working    # launch-sync Claude's shared root to Working
#
# Skills are named by directory under <repo>/skills/. Unknown names abort
# before any change is made.
#
# Two separation models coexist (both mirror the dev-setup stack):
#   Durable (spatial) — omp profiles and private/working Codex homes. Routing
#     is EXCLUSIVE (tools/profile-map.tsv, scope = private|working|both):
#       both     -> shared roots + native OMP roots for both profiles
#       private  -> private roots (~/.omp/profiles/private/agent/skills, ~/.codex/skills)
#       working  -> working roots (~/.omp/profiles/working/agent/skills, $STACK/codex-working-home/skills)
#     A scoped skill is absent from the other scopes, so omp/Codex never cross.
#   Launch (temporal) — Claude Code has ONE shared root (~/.claude/skills), read
#     by every profile, so it cannot be scoped spatially. `--claude <profile>`
#     rewrites that root in place (mirrors mm-profile-skills-sync): the last
#     launched profile's scoped skills win. OMP receives common skills in its
#     native profile roots, without relying on foreign user-skill discovery.
#     Per-profile roots keep the durable OMP/Codex split.
#
# Idempotent. Foreign (non-managed) skills in target dirs are never touched.
# Conflicts (a real dir or foreign link where a managed link belongs) are
# reported and skipped, not overwritten. Reinstall after a scope change prunes
# the stale durable roots; Claude's launch root is only rewritten by --claude.
#
# Links are recorded in <repo>/.installed-manifest as
# "<skill-name><TAB><target-root>" per line; the uninstaller trusts only that
# manifest. Legacy name-only lines are honored against all roots.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$REPO/.installed-manifest"
PROFILE_MAP="$REPO/tools/profile-map.tsv"
command -v flock >/dev/null || { echo "error: flock is required" >&2; exit 1; }
exec 9>"$MANIFEST.lock"
flock -x 9

SHARED=("$HOME/.claude/skills" "$HOME/.agents/skills")
LAUNCH="$HOME/.claude/skills"   # Claude's single shared root; --claude owns it
STACK="${MM_STACK_DATA_HOME:-${XDG_DATA_HOME:-$HOME/.local/share}/frontend-ai-stack}"
PRIVATE=("$HOME/.omp/profiles/private/agent/skills" "$HOME/.codex/skills")
WORKING=("$HOME/.omp/profiles/working/agent/skills" "${MM_CODEX_WORKING_HOME:-$STACK/codex-working-home}/skills")
ALL_ROOTS=("${SHARED[@]}" "${PRIVATE[@]}" "${WORKING[@]}")
SKILLS_SRC="$REPO/skills"

declare -A SCOPE
if [[ -f "$PROFILE_MAP" ]]; then
  while IFS=$'\t' read -r n s _; do
    [[ -n "${n-}" && ! "${n}" =~ ^# ]] || continue
    [[ -n "${s-}" ]] && SCOPE["$n"]="$s"
  done < "$PROFILE_MAP"
fi
scope_of() { printf '%s' "${SCOPE[$1]:-both}"; }

# Durable roots for a scope (excludes Claude's launch root for scoped skills).
targets_for() {
  case "$(scope_of "$1")" in
    private) printf '%s\n' "${PRIVATE[@]}" ;;
    working) printf '%s\n' "${WORKING[@]}" ;;
    *)       printf '%s\n' "${SHARED[@]}" "${PRIVATE[0]}" "${WORKING[0]}" ;;
  esac
}
# True when `root` is owned by the skill: its durable roots, or — for a scoped
# skill — Claude's launch root (managed only by --claude, left alone here).
in_targets() {
  local r
  [[ "$2" == "$LAUNCH" && "$(scope_of "$1")" != both ]] && return 0
  for r in $(targets_for "$1"); do [[ "$r" == "$2" ]] && return 0; done
  return 1
}
is_requested() { local n; for n in "${requested[@]}"; do [[ "$n" == "$1" ]] && return 0; done; return 1; }

die() { echo "error: $*" >&2; exit 1; }

link_skill() { # $1 = skill dir, $2 = target root
  local src="$1" dst="$2/$(basename "$1")" name; name="$(basename "$1")"
  mkdir -p "$2"
  if [[ -L "$dst" ]]; then
    local cur; cur="$(readlink -f "$dst")"
    if [[ "$cur" == "$src" ]]; then
      printf '%s\t%s\n' "$name" "$2" >> "$MANIFEST_TMP"
      echo "ok      $name -> ${2}  (already linked)"; return 0
    fi
    echo "conflict $name @ ${2}: existing link points to $cur (left alone)"; return 1
  elif [[ -e "$dst" ]]; then
    echo "conflict $name @ ${2}: real directory/file present (left alone)"; return 1
  fi
  ln -s "$src" "$dst"
  printf '%s\t%s\n' "$name" "$2" >> "$MANIFEST_TMP"
  echo "installed $name -> ${2}"
}

prune_skill() { # $1 = name, $2 = target root — drop a managed repo link
  local path="$2/$1" dest
  [[ -L "$path" ]] || return 0
  dest="$(readlink -f "$path")"
  if [[ "$dest" == "$SKILLS_SRC/$1" ]]; then
    rm "$path"
    echo "pruned  $1 <- ${2}"
  fi
  return 0  # foreign links are left alone; absence of work is not failure
}

all_skills() { local d; for d in "$SKILLS_SRC"/*/; do [[ -f "$d/SKILL.md" ]] && basename "${d%/}"; done; }

# --- argument parsing ---
MODE=durable; PROFILE=; requested=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --claude) MODE=launch; PROFILE="${2:-}"; shift 2; [[ "$PROFILE" == private || "$PROFILE" == working ]] || die "--claude needs private|working";;
    *) requested+=("$1"); shift;;
  esac
done

# --- launch mode: rewrite Claude's shared root for one profile, atomically ---
if [[ "$MODE" == launch ]]; then
  [[ ${#requested[@]} -eq 0 ]] || die "--claude takes no skill names (it syncs the whole root)"
  touch "$MANIFEST"
  MANIFEST_TMP=$(mktemp "$MANIFEST.tmp.XXXXXX")
  KEEP_TMP=$(mktemp "$MANIFEST.tmp.keep.XXXXXX")
  LAUNCH_TMP=$(mktemp "$MANIFEST.tmp.launch.XXXXXX")
  trap 'rm -f "$MANIFEST.tmp."*' EXIT
  # Durable rows for other roots survive untouched; the Claude rows rebuild.
  awk -F'\t' -v l="$LAUNCH" '$2!=l' "$MANIFEST" > "$KEEP_TMP"
  MANIFEST_TMP="$LAUNCH_TMP"   # link_skill appends launch rows here
  while IFS= read -r name; do
    sc="$(scope_of "$name")"
    if [[ "$sc" == both || "$sc" == "$PROFILE" ]]; then
      link_skill "$SKILLS_SRC/$name" "$LAUNCH" || exit 1
    else
      prune_skill "$name" "$LAUNCH"
    fi
  done < <(all_skills)
  cat "$LAUNCH_TMP" >> "$KEEP_TMP"
  sort -u "$KEEP_TMP" -o "$KEEP_TMP"
  mv "$KEEP_TMP" "$MANIFEST"
  echo "claude root synced to $PROFILE; durable roots untouched"
  echo "manifest: $MANIFEST"
  exit 0
fi

# --- durable mode ---
if [[ ${#requested[@]} -eq 0 ]]; then
  mapfile -t requested < <(all_skills)
else
  for name in "${requested[@]}"; do
    [[ -f "$SKILLS_SRC/$name/SKILL.md" ]] || die "no such skill: $name (expected skills/$name/SKILL.md)"
  done
fi

rc=0
touch "$MANIFEST"
MANIFEST_TMP=$(mktemp "$MANIFEST.tmp.XXXXXX")
CLEAN_TMP=$(mktemp "$MANIFEST.tmp.clean.XXXXXX")
trap 'rm -f "$MANIFEST.tmp."*' EXIT
cp "$MANIFEST" "$MANIFEST_TMP"
for name in "${requested[@]}"; do
  for root in "${ALL_ROOTS[@]}"; do
    in_targets "$name" "$root" || prune_skill "$name" "$root"
  done
  for tgt in $(targets_for "$name"); do
    link_skill "$SKILLS_SRC/$name" "$tgt" || rc=1
  done
done

# Prune durable manifest rows a scope change orphaned; launch (Claude) rows and
# unrelated skills stay intact.
while IFS=$'\t' read -r name tgt _; do
  [[ -n "${name-}" ]] || continue
  if is_requested "$name"; then in_targets "$name" "${tgt:-}" || continue; fi
  printf '%s\t%s\n' "$name" "${tgt-}"
done < "$MANIFEST_TMP" > "$CLEAN_TMP"
mv "$CLEAN_TMP" "$MANIFEST_TMP"
sort -u "$MANIFEST_TMP" -o "$MANIFEST_TMP"
mv "$MANIFEST_TMP" "$MANIFEST"
echo "manifest: $MANIFEST"
exit $rc
