#!/usr/bin/env python3
"""gltf_validate.py — glTF 2.0 / GLB structural validator (stdlib only).

Checks container, JSON parse, buffer/image/material/UV/normal/skin/animation
reference integrity against the declared counts. Extensions are REPORTED for
adapter gating (mesh-codecs = mesh-only; basisu = textures) — support proof
lives in the engine adapter, not here. Read-only.

Usage: python3 scripts/gltf_validate.py file.glb|file.gltf [--json out.json]
Exit 0 = valid (notes possible); 1 = blocking findings; 2 = usage/IO.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_lib import Report, read_gltf, walk_gltf, usage  # noqa: E402

MESH_EXTS = {"KHR_draco_mesh_compression", "EXT_meshopt_compression",
             "KHR_mesh_quantization", "EXT_mesh_gpu_instancing"}
TEX_EXTS = {"KHR_texture_basisu"}


def main(argv):
    if not argv:
        usage(__doc__)
    path = Path(argv[0])
    out_json = argv[argv.index("--json") + 1] if "--json" in argv else None
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1
    doc, err = read_gltf(path)
    rep = Report(path.name)
    if err:
        rep.add(path, "container", "Critical", err, validation="STATIC")
        _emit(rep, out_json)
        return 1
    rep.add(path, "container", "Informational",
            f"glTF 2.0 ({'GLB' if doc.get('_glb_embedded') else 'JSON'}) parses",
            validation="STATIC")

    ext = set(str(e) for e in (doc.get("extensionsUsed") or []))
    req = set(str(e) for e in (doc.get("extensionsRequired") or []))
    for e in sorted(ext | req):
        dom = "mesh-geometry" if e in MESH_EXTS else \
              "textures" if e in TEX_EXTS else "material/other"
        sev = "High" if e in req else "Medium"
        rep.add(path, "extension", sev, f"{e} {'required' if e in req else 'used'} — domain={dom}",
                fix=f"adapter-gate: verify engine+version decode support before shipping "
                    f"({'never conflate with ' + ('textures' if dom != 'textures' else 'mesh codecs')})",
                validation="STATIC") if (ext or req) else None

    defs = doc.get("buffers") or []
    for i, b in enumerate(defs):
        uri = b.get("uri")
        if uri and not uri.startswith("data:"):
            if not (path.parent / uri).is_file():
                rep.add(path, "buffer", "Critical", f"buffer[{i}] missing: {uri}",
                        fix="re-export with embedded buffers or copy bin alongside",
                        validation="STATIC")
    if any(c.get("bufferView", 0) >= len(doc.get("bufferViews") or [])
           for c in list(walk_gltf(doc, "accessors")) if isinstance(c, dict)):
        pass  # accessor->view bounds checked below
    nviews = len(doc.get("bufferViews") or [])
    for i, acc in enumerate(doc.get("accessors") or []):
        bv = acc.get("bufferView")
        if bv is not None and bv >= nviews:
            rep.add(path, "accessor", "Critical", f"accessor[{i}] -> bufferView {bv} >= {nviews}",
                    fix="corrupt export: re-export from source", validation="STATIC")
    nbuf = len(defs)
    for i, b in enumerate(doc.get("buffers") or []):
        if b.get("uri") is None and not doc.get("_glb_embedded") and nbuf:
            rep.add(path, "buffer", "Medium", f"buffer[{i}] no uri, no GLB chunk context",
                    validation="STATIC")

    nimg = len(doc.get("images") or [])
    for i, im in enumerate(doc.get("images") or []):
        uri = im.get("uri")
        if uri and not uri.startswith("data:") and not (path.parent / uri).is_file():
            rep.add(path, "image", "Critical", f"image[{i}] missing: {uri}",
                    fix="re-export textures embedded or co-located", validation="STATIC")
    ntx = len(doc.get("textures") or [])
    for m in doc.get("materials") or []:
        name = m.get("name", "?")
        slots = [("pbrMetallicRoughness.baseColorTexture",
                  (m.get("pbrMetallicRoughness") or {}).get("baseColorTexture")),
                 ("pbrMetallicRoughness.metallicRoughnessTexture",
                  (m.get("pbrMetallicRoughness") or {}).get("metallicRoughnessTexture")),
                 ("normalTexture", m.get("normalTexture")),
                 ("occlusionTexture", m.get("occlusionTexture")),
                 ("emissiveTexture", m.get("emissiveTexture"))]
        for slot, info in slots:
            if not isinstance(info, dict):
                continue
            ts = info.get("index")
            if isinstance(ts, int) and not (0 <= ts < ntx):
                rep.add(path, "material", "Critical",
                        f"material '{name}' {slot} -> texture {ts} >= {ntx}",
                        fix="re-point or re-export", validation="STATIC")
    nm = len(doc.get("meshes") or [])
    for i, node in enumerate(doc.get("nodes") or []):
        mesh = node.get("mesh")
        if mesh is not None and mesh >= nm:
            rep.add(path, "node", "Critical", f"node[{i}] mesh {mesh} >= {nm}",
                    validation="STATIC")
        for key, lim in (("cameras", len(doc.get("cameras") or [])),
                         ("skins", len(doc.get("skins") or []))):
            v = node.get(key)
            if v is not None and v >= lim:
                rep.add(path, "node", "High", f"node[{i}] {key} {v} >= {lim}",
                        validation="STATIC")
    mesh_gaps, unlit = [], []
    for i, m in enumerate(doc.get("meshes") or []):
        for pi, prim in enumerate(m.get("primitives") or []):
            attrs = prim.get("attributes") or {}
            mat = prim.get("material")
            if mat is not None and "NORMAL" not in attrs:
                mesh_gaps.append(f"mesh[{i}].prim[{pi}] no NORMAL (flat shading in engine)")
            if "TEXCOORD_0" not in attrs and mat is not None:
                rep.add(path, "geometry", "High",
                        f"mesh[{i}].prim[{pi}] material set, no TEXCOORD_0",
                        fix="UV unwrap or drop material", validation="STATIC")
    for g in mesh_gaps:
        rep.add(path, "geometry", "Medium", g, fix="recompute normals before export",
                validation="STATIC")
    for i, s in enumerate(doc.get("skins") or []):
        jn = s.get("joints") or []
        accs = doc.get("accessors") or []
        for j in jn:
            if j >= len(accs):
                rep.add(path, "skin", "Critical", f"skin[{i}] joint accessor {j} >= {len(accs)}",
                        validation="STATIC")
    for i, a in enumerate(doc.get("animations") or []):
        for ch in a.get("channels") or []:
            if (ch.get("target") or {}).get("node", 0) >= len(doc.get("nodes") or []):
                rep.add(path, "animation", "High",
                        f"animation[{i}] '{a.get('name','?')}' targets missing node",
                        fix="prune or re-export with animation", validation="STATIC")
    blocking = [f for f in rep.findings if f["severity"] in ("Critical",)]
    rep.note(f"extensions: {sorted(ext)} | meshes={nm} materials={len(doc.get('materials') or [])} "
             f"images={nimg} anims={len(doc.get('animations') or [])}")
    _emit(rep, out_json)
    md = rep.to_markdown()
    print(md)
    return 1 if blocking else 0


def _emit(rep, out_json):
    if out_json:
        Path(out_json).write_text(json.dumps(rep.to_json(), indent=1), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
