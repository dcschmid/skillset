#!/usr/bin/env bash
# detect-project.sh — backend architecture profile (read-only, no installs).
# Prints key: value lines: languages+versions, frameworks, package managers,
# runtimes, API surfaces+specs, DB engines+ORMs+migration tools, auth libs,
# jobs/queues, deploy/CI, test runners, config layout, risk hints, project
# class guess. Exit: 0 ok · 1 not a directory · 2 unreadable.
set -uo pipefail
PROJ="${1:-.}"
case "${1:-}" in -h|--help) sed -n '2,7p' "$0"; exit 0;; esac
[[ -d "$PROJ" ]] || { echo "error: not a directory: $PROJ" >&2; exit 1; }
PROJ="$(cd "$PROJ" && pwd)" || { echo "error: cannot read $PROJ" >&2; exit 2; }

FILES="$(find "$PROJ" \( -name node_modules -o -name .git -o -name dist -o -name build \
  -o -name .venv -o -name venv -o -name target -o -name vendor -o -name __pycache__ \
  -o -name .next -o -name .venv-* \) -prune -o -type f -print 2>/dev/null | head -30000)"
say(){ printf '%s\n' "$*"; }
has(){ grep -qxF "$1" <<<"$FILES"; }
hasre(){ grep -qE "$1" <<<"$FILES"; }
cnt(){ grep -cE "$1" <<<"$FILES" || true; }
names(){ grep -E "$1" <<<"$FILES" | sed "s|^$PROJ/||" | head -12 | tr '\n' ' '; }

say "# backend-profile v1  $(date -u +%FT%TZ)"
say "root: $PROJ"

# languages + version pins
L=""
add(){ L="${L:+$L }$1"; }
[[ "$(cnt '\.py$')" -gt 0 ]] && add "python:$(cnt '\.py$')"
[[ "$(cnt '\.ts$')"  -gt 0 ]] && add "typescript:$(cnt '\.ts$')"
[[ "$(cnt '\.tsx?$')" -gt 0 || "$(cnt '\.js$')" -gt 0 ]] && add "javascript:$(($(cnt '\.js$')+$(cnt '\.jsx$')))"
[[ "$(cnt '\.go$')" -gt 0 ]] && add "go:$(cnt '\.go$')"
[[ "$(cnt '\.rs$')" -gt 0 ]] && add "rust:$(cnt '\.rs$')"
[[ "$(cnt '\.php$')" -gt 0 ]] && add "php:$(cnt '\.php$')"
[[ "$(cnt '\.java$')" -gt 0 ]] && add "java:$(cnt '\.java$')"
[[ "$(cnt '\.kt$')" -gt 0 ]] && add "kotlin:$(cnt '\.kt$')"
[[ "$(cnt '\.cs$')" -gt 0 ]] && add "csharp:$(cnt '\.cs$')"
[[ "$(cnt '\.rb$')" -gt 0 ]] && add "ruby:$(cnt '\.rb$')"
say "languages: ${L:-none-detected}"
for f in .python-version runtime.txt .nvmrc .node-version go.mod Cargo.toml global.json; do
  has "$PROJ/$f" || hasre "/$f\$" && say "runtime-pin: $(grep -m1 -E '[0-9]+\.[0-9]+' "$PROJ/${f}" 2>/dev/null | head -1 | tr -d '\n') ($f)"
done

# manifests / package managers
M=""
for f in package.json pnpm-lock.yaml package-lock.json yarn.lock bun.lockb \
         pyproject.toml requirements.txt uv.lock poetry.lock Pipfile.lock \
         go.mod go.sum Cargo.lock composer.json composer.lock pom.xml build.gradle \
         Gemfile mix.exs *.csproj; do
  hasre "/$(basename "$f")\$" && M="${M:+$M }$(basename "$f")"
done
say "manifests: ${M:-none}"

# frameworks (manifest-content probes, per found manifest)
FW=""
pj() { find "$PROJ" -maxdepth 3 -name package.json -not -path '*/node_modules/*' 2>/dev/null | head -20; }
for f in $(pj); do
  grep -qE '"(fastify|nestjs|@nestjs/)' "$f" 2>/dev/null && FW="${FW:+$FW }node:fastify-or-nest"
  grep -q '"express"' "$f" 2>/dev/null && FW="${FW:+$FW }node:express"
  grep -q '"hono"' "$f" 2>/dev/null && FW="${FW:+$FW }node:hono"
  grep -qE '"(next|@next/)' "$f" 2>/dev/null && FW="${FW:+$FW }node:nextjs"
  grep -qE '"(astro|@astrojs/)' "$f" 2>/dev/null && FW="${FW:+$FW }node:astro"
  grep -q '"@prisma/' "$f" 2>/dev/null && FW="${FW:+$FW }orm:prisma"
  grep -q '"drizzle-orm"' "$f" 2>/dev/null && FW="${FW:+$FW }orm:drizzle"
  grep -qE '"(typeorm|sequelize|knex|socket.io|ioredis|bullmq|amqplib|kafkajs|@grpc/)' "$f" 2>/dev/null \
    && FW="${FW:+$FW }node:$(grep -oE '"(typeorm|sequelize|knex|socket\.io|ioredis|bullmq|amqplib|kafkajs|@grpc/[a-z-]+)"' "$f" | tr -d '"' | tr '\n' ',')"
