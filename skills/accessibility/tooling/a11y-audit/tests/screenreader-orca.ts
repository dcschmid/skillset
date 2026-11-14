// SR evidence harness: real Orca (via Guidepup) + Firefox on this Fedora/KDE
// Wayland host. Verdict only from real speech capture. Runnable:
//   node tests/screenreader-orca.ts [outDir]
// Requirements: Guidepup assets (`npx @guidepup/setup install` — project scope,
// already run on this machine 2026-11-14), Firefox, AT-SPI bus, session D-Bus.
import { firefox } from 'playwright';
import { orca } from '@guidepup/guidepup';
import { mkdirSync, writeFileSync } from 'node:fs';
import { setTimeout as sleep } from 'node:timers/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const fixture = join(here, '..', 'fixtures', 'clean.html');
const outDir = process.argv[2] ?? join(here, '..', 'out');
mkdirSync(outDir, { recursive: true });

const EXPECTED = [
  'Accessible components reference', // h1
  'Skip to main content',            // skip link
  'Email address',                   // labelled input
];

let verdict = 'SR_UNAVAILABLE';
const lines: string[] = [];
try {
  const browser = await firefox.launch();
  const page = await (await browser.newContext()).newPage();
  await page.goto('file://' + fixture);
  await page.getByRole('heading', { level: 1 }).waitFor();

  await orca.start({ capture: true });
  const cmds = orca.keyboardCommands;
  const speechOf = (): string[] => {
    const log = orca.spokenPhraseLog;
    return Array.isArray(log) ? log.map(String) : [];
  };
  await orca.perform(cmds.CaretNavigator.StartOfFile);
  await sleep(250);
  const heard = new Set<string>();
  const capture = () => {
    const text = speechOf().join(' ');
    for (const e of EXPECTED) if (text.includes(e)) heard.add(e);
  };
  capture();
  for (let i = 0; i < 40; i++) {
    await orca.perform(cmds.StructuralNavigator.NextHeading);
    await sleep(200);
    capture();
  }
  await orca.perform(cmds.CaretNavigator.StartOfFile);
  for (let i = 0; i < 15; i++) {
    await orca.perform(cmds.StructuralNavigator.NextLink);
    await sleep(200);
    capture();
  }
  for (let i = 0; i < 10; i++) {
    await orca.perform(cmds.CaretNavigator.NextLine);
    await sleep(200);
    capture();
  }
  const fullLog = speechOf();
  writeFileSync(join(outDir, 'sr-speech.json'), JSON.stringify({
    spoken: fullLog, expected: EXPECTED,
    observed: EXPECTED.filter((e) => fullLog.some((s) => s.includes(e))),
  }, null, 2));
  const missing = EXPECTED.filter((e) => !heard.has(e));
  if (fullLog.length === 0) verdict = 'SR_ENV_FAIL';
  else verdict = missing.length === 0 ? 'SR_PASS' : 'SR_INCOMPLETE';
  lines.push(`speech lines=${fullLog.length} heard=${heard.size}/${EXPECTED.length}`);
  if (missing.length) lines.push('missing=' + missing.join('|'));
  await orca.stop();
  await browser.close();
} catch (err) {
  verdict = 'SR_ENV_FAIL';
  const e = err as Error & { cause?: { message?: string } };
  lines.push('error: ' + (e.message?.split('\n')[0] ?? String(err)));
  if (e.cause) lines.push('cause: ' + String(e.cause.message ?? e.cause).split('\n')[0]);
  lines.push('fallback: manual Orca workflow in references/screenreaders.md');
}
writeFileSync(join(outDir, 'sr-verdict.txt'), verdict + '\n' + lines.join('\n') + '\n');
process.stdout.write(`verdict ${verdict} · ${lines.join(' · ')}\n`);
process.exit(verdict === 'SR_PASS' ? 0 : 1);
