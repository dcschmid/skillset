// discover.mjs — project type + existing i18n structure detection.
// Zero deps. Facts over guesses: every claim carries the file that proves it.

import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { join, basename } from 'node:path';
import { normalizeLocale } from './locales.mjs';

const SKIP = new Set(['node_modules', '.git', 'dist', 'build', '.output', '.svelte-kit', '.astro', 'vendor', 'out', '.godot', 'Library', 'obj']);

export function walk(root, { maxDepth = 8, filter } = {}, acc = [], depth = 0) {
  if (depth > maxDepth || !existsSync(root)) return acc;
  for (const e of readdirSync(root, { withFileTypes: true })) {
    if (SKIP.has(e.name) || e.name.startsWith('.') && e.name !== '.gitignore') continue;
    const p = join(root, e.name);
    if (e.isDirectory()) walk(p, { maxDepth, filter }, acc, depth + 1);
    else if (!filter || filter(basename(p), p)) acc.push(p);
  }
  return acc;
}

const read = (p) => { try { return readFileSync(p, 'utf8'); } catch { return ''; } };

/** Detect stack + i18n setup. Returns { stack[], i18n: {system, localesDir, locales, configRefs} } */
export function discover(root) {
  const stack = [];
  const configRefs = [];
  const pkgPath = join(root, 'package.json');
  let deps = {};
  if (existsSync(pkgPath)) {
    try { deps = { ...JSON.parse(read(pkgPath)).dependencies, ...JSON.parse(read(pkgPath)).devDependencies }; } catch {}
  }
  const has = (n) => Object.hasOwn(deps, n);
  if (has('astro') || existsSync(join(root, 'astro.config.mjs')) || existsSync(join(root, 'astro.config.ts'))) stack.push('astro');
  if (has('next') || existsSync(join(root, 'next.config.js')) || existsSync(join(root, 'next.config.mjs'))) stack.push('nextjs');
  else if (has('react') || has('react-dom')) stack.push('react');
  if (has('nuxt') || existsSync(join(root, 'nuxt.config.ts'))) stack.push('nuxt');
  else if (has('vue')) stack.push('vue');
  if (has('svelte') || has('@sveltejs/kit')) stack.push('svelte');
  if (existsSync(join(root, 'project.godot'))) stack.push('godot');
  if (existsSync(join(root, 'game.project'))) stack.push('defold');
  const html = walk(root, { filter: (f) => f.endsWith('.html') && !f.includes('/dist/'), maxDepth: 3 });
  if (!stack.length && html.length) stack.push('vanilla-web');

  // i18n system
  let system = null;
  if (has('next-intl')) system = 'next-intl';
  else if (has('i18next') || has('react-i18next')) system = 'i18next';
  else if (has('@nuxtjs/i18n')) system = '@nuxtjs/i18n';
  else if (has('vue-i18n')) system = 'vue-i18n';
  else if (has('svelte-i18n')) system = 'svelte-i18n';
  else if (has('react-intl') || has('@formatjs/intl') || has('intl-messageformat')) system = 'formatjs';
  else if (stack.includes('astro')) {
    const conf = read(join(root, 'astro.config.mjs')) + read(join(root, 'astro.config.ts'));
    if (/i18n\s*:/.test(conf)) system = 'astro-i18n-routing';
  }
  if (!system && stack.includes('godot')) system = 'godot-translationserver';

  // locales dirs (both conventional and flat)
  const candidates = ['src/locales', 'src/i18n/locales', 'locales', 'public/locales', 'i18n', 'assets/locales', 'translations', 'localization', 'src/lib/locales', 'content/i18n'];
  const localesDir = candidates.map((d) => join(root, d)).find((d) => existsSync(d) && readdirSync(d).length) || null;

  // declared locales from config files
  const locales = new Set();
  let defaultLocale = null;
  const configFiles = ['astro.config.mjs', 'astro.config.ts', 'nuxt.config.ts', 'next-intl.mts', 'src/i18n/config.ts', 'src/i18n.ts', 'i18n.ts', 'src/middleware.ts', 'src/i18n/settings.ts'];
  const LANG_OK = /^[a-z]{2,3}$/;
  for (const f of configFiles) {
    const t = read(join(root, f));
    for (const m of t.matchAll(/['"]([a-z]{2}(?:[-_][A-Za-z]{2,4})?)['"]/g)) {
      const l = normalizeLocale(m[1]);
      if (l && LANG_OK.test(l.split('-')[0])) locales.add(l);
    }
    const d = /defaultLocale\s*[:=]\s*['"]([a-z]{2}[-_A-Za-z]*)['"]|locale\s*[:=]\s*['"](de|en|fr|es|it|pt|pl|ja|ko|zh|ar|he|tr)['"]/.exec(t);
    if (d && !defaultLocale) defaultLocale = normalizeLocale(d[1] || d[2]);
  }
  if (localesDir) {
    for (const f of readdirSync(localesDir, { recursive: true })) {
      const name = String(f).replace(/\.[^.]+$/, '').split(/[-_.\/]/).at(-1);
      const l = normalizeLocale(name);
      if (l && /^[a-z]{2,3}(-[A-Z]{2,4})?$/.test(l)) locales.add(l);
    }
  }
  if (system === 'defold-lang') locales.add('en');
  if (stack.includes('defold')) {
    const gp = read(join(root, 'game.project'));
    for (const m of gp.matchAll(/languages=(.+)/g)) m[1].split(',').forEach((l) => { const n = normalizeLocale(l.trim()); if (n) locales.add(n); });
  }
  locales.delete('');

  // framework-adjacent facts used by audit
  const sources = walk(root, { filter: (f) => /\.(tsx?|jsx?|astro|svelte|vue|lua|gd)$/.test(f) && !/\.test\.|\.spec\.|\.d\.ts$/.test(f), maxDepth: 8 });
  return {
    root,
    stack: [...new Set(stack)],
    stackDetail: { stack: [...new Set(stack)], system, configRefs },
    i18n: { system, localesDir: localesDir || null, locales: [...locales].sort(), configRefs, defaultLocale },
    sources,
    isSite: stack.some((s) => ['astro', 'nextjs', 'react', 'vue', 'nuxt', 'svelte', 'vanilla-web'].includes(s)) || html.length > 0,
    gameEngine: stack.includes('godot') ? 'godot' : stack.includes('defold') ? 'defold' : null,
    i18nLibs: Object.keys(deps).filter((d) => /i18n|intl|locale|translat/.test(d)).map((name) => ({ name, version: deps[name] })),
  };
}
