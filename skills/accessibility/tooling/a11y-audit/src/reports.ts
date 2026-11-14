// reports.ts — JSON / accessible-HTML / JUnit / SARIF writers + compare.
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { basename } from 'node:path';
import type { AuditResult, Finding } from './types.ts';

function ensureDir(dir: string): void { mkdirSync(dir, { recursive: true }); }

export function writeJson(r: AuditResult, path: string): void {
  writeFileSync(path, JSON.stringify(r, null, 2));
}

function esc(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// The report itself is WCAG-considered: lang, landmarks, table semantics,
// sufficient contrast tokens, no color-only signaling.
export function writeHtml(r: AuditResult, path: string): void {
  const rows = r.findings.map((f) => `<tr>
    <td>${esc(f.ruleId)}</td><td>${esc(f.sc)}</td><td>${esc(f.level)}</td>
    <td>${esc(f.impact)}</td><td>${esc(f.route)}/${esc(f.viewport)}/${esc(f.scenario)}</td>
    <td>${esc(f.message)}</td><td><code>${esc(f.selector)}</code></td>
    <td>${f.manualVerification ? 'Manual review required' : esc(f.fix ?? '')}</td>
    <td><ol>${f.repro.map((s) => `<li>${esc(s)}</li>`).join('')}</ol></td>
  </tr>`).join('\n');
  const manual = r.manual.map((m) => `<tr><td>${esc(m.sc)}</td><td>${esc(m.scName)}</td>
    <td>${esc(m.status)}</td><td>${esc(m.how)}</td></tr>`).join('\n');
  const html = `<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Accessibility audit — ${esc(r.standard)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{color-scheme:light dark}
body{font:14px/1.5 system-ui;margin:2rem auto;max-width:72rem;padding:0 1rem;color:canva;text}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{border:1px solid currentColor;padding:.4rem;vertical-align:top;text-align:left}
caption{text-align:left;font-weight:700;padding-block:.5rem}
:focus-visible{outline:3px solid Highlight;outline-offset:2px}
code{overflow-wrap:anywhere}
summary{cursor:pointer;font-weight:600;padding-block:.75rem}
</style></head>
<body>
<a href="#findings">Skip to findings</a>
<header><h1>Accessibility audit report</h1>
<p>Standard: ${esc(r.standard)} · target level <strong>${esc(r.level.toUpperCase())}</strong> ·
generated ${esc(r.generatedAt)} · ${esc(r.browser)} on ${esc(r.os)} · axe-core ${esc(r.axeVersion)}</p>
<p role="status">Gate result: <strong>${esc(r.gate)}</strong> — ${esc(r.gateNote)}</p></header>
<main>
<section><h2 id="summary">Summary</h2>
<ul>
<li>Blocking findings (A/AA): <strong>${r.summary.violationsAa}</strong></li>
<li>AAA advisory findings: <strong>${r.summary.violationsAaa}</strong></li>
<li>Needs manual review: <strong>${r.summary.needsManualReview}</strong></li>
<li>Rule passes: <strong>${r.summary.passes}</strong> · scenarios run: ${r.summary.scenariosRun}</li>
</ul></section>
<section id="findings"><h2>Findings (${r.findings.length})</h2>
<table><caption>Automated findings grouped by rule and element</caption>
<thead><tr><th scope="col">Rule</th><th scope="col">SC</th><th scope="col">Level</th>
<th scope="col">Impact</th><th scope="col">Context</th><th scope="col">Message</th>
<th scope="col">Selector</th><th scope="col">Remediation</th><th scope="col">Repro steps</th></tr></thead>
<tbody>${rows}</tbody></table></section>
<section><h2>Manual verification queue</h2>
<p>These items automated tools cannot decide (WCAG-EM manual slice). Absence of a
finding here is NOT a pass.</p>
<table><caption>Criteria requiring human/AT verification</caption>
<thead><tr><th scope="col">SC</th><th scope="col">Topic</th><th scope="col">Status</th><th scope="col">How</th></tr></thead>
<tbody>${manual}</tbody></table></section>
<details><summary>Per-scenario detail (${r.routes.length} runs)</summary>
<table><caption>Scenario runs</caption>
<thead><tr><th scope="col">Route</th><th scope="col">Viewport</th><th scope="col">Scenario</th>
<th scope="col">Passes</th><th scope="col">Violations</th><th scope="col">Notes</th></tr></thead>
<tbody>${r.routes.map((s) => `<tr><td>${esc(s.route)}</td><td>${esc(s.viewport)}</td>
<td>${esc(s.scenario)}</td><td>${s.pass}</td><td>${s.violations.length}</td>
<td>${s.notes.map(esc).join('; ')}</td></tr>`).join('')}</tbody></table></details>
</main>
<footer><p>Report tool: ${esc(r.tool)} ${esc(r.toolVersion)}. Automated PASS ≠ conformance claim.</p></footer>
</body></html>`;
  writeFileSync(path, html);
}

export function writeJunit(r: AuditResult, path: string): void {
  const cases = r.routes.map((s) => {
    const fails = s.violations.map((f) =>
      `      <failure message="${esc(f.ruleId)} (${f.level})" type="${esc(f.impact)}">${esc(f.message)} @ ${esc(f.selector)}</failure>`).join('\n');
    return `    <testcase classname="${esc(s.route)}.${esc(s.viewport)}.${esc(s.scenario)}" name="axe" time="0">\n${fails || '      <passed/>'}\n    </testcase>`;
  }).join('\n');
  writeFileSync(path, `<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="a11y-audit (${r.level.toUpperCase()})" tests="${r.routes.length}" failures="${r.summary.violationsAa}">
${cases}
</testsuite>\n`);
}

export function writeSarif(r: AuditResult, path: string): void {
  const rules = new Map<string, { id: string; shortDescription: { text: string } }>();
  const results = r.findings.map((f) => {
    rules.set(f.ruleId, { id: f.ruleId, shortDescription: { text: f.message } });
    return {
      ruleId: f.ruleId,
      level: f.manualVerification ? 'note' : (f.level === 'AAA' ? 'warning' : 'error'),
      message: { text: `${f.message} — ${f.fix ?? f.manualVerification ? (f.fix ?? 'manual review') : ''}` },
      locations: [{ physicalLocation: { artifactLocation: { uri: f.route }, region: {} },
        logicalLocations: [{ name: `${f.scenario}/${f.viewport}` }] }],
    };
  });
  writeFileSync(path, JSON.stringify({
    $schema: 'https://json.schemastore.org/sarif-2.1.0.json', version: '2.1.0',
    runs: [{ tool: { driver: { name: 'a11y-audit', version: r.toolVersion, rules: [...rules.values()] } }, results }],
  }, null, 2));
}

export function renderReport(jsonPath: string, format: string, outDir: string): number {
  const r = JSON.parse(readFileSync(jsonPath, 'utf8')) as AuditResult;
  ensureDir(outDir);
  const base = basename(jsonPath).replace(/\.json$/, '');
  if (format === 'html') writeHtml(r, `${outDir}/${base}.html`);
  else if (format === 'junit') writeJunit(r, `${outDir}/${base}.junit.xml`);
  else if (format === 'sarif') writeSarif(r, `${outDir}/${base}.sarif`);
  else { process.stderr.write(`unknown format ${format}\n`); return 2; }
  process.stdout.write(`rendered ${format}: ${outDir}/${base}\n`);
  return 0;
}

interface Side { ruleId: string; selector: string; route: string; level: string; manualVerification: boolean }
function key(f: Side): string { return `${f.ruleId}|${f.selector}|${f.route}`; }

export function compareResults(beforePath: string, afterPath: string, outDir: string): number {
  const before = JSON.parse(readFileSync(beforePath, 'utf8')) as AuditResult;
  const after = JSON.parse(readFileSync(afterPath, 'utf8')) as AuditResult;
  const norm = (r: AuditResult): Map<string, Finding> =>
    new Map(r.findings.filter((f) => !f.manualVerification && f.level !== 'AAA').map((f) => [key(f), f]));
  const a = norm(before), b = norm(after);
  const fixed = [...a.keys()].filter((k) => !b.has(k));
  const introduced = [...b.keys()].filter((k) => !a.has(k));
  const report = {
    before: before.generatedAt, after: after.generatedAt,
    beforeBlocking: before.summary.violationsAa, afterBlocking: after.summary.violationsAa,
    fixed, introduced,
    verdict: introduced.length ? 'REGRESSIONS' : fixed.length ? 'IMPROVED' : 'UNCHANGED',
  };
  ensureDir(outDir);
  const out = `${outDir}/compare-${Date.now()}.json`;
  writeFileSync(out, JSON.stringify(report, null, 2));
  process.stdout.write(`compare ${report.verdict}: fixed=${fixed.length} introduced=${introduced.length} ` +
    `(${report.beforeBlocking}→${report.afterBlocking}) → ${out}\n`);
  return introduced.length > 0 ? 1 : 0;
}
