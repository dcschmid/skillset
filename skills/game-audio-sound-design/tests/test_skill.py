#!/usr/bin/env python3
"""test_skill.py — validation for game-audio-sound-design.

Tier 1 STATIC: structure/frontmatter/router/README contract.
Tier 2 LIVE-no-GPU: synthetic WAV fixtures through doctor/audit/process/
validate/manifest + engine adapters + backend-resolution failure modes
(uses real ffmpeg; generation NOT exercised — that is game-audio-forge's
gaf-test.sh territory, reported NOT_TESTED here).
Exit 0 = all PASS. Non-destructive (temp dirs only).
Usage: python3 tests/test_skill.py [skill_dir]
"""
import json
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else \
    Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

pass_n = fail_n = 0


def check(name, ok, detail=""):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"PASS {name}")
    else:
        fail_n += 1
        print(f"FAIL {name} {detail}")


def run(script, *args, env=None):
    import os
    e = dict(os.environ)
    e.update(env or {})
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          capture_output=True, text=True, env=e, timeout=240)


# ---------------------------------------------------------------- tier 1
skill_md = (ROOT / "SKILL.md").read_text(encoding="utf-8")
fm = re.match(r"^---\n(.*?)\n---\n", skill_md, re.S)
check("frontmatter.parses", bool(fm))
check("frontmatter.name", bool(fm) and "name: game-audio-sound-design"
      in fm.group(1))
desc = re.search(r"description: >\n(.*?)\n---", skill_md, re.S)
check("frontmatter.triggers", bool(desc) and "game-audio-forge" in
      desc.group(1) and "AUDIO" in desc.group(1).upper())
routed = set(re.findall(r"(?:references|templates)/[\w./-]+\.md|"
                        r"templates/[\w./-]+\.json", skill_md))
dead = [t for t in sorted(routed) if not (ROOT / t).is_file()]
check("router.targets_exist", not dead, str(dead))
check("router.compact", len(skill_md.splitlines()) <= 120,
      f"{len(skill_md.splitlines())} lines")
refs = list((ROOT / "references").glob("*.md"))
empty = [p.name for p in refs if p.stat().st_size < 200]
check("references.non_empty", len(refs) >= 10 and not empty, str(empty))
check("readme.gates_backend_first", (ROOT / "README.md").is_file() and
      "Prerequisites" in (ROOT / "README.md").read_text() and
      "game-audio-forge" in (ROOT / "README.md").read_text())

for py in list(SCRIPTS.glob("*.py")) + [Path(__file__)]:
    try:
        py_compile.compile(str(py), doraise=True)
        ok, det = True, ""
    except py_compile.PyCompileError as e:
        ok, det = False, str(e)[:120]
    check(f"compile.{py.name}", ok, det)

# ---------------------------------------------------------------- tier 2
import audio_common as ac          # noqa: E402

tmp = Path(tempfile.mkdtemp(prefix="gaf-skill-test."))
FFMPEG = ac.tool("ffmpeg")
check("host.ffmpeg", FFMPEG is not None)
check("host.python_314_audioop_removed", sys.version_info[:2] >= (3, 12)
      and not __import__("importlib").util.find_spec("audioop"))


def synth(path, kind, dur=1.0, rate=48000, ch=2):
    """Deterministic fixtures: tone / silence / clipped (square, flat_factor 23)."""
    if kind == "clip":
        src = ("aevalsrc=exprs='if(gt(sin(440*2*PI*t)\\,0)\\,1\\,-1)|"
               "if(gt(sin(440*2*PI*t)\\,0)\\,1\\,-1)'")
        args = [FFMPEG, "-y", "-v", "error", "-f", "lavfi", "-i", src,
                "-ar", str(rate), "-t", str(dur), "-c:a", "pcm_s16le", str(path)]
    else:
        src = {"tone": "sine=f=440", "silence": f"anullsrc=r={rate}"}[kind]
        args = [FFMPEG, "-y", "-v", "error", "-f", "lavfi", "-i", src,
                "-ar", str(rate), "-ac", str(ch), "-t", str(dur),
                "-c:a", "pcm_s16le", str(path)]
    subprocess.run(args, check=True)
    return path


proj = tmp / "proj"
(proj / "audio").mkdir(parents=True)
tone = synth(proj / "audio/tone.wav", "tone")
sil = synth(proj / "audio/silence.wav", "silence")
clip = synth(proj / "audio/clip.wav", "clip")
(tone.parent / "tone.meta.json").write_text('{"prompt": "t"}')

