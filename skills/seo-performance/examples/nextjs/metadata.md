// Next.js app-router metadata baseline (react-nextjs skill owns depth).
// app/layout.tsx — global; per-route overrides live in route layout/page.
import type { Metadata } from 'next';

export const metadata: Metadata = {
  metadataBase: new URL('https://example.com'),       // absolute URLs everywhere
  title: { template: '%s — Site', default: 'Site — tagline' },
  description: 'Shared fallback description; every route overrides it.',
  openGraph: { type: 'website', siteName: 'Site' },
};
// app/sitemap.ts + app/robots.ts: emit dynamic, route-table-accurate files
// (replaces public/sitemap.xml drift). generateMetadata for dynamic routes:
// export async function generateMetadata({ params }): Promise<Metadata> {
//   return { title: ..., alternates: { canonical: ... } };
// }
