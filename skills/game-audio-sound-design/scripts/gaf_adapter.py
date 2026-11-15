#!/usr/bin/env python3
"""gaf_adapter.py — thin client for the game-audio-forge backend (gaf CLI).

The backend stays the single generation platform; this module never
re-implements generation. It resolves the install (CLI arg > $GAME_AUDIO_FORGE_ROOT
> ~/dev/github/game-audio-forge), shells out to scripts/gaf, and harvests the
produced WAV + .meta.json sidecar into the caller's output directory.

Verified backend contract (scripts/gaf, 2026-11-13 install):
  gaf music "PROMPT" [--bpm N --duration 10-600 --seed N --steps N
                      --cover SRC [--cover-strength F] [--noise-strength F]
                      --repaint SRC --from S --to S --ref AUDIO]
  gaf sfx   "PROMPT" [--backend sa3|dasheng --duration N --steps N --cfg F --seed N]
  gaf status | ui | help
  - output: <root>/output/{music,sfx}/<timestamp>_<slug>.wav + .meta.json
  - never overwrites (collision → -2, -3 …); queues GPU work internally
  - music: ACE-Step 1.5 (SFT DiT) 48 kHz stereo; --bpm is NOT executed by
    the DiT (tempo comes from the words; measured, see docs/PROMPTING.md)
  - sfx sa3 (default): Stable Audio 3 small-sfx 44.1 kHz stereo;
    dasheng: 16 kHz mono, runtime UNLICENSED → never commercial
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import audio_common as ac

MUSIC_TIMEOUT = 1800  # generations are GPU-queued; long tracks + queue waits
SFX_TIMEOUT = 600


class GafError(RuntimeError):
    pass


def _root(cli_root: str | None = None) -> Path:
    root, reason = ac.resolve_gaf_root(cli_root)
    if root is None:
        raise GafError(
            f"{reason}\n"
            f"Install: git clone {ac.GAF_GITHUB_URL} ~/dev/github/game-audio-forge\n"
            f"then follow its docs/SETUP.md (bash scripts/setup.sh). The skill "
            f"will NOT install the backend for you."
        )
    return root


def _latest_output(outdir: Path, since_files: set[str]) -> Path | None:
    """Newest wav in outdir not present before the run (gaf never overwrites)."""
    new = [p for p in outdir.glob("*.wav") if p.name not in since_files]
    if not new:
        return None
    return max(new, key=lambda p: p.stat().st_mtime)


def _sidecar(wav: Path) -> dict:
    meta = wav.with_name(wav.stem + ".meta.json")
    if not meta.is_file():
        for alt in (wav.with_suffix(".meta.json"),):
            meta = alt if alt.is_file() else meta
    try:
        return json.loads(meta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _harvest(wav: Path, dest_dir: Path) -> dict:
    """Copy backend output + sidecar into dest_dir; return record."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    wav_out = ac.unique_path(dest_dir / wav.name)
    shutil.copy2(wav, wav_out)
    meta = _sidecar(wav)
    side = wav_out.with_name(wav_out.stem + ".meta.json")
    side.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return {"audio": str(wav_out), "sidecar": str(side),
            "backend_meta": meta, "backend_file": str(wav)}


def _run(root: Path, args: list[str], outdir: Path, dest_dir: Path | None,
         timeout: int, label: str) -> dict:
    cli = ac.gaf_cli(root)
    before = {p.name for p in outdir.glob("*.wav")} if outdir.is_dir() else set()
    cmd = [str(cli), *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                          cwd=str(root))
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        raise GafError(f"gaf {label} failed (rc={proc.returncode}):\n{out[-1500:]}")
    produced = _latest_output(outdir, before)
    if produced is None:
        m = re.search(r"done: (.+\.wav)", out)
        cand = Path(m.group(1)) if m and Path(m.group(1)).is_file() else None
        produced = cand
    if produced is None:
        raise GafError(f"gaf {label} reported no output file:\n{out[-800:]}")
    if dest_dir is None:
        return {"audio": str(produced), "sidecar": str(
            produced.with_name(produced.stem + ".meta.json")),
            "backend_meta": _sidecar(produced), "backend_file": str(produced)}
    return _harvest(produced, Path(dest_dir))


def generate_music(prompt: str, *, root: str | None = None,
                   duration: int | None = None, seed: int | None = None,
                   steps: int | None = None, bpm: int | None = None,
                   cover: str | None = None, cover_strength: float | None = None,
                   repaint: str | None = None, frm: float | None = None,
                   to: float | None = None, ref: str | None = None,
                   out_dir: str | Path | None = None) -> dict:
    """Instrumental music via ACE-Step 1.5 (backend-queued, CUDA).

    bpm is passed through but NOT enforced by the DiT (measured): treat
    measured BPM (audio_audit) as authoritative for sync work.
    """
    root = _root(root)
    args = ["music", prompt]
    if duration is not None:
        args += ["--duration", str(duration)]
    if seed is not None:
        args += ["--seed", str(seed)]
    if steps is not None:
        args += ["--steps", str(steps)]
    if bpm is not None:
        args += ["--bpm", str(bpm)]
    if cover:
        args += ["--cover", str(cover)]
    if cover_strength is not None:
        args += ["--cover-strength", str(cover_strength)]
    if repaint:
        args += ["--repaint", str(repaint)]
    if frm is not None:
        args += ["--from", str(frm)]
    if to is not None:
        args += ["--to", str(to)]
    if ref:
        args += ["--ref", str(ref)]
    return _run(root, args, root / "output" / "music", out_dir,
                MUSIC_TIMEOUT, "music")


def generate_sfx(prompt: str, *, root: str | None = None,
                 duration: float | None = None, seed: int | None = None,
                 steps: int | None = None, cfg: float | None = None,
                 backend: str | None = None,
                 out_dir: str | Path | None = None) -> dict:
    """One SFX via sa3.cpp (Stable Audio 3, default) or dasheng (legacy,
    internal-use-only — runtime unlicensed)."""
    root = _root(root)
    args = ["sfx", prompt]
    if backend:
        args += ["--backend", backend]
    if duration is not None:
        args += ["--duration", str(duration)]
    if steps is not None:
        args += ["--steps", str(steps)]
    if cfg is not None:
        args += ["--cfg", str(cfg)]
    if seed is not None:
        args += ["--seed", str(seed)]
    return _run(root, args, root / "output" / "sfx", out_dir,
                SFX_TIMEOUT, "sfx")


def status(*, root: str | None = None) -> dict:
    """Backend self-report (GPU, binaries, models, ffmpeg) as text."""
    root = _root(root)
    proc = subprocess.run([str(ac.gaf_cli(root)), "status"],
                          capture_output=True, text=True, timeout=120)
    return {"root": str(root), "rc": proc.returncode,
            "report": (proc.stdout or "") + (proc.stderr or "")}


if __name__ == "__main__":
    import argparse
    import sys
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--forge-root")
    ap.add_argument("mode", choices=["status"])
    ns = ap.parse_args(sys.argv[1:])
    try:
        print(json.dumps(status(root=ns.forge_root), indent=2))
    except GafError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
