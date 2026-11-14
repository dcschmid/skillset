# React/Vite (CSR) metadata baseline (react-nextjs skill owns depth)
index.html carries shell meta; per-route head management keeps SEO signals
in the DOM before snapshots; pre-render/SSR is a proposal, never automatic.

```tsx
// src/Seo.tsx — route head via react-helmet-async (or existing head lib)
import { Helmet } from 'react-helmet-async';
export const Seo = ({ t, d, path }: { t: string; d: string; path: string }) => (
  <Helmet>
    <title>{t}</title><meta name="description" content={d} />
    <link rel="canonical" href={`https://example.com${path}`} />
  </Helmet>
);
// App.tsx renders <Seo .../> per route; keep <html lang> in index.html.
// If delivered-HTML checks fail on key routes: evaluate pre-render
// (vite-plugin-prerender) or SSR framework — PROPOSE with evidence first.
```
