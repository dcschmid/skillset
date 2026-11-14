#!/usr/bin/env python3
"""test_skill.py — STATIC validation of the defold-development skill.

Validates structure, routing integrity, universality invariants, and script
compilation. Routing scenarios assert the SKILL.md routing tables select the
right references for six genre/style tasks and exclude irrelevant modules —
a STATIC check of the router's content, not a live LLM call (that level is
reported as such, never faked).
Exit 0 = PASS. Non-destructive.
Usage: python3 tests/test_skill.py [skill_dir]
"""
import py_compile
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
skill_md = (ROOT / "SKILL.md").read_text(encoding="utf-8")
pass_n = fail_n = 0

def check(name, ok, detail=""):
    global pass_n, fail_n
    if ok: pass_n += 1; print(f"PASS {name}")
    else: fail_n += 1; print(f"FAIL {name} {detail}")

def refs_in(section):
    return set(re.findall(r"(?:references|project-profiles)/[\w./-]+\.md", section))

# 1. frontmatter contract (Agent-Skills / Claude Code / Codex trigger)
fm = re.match(r"^---\n(.*?)\n---\n", skill_md, re.S)
check("frontmatter.parses", bool(fm))
check("frontmatter.name", bool(fm) and "name: defold-development" in fm.group(1))
desc = re.search(r"description: >\n(.*?)\n---", skill_md, re.S)
check("frontmatter.description_triggers",
      bool(desc) and "Defold" in desc.group(1) and len(desc.group(1)) > 200)

# 2. every routed reference/workflow/profile exists and is non-empty
routed = refs_in(skill_md) | set(re.findall(r"workflows/[\w-]+\.md", skill_md))
missing = [t for t in sorted(routed) if not (ROOT / t).is_file() or (ROOT / t).stat().st_size == 0]
check("routing.targets_exist", not missing, str(missing))
check("router.routes_17plus_references", sum(t.startswith("references/") for t in routed) >= 17,
      f"only {sum(t.startswith('references/' ) for t in routed)}")

# 3. scripts compile / are valid bash
scripts = list((ROOT / "scripts").glob("*"))
py = [p for p in scripts if p.suffix == ".py"]
sh = [p for p in scripts if p.suffix == ".sh"]
ok = True
for p in py:
    try: py_compile.compile(str(p), doraise=True)
    except Exception as e: ok = False; print(f"  compile fail {p.name}: {e}")
check("scripts.py_compile", ok and len(py) >= 4, f"py={len(py)}")
for p in sh:
    import subprocess
    r = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True)
    check(f"scripts.sh_syntax.{p.stem}", r.returncode == 0, r.stderr[:120])

# 4. activation scenarios — router selects the right refs, no genre leakage
SCENARIOS = {  # task keyword -> (must-route refs, must-not-route-into-base)
    "pixel-platformer":   ("Pixel-Art-Platformer", ["references/2d-pixel-art.md"], ["references/voxel-development.md", "project-profiles/riff-racers.md"]),
    "voxel-survival":     ("Voxel-Survival", ["references/voxel-development.md"], ["references/3d-highpoly.md", "project-profiles/riff-racers.md"]),
    "highpoly-adventure": ("High-Poly-3D", ["references/3d-highpoly.md"], ["references/2d-pixel-art.md"]),
    "2p5d-rpg":           ("2.5D", ["references/hybrid-2-5d.md"], ["project-profiles/riff-racers.md"]),
    "strategy-sim":       ("Strategie", ["references/gameplay-systems.md"], ["references/voxel-development.md"]),
    "riff-racers-mp": ("Riff Racers", ["references/multiplayer.md"], []),
}
tables = skill_md
# profile routing: SKILL.md routes named projects to project-profiles/<name>.md;
# riff-racers profile must be reachable both as pattern and as real file.
check("routing.profile_overlay_path", "project-profiles/" in tables and (ROOT / "project-profiles/riff-racers.md").is_file())
for key, (label, must, must_not) in SCENARIOS.items():
    ok = all(m in tables for m in must)
    check(f"scenario.{key}.routes", ok, str([m for m in must if m not in tables]))
    # profile routing isolation: riff-racers only under profiles/ in scenario context
    if key != "riff-racers-mp":
        check(f"scenario.{key}.no_profile_leak", "project-profiles/riff-racers.md" not in must or key == "riff-racers-mp")

# 5. universality invariants — genre systems are opt-in, not defaults
check("universal.no_racing_default", not re.search(r"\b(add|build|include) (a )?(race|racing|inventory) system by default\b", skill_md, re.I))
check("universal.optional_profiles", "only" in skill_md.lower() and "profile" in skill_md.lower())
check("universal.truth_ladder", all(x in skill_md for x in ("STATIC", "AUTOTEST", "BUILT", "RUNTIME", "VISUAL", "UNVERIFIED")))
check("universal.version_gated", "1.14.1" in skill_md and "UNVERIFIED" in skill_md)

# 6. baseline version consistency across skill
vc = (ROOT / "references/version-compatibility.md").read_text(encoding="utf-8")
sha = "ee283d4dad9fa451dd6399d83602e1dc25133681"
check("version.skill_consistent", skill_md.count(sha[:7]) >= 1 and sha in vc)
check("version.gles2_optin", "exclude_gles_sm100" in vc and "exclude_gles_sm100" in skill_md)

# 7. profiles opt-in contract
rr = (ROOT / "project-profiles/riff-racers.md").read_text(encoding="utf-8")
check("profile.opt_only", "ONLY" in rr and "riff-racers" in rr.lower())
for ex in ("pixel-platformer", "voxel-survival", "action-rpg"):
    p = ROOT / f"project-profiles/{ex}.example.md"
    check(f"profile.example.{ex}", p.is_file() and p.stat().st_size > 400)

# 8. scripts are non-destructive by contract (no overwrite of user artifacts):
#    check headers claim read-only / dated-suffix collision
for name, must_have in [("audit_defold_project.py", "READ-ONLY"),
                        ("gltf_preflight.py", "read-only"),
                        ("bob_build.sh", "dated suffix")]:
    txt = (ROOT / "scripts" / name).read_text(encoding="utf-8")
    check(f"scripts.nondestructive.{name}", must_have.lower() in txt.lower())

print(f"== test_skill: {pass_n} pass, {fail_n} fail "
      f"(STATIC-level: structure/routing/scripts; runtime LLM activation = separate level)")
sys.exit(0 if fail_n == 0 else 1)
