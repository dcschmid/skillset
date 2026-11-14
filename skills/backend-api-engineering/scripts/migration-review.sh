#!/usr/bin/env bash
# migration-review.sh — static review of SQL migration directories.
# Flags destructive DDL (DROP/TRUNCATE/NOT NULL w/o default/type changes),
# missing down/rollback sections, non-concurrent index creation on live
# systems. Lint-only: reads files, mutates nothing.
# Usage: migration-review.sh MIGRATIONS_DIR   (-h help)
# Exit: 0 no findings · 1 findings present · 2 bad args/dir
set -uo pipefail
case "${1:-}" in -h|--help) sed -n '2,7p' "$0"; exit 0;; esac
DIR="${1:-}"
[[ -n "$DIR" && -d "$DIR" ]] || { echo "usage: migration-review.sh MIGRATIONS_DIR" >&2; exit 2; }

files="$(find "$DIR" -type f \( -name '*.sql' -o -iname '*migration*' -o -iname '*version*' \) \
  -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/dist/*' 2>/dev/null | sort)"
[[ -n "$files" ]] || { echo "PASS    no migration files under $DIR"; exit 0; }

findings=0
note(){ echo "FINDING [$1] $2 :: $3"; findings=$((findings+1)); }

while IFS= read -r f; do
  rel="${f#"$DIR"/}"
  sql="$(tr -d '\r' <"$f")"
  up="$(grep -icE '^\s*--\s*up\b|def upgrade|exports\.up|"up":' <<<"$sql" || true)"
  dn="$(grep -icE '^\s*--\s*down\b|def downgrade|exports\.down|"down":' <<<"$sql" || true)"
  if [[ "$f" == *.sql ]]; then
    while IFS= read -r line; do
      [[ -z "$line" ]] && continue
      note "destructive-DDL" "$rel" "DROP/TRUNCATE — confirm no prod readers/writers: ${line:0:90}"
    done < <(awk 'tolower($0) ~ /-- *down/{exit} 1' <<<"$sql" | grep -inE '(drop|truncate) (table|column|index|constraint|schema|database)' \
             | grep -viE 'temp|tmp' | head -20)
    while IFS= read -r line; do
      [[ -z "$line" ]] && continue
      grep -qiE 'not null' <<<"$line" || continue
      grep -qiE 'default|using|timestamp|serial|primary key|generated' <<<"$line" && continue
      note "lock-risk" "$rel" "ADD NOT NULL w/o DEFAULT — nullable→backfill→constrain instead: ${line:0:90}"
    done < <(grep -inE 'add (column )?[a-z_]+ .*(not null)|alter column' <<<"$sql" | grep -iE 'not null' | head -40)
    while IFS= read -r line; do
      [[ -z "$line" ]] && continue
      grep -qiE 'concurrently' <<<"$line" && continue
      note "lock-risk" "$rel" "index/constraint without CONCURRENTLY (live PG tables): ${line:0:90}"
    done < <(grep -inE 'create (unique )?(index|constraint)' <<<"$sql" | head -20)
    while IFS= read -r line; do
      [[ -z "$line" ]] && continue
      note "type-change" "$rel" "column TYPE change rewrites table — new col + copy + swap: ${line:0:90}"
    done < <(grep -inE 'alter column .*type|modify .*(varchar|int|decimal|numeric)' <<<"$sql" | head -20)
    if [[ "$up" -gt 0 && "$dn" -eq 0 ]]; then
      note "no-rollback" "$rel" "up without down — attach forward-fix note or downgrade"
    fi
  else
    c=$(grep -ciE '(drop|truncate) (table|column)' <<<"$sql" || true)
    if (( c > 0 )); then note "destructive-DDL" "$rel" "${c} destructive stmts in tool file - review each"; fi
    echo "INFO    $rel  (tool-managed: check the tool's down/undo config)"
  fi
done <<<"$files"

if [[ "$findings" -eq 0 ]]; then echo "PASS    $DIR  no lint findings"; exit 0
else echo "REVIEW  $DIR  findings=$findings"; exit 1; fi
