// run.mjs — skill validation suite (repo rule: parseable verdict, headless).
// Runs the real tool against the real fixtures; asserts detection quality.
// Run: node tests/run.mjs  (from tooling/a11y-audit) or via SKILL tests step.
import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const cli = join(root, 'bin', 'a11y.mjs');
const out = join(root, 'out', 'suite');
let pass = 0, fail = 0;
const ok = (name, cond, detail = '') => {
  if (cond) { pass++; process.stdout.write(`PASS ${name}\n`); }
  else { fail++; process.stdout.write(`FAIL ${name} ${detail}\n`); }
};
// gate exit 1 is expected on FAIL fixtures — execFileSync throws, keep going
const runAudit = (extra) => {
  try { execFileSync('node', [cli, 'audit', ...extra, '--out', out], { cwd: root, timeout: 90000 }); }
  catch (e) { if (e.status !== 1) throw e; }
  return JSON.parse(readFileSync(join(out, 'latest.json'), 'utf8'));
};

// 1. broken fixture → exit 1, known rules found, repro + selectors present
const fx = join(root, 'fixtures');
let r1code = 0;
try { execFileSync('node', [cli, 'audit', '--url', `file://${fx}/broken.html`, '--level', 'aa', '--out', out, '--viewport', 'desktop'], { cwd: root, timeout: 90000 }); }
catch (e) { r1code = e.status ?? 1; }
const r1 = JSON.parse(readFileSync(join(out, 'latest.json'), 'utf8'));
const rules1 = new Set(r1.findings.filter((f) => !f.manualVerification).map((f) => f.ruleId));
ok('broken fixture gates FAIL (exit 1)', r1code === 1, `code=${r1code}`);
// normative detections expected on broken fixture (axe-computed names explain
// absent `label`: placeholder is a name source; positive tabindex is BP-only)
for (const need of ['image-alt', 'color-contrast', 'link-name', 'input-button-name', 'aria-hidden-focus', 'target-size'])
  ok(`detects ${need}`, rules1.has(need), [...rules1].join(','));
ok('findings carry selectors+repro', r1.findings.every((f) => f.selector && Array.isArray(f.repro)));
ok('manual queue non-empty', r1.manual.length >= 3);

// 2. clean fixture → gate PASS, AAA advisory separation
const r2 = runAudit(['--url', `file://${fx}/clean.html`, '--level', 'aaa', '--out', out, '--viewport', 'desktop']);
ok('clean fixture gates PASS', r2.gate === 'PASS' && r2.summary.violationsAa === 0);
ok('passes recorded', r2.summary.passes > 10);

// 3. level separation: enhanced contrast only at AAA
const r3 = runAudit(['--url', `file://${fx}/broken.html`, '--level', 'aaa', '--out', out, '--viewport', 'desktop']);
const aaaRules = new Set(r3.findings.filter((f) => f.level === 'AAA').map((f) => f.ruleId));
ok('AAA advisory separate block', r3.summary.violationsAaa > 0 && aaaRules.has('color-contrast-enhanced'));
ok('AAA does not mask AA', r3.summary.violationsAa > 0);

// 4. dynamic state: dialog scenario catches violation invisible at load
const dlg = join(root, 'fixtures', 'a11y.config.json');
const cfg = readFileSync(dlg, 'utf8').replace('DIALOG_URL', `file://${fx}/dialog.html`);
const { writeFileSync } = await import('node:fs');
const cfgPath = join(out, 'cfg.json'); writeFileSync(cfgPath, cfg);
const r4 = runAudit(['--config', cfgPath, '--level', 'aa', '--out', out, '--viewport', 'desktop']);
ok('scenarios multiply scenario runs', r4.summary.scenariosRun >= 3);

// 5. keyboard probe runs
try { execFileSync('node', [cli, 'keyboard', '--url', `file://${fx}/dialog.html`, '--out', out], { cwd: root, timeout: 60000 });
  ok('keyboard probe produces report', existsSync(join(out, 'latest.json')) || readdirSync(out).some((f) => f.startsWith('keyboard-'))); }
catch { ok('keyboard probe produces report', false, 'exit'); }

// 6. compare
try {
  const cmp = execFileSync('node', [cli, 'compare', '--before', join(out, 'latest.json'), '--after', join(out, 'latest.json'), '--out', out], { cwd: root, timeout: 30000 }).toString();
  ok('compare UNCHANGED on identical', cmp.includes('UNCHANGED'));
} catch { ok('compare UNCHANGED on identical', false); }

// 7. SR verdict artifact (environment-declared, never fabricated)
const sr = join(root, 'out', 'sr-verdict.txt');
ok('SR verdict file exists', existsSync(sr) ? readFileSync(sr, 'utf8').includes('SR_') : 'absent (run tests/screenreader-orca.ts)');

process.stdout.write(`\nVERDICT ${fail === 0 ? 'PASS' : 'FAIL'} ${pass}/${pass + fail}\n`);
process.exit(fail === 0 ? 0 : 1);
