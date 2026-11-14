#!/usr/bin/env bash
# detect-project.sh — project fingerprint for security auditing.
# Prints: languages, frameworks, package managers/lockfiles, surfaces
# (API/DB/auth/deploy/CI/containers/IaC), existing security tooling & tests,
# trust-boundary hints. Detection-only: installs nothing, mutates nothing.
# Output: key: value lines + JSON block (parseable). Exit 0 ok / 1 bad dir / 2 no perms.
set -uo pipefail

PROJ="${1:-.}"
case "${1:-}" in -h|--help)
  sed -n '2,8p' "$0"; exit 0;;
esac
[[ -d "$PROJ" ]] || { echo "error: not a directory: $PROJ" >&2; exit 1; }
PROJ="$(cd "$PROJ" && pwd)" || { echo "error: cannot resolve $PROJ" >&2; exit 2; }

# bounded, ignore-virtuous listing (skip vendored/VCS noise early)
list_files() {
  find "$PROJ" \( -name node_modules -o -name .git -o -name dist -o -name build \
     -o -name .venv -o -name venv -o -name target -o -name vendor -o -name __pycache__ \) -prune \
     -o -type f -print 2>/dev/null | head -20000
}
ALL="$(list_files)"
has()  { grep -qxF "$1" <<<"$ALL"; }            # exact relpath-exists helper
has_re() { grep -qE "$1" <<<"$ALL"; }
count_ext() { grep -cE "\.$1\$" <<<"$ALL" || true; }

say() { printf '%s\n' "$*"; }
say "# project-detection v1  $(date -u +%FT%TZ)"
say "root: $PROJ"

# ---------- languages ----------
lang=""
addl() { lang="${lang:+$lang }$1"; }
[[ "$(count_ext py)" -gt 0 ]]   && addl "python:$(count_ext py)"
[[ "$(count_ext js)" -gt 0 ]]   && addl "javascript:$(count_ext js)"
[[ "$(count_ext ts)" -gt 0 || "$(count_ext tsx)" -gt 0 ]] && addl "typescript:$(($(count_ext ts)+$(count_ext tsx)))"
[[ "$(count_ext go)" -gt 0 ]]   && addl "go:$(count_ext go)"
[[ "$(count_ext rs)" -gt 0 ]]   && addl "rust:$(count_ext rs)"
[[ "$(count_ext php)" -gt 0 ]]  && addl "php:$(count_ext php)"
[[ "$(count_ext java)" -gt 0 ]] && addl "java:$(count_ext java)"
[[ "$(count_ext rb)" -gt 0 ]]   && addl "ruby:$(count_ext rb)"
[[ "$(count_ext cs)" -gt 0 ]]   && addl "csharp:$(count_ext cs)"
say "languages: ${lang:-none-detected}"

# ---------- stack manifests ----------
manifests=""
addm() { manifests="${manifests:+$manifests }$1"; }
for f in package.json pnpm-lock.yaml package-lock.json yarn.lock \
         requirements.txt pyproject.toml uv.lock poetry.lock Pipfile.lock \
         Cargo.lock Cargo.toml go.mod go.sum composer.json composer.lock \
         Gemfile.lock *.csproj packages.config pubspec.yaml build.gradle pom.xml; do
  has_re "(^|/)${f}\$" && addm "$f"
done
say "manifests: ${manifests:-none}"

# ---------- frameworks (manifest-gated, cheap greps) ----------
fw=""
addfw() { fw="${fw:+$fw }$1"; }
pj() { has_re "(^|/)package\.json\$" && head -c 200000 "$(grep -m1 -E '(^|/)package.json$' <<<"$ALL" | head -1)" 2>/dev/null; }
PJ_CONTENT="$(pj)"
grep -q '"next"'           <<<"$PJ_CONTENT" && addfw nextjs
grep -q '"astro"'          <<<"$PJ_CONTENT" && addfw astro
grep -q '"react"'          <<<"$PJ_CONTENT" && addfw react
grep -q '"nuxt"'           <<<"$PJ_CONTENT" && addfw nuxt
grep -q '"vue"'            <<<"$PJ_CONTENT" && addfw vue
grep -q '"svelte"'         <<<"$PJ_CONTENT" && addfw svelte
grep -q '"@nestjs/core"'   <<<"$PJ_CONTENT" && addfw nestjs
grep -q '"express"'        <<<"$PJ_CONTENT" && addfw express
grep -q '"fastify"'        <<<"$PJ_CONTENT" && addfw fastify
has_re "(^|/)manage.py$"            && addfw django
grep -rlq "FastAPI" --include=py -m1 "$PROJ" 2>/dev/null | grep -q . && addfw fastapi
grep -rlq "actix_web\|axum" --include=*.rs -m1 "$PROJ" 2>/dev/null | grep -q . && addfw "rust-web"
say "frameworks: ${fw:-none-detected}"

