// catalog.mjs — parse/serialize translation catalogs without dependencies.
// Supported: JSON, YAML (flat + one nesting level + inline lists), CSV,
// gettext PO/POT, Fluent FTL (messages + simple plurals), XLIFF 1.2 (units).
// Unknown structures fail loudly with a parse error, never silent partial data.

import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { join, basename, extname } from 'node:path';

// ---------- tiny YAML (subset) ----------
export function parseYaml(text) {
  const lines = text.replace(/\r\n/g, '\n').split('\n');
  const root = {};
  const stack = [{ obj: root, indent: -1 }];
  for (let raw of lines) {
    const line = raw.replace(/\s+$/, '');
    if (!line.trim() || line.trim().startsWith('#')) continue;
    const indent = line.match(/^ */)[0].length;
    const content = line.trim();
    while (stack.length > 1 && indent <= stack[stack.length - 1].indent) stack.pop();
    const parent = stack[stack.length - 1].obj;
    const m = content.match(/^([^:]+):(?:\s+(.*))?$/);
    if (!m) throw new Error(`yaml: cannot parse line: ${content}`);
    const key = stripQuote(m[1].trim());
    const val = (m[2] || '').trim();
    if (val === '' || val.startsWith('#')) {
      const child = {};
      setVal(parent, key, child);
      stack.push({ obj: child, indent });
    } else if (val.startsWith('[') && val.endsWith(']')) {
      setVal(parent, key, splitCsv(val.slice(1, -1)).map(stripQuote));
    } else {
      setVal(parent, key, coerce(stripQuote(val)));
    }
  }
  return root;

  function setVal(obj, key, v) {
    if (key.includes('.')) {
      const parts = key.split('.');
      let t = obj;
      for (const p of parts.slice(0, -1)) t = (t[p] = t[p] && typeof t[p] === 'object' ? t[p] : {});
      setVal(t, parts.at(-1), v);
    } else obj[key] = v;
  }
}
function coerce(v) {
  if (v === 'true') return true; if (v === 'false') return false;
  if (/^-?\d+(\.\d+)?$/.test(v)) return Number(v);
  return v;
}
function stripQuote(s) {
  s = s.trim();
  if ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'"))) return s.slice(1, -1);
  return s;
}

// ---------- CSV ----------
export function parseCsv(text) {
  const rows = [];
  let row = [], field = '', q = false;
  const src = text.replace(/\r\n/g, '\n');
  for (let i = 0; i < src.length; i++) {
    const c = src[i];
    if (q) {
      if (c === '"') { if (src[i + 1] === '"') { field += '"'; i++; } else q = false; }
      else field += c;
    } else if (c === '"') q = true;
    else if (c === ',') { row.push(field); field = ''; }
    else if (c === '\n') { row.push(field); rows.push(row); row = []; field = ''; }
    else field += c;
  }
  if (field !== '' || row.length) { row.push(field); rows.push(row); }
  return rows.filter((r) => r.length > 1 || r[0] !== '');
}

