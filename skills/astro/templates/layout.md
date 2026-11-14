# Template: Base Layout (head + a11y + token contract)

Every page renders through a layout. Props feed the SEO head contract
(references/seo.md); a11y scaffolding is structural (references/accessibility.md).

```astro
---
// src/layouts/Base.astro
import '../styles/global.css';

interface Props {
  title: string;
  description: string;
  ogImage?: string;
  noindex?: boolean;
  lang?: string;
}
const { title, description, ogImage = '/og-default.png', noindex = false,
        lang = 'en' } = Astro.props;
const canonical = new URL(Astro.url.pathname, Astro.site);
---
<!doctype html>
<html lang={lang}>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <meta name="description" content={description} />
    <link rel="canonical" href={canonical} />
    <meta name="generator" content={Astro.generator} />
    <meta property="og:type" content="website" />
    <meta property="og:title" content={title} />
    <meta property="og:description" content={description} />
    <meta property="og:url" content={canonical} />
    <meta property="og:image" content={new URL(ogImage, Astro.site)} />
    <meta name="twitter:card" content="summary_large_image" />
    {noindex && <meta name="robots" content="noindex" />}
    <slot name="head" />
  </head>
  <body>
    <a href="#main" class="skip-link">Skip to content</a>
    <header><slot name="header" /></header>
    <main id="main" tabindex="-1">
      <slot />
    </main>
    <footer><slot name="footer" /></footer>
  </body>
</html>

<style is:global>
  /* token + skip-link/focus rules live in global.css; keep layout CSS thin */
</style>
```

Contract: unique `title`/`description` per route (from collection data when
content-driven); `canonical` absolute (needs `site`); skip-link target
`#main` focusable; JSON-LD and hreflang go in `slot="head"` from pages.
Framework: no `<script>` here — islands attach at page/component level.
