# Testing & QA — lanes by project reality

Pick lanes the project needs; run them before declaring done. Report each lane
with its actual result (testing.md truth ladder in SKILL.md).

## Lane table

| Lane | Tool | When | Command (baseline) |
|---|---|---|---|
| Types | `astro check` | every project, CI | `npx astro check` |
| Lint/format | eslint + prettier | project has config | `npm run lint` |
| Unit/lib | vitest | pure logic in `lib/`, schemas | `npx vitest run` |
| Component | vitest + browser mode or node render | shared components | `npx vitest run` |
| E2E | playwright (firefox default per house rule) | routes + flows that matter | `npx playwright test` |
| A11y | axe-core in playwright | user-facing templates | in e2e lane |
| SEO/meta | crawl + assert | content sites | script or e2e |
| Perf | lighthouse CI | before/after a change | `npx lighthouse <url>` |
| Build | `astro build` | every PR | required |
| SSR smoke | preview + fetch routes | on-demand routes exist | `astro preview` + curl |

Minimum honest gate: `astro check` + `astro build` pass; add lanes as surface
grows. Do not pretend a lane ran.

## What to test (not framework plumbing)

- lib functions: date/slug/format edge cases; schema validation accept/reject.
- Content: collection queries return expected counts/filters (draft excluded).
- Routes: status codes (200/404/redirect), key text, head tags on templates.
- Islands: island renders and is interactive (playwright click), not just
  present in HTML.
- Actions: happy path + validation failure shape.
- Regression: bugfix gets a test that failed before the fix.

## SaaS/CMS note

External sources: fixture the payload (JSON file) — tests hit no live CMS.

## CI shape (GitHub Actions, all lanes)

```yaml
- run: npm ci
- run: npx astro check
- run: npx astro build
- run: npx vitest run            # if present
- run: npx playwright test       # if present (install browsers w/ cache)
- run: npx lighthouse http://localhost:4321 --output=json # preview first
```
Cache npm + playwright browsers; fail on lint/type/build; perf budget fail
soft (report) until budgets are agreed.
