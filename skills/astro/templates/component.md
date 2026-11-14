# Template: Typed `.astro` Component

Copy → adjust props/slots/tokens. Server-rendered by default; add
`server:defer` (server island) or `client:*` (framework island) only per the
islands ladder (references/islands-interactivity.md).

```astro
---
// src/components/Card.astro
import { Image } from 'astro:assets';

interface Props {
  title: string;
  href: string;
  image?: { src: string; alt: string };
  eyebrow?: string;
  interactive?: boolean; // true => consumer decides hydration elsewhere
}
const { title, href, image, eyebrow, interactive = false } = Astro.props;
---

<article class:list={['card', interactive && 'card--interactive']}>
  {eyebrow && <p class="eyebrow">{eyebrow}</p>}
  <a href={href} class="card__link">
    {image
      ? <Image src={image.src} alt={image.alt} width={640} height={360}
               loading="lazy" class="card__media" />
      : <div class="card__media card__media--empty" aria-hidden="true" />}
    <h3 class="card__title">{title}</h3>
  </a>
  <slot />
</article>

<style>
  .card { container-type: inline-size; display: grid; gap: var(--space-2); }
  .card__media { width: 100%; height: auto; aspect-ratio: 16 / 9;
                 object-fit: cover; border-radius: var(--radius); }
  .card__title { font-size: var(--step-1); color: var(--color-fg); }
  a:focus-visible { outline: var(--focus-ring); }
  @container (min-width: 30rem) { .card { grid-template-columns: 8rem 1fr; } }
</style>
```

Checks: props typed; images sized+alt'd; tokens only; focus visible; slot for
children; no client JS unless the ladder demanded it.