// ---------- PO/POT ----------
export function parsePo(text) {
  const entries = [];
  let cur = null;
  const flush = () => { if (cur && cur.msgid !== null) entries.push(cur); cur = null; };
  for (const raw of text.replace(/\r\n/g, '\n').split('\n')) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) { if (line.startsWith('#~')) flush(); continue; }
    if (line.startsWith('msgctxt')) { flush(); cur = { msgctxt: poStr(line.slice(7)), msgid: null, msgid_plural: null, msgstrs: [], comments: [] }; continue; }
    if (line.startsWith('msgctxt')) {}
    if (line.startsWith('msgid_plural')) { if (cur) cur.msgid_plural = poStr(line.slice(12)); continue; }
    if (line.startsWith('msgid')) {
      if (cur && cur.msgstrs.length) { flush(); cur = { msgid: poStr(line.slice(5)), msgid_plural: null, msgstrs: [], comments: [] }; }
      else if (cur) cur.msgid = poStr(line.slice(5));
      else cur = { msgid: poStr(line.slice(5)), msgid_plural: null, msgstrs: [], comments: [] };
      continue;
    }
    if (line.startsWith('msgstr[')) { if (cur) cur.msgstrs.push(poStr(line.slice(7).replace(/^\s*\d+\s*\]/, ''))); continue; }
    if (line.startsWith('msgstr')) { if (cur) cur.msgstrs.push(poStr(line.slice(6))); continue; }
    if (line.startsWith('"') && cur) { // continuation
      const s = poStr(line);
      if (cur.msgstrs.length) cur.msgstrs[cur.msgstrs.length - 1] += s;
      else if (cur.msgid_plural !== null || cur.pluralNext) cur.msgid_plural = (cur.msgid_plural || '') + s;
      else cur.msgid += s;
      continue;
    }
  }
  flush();
  return entries.filter((e) => e.msgid);
}
function poStr(s) {
  const m = String(s).trim().match(/"((?:\\.|[^"\\])*)"/);
  if (!m) return '';
  return m[1].replace(/\\n/g, '\n').replace(/\\t/g, '\t').replace(/\\"/g, '"').replace(/\\\\/g, '\\');
}
export function serializePo(entries) {
  return entries.map((e) => {
    let out = '';
    if (e.msgctxt) out += `msgctxt "${escPo(e.msgctxt)}"\n`;
    out += `msgid "${escPo(e.msgid)}"\n`;
    if (e.msgid_plural) out += `msgid_plural "${escPo(e.msgid_plural)}"\n`;
    if (e.msgstrs.length > 1) e.msgstrs.forEach((s, i) => { out += `msgstr[${i}] "${escPo(s)}"\n`; });
    else out += `msgstr "${escPo(e.msgstrs[0] || '')}"\n`;
    return out;
  }).join('\n');
}
const escPo = (s) => String(s).replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n');

// ---------- Fluent FTL ----------
export function parseFtl(text) {
  const msgs = new Map();
  const re = /^([a-zA-Z0-9_-]+)\s*=\s*([\s\S]*?)(?=\n[a-zA-Z0-9_-]+\s*=|\n\[|\n#|$)/gm;
  for (const m of text.replace(/\r\n/g, '\n').matchAll(re)) {
    msgs.set(m[1], m[2].trim().replace(/\n\s+/g, ' '));
  }
  return msgs;
}

// ---------- XLIFF 1.2 ----------
export function parseXliff(text) {
  const units = [];
  for (const m of text.matchAll(/<trans-unit[^>]*id="([^"]*)"[^>]*>([\s\S]*?)<\/trans-unit>/g)) {
    const src = /<source>([\s\S]*?)<\/source>/.exec(m[2]);
    const tgt = /<target[^>]*>([\s\S]*?)<\/target>/.exec(m[2]);
    units.push({ id: m[1], source: unescXml(src ? src[1] : ''), target: tgt ? unescXml(tgt[1]) : '' });
  }
  return units;
}
const unescXml = (s) => s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&').replace(/&quot;/g, '"');

// ---------- catalog loading ----------
const LOCALE_FILE = /(?:^|[/\\._-])([a-z]{2}(?:[-_][A-Za-z]{2,4}(?:[-_][A-Za-z]{2,4})?|[-_][A-Z]{2})?)(?:\.|-)(json|ya?ml|csv|po|ftl|xlf|json5?)$/;

/** Walk a locales dir, return [{file, locale, format, data}]. localeFrom() maps file->locale. */
export function loadCatalogDir(dir, { locales } = {}) {
  if (!existsSync(dir)) return [];
  const known = locales ? new Set(locales.map((l) => l.toLowerCase().replace(/_/g, '-'))) : null;
  const out = [];
  for (const file of walk(dir)) {
    const ext = extname(file).slice(1).toLowerCase();
    if (!['json', 'yaml', 'yml', 'csv', 'po', 'pot', 'ftl', 'xlf', 'xliff'].includes(ext)) continue;
    const base = basename(file);
    const locale = matchLocale(base, known);
    if (!locale) continue;
    const text = readFileSync(file, 'utf8');
    out.push({ file, locale, format: ext, text });
  }
  return out.sort((a, b) => a.file.localeCompare(b.file));
}
function walk(dir, acc = []) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) { if (e.name !== 'node_modules' && !e.name.startsWith('.')) walk(p, acc); }
    else acc.push(p);
  }
  return acc;
}
function matchLocale(fileName, known) {
  const stem = fileName.replace(/\.[^.]+$/, '').toLowerCase().replace(/_/g, '-');
  if (known && known.has(stem)) return stem;
  const m = fileName.match(LOCALE_FILE);
  if (m) return m[1].toLowerCase().replace(/_/g, '-');
  const parts = stem.split(/[-._]/);
  const last = parts.at(-1);
  if (known && known.has(last)) return last;
  return /^[a-z]{2}(-[a-z]{2}|-[a-z]{4}-[a-z]{2}|-[a-z]{2})?$/.test(stem) ? stem : null;
}

