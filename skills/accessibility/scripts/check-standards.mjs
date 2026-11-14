// check-standards.mjs — standards drift probe (audit-methodology.md §Update).
// Fetches pinned sources, extracts status lines, diffs against
// references/standards.md pins. Prints CHANGE report; exits 0 always (report,
// not gate). Network failure: prints UNVERIFIED with pin age — no invented
// news, no silent success.
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const skillRoot = join(here, '..');
const pins = readFileSync(join(skillRoot, 'references', 'standards.md'), 'utf8');

const SOURCES = [
  { name: 'WCAG 2.2', url: 'https://www.w3.org/TR/WCAG22/', match: /W3C Recommendation[^<]*/ },
  { name: 'WCAG 3.0', url: 'https://www.w3.org/TR/wcag3/', match: /W3C Working Draft[^<]*/ },
  { name: 'WCAG-EM 2.0', url: 'https://www.w3.org/TR/wcag-em/', match: /W3C Group Note[^<]*/ },
  { name: 'axe-core', url: 'https://registry.npmjs.org/axe-core/latest', match: /"version":\s*"([\d.]+)"/, json: true },
  { name: 'Guidepup guidepup', url: 'https://registry.npmjs.org/@guidepup/guidepup/latest', match: /"version":\s*"([\d.]+)"/, json: true },
];

const PROBE_DATE = new Date().toISOString().slice(0, 10);
const report = [];
let changes = 0;

for (const s of SOURCES) {
  let found = 'UNVERIFIED (network/parse failure)';
  try {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 10000);
    const res = await fetch(s.url, { signal: ctrl.signal, headers: { accept: s.json ? 'application/json' : 'text/html' } });
    clearTimeout(t);
    const body = await res.text();
    const m = body.match(s.match);
    if (m) found = m[1] ?? m[0];
  } catch { /* offline: report pin age below */ }
  const pinned = pins.match(new RegExp(`[0-9]{4}-[0-9]{2}-[0-9]{2}|\\d+\\.\\d+\\.\\d+`))?.[0] ?? '?';
  const stale = /UNVERIFIED/.test(found);
  report.push(`${stale ? '·' : '✓'} ${s.name}: live=${found} · pinned=${pinned} · probe=${PROBE_DATE}`);
  if (!stale && !pins.includes(found.slice(0, 10))) { changes++; report.push(`  CHANGE: review references/standards.md entry "${s.name}"`); }
}

process.stdout.write(`standards check ${PROBE_DATE}\n${report.join('\n')}\n`);
process.stdout.write(
  `${changes === 0 ? 'no drift detected among reachable sources' : changes + ' drift candidate(s) above — update via human review only (no auto-edits to normative content)'}\n` +
  `stale pins on unreachable sources: cite probe date in outputs while unfixed.\n`);
