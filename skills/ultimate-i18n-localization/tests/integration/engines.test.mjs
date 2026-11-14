import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { join } from 'node:path';
export const tests = [];

const SKILL = new URL('../..', import.meta.url).pathname;
const has = (cmd) => spawnSync('which', [cmd], { encoding: 'utf8' }).status === 0;

tests.push(['godot 4.7 headless translation probe (or NOT TESTED)', () => {
  if (!has('godot')) { console.log('NOT TESTED godot binary missing'); return; }
  const out = execFileSync('godot', ['--headless', '--path', join(SKILL, 'examples/game/godot'), '-s', 'probe_i18n.gd'], { encoding: 'utf8', timeout: 120000 });
  assert.match(out, /PROBE PASS/);
  assert.match(out, /pseudo_braces_ok=true/);
}]);

tests.push(['defold i18n.lua pure-lua core (luajit or NOT TESTED)', () => {
  if (!has('luajit')) { console.log('NOT TESTED luajit missing'); return; }
  const lua = `
    local i = dofile(${JSON.stringify(join(SKILL, 'examples/game/defold/i18n.lua'))})
    local t = i.decode_json(io.open(${JSON.stringify(join(SKILL, 'examples/game/defold/locales/de.json'))}):read('a'))
    assert(t['menu/settings'] == 'Einstellungen')
    i.register('de', t); i.register('en', {['hud/score']='Score: {score}'})
    local ok, rtl = i.set_locale('de'); assert(ok and rtl == false)
    assert(i.t('hud/score', {score=7}) == 'Punkte: 7')
    i.register('ar', {['hud/score']='نتيجة {score}'}); i.set_locale('ar')
    assert(i.is_rtl('ar') and i.pivot('ar') == 'TEXT_PIVOT_E')
    print('LUA PASS')`;
  const out = execFileSync('luajit', ['-e', lua], { encoding: 'utf8', timeout: 30000 });
  assert.match(out, /LUA PASS/);
}]);

tests.push(['defold engine runtime NOT TESTED on this machine (honest marker)', () => {
  // Defold engine is not installed here; adapter claims are docs-verified only.
  const r = spawnSync('defold', ['--version'], { encoding: 'utf8' });
  if (r.error || r.status !== 0) assert.ok(true, 'NOT TESTED (engine absent) — adapters/defold/NOTES.md');
}]);
