// env.ts — `a11y check`: environment probe with honest capability matrix.
import { execSync } from 'node:child_process';
import { existsSync, readdirSync } from 'node:fs';
import { homedir } from 'node:os';

function probe(cmd: string): string {
  try { return execSync(cmd, { encoding: 'utf8', timeout: 8000 }).trim().split('\n')[0]; }
  catch { return 'MISSING'; }
}

export function runEnvCheck(): number {
  const browsers = existsSync(`${homedir()}/.cache/ms-playwright`)
    ? readdirSync(`${homedir()}/.cache/ms-playwright`).filter((d) => /^(chromium|firefox)/.test(d)).sort().join(', ')
    : 'none cached';
  const lines = [
    ['node', process.version],
    ['playwright browsers cached', browsers || 'none'],
    ['firefox (system)', probe('firefox --version 2>/dev/null')],
    ['orca (screen reader)', probe('orca --version 2>/dev/null')],
    ['desktop session', `${process.env.XDG_SESSION_TYPE ?? '?'} / ${process.env.XDG_CURRENT_DESKTOP ?? '?'}`],
  ];
  const width = Math.max(...lines.map((l) => l[0].length));
  process.stdout.write('a11y environment check\n');
  for (const [k, v] of lines) process.stdout.write(`  ${k.padEnd(width)}  ${v}\n`);
  process.stdout.write(
    '  real-SR automation: Orca+Firefox on Wayland/KDE requires AT-SPI bus; Guidepup Orca ' +
    'support is experimental — verify before CI use (references/screenreaders.md).\n');
  return 0;
}