/** Flatten {a:{b:'x'}} to {'a.b':'x'}; leaves stay strings. */
export function flatten(obj, prefix = '', out = {}) {
  for (const [k, v] of Object.entries(obj)) {
    const key = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === 'object' && !Array.isArray(v)) flatten(v, key, out);
    else if (Array.isArray(v)) out[key] = v.join(', ');
    else out[key] = v == null ? '' : String(v);
  }
  return out;
}
export function unflatten(flat) {
  const out = {};
  for (const [key, v] of Object.entries(flat)) {
    const parts = key.split('.');
    let t = out;
    for (const p of parts.slice(0, -1)) t = (t[p] = t[p] && typeof t[p] === 'object' ? t[p] : {});
    t[parts.at(-1)] = v;
  }
  return out;
}

/**
 * parse a catalog file body -> { keys: Map<key,value>, meta } or { error }.
 * `context.locales` unused; `keyColumn` for CSV first col default 'key'.
 */
export function parseCatalog(text, format, { keyColumn = 'key', valueColumn, sourceLocale } = {}) {
  const fmt = format.toLowerCase();
  try {
    if (fmt === 'json' || fmt === 'json5') {
      const data = JSON.parse(stripBom(text));
      return { keys: new Map(Object.entries(flatten(data))), meta: {} };
    }
    if (fmt === 'yaml' || fmt === 'yml') {
      return { keys: new Map(Object.entries(flatten(parseYaml(text)))), meta: {} };
    }
    if (fmt === 'csv') {
      const rows = parseCsv(text);
      if (!rows.length) return { keys: new Map(), meta: {} };
      const head = rows[0].map((h) => h.trim());
      const col = head.indexOf(keyColumn);
      const idx = col === -1 ? 0 : col;
      let start = col === -1 ? 0 : 1;
      if (start === 0 && rows.length && /^(keys?|identifier|term)$/i.test((rows[0][0] || '').trim())) start = 1;
      let vIdx = -1;
      if (valueColumn) {
        vIdx = head.findIndex((h) => h.toLowerCase() === String(valueColumn).toLowerCase());
        if (vIdx === -1) return { error: `csv missing column ${valueColumn}` };
      }
      const keys = new Map();
      for (const r of rows.slice(start)) if (r[idx] && r[idx].trim()) keys.set(r[idx].trim(), ((vIdx > -1 ? r[vIdx] : r[idx + 1]) ?? '').trim());
      return { keys, meta: { header: head } };
    }
    if (fmt === 'po' || fmt === 'pot') {
      const entries = parsePo(text);
      const keys = new Map();
      for (const e of entries) if (e.msgid) keys.set(e.msgid, e.msgstrs[0] ?? '');
      return { keys, meta: { entries } };
    }
    if (fmt === 'ftl') {
      return { keys: new Map(parseFtl(text)), meta: {} };
    }
    if (fmt === 'xlf' || fmt === 'xliff') {
      const units = parseXliff(text);
      return { keys: new Map(units.map((u) => [u.id, u.target || u.source])), meta: { units } };
    }
    return { error: `unsupported format: ${format}` };
  } catch (e) {
    return { error: `${fmt} parse error: ${e.message}` };
  }
}

const stripBom = (s) => s.charCodeAt(0) === 0xfeff ? s.slice(1) : s;
export { LOCALE_FILE };
