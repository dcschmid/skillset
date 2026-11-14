#!/usr/bin/env bash
# check-versions.sh — read-only React/Next.js version census.
# Prints installed vs latest-stable and feature-floor verdicts for a project.
# Never modifies anything. Exit 0 always (unless no project given/exists).
# Usage: bash scripts/check-versions.sh [project_dir]  (default: cwd)
set -u
root="${1:-$(pwd)}"
[ -d "$root" ] || { echo "not a directory: $root" >&2; exit 1; }
cd "$root"

jget() { node -p "try{require('./node_modules/$1/package.json').version}catch(e){'ABSENT'}" 2>/dev/null || echo "no-node"; }
dget() { grep -oE "\"$1\": *\"[^\"]+\"" package.json 2>/dev/null | head -1 | sed 's/.*: *"//;s/"//'; }

echo "project: $root"
for p in react react-dom next typescript; do
  echo "$p: installed=$(jget "$p") declared=$(dget "$p")"
done
[ -f package.json ] || echo "note: no package.json (not a JS project root?)"

lock=none
[ -f pnpm-lock.yaml ] && lock=pnpm
[ -f yarn.lock ] && lock=yarn
[ -f bun.lockb ] || [ -f bun.lock ] && lock=bun
[ -f package-lock.json ] && lock=npm
echo "package-manager: $lock"

if [ -d node_modules/next/dist/docs ]; then
  echo "next-local-docs: present ($(find node_modules/next/dist/docs -name '*.md' | wc -l | tr -d ' ') files) — AUTHORITATIVE for this version"
else
  echo "next-local-docs: absent (no next installed or old layout)"
fi

echo "app-router: $([ -d app ] || [ -d src/app ] && echo yes || echo no)  pages-router: $([ -d pages ] || [ -d src/pages ] && echo yes || echo no)"
echo "proxy.ts: $(find . -maxdepth 2 -name 'proxy.ts' -not -path './node_modules/*' 2>/dev/null | head -1 | grep -q . && echo present || echo absent)  middleware.ts: $(find . -maxdepth 2 -name 'middleware.ts' -not -path './node_modules/*' 2>/dev/null | head -1 | grep -q . && echo present || echo absent)"

echo "--- latest stable (network) ---"
for p in react next typescript; do
  printf '%s latest: %s\n' "$p" "$(npm view "$p" version 2>/dev/null || echo offline)"
done
echo "floors: react19=use/useActionState/useOptimistic/useFormStatus/useEffectEvent; 19.2=Activity/ViewTransition/addTransitionType; next16=proxy.ts/cacheComponents/use-cache/updateTag"
