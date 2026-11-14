#!/usr/bin/env bash
# test_installer.sh — installer/uninstaller behavior tests.
# Uses an isolated TEST_HOME so the real ~/.claude and ~/.agents are untouched.
#   TEST_HOME=$(mktemp -d) bash tools/test_installer.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
: "${TEST_HOME:?set TEST_HOME to a scratch dir}"
TEST_REPO=$(mktemp -d)
trap 'rm -rf "$TEST_REPO"' EXIT
mkdir -p "$TEST_REPO/tools" "$TEST_REPO/skills"
cp "$REPO/tools/install-skills.sh" "$REPO/tools/uninstall-skills.sh" "$TEST_REPO/tools/"
for name in lowpoly-reference-to-blender human-writing; do
  mkdir -p "$TEST_REPO/skills/$name"
  printf '%s\n' 'fixture' > "$TEST_REPO/skills/$name/SKILL.md"
done
REPO="$TEST_REPO"
export HOME="$TEST_HOME"
CLAUDE="$HOME/.claude/skills"
CODEX="$HOME/.agents/skills"
SKILL=lowpoly-reference-to-blender
SECOND=human-writing
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
t "install.manifest"     "awk -F'\\t' -v n='$SKILL' '\$1==n' '$MANIFEST' | grep -q ."

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

# 6. per-skill install: only the named skill is linked and recorded
clean
bash "$REPO/tools/install-skills.sh" "$SKILL" >/dev/null 2>&1
t "single.links_named_claude"  '[ -L "$CLAUDE/$SKILL" ]'
t "single.links_named_codex"   '[ -L "$CODEX/$SKILL" ]'
t "single.skips_others"        '[ ! -e "$CLAUDE/$SECOND" ] && [ ! -e "$CODEX/$SECOND" ]'
t "single.manifest_targeted"   "! awk -F'\\t' -v n='$SECOND' '\$1==n' '$MANIFEST' | grep -q . && awk -F'\\t' -v n='$SKILL' '\$1==n && NF>1' '$MANIFEST' | grep -q ."

# 7. per-skill uninstall: named skill gone, other manifest entries survive
bash "$REPO/tools/install-skills.sh" "$SECOND" >/dev/null 2>&1
bash "$REPO/tools/uninstall-skills.sh" "$SKILL" >/dev/null 2>&1
t "single.uninstall_named"     '[ ! -e "$CLAUDE/'"$SKILL"'" ] && [ ! -e "$CODEX/'"$SKILL"'" ]'
t "single.keeps_other"         '[ -L "$CLAUDE/'"$SECOND"'" ] && awk -F"\t" -v n="$SECOND" "\$1==n" "$MANIFEST" | grep -q .'
t "single.unnamed_gone_from_manifest" "! awk -F'\\t' -v n='$SKILL' '\$1==n' '$MANIFEST' | grep -q ."

# 8. unknown skill name aborts before touching anything
clean
out=$(bash "$REPO/tools/install-skills.sh" no-such-skill 2>&1); rc=$?
t "unknown.aborts"         "[ $rc -ne 0 ] && printf '%s' \"\$out\" | grep -q 'no such skill'"
t "unknown.nothing_linked" '[ ! -e "$CLAUDE/'"$SKILL"'" ] && [ ! -e "$CODEX/'"$SKILL"'" ]'

# 9. legacy manifest (name-only lines) is still understood by uninstall
clean
bash "$REPO/tools/install-skills.sh" "$SKILL" >/dev/null 2>&1
cut -f1 "$MANIFEST" | sort -u > "$MANIFEST.tmp" && mv "$MANIFEST.tmp" "$MANIFEST"
bash "$REPO/tools/uninstall-skills.sh" >/dev/null 2>&1
t "legacy.uninstall_works" '[ ! -e "$CLAUDE/'"$SKILL"'" ] && [ ! -e "$CODEX/'"$SKILL"'" ] && [ ! -f "$MANIFEST" ]'

# 10. concurrent installers retain both skills and a valid manifest.
clean
bash "$REPO/tools/install-skills.sh" "$SKILL" >/dev/null 2>&1 &
pid_first=$!
bash "$REPO/tools/install-skills.sh" "$SECOND" >/dev/null 2>&1 &
pid_second=$!
wait "$pid_first"; first_rc=$?
wait "$pid_second"; second_rc=$?
t "parallel.install_success" "[ $first_rc -eq 0 ] && [ $second_rc -eq 0 ]"
t "parallel.manifest_complete" '[ "$(wc -l < "$MANIFEST")" -eq 4 ]'
t "parallel.links_complete" '[ -L "$CLAUDE/$SKILL" ] && [ -L "$CODEX/$SECOND" ]'
# The same lock must also serialize uninstall with install.
bash "$REPO/tools/uninstall-skills.sh" "$SKILL" >/dev/null 2>&1 &
pid_first=$!
bash "$REPO/tools/install-skills.sh" "$SECOND" >/dev/null 2>&1 &
pid_second=$!
wait "$pid_first"; first_rc=$?
wait "$pid_second"; second_rc=$?
t "parallel.mixed_success" "[ $first_rc -eq 0 ] && [ $second_rc -eq 0 ]"
t "parallel.mixed_manifest" '[ "$(wc -l < "$MANIFEST")" -eq 2 ] && [ ! -L "$CLAUDE/$SKILL" ] && [ -L "$CODEX/$SECOND" ]'
t "parallel.no_temp_left" '! compgen -G "$MANIFEST.tmp.*" >/dev/null'

rm -rf "$FOREIGN"
echo "== installer tests: $pass pass, $fail fail"
[ "$fail" -eq 0 ]
