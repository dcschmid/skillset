# Components — `.astro` first, typed, composable

## The standard `.astro` component

```astro
---
// src/components/PostCard.astro
import { Image } from 'astro:assets';
import type { CollectionEntry } from 'astro:content';

interface Props {
  post: Pick<CollectionEntry<'blog'>, 'slug' | 'data'>;
  featured?: boolean;
}
const { post, featured = false } = Astro.props;
---
<article class:list={['card', featured && 'card--featured']}>
  <a href={`/blog/${post.slug}/`}>
    <h3>{post.data.title}</h3>
    {post.data.hero && <Image src={post.data.hero} alt="" width={640} height={360} />}
  </a>
</article>

<style>
  .card { container-type: inline-size; }
</style>
```

- Props typed with `interface Props` (or `type`), defaults via destructuring.
- `class:list` for conditional classes (Astro-native; no clsx dep needed).
- Scoped `<style>` by default; `is:global` only for deliberate escapes.
- Children: `<slot />`; named slots `slot="name"`; fall back content inside slot.

## Composition rules

- Layout receives `slot` children; pages pass content, never full documents.
- Data flows down via props; server islands (`server:defer`) replace "fetch in
  child" patterns — deferred components fetch their own data server-side.
- Eventing to parent = HTML forms/links or a small island; no custom event bus
  for server-rendered composition.
- Reusable logic in frontmatter = plain `.ts` functions in `lib/` (no
  `.astro` files as utilities).

## Server islands (4.16+, adapter) — server-owned dynamic blocks

```astro
<Avatar server:defer>
  <span slot="fallback">loading…</span>   <!-- shown until island resolves -->
</Avatar>
```
- Component renders late, per-request; page stays static/aggressively cached.
- Props MUST be serializable (no functions/circular); large props → tiny ids.
- `slot="fallback"` = instant placeholder (match final size → CLS 0).
- In island: `Astro.url` is the island endpoint, not the page URL — pass
  needed page context as props or read `Referer`.
- Use for: personalized blocks (cart count, avatar, live status) on otherwise
  static pages — instead of hydrating a framework component.

## Client components (frameworks) — only when justified

`.astro` has no client state. When a real interactive widget is required,
mount a framework component (React/Vue/Svelte/Solid) with a `client:*`
directive (see islands-interactivity.md). One component per island, never a
page-wide app, and the integration install is an explicit decision.

## Error surfaces

- Optional data → default slot content or a skeleton, not a crash:
  `const img = post.data.hero ?? fallback` beats `!` assertions in pages.
- `404.astro` route for unknown slugs: `Astro.rewrite('/404')` or
  render not-found block; never throw raw in page render for user-facing 404.
