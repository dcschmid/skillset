#!/usr/bin/env bash
# test_installer.sh — installer/uninstaller behavior tests.
# Uses an isolated TEST_HOME so the real ~/.claude and ~/.agents are untouched.
#   TEST_HOME=$(mktemp -d) bash tools/test_installer.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
: "${TEST_HOME:?set TEST_HOME to a scratch dir}"
export HOME="$TEST_HOME"
CLAUDE="$HOME/.claude/skills"
CODEX="$HOME/.agents/skills"
SKILL=lowpoly-reference-to-blender
MANIFEST="$REPO/.installed-manifest"
FOREIGN=/tmp/foreign-elsewhere-$$

pass=0; fail=0
t() { # name, command-string
  if eval "$2"; then echo "PASS $1"; pass=$((pass+1));
  else echo "FAIL $1"; fail=$((fail+1)); fi
}
clean() { rm -rf "$HOME/.claude" "$HOME/.agents" "$MANIFEST"; }

# 1. fresh install links the skill into both agents + writes manifest
clean
bash "$REPO/tools/install-skills.sh" >/dev/null 2>&1
t "install.links_claude" '[ -L "$CLAUDE/$SKILL" ]'
t "install.links_codex"  '[ -L "$CODEX/$SKILL" ]'
t "install.manifest"     "grep -qx $SKILL '$MANIFEST'"

# 2. idempotent: rerun keeps links, exit 0, manifest has no dupes
bash "$REPO/tools/install-skills.sh" >/dev/null 2>&1; rc=$?
t "install.idempotent"   "[ $rc -eq 0 ] && [ -L '$CLAUDE/$SKILL' ]"
t "install.manifest_unique" "[ \$(sort -u '$MANIFEST' | wc -l) = \$(wc -l < '$MANIFEST') ]"

# 3. foreign real directory with the skill's name survives install untouched
rm -rf "$CLAUDE/$SKILL"
mkdir -p "$CLAUDE/$SKILL"
printf 'foreign\n' > "$CLAUDE/$SKILL/SKILL.md"
bash "$REPO/tools/install-skills.sh" >/dev/null 2>&1 || true
t "protect.foreign_dir" "grep -q foreign '$CLAUDE/$SKILL/SKILL.md'"

# 4. foreign symlink is left alone and the conflict is reported
rm -rf "$CLAUDE/$SKILL"; mkdir -p "$FOREIGN"
ln -sfn "$FOREIGN" "$CLAUDE/$SKILL"
out=$(bash "$REPO/tools/install-skills.sh" 2>&1) || true
t "protect.foreign_link" "[ \"\$(readlink -f '$CLAUDE/$SKILL')\" = '$FOREIGN' ]"
t "conflict.reported"    "printf '%s' \"\$out\" | grep -q conflict"

# 5. uninstall removes only managed links; foreign files/links survive
clean
bash "$REPO/tools/install-skills.sh" >/dev/null 2>&1
mkdir -p "$CLAUDE/unrelated-skill"
ln -sfn "$FOREIGN" "$CODEX/$SKILL"   # make codex copy foreign on purpose
bash "$REPO/tools/uninstall-skills.sh" >/dev/null 2>&1
t "uninstall.removes_claude" '[ ! -e "$CLAUDE/'"$SKILL"'" ]'
t "uninstall.keeps_foreign_codex" "[ \"\$(readlink -f '$CODEX/$SKILL')\" = '$FOREIGN' ]"
t "uninstall.keeps_foreign_dir"   '[ -d "$CLAUDE/unrelated-skill" ]'
t "uninstall.clears_manifest"     "[ ! -f '$MANIFEST' ]"

rm -rf "$FOREIGN"
echo "== installer tests: $pass pass, $fail fail"
[ "$fail" -eq 0 ]
