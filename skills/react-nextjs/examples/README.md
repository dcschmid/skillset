# Examples — copyable, current, dependency-free snippets

Each folder is a self-contained set of files illustrating ONE skill module's
idioms at the 2026-11 baseline (React 19.3 / Next 16.4 line; floors in
`references/version-policy.md`). No external services, no secrets, no
install-required packages beyond the named framework + TypeScript.

| Folder | Shows | Module |
|---|---|---|
| `react-vite/` | typed SPA feature: state, effect cleanup, derived data | react-core.md |
| `nextjs-app-router/` | route file set: layout/page/loading/metadata split | nextjs-app-router.md |
| `reusable-components/` | prop-variant + composition pattern | react-core.md, styling |
| `forms-validation/` | useActionState + validated Server Function | react-modern-apis, server-actions |
| `testing-patterns/` | RTL component test + Playwright flow test | testing.md |

Snippets are illustrative of idioms, not runnable packages; integrate into a
real scaffold (tooling.md) and run the gates (testing.md).
