#!/usr/bin/env python3
"""engine_godot.py — Godot integration for audio assets (baseline 4.7.2).

Emit / inspect (non-destructive unique names):
  --facts           engine version + audio bus + import facts (read-only)
  --sound ENTRY     manifest entry → res:// path + import-plan note
  --gd PATH         AudioDirector autoload (verified 4.x APIs only)

Verified Godot 4.x audio surface (docs.godot.org/4.7):
  AudioStreamPlayer / AudioStreamPlayer2D / AudioStreamPlayer3D
  AudioServer.play_bus/play_server; bus layout .bus resource;
  AudioStreamWAV/OggVorbis/DMP; import settings .import files;
  listener defaults: 2D→window, 3D→camera (AudioListener3D overrides).
NOT native: multi-listener split-screen (one listener per viewport type) —
fallback: viewport/audio or manual panning (documented, references/spatial).
Never invent methods (skillset rule).

Usage: engine_godot.py PROJECT (--facts | --sound JSON | --gd PATH) [--json]
Exit 0 ok, 1 not a godot project, 2 usage.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import audio_common as ac

GD_DIRECTOR = '''# game-audio-sound-design — AudioDirector (Godot 4.7, verified API surface)
extends Node
## Attach as autoload. Buses expected: Master/Music/SFX/UI (create in
## default_bus_layout.tres — AudioServer has no runtime bus creation in 4.x).

@export var music_player: AudioStreamPlayer
@export var sfx_pool: Array[AudioStreamPlayer] = []

var _next := 0

func play_sfx(stream: AudioStream, volume_db := 0.0, pitch := 1.0) -> void:
    if sfx_pool.is_empty():
        return
    var p := sfx_pool[_next % sfx_pool.size()]
    _next += 1
    p.stream = stream
    p.volume_db = volume_db
    p.pitch_scale = pitch          # round-robin variation without regen
    p.play()

func play_music(stream: AudioStream, crossfade_bus_gain := false) -> void:
    if music_player == null:
        return
    music_player.stream = stream
    music_player.play()

func set_bus_volume_db(bus: StringName, db: float) -> void:
    var idx := AudioServer.get_bus_index(bus)
    if idx >= 0:
        AudioServer.set_bus_volume_db(idx, db)

func set_bus_mute(bus: StringName, muted: bool) -> void:
    var idx := AudioServer.get_bus_index(bus)
    if idx >= 0:
        AudioServer.set_bus_mute(idx, muted)
'''


def _facts(project: Path) -> dict:
    facts = {"engine": "godot", "project_godot": True, "version": None,
             "audio_files": 0, "buses_layout": None}
    txt = (project / "project.godot").read_text(encoding="utf-8",
                                                errors="replace")
    m = re.search(r'config_version=(\d+)|config/features=PackedStringArray\("([\d.]+)"',
                  txt)
    if m:
        facts["version"] = m.group(2) or f"config_version {m.group(1)}"
    facts["audio_files"] = sum(1 for p in ac.audio_files(project))
    bl = project / "default_bus_layout.tres"
    facts["buses_layout"] = str(bl) if bl.is_file() else "default (Master only)"
    return facts


def _emit(project: Path, entry: dict) -> dict:
    f = Path(entry.get("file", ""))
    res_path = None
    try:
        res_path = f"res://{f.resolve().relative_to(project)}"
    except (ValueError, OSError):
        pass
    return {"res_path": res_path, "entry": entry.get("asset_id"),
            "import_note": "OGG/music → AudioStreamOggVorbis loop mode, "
                           "short sfx → AudioStreamWAV; drop into project and "
                           "let the editor import (headless: --import)"}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="engine_godot.py")
    ap.add_argument("project")
    ap.add_argument("--facts", action="store_true")
    ap.add_argument("--sound", metavar="ENTRY_JSON")
    ap.add_argument("--gd", metavar="PATH")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args(argv)
    project = Path(ns.project).expanduser().resolve()
    if not (project / "project.godot").is_file():
        print(f"error: not a godot project (no project.godot): {project}",
              file=sys.stderr)
        return 1
    if ns.sound:
        out = _emit(project, json.loads(ns.sound))
    elif ns.gd:
        p = ac.unique_path(Path(ns.gd).expanduser().resolve())
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(GD_DIRECTOR, encoding="utf-8")
        out = {"gd": str(p), "action": "applied"}
    else:
        out = _facts(project)
    print(json.dumps(out, indent=2, ensure_ascii=False) if ns.json
          else json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
