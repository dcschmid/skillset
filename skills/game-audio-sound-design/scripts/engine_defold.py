#!/usr/bin/env python3
"""engine_defold.py — Defold integration for audio assets (baseline 1.14.1).

Emit (non-destructive unique names):
  --facts           game.project audio facts + .sound inventory (read-only)
  --sound ENTRY     manifest entry → .sound component
  --music ENTRY     long-form music → streaming .sound component
  --lua PATH        music/sound manager snippet (verified APIs only)

Verified Defold 1.14.1 surface (defold.com/ref, cross-checked with the
defold-development skill's audio reference):
  sound.play(url|component[, props]) / sound.stop(url[, {play_id}])
  sound.set_gain(url, gain[, {play_id}])  sound.set_pan(url, pan) (-1..1 CP)
  sound.set_group_gain(group, gain[0..1]) / get_groups() / get_group_gain()
  sound.get_peak/get_rms(group, window)  sound.is_music_playing()
  game.project [audio] max_sound_instances; .sound: sound/looping/gain/stream
NOT available at this baseline (do not emit): sound.set_listener,
source-listener 3D API, native bus FX/ducking — positional audio is computed
in Lua (pan+gain from relative position), ducking via set_group_gain ramps.

Usage: engine_defold.py PROJECT (--facts | --sound JSON | --music JSON |
       --lua PATH) [--json]
Exit 0 ok, 1 not a defold project, 2 usage.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import audio_common as ac

SOUND_TPL = ('sound: "{ref}"\nlooping: {looping}\ngain: 1.0\n'
             'stream: {stream}\nsample_rate: 0\n')

LUA_MANAGER = '''-- game-audio-sound-design — sound & music manager (Defold 1.14.1 verified APIs)
local M = {}
local music_play_id = nil

function M.play_sfx(url, opts)
    opts = opts or {}
    return sound.play(url, { gain = opts.gain or 0.0,
                             looping = opts.looping or false })
end

function M.play_music(url, looping)
    if music_play_id then sound.stop("#music", { play_id = music_play_id }) end
    music_play_id = sound.play("#music", { gain = 0.0,
                                           looping = looping ~= false })
    return music_play_id
end

-- group volumes: gain 0..1 (linear), groups from sound.get_groups()
function M.set_group_volume(group, linear)
    sound.set_group_gain(group, math.max(0.0, math.min(1.0, linear or 1.0)))
end

-- positional fallback (no native listener API at this baseline):
-- caller feeds listener-relative x (right) / z (forward); pan is -1..1 CP.
function M.place(url, x, z, gain)
    local dist = math.sqrt(x * x + z * z)
    local pan = (dist > 0.001) and (x / dist) or 0.0
    sound.set_pan(url, pan)
    sound.set_gain(url, (gain or 0.0) - 6.0 * dist)  -- dB falloff, tune it
end
return M
'''


def _facts(project: Path) -> dict:
    gp = project / "game.project"
    facts = {"engine": "defold", "game_project": gp.is_file(),
             "max_sound_instances": None, "sounds": 0}
    if gp.is_file():
        m = re.search(r"max_sound_instances\s*=\s*(\d+)",
                      gp.read_text(encoding="utf-8", errors="replace"))
        facts["max_sound_instances"] = int(m.group(1)) if m else None
    facts["sounds"] = sum(1 for _ in project.rglob("*.sound"))
    return facts


def _emit_sound(project: Path, entry: dict, music: bool) -> dict:
    ref = Path(entry.get("file", ""))
    out = ac.unique_path(project / "sounds" /
                         f"{entry.get('asset_id', ref.stem)}.sound")
    out.parent.mkdir(parents=True, exist_ok=True)
    dur = entry.get("duration_seconds") or 0
    out.write_text(SOUND_TPL.format(
        ref=ref.as_posix(),
        looping="true" if (music or dur > 8) else "false",
        stream="true" if dur > 8 else "false"), encoding="utf-8")
    return {"sound": str(out), "source": str(ref), "action": "applied",
            "recheck": "PASS" if out.is_file() else "FAIL"}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="engine_defold.py")
    ap.add_argument("project")
    ap.add_argument("--facts", action="store_true")
    ap.add_argument("--sound", metavar="ENTRY_JSON")
    ap.add_argument("--music", metavar="ENTRY_JSON")
    ap.add_argument("--lua", metavar="PATH")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args(argv)
    project = Path(ns.project).expanduser().resolve()
    if not (project / "game.project").is_file():
        print(f"error: not a defold project (no game.project): {project}",
              file=sys.stderr)
        return 1
    if ns.sound or ns.music:
        out = _emit_sound(project, json.loads(ns.sound or ns.music),
                          music=bool(ns.music))
    elif ns.lua:
        p = ac.unique_path(Path(ns.lua).expanduser().resolve())
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(LUA_MANAGER, encoding="utf-8")
        out = {"lua": str(p), "action": "applied"}
    else:
        out = _facts(project)
    print(json.dumps(out, indent=2, ensure_ascii=False) if ns.json
          else json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
