/**
 * report.mjs — snapshots (JSON, trendable) + Markdown reports.
 * Numbers appear ONLY from real measurements; missing = "not measured".
 */
import { writeFileSync, mkdirSync, readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

export function snapshot({ root, name, pages, findings, metrics, project, tools, dataGaps }) {
  return { schema: 'seo-performance-snapshot/1', capturedAt: new Date().toISOString(), name,
    project: { framework: project?.framework, version: project?.version, rendering: project?.rendering },
    tools, pagesMeasured: (pages ?? []).length, metrics: metrics ?? [],
    findings: (findings ?? []).map((f) => ({ id: f.id, severity: f.severity, category: f.category, urls: f.urls, evidence: f.evidence })),
    counts: count(findings), dataGaps: dataGaps ?? [],
    dataPolicy: 'numbers from measurements only; UNAVAILABLE marks missing inputs'};
}
const count = (fs) => ({ critical: (fs ?? []).filter((f) => f.severity === 'critical').length, high: (fs ?? []).filter((f) => f.severity === 'high').length,
  medium: (fs ?? []).filter((f) => f.severity === 'medium').length, low: (fs ?? []).filter((f) => f.severity === 'low').length });

export function saveSnapshot(dir, snap) {
  mkdirSync(dir, { recursive: true });
  const f = join(dir, `snapshot-${snap.capturedAt.replace(/[:.]/g, '-')}.json`);
  writeFileSync(f, JSON.stringify(snap, null, 2));
  const latest = join(dir, 'latest.json');
  writeFileSync(latest, JSON.stringify(snap, null, 2));
  return f;
}
export function listSnapshots(dir) {
  try { return readdirSync(dir).filter((f) => f.startsWith('snapshot-')).sort().map((f) => join(dir, f)); } catch { return []; }
}
export function loadSnapshot(p) { try { return JSON.parse(readFileSync(p, 'utf8')); } catch { return null; } }

/** Compare two snapshots. Classifies change: regression | improvement | noise | environment. */
export function compareSnapshots(before, after, { noisePct = 10 } = {}) {
  if (!before || !after) return { status: 'INCOMPLETE', detail: before ? 'missing "after" snapshot' : 'missing "before" snapshot' };
  const envChanged = before.project?.framework !== after.project?.framework || before.tools?.node !== after.tools?.node;
  const keyOf = (f) => f.id + '|' + (f.urls?.[0] ?? '');
  const bKeys = new Set((before.findings ?? []).map(keyOf));
  const aKeys = new Set((after.findings ?? []).map(keyOf));
  const introduced = (after.findings ?? []).filter((f) => !bKeys.has(keyOf(f)));
  const fixed = (before.findings ?? []).filter((f) => !aKeys.has(keyOf(f)));
  const metricDelta = [];
  for (const m of after.metrics ?? []) {
    const prev = (before.metrics ?? []).find((x) => x.url === m.url && x.metric === m.metric);
    if (!prev || typeof m.value !== 'number' || typeof prev.value !== 'number') { metricDelta.push({ ...m, delta: null, note: 'no comparable baseline' }); continue; }
    const pct = prev.value === 0 ? 0 : ((m.value - prev.value) / prev.value) * 100;
    metricDelta.push({ url: m.url, metric: m.metric, before: prev.value, after: m.value, deltaPct: +pct.toFixed(1),
      verdict: Math.abs(pct) <= noisePct ? 'noise' : pct > 0 ? (m.lowerIsBetter === false ? 'improvement' : 'regression') : (m.lowerIsBetter === false ? 'regression' : 'improvement'),
      environmentChanged: envChanged });
  }
  return { status: 'OK', before: before.capturedAt, after: after.capturedAt, envChanged, metricDelta,
    newFindings: introduced, resolvedFindings: fixed.map((f) => ({ id: f.id, urls: f.urls })),
    unresolved: [...bKeys].filter((k) => aKeys.has(k)).length,
    counts: { before: before.counts, after: after.counts } };
}

export function renderMarkdown({ snap, compare, template }) {
  const f = (n) => (n == null ? 'not measured' : typeof n === 'number' ? +n.toFixed(2) : n);
  const L = [];
  L.push(`# SEO & Performance Audit — ${snap.name}`);
  L.push(`_captured ${snap.capturedAt} · framework: ${snap.project?.framework ?? 'unknown'} (${snap.project?.rendering ?? '?'}) · pages: ${snap.pagesMeasured}_`);
  L.push('');
  L.push('## Executive Summary');
  L.push(`| severity | count |\n|---|---|\n| critical | ${snap.counts.critical} |\n| high | ${snap.counts.high} |\n| medium | ${snap.counts.medium} |\n| low | ${snap.counts.low} |`);
  if (snap.dataGaps?.length) { L.push(''); L.push('**Data gaps:** ' + snap.dataGaps.join('; ')); }
  L.push('');
  L.push('## Findings & Remediation Plan');
  L.push('| ID | sev | category | URLs | evidence | fix | effort | risk | verify |');
  L.push('|---|---|---|---|---|---|---|---|---|');
  for (const x of (snap.findings ?? []).slice(0, 100))
    L.push(`| ${x.id} | ${x.severity} | ${x.category} | ${(x.urls ?? []).slice(0, 2).join(' ')} | ${String(x.evidence).slice(0, 120)} | | | | |`);
  if (compare && compare.status === 'OK') {
    L.push(''); L.push('## Before / After');
    L.push('| metric | url | before | after | Δ% | verdict |');
    L.push('|---|---|---|---|---|---|');
    for (const m of compare.metricDelta ?? [])
      L.push(`| ${m.metric} | ${m.url ?? '-'} | ${f(m.before)} | ${f(m.after)} | ${m.deltaPct ?? '-'} | ${m.verdict ?? m.note} |`);
    L.push('');
    if ((compare.newFindings ?? []).length) { L.push('**New findings:**'); for (const n of compare.newFindings.slice(0, 20)) L.push(`- ${n.id} (${n.severity})`); }
    if ((compare.resolvedFindings ?? []).length) { L.push('**Resolved:**'); for (const r of compare.resolvedFindings.slice(0, 20)) L.push(`- ${r.id}`); }
  } else if (compare) { L.push(''); L.push(`## Before/After: ${compare.status} — ${compare.detail}`); }
  L.push('');
  L.push('_Scores are lab measurements, not ranking guarantees. Field metrics (INP) only from CrUX/RUM._');
  return L.join('\n');
}