done
for f in $(find "$PROJ" -maxdepth 3 -name pyproject.toml -not -path '*/.venv/*' 2>/dev/null | head -8); do
  grep -qiE 'fastapi' "$f" && FW="${FW:+$FW }py:fastapi"
  grep -qiE 'django|\bdrf\b|djangorestframework' "$f" && FW="${FW:+$FW }py:django"
  grep -qiE '\bflask\b|sqlalchemy|alembic|celery|redis|litestar' "$f" \
    && FW="${FW:+$FW }py:$(grep -oiE '(flask|sqlalchemy|alembic|celery|redis|litestar)' "$f" | sort -u | tr '\n' ',')"
done
hasre "go.mod$" && FW="${FW:+$FW }go:$(grep -hoE '(gin-gonic/gin|go-chi/chi|labstack/echo|gofiber/fiber|grpc/grpc-go)[^"]*' $(grep -l go.mod <<<"$FILES" | head -3) 2>/dev/null | sort -u | head -4 | tr '\n' ',')"
hasre "Cargo.toml$" && FW="${FW:+$FW }rust:$(grep -hoE '(axum|actix-web|tonic|sqlx|diesel|sea-orm)' $(grep -l Cargo.toml <<<"$FILES" | head -3) 2>/dev/null | sort -u | tr '\n' ',')"
hasre "pom.xml|build.gradle" && grep -rlE 'spring-boot|ktor' $(grep -E 'pom.xml|build.gradle' <<<"$FILES" | head -5) >/dev/null 2>&1 && FW="${FW:+$FW }jvm:spring-or-ktor"
for f in $(grep -lE '<Project|\.csproj$' <<<"$FILES" | head -3); do grep -qi 'Microsoft.AspNetCore' "$f" && FW="${FW:+$FW }dotnet:aspnetcore"; done
for f in $(grep -l 'composer.json' <<<"$FILES" | head -2); do
  grep -q 'laravel/framework' "$f" 2>/dev/null && FW="${FW:+$FW }php:laravel"
  grep -q 'symfony/' "$f" 2>/dev/null && FW="${FW:+$FW }php:symfony"
done
[[ -f "$PROJ/composer.json" ]] && { grep -q 'laravel/framework' "$PROJ/composer.json" && FW="${FW:+$FW }php:laravel"; }
say "frameworks: ${FW:-none-detected}"

# API surfaces
A=""
hasre 'openapi.*(ya?ml|json)$|swagger\.(ya?ml|json)$' && A="${A:+$A }spec:$(names 'openapi.*\.(ya?ml|json)$|swagger\.(ya?ml|json)$')"
hasre '\.proto$' && A="${A:+$A }grpc:$(names '\.proto$')"
hasre 'schema\.graphqls?$|\.gql$' && A="${A:+$A }graphql:$(names 'schema\.graphqls?$|\.gql$')"
grep -qiE 'FastRoute|Router\(|@app\.(get|post)|router\.(get|post)|app\.(Get|Post)|@Get\(|Route::(get|post)' $(grep -E '\.(go|py|php|rb|java|kt|cs|ts|js)$' <<<"$FILES" | head -400) 2>/dev/null && A="${A:+$A }http-routes:detected"
grep -rqlE 'WebSocket|socket\.io|ws://|wss://|EventSource|text/event-stream' $(grep -E '\.(go|py|rs|php|rb|java|kt|cs|ts|js)$' <<<"$FILES" | head -400) 2>/dev/null && A="${A:+$A }realtime:ws/sse-hint"
say "api: ${A:-none-detected}"

# datastores / ORMs / migrations
D=""
grep -qiE 'postgres|psycopg|pgx|node-postgres|postgres-go' <<<"$M $(grep -rli 'postgres' $(grep -E '(requirements|pyproject|package\.json|go\.mod|Cargo\.toml)$' <<<"$FILES" | head -10) 2>/dev/null)" && D="${D:+$D }db:postgres"
grep -qiE 'mysql|maria' <<<"$M" && D="${D:+$D }db:mysql"
hasre '\.sqlite3?$|\.db$' && D="${D:+$D }db:sqlite"
grep -qiE 'mongo|pymongo|mongoose' <<<"$FW $M" && D="${D:+$D }db:mongo"
grep -qiE 'redis|ioredis' <<<"$FW" && D="${D:+$D }store:redis"
grep -qiE 'elasticsearch|meilisearch|typesense|qdrant|pinecone|pgvector|weaviate' <<<"$M" && D="${D:+$D }search/vector:hint"
grep -qiE 'prisma|drizzle|typeorm|sequelize|sqlalchemy|django|alembic|knex|gorm|sqlx|diesel|sea-orm|entity-framework|ef core|hibernate|mybatis|activerecord|eloquent|goose|sqlc' <<<"$FW $M" && D="${D:+$D }orm:$(echo "${FW:-none}")"
MIG=""
hasre 'migrations/|alembic/versions/|db/migrate|/migrations' && MIG="$(names 'migrations/|alembic/versions/')[…]"
say "data: ${D:-none-detected}"
say "migrations: ${MIG:-none-detected}"

