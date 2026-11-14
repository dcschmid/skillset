import assert from 'node:assert/strict';
import { extractPlaceholders, diffPlaceholders, checkPluralKeys, pluralSuffix } from '../../scripts/lib/placeholders.mjs';
export const tests = [];

tests.push(['named/numeric/icu/sprintf tokens', () => {
  assert.deepEqual(extractPlaceholders('Hi {name}'), ['{name}']);
  assert.deepEqual(extractPlaceholders('{{nested}}'), ['{nested}']);
  assert.deepEqual(extractPlaceholders('{0} und {1}'), ['{0}', '{1}']);
  assert.deepEqual(extractPlaceholders('%d Stück %s'), ['%d', '%s']);
  assert.deepEqual(extractPlaceholders('%1$s und %2$d'), ['%1$s', '%2$d']);
  assert.deepEqual(extractPlaceholders('{count, plural, one {x} other {y}}'), ['{count}']);
}]);

tests.push(['dedupe + sorted', () => {
  assert.deepEqual(extractPlaceholders('{b} {a} {b}'), ['{a}', '{b}', '{b}']); // multiset
}]);

tests.push(['diff missing/extra', () => {
  const d = diffPlaceholders('Hallo {name}', 'Hello {username}');
  assert.deepEqual(d.missing, ['{name}']);
  assert.deepEqual(d.extra, ['{username}']);
  assert.deepEqual(diffPlaceholders('{a} {b}', '{b} {a}').missing, []);
}]);

tests.push(['plural key checks', () => {
  assert.deepEqual(checkPluralKeys({ one: 1, other: 1 }, ['one', 'other']), []);
  const bad = checkPluralKeys({ one: 1 }, ['one', 'other']);
  assert.equal(bad.length, 1);
  assert.match(bad[0].problem, /missing plural category "other"/);
  const wrong = checkPluralKeys({ few: 1 }, ['other']);
  assert.ok(wrong.some((p) => /not valid/.test(p.problem)), JSON.stringify(wrong));
}]);

tests.push(['suffix plurals', () => {
  assert.equal(pluralSuffix('items_one'), 'one');
  assert.equal(pluralSuffix('items_other'), 'other');
  assert.equal(pluralSuffix('items'), null);
}]);
