import assert from 'node:assert/strict';
import { validateSchemaHtml, crossCheckContent } from '../../scripts/lib/schema.mjs';
import { snapshot, compareSnapshots, renderMarkdown, saveSnapshot, loadSnapshot } from '../../scripts/lib/report.mjs';
import { detectProject } from '../../scripts/lib/project.mjs';
import { loadConfig } from '../../scripts/lib/config.mjs';
import { writeFileSync, mkdirSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

export default function (t) {
  t('schema tiers: valid schema but offline-undetermined award', () => {
    const v = validateSchemaHtml('<script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","name":"X","url":"https://x.test"}</script>');
    assert.equal(v.tiers['valid-schema'], true);
    assert.equal(v.tiers['google-conform'], true);
    assert.equal(v.tiers['rich-result-award'], 'UNDETERMINED-OFFLINE');
  });
  t('schema: broken json fails syntax tier, relative url flagged', () => {
    const v = validateSchemaHtml('<script type="application/ld+json">{bad</script>');
    assert.equal(v.tiers['valid-schema'], false);
    assert.ok(validateSchemaHtml('<script type="application/ld+json">{"@type":"Organization","name":"X","url":"/rel"}</script>').issues.some((i) => i.tier === 'valid-schema'));
  });
  t('content cross-check flags invisible headline', () => {
    const html = '<script type="application/ld+json">{"@type":"Organization","name":"A claim that never appears in the visible copy of this page","url":"https://x.test"}</script><p>short copy</p>';
    const cross = crossCheckContent(html, 'short copy');
    assert.equal(cross.length, 1); assert.equal(cross[0].verdict, 'not-in-visible-text');
  });
  t('snapshot->compare: regression/noise/improvement classified', () => {
    const mk = (lcp, fnd) => ({ capturedAt: 't', name: 'n', project: {}, tools: { node: 'v' }, pagesMeasured: 1,
      metrics: [{ url: 'u', metric: 'lcp', value: lcp, lowerIsBetter: true }], findings: fnd, counts: { critical: 0, high: fnd.length, medium: 0, low: 0 }, dataGaps: [] });
    const cmp = (a, b) => compareSnapshots(mk(1000, [{ id: 'x|u', severity: 'high', urls: ['u'] }]), mk(b, a === 'noise' ? [{ id: 'x|u', severity: 'high', urls: ['u'] }] : []));
    assert.equal(cmp(1000, 1020).metricDelta[0].verdict, 'noise');
    assert.equal(cmp(1000, 3000).metricDelta[0].verdict, 'regression');
    assert.equal(cmp(1000, 500).metricDelta[0].verdict, 'improvement');
    assert.equal(cmp(1000, 1000).newFindings.length + cmp(1000, 1000).resolvedFindings.length, 1, 'finding resolved tracked');
    assert.equal(compareSnapshots(null, mk(1, [])).status, 'INCOMPLETE');
    assert.ok(renderMarkdown({ snap: mk(1, []), compare: cmp(1000, 3000) }).includes('regression'));
  });
  t('missing metric => "not measured" not zero', () => {
    const md = renderMarkdown({ snap: { name: 'n', capturedAt: 't', counts: { critical: 0, high: 0, medium: 0, low: 0 }, findings: [], metrics: [{ url: 'u', metric: 'inp', value: null }], dataGaps: [] }, compare: null });
    assert.ok(md.includes('not measured') || !md.includes(' inp '));
  });
  t('snapshot persistence roundtrip', () => {
    const d = join(tmpdir(), 'seoperf-test-' + Date.now());
    const snap = snapshot({ root: d, name: 'n', pages: [], findings: [{ id: 'a|u', severity: 'low', urls: ['u'] }], metrics: [], project: { framework: 'static-html' }, tools: {}, dataGaps: [] });
    const f = saveSnapshot(d, snap);
    const back = loadSnapshot(f);
    assert.equal(back.counts.low, 1);
    assert.equal(loadSnapshot(d + '/latest.json').name, 'n');
    rmSync(d, { recursive: true, force: true });
  });
  t('detectProject: static fixture + next app detection', () => {
    const d = join(tmpdir(), 'seoperf-det-' + Date.now());
    mkdirSync(join(d, 'app'), { recursive: true });
    writeFileSync(join(d, 'package.json'), JSON.stringify({ dependencies: { next: '16.0.0' } }));
    const p = detectProject(d);
    assert.equal(p.framework, 'next'); assert.match(p.rendering, /app-router/);
    writeFileSync(join(d, 'package.json'), JSON.stringify({ dependencies: { react: '19' } }));
    assert.equal(detectProject(d).framework, 'react');
    rmSync(d, { recursive: true, force: true });
    const fx = detectProject(new URL('../fixtures/site', import.meta.url).pathname);
    assert.equal(fx.framework, 'static-html');
  });
  t('config layering: strict extends default; project overrides skill', () => {
    const d = join(tmpdir(), 'seoperf-cfg-' + Date.now());
    mkdirSync(d, { recursive: true });
    writeFileSync(join(d, '.seo-performance.json'), JSON.stringify({ cwv: { lcpMs: 999 } }));
    const cfg = loadConfig({ profile: 'strict', projectDir: d });
    assert.equal(cfg.cwv.lcpMs, 999, 'project wins');
    assert.equal(cfg.failOnSeverity, 'high', 'strict profile merged');
    assert.ok(loadConfig({}).cwv.inpMs === 200, 'default intact');
    rmSync(d, { recursive: true, force: true });
  });
}
