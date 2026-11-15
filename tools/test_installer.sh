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
# Test-local routing map: two fixture skills exercise private/working scope;
# the fixtures below stay unlisted (scope=both) so shared-root tests hold.
printf 'priv-skill\tprivate\nwork-skill\tworking\n' > "$TEST_REPO/tools/profile-map.tsv"
for name in lowpoly-reference-to-blender human-writing priv-skill work-skill; do
  mkdir -p "$TEST_REPO/skills/$name"
  printf '%s\n' 'fixture' > "$TEST_REPO/skills/$name/SKILL.md"
done
REPO="$TEST_REPO"
export HOME="$TEST_HOME"
CLAUDE="$HOME/.claude/skills"
CODEX="$HOME/.agents/skills"
PP="$HOME/.omp/profiles/private/agent/skills"
PW="$HOME/.omp/profiles/working/agent/skills"
CX="$HOME/.codex/skills"
CW="$HOME/.local/share/frontend-ai-stack/codex-working-home/skills"
SKILL=lowpoly-reference-to-blender
SECOND=human-writing
PRIV=priv-skill
WORK=work-skill
MANIFEST="$REPO/.installed-manifest"
FOREIGN=/tmp/foreign-elsewhere-$$

pass=0; fail=0
t() { # name, command-string
  if eval "$2"; then echo "PASS $1"; pass=$((pass+1));
  else echo "FAIL $1"; fail=$((fail+1)); fi
}
clean() {
  rm -rf "$HOME/.claude" "$HOME/.agents" "$HOME/.codex" "$HOME/.omp" \
         "$HOME/.local/share/frontend-ai-stack" "$MANIFEST"
}

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
t "uninstall.removes_omp" '[ ! -L "$PP/$SKILL" ] && [ ! -L "$PW/$SKILL" ]'
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
t "parallel.manifest_complete" '[ "$(wc -l < "$MANIFEST")" -eq 8 ]'
t "parallel.links_complete" '[ -L "$CLAUDE/$SKILL" ] && [ -L "$CODEX/$SECOND" ]'
# The same lock must also serialize uninstall with install.
bash "$REPO/tools/uninstall-skills.sh" "$SKILL" >/dev/null 2>&1 &
pid_first=$!
bash "$REPO/tools/install-skills.sh" "$SECOND" >/dev/null 2>&1 &
pid_second=$!
wait "$pid_first"; first_rc=$?
wait "$pid_second"; second_rc=$?
t "parallel.mixed_success" "[ $first_rc -eq 0 ] && [ $second_rc -eq 0 ]"
t "parallel.mixed_manifest" '[ "$(wc -l < "$MANIFEST")" -eq 4 ] && [ ! -L "$CLAUDE/$SKILL" ] && [ -L "$CODEX/$SECOND" ]'
t "parallel.no_temp_left" '! compgen -G "$MANIFEST.tmp.*" >/dev/null'

# 11. EXCLUSIVE routing: a scoped skill lives only in its own profile roots —
#     absent from shared roots and from the other profile, so omp profiles and
#     Codex homes never cross the private/working boundary.
clean
bash "$REPO/tools/install-skills.sh" >/dev/null 2>&1
t "route.private_omp"      '[ -L "$PP/$PRIV" ]'
t "route.private_codex"    '[ -L "$CX/$PRIV" ]'
t "route.private_absent_shared" '[ ! -e "$CLAUDE/'"$PRIV"'" ] && [ ! -e "$CODEX/'"$PRIV"'" ]'
t "route.private_not_working" '[ ! -e "$PW/'"$PRIV"'" ] && [ ! -e "$CW/'"$PRIV"'" ]'
t "route.working_omp"      '[ -L "$PW/$WORK" ]'
t "route.working_codex"    '[ -L "$CW/$WORK" ]'
t "route.working_absent_shared" '[ ! -e "$CLAUDE/'"$WORK"'" ] && [ ! -e "$CODEX/'"$WORK"'" ]'
t "route.working_not_private" '[ ! -e "$PP/'"$WORK"'" ] && [ ! -e "$CX/'"$WORK"'" ]'
t "route.both_shared_and_omp" '[ -L "$CLAUDE/$SKILL" ] && [ -L "$CODEX/$SKILL" ] && [ -L "$PP/'"$SKILL"'" ] && [ -L "$PW/'"$SKILL"'" ]'
t "route.manifest_scoped"  "awk -F'\\t' -v n='$PRIV' '\$1==n' '$MANIFEST' | grep -q 'omp/profiles/private' && ! awk -F'\\t' -v n='$PRIV' '\$1==n' '$MANIFEST' | grep -q '.claude'"

