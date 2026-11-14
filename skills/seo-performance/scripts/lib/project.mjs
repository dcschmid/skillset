/**
 * project.mjs — read-only framework/rendering-strategy detection.
 * Detection is evidence-based (files on disk), version-gated where versions matter.
 */
import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

export function detectProject(dir = process.cwd()) {
  const read = (p) => { try { return readFileSync(join(dir, p), 'utf8'); } catch { return null; } };
  const exists = (p) => existsSync(join(dir, p));
  const pkg = (() => { try { return JSON.parse(read('package.json') ?? '{}'); } catch { return null; } })();
  const deps = { ...(pkg?.dependencies ?? {}), ...(pkg?.devDependencies ?? {}) };
  const has = (d) => d in deps;
  const ver = (d) => deps[d] ?? null;

  const pm = exists('pnpm-lock.yaml') ? 'pnpm' : exists('yarn.lock') ? 'yarn'
    : exists('bun.lockb') || exists('bun.lock') ? 'bun' : exists('package-lock.json') ? 'npm' : 'unknown';

  let framework = 'static-html', version = null, rendering = 'static', routes = null;
  if (has('astro')) { framework = 'astro'; version = ver('astro');
    const cfg = read('astro.config.mjs') ?? read('astro.config.ts') ?? read('astro.config.mjs') ?? '';
    rendering = /output:\s*['"]server['"]/.test(cfg) ? 'ssr-hybrid' : 'ssg-default';
    routes = exists('src/pages') ? count(join(dir, 'src/pages')) : 0;
  } else if (has('next')) { framework = 'next'; version = ver('next');
    const app = exists('app') || exists('src/app'); const pages = exists('pages') || exists('src/pages');
    rendering = app && pages ? 'hybrid(app+pages-router)' : app ? 'app-router(ssr-iso)' : 'pages-router(ssr)';
    routes = (app ? count(join(dir, 'src/app')) + count(join(dir, 'app')) : 0) || (pages ? count(join(dir, 'src/pages')) : null);
  } else if (has('react') && has('vite')) { framework = 'react-vite'; version = ver('vite'); rendering = 'csr-default';
    routes = exists('src/App.jsx') || exists('src/App.tsx') ? 'component-tree' : null;
  } else if (has('react')) { framework = 'react'; version = ver('react'); rendering = 'csr-default';
  } else if (has('nuxt')) { framework = 'nuxt'; version = ver('nuxt'); rendering = 'ssr-ssg-mixed';
  } else if (has('@astrojs/check') || has('vue')) { framework = 'vue-family'; rendering = 'mixed';
  } else if (exists('index.html') || exists('_site') || exists('public/index.html')) { framework = 'static-html'; rendering = 'static';
    routes = countPublicHtml(dir);
  } else if (pkg?.scripts?.build) framework = 'unknown-build';

  const seoSurface = {
    sitemapConfig: has('@astrojs/sitemap') || exists('public/sitemap.xml') || exists('src/pages/sitemap.xml')
      || (framework === 'next' && (exists('src/app/sitemap.ts') || exists('app/sitemap.ts') || exists('src/app/sitemap.js'))) ? 'present' : 'absent',
    robotsConfig: exists('public/robots.txt') || (framework === 'next' && (exists('src/app/robots.ts') || exists('app/robots.ts'))) ? 'present'
      : framework === 'astro' && /@astrojs\/sitemap/.test(read('astro.config.mjs') ?? read('astro.config.ts') ?? '') ? 'present' : 'absent',
    seoComponent: findSeoComponent(dir, framework),
    buildCmd: pkg?.scripts?.build ?? null,
    startCmd: pkg?.scripts?.dev ?? pkg?.scripts?.start ?? null,
    staticOut: framework === 'astro' ? 'dist' : framework === 'next' ? (read('next.config.mjs')?.includes('output') ? 'out' : '.next') : framework === 'react-vite' ? 'dist' : null,
    hasLighthouseCI: exists('lighthouserc.js') || exists('lighthouserc.cjs') || exists('.lighthouserc.json') || exists('lighthouserc.json') || !!pkg?.lhci,
    hasTests: exists('tests') || exists('test') || exists('__tests__') || !!pkg?.scripts?.test || exists('playwright.config.ts'),
    testCmd: pkg?.scripts?.test ?? null,
  };

  return { dir, framework, version, rendering, routes, pm, deps: Object.keys(deps).length, seoSurface,
    note: rendering === 'csr-default' ? 'CSR: delivered HTML may lack SEO content; always verify delivered bytes' : null };
}

function findSeoComponent(dir, fw) {
  const hits = [];
  const scan = (d, depth) => {
    if (depth > 4 || !existsSync(d)) return;
    for (const e of readdirSync(d, { withFileTypes: true })) {
      if (['node_modules', '.git', 'dist', '.next', '.astro', 'out'].includes(e.name)) continue;
      const p = join(d, e.name);
      if (e.isDirectory()) scan(p, depth + 1);
      else if (/seo|meta|head/i.test(e.name) && /\.(astro|tsx|jsx|js|ts|vue|svelte)$/.test(e.name)) hits.push(p.replace(dir + '/', ''));
    }
  };
  scan(dir, 0);
  return hits.slice(0, 5);
}
function count(d) { if (!existsSync(d)) return 0;
  try { return readdirSync(d, { recursive: true }).filter((f) => /\.[ah]?(?:tsx|jsx|astro|md|vue|svelte)$|\.tsx?$/.test(String(f))).length; } catch { return -1; } }
function countPublicHtml(dir) {
  const pub = join(dir, 'public'); const site = join(dir, '_site'); const root = join(dir, 'html');
  for (const d of [pub, site, root]) if (existsSync(d)) { try {
    return readdirSync(d, { recursive: true }).filter((f) => String(f).endsWith('.html')).length; } catch {} }
  return existsSync(join(dir, 'index.html')) ? 1 : 0;
}
