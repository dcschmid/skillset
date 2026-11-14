# Template: Content Collection (schema + source + page)

Content Layer (Astro 5+). Adapt fields per project (references/content-cms.md).

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
    hero: z.image().optional(),
    author: z.string().optional(),
  }),
});
export const collections = { blog };
```

```astro
---
// src/pages/blog/[...id].astro
import { getCollection, render } from 'astro:content';
import BaseLayout from '../../layouts/Base.astro';

export async function getStaticPaths() {
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  return Promise.all(posts.map(async (post) => ({
    params: { id: post.id },
    props: { post, ...(await render(post)) },   // Body removed API: render()
  })));
}
const { post, Content } = Astro.props;
---
<BaseLayout title={post.data.title}
            description={post.data.description}>
  <template slot="head">
    <script type="application/ld+json" set:html={JSON.stringify({
      '@context': 'https://schema.org', '@type': 'BlogPosting',
      headline: post.data.title,
      datePublished: post.data.pubDate.toISOString(),
      ...(post.data.updatedDate && { dateModified: post.data.updatedDate.toISOString() }),
    })} />
  </template>
  <article>
    <h1>{post.data.title}</h1>
    <time datetime={post.data.pubDate.toISOString()}>{post.data.pubDate.toDateString()}</time>
    <Content />
  </article>
</BaseLayout>
```

Rules: draft filtered at every query; `id` is the entry key (5.x); dates ISO in
`<time>`; JSON-LD from data; remote/CMS source → custom Loader instead of
`glob`, same schema boundary. Verify `render()` usage against target docs.
