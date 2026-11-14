// pseudo.mjs — pseudolocalization for layout/unicode stress testing.
// Expansion is a test parameter (default +30%), never a claim about real
// translation length. Preserves: placeholders, newlines, leading/trailing ws.

import { extractPlaceholders } from './placeholders.mjs';

const ACCENT_MAP = {
  a: 'ä', b: 'ḃ', c: 'ç', d: 'ḍ', e: 'é', f: 'ƒ', g: 'ĝ', h: 'ḥ', i: 'ï',
  j: 'ĵ', k: 'ḱ', l: 'ł', m: 'ṁ', n: 'ñ', o: 'ö', p: 'ṗ', q: 'ɋ', r: 'ŕ',
  s: 'š', t: 'ṭ', u: 'ü', v: 'ṽ', w: 'ŵ', x: 'ẋ', y: 'ý', z: 'ž',
  A: 'Ä', B: 'Ḃ', C: 'Ç', D: 'Ḍ', E: 'É', F: 'Ƒ', G: 'Ĝ', H: 'Ḥ', I: 'Ï',
  J: 'Ĵ', K: 'Ḱ', L: 'Ł', M: 'Ṁ', N: 'Ñ', O: 'Ö', P: 'Ṗ', Q: 'Ɋ', R: 'Ŕ',
  S: 'Š', T: 'Ṭ', U: 'Ü', V: 'Ṽ', W: 'Ŵ', X: 'Ẋ', Y: 'Ý', Z: 'Ž',
};

/**
 * Pseudolocalize a string.
 * options: { expand=0.3 (0..1 extra padding words), rtl=false, prefix/suffix }
 * Placeholders ({name}, %s, {0}, [tag]) pass through untouched.
 */
export function pseudo(text, options = {}) {
  if (typeof text !== 'string') return text;
  const { expand = 0.3, rtl = false } = options;
  const pads = Math.round(clamp01(expand) * 10);
  const padWord = rtl ? 'تمتد' : 'ext';
  const pad = ' ' + Array.from({ length: pads }, (_, i) => `${padWord}${i + 1}`).join(' ');

  // split out protected spans (placeholders), transform the rest
  const spans = [];
  const masked = text.replace(/\{\{?[a-zA-Z0-9_$.,\s-]*\}?\}|%\d*\$?[sdif]|\\\([a-zA-Z_]+\)/g, (m) => {
    spans.push(m); return `\u0000${spans.length - 1}\u0000`;
  });
  let mapped = [...masked].map((ch) => ACCENT_MAP[ch] || ch).join('');
  if (expand > 0) {
    mapped = mapped.replace(/(\n|$)/, (m) => pad + m).replace(/^/, rtl ? '' : '[').replace(/$/, rtl ? '' : ']');
  }
  let out = masked === mapped ? mapped : mapped.replace(/\u0000(\d+)\u0000/g, (_, i) => spans[+i]);
  if (rtl) out = '\u202B' + out + '\u202C'; // bidi isolate for RTL pseudo locale
  return out;
}

const clamp01 = (n) => Math.max(0, Math.min(1, Number(n) || 0));

/** Grapheme count (Intl.Segmenter) vs codepoint count — layout math uses this. */
export function graphemeCount(text) {
  if (typeof Intl !== 'undefined' && Intl.Segmenter) {
    return [...new Intl.Segmenter('und', { granularity: 'grapheme' }).segment(text)].length;
  }
  return [...text].length;
}

/** Detect likely mojibake / stray control chars / missing NBSP issues. */
export function unicodeFindings(text, locale) {
  const findings = [];
  if (/[\u00C0-\u00FF]{2,}\?|Ã©|â€/.test(text)) findings.push({ type: 'mojibake', detail: 'double-encoded UTF-8 suspected' });
  const ctrl = [...text].filter((c) => c.charCodeAt(0) < 0x20 && c !== '\n' && c !== '\t' && c !== '\r');
  if (ctrl.length) findings.push({ type: 'control-chars', detail: `${ctrl.length} control chars` });
  if (/[\uFEFF]/.test(text)) findings.push({ type: 'bom', detail: 'BOM inside string' });
  return findings;
}