# auth
AUTH=""
grep -qiE 'passport|next-auth|authlib|oauthlib|keycloak|auth0|clerk|casdoor|django-allauth|laravel/sanctum|firebase-auth|jsonwebtoken|pyjwt|jsonwebtoken|django-oauth' <<<"$M $FW" && AUTH="$(grep -rhoiE '(passport|next-auth|authlib|oauthlib|keycloak|auth0|clerk|allauth|sanctum|pyjwt|jsonwebtoken)' <<<"$M $FW" | sort -u | tr '\n' ',')"
hasre 'docker-compose.*\.(ya?ml)$' && grep -qiE 'keycloak|cas|oidc' $(grep 'docker-compose' <<<"$FILES" | head -3) 2>/dev/null && AUTH="${AUTH:+$AUTH,}idp-in-compose"
say "auth: ${AUTH:-none-detected}"

# jobs / messaging
J=""
grep -qiE 'celery|rq\b|sidekiq|bullmq|bun\b.*queue|resque|laravel.*queue|quartz|hangfire|sqs|sns|kafka|rabbit|amqp|nats|asynq|temporal' <<<"$FW $M" && J="$(grep -hoiE '(celery|sidekiq|bullmq|kafka|rabbit|amqp|nats|asynq|temporal|sqs)' <<<"$FW $M" | sort -u | tr '\n' ',')"
hasre 'crontab|schedule|cron' && grep -rqlE 'cron|scheduler' $(grep -E '\.(py|go|rb|php|ts)$' <<<"$FILES" | head -200) 2>/dev/null && J="${J:+$J,}cron-hint"
say "jobs: ${J:-none-detected}"

# deploy / infra
DEP=""
hasre 'Dockerfile' && DEP="${DEP:+$DEP }docker:$(names 'Dockerfile')"
hasre 'docker-compose.*\.ya?ml$' && DEP="${DEP:+$DEP }compose:$(names 'docker-compose.*\.ya?ml$')"
hasre '\.service$|systemd' && DEP="${DEP:+$DEP }systemd"
hasre 'nginx.*\.conf$|Caddyfile' && DEP="${DEP:+$DEP }proxy:$(names 'nginx.*\.conf$|Caddyfile')"
hasre 'k8s|kubernetes|helm|Chart.yaml' && DEP="${DEP:+$DEP }k8s"
hasre '(fly|vercel|railway|render)\.(toml|json)$' && DEP="${DEP:+$DEP }paas"
say "deploy: ${DEP:-none-detected}"

# CI + tests
CI="$(names '^.github/workflows/|\.gitlab-ci\.yml$|Jenkinsfile$|\.woodpecker')"
say "ci: ${CI:-none-detected}"
T="$(names 'tests?/|conftest\.py$|_test\.go$|Test\.java$|\.test\.(ts|js|tsx)$|phpunit\.xml')"
say "tests: ${T:-none-detected}"
say "config: $(names '\.env\.example$|settings/|config\.(py|ts|js)$|appsettings')"

# risk hints (grep-level, needs manual confirm)
R=""
hasre '\.env$' && ! hasre '\.env\.example$' && R="${R:+$R }env-file-committed-check"
grep -rqlE 'SELECT \* .*\+|execute\(.*%|db\.exec\(.*\+' $(grep -E '\.(py|php|rb|go|ts|js)$' <<<"$FILES" | head -300) 2>/dev/null && R="${R:+$R }sql-concat-candidates"
say "risks: ${R:-none-obvious}  (hints, confirm before fixing)"

# class guess
FRESH=$(find "$PROJ" -newer "$PROJ" -name '*.md' 2>/dev/null | head -1); GITN=""
GITC=$(git -C "$PROJ" rev-list --count HEAD 2>/dev/null || echo "")
SRC=$(cnt '\.(py|go|rs|php|ts|java|kt|cs|rb)$')
if [[ "$SRC" -lt 15 ]]; then CLASS="new-or-small"
elif [[ -n "${GITC:-}" && "$GITC" -gt 200 && "$SRC" -gt 200 ]]; then CLASS="established(check-age-migrations-for-legacy)"
else CLASS="active-project"; fi
say "class-guess: ${CLASS} (src-files:$SRC, git-commits:${GITC:-n/a}) — confirm by reading code"
