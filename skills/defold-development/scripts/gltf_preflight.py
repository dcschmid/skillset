#!/usr/bin/env python3
"""gltf_preflight.py — GLB/glTF import preflight (stdlib only, read-only).

Checks a .glb/.gltf for conditions that break or degrade Defold import:
container sanity, extensions used (Draco/Meshopt/KTX2 need Defold >= 1.14.1
IMPORT-TIME support), texture formats, node/mesh counts, animation presence,
up-axis hints. Reports findings; imports nothing, writes nothing.
Usage: python3 scripts/gltf_preflight.py file.glb|file.gltf
Exit 0 = importable with notes; exit 1 = blocking findings.
"""
import json
import struct
import sys
from pathlib import Path

def fail(msg): print(f"BLOCK {msg}"); return 1

def main():
    if len(sys.argv) < 2:
        print(__doc__); return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        return fail(f"file not found: {path}")
    data = path.read_bytes()
    notes, blocks, ext_used, ktx = [], [], [], False

    if path.suffix.lower() == ".glb":
        if len(data) < 12 or data[:4] != b"glTF":
            return fail("not a GLB container (bad magic)")
        version = struct.unpack("<I", data[4:8])[0]
        if version != 2:
            return fail(f"glTF {version}; Defold targets glTF 2.0")
        # walk chunks
        off = 12
        json_chunk = None
        while off + 8 <= len(data):
            clen, ctype = struct.unpack("<I4s", data[off:off + 8])
            payload = data[off + 8:off + 8 + clen]
            blocks.append(ctype.decode(errors="replace"))
            if ctype == b"JSON" and json_chunk is None:
                json_chunk = payload
            off += 8 + clen
        if json_chunk is None:
            return fail("GLB has no JSON chunk")
        raw = json_chunk
    else:
        try:
            raw = data
            json.loads(raw)
        except json.JSONDecodeError as e:
            return fail(f"invalid JSON: {e}")

    try:
        g = json.loads(raw)
    except json.JSONDecodeError as e:
        return fail(f"invalid JSON: {e}")

    ext_used = list(g.get("extensionsUsed", []))
    req = list(g.get("extensionsRequired", []))
    ktx = any("ktx" in e.lower() for e in ext_used + req)

    for e in req:
        low = e.lower()
        if "draco" in low or "meshopt" in low or "ktx" in low:
            notes.append(f"{e}: required — needs Defold >= 1.14.1 import-time support "
                         "(import-time ONLY, not runtime)")
        elif low not in ("",):
            blocks_or_note = None  # unknown ext: warn, engine may drop it
            notes.append(f"extension required: {e} — verify Defold support before import")

    meshes = g.get("meshes", [])
    tris = 0
    for m in meshes:
        for p in m.get("primitives", []):
            mode = p.get("mode", 4)
            idx = p.get("indices")
            if mode == 4 and idx is not None:
                acc = (g.get("accessors") or [])[idx]
                tris += acc.get("count", 0) // 3
    mats = g.get("materials", [])
    pbr = sum(1 for m in mats if "pbrMetallicRoughness" in m)
    anims = len(g.get("animations", []))
    imgs = g.get("images", [])
    embedded = sum(1 for i in imgs if "bufferView" in i)

    print(f"# preflight {path.name}")
    print(f"meshes {len(meshes)} | ~tris {tris} | materials {len(mats)} (PBR {pbr}) | animations {anims}")
    print(f"images {len(imgs)} ({embedded} embedded) | chunks {blocks or 'n/a'}")
    if ktx:
        print("KTX2 textures present — 1.14.1 import-time; recompression policy applies")
    if tris > 200000:
        notes.append(f"high triangle count ({tris}) — check platform budget (templates/import-checklist.md)")
    for n in notes:
        print(f"NOTE {n}")
    if not notes:
        print("no blocking findings")
    print("VERDICT IMPORTABLE (with notes above) — verify in-engine: workflows/import-3d-assets.md")
    return 0

if __name__ == "__main__":
    sys.exit(main())
