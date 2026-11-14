# Client-side security (module §D/§E by framework)

Framework skills own idioms; this layer checks the security sink map per
stack detected by `detect-project.sh`. Only the present stacks run.

## Sink map (untrusted → DOM/JS boundary)

| Stack | Safe default | Dangerous sinks to audit |
|---|---|---|
| React/Next | JSX text interpolation | `dangerouslySetInnerHTML`, `serverActions` raw fetches, `next/dynamic` remote, middleware auth gaps (pages dir `_app` auth ≠ route protection — check `middleware.ts`) |
| Astro | `.astro` interpolation, `set:html` escape hatch | `set:html`/`is:inline` on user data, island props serialization, SSR/CSR boundary trust |
| Vue/Nuxt | `{{ }}`, `v-html` | `v-html`, `nuxt-content` renderer config, server routes in `server/api` without validation |
| Svelte/SvelteKit | `{text}` interpolation | `{@html}`, load functions trusting URL params, form actions without schema |
| Vanilla | `textContent` | `innerHTML`, `document.write`, `insertAdjacentHTML`, `outerHTML` |
| Extensions | — | `host_permissions` breadth, message passing origin checks, remote code (no eval in CSP-restricted pages) |

Universal: `postMessage` origin both ends · `localStorage` for tokens (XSS
tradeoff documented) · Web Storage of PII · third-party script SRI/version pin ·
source maps shipping internals in prod · inline event handlers.

## Per-framework checks

**Next.js**: `middleware.ts` auth patterns skip static? revalidate/webhook
routes verify signature? server components fetch server-side (no leaked
keys via `NEXT_PUBLIC_*`)? image optimizer host allowlist?
**Astro**: SSR endpoints (`endpoint` in astro.config) validation; content
collections render pipelines.
**SPAs (Vite)**: env prefixing (`VITE_` public!) — keys meant private must
not carry the public prefix; API base URLs proxyable.

## Header/CSP reality check (per stack)

Astro/SSR: middleware/headers config sets CSP; static hosts: `_headers`/
`netlify.toml`/vercel.json — check both dev proxy and prod host, they drift.
SPA behind CDN: headers must exist at the edge, framework config alone
insufficient. CSP for bundlers with inline bootstrap: nonce/hash mode via
host feature or documented report-only phase.

## Test hooks

Sink fixes get a render test (payload → inert output) where the project has
a component test story; otherwise a documented manual check list in
`security-test-results.md` with exact repro payloads.
