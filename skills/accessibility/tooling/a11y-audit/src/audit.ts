// audit.ts — core engine: Playwright + axe-core, level-aware, scenario-aware.
import { chromium, firefox, type Browser, type Page } from 'playwright';
import axe from 'axe-core';
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { createRequire } from 'node:module';
import type { AuditResult, Config, Finding, Level, RouteResult, StepDef, ManualItem } from './types.ts';
import { writeHtml, writeJunit, writeSarif } from './reports.ts';
import { scName, levelOf, fixHint } from './catalog.ts';

export interface AuditOpts {
  url?: string; config?: string; out: string; level: Level; strictAaa: boolean;
  formats: string[]; viewports?: string; browser: string; name?: string;
}

// Rules axe disables by default that ARE normative WCAG — enable per level.
const AA_DISABLED = ['aria-roledescription', 'audio-caption', 'target-size'];
const AAA_DISABLED = ['color-contrast-enhanced', 'identical-links-same-purpose', 'meta-refresh-no-exceptions'];

const VIEWPORTS: Record<string, { width: number; height: number }> = {
  desktop: { width: 1280, height: 720 },
  mobile: { width: 375, height: 667 },
};

function loadConfig(path: string): Config {
  const raw = readFileSync(resolve(path), 'utf8');
  const parsed: unknown = JSON.parse(raw);
  if (typeof parsed !== 'object' || parsed === null || !('routes' in parsed)) {
    throw new Error('config: "routes" must be an array');
  }
  const cfg = parsed as Config; // validated boundary: config file, project-owned shape
  if (!Array.isArray(cfg.routes)) throw new Error('config: "routes" must be an array');
  return cfg;
}

function errText(err: unknown): string {
  const msg = err instanceof Error ? err.message : String(err);
  return msg.split('\n')[0];
}

// ${ENV_VAR} placeholders keep credentials out of config and reports.
function envExpand(s: string): string {
  return s.replace(/\$\{(\w+)\}/g, (_, k: string) => process.env[k] ?? '');
}
function isSecretish(selector: string, value: string): boolean {
  return /password|pass|token|secret|otp/i.test(selector) || /\$\{A11Y_/.test(value);
}
function maskStep(s: StepDef): string {
  if (s.fill) return `fill "${s.fill[0]}" with "${isSecretish(s.fill[0], s.fill[1]) ? '••••••' : envExpand(s.fill[1])}"`;
  if (s.click) return `click "${s.click}"`;
  if (s.press) return `press ${s.press}`;
  if (s.hover) return `hover "${s.hover}"`;
  if (s.waitFor) return `wait for "${s.waitFor}"`;
  if (s.waitMs) return `wait ${s.waitMs}ms`;
  return 'noop';
}

async function runSteps(page: Page, steps: StepDef[], repro: string[]): Promise<void> {
  for (const s of steps) {
    const i = repro.length + 1;
    try {
      if (s.waitFor) await page.waitForSelector(envExpand(s.waitFor), { timeout: 5000 });
      else if (s.click) await page.click(envExpand(s.click), { timeout: 5000 });
      else if (s.fill) await page.fill(envExpand(s.fill[0]), envExpand(s.fill[1]), { timeout: 5000 });
      else if (s.press) await page.keyboard.press(s.press);
      else if (s.hover) await page.hover(envExpand(s.hover), { timeout: 5000 });
      else if (s.waitMs) await page.waitForTimeout(s.waitMs);
      if (s.expect) await page.waitForSelector(envExpand(s.expect), { state: 'visible', timeout: 4000 });
      repro.push(`${i}. ${maskStep(s)}`);
    } catch (err) {
      repro.push(`${i}. ${maskStep(s)}  [FAILED: ${errText(err)}]`);
    }
  }
}

interface AxeNodeLike { target: string[] | string; html?: string }
interface AxeRuleLike { id: string; help: string; impact?: string | null; nodes: AxeNodeLike[] }
interface AxeResultLike {
  violations: AxeRuleLike[]; incomplete: AxeRuleLike[];
  passes: unknown[]; inapplicable: unknown[];
}

function nodeTargets(n: AxeNodeLike): string {
  return Array.isArray(n.target) ? n.target.join(' ') : String(n.target);
}

const AXE_PATH = createRequire(import.meta.url).resolve('axe-core/axe.js');

// Direct axe run: runOnly-by-tag + explicit enabling of default-off normative
// rules (the `rules` option merges, so off-by-default WCAG rules join the run).
async function axeRun(page: Page, level: Level, route: string, viewport: string, scenario: string, repro: string[]) {
  const enabled = level === 'aaa' ? [...AA_DISABLED, ...AAA_DISABLED] : AA_DISABLED;
  const tags = level === 'aaa'
    ? ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'wcag2aaa', 'wcag21aaa']
    : ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'];
  await page.addScriptTag({ path: AXE_PATH });
  const res = (await page.evaluate(async (args: { tags: string[]; enabled: string[] }) => {
    const rules: Record<string, { enabled: boolean }> = {};
    for (const r of args.enabled) rules[r] = { enabled: true };
    const ax = (window as unknown as {
      axe: { run: (el: Element | Document, o: unknown) => Promise<unknown> };
    }).axe;
    return ax.run(document, {
      runOnly: { type: 'tag', values: args.tags },
      rules, resultTypes: ['violations', 'incomplete', 'passes', 'inapplicable'],
    });
  }, { tags, enabled })) as unknown as AxeResultLike;
  const findings: Finding[] = [];
  const incomplete: Finding[] = [];
  const toFinding = (v: AxeRuleLike, n: AxeNodeLike, manual: boolean): Finding => ({
    ruleId: v.id, sc: v.id, scName: scName(v.id),
    level: levelOf(v.id), impact: v.impact ?? 'unknown',
    route, viewport, scenario, message: v.help,
    selector: nodeTargets(n), html: (n.html ?? '').slice(0, 300),
    fix: manual ? undefined : fixHint(v.id), repro: [...repro], manualVerification: manual,
  });
  for (const v of res.violations) for (const n of v.nodes) findings.push(toFinding(v, n, false));
  for (const v of res.incomplete) for (const n of v.nodes) incomplete.push(toFinding(v, n, true));
  return { findings, passes: res.passes.length, incomplete, inapplicable: res.inapplicable.length };
}

