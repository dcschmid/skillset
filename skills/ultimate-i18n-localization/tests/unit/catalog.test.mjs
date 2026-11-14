import assert from 'node:assert/strict';
import { parseCatalog, parseYaml, flatten, unflatten } from '../../scripts/lib/catalog.mjs';
export const tests = [];

tests.push(['json nested flatten', () => {
  const r = parseCatalog('{"a":{"b":"x"},"c":"y"}', 'json');
  assert.equal(r.error, undefined);
  assert.equal(r.keys.get('a.b'), 'x');
  assert.equal(r.keys.get('c'), 'y');
}]);

tests.push(['json syntax error reported not swallowed', () => {
  const r = parseCatalog('{"a":}', 'json');
  assert.match(r.error, /parse error/);
}]);

tests.push(['yaml flat + nested', () => {
  const y = parseYaml('a: 1\nb:\n  c: hello\n');
  assert.equal(y.a, 1);
  assert.equal(y.b.c, 'hello');
}]);

tests.push(['csv godot layout (keys,en,de)', () => {
  const r = parseCatalog('keys,en,de\nk1,Home,Startseite\nk2,"Save, really",Speichern', 'csv', { valueColumn: 'de' });
  assert.equal(r.keys.get('k1'), 'Startseite');
  assert.equal(r.keys.get('k2'), 'Speichern');
}]);

tests.push(['csv missing value column -> error', () => {
  const r = parseCatalog('keys,en\nk1,Home', 'csv', { valueColumn: 'de' });
  assert.match(r.error || '', /missing column de/);
}]);

tests.push(['po/pot parse', () => {
  const po = 'msgid "hello"\nmsgstr "hallo"\n\nmsgctxt "menu"\nmsgid "file"\nmsgstr "Datei"\n';
  const r = parseCatalog(po, 'po');
  assert.equal(r.keys.get('hello'), 'hallo');
  const hello = r.meta.entries.find((e) => e.msgid === 'hello');
  assert.equal(hello.msgstrs[0], 'hallo');
}]);

tests.push(['ftl messages', () => {
  const r = parseCatalog('app-title = Mein Shop\nwelcome = Willkommen, {name}!\n', 'ftl');
  assert.equal(r.keys.get('app-title'), 'Mein Shop');
  assert.equal(r.keys.get('welcome'), 'Willkommen, {name}!');
}]);

tests.push(['xliff units', () => {
  const xl = '<trans-unit id="k1"><source>Hello</source><target>Hallo</target></trans-unit>';
  const r = parseCatalog(xl, 'xlf');
  assert.equal(r.keys.get('k1'), 'Hallo');
}]);

tests.push(['flatten/unflatten inverse', () => {
  const src = { a: { b: { c: 'v' } }, d: 'w' };
  assert.deepEqual(unflatten(flatten(src)), src);
}]);
