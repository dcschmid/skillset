// locales.mjs — canonical locale handling (BCP-47 subset + CLDR plural facts).
// Verified facts: probe targets are documented in references/standards.md.

const LANGS = {
  de: 'Deutsch', en: 'English', fr: 'Français', es: 'Español', it: 'Italiano',
  pt: 'Português', pl: 'Polski', ja: '日本語', ko: '한국어', zh: '中文',
  ar: 'العربية', he: 'עברית', tr: 'Türkçe', nl: 'Nederlands', sv: 'Svenska',
  ru: 'Русский', cs: 'Čeština', uk: 'Українська', hi: 'हिन्दी', th: 'ไทย',
};

// Regions commonly paired with a language (NOT auto-assumed at runtime;
// see SKILL.md: regions are only used when the project declares them).
export const KNOWN_REGIONS = {
  de: ['DE', 'AT', 'CH'], en: ['US', 'GB', 'AU', 'CA'], pt: ['BR', 'PT'],
  zh: ['CN', 'TW', 'HK'], es: ['ES', 'MX', 'AR'], fr: ['FR', 'CA', 'CH', 'BE'],
  ar: ['SA', 'EG', 'AE'], sr: ['RS'], it: ['IT'], pl: ['PL'], ja: ['JP'],
  ko: ['KR'], he: ['IL'], tr: ['TR'], nl: ['NL', 'BE'], sv: ['SE'], ru: ['RU'],
};

// ISO-639-1 -> ISO-15921 preferred script fallback when a font stack needs one.
export const RTL_LANGS = new Set(['ar', 'he', 'fa', 'ur', 'yi', 'ps', 'sd', 'ckb']);

// CLDR plural categories per language (verified against cldr.unicode.org
// plural-rules, probe 2026-11-14). Languages outside this table report
// ['other'] plus an INFO finding — never a guess.
export const PLURAL_CATEGORIES = {
  en: ['one', 'other'], de: ['one', 'other'], nl: ['one', 'other'],
  sv: ['one', 'other'], da: ['one', 'other'], no: ['one', 'other'],
  nb: ['one', 'other'], nn: ['one', 'other'], fi: ['one', 'other'],
  et: ['one', 'other'], hu: ['one', 'other'], el: ['one', 'other'],
  es: ['one', 'other'], pt: ['one', 'other'], it: ['one', 'other'],
  bg: ['one', 'other'], tr: ['other'], ja: ['other'], ko: ['other'],
  zh: ['other'], th: ['other'], vi: ['other'], id: ['other'], ms: ['other'],
  hi: ['one', 'other'],
  fr: ['one', 'many', 'other'],
  cs: ['one', 'few', 'other'],
  he: ['one', 'two', 'many', 'other'],
  uk: ['one', 'few', 'many', 'other'],
  ru: ['one', 'few', 'many', 'other'],
  pl: ['one', 'few', 'many', 'other'],
  ar: ['zero', 'one', 'two', 'few', 'many', 'other'],
  cy: ['zero', 'one', 'two', 'few', 'many', 'other'],
  ga: ['one', 'two', 'few', 'many', 'other'],
  lv: ['zero', 'one', 'other'],
  ro: ['one', 'few', 'other'],
  lt: ['one', 'few', 'other'],
};

const REGION_TAG = /^[A-Z]{2}$|^[0-9]{3}$/;
const SUBTAG = /^[A-Za-z]{2,8}$/;

/** Normalize 'de_DE','de-DE ','DE_de','de-at' -> 'de-DE'; '' for garbage. */
export function normalizeLocale(tag) {
  if (typeof tag !== 'string') return '';
  const parts = tag.trim().replace(/_/g, '-').split('-').filter(Boolean);
  if (!parts.length) return '';
  const out = [parts[0].toLowerCase()];
  const rest = parts.slice(1);
  if (rest.length && /^[A-Za-z]{4}$/.test(rest[0])) { // script subtag
    out.push(title(rest[0]));
    rest.shift();
  }
  const rIdx = rest.findIndex((p) => /^[A-Za-z]{2}$/.test(p) || /^[0-9]{3}$/.test(p));
  if (rIdx > -1) {
    out.push(rest[rIdx].toUpperCase());
    rest.splice(rIdx, 1);
  }
  out.push(...rest.map((r) => (REGION_TAG.test(r) ? r : /^[A-Za-z0-9]{4,8}$/.test(r) ? title(r) : null)).filter(Boolean));
  return out.join('-');
}

const title = (s) => s[0].toUpperCase() + s.slice(1).toLowerCase();

/** Primary subtag: 'de-AT' -> 'de'. '' for invalid. */
export function baseLang(tag) {
  const n = normalizeLocale(tag);
  return n ? n.split('-')[0] : '';
}

export function isRtl(tag) {
  return RTL_LANGS.has(baseLang(tag));
}

export function localeName(tag) {
  return LANGS[baseLang(tag)] || null;
}

export function pluralCategories(tag) {
  return PLURAL_CATEGORIES[baseLang(tag)] || null; // null = unknown, caller reports INFO
}

/** CLDR plural category of an integer count for a language (subset rules). */
export function pluralCategory(tag, n) {
  const lang = baseLang(tag);
  const cats = PLURAL_CATEGORIES[lang];
  if (!cats) return null;
  const i = Math.trunc(Math.abs(n));
  switch (lang) {
    case 'en': case 'de': case 'nl': case 'sv': case 'da': case 'no': case 'nb':
    case 'nn': case 'fi': case 'et': case 'hu': case 'el': case 'es': case 'pt':
    case 'it': case 'bg': case 'hi':
      return i === 1 ? 'one' : 'other';
    case 'fr':
      return i === 0 || i === 1 ? 'one' : (i >= 1000000 && i % 1000000 === 0 ? 'many' : 'other');
    case 'cs':
      return i === 1 ? 'one' : (i >= 2 && i <= 4 ? 'few' : 'other');
    case 'he':
      return i === 1 ? 'one' : (i === 2 ? 'two' : (i >= 11 && i <= 99 && (i % 10 !== 0) ? 'many' : 'other'));
    case 'uk': case 'ru':
      if (i % 10 === 1 && i % 100 !== 11) return 'one';
      if (i % 10 >= 2 && i % 10 <= 4 && !(i % 100 >= 12 && i % 100 <= 14)) return 'few';
      return 'many';
    case 'pl':
      if (i === 1) return 'one';
      if (i % 10 >= 2 && i % 10 <= 4 && !(i % 100 >= 12 && i % 100 <= 14)) return 'few';
      return 'many';
    case 'ar':
      if (i === 0) return 'zero';
      if (i === 1) return 'one';
      if (i === 2) return 'two';
      const m = i % 100;
      if (m >= 3 && m <= 10) return 'few';
      if (m >= 11 && m <= 99) return 'many';
      return 'other';
    default:
      return cats.length === 1 ? 'other' : (i === 1 ? 'one' : 'other');
  }
}

/** BCP-47 valid tag check used by audits; accepts language[-Script][-REGION][-variants]. */
export function isValidLocale(tag) {
  if (tag === 'x-default') return true;
  const n = normalizeLocale(tag);
  if (!n) return false;
  return /^[a-z]{2,3}(-[A-Z][a-z]{3})?(-([A-Z]{2}|[0-9]{3}))?(-([A-Za-z0-9]{4,8}|[0-9][A-Za-z0-9]{3}))*$/.test(n);
}
