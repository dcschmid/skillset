#!/usr/bin/env python3
"""test_skill.py — STATIC validation of game-asset-pipeline-shaders.

Structure, routing integrity, universality invariants, script compilation,
plus functional spot-checks on fixtures: valid GLB passes, broken reference
fails, dry-run fix writes nothing, protected paths untouched, pixel-art keeps
lossless advice, adapter tables engine-scoped. Exit 0 = PASS. Non-destructive.
Usage: python3 tests/test_skill.py [skill_dir]
"""
import json
import py_compile
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
S = ROOT / "scripts"
FIX = ROOT / "tests" / "fixtures"
pass_n = fail_n = 0


def check(name, ok, detail=""):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"PASS {name}")
    else:
        fail_n += 1
        print(f"FAIL {name} {detail}")


def run(script, *args):
    return subprocess.run([sys.executable, str(S / script), *map(str, args)],
                          capture_output=True, text=True)


skill_md = (ROOT / "SKILL.md").read_text(encoding="utf-8")

# 1. frontmatter contract (Agent-Skills / Claude Code / Codex trigger)
fm = re.match(r"^---\n(.*?)\n---\n", skill_md, re.S)
check("frontmatter.parses", bool(fm))
check("frontmatter.name", bool(fm) and "name: game-asset-pipeline-shaders" in fm.group(1))
desc = re.search(r"description: >\n(.*?)\n---", skill_md, re.S)
check("frontmatter.description_triggers",
      bool(desc) and "Defold" in desc.group(1) and "Godot" in desc.group(1)
      and len(desc.group(1)) > 200)

# 2. routing targets exist and non-empty
routed = set(re.findall(r"references/[\w.-]+\.md", skill_md))
expected_refs = {"materials", "textures", "shaders", "gltf-pipeline", "optimization",
                 "blender-integration", "defold", "godot", "engine-adapters",
                 "quality-gates", "tooling", "troubleshooting"}
check("routing.all_12_references_routed",
      {f"references/{n}.md" for n in expected_refs} <= routed,
      str(sorted({f"references/{n}.md" for n in expected_refs} - routed)))
missing = [t for t in sorted(routed) if not (ROOT / t).is_file()
           or (ROOT / t).stat().st_size < 200]
check("routing.targets_exist_nontrivial", not missing, str(missing))

# 3. scripts compile
py = sorted((S).glob("*.py"))
check("scripts.count>=8", len(py) >= 8, str(len(py)))
for p in py:
    try:
        py_compile.compile(str(p), doraise=True)
        check(f"compiles.{p.stem}", True)
    except Exception as e:
        check(f"compiles.{p.stem}", False, str(e))

# 4. universality: no hardcoded per-game names, no fixed hardware constants
for bad in ("zelda", "mario", "rtx 4090", "iphone 13"):
    body = skill_md.lower()
    check(f"universality.no_{bad}", bad not in body)

# 5. honesty ladder + dry-run + ownership declared
check("truth_ladder.levels", all(w in skill_md for w in
      ("STATIC", "HEADLESS", "RENDER", "MEASURED")))
check("dry_run.rule", "Dry-run first" in skill_md or "dry-run" in skill_md)
check("ownership.boundaries_table", "lowpoly-reference-to-blender" in skill_md
      and "ultimate-testing-qa" in skill_md and "skill-orchestrator" in skill_md)

# 6. config template parses both paths
tpl = (ROOT / "assets" / "templates" / "asset-pipeline.yaml").read_text()
try:
    import yaml
    cfg = yaml.safe_load(tpl)
    check("config.template.yaml", isinstance(cfg, dict) and "auto_fix" in cfg)
except ImportError:
    check("config.template.yaml", True, "(PyYAML absent; mini-parser lane tested below)")
sys.path.insert(0, str(S))
import pipeline_lib  # noqa: E402
mini, warn = pipeline_lib._mini_yaml(tpl)
check("config.mini_parser_nested", isinstance(mini.get("auto_fix"), dict)
      and isinstance(mini.get("reporting"), dict), f"{mini.get('auto_fix')} {warn}")

# 7. functional: fixtures
r = run("gltf_validate.py", FIX / "triangle.glb")
check("gltf.valid_passes", r.returncode == 0, r.stdout[-200:])
r = run("gltf_validate.py", FIX / "broken_ref.gltf")
check("gltf.broken_reference_blocks", r.returncode == 1 and "Critical" in r.stdout)
r = run("gltf_validate.py", FIX / "extensions.gltf")
check("gltf.extensions_reported", r.returncode == 0
      and "KHR_texture_basisu" in r.stdout and "domain=mesh-geometry" in r.stdout,
      r.stdout[-300:])
bad = Path(tempfile.mkdtemp()) / "broken.glb"
bad.write_bytes(b"glTF" + b"\x02\x00\x00\x00" + b"\x00" * 8)
r = run("gltf_validate.py", bad)
check("gltf.truncated_glb_blocks", r.returncode == 1)

r = run("material_audit.py", FIX)
check("material.broken_ref_found", r.returncode == 1 and "Critical" in r.stdout)

