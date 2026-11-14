# Content & CMS — Content Layer, collections, external sources

Astro's content model on 5+ is the **Content Layer**: config in
`src/content.config.ts` (not the legacy `src/content/config.ts`), sources via
**loaders**, schemas via Zod. Verify against docs/`reference/content-layer-reference`.

## Local content collections (markdown/MDX in repo)

```ts
// src/content.config.ts
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
    hero: z.image().optional(),          // astro:assets image
    author: z.string().optional(),
  }),
});

export const collections = { blog };
```

Consuming (typed):

```ts
import { getCollection, render } from 'astro:content';
const posts = (await getCollection('blog', ({ data }) => !data.draft))
  .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
const { Content } = await render(post);   // Body removed in 5.x; use render()
```

- `id` replaced `slug` as the entry key (5.x); derive URL segments from
  `id`. `z.image()` for optimized hero images; `reference()` for cross-refs.
- Filter `draft` at every query; drafts never reach `dist/`.
- Pagination: paginate() helper (7.1+ `format` option) or manual chunk over
  `getCollection` in `getStaticPaths`.

## External / headless CMS (Content Layer loaders)

- REST/GraphQL source → custom `Loader` (`{ name, load() }`) returning
  `{ id, data }[]`; fetch in `load()` at build; env keys via `import.meta.env`.
- Live Content Collections (reload on change in dev) exist for some
  integrations — confirm per target docs; use to iterate CMS fields fast.
- Never install a CMS or its SDK the task didn't ask for; loaders wrap any
  HTTP endpoint (Strapi/Sanity/Directus/Storyblok/Contentful/WP-REST) without
  their client libs unless a lib buys typed queries — decision + reasons.
- Images from remote CMS: `remote` image config + `getImage()`/`<Image>` with
  `src` URL; keep aspect + dimensions for CLS.

## Content features (implement only what's asked)

| Feature | Method |
|---|---|
| categories/tags | schema array + derived index route |
| authors | author collection or `reference()`; profile page route |
| pubDate/updatedDate | schema `z.coerce.date()`; `<time datetime>` |
| TOC | rehype/remark plugin or Sätteri hook (7.x) — verify |
| syntax highlight | built-in Shiki via `markdown.shikiConfig` |
| RSS | endpoint generating XML from collection; `@astrojs/rss` if kept |
| sitemap | integration or endpoint from routes |
| related | tag/author overlap over `getCollection` |
| OG images | `getImage`/satori per route; deterministic |
| search index | static JSON route from collection |

## Migration note (legacy → current)

Pre-5 project → current: move `src/content/config.ts` → `src/content.config.ts`,
replace `getEntry`/`render(entry)` body access with `render()` + `Content`,
`slug` → `id`, add a loader (`glob`) per collection. Run `astro check` after
each collection; content files stay untouched. See upgrades.md.
