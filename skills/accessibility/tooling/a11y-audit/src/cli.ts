// a11y — WCAG 2.2 audit CLI (axe-core + Playwright). Entry point.
// Runs directly on Node >= 22.18 via type-stripping; erasable-syntax-only TS.
import { parseArgs } from 'node:util';
import { runAudit } from './audit.ts';
import { runKeyboard } from './keyboard.ts';
import { renderReport, compareResults } from './reports.ts';
import { runEnvCheck } from './env.ts';

const HELP = `a11y — WCAG 2.2 audit tool (axe-core + Playwright)

Usage:
  a11y audit    --url <url> [--level a|aa|aaa] [--config <file>] [--out <dir>]
                [--format json,html,junit,sarif] [--viewport desktop|mobile|both]
                [--browser chromium|firefox] [--name <label>]
  a11y audit    --config a11y.config.json            (multi-route via config)
  a11y keyboard --url <url> [--config <file>] [--out <dir>] [--browser ...]
  a11y report   <results.json> [--format html|junit|sarif] [--out <dir>]
  a11y compare  --before <a.json> --after <b.json> [--out <dir>]
  a11y check                                             (environment probe)

Exit codes: 0 no blocking violations · 1 blocking violations · 2 usage/config error.
AAA findings are advisory for gates (listed separately) unless --strict-aaa.`;

async function main(): Promise<number> {
  const argv = process.argv.slice(2);
  const cmd = argv[0];
  if (!cmd || cmd === '-h' || cmd === '--help' || cmd === 'help') {
    process.stdout.write(HELP + '\n');
    return 0;
  }
  const { values } = parseArgs({
    args: argv.slice(1),
    allowPositionals: true,
    options: {
      url: { type: 'string' },
      level: { type: 'string' },
      config: { type: 'string' },
      out: { type: 'string' },
      format: { type: 'string' },
      viewport: { type: 'string' },
      browser: { type: 'string' },
      name: { type: 'string' },
      before: { type: 'string' },
      after: { type: 'string' },
      'strict-aaa': { type: 'boolean' },
    },
  });
  const level = (values.level ?? 'aa') as 'a' | 'aa' | 'aaa';
  if (!['a', 'aa', 'aaa'].includes(level)) {
    process.stderr.write(`a11y: unknown level "${values.level}" (use a|aa|aaa)\n`);
    return 2;
  }
  switch (cmd) {
    case 'audit':
      return runAudit({
        url: values.url, config: values.config, out: values.out ?? 'a11y-report',
        level, strictAaa: values['strict-aaa'] === true,
        formats: (values.format ?? 'json,html').split(','),
        viewports: values.viewport, browser: values.browser ?? 'chromium',
        name: values.name,
      });
    case 'keyboard':
      return runKeyboard({
        url: values.url, config: values.config, out: values.out ?? 'a11y-report',
        browser: values.browser ?? 'chromium',
      });
    case 'report': {
      const source = argv[1];
      if (!source) { process.stderr.write('a11y report: need results.json path\n'); return 2; }
      return renderReport(source, values.format ?? 'html', values.out ?? 'a11y-report');
    }
    case 'compare':
      if (!values.before || !values.after) {
        process.stderr.write('a11y compare: need --before and --after\n'); return 2;
      }
      return compareResults(values.before, values.after, values.out ?? 'a11y-report');
    case 'check':
      return runEnvCheck();
    default:
      process.stderr.write(`a11y: unknown command "${cmd}"\n` + HELP + '\n');
      return 2;
  }
}

main().then((code) => process.exit(code)).catch((err) => {
  process.stderr.write('a11y: fatal: ' + (err instanceof Error ? err.stack ?? err.message : String(err)) + '\n');
  process.exit(2);
});