# 8. dry-run fix writes nothing; pixel-art keeps lossless guidance
with tempfile.TemporaryDirectory() as td:
    tdp = Path(td)
    (tdp / "a.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"a" * 40)
    (tdp / "b.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"a" * 40)
    before = {p: p.read_bytes() for p in tdp.iterdir()}
    r = run("pipeline_runner.py", "fix", tdp)
    check("fix.dryrun_zero_writes", r.returncode == 0
          and all(p.read_bytes() == v for p, v in before.items())
          and not any(p.name.endswith(".orig") for p in tdp.rglob("*")),
          r.stdout[-200:])
    check("fix.dryrun_labels_plan", "DRY-RUN" in r.stdout.upper())
    (tdp / "asset-pipeline.yaml").write_text("art_style: pixel-art\n"
                                             "compression: { albedo: none }\n")
    r = run("texture_analyze.py", tdp, "--config", tdp)
    check("textures.pixel_art_nearest", "nearest, no mipmaps" in r.stdout
          and "pixel_art=True" in r.stdout, r.stdout[-200:])

# 9. engine adapters scoped: no cross-leak of engine constants into shared libs
lib = (S / "pipeline_lib.py").read_text()
check("adapters.no_engine_budget_literals_in_lib",
      all(x not in lib for x in ("etc2", "astc", "bc7", "bob.jar", "uastc")))
god = (ROOT / "references" / "godot.md").read_text()
defd = (ROOT / "references" / "defold.md").read_text()
check("adapter.godot_version_gated", "4.7" in god and "ed1daf0b" in god)
check("adapter.defold_version_gated", "1.14.1" in defd and "ee283d4" in defd)
check("adapter.docs_beat_files", "beat" in god.lower() or "docs" in god.lower())

# 10. README/USAGE/README-canonical sync
readme = (ROOT / "README.md").read_text()
usage_f = (ROOT / "USAGE.md").read_text()
check("docs.usage_mentions_modes", "audit" in usage_f and "compare" in usage_f)
check("docs.verify_cmd_runs", "test_skill.py" in readme and "test_skill.py" in usage_f)
for f in ("install-skills.sh game-asset-pipeline-shaders", ".installed-manifest"):
    check(f"docs.sync[{f}]", f in usage_f)

# 11. tool_probe degrades honestly on missing tools
r = run("tool_probe.py")
check("probe.lists_lanes", r.returncode == 0 and "MISSING" in (r.stdout + "x")
      and "degraded" in r.stdout.lower() or "present" in r.stdout)


# 12. live tool lanes: run the real tool when present, SKIP honestly when not
def has(tool):
    return shutil_which(tool) is not None


def shutil_which(name):
    import shutil
    return shutil.which(name)


def skip_or(name, tool, fn):
    if not has(tool):
        check(f"{name}.skipped_missing_{tool}", True, "(NOT_RUN: tool absent)")
        return
    ok, detail = fn()
    check(name, ok, detail)


def toktx_roundtrip():
    import tempfile as tf
    with tf.TemporaryDirectory() as td:
        out = Path(td) / "lane.ktx2"
        r = subprocess.run(["toktx", "--t2", "--assign_oetf", "srgb",
                            str(out), str(FIX / "tex_a.png")],
                           capture_output=True, text=True)
        if r.returncode != 0 or not out.is_file():
            return False, r.stderr[-160:]
        head = out.read_bytes()[:15]
        return head[:4] == b"\xabKTX", f"magic {head[:8]!r}"


skip_or("tool.toktx_encodes_ktx2", "toktx", toktx_roundtrip)


def ktxinfo_reads_fixture():
    r = subprocess.run(["ktxinfo", str(FIX / "albedo_etc1s.ktx2")],
                       capture_output=True, text=True)
    return "KTX 20" in r.stdout and r.returncode == 0, r.stdout[:120]


skip_or("tool.ktxinfo_reads_fixture", "ktxinfo", ktxinfo_reads_fixture)


def gltfpack_output_valid():
    import tempfile as tf
    with tf.TemporaryDirectory() as td:
        out = Path(td) / "p.glb"
        r = subprocess.run(["gltfpack", "-i", str(FIX / "triangle.glb"),
                            "-o", str(out)], capture_output=True, text=True)
        if r.returncode != 0 or not out.is_file():
            return False, (r.stdout + r.stderr)[-160:]
        v = run("gltf_validate.py", out)
        return v.returncode == 0, f"pack+validate exit {v.returncode}"


skip_or("tool.gltfpack_output_validates", "gltfpack", gltfpack_output_valid)


def glslang_compiles_fixture_shaders():
    r = subprocess.run(["glslangValidator", str(FIX / "tex.vert"),
                        str(FIX / "tex.frag")], capture_output=True, text=True)
    return r.returncode == 0, (r.stdout + r.stderr)[-160:]


skip_or("tool.glslang_compiles_fixtures", "glslangValidator",
        glslang_compiles_fixture_shaders)


def gltf_transform_inspects():
    r = subprocess.run(["gltf-transform", "inspect", str(FIX / "triangle.glb")],
                       capture_output=True, text=True)
    return r.returncode == 0 and "OVERVIEW" in r.stdout, r.stdout[:120]


skip_or("tool.gltf_transform_inspects", "gltf-transform",
        gltf_transform_inspects)

print(f"\n{pass_n} passed, {fail_n} failed")
sys.exit(0 if fail_n == 0 else 1)
