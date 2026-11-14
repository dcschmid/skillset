#!/usr/bin/env node
/**
 * audit_astro_project.mjs — read-only Astro project auditor.
 * Node >= 18.17, stdlib only, non-destructive. Prints a census a coding agent
 * can act on; exits 0 on any readable project, 1 only on unreadable input.
 * Usage: node scripts/audit_astro_project.mjs [project_dir]
 */
import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import { join, relative, extname } from 'node:path';

const root = process.argv[2] ? process.argv[2] : process.cwd();
const out = [];
const fail = (msg) => { console.error(`astro-audit: ${msg}`); process.exit(1); };
if (!existsSync(root) || !statSync(root).isDirectory()) fail(`not a directory: ${root}`);

const read = (p) => { try { return readFileSync(join(root, p), 'utf8'); } catch { return null; } };
const readAbs = (f) => { try { return readFileSync(f, 'utf8'); } catch { return null; } };
const walk = (dir, acc = []) => {
  if (!existsSync(dir)) return acc;
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const f = join(dir, e.name);
    if (e.isDirectory()) walk(f, acc); else acc.push(f);
  }
  return acc;
};

// 1. Identity & versions
const pkg = (() => { try { return JSON.parse(read('package.json') ?? '{}'); } catch { fail('package.json unreadable — is this a project root?'); } })();
const deps = { ...pkg.dependencies, ...pkg.devDependencies };
const pm = existsSync(join(root, 'pnpm-lock.yaml')) ? 'pnpm'
  : existsSync(join(root, 'yarn.lock')) ? 'yarn'
  : existsSync(join(root, 'bun.lockb')) || existsSync(join(root, 'bun.lock')) ? 'bun'
  : existsSync(join(root, 'package-lock.json')) ? 'npm' : 'unknown';
out.push(`project: ${root}`);
out.push(`package-manager: ${pm}  lockfile: ${pm !== 'unknown'}`);
out.push(`astro: ${deps.astro ?? 'ABSENT'}  node-engine: ${pkg.engines?.node ?? 'unset'}`);

// 2. Config census
const cfgName = ['astro.config.mjs', 'astro.config.ts', 'astro.config.mts', 'astro.config.js']
  .find((f) => existsSync(join(root, f)));
const cfg = cfgName ? read(cfgName) ?? '' : '';
out.push(`config: ${cfgName ?? 'MISSING'} output:${(cfg.match(/output:\s*['"](\w+)['"]/) ?? [, 'static(default)'])[1]
} site:${cfg.includes('site:') ? 'set' : 'MISSING'} adapter:${(cfg.match(/@astrojs\/(node|netlify|vercel|cloudflare)/) ?? [, 'none'])[1]
} prefetch:${/prefetch:\s*(true|\{)/.test(cfg)} compress:${!/compressDefault:\s*false/.test(cfg)}`);
out.push(`config-keys: session:${cfg.includes('session')} cache:${cfg.includes('cache')} routeRules:${cfg.includes('routeRules')} i18n:${cfg.includes('i18n')} fonts:${cfg.includes('fonts:')} markdown:${cfg.includes('markdown:')}`);

// 3. Routes & rendering split
const pagesDir = join(root, 'src', 'pages');
const pages = walk(pagesDir).filter((f) => ['.astro', '.md', '.mdx', '.ts', '.js'].includes(extname(f)));
const src = walk(join(root, 'src'));
const allFiles = src.filter((f) => ['.astro', '.ts', '.tsx', '.js', '.md', '.mdx'].includes(extname(f)));
const readAll = allFiles.map((f) => [relative(root, f), readAbs(f) ?? '']);
const serverRoutes = readAll.filter(([, c]) => /export const prerender\s*=\s*false/.test(c)).map(([f]) => f);
const fetchContentLegacy = readAll.filter(([, c]) => /Astro\.fetchContent\s*\(/.test(c)).map(([f]) => f);

out.push(`routes: ${pages.length} (pages/) · src-files: ${allFiles.length}`);
if (pages.length === 0) out.push('  WARN src/pages empty or missing — no routes');
out.push(`on-demand-routes (prerender=false): ${serverRoutes.length}${serverRoutes.length ? '\n  ' + serverRoutes.join('\n  ') : ''}`);
if (!cfgName) out.push('  WARN no astro.config.* found');
else if (!cfg.includes('site:')) out.push('  WARN site: unset — canonical/sitemap/OG will be relative');
if (serverRoutes.length && !cfg.includes('@astrojs/')) out.push('  WARN prerender=false routes but no adapter in config');
if (fetchContentLegacy.length) out.push(`  legacy Astro.fetchContent: ${fetchContentLegacy.join(', ')}`);

// 4. Content layer
const cfgNew = existsSync(join(root, 'src/content.config.ts'));
const cfgOld = existsSync(join(root, 'src/content/config.ts'));
const collections = cfgNew ? (read('src/content.config.ts')?.match(/^\s*(\w+)\s*:\s*defineCollection/gm) ?? []).length : 0;
out.push(`content: ${cfgNew ? `content.config.ts (${collections ? collections + ' collection(s)' : '?'})` : cfgOld ? 'LEGACY src/content/config.ts (migrate on 5+)' : 'none'}`);

// 5. Interactivity surface
const islands = readAll.filter(([, c]) => /client:(load|idle|visible|media|only)/.test(c)).map(([f]) => f);
const serverIslands = readAll.filter(([, c]) => /server:(defer|print)/.test(c)).map(([f]) => f);
const fw = Object.keys(deps).filter((d) => ['react', 'vue', 'svelte', 'solid-js', 'preact'].some((x) => d.includes(x)));
out.push(`client-islands: ${islands.length}${islands.length ? '\n  ' + islands.join('\n  ') : ''}`);
out.push(`server-islands (server:defer/print): ${serverIslands.length}${serverIslands.length ? '\n  ' + serverIslands.join('\n  ') : ''}`);
out.push(`framework-deps: ${fw.length ? fw.join(', ') : 'none (astro-native)'}`);
if (fw.length && !islands.length) out.push('  NOTE framework deps present but no client:* directives found in src');

// 6. Hygiene
const has404 = existsSync(join(root, 'src/pages/404.astro'));
const envFiles = ['.env', '.env.local'].filter((f) => existsSync(join(root, f)));
const gitignore = read('.gitignore') ?? '';
out.push(`404-page: ${has404} · env-files: ${envFiles.join(',') || 'none'} · .env gitignored: ${/\.env/.test(gitignore) || 'n/a'}`);
const tsStrict = /astro\/tsconfigs\/(strict|base)/.test(read('tsconfig.json') ?? '');
out.push(`tsconfig: astro ${tsStrict ? 'strict/base' : 'custom — verify strict'}`);
out.push(`integrations: ${Object.keys(deps).filter((d) => d.startsWith('@astrojs/')).map((d) => `${d}@${deps[d]}`).join(', ') || 'only core'}`);

console.log(out.join('\n'));
