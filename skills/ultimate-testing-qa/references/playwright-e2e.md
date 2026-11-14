# Playwright E2E, browser audits, responsive & visual

Baselines: Playwright 1.65.1; assertions from `@playwright/test` (`expect`
is NOT exported by the `playwright` library package — that one has
`devices`). All snippets verified against current docs (vitest.dev/
playwright.dev checked 2026-11-14).

## Server lifecycle (audit + E2E)

Start the project's OWN command (`dev` for CSR-hydration truths, `preview`
after build for SSG truths). Wait for the port; never `sleep`.

```ts
// playwright.config.ts — reuse project commands, all three engines
import { defineConfig, devices } from '@playwright/test';
export default defineConfig({
  testDir: './e2e',
  use: { baseURL: process.env.PW_BASE ?? 'http://127.0.0.1:4321', trace: 'on-first-retry' },
  reporter: [['html', { open: 'never' }], ['list']],
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'mobile', use: { ...devices['Pixel 7'] } },
  ],
  webServer: { command: 'npm run dev', url: 'http://127.0.0.1:4321', reuseExistingServer: !process.env.CI },
});
```

## Runtime-error auditing (Workflow C core)

```ts
import { test, expect } from '@playwright/test';

test('route health: console, exceptions, network', async ({ page }) => {
  const defects: string[] = [];
  page.on('console', m => { if (m.type() === 'error') defects.push(`console: ${m.text()}`); });
  page.on('pageerror', e => defects.push(`exception: ${e.message}`));
  page.on('requestfailed', r => defects.push(`net-fail: ${r.url()} ${r.failure()?.errorText}`));
  page.on('response', r => { if (r.status() >= 400) defects.push(`http ${r.status()}: ${r.url()}`); });

  await page.goto('/route-under-test', { waitUntil: 'networkidle' });
  expect(defects, defects.join('\n')).toEqual([]);
  await expect(page.locator('main h1')).toBeVisible(); // content truth
});
```

Hydration note: CSR shells pass HTTP but fail `pageerror`; networkidle +
element assertions catch that class. SSG: additionally assert the server
HTML contains content (`page.content()` before JS settles) — delivered-HTML
truth shared with the seo-performance skill.

## Forms & validation

```ts
test('signup validates then submits', async ({ page }) => {
  await page.goto('/signup');
  await page.getByLabel('Email').fill('not-an-email');
  await page.getByRole('button', { name: /sign up/i }).click();
  await expect(page.getByRole('alert')).toContainText(/valid email/i); // client validation
  await page.getByLabel('Email').fill('a@b.co');
  await page.getByLabel(/^Password/).fill('hunter2hunter2');
  await page.getByRole('button', { name: /sign up/i }).click();
  await expect(page).toHaveURL(/dashboard|verify/);                      // server result
});
```

Locators: `getByRole/getByLabel/getByText` first; CSS only as last resort
(also proves the a11y tree works — failing label locators are a11y defects).

## Auth & protected flows

Login once, `storageState` to a file, reuse via `use: { storageState }` in a
dependency project (`dependencies: ['setup']`). Secrets from `.env[.*]`
read at runtime; never committed into specs or reports.

## Responsive

`devices['Pixel 7']`/`'iPhone 13'`/desktop widths + 320px edge. Per tier-1
route assert: no horizontal overflow
(`document.documentElement.scrollWidth <= clientWidth`), nav usable
(hamburger opens), images `object-fit` intact. Breakpoints come from the
project's CSS, not from a fixed list.

## Visual regression

`await expect(page).toHaveScreenshot('home.png', { maxDiffPixelRatio: 0.01 })`
— only tier-1 surfaces with a committed baseline dir in git. `--update-snapshots`
after intentional design change, show the diff in the report. Fonts: CI pins
with the same image as dev (font antialiasing = false diffs).

## Cross-browser & failure repro

Three engines in config above; failures: `--trace on-first-retry` keeps a
trace → `npx playwright show-trace trace.zip` is the reproduction artifact
for Workflow E. Flaky ≠ retry harder: max 1 retry, trace triaged, then
fix source or quarantine with an issue reference.

## API endpoints

Two layers: contract tests hit the API directly (`request` fixture, status +
shape assertions, no browser) and UI tests consume it through the page. msw
covers component level only — E2E talks to real endpoints (or the documented
test backend).
