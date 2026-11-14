# Vitest unit & integration (framework-agnostic)

Vitest 5.1.0 baseline; peer `vite ^6.4.0 || ^7 || ^8` — a project on older
Vite installs the matching Vitest major instead. Config in `vitest.config.*`
or the `test` block of `vite.config.*` (existing wins).

## Layers

```ts
// unit — node env, ms, no DOM
import { describe, it, expect, vi } from 'vitest';
import { parseAmount } from '../src/lib/money';
describe('parseAmount', () => {
  it('parses localized input', () => expect(parseAmount('1.234,56', 'de')).toBeCloseTo(1234.56));
});

// integration — real component, msw network, user behavior
import { render, screen } from '@testing-library/*'; // wrapper per framework
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
const server = setupServer(http.get('/api/cart', () => HttpResponse.json({ items: 2 })));
beforeAll(() => server.listen()); afterAll(() => server.close());
// test: user-visible result of an interaction, not internal calls
```

Component wrappers: TL/react, TL/vue (+@vitejs/plugin-vue), TL/svelte
(svelte preprocess). Astro: unit-test exported functions / content loaders;
`.astro` rendering goes to Playwright. Server components: test data
functions + E2E the page.

## Mocking discipline

- `vi.mock` only module boundaries you don't own (fetch libs, third-party).
- Timers `vi.useFakeTimers` + advance, never `setTimeout` waits.
- msw over `vi.mock(fetch)`: keeps request semantics, ports to E2E truths.
- Never mock the unit under test; never mock internals (private fns,
  call-count assertions on own modules).

## Snapshots (Vitest built-in)

`toMatchSnapshot`/`toMatchInlineSnapshot` for stable transforms (parsers,
formatters, small markup). Not for layout, not for full pages. `vitest -u`
on intentional change; diff shown in report. Browser-mode snapshots →
Playwright `toHaveScreenshot` instead.

## Coverage

```
vitest run --coverage    # @vitest/coverage-v8, same minor as vitest
```
Report the number + the files under 50%; thresholds = reality + ratchet.
Coverage is a map, not a goal: state uncovered risk in the report.

## Commands

```
vitest run                    # CI      (no watch)
vitest                        # dev     (watch)
vitest run --changed          # PR lane (git-diff scoped)
vitest related <file>         # after a fix: what covers this?
vitest run --reporter=html    # optional artifact (needs @vitest/ui)
```

## Failure triage → Workflow E

1. Red test = the reproduction. `vitest run path -t "name"` isolates it.
2. Stack frames → source file (`vitest related src/x.ts` confirms coverage).
3. Fix source; `vitest related` green; file's suite green.
4. No test existed for the fix → add one (the fix's regression lock).
