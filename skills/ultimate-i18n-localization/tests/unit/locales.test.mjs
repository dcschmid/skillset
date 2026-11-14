import { normalizeLocale, baseLang, isValidLocale, isRtl, pluralCategories, pluralCategory } from '../../scripts/lib/locales.mjs';
import assert from 'node:assert/strict';
export const tests = [];

tests.push(['normalizeLocale canonicalizes', () => {
  assert.equal(normalizeLocale('de_DE'), 'de-DE');
  assert.equal(normalizeLocale('de-at'), 'de-AT');
  assert.equal(normalizeLocale('EN_us'), 'en-US');
  assert.equal(normalizeLocale('zh-Hans-CN'), 'zh-Hans-CN');
  assert.equal(normalizeLocale(''), '');
  assert.equal(normalizeLocale('de'), 'de');
}]);

tests.push(['baseLang/validity', () => {
  assert.equal(baseLang('de-AT'), 'de');
  assert.equal(isValidLocale('de'), true);
  assert.equal(isValidLocale('de-DE'), true);
  assert.equal(isValidLocale('x-default'), true);
  assert.equal(isValidLocale('deutsch'), false);
  assert.equal(isValidLocale(''), false);
}]);

tests.push(['rtl detection', () => {
  assert.equal(isRtl('ar'), true);
  assert.equal(isRtl('he-IL'), true);
  assert.equal(isRtl('de'), false);
}]);

tests.push(['CLDR plural sets', () => {
  assert.deepEqual(pluralCategories('en'), ['one', 'other']);
  assert.deepEqual(pluralCategories('ar'), ['zero', 'one', 'two', 'few', 'many', 'other']);
  assert.deepEqual(pluralCategories('ja'), ['other']);
  assert.equal(pluralCategories('xx'), null);
}]);

tests.push(['pluralCategory matches CLDR subset rules', () => {
  assert.equal(pluralCategory('en', 1), 'one');
  assert.equal(pluralCategory('en', 5), 'other');
  assert.equal(pluralCategory('ar', 0), 'zero');
  assert.equal(pluralCategory('ar', 2), 'two');
  assert.equal(pluralCategory('ar', 3), 'few');
  assert.equal(pluralCategory('ar', 11), 'many');
  assert.equal(pluralCategory('ar', 100), 'other');
  assert.equal(pluralCategory('pl', 2), 'few');
  assert.equal(pluralCategory('pl', 5), 'many');
}]);

