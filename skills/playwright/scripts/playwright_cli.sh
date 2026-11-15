#!/usr/bin/env bash
# playwright_cli.sh — resolve a Playwright CLI for this skill.
# Order: $PLAYWRIGHT_CLI override, official playwright-cli, then a
# repository/stack launcher already on PATH. Never installs anything.
set -euo pipefail
if [[ -n "${PLAYWRIGHT_CLI:-}" && -x "${PLAYWRIGHT_CLI}" ]]; then
  exec "${PLAYWRIGHT_CLI}" "$@"
fi
for candidate in playwright-cli mm-playwright; do
  if command -v "$candidate" >/dev/null 2>&1; then
    exec "$candidate" "$@"
  fi
done
echo "playwright_cli: no Playwright CLI found; set PLAYWRIGHT_CLI or install playwright-cli" >&2
exit 127
