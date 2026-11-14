#!/usr/bin/env python3
"""pipeline_lib.py — shared stdlib-only helpers for asset-pipeline scripts.

Config loading (asset-pipeline.yaml), engine detection, finding model,
VRAM/size math. Optional deps (yaml, PIL) degrade with named fallbacks.
"""
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

SEVERITIES = ("Critical", "High", "Medium", "Low", "Informational")
ASSET_EXT = {
    ".png": "texture", ".jpg": "texture", ".jpeg": "texture", ".webp": "texture",
    ".tga": "texture", ".exr": "texture", ".hdr": "texture", ".dds": "texture",
    ".ktx2": "texture", ".bmp": "texture",
    ".glb": "model", ".gltf": "model", ".fbx": "model", ".dae": "model",
    ".obj": "model",
}
DATA_MAP_RE = re.compile(
    r"(?i)(normal|nrm|rough|metal|ao|occlusion|height|disp|mask|orm|opaque|alpha_mask)")

DEFAULTS = {
    "engine": None, "engine_version": None, "art_style": None,
    "targets": [], "profile": "midrange",
    "texture_max_size": {},           # per profile; empty = no cap enforced
    "compression": {},                # per-kind preference overrides
    "mesh_budgets": {}, "shader_requirements": {},
    "quality_thresholds": {"ssim_min": 0.95, "pixel_diff_max_pct": 2.0},
    "auto_fix": {"enabled": ["repoint-missing-texture", "dedupe-identical"],
                 "protect": ["*.orig", ".import"]},
    "exclude_dirs": ["*.orig", ".git", "build", "*.import"],
    "reporting": {"formats": ["json", "markdown"], "dir": "asset-reports"},
}


def load_config(root):
    """asset-pipeline.yaml next to project root or root itself; defaults merged."""
    cfg = json.loads(json.dumps(DEFAULTS))  # deep copy, stdlib-only
    path = Path(root) / "asset-pipeline.yaml"
    if not path.is_file():
        path = Path(root) / "asset-pipeline.yml"
    notes = []
    if path.is_file():
        raw = path.read_text(encoding="utf-8", errors="replace")
        try:
            import yaml  # optional
            data = yaml.safe_load(raw) or {}
        except Exception:
            data, warn = _mini_yaml(raw)
            if warn:
                notes.append(f"config: mini-parser: {warn}")
        _merge(cfg, data if isinstance(data, dict) else {})
        notes.append(f"config: loaded {path}")
    else:
        notes.append("config: no asset-pipeline.yaml — conservative defaults")
    return cfg, notes, path if path.is_file() else None


def _mini_yaml(text):
    """Indent-nested subset: scalars, lists of scalars, nested maps. warn=''."""
    root, stack, warn = {}, [(-1, None)], []

    def coerce(v):
        v = v.strip().strip('"\'')
        if v in ("true", "false"):
            return v == "true"
        try:
            return int(v)
        except ValueError:
            pass
        try:
            return float(v)
        except ValueError:
            return v
    lines = [l for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]
    stack = [(-1, root)]  # (indent_of_key_that_opened_it, container)
    for i, line in enumerate(lines):
        indent = len(line) - len(line.lstrip(" "))
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        ctx = stack[-1][1]
        body = line.strip()
        if body.startswith("- "):
            if isinstance(ctx, list):
                ctx.append(coerce(body[2:]))
            continue
        m = re.match(r"([\w.-]+):\s*(.*)$", body)
        if not m or isinstance(ctx, list):
            continue
        key, val = m.group(1), m.group(2)
        if val == "":
            nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
            child = [] if nxt.startswith("- ") else {}
            ctx[key] = child
            stack.append((indent, child))
        else:
            ctx[key] = coerce(val)
    return root, ";".join(warn)


