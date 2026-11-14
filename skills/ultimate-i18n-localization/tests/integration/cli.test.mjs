import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, mkdirSync, rmSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
export const tests = [];

const SKILL = new URL('../..', import.meta.url).pathname;
const CLI = join(SKILL, 'scripts', 'i18n');
const FIXTURE = join(SKILL, 'tests', 'fixtures', 'web-shop');
const run = (args, cwd = FIXTURE) =>
  execFileSync('node', [CLI, ...args, '--root', cwd], { encoding: 'utf8', timeout: 30000 });
const runExit = (args, cwd) => {
  try { return { code: 0, out: run(args, cwd) }; }
  catch (e) { return { code: e.status ?? 1, out: String(e.stdout || '') + String(e.stderr || '') }; }
};

function scratchProject(locales) {
  const dir = mkdtempSync(join(tmpdir(), 'i18n-it-'));
  mkdirSync(join(dir, 'locales'), { recursive: true });
  for (const [loc, body] of Object.entries(locales)) writeFileSync(join(dir, 'locales', `${loc}.json`), JSON.stringify(body));
  return dir;
}

tests.push(['audit fixture detects missing keys + reference de', () => {
  const out = run(['audit', '--reference', 'de']);
  assert.match(out, /Reference locale: de/);
  assert.match(out, /missing-key: 2/);
  assert.match(out, /placeholder-mismatch/);
}]);

tests.push(['coverage measured, never invented', () => {
  const out = run(['audit', '--reference', 'de', '--format', 'json']);
  const body = JSON.parse(out.slice(out.indexOf('{')));
  assert.equal(body.coverage.de, 100);
  assert.ok(body.coverage.en > 0 && body.coverage.en < 100, `en partial: ${body.coverage.en}`);
}]);

tests.push(['check exit code reflects blocking', () => {
  const clean = scratchProject({ de: { a: 'x' }, en: { a: 'x' } });
  try { assert.match(runExit(['check'], clean).out, /VERDICT PASS/); } finally { rmSync(clean, { recursive: true, force: true }); }
  const dirty = scratchProject({ de: { a: 'x' }, en: { a: 'x', b: 'y' } });
  try {
    const r = runExit(['check'], dirty);
    assert.equal(r.code, 1);
    assert.match(r.out, /VERDICT FAIL/);
  } finally { rmSync(dirty, { recursive: true, force: true }); }
}]);

tests.push(['validate fails loud on broken json', () => {
  const dir = scratchProject({ de: { a: 'x' } });
  writeFileSync(join(dir, 'locales', 'en.json'), '{broken');
  try {
    const r = runExit(['validate', '--dir', join(dir, 'locales')], FIXTURE);
    assert.equal(r.code, 1);
    assert.match(r.out, /FAIL .*en\.json/);
    assert.match(r.out, /VERDICT FAIL/);
  } finally { rmSync(dir, { recursive: true, force: true }); }
}]);

tests.push(['pseudo preserves placeholders and grows', () => {
  const out = run(['pseudo', '--text', 'Speichern {count} Elemente', '--expand', '0.3']);
  assert.ok(out.includes('{count}'), `placeholder kept: ${out}`);
  assert.ok(out.trim().length > 'Speichern {count} Elemente'.length);
}]);

tests.push(['pseudo dir mode writes locales-pseudo', () => {
  const dir = scratchProject({ de: { k: 'Sp' }, en: { k: 'Sa' } });
  try {
    const out = run(['pseudo', '--dir', join(dir, 'locales')]);
    assert.match(out, /VERDICT PASS/);
    assert.match(out, /graphemes \d+->\d+ \(\+\d+%\)/);
  } finally { rmSync(dir, { recursive: true, force: true }); }
}]);

tests.push(['fix adds missing keys, verifies, never deletes', () => {
  const dir = scratchProject({ de: { a: 'x', b: 'y' }, en: { a: 'x' } });
  try {
    const out = JSON.parse(run(['fix', '--reference', 'de'], dir));
    assert.equal(out.verified, true, JSON.stringify(out));
    const en = JSON.parse(readFileSync(join(dir, 'locales', 'en.json'), 'utf8'));
    assert.equal(en.b, 'TODO:b');
    assert.equal(en.a, 'x', 'existing untouched');
  } finally { rmSync(dir, { recursive: true, force: true }); }
}]);

tests.push(['extract collects t() keys from source', () => {
  const dir = scratchProject({ de: { nav: { home: 'x' } } });
  writeFileSync(join(dir, 'nav.js'), 'export const a = t("nav.home"); export const b = t("footer.copy");');
  try {
    const out = run(['extract'], dir);
    const body = JSON.parse(out.slice(0, out.lastIndexOf('}') + 1));
    assert.ok('nav.home' in body && 'footer.copy' in body);
  } finally { rmSync(dir, { recursive: true, force: true }); }
}]);

tests.push(['report json machine-readable', () => {
  const out = run(['report', '--format', 'json']);
  const body = JSON.parse(out.slice(out.indexOf('{')));
  assert.ok(Array.isArray(body.findings));
  assert.ok('blocking' in body && 'status' in body);
}]);
