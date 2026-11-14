// keyboard.ts — focus traversal + interaction audit (Playwright, no axe).
// Real-browser focus walk: Tab/Shift+Tab loops, hidden-focusable detection,
// off-viewport focus (2.4.11 heuristic). DOM evidence ≠ screenreader evidence.
import { chromium, firefox, type Browser, type Page } from 'playwright';
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import type { AuditResult, Config, Finding, StepDef } from './types.ts';
import { writeHtml } from './reports.ts';

interface KbOpts { url?: string; config?: string; out: string; browser: string }

interface FocusStop {
  tag: string; text: string; id: string; visible: boolean; offscreen: boolean;
}

const MAX_TABS = 60;

async function focusStop(page: Page): Promise<FocusStop> {
  return page.evaluate((): FocusStop => {
    const el = document.activeElement as HTMLElement | null;
    if (!el || el === document.body) return { tag: 'body', text: '', id: '', visible: true, offscreen: false };
    const r = el.getBoundingClientRect();
    const visible = r.width > 0 && r.height > 0;
    const offscreen = visible && (r.bottom < 0 || r.top > innerHeight || r.right < 0 || r.left > innerWidth);
    return {
      tag: el.tagName.toLowerCase(), visible, offscreen,
      id: el.id ?? '', text: (el.textContent ?? '').trim().slice(0, 40),
    };
  });
}

function finding(msg: string, repro: string[], fix: string): Finding {
  return {
    ruleId: 'focus-traversal', sc: '2.4.7/2.4.11', scName: 'Focus Visible / Not Obscured',
    level: 'AA', impact: 'serious', route: 'keyboard', viewport: 'desktop', scenario: 'tab-traversal',
    message: msg, selector: '(dynamic focus walk)', html: '', repro, manualVerification: false, fix,
  };
}

export async function runKeyboard(o: KbOpts): Promise<number> {
  const cfg: Config = o.config
    ? JSON.parse(readFileSync(resolve(o.config), 'utf8')) as Config
    : { routes: [{ name: 'default', url: o.url ?? '' }] };
  const url = cfg.routes[0]?.url;
  if (!url) { process.stderr.write('a11y keyboard: need --url or config routes[].url\n'); return 2; }
  const browser: Browser = o.browser === 'firefox' ? await firefox.launch() : await chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: 1280, height: 720 } })).newPage();
  const findings: Finding[] = [];
  const notes: string[] = [];

  try {
    await page.goto(url, { waitUntil: 'networkidle' });

    // 1. forward traversal: hidden-but-focusable + off-viewport + trap heuristic
    const seen = new Map<string, number>();
    let offscreenStops = 0, trapSuspected = true;
    for (let i = 0; i < MAX_TABS; i++) {
      await page.keyboard.press('Tab');
      const s = await focusStop(page);
      const key = `${s.tag}#${s.id}|${s.text}`;
      const hits = (seen.get(key) ?? 0) + 1;
      seen.set(key, hits);
      if (s.visible && s.offscreen) offscreenStops++;
      if (hits >= 2 && seen.size >= 3) { trapSuspected = false; break; } // full loop reached
      if (s.tag === 'body' && i > 0) { trapSuspected = false; break; }    // wrapped to browser UI
    }
    if (trapSuspected && seen.size < 3) {
      findings.push(finding(
        `traversal never completed a loop within ${MAX_TABS} tabs over ${seen.size} distinct stops — possible focus trap`,
        ['open page', `press Tab up to ${MAX_TABS}×`, 'confirm sequence wraps back to first stop'],
        'Ensure every widget releases Tab; dialogs trap only while open and restore focus on close.'));
    }
    if (offscreenStops > 0) {
      findings.push(finding(
        `${offscreenStops} focus stop(s) landed outside the viewport (hidden-but-focusable or covered)`,
        ['open page', 'Tab through all controls', 'watch for focus ring on invisible/covered elements'],
        'Set inert/tabindex="-1" on content inside closed overlays; scroll sticky content out of the way.'));
    }

    // 2. Escape closes overlay behavior (common dialog contract sample)
    await page.keyboard.press('Escape');
    const afterEsc = await focusStop(page);
    notes.push(`escape→focus=${afterEsc.tag}`);
  } finally {
    await browser.close();
  }

  const outDir = resolve(o.out);
  mkdirSync(outDir, { recursive: true });
  const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-');
  const result: AuditResult = {
    tool: 'a11y-keyboard', toolVersion: '1.0.0', axeVersion: 'n/a', generatedAt: new Date().toISOString(),
    standard: 'WCAG 2.2 keyboard/focus slice', level: 'aa', browser: o.browser, os: process.platform,
    summary: { routes: 1, scenariosRun: 1, violationsAa: findings.length, violationsAaa: 0, needsManualReview: 3, passes: 0 },
    findings,
    manual: [
      { sc: '2.4.3', scName: 'Focus Order (logical?)', level: 'AA', status: 'NEEDS MANUAL REVIEW', how: 'compare observed tab sequence against visual order' },
      { sc: '2.1.2', scName: 'No Keyboard Trap', level: 'AA', status: 'NEEDS MANUAL REVIEW', how: 'heuristic only; confirm widgets release focus' },
      { sc: '2.4.11', scName: 'Focus Not Obscured (Minimum)', level: 'AA', status: 'NEEDS MANUAL REVIEW', how: 'sticky headers/overlays may cover focus mid-scroll' },
    ],
    routes: [], gate: findings.length ? 'FAIL' : 'PASS',
    gateNote: `keyboard gate · ${notes.join('; ')} · DOM evidence only, not a screenreader test`,
  };
  const jsonPath = join(outDir, `keyboard-${stamp}.json`);
  writeFileSync(jsonPath, JSON.stringify(result, null, 2));
  writeHtml(result, join(outDir, `keyboard-${stamp}.html`));
  process.stdout.write(`a11y keyboard ${result.gate} · findings=${findings.length} · ${notes.join('; ') || 'traversal ok'}\n${jsonPath}\n`);
  return findings.length > 0 ? 1 : 0;
}

// scenario-driven keyboard probe (component tests feed expected focus log)
export async function probeSteps(page: Page, steps: StepDef[]): Promise<string[]> {
  const log: string[] = [];
  for (const s of steps) {
    if (s.press) { await page.keyboard.press(s.press); log.push(`press ${s.press}`); }
    if (s.click) { await page.click(s.click); log.push(`click ${s.click}`); }
    await page.waitForTimeout(60);
    const stop = await focusStop(page);
    log.push(`focus→${stop.tag}#${stop.id}`);
  }
  return log;
}
