// nextjs-app-router example — route segment file set (Next 16 line, App
// Router). Server Components by default; typed async params (await = 15+/16).
// Authority for exact signatures: node_modules/next/dist/docs/ (version-policy).

// app/blog/[slug]/page.tsx
import { Suspense } from "react";
import { notFound } from "next/navigation";

type PageProps = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: PageProps) {
  const { slug } = await params;
  const article = await getArticle(slug); // cached read: data-caching.md
  if (!article) return {};
  return { title: article.title, description: article.excerpt };
}

export default async function ArticlePage({ params }: PageProps) {
  const { slug } = await params;
  const article = await getArticle(slug); // server-side read, no client fetch
  if (!article) notFound();

  return (
    <article>
      <h1>{article.title}</h1>
      {/* Suspense where the fallback belongs, not at the root (rendering.md) */}
      <Suspense fallback={<p aria-hidden="true">Loading related…</p>}>
        <Related slug={slug} />
      </Suspense>
    </article>
  );
}

async function getArticle(slug: string) {
  // Real projects: data layer behind a typed fn; `use cache` where a lifetime
  // + invalidation story exists (data-caching.md). Placeholder shape:
  return { title: `Article ${slug}`, excerpt: `About ${slug}` } as const;
}

async function Related({ slug }: { slug: string }) {
  const items = [`more:${slug}`];
  return <ul>{items.map((i) => <li key={i}>{i}</li>)}</ul>;
}
