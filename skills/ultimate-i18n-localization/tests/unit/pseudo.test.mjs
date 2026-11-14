import assert from 'node:assert/strict';
import { pseudo, graphemeCount, unicodeFindings } from '../../scripts/lib/pseudo.mjs';
export const tests = [];

tests.push(['accent map expands, preserves placeholders + newlines', () => {
  const p = pseudo('Hello {name}', { expand: 0.3 });
  assert.match(p, /^\[.*\]$/);
  assert.ok(p.includes('{name}'), 'placeholder survives');
  assert.ok(p.length > 'Hello {name}'.length, 'expansion grows text');
  const nl = pseudo('a\nb', { expand: 0 });
  assert.ok(nl.includes('\n'), 'newline kept');
}]);

tests.push(['zero expansion keeps length except accents', () => {
  const p = pseudo('abc', { expand: 0 });
  assert.equal(graphemeCount(p), 3);
}]);

tests.push(['rtl isolate wrap', () => {
  const p = pseudo('Hallo', { rtl: true, expand: 0 });
  assert.ok(p.codePointAt(0) === 0x202b && p.codePointAt(p.length - 1) === 0x202c, 'bidi isolates');
}]);

tests.push(['graphemes not codepoints', () => {
  assert.equal(graphemeCount('é'), 1); // precomposed
  assert.ok(graphemeCount('👨‍👩‍👧') <= 3, 'family emoji is one-or-few graphemes, many codepoints');
}]);

tests.push(['unicode findings detect mojibake and BOM', () => {
  assert.equal(unicodeFindings('Ã©').some((f) => f.type === 'mojibake'), true);
  assert.equal(unicodeFindings('sauber').length, 0);
}]);
