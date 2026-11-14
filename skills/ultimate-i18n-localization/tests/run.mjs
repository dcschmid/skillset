#!/usr/bin/env node
/**
 * run.mjs — zero-dep test runner (skillset convention, matches seo-performance).
 * Usage: node tests/run.mjs [--filter SUBSTR]
 * Discovers tests/unit/*.test.mjs + tests/integration/*.test.mjs, each default-
 * exporting (name, fn) registrant OR using node:test style via --test fallback.
 * Prints PASS/FAIL lines + VERDICT, exit 0 iff all pass.
 */
import { readdirSync } from 'node:fs';
import { join, basename } from 'node:path';
import { pathToFileURL } from 'node:url';

const ROOT = new URL('.', import.meta.url).pathname;
const filter = (() => { const i = process.argv.indexOf('--filter'); return i > -1 ? process.argv[i + 1] : null; })();
const files = ['unit', 'integration'].flatMap((dir) => {
  try { return readdirSync(join(ROOT, dir)).filter((f) => f.endsWith('.test.mjs')).sort().map((f) => [dir, join(ROOT, dir, f)]); }
  catch { return []; }
});
let pass = 0, fail = 0;
const failures = [];
for (const [suite, file] of files) {
  const mod = await import(pathToFileURL(file).href);
  const tests = mod.tests || [];
  for (const [name, fn] of tests) {
    const label = `${basename(file)} :: ${name}`;
    if (filter && !label.includes(filter)) continue;
    try {
      await withTimeout(fn(), 30000, label);
      console.log(`PASS ${suite} ${label}`); pass++;
    } catch (e) {
      console.log(`FAIL ${suite} ${label} — ${String((e && e.message) || e).split('\n')[0]}`);
      failures.push(label); fail++;
    }
  }
}
console.log(`VERDICT ${fail === 0 ? 'PASS' : 'FAIL'} pass=${pass} fail=${fail} total=${pass + fail}`);
if (fail) console.log('failed:\n' + failures.map((f) => '  ' + f).join('\n'));
process.exit(fail ? 1 : 0);

async function withTimeout(p, ms, label) {
  let t;
  await Promise.race([p, new Promise((_, rej) => { t = setTimeout(() => rej(new Error(`timeout ${ms}ms: ${label}`)), ms); })]);
  clearTimeout(t);
}
