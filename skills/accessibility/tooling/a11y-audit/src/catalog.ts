// catalog.ts — axe rule id → { WCAG SC, level, concrete fix hint }.
// SC/level from axe-core 4.14 tags (WCAG 2.2); hints from W3C Understanding docs.
type Entry = { sc: string; level: 'A' | 'AA' | 'AAA' | 'BP'; fix: string };

const CATALOG: Record<string, Entry> = {
  'image-alt': { sc: '1.1.1', level: 'A', fix: 'Add descriptive alt="…" for informative images; alt="" for decorative.' },
  'input-image-alt': { sc: '1.1.1', level: 'A', fix: 'Add alt to <input type="image">.' },
  'video-caption': { sc: '1.2.2', level: 'A', fix: 'Provide synchronized captions; automate only as candidate.' },
  'definition-list': { sc: '1.3.1', level: 'A', fix: 'Use <dl><dt><dd> in pairs.' },
  'dlitem': { sc: '1.3.1', level: 'A', fix: '<dt>/<dd> must live inside <dl>.' },
  'layout-table': { sc: '1.3.1', level: 'A', fix: 'Data tables: add <th scope>; layout tables keep th out.' },
  'list': { sc: '1.3.1', level: 'A', fix: 'Only <li> (and script/template) as direct children of ul/ol.' },
  'listitem': { sc: '1.3.1', level: 'A', fix: '<li> must have ul/ol parent.' },
  'table-fake-caption': { sc: '1.3.1', level: 'A', fix: 'Use <caption> instead of first row/column as pseudo-caption.' },
  'td-headers-attr': { sc: '1.3.1', level: 'A', fix: 'headers must reference existing th ids.' },
  'th-has-data-cells': { sc: '1.3.1', level: 'A', fix: 'Every th column/row needs data cells.' },
  'valid-lang': { sc: '3.1.1', level: 'A', fix: 'Use BCP-47 langs (en, de-DE); lang="" for unknown.' },
  'label': { sc: '4.1.2', level: 'A', fix: 'Give form controls accessible names: wrapping <label for> preferred over aria-label.' },
  'form-field-multiple-labels': { sc: '4.1.2', level: 'A', fix: 'One label per control.' },
  'aria-allowed-attr': { sc: '4.1.2', level: 'A', fix: 'Only ARIA attrs valid for the role/element.' },
  'aria-required-attr': { sc: '4.1.2', level: 'A', fix: 'Add all role-required states/properties.' },
  'aria-roles': { sc: '4.1.2', level: 'A', fix: 'Use roles from ARIA spec list.' },
  'aria-valid-attr-value': { sc: '4.1.2', level: 'A', fix: 'IDREFS must resolve; enums within allowed values.' },
  'aria-valid-attr': { sc: '4.1.2', level: 'A', fix: 'Spelled-correct ARIA attribute names.' },
  'aria-conditional-attr': { sc: '4.1.2', level: 'A', fix: 'Role-conditional attribute values must match role.' },
  'aria-deprecated-role': { sc: '4.1.2', level: 'A', fix: 'Replace deprecated roles (e.g. directory→list, definition→term/description).' },
  'aria-hidden-body': { sc: '4.1.2', level: 'A', fix: 'Never aria-hidden on <body>.' },
  'aria-prohibited-attr': { sc: '4.1.2', level: 'A', fix: 'Some elements (presentational, some generic) forbid naming; wrap or use allowed attrs.' },
  'aria-unsupported-attr': { sc: '4.1.2', level: 'A', fix: 'Remove attributes unsupported in this role/version.' },
  'role-supports-aria-attr': { sc: '4.1.2', level: 'A', fix: 'Element role must support the ARIA attr used.' },
  'accesskey': { sc: '2.1.1', level: 'BP', fix: 'Prefer tab order over accesskey.' },
  'focus-order-semantics': { sc: '1.3.2', level: 'BP', fix: 'Keep DOM order = visual order; tabindex≥1 discouraged.' },
  'tabindex': { sc: '2.4.3', level: 'BP', fix: 'Use tabindex="0"/-1 only; positive values break order.' },
  'link-name': { sc: '2.4.4', level: 'A', fix: 'Links need discernible text (text content, aria-label, or alt of child img).' },
  'button-name': { sc: '4.1.2', level: 'A', fix: 'Buttons need text or accessible name.' },
  'frame-title': { sc: '2.4.4', level: 'A', fix: '<iframe>/<frame> need title describing content.' },
  'heading-order': { sc: '1.3.1', level: 'BP', fix: 'Step headings without skips: h1→h2→h3.' },
  'html-has-lang': { sc: '3.1.1', level: 'A', fix: '<html lang="…">.' },
  'html-lang-valid': { sc: '3.1.1', level: 'A', fix: 'BCP-47 value.' },
  'document-title': { sc: '2.4.2', level: 'A', fix: 'Unique <title> per page.' },
  'meta-viewport': { sc: '1.4.4', level: 'AA', fix: 'Do not disable zoom via user-scalable=no / maximum-scale<2.' },
  'color-contrast': { sc: '1.4.3', level: 'AA', fix: '≥4.5:1 normal, ≥3:1 large (18.66px bold+); see enhanced mode check.' },
  'color-contrast-enhanced': { sc: '1.4.6', level: 'AAA', fix: 'AAA: ≥7:1 normal, ≥4.5:1 large.' },
  'duplicate-id-active': { sc: '4.1.1', level: 'A', fix: 'Unique ids among focusable.' },
  'duplicate-id': { sc: '4.1.1', level: 'A', fix: 'ids unique in document.' },
  'aria-treeitem-name': { sc: '4.1.2', level: 'A', fix: 'treeitem needs accessible name.' },
  'nested-interactive': { sc: '4.1.2', level: 'BP', fix: 'No focusable inside button/summary-with-control.' },
  'region': { sc: '1.3.1', level: 'BP', fix: 'All content in landmarks.' },
  'landmark-one-main': { sc: '1.3.1', level: 'BP', fix: 'Exactly one <main>.' },
  'page-has-heading-one': { sc: '1.3.1', level: 'BP', fix: 'One h1 describing page topic.' },
  'identical-links-same-purpose': { sc: '2.4.4', level: 'AAA', fix: 'AAA: identical accessible-name links must share destination.' },
  'meta-refresh': { sc: '2.2.1', level: 'AA', fix: 'Timings adjustable or allow user to extend/turn off.' },
  'meta-refresh-no-exceptions': { sc: '2.2.4', level: 'AAA', fix: 'AAA: no timed refresh except user-controlled.' },
  'blink': { sc: '2.2.2', level: 'A', fix: 'No blink; pausable content.' },
  'marquee': { sc: '2.2.2', level: 'A', fix: 'No marquee; pausable content.' },
  'target-size': { sc: '2.5.8', level: 'AA', fix: 'Pointer targets ≥24×24 CSS px (or spacing-met).' },
  'aria-roledescription': { sc: '4.1.2', level: 'AA', fix: 'roledescription only on role-bearing elements.' },
  'audio-caption': { sc: '1.2.5', level: 'AA', fix: 'Captions for prerecorded audio in sync media.' },
};

export function scName(ruleId: string): string {
  return CATALOG[ruleId]?.sc ?? ruleId;
}
export function levelOf(ruleId: string): 'A' | 'AA' | 'AAA' | 'BP' {
  return CATALOG[ruleId]?.level ?? 'AA';
}
export function fixHint(ruleId: string): string {
  return CATALOG[ruleId]?.fix ?? 'Consult axe message + W3C Understanding doc for the mapped SC.';
}
