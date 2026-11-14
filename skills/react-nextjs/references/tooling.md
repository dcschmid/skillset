# Tooling & Development Workflow

## Package manager: project's, always

Lockfile decides: `pnpm-lock.yaml`→pnpm, `yarn.lock`→yarn, `bun.lock(b)`→bun,
`package-lock.json`→npm. New project: pick by environment (pnpm where disk/CI
speed matters, npm default otherwise) and state it. No global installs;
`npx`/`pnpm dlx` for one-offs.

## New-project scaffolds

```bash
pnpm create next-app@latest app --typescript   # App Router defaults (16 line)
npm create vite@latest app -- --template react-ts
```
Then immediately: tsc strict check, lint config (eslint-plugin-react-hooks
compiler mode if Compiler on), test runner wired (testing.md), env validation
(architecture.md).

## Scripts (package.json convention)

`dev` (framework default — 16: Turbopack; webpack fallback only per local
docs), `build`, `start`, `lint`, `typecheck`, `test`, `test:e2e`. CI runs
the release-gate set (testing.md) with the lockfile (`npm ci`/`pnpm --frozen-lockfile`).

## CI/CD (GitHub Actions baseline)

node-version = project LTS; cache by lockfile; steps: install → tsc → lint →
test → build → (E2E boot build + Playwright) → artifact deploy. Fail loud on
warnings-as-errors config drift.

## Monorepos

pnpm workspaces / turbo / Nx: shared UI/types packages built or source-imported
per framework support; Next consumes workspace source via `transpilePackages`
(read local docs). Don't add a build system before a second consumer.

## Env management

`.env` files uncommitted; validation module (architecture.md 5); framework
prefix rules for public vars (security.md); secrets in host vault/CI store;
`.env.example` current.

## Vite (React-only)

Stable line; dev = native ESM/esbuild, build = Rollup; React plugin for fast
refresh. No App-Router idioms (state-management/rendering boundaries stay
client-only).

## Dependency updates

Patch/minor within majors via changelog skim + gate run; majors = migration
(migrations.md). `npm audit`/`pnpm audit` in CI (security.md).
