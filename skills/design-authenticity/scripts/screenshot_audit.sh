#!/usr/bin/env bash
# screenshot_audit.sh — browser-gated screenshot capture for design reviews.
# Usage: screenshot_audit.sh <url> <out-dir> [widths csv]  (default viewports:
#        390x844,768x1024,1440x900,1920x1080)
# Emits <out-dir>/<w>x<h>.<urlhash>.png per viewport + a manifest line per shot.
# Capability truth: no usable browser -> prints BROWSER_UNAVAILABLE, exit 3,
# and writes NOTHING (a missing audit is never reported as a passed audit).
set -euo pipefail

url="${1:?usage: screenshot_audit.sh <url> <out-dir> [widths csv]}"; shift
out="${1:?missing out-dir}"; shift
viewports="${1:-390x844,768x1024,1440x900,1920x1080}"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
audit_dir="$repo/skills/accessibility/tooling/a11y-audit"

browser=""
if [[ -d "$audit_dir/node_modules/playwright" ]] && command -v node >/dev/null; then
  browser="playwright-node"
elif command -v npx >/dev/null && npx --no-install playwright --version >/dev/null 2>&1; then
  browser="playwright-npx"
elif command -v chromium >/dev/null; then browser="chromium-cli"
elif command -v chromium-browser >/dev/null; then browser="chromium-cli"
elif command -v firefox >/dev/null; then browser="firefox-cli"
fi

if [[ -z "$browser" ]]; then
  echo "BROWSER_UNAVAILABLE no playwright/chromium/firefox found; screenshot audit NOT performed"
  exit 3
fi

mkdir -p "$out"
hash8="$(printf '%s' "$url" | cksum | cut -d' ' -f1)"
manifest="$out/manifest.txt"; : > "$manifest"

capture() { # $1=w $2=h $3=file
  case "$browser" in
    playwright-node|playwright-npx)
      local runner; runner="$(mktemp /tmp/dashot.XXXX.mjs)"
      cat > "$runner" <<'JS'
import { createRequire } from 'node:module';
const require = createRequire(process.env.DA_PW_BASE);
const { chromium, firefox } = require('playwright');
const [url, w, h, file] = process.argv.slice(2);
const b = await (file.endsWith('.ff.png') ? firefox : chromium).launch();
const p = await (await b.newContext({ viewport: { width: +w, height: +h } })).newPage();
await p.goto(url, { waitUntil: 'networkidle' });
await p.screenshot({ path: file, fullPage: true });
await b.close();
JS
      local runcmd=(node)
      [[ "$browser" == playwright-npx ]] && runcmd=(npx --no-install node)
      ( cd "$audit_dir" && DA_PW_BASE="$audit_dir/" "${runcmd[@]}" "$runner" "$url" "$1" "$2" "$3" ) \
        || { rm -f "$runner"; return 1; }
      rm -f "$runner" ;;
    chromium-cli) local bin; bin="$(command -v chromium || command -v chromium-browser)"
      "$bin" --headless=new --disable-gpu --no-sandbox --window-size="$1,$2" \
        --screenshot="$3" "$url" >/dev/null 2>&1 ;;
    firefox-cli)
      firefox --screenshot "$3" --window-size "$1,$2" "$url" >/dev/null 2>&1 ;;
  esac
}

IFS=',' read -ra vps <<< "$viewports"
for vp in "${vps[@]}"; do
  w="${vp%x*}"; h="${vp#*x}"; f="$out/${w}x${h}.${hash8}.png"
  if capture "$w" "$h" "$f"; then
    echo "shot $f ${w}x${h} via $browser" | tee -a "$manifest"
  else
    echo "fail ${w}x${h} via $browser (capture error, no artifact claimed)" | tee -a "$manifest"
  fi
done
if grep -q '^shot ' "$manifest"; then
  echo "done browser=$browser out=$out  # diffs prove change, not quality (see references/visual-quality-gates.md)"
else
  echo "AUDIT FAILED browser=$browser produced 0 shots — not reported as passed"
  exit 3
fi