def _merge(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _merge(dst[k], v)
        else:
            dst[k] = v


def detect_engine(root):
    """Probed engine markers only; version from files, never assumed."""
    root = Path(root)
    hits = []
    if (root / "game.project").is_file():
        ver = ""
        try:
            m = re.search(r"engine_version\s*=\s*(\S+)",
                          (root / "game.project").read_text(errors="replace"))
            ver = m.group(1) if m else ""
        except OSError:
            pass
        hits.append(("defold", ver or "unknown"))
    pg = root / "project.godot"
    if pg.is_file():
        ver, renderer = "unknown", ""
        try:
            t = pg.read_text(errors="replace")
            m = re.search(r'config/features=PackedStringArray\("([\d.]+)', t)
            ver = m.group(1) if m else "unknown"
            m = re.search(r'type="(forward_plus|mobile|gl_compatibility)"', t)
            renderer = m.group(1) if m else ""
        except OSError:
            pass
        hits.append(("godot", ver + (f"/{renderer}" if renderer else "")))
    for name, marker in (("unity", "ProjectSettings"), ("unreal", "Config/DefaultEngine.ini"),
                         ("bevy", "Cargo.toml")):
        pass  # adapters exist; detection needs explicit project probe, not guesses
    return hits[0] if len(hits) == 1 else (None, None) if not hits else ("multi", "; ".join(
        f"{e}:{v}" for e, v in hits))


def find_assets(root, cfg, limit=5000):
    root = Path(root)
    out = []
    excl = cfg.get("exclude_dirs", [])
    for p in root.rglob("*"):
        if len(out) >= limit:
            break
        if not p.is_file() or p.suffix.lower() not in ASSET_EXT:
            continue
        rel = p.relative_to(root)
        if any(part in (".git", "build", "__pycache__") or part.endswith(".orig")
               for part in rel.parts):
            continue
        if any(g.strip("/") in str(rel) for g in excl if isinstance(g, str)):
            continue
        out.append((ASSET_EXT[p.suffix.lower()], p))
    return out


class Report:
    def __init__(self, subject):
        self.subject, self.findings, self.notes = subject, [], []

    def add(self, file, category, severity, description, cause="", fix="",
            impact="", validation="STATIC"):
        assert severity in SEVERITIES, severity
        self.findings.append({"file": str(file), "category": category,
                              "severity": severity, "description": description,
                              "cause": cause, "fix": fix, "impact": impact,
                              "validation": validation})

    def note(self, msg):
        self.notes.append(msg)

    def counts(self):
        c = {s: 0 for s in SEVERITIES}
        for f in self.findings:
            c[f["severity"]] += 1
        return c

    def to_json(self):
        return {"subject": str(self.subject), "counts": self.counts(),
                "notes": self.notes, "findings": self.findings}

    def to_markdown(self):
        c = self.counts()
        lines = [f"## Asset report — {self.subject}",
                 "", "| severity | count |", "|---|---|"]
        lines += [f"| {s} | {c[s]} |" for s in SEVERITIES]
        for f in self.findings:
            lines += ["", f"### [{f['severity']}] {f['category']} — `{f['file']}`",
                      f"- description: {f['description']}",
                      *( [f"- cause: {f['cause']}"] if f["cause"] else [] ),
                      f"- fix: {f['fix']}" if f["fix"] else "- fix: (none proposed)",
                      f"- impact: {f['impact']}" if f["impact"] else "",
                      f"- validation: `{f['validation']}`"]
        for n in self.notes:
            lines.append(f"- note: {n}")
        return "\n".join(l for l in lines if l != "")

    def emit(self, out_dir, stem):
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{stem}.json").write_text(json.dumps(self.to_json(), indent=1),
                                              encoding="utf-8")
        (out_dir / f"{stem}.md").write_text(self.to_markdown() + "\n", encoding="utf-8")
        return out_dir / f"{stem}.json", out_dir / f"{stem}.md"


def vram_est_bytes(w, h, bpp_bits=32, mips=True):
    """Estimated texture VRAM (block/raw); labeled estimated by callers."""
    base = max(1, w) * max(1, h) * max(1, bpp_bits) // 8
    return int(base * (4 / 3)) if mips else base


def file_vram_est(path, cfg):
    """Disk size + best-effort dimensions without heavy deps."""
    size = path.stat().st_size
    w = h = 0
    try:
        b = path.read_bytes()
        suf = path.suffix.lower()
        if suf == ".png" and b[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = struct.unpack(">II", b[16:24])
        elif suf in (".jpg", ".jpeg") and b[:2] == b"\xff\xd8":
            i = 2
            while i < len(b) - 9:
                if b[i] != 0xFF:
                    break
                marker = b[i + 1]
                if marker in (0xC0, 0xC1, 0xC2, 0xC3):
                    h, w = struct.unpack(">HH", b[i + 5:i + 9])
                    break
                seg = struct.unpack(">H", b[i + 2:i + 4])[0]
                i += 2 + seg
        elif suf == ".webp" and b[:4] == b"RIFF":
            w = h = -1  # dims need chunk walk; Pillow path preferred
    except OSError:
        pass
    return size, w, h


def sha1_head(path, n=65536):
    h = hashlib.sha1()
    try:
        with open(path, "rb") as f:
            h.update(f.read(n))
    except OSError:
        return ""
    return h.hexdigest()


def walk_gltf(obj, key):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                yield v
            yield from walk_gltf(v, key)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_gltf(v, key)


def read_gltf(path):
    """Return (json_dict, error). GLB and .gltf with external bin tolerated."""
    path = Path(path)
    data = path.read_bytes()
    if data[:4] == b"glTF":
        if len(data) < 12:
            return None, "truncated GLB header"
        ver = struct.unpack("<I", data[4:8])[0]
        if ver != 2:
            return None, f"glTF version {ver} (expect 2)"
        off, json_len, chunks = 12, 0, []
        while off + 8 <= len(data):
            clen, ctype = struct.unpack("<II", data[off:off + 8])
            body = data[off + 8:off + 8 + clen]
            if ctype == 0x4E4F534A:
                json_len = clen
                try:
                    doc = json.loads(body.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as e:
                    return None, f"GLB JSON chunk: {e}"
            else:
                chunks.append(ctype)
            off += 8 + clen + (4 - clen % 4) % 4
        if not json_len:
            return None, "no JSON chunk in GLB"
        doc["_glb_bin_chunks"] = len(chunks)
        doc["_glb_embedded"] = True
        return doc, None
    if data[:1] in (b"{", b" [") or data[:1] == b"\xef":
        try:
            return json.loads(data.decode("utf-8")), None
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            return None, f"gltf JSON: {e}"
    return None, "not glTF/GLB"


def is_pixel_art(cfg):
    return (cfg.get("art_style") or "").lower() in ("pixel-art", "pixelart", "voxel")


def die(msg, code=1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def usage(doc):
    print(doc.strip())
    sys.exit(2)
