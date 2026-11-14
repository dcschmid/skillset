/**
 * schema-check.mjs — offline JSON-LD / schema.org validator layer.
 * Validation tiers (never conflated in reports):
 *   valid-schema      : parses + types/fields exist
 *   google-conform    : field set matches Google feature docs (subset check)
 *   rich-result-award : UNDETERMINED offline — needs Rich Results Test/API
 */
import { jsonLdBlocks } from './html.mjs';

const KNOWN = new Set(['Article','BlogPosting','NewsArticle','Organization','LocalBusiness','Corporation','Person',
  'WebSite','WebPage','BreadcrumbList','ItemList','Product','Offer','AggregateRating','Review','Event','VideoObject',
  'ImageObject','SoftwareApplication','FAQPage','HowTo','Question','Answer','SiteNavigationElement','Course','Recipe',
  'MedicalWebPage','JobPosting','PostalAddress','GeoCoordinates','SearchAction','ReadAction','ViewAction']);

const TYPES_URL = new Set(['WebPage','WebSite','ImageObject','VideoObject','PostalAddress','GeoCoordinates','Person','Organization']);

/** @returns {{tiers:Object, issues:Array, nodes:Array}} */
export function validateSchemaHtml(html) {
  const blocks = jsonLdBlocks(html);
  const issues = [];
  const nodes = [];
  let validSchema = blocks.length > 0;
  for (const b of blocks) {
    if (!b.ok) { issues.push({ tier: 'syntax', level: 'error', message: b.error }); validSchema = false; continue; }
    walk(b.data, (n, path) => {
      nodes.push({ node: n, path });
      const t = n['@type'];
      const list = Array.isArray(t) ? t : [t];
      for (const ty of list.filter(Boolean)) {
        if (!KNOWN.has(ty)) issues.push({ tier: 'valid-schema', level: 'warn', message: `type "${ty}" outside curated set (schema.org hosts 800+; verify at schema.org)`, path });
      }
      if (n.url && typeof n.url === 'string' && !/^https?:\/\//.test(n.url))
        issues.push({ tier: 'valid-schema', level: 'error', message: `url not absolute: ${n.url}`, path });
      if (n.datePublished && n.dateModified && new Date(n.dateModified) < new Date(n.datePublished))
        issues.push({ tier: 'google-conform', level: 'warn', message: 'dateModified < datePublished', path });
      if (n['@type'] === 'BreadcrumbList' && !Array.isArray(n.itemListElement))
        issues.push({ tier: 'valid-schema', level: 'error', message: 'BreadcrumbList without itemListElement array', path });
      if ((n['@type'] === 'Organization' || n['@type'] === 'LocalBusiness')) {
        if (!n.name) issues.push({ tier: 'google-conform', level: 'error', message: `${n['@type']} missing name`, path });
        if (!n.url) issues.push({ tier: 'google-conform', level: 'warn', message: `${n['@type']} missing url`, path });
      }
      if ((n['@type'] === 'Article' || n['@type'] === 'BlogPosting')) {
        for (const f of ['headline', 'datePublished', 'author']) if (!n[f])
          issues.push({ tier: 'google-conform', level: 'error', message: `${n['@type']} missing ${f}`, path });
      }
    });
  }
  const googleConform = validSchema && !issues.some((i) => i.tier === 'google-conform' && i.level === 'error');
  return {
    present: blocks.length > 0,
    tiers: { 'valid-schema': validSchema && !issues.some((i) => i.level === 'error' && i.tier === 'valid-schema'),
      'google-conform': googleConform, 'rich-result-award': 'UNDETERMINED-OFFLINE' },
    issues, nodes: nodes.map((n) => ({ type: n.node['@type'], path: n.path })),
    blocks: blocks.length,
  };
}
function walk(n, cb, path = '$') {
  if (!n || typeof n !== 'object') return;
  if (Array.isArray(n)) return n.forEach((v, i) => walk(v, cb, `${path}[${i}]`));
  if (n['@type']) cb(n, path);
  for (const [k, v] of Object.entries(n)) if (v && typeof v === 'object') walk(v, cb, `${path}.${k}`);
}

/** Visible-content cross-check: schema claims must exist on the page. */
export function crossCheckContent(html, text) {
  const v = (text ?? '').toLowerCase();
  const out = [];
  for (const { node } of walkAll(html)) {
    for (const field of ['name', 'headline']) {
      const val = node[field];
      if (typeof val === 'string' && val.length > 12 && !v.includes(val.toLowerCase().slice(0, 40)))
        out.push({ type: node['@type'], field, claim: val.slice(0, 80), verdict: 'not-in-visible-text' });
    }
    if (node.ratingValue && !v.includes(String(node.ratingValue)))
      out.push({ type: node['@type'], field: 'ratingValue', claim: String(node.ratingValue), verdict: 'not-in-visible-text' });
  }
  return out;
}
function walkAll(html) {
  const out = [];
  for (const b of jsonLdBlocks(html)) if (b.ok) walk(b.data, (n) => out.push({ node: n }));
  return out;
}