// Criteria axe cannot decide; always surfaced as manual review items.
const MANUAL_CRITERIA: [string, string][] = [
  ['1.2.1', 'audio-only/video-only prerequisites'], ['1.2.4', 'live captions'],
  ['2.4.5', 'multiple ways (headings/links/labels correct?)'], ['3.1.1', 'page language programmatically set'],
  ['3.3.2', 'instructions/labels present where needed'], ['3.3.3', 'error suggestions where recoverable'],
];

export async function runAudit(o: AuditOpts): Promise<number> {
  const cfg: Config = o.config ? loadConfig(o.config) : { routes: [{ name: o.name ?? 'default', url: o.url ?? '' }] };
  if (!cfg.routes.length || !cfg.routes[0].url) {
    process.stderr.write('a11y audit: need --url or config with routes[].url\n'); return 2;
  }
  const level = o.level;
  const viewports = (o.viewports === 'both' || !o.viewports ? ['desktop', 'mobile']
    : [o.viewports as 'desktop' | 'mobile']);
  const browserKind = (o.browser || cfg.browser || 'chromium') as 'chromium' | 'firefox';
  const browser: Browser = browserKind === 'firefox' ? await firefox.launch() : await chromium.launch();
  const results: RouteResult[] = [];
  let passes = 0, manual = 0;
  const allFindings: Finding[] = [];

  for (const route of cfg.routes) {
    for (const vp of viewports) {
      const ctx = await browser.newContext({ viewport: VIEWPORTS[vp] });
      const page = await ctx.newPage();
      const scenes = [{ name: 'initial', steps: [] as StepDef[] }, ...(route.scenarios ?? [])];
      for (const scene of scenes) {
        const repro: string[] = [`open ${route.url}`];
        try {
          await page.goto(route.url, { waitUntil: 'networkidle', timeout: cfg.timeoutMs ?? 20000 });
          if (route.auth && cfg.auth) await runSteps(page, cfg.auth.steps, repro);
          await runSteps(page, scene.steps, repro);
          const r = await axeRun(page, level, route.name, vp, scene.name, repro);
          passes += r.passes;
          manual += r.incomplete.length;
          allFindings.push(...r.findings, ...r.incomplete);
          results.push({
            route: route.name, url: route.url, viewport: vp, scenario: scene.name,
            pass: r.passes, incomplete: r.incomplete, violations: r.findings,
            inapplicableCount: r.inapplicable, notes: [],
          });
        } catch (err) {
          results.push({
            route: route.name, url: route.url, viewport: vp, scenario: scene.name, pass: 0,
            incomplete: [], violations: [], inapplicableCount: 0,
            notes: ['navigation/analysis failed: ' + errText(err)],
          });
        }
      }
      await ctx.close();
    }
  }
  await browser.close();

  // dedupe: same rule + same element + same route/viewport collapse; scenarios merged into message
  const dedup = new Map<string, Finding>();
  for (const f of allFindings) {
    const k = `${f.ruleId}|${f.selector}|${f.route}|${f.viewport}`;
    const prev = dedup.get(k);
    if (prev) {
      if (!prev.scenario.includes(f.scenario)) prev.message = `${prev.message} (also: ${f.scenario})`;
    } else dedup.set(k, f);
  }
  const findings = [...dedup.values()];
  const autoBlocking = findings.filter((f) => !f.manualVerification && (level === 'a' ? f.level === 'A' : f.level !== 'AAA'));
  const aaaFindings = findings.filter((f) => f.level === 'AAA' && !f.manualVerification);

  const manualList: ManualItem[] = MANUAL_CRITERIA.map(([sc, name]) => ({
    sc, scName: name, level: 'AA', status: 'NEEDS MANUAL REVIEW',
    how: 'Not decidable from DOM alone — verify per WCAG-EM sample with AT/user. See references/audit-methodology.md',
  }));

  const gateFail = autoBlocking.length > 0 || (o.strictAaa && aaaFindings.length > 0);
  const result: AuditResult = {
    tool: 'a11y-audit', toolVersion: '1.0.0', axeVersion: axe.version,
    generatedAt: new Date().toISOString(),
    standard: 'WCAG 2.2 (W3C Recommendation, consolidated 2024-12-12)', level,
    browser: browserKind, os: process.platform,
    summary: {
      routes: cfg.routes.length, scenariosRun: results.length,
      violationsAa: autoBlocking.length, violationsAaa: aaaFindings.length,
      needsManualReview: manual + manualList.length, passes,
    },
    findings, manual: manualList, routes: results,
    gate: gateFail ? 'FAIL' : 'PASS',
    gateNote: `Automated gate ${gateFail ? 'FAILED' : 'PASSED'} — this is a gate, not a conformance claim. ` +
      `${manual} automated "needs review" node(s) + ${manualList.length} criteria need manual verification before any WCAG claim.`,
  };
  const outDir = resolve(o.out);
  mkdirSync(outDir, { recursive: true });
  const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-');
  const jsonPath = join(outDir, `a11y-${stamp}.json`);
  writeFileSync(jsonPath, JSON.stringify(result, null, 2));
  writeFileSync(join(outDir, 'latest.json'), JSON.stringify(result, null, 2));
  for (const fmt of o.formats) {
    if (fmt === 'html') writeHtml(result, join(outDir, `a11y-${stamp}.html`));
    if (fmt === 'junit') writeJunit(result, join(outDir, `a11y-${stamp}.junit.xml`));
    if (fmt === 'sarif') writeSarif(result, join(outDir, `a11y-${stamp}.sarif`));
  }
  process.stdout.write(
    `a11y audit ${result.gate} · level=${level} · blocking=${autoBlocking.length} ` +
    `· advisory(AAA)=${aaaFindings.length} · manual=${result.summary.needsManualReview} ` +
    `· passes=${passes} · scenarios=${result.summary.scenariosRun}\nreport: ${jsonPath}\n`);
  return gateFail ? 1 : 0;
}
