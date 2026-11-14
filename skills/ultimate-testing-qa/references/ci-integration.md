# CI/CD integration (additive, correct exit codes)

Golden rule: QA jobs extend the project's pipeline; existing jobs keep
their contracts. Exit codes are the gate — `--reporter` never swallows them
(`exit code 0 == green`, both runners).

## GitHub Actions

Full job in `assets/github-actions-qa.yml`. Shape:
1. checkout → setup-node (pm-correct cache: npm/pnpm/yarn/bun flags) →
   `pm install --frozen-lockfile`
2. unit lane: `vitest run --coverage` (PR: `--changed`)
3. e2e lane: `playwright install --with-deps chromium firefox webkit`
   (cache `~/.cache/ms-playwright`) → `playwright test`; artifacts:
   `playwright-report/`, `test-results/`, traces on failure
4. report upload: `actions/upload-artifact` per lane; PR comment optional
5. `if: always()` on uploads so red lanes still deliver evidence.

Docker-based projects: run lanes inside the project's own compose/dev
container (same Node, same fonts → same visual diffs); browsers need
`--with-deps` or a Playwright base image.

## Gate policy

- PR: fail on any red unit/integration + tier-1 journeys; visual diff →
  artifact + review (NEEDS REVIEW), not red.
- main/nightly: full matrix, coverage thresholds at ratchet level.
- Flakes: `retries: process.env.CI ? 1 : 0` max, then triage trace.

## VCS-local parity

The CI commands ARE the local commands (`npm test`, `npm run test:e2e`).
A gate nobody can run locally is a gate that will surprise someone at 2am;
both are documented in README with the report output path.

## Other systems

GitLab: same lanes as `script:` jobs, `artifacts:paths:` for reports.
Local hook: lint-staged runs `vitest related` per staged file; full matrix
stays on CI.