# 1. forge resolution: default + env override + missing root
root, src = ac.resolve_gaf_root()
check("forge.detected_default", root is not None and src == "default", str(src))
import importlib
old = ac.DEFAULT_GAF_ROOT
ac.DEFAULT_GAF_ROOT = tmp / "nowhere"
r2, _ = ac.resolve_gaf_root()
check("forge.missing_reports_none", r2 is None)
alt = tmp / "alt-forge"
(alt / "scripts").mkdir(parents=True)
(alt / "scripts/gaf").write_text("#!/bin/sh\n")
r3, s3 = ac.resolve_gaf_root(str(alt))
check("forge.cli_arg_override", r3 == alt and s3 == "--forge-root")
import os
os.environ["GAME_AUDIO_FORGE_ROOT"] = str(alt)
importlib.reload(ac)
r4, s4 = ac.resolve_gaf_root()
check("forge.env_override", r4 == alt and "GAME_AUDIO_FORGE" in s4)
del os.environ["GAME_AUDIO_FORGE_ROOT"]
ac.DEFAULT_GAF_ROOT = old
importlib.reload(ac)

# 2. facts: probe/measure on synthetic + corrupt + unicode/space paths
check("facts.probe", ac.probe(tone).get("rate") == "48000")
check("facts.measure", ac.measure(tone).get("ok") and
      ac.measure(tone)["peak_dbfs"] is not None)
broken = tmp / "broken.wav"           # outside proj — manifests stay clean
broken.write_bytes(b"RIFF junk not audio")
check("facts.corrupt_detected", not ac.probe(broken).get("ok"))
uni = proj / "audio" / "ünïcödé file τῶν.wav"
subprocess.run([FFMPEG, "-y", "-v", "error", "-f", "lavfi", "-i",
                "sine=d=0.3", "-c:a", "pcm_s16le", str(uni)], check=True)
check("facts.unicode_space_path", ac.probe(uni).get("ok"))

# 3. silent/clipping detection through the gate
v = run("audio_validate.py", proj, "--profile", "gameplay-sfx", "--json")
d = json.loads(v.stdout)
per = {Path(r["file"]).name: r for r in d["rows"]}
check("gate.silent_fail", per["silence.wav"]["tests"].get("silence") == "FAIL")
check("gate.clip_fail", per["clip.wav"]["tests"].get("clipping") == "FAIL")
check("gate.lufs_never_fake", all(r["tests"].get("lufs") == "NOT_TESTED"
      for r in d["rows"]))

# 4. process: dry-run plan, apply with recheck, idempotence, no overwrite
out = run("audio_process.py", tone, "--op", "fade", "--dry-run", "--json")
check("process.dry_run", json.loads(run("audio_process.py", tone, "--op",
      "fade", "--dry-run", "--json").stdout)["action"] == "proposed")
p1 = run("audio_process.py", tone, "--op", "normalize -1.0", "--json")
r1 = json.loads(p1.stdout)
check("process.apply_recheck", r1["recheck"] == "PASS" and
      Path(r1["out"]).is_file() and r1["out"] != str(tone))
p2 = run("audio_process.py", tone, "--op", "normalize -1.0", "--json")
check("process.idempotent_unique_out", json.loads(p2.stdout)["out"] !=
      r1["out"], "second run must not overwrite first output")
bad = run("audio_process.py", tone, "--op", "nonsense")
check("process.bad_op_exit2", bad.returncode == 2)

# 5. audit: engine detection + refs + fixes never touch originals
dproj = tmp / "defold-proj"
(dproj / "sounds").mkdir(parents=True)
(dproj / "game.project").write_text("[audio]\nmax_sound_instances=32\n")
(dproj / "sounds/x.sound").write_text('sound = "tone.wav"\n')
shutil.copy(tone, dproj / "sounds/tone.wav")
a = json.loads(run("audio_audit.py", dproj, "--json", "--profile",
                   "ui-sfx").stdout)
check("audit.engine_defold", a["engine"]["engine"] == "defold" and
      a["engine"]["max_sound_instances"] == 32 and
      a["engine"]["referenced"] >= 1 and not a["engine"]["missing"],
      str(a["engine"]))
