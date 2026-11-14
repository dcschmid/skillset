#!/usr/bin/env node
/**
 * audit_react_project.mjs — read-only React/Next.js project auditor.
 * Node >= 18, stdlib only, non-destructive. Prints a census a coding agent
 * acts on; exit 0 on any readable project, 1 only on unreadable input.
 * Usage: node scripts/audit_react_project.mjs [project_dir]
 */
import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import { join, relative, extname } from 'node:path';

const root = process.argv[2] ? process.argv[2] : process.cwd();
const out = [];
const fail = (msg) => { console.error(`react-audit: ${msg}`); process.exit(1); };
if (!existsSync(root) || !statSync(root).isDirectory()) fail(`not a directory: ${root}`);

const read = (p) => { try { return readFileSync(join(root, p), 'utf8'); } catch { return null; } };
const walk = (dir, acc = []) => {
  if (!existsSync(dir)) return acc;
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    if (e.name === 'node_modules' || e.name.startsWith('.')) continue;
    const f = join(dir, e.name);
    if (e.isDirectory()) walk(f, acc); else acc.push(f);
  }
  return acc;
};

const pkg = (() => { try { return JSON.parse(read('package.json') ?? '{}'); } catch { fail('package.json unreadable — project root?'); } })();
const deps = { ...pkg.dependencies, ...pkg.devDependencies };
const pm = existsSync(join(root, 'pnpm-lock.yaml')) ? 'pnpm'
  : existsSync(join(root, 'yarn.lock')) ? 'yarn'
  : existsSync(join(root, 'bun.lockb')) || existsSync(join(root, 'bun.lock')) ? 'bun'
  : existsSync(join(root, 'package-lock.json')) ? 'npm' : 'unknown';
const jver = (n) => deps[n] ?? 'ABSENT';

out.push(`project: ${relative('.', root) || '.'}  package-manager: ${pm}`);
out.push(`react:${jver('react')} react-dom:${jver('react-dom')} next:${jver('next')} typescript:${jver('typescript')} vite:${jver('vite') ?? 'ABSENT'}`);
out.push(`stack: ${deps.next ? 'NEXT(likely App+Pages per dirs below)' : (deps.vite || deps.react ? 'REACT-ONLY (no Next rules)' : 'unknown')}`);

const ts = read('tsconfig.json') ?? '';
out.push(`ts-strict: ${/"strict":\s*true/.test(ts) ? 'yes' : ts ? 'NO/unchecked' : 'no-tsconfig'}`);

const dirs = ['app', 'src/app', 'pages', 'src/pages', 'src', 'proxy.ts', 'middleware.ts', 'src/proxy.ts', 'src/middleware.ts'];
for (const d of dirs) if (existsSync(join(root, d))) out.push(`dir: ${d}`);

const files = walk(join(root, 'src')).concat(walk(join(root, 'app')));
const src = files.filter((f) => ['.tsx', '.ts', '.jsx', '.js'].includes(extname(f)));
let client = 0, serverFns = 0, useCache = 0, memo = 0;
for (const f of src) {
  const t = read(relative(root, f)) ?? '';
  if (/"use client"/.test(t)) client++;
  if (/"use server"/.test(t)) serverFns++;
  if (/["']use cache["']|use\s+cache\b/.test(t)) useCache++;
  if (/\buse(Memo|Callback)\b/.test(t)) memo++;
}
out.push(`source-files:${src.length} client-components:${client} server-fn-files:${serverFns} use-cache:${useCache} memo-callsites:${memo} (memo>0 with Compiler on: review react-compiler.md)`);

const cfg = ['next.config.ts', 'next.config.mjs', 'next.config.js'].map((f) => read(f)).find(Boolean) ?? '';
out.push(`next-config: cacheComponents:${/cacheComponents:\s*true/.test(cfg)} reactCompiler:${/reactCompiler|react-compiler/.test(cfg)} output:${(cfg.match(/output:\s*['"](\w+)['"]/) ?? [, 'default'])[1] || 'n/a'}`);
out.push(`local-docs: ${existsSync(join(root, 'node_modules/next/dist/docs')) ? 'node_modules/next/dist/docs PRESENT (version-matched authority)' : 'absent'}`);
out.push(`tests: vitest:${Object.keys(deps).some((d) => /vitest/.test(d))} playwright:${Object.keys(deps).some((d) => /playwright/.test(d))} rtl:${Object.keys(deps).some((d) => /testing-library/.test(d))}`);
out.push(`AGENTS.md:${existsSync(join(root, 'AGENTS.md')) ? 'present (append-only edits)' : 'absent'} CLAUDE.md:${existsSync(join(root, 'CLAUDE.md')) ? 'present' : 'absent'}`);

console.log(out.join('\n'));
