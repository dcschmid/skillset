#!/usr/bin/env python3
"""audio_common.py — shared plumbing for the game-audio-sound-design skill.

Host baseline (verified on this machine): Python 3.14.8 (audioop REMOVED —
stdlib-only, no audioop), ffmpeg/ffprobe on PATH, game-audio-forge at
~/dev/github/game-audio-forge. All analysis goes through ffmpeg/ffprobe
subprocess calls; no third-party Python packages.

Audio level metering parses ffmpeg `astats` output (dBFS). No LUFS/EBU R128
meter is available offline (loudnorm is single-pass); see references for the
playback-time measurement route.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

DEFAULT_GAF_ROOT = Path.home() / "dev/github/game-audio-forge"
ENV_GAF_ROOT = "GAME_AUDIO_FORGE_ROOT"
GAF_GITHUB_URL = "https://github.com/dcschmid/game-audio-forge"

DOC_LANG = ("approved", "review_required", "restricted", "unknown")
VALIDATION_STATUS = ("PASS", "WARNING", "FAIL", "NOT_TESTED")


class AudioToolError(RuntimeError):
    """A required external tool is missing or failed."""


# ---------------------------------------------------------------------------
# resolution / discovery
# ---------------------------------------------------------------------------

def resolve_gaf_root(cli_root: str | None = None) -> tuple[Path | None, str]:
    """Locate game-audio-forge. Priority: CLI arg > env > default.

    Returns (path_or_None, reason_string). Never creates anything.
    """
    candidates: list[tuple[str, Path]] = []
    if cli_root:
        candidates.append(("--forge-root", Path(cli_root).expanduser()))
    env = os.environ.get(ENV_GAF_ROOT, "").strip()
    if env:
        candidates.append((f"${ENV_GAF_ROOT}", Path(env).expanduser()))
    candidates.append(("default", DEFAULT_GAF_ROOT))
    for source, root in candidates:
        if (root / "scripts" / "gaf").is_file():
            return root, source
    tried = ", ".join(str(r) for _, r in candidates)
    return None, f"game-audio-forge not found (tried: {tried})"


def gaf_cli(root: Path) -> Path:
    return root / "scripts" / "gaf"


def gaf_config(root: Path) -> dict:
    """Read config/gaf.json; {} when absent or broken (doctor reports it)."""
    cfg = root / "config" / "gaf.json"
    try:
        return json.loads(cfg.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def tool(name: str) -> str | None:
    """Absolute path of an external tool on PATH, or None."""
    return shutil.which(name)


def require(name: str) -> str:
    p = tool(name)
    if p is None:
        raise AudioToolError(
            f"{name} not on PATH. Install it (e.g. `sudo dnf install ffmpeg-full`) "
            f"or point the skill at an install that has it."
        )
    return p


def run(cmd: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
    """Run a command; never raises on non-zero exit (caller inspects rc)."""
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


# ---------------------------------------------------------------------------
# audio facts (ffprobe / ffmpeg)
# ---------------------------------------------------------------------------

def probe(path: str | Path) -> dict:
    """Container facts via ffprobe: {duration, rate, channels, codec, ok}.

    ok=False with an `error` key when the file is unreadable/corrupt.
    """
    path = str(path)
    p = run([require("ffprobe"), "-v", "error",
             "-show_entries", "stream=sample_rate,channels,codec_name",
             "-show_entries", "format=duration", "-of", "json", path], timeout=60)
    if p.returncode != 0:
        return {"ok": False, "error": (p.stderr or "ffprobe failed").strip()[:400]}
    try:
        data = json.loads(p.stdout or "{}")
    except json.JSONDecodeError:
        return {"ok": False, "error": "unparseable ffprobe output"}
    fmt = data.get("format", {})
    streams = data.get("streams") or []
    st = streams[0] if streams else {}
    try:
        duration = round(float(fmt.get("duration", 0.0)), 4)
    except (TypeError, ValueError):
        duration = None
    return {
        "ok": True,
        "duration": duration,
        "rate": st.get("sample_rate"),
        "channels": st.get("channels"),
        "codec": st.get("codec_name"),
    }


# ffmpeg astats emits per-channel ("Peak level dB: -0.53") and overall
# ("Overall:\n  Peak level dB: ...") lines; the overall value follows its
# "Overall:" header, so track a pending-scope flag per stats key.
_STATS = {
    "Peak level dB": "peak_dbfs",
    "RMS level dB": "rms_dbfs",
    "Flat factor": "flat_factor",
    "DC offset": "dc_offset",
    "Number of samples": "num_samples",
}
# astats measure tokens (verified ffmpeg on this host): Peak_level, RMS_level,
# Flat_factor, DC_offset, Number_of_samples


def measure(path: str | Path, timeout: int = 300) -> dict:
    """Level statistics via ffmpeg astats (overall scope, dBFS / raw).

    {peak_dbfs, rms_dbfs, flat_factor, dc_offset, num_samples, ok, error?}
    (overall scope; dc_offset in raw sample units)
    """
    p = run([require("ffmpeg"), "-hide_banner", "-nostats", "-i", str(path),
             "-af", "astats=measure_overall=Peak_level+RMS_level+Flat_factor+DC_offset+Number_of_samples",
             "-f", "null", "-"], timeout=timeout)
    text = p.stderr or ""
    if p.returncode != 0:
        return {"ok": False, "error": text.strip()[-400:] or "ffmpeg astats failed"}
    values: dict = {"ok": True}
    overall = {"dc_offset": None, "peak_dbfs": None, "rms_dbfs": None,
               "flat_factor": None, "num_samples": None}
    scope_overall = False
    # ffmpeg prefixes every astats line with "[Parsed_astats_0 @ 0x…] " (the
    # hex address varies) and prints the overall header as "Overall" without
    # a colon; strip the prefix, then match on the trailing "key: value".
    for line in text.splitlines():
        s = line.rstrip()
        if "] " in s:
            s = s.split("] ", 1)[1]
        s = s.strip()
        if s == "Overall":
            scope_overall = True
            continue
        if ":" not in s:
            continue
        key, _, raw = s.rpartition(":")
        key, raw = key.strip(), raw.strip()
        if scope_overall and key in _STATS:
            field = _STATS[key]
            try:
                overall[field] = float(raw)
            except ValueError:
                continue
    if overall["peak_dbfs"] is None and overall["dc_offset"] is None:
        return {"ok": False, "error": "astats produced no parseable stats"}
    values.update({
        "peak_dbfs": overall["peak_dbfs"],
        "rms_dbfs": overall["rms_dbfs"],
        "flat_factor": overall["flat_factor"],
        "num_samples": overall["num_samples"],
        "dc_offset": overall["dc_offset"],
    })
    return values


# ---------------------------------------------------------------------------
# safe output policy (non-destructive by skill contract)
# ---------------------------------------------------------------------------

def unique_path(path: str | Path) -> Path:
    """Collision-safe path: foo.wav → foo-2.wav → foo-3.wav … (never overwrite)."""
    path = Path(path)
    if not path.exists():
        return path
    n = 2
    while True:
        cand = path.with_name(f"{path.stem}-{n}{path.suffix}")
        if not cand.exists():
            return cand
        n += 1


def write_json(path: str | Path, payload, force: bool = False) -> Path:
    """Write JSON without silent overwrite (dated/numbered suffix on collision
    unless force=True). Atomic via tmp+rename."""
    path = Path(path)
    if not force:
        path = unique_path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    tmp.replace(path)
    return path


def audio_files(root: str | Path, exts=(".wav", ".ogg", ".mp3", ".flac", ".opus")):
    """Yield audio files under root, skipping hidden dirs; deterministic order."""
    root = Path(root)
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in exts and not any(
                part.startswith(".") for part in path.relative_to(root).parts):
            yield path


def verdict_line(tests: dict) -> str:
    """Deterministic verdict from {name: PASS|WARNING|FAIL|NOT_TESTED}.
    Unrun (NOT_TESTED) never reports as PASS."""
    if any(v == "FAIL" for v in tests.values()):
        return "FAIL"
    if any(v == "WARNING" for v in tests.values()):
        return "WARNING"
    if all(v == "PASS" for v in tests.values()):
        return "PASS"
    return "REVIEW_REQUIRED"
