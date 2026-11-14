#!/usr/bin/env python3
"""tool_probe.py — presence/version/license probe for pipeline tools.

Reports what THIS machine has; missing tools are lanes degrading to
analysis-only (tooling.md), never a dead pipeline. Read-only.
Usage: python3 scripts/tool_probe.py [name ...]   (default: all)
Exit always 0 unless a named tool filter matches nothing.
"""
import shutil
import subprocess
import sys

TOOLS = {
    "blender": (["blender", "--version"], "GPL-2.0", "export/bake/preflight (run in-engine)"),
    "godot": (["godot", "--version"], "MIT", "HEADLESS import + render gate"),
    "gltf-transform": (["gltf-transform", "--version"], "MIT", "glTF edit/compress/inspect"),
    "gltfpack": (["gltfpack", "-h"], "MIT", "mesh compress (draco/meshopt)"),
    "toktx": (["toktx", "--version"], "Apache-2.0", "KTX2/Basis/ASTC encode"),
    "ktx": (["ktx", "--version"], "Apache-2.0", "KTX inspect/transcode"),
    "ktxinfo": (["ktxinfo", "--help"], "Apache-2.0", "KTX2 header read"),
    "glslangValidator": (["glslangValidator", "--version"], "Apache-2.0",
                         "GLSL/SPIR-V precheck (pre-filter, not engine truth)"),
    "magick": (["magick", "--version"], "Apache-2.0", "format conversion batch"),
    "python3": ([sys.executable or "python3", "--version"], "-", "scripts host"),
}
PYLIBS = {"PIL": "Pillow (metrics/pixel ops)", "yaml": "PyYAML (config)"}


def probe(cmd):
    exe = shutil.which(cmd[0])
    if not exe:
        return None, ""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        out = (r.stdout or r.stderr).strip().splitlines()
        return exe, out[0][:80] if out else ""
    except Exception as e:
        return exe, f"error: {e}"


def main(argv):
    want = argv or list(TOOLS)
    rows = []
    for name in want:
        if name in TOOLS:
            cmd, lic, role = TOOLS[name]
            path, ver = probe(cmd)
            rows.append((name, "present" if path else "MISSING", ver, lic, role))
        else:
            print(f"unknown tool filter: {name} (have: {', '.join(TOOLS)})",
                  file=sys.stderr)
            return 2
    for lib, role in PYLIBS.items():
        try:
            __import__(lib)
            rows.append((lib, "present", "import-ok", "-", role))
        except ImportError:
            rows.append((lib, "MISSING", "", "-", f"fallback: {role} degraded"))
    print("| tool | state | version | license | lane |")
    print("|---|---|---|---|---|")
    for t, s, v, l, r in rows:
        print(f"| {t} | {s} | {v} | {l} | {r} |")
    missing = [r[0] for r in rows if r[1] == "MISSING"]
    if missing:
        print("degraded lanes (analysis-only fallbacks, skill stays functional): "
              + ", ".join(missing))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