# 12. scope change prunes the old profile root on reinstall (private -> working).
clean
bash "$REPO/tools/install-skills.sh" "$PRIV" >/dev/null 2>&1
printf 'priv-skill\tworking\nwork-skill\tworking\n' > "$REPO/tools/profile-map.tsv"
bash "$REPO/tools/install-skills.sh" "$PRIV" >/dev/null 2>&1
t "rescope.linked_new"     '[ -L "$PW/'"$PRIV"'" ] && [ -L "$CW/'"$PRIV"'" ]'
t "rescope.pruned_old"     '[ ! -e "$PP/'"$PRIV"'" ] && [ ! -e "$CX/'"$PRIV"'" ]'
t "rescope.shared_absent"  '[ ! -e "$CLAUDE/'"$PRIV"'" ] && [ ! -e "$CODEX/'"$PRIV"'" ]'
t "rescope.manifest_clean" "! awk -F'\\t' -v n='$PRIV' '\$1==n' '$MANIFEST' | grep -q 'omp/profiles/private'"

# 13. uninstall clears every root the skill was ever linked into.
clean
bash "$REPO/tools/install-skills.sh" >/dev/null 2>&1
bash "$REPO/tools/uninstall-skills.sh" "$PRIV" >/dev/null 2>&1
t "uninstall.private_roots" '[ ! -e "$PP/'"$PRIV"'" ] && [ ! -e "$CX/'"$PRIV"'" ]'
t "uninstall.other_intact"  '[ -L "$PW/'"$WORK"'" ] && [ -L "$CLAUDE/$SKILL" ]'

# 14. launch-sync (--claude <profile>): Claude's shared root is rewritten to the
#     last-launched profile; durable (omp/Codex) roots stay exclusive.
clean
printf 'priv-skill\tprivate\nwork-skill\tworking\n' > "$REPO/tools/profile-map.tsv"
bash "$REPO/tools/install-skills.sh" >/dev/null 2>&1          # durable base
bash "$REPO/tools/install-skills.sh" --claude private >/dev/null 2>&1; rc=$?
t "claude_sync.private_exit" "[ $rc -eq 0 ]"
t "claude_sync.private_here" '[ -L "$CLAUDE/$PRIV" ]'           # private scoped lands in Claude root
t "claude_sync.working_gone" '[ ! -e "$CLAUDE/'"$WORK"'" ]'      # working scoped absent
t "claude_sync.both_stay"    '[ -L "$CLAUDE/$SKILL" ]'           # both always present
t "claude_sync.durable_intact" '[ -L "$PP/$PRIV" ] && [ -L "$PW/$WORK" ] && [ ! -e "$PW/'"$PRIV"'" ]'
t "claude_sync.manifest_records" "awk -F'\\t' -v n='$PRIV' -v l='$CLAUDE' '\$1==n && \$2==l' '$MANIFEST' | grep -q ."
bash "$REPO/tools/install-skills.sh" --claude working >/dev/null 2>&1
t "claude_sync.relaunch_working" '[ -L "$CLAUDE/$WORK" ] && [ ! -e "$CLAUDE/'"$PRIV"'" ] && [ -L "$CLAUDE/$SKILL" ]'
t "claude_sync.durable_still_exclusive" '[ -L "$PP/$PRIV" ] && [ ! -e "$PP/'"$WORK"'" ]'
t "claude_sync.manifest_rewritten" "! awk -F'\\t' -v n='$PRIV' -v l='$CLAUDE' '\$1==n && \$2==l' '$MANIFEST' | grep -q ."
t "claude_sync.no_names_accepted" 'bash "$REPO/tools/install-skills.sh" --claude private '"$SKILL"' >/dev/null 2>&1; [ $? -ne 0 ] && true'

rm -rf "$FOREIGN"
echo "== installer tests: $pass pass, $fail fail"
[ "$fail" -eq 0 ]
