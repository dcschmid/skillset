# Engine integration

## Detection

`game.project` → Defold · `project.godot` → Godot · else generic (asset
delivery + manifest only; adapters idle). Version from project files or the
defold/godot skills' probes — never assume.

## Defold (baseline 1.14.1, sha ee283d4)

`engine_defold.py --facts` inventory · `--sound/--music ENTRY` emits `.sound`
(sound/looping/gain/stream/sample_rate) · `--lua` manager using ONLY verified
APIs: `sound.play/stop/set_gain/set_pan/set_group_gain/get_groups/
get_group_gain/get_peak/get_rms`, `[audio] max_sound_instances`. NOT emitted
(verify per project): listener/source 3D, bus FX, ducking — computed fallbacks
in spatial-audio.md. Assets: short sfx wav (stream false), music/ambience ogg
or long wav (stream true). msg-based GO components: `msg.post("#sound",
"play_sound")` — carry play_id for handle control.

## Godot (baseline 4.7.2)

`engine_godot.py --facts` (version/features, audio file count, bus layout) ·
`--sound` → res:// path + import note · `--gd` AudioDirector autoload
(AudioStreamPlayer pool, `AudioServer.get_bus_index/set_bus_volume_db/
set_bus_mute`, Player2D/3D). Import: editor or headless `--import`
(godot skill's headless_check exists for projects). One listener per
viewport type — split-screen per spatial-audio.md ladder.

## Generic / adapter-ready

Unity/Unreal: no implementation shipped (no API verified, no test target —
state as adapter-ready, never claim). Interface = manifest + measured facts
+ per-engine loudness/loop conventions; an adapter consumes manifest and
emits engine-native references behind the same QA gates.

## Integration QA (all engines)

missing references = audit engine finding · post-integration: play every
state (menu→gameplay→pause→scene-change) and confirm no double/orphan audio ·
volume sliders affect intended buses only.
