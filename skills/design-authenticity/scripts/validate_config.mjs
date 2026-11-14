#!/usr/bin/env node
// validate_config.mjs — validate an optional design-authenticity config
// (YAML subset: key: value | nested key: value | - item | [a, b]).
// Usage: node validate_config.mjs [path]   (default: ./design.config.yaml)
// Missing config is NOT a failure: prints CONFIG MISSING, exit 0.
import { readFileSync, existsSync } from 'node:fs';

const file = process.argv[2] ?? 'design.config.yaml';
if (!existsSync(file)) { console.log(`CONFIG MISSING ${file} (defaults apply, not an error)`); process.exit(0); }

const text = readFileSync(file, 'utf8');
const problems = [];
const t2 = (s) => s.trim().replace(/^["']|["']$/g, '');
const sections = {}; let cur = null; let openList = null; // [section, acc] open array
for (const [i, raw] of text.split('\n').entries()) {
  const line = raw.replace(/#.*$/, '').replace(/\s+$/, '');
  if (!line.trim()) continue;
  if (openList) { // continuation of a multi-line [ ... ] value
    const tail = line.replace(/\]\s*$/, '').trim();
    if (tail) for (const part of tail.split(',')) { const t = t2(part); if (t) openList[1].push(t); }
    if (/\]\s*$/.test(line)) { openList[0]._v = '[' + openList[1].join(', ') + ']'; openList = null; }
    continue;
  }
  const m = /^([A-Za-z_][\w-]*):(.*)$/.exec(line);
  if (m && !line.startsWith(' ')) {
    cur = m[1]; const v = m[2].trim();
    sections[cur] = v ? { _v: v } : {};
    if (v.startsWith('[') && !/\]\s*$/.test(v)) openList = [sections[cur], []]; // open array
    continue;
  }
  const kv = /^\s+([A-Za-z_][\w-]*):(.*)$/.exec(line);
  if (kv && cur) {
    const v = kv[2].trim(); const vo = { _v: v }; ((sections[cur]._ ??= {})[kv[1]] = vo);
    if (v.startsWith('[') && !/\]\s*$/.test(v)) openList = [vo, []];
    continue;
  }
  if (/^\s+-\s/.test(line) && cur) { (sections[cur]._list ??= []).push(line.trim().slice(1).trim()); continue; }
  problems.push(`line ${i + 1}: unsupported syntax "${line.trim()}" (keep: key: value, nested key: value, - item)`);
}

const get = (path) => path.split('.').reduce((o, k) => (o?._ ?? o)?.[k], sections);
const val = (p) => { const o = get(p); return typeof o === 'object' && o !== null ? o._v : o; };
const list = (p) => { const v = val(p); if (v === undefined) { const o = get(p); return Array.isArray(o?._list) ? o._list : []; }
  return String(v).replace(/^\[|\]$/g, '').split(',').map((s) => s.trim()).filter(Boolean); };
const enumIn = (v, set, where, req = false) => {
  if (v === undefined) { if (req) problems.push(`${where}: required`); return; }
  if (!set.includes(v)) problems.push(`${where}: '${v}' not in ${set.join('|')}`);
};

enumIn(val('strictness'), ['light', 'standard', 'strict'], 'strictness');
enumIn(val('brand.dark_mode'), ['authored', 'auto', 'none'], 'brand.dark_mode');
enumIn(val('screenshot_testing.enabled'), ['auto', 'on', 'off'], 'screenshot_testing.enabled');
enumIn(val('accessibility_target'), ['WCAG2AA', 'WCAG2AAA'], 'accessibility_target');
for (const vp of list('screenshot_testing.viewports'))
  if (!/^\d+x\d+$/.test(vp)) problems.push(`screenshot_testing.viewports: '${vp}' must be WxH`);
const mq = val('minimum_quality');
if (mq !== undefined && !(Number(mq) >= 0 && Number(mq) <= 100)) problems.push(`minimum_quality '${mq}' outside 0..100`);
const it = val('max_refine_iterations');
if (it !== undefined && !(Number.isInteger(+it) && +it >= 0 && +it <= 5)) problems.push(`max_refine_iterations '${it}' outside 0..5`);
const dir = val('direction'); if (dir !== undefined && dir.length < 3) problems.push('direction too vague');

if (problems.length) { console.log(`CONFIG FAIL ${file}`); for (const p of problems) console.log('  - ' + p); process.exit(1); }
console.log(`CONFIG PASS ${file}`);
