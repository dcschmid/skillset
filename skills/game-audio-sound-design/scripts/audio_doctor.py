#!/usr/bin/env python3
"""audio_doctor.py — installation & readiness diagnosis for game audio work.

Checks (never installs, never downloads, never mutates the backend):
  1. game-audio-forge install present + config parseable
  2. gaf CLI executable; generator binaries + model dirs (via gaf status)
  3. ffmpeg / ffprobe on PATH
  4. Python host (3.14: no audioop — analysis is ffmpeg-based by design)
  5. output dir writable where the skill would write
  6. engine detection (defold game.project / godot project.godot) in cwd

Report: per-check {status, problem, impact, fix, probe}. Verdict:
READY | PARTIALLY_READY | NOT_READY. JSON out with --json, human otherwise.
Exit 0 = READY or PARTIALLY_READY, 1 = NOT_READY.

Usage: audio_doctor.py [--project DIR] [--forge-root PATH] [--json]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import audio_common as ac

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gaf_adapter  # noqa: E402


def _checks(project: Path | None, forge_root_arg: str | None) -> list[dict]:
    checks: list[dict] = []

    def add(name, ok, problem="", impact="", fix="", probe=""):
        checks.append({"check": name,
                       "status": "OK" if ok else ("PARTIAL" if ok is None else "FAIL"),
                       "problem": problem, "impact": impact, "fix": fix,
                       "probe": probe})
        return ok

    # 1. game-audio-forge
    root, source = ac.resolve_gaf_root(forge_root_arg)
    if root is None:
        add("game-audio-forge", False, source,
            "Generation (music/SFX) unavailable; analysis/audit still work.",
            f"git clone {ac.GAF_GITHUB_URL} ~/dev/github/game-audio-forge && "
            "cd ~/dev/github/game-audio-forge && bash scripts/setup.sh",
            "ls ~/dev/github/game-audio-forge/scripts/gaf")
        root = None
    else:
        add("game-audio-forge", True, probe=f"{root} ({source})")
        cfg = ac.gaf_config(root)
        add("gaf-config", bool(cfg), "" if cfg else "config/gaf.json missing/invalid",
            "gaf runs fall back to defaults or die",
            "re-create config/gaf.json (see backend README)",
            f"jq . {root / 'config/gaf.json'}")
        add("gaf-cli", (ac.gaf_cli(root).is_file()),
            "" if (root / "scripts/gaf").is_file() else "scripts/gaf missing",
            "no CLI entry point", "git pull / re-run backend setup",
            f"{ac.gaf_cli(root)} status")
        if cfg:
            add("ffmpeg-policy", True,
                probe=f"ffmpeg.enabled={cfg.get('ffmpeg', {}).get('enabled')} "
                      f"rate={cfg.get('ffmpeg', {}).get('target_rate')}")
            if str(cfg.get("sfx", {}).get("backend", "sa3")) == "dasheng":
                add("sfx-backend-licence", None,
                    "sfx.backend=dasheng — runtime unlicensed",
                    "dasheng output must not ship in commercial builds",
                    "keep default sa3 for commercial targets (backend docs/LICENSES.md)")
    # 2. backend live report (binaries/models/GPU) — only if install exists
    if root:
        try:
            st = gaf_adapter.status(root=str(root))
            rep = st.get("report", "")
            # dasheng is the legacy optional backend — its absence never
            # blocks readiness (default chain: ace-lm/ace-synth/sa3-generate)
            missing = [ln for ln in rep.splitlines()
                       if "MISSING" in ln and "dasheng" not in ln
                       and "Dasheng" not in ln]
            add("generators+models", st["rc"] == 0 and not missing,
                "; ".join(m.strip()[:90] for m in missing[:4]),
                "missing binaries/models block the matching generator",
                "backend: bash scripts/setup.sh (idempotent)",
                f"{ac.gaf_cli(root)} status")
        except Exception as e:  # status itself failed
            add("generators+models", False, str(e)[:200],
                "backend not answering", "run gaf status manually", "gaf status")
    # 3. host tools
    for t, why in (("ffmpeg", "all metering/transcode/fix operations"),
                   ("ffprobe", "audio fact extraction")):
        p = ac.tool(t)
        add(t, p is not None, "" if p else f"{t} not on PATH", why,
            "install ffmpeg ( Fedora: ffmpeg-full RPM)", f"which {t}")
    # 4. python host facts recorded by _python_host() below
    return checks


# audioop is gone in 3.14; record it as host truth, not a failure.
def _python_host(checks: list[dict]) -> None:
    import sys as _s
    checks.append({"check": "python-host", "status": "OK",
                   "problem": "", "impact": "",
                   "fix": "", "probe": f"{_s.version.split()[0]} audioop-removed"
                   if not _has_audioop() else f"{_s.version.split()[0]}"})


def _has_audioop() -> bool:
    try:
        import audioop  # noqa: F401
        return True
    except ModuleNotFoundError:
        return False


def _engines(project: Path, checks: list[dict]) -> None:
    engines = []
    if (project / "game.project").is_file():
        engines.append("defold")
    if (project / "project.godot").is_file():
        engines.append("godot")
    checks.append({"check": "engine-detection",
                   "status": "OK" if engines else "PARTIAL",
                   "problem": "" if engines else "no engine project in cwd",
                   "impact": "" if engines else "engine adapters inactive; "
                   "asset work still possible",
                   "fix": "", "probe": ",".join(engines) or str(project)})


def _writable(target: Path, checks: list[dict]) -> None:
    try:
        target.mkdir(parents=True, exist_ok=True)
        t = target / ".gaf-skill-probe"
        t.write_text("x", encoding="utf-8")
        t.unlink()
        checks.append({"check": "output-writable", "status": "OK",
                       "problem": "", "impact": "", "fix": "", "probe": str(target)})
    except OSError as e:
        checks.append({"check": "output-writable", "status": "FAIL",
                       "problem": str(e), "impact": "no files can be written",
                       "fix": "choose a writable output dir", "probe": str(target)})


def main(argv: list[str]) -> int:
    project = Path.cwd()
    forge = None
    as_json = "--json" in argv
    if "--project" in argv:
        project = Path(argv[argv.index("--project") + 1]).expanduser()
    if "--forge-root" in argv:
        forge = argv[argv.index("--forge-root") + 1]
    checks = _checks(project, forge)
    _python_host(checks)
    _engines(project, checks)
    _writable(project / "output", checks)

    fails = [c for c in checks if c["status"] == "FAIL"]
    critical = {c["check"] for c in fails if c["check"] in
                ("ffmpeg", "ffprobe", "output-writable")}
    verdict = "NOT_READY" if critical else ("PARTIALLY_READY" if fails else "READY")
    report = {"verdict": verdict, "checks": checks}
    if as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"audio-doctor: {verdict}")
        for c in checks:
            print(f"  [{c['status']:^7}] {c['check']:20} {c['probe']}")
            if c["problem"]:
                print(f"           problem: {c['problem']}")
                print(f"           impact : {c['impact']}")
                print(f"           fix    : {c['fix']}")
    return 0 if verdict != "NOT_READY" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