# ---------- surfaces ----------
api="no"; has_re "(^|/)(api|routes|controllers)/" && api=yes
grep -rlqE "app\.(get|post)\(|@app\.(get|post)|Router\(|router\.(get|post)" --include='*.{js,ts,py,go,php}' -m1 "$PROJ" 2>/dev/null | grep -q . && api=yes
db="none"
grep -rlqiE "postgres|psycopg|pg-pool|PrismaClient|sequelize|typeorm|knex|SQLAlchemy|Django.*DATABASES" --include='*.{js,ts,py,json,toml}' -m1 "$PROJ" 2>/dev/null | grep -q . && db="sql"
grep -rlqiE "mysql|mariadb" --include='*.{js,ts,py,toml}' -m1 "$PROJ" 2>/dev/null | grep -q . && db="${db}+mysql"
has_re "(^|/)[^/]*\.sqlite3?$|(^|/)db\.sqlite" && db="${db}+sqlite"
grep -rlqiE "mongoose|mongodb" --include='*.{js,ts}' -m1 "$PROJ" 2>/dev/null | grep -q . && db="${db}+mongo"
grep -rlqiE "redis|ioredis" --include='*.{js,ts,py}' -m1 "$PROJ" 2>/dev/null | grep -q . && db="${db}+redis"
auth="no"
grep -rlqiE "passport|jsonwebtoken|jwt|session|login|oauth|authlib|django.contrib.auth" --include='*.{js,ts,py}' -m1 "$PROJ" 2>/dev/null | grep -q . && auth=yes
say "surface: api=$api db=$db auth=$auth"

# ---------- deploy / CI / containers / IaC ----------
infra=""
addi() { infra="${infra:+$infra }$1"; }
has_re "(^|/)Dockerfile" && addi docker
has_re "(^|/)docker-compose\.(yml|yaml)$|(^|/)compose\.(yml|yaml)$" && addi compose
has_re "(^|/)\.github/workflows/.*\.ya?ml$" && addi github-actions
has_re "(^|/)\.gitlab-ci\.yml$" && addi gitlab-ci
has_re "(^|/)(k8s|kubernetes)/.*\.ya?ml$|(^|/)Chart\.yaml$" && addi kubernetes
has_re "\.tf$" && addi terraform
has_re "(^|/)(nginx\.conf|Caddyfile|traefik\.(yml|toml))$" && addi proxy
say "infra: ${infra:-none-detected}"

# ---------- tests + existing security tooling ----------
tests="none"
has_re "(^|/)(tests?|__tests__|spec)/" && tests=dirs
grep -qE "vitest|jest" <<<"$PJ_CONTENT" && tests="${tests}+jest/vitest"
grep -rlq "pytest\|def test_" --include='*.py' -m1 "$PROJ" 2>/dev/null | grep -q . && tests="${tests}+pytest"
has_re "(^|/)playwright\.config\.(ts|js)$" && tests="${tests}+playwright"
sectools="none"
for f in .gitleaks.toml .semgrep.yml semgrep .snyk zap .trivyignore bandit; do
  has_re "(^|/)${f}" && sectools="${sectools/none/}+$f"
done
say "tests: ${tests# } | existing-security-tooling: ${sectools:-none}"

# ---------- secrets-adjacent config surface (trust boundary notes) ----------
envfiles="$(grep -E '(^|/)\.env' <<<"$ALL" | sed "s|^$PROJ/||" | tr '\n' ' ')"
say "env-files: ${envfiles:-none}"
say "trust-boundaries-hint: browser<->api=$([[ $api == yes ]] && echo yes || echo n/a) user-content<->renderer=$([[ -n $fw ]] && echo likely n/a-check-stacks) ci<->repo=$([[ $infra == *github* || $infra == *gitlab* ]] && echo yes || echo n/a) deps<->build=$( [[ -n $manifests ]] && echo yes || echo n/a)"

# ---------- machine block ----------
say "json:"
{ printf '{\n  "root": "%s",\n  "languages": "%s",\n  "manifests": "%s",\n  "frameworks": "%s",\n  "api": "%s",\n  "db": "%s",\n  "auth": "%s",\n  "infra": "%s",\n  "tests": "%s",\n  "env_files": "%s"\n}\n' \
  "$PROJ" "$lang" "$manifests" "$fw" "$api" "$db" "$auth" "$infra" "$tests" "$envfiles"; }
