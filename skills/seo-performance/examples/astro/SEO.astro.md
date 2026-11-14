# Astro SEO component — minimal correct baseline (astro skill owns depth)
# src/components/SEO.astro — layout-level metadata per route.
---
interface Props { title: string; description: string; image?: string; noindex?: boolean }
const { title, description, image, noindex = false } = Astro.props;
const canonical = new URL(Astro.url.pathname, Astro.site).href; // site: required
---
<title>{title}</title>
<meta name="description" content={description} />
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link rel="canonical" href={canonical} />
{image && <meta property="og:image" content={new URL(image, Astro.site).href} />}
{noindex && <meta name="robots" content="noindex" />}
