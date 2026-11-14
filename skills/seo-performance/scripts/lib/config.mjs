/**
 * config.mjs — layered config: skill defaults -> profile -> project file -> flags.
 * Project file: <project>/.seo-performance.json (or config field of package.json).
 */
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const SKILL_ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');

export function loadConfig({ profile = 'default', projectDir = null, flags = {} } = {}) {
  const read = (p) => { try { return JSON.parse(readFileSync(p, 'utf8')); } catch { return null; } };
  const deep = (a, b) => { const o = { ...a }; for (const [k, v] of Object.entries(b ?? {})) {
    if (v && typeof v === 'object' && !Array.isArray(v)) o[k] = deep(a[k] ?? {}, v); else o[k] = v; } return o; };
  let cfg = read(join(SKILL_ROOT, 'config', 'default.json')) ?? {};
  const prof = read(join(SKILL_ROOT, 'config', `${profile}.json`));
  if (prof) { if (prof.$extends && prof.$extends !== 'default.json') cfg = deep(cfg, read(join(SKILL_ROOT, 'config', prof.$extends)) ?? {});
    cfg = deep(cfg, strip(prof)); }
  if (projectDir) {
    const pf = read(join(projectDir, '.seo-performance.json'));
    if (pf) cfg = deep(cfg, strip(pf));
    else { const pkg = read(join(projectDir, 'package.json')); if (pkg?.['seo-performance']) cfg = deep(cfg, strip(pkg['seo-performance'])); }
  }
  cfg = deep(cfg, strip(flags));
  return cfg;
}
const strip = (o) => Object.fromEntries(Object.entries(o).filter(([k]) => !k.startsWith('$')));

export function loadBudgets(projectDir = null, skillRoot = SKILL_ROOT) {
  const read = (p) => { try { return JSON.parse(readFileSync(p, 'utf8')); } catch { return null; } };
  return (projectDir && (read(join(projectDir, 'performance-budgets.json')) ?? read(join(projectDir, '.seo-performance-budgets.json'))))
    ?? read(join(skillRoot, 'config', 'performance-budgets.json'))
    ?? { rules: [], tolerancePct: 10, retries: 2 };
}
