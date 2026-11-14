// placeholders.mjs — extraction + comparison of interpolation tokens.
// Grammar covers: {name}, {{name}}, {name, plural, ...}, %s, %d, %1$s,
// %1$d, {0}, <b>html-ish tags are NOT placeholders. ICU aware.

const TOKEN_SIMPLE = /\{\{?\s*([a-zA-Z_$][\w$.-]*|[0-9]+)\s*\}?\}/g;
const SPRINTF = /%\d*\$?[sdifjoax]|%[<>]/g;
const LUA_FMT = /\\\((\w+)\\\)/g;
const ICU_START = /\{\s*([a-zA-Z_$][\w$.-]*)\s*,\s*(?:plural|selectordinal|select)\s*,/g;

/** Multiset of interpolation tokens in a string (sorted array).
 *  Tokens: {name}, {0}, %s/%d/%1$s, \(var). ICU plural/select blocks reduce
 *  to their variable token {var — nesting is scanned, never mis-split. */
export function extractPlaceholders(text) {
  if (typeof text !== 'string' || !text) return [];
  const out = [];
  // ICU blocks first; mask them so simple scanning can't fragment them
  let src = text;
  for (const m of text.matchAll(ICU_START)) {
    const end = matchBrace(src, src.indexOf(m[0]));
    if (end > -1) { out.push(`{${m[1]}}`); src = src.slice(0, src.indexOf(m[0])) + '\u0000' + src.slice(end + 1); }
  }
  for (const m of src.matchAll(TOKEN_SIMPLE)) out.push(`{${m[1]}}`);
  for (const m of src.matchAll(SPRINTF)) out.push(m[0]);
  for (const m of src.matchAll(LUA_FMT)) out.push(`(${m[1]})`);
  return out.sort();
}
function matchBrace(s, from) {
  if (s[from] !== '{') return -1;
  let depth = 0;
  for (let i = from; i < s.length; i++) {
    if (s[i] === '{') depth++;
    else if (s[i] === '}') { depth--; if (depth === 0) return i; }
  }
  return -1;
}

/** Compare token sets between source and target strings. */
export function diffPlaceholders(source, target) {
  const a = extractPlaceholders(source), b = extractPlaceholders(target);
  const missing = [...a]; const extra = [...b];
  for (const t of a) { const i = extra.indexOf(t); if (i > -1) extra.splice(i, 1); }
  for (const t of b) { const i = missing.indexOf(t); if (i > -1) missing.splice(i, 1); }
  return { missing: unique(missing), extra: unique(extra) };
}
const unique = (a) => [...new Set(a)];

export function hasIcuPlural(text) {
  return typeof text === 'string' && ICU_PLURAL.test(text);
}

/**
 * Validate plural-key sets. Accepts {pluralObj, locale, categories}.
 * Returns array of {key, problem}. categories = CLDR set for locale,
 * e.g. ar: [zero,one,two,few,many,other], en: [one,other].
 */
export function checkPluralKeys(obj, categories) {
  const problems = [];
  if (!categories) return problems;
  const seen = new Set(Object.keys(obj).filter((k) => ['zero', 'one', 'two', 'few', 'many', 'other'].includes(k)));
  for (const c of categories) if (!seen.has(c)) problems.push({ problem: `missing plural category "${c}"` });
  for (const c of seen) if (!categories.includes(c)) problems.push({ problem: `plural category "${c}" not valid for locale` });
  return problems;
}

// Suffix-style plurals: greeting_one / greeting_other (i18next/vue-i18n/Godot)
const PLURAL_SUFFIX = /_(zero|one|two|few|many|other|0|1|n)$/;
export function pluralSuffix(key) {
  const m = PLURAL_SUFFIX.exec(key);
  return m ? m[1] : null;
}