(dproj / "sounds/ghost.sound").write_text('sound = "gone.wav"\n')
a2 = json.loads(run("audio_audit.py", dproj, "--json").stdout)
check("audit.missing_ref_flagged", any("gone.wav" in m
      for m in a2["engine"]["missing"]) and
      any(x["problem"] == "missing-audio-reference"
          for x in a2["engine_findings"]))
inj = dproj / "sounds" / "broken.wav"
broken.rename(inj)
cor = json.loads(run("audio_audit.py", dproj, "--json").stdout)
check("audit.corrupt_asset_reported", any(
    r["file"].endswith("broken.wav") and any(
        x["problem"] == "unreadable/corrupt" for x in r["findings"])
    for r in cor["asset_findings"]))
inj.rename(broken)
h_before = tone.read_bytes()
fx = json.loads(run("audio_audit.py", proj, "--mode", "fix", "--apply",
                    "--json").stdout)
check("audit.fix_never_touches_original", tone.read_bytes() == h_before and
      fx["fixes"] and all(f.get("action") in
      ("applied", "skipped", "proposed") for f in fx["fixes"]))

# 6. manifest lifecycle incl license seeding
m = run("audio_manifest.py", "create", proj, "--out", tmp / "m.json")
doc = json.loads((tmp / "m.json").read_text())
check("manifest.create", m.returncode == 0 and len(doc["assets"]) >= 3)
check("manifest.recheck_clean_pass",
      run("audio_manifest.py", "check", tmp / "m.json").returncode == 0)
inj = proj / "audio" / "broken.wav"
broken.rename(inj)                                 # inject unreadable asset
run("audio_manifest.py", "create", proj, "--out", tmp / "mb.json")
check("manifest.recheck_catches_corruption", json.loads(
    run("audio_manifest.py", "check", tmp / "mb.json", "--json").stdout
)["verdict"] in ("WARNING", "FAIL"))
inj.rename(broken)                                 # restore scope

# 7. engine adapters (verified APIs only; emit into temp projects)
f_l = run("engine_defold.py", dproj, "--facts", "--json")
check("engine.defold_facts", json.loads(f_l.stdout)["engine"] == "defold")
lua = run("engine_defold.py", dproj, "--lua", tmp / "m.lua", "--json")
lua_txt = (tmp / "m.lua").read_text() if lua.returncode == 0 else ""
check("engine.defold_lua_verified_apis",
      "sound.set_group_gain" in lua_txt and "set_listener" not in lua_txt
      and "sound.set_pan" in lua_txt)
gproj = tmp / "godot-proj"
gproj.mkdir()
(gproj / "project.godot").write_text('config_version=5\n[application]\n')
check("engine.godot_facts", json.loads(
    run("engine_godot.py", gproj, "--facts", "--json").stdout)["engine"] ==
    "godot")

# 8. doctor honest reporting (with and without backend)
doc_j = run("audio_doctor.py", "--project", tmp, "--json")
check("doctor.ready_with_backend", json.loads(doc_j.stdout)["verdict"] in
      ("READY", "PARTIALLY_READY"))
env_missing = {"GAME_AUDIO_FORGE_ROOT": str(tmp / "absent"),
               "HOME": str(tmp)}
dm = subprocess.run([sys.executable, str(SCRIPTS / "audio_doctor.py"),
                     "--project", str(tmp), "--json"],
                    capture_output=True, text=True, env={
                    **{k: v for k, v in os.environ.items()}, **env_missing})
dmj = json.loads(dm.stdout)
forge_c = [c for c in dmj["checks"] if c["check"] == "game-audio-forge"][0]
check("doctor.missing_backend_explained", "git clone" in forge_c["fix"] and
      "game-audio-forge" in forge_c["fix"] and dm.returncode == 0)

# 9. batch: report + convert idempotent naming
b = json.loads(run("audio_batch.py", "report", proj, "--json").stdout)
check("batch.report", b["files"] >= 3)
c1 = json.loads(run("audio_batch.py", "convert", proj / "audio", "--to",
                    "ogg", "--out-dir", tmp / "conv", "--json").stdout)
check("batch.convert_new_files", all(x["action"] == "applied"
      for x in c1["rows"]) and c1["failed"] == 0)

print(f"\nVERDICT {'PASS' if fail_n == 0 else 'FAIL'} "
      f"({pass_n} passed, {fail_n} failed)")
print("NOT_TESTED: GPU generation paths (music/sfx via gaf) — run backend "
      "scripts/gaf-test.sh for those.")
sys.exit(0 if fail_n == 0 else 1)
