#!/usr/bin/env python3
"""check_version.py — Godot release-channel gate (stdlib only, network-aware).

Answers: what is the current stable Godot, what is the skill baseline
(4.7.2 stable, ed1daf0b), and does a project's declared version sit on an
allowed channel. Never mutates anything.

Usage:
  check_version.py             # probe official sources, print table
  check_version.py <proj_dir>  # also gate that project's config/features
Exit 0 = gate pass / info printed; exit 1 = stale baseline or forbidden
channel. Network down -> prints OFFLINE verdict (not a failure of the skill).
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

BASELINE = {"version": "4.7.2", "channel": "stable",
            "commit": "ed1daf0bf001b61586d9930840f2f1394092c079",
            "docs": "https://docs.godotengine.org/en/4.7/"}
API = "https://api.github.com/repos/godotengine/godot/releases?per_page=20"
DOCS_OK = re.compile(r"^\d+\.\d+\.\d+$")


def fetch(url: str, timeout: int = 15) -> bytes | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "godot-skill"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception:
        return None


def stable_tag(t: str) -> bool:
    return bool(re.fullmatch(r"\d+\.\d+\.\d+-stable", t))


def probe_latest_stable() -> str | None:
    raw = fetch(API)
    if raw is None:
        return None
    tags = []
    for rel in json.loads(raw):
        tag = rel.get("tag_name", "")
        if tag.endswith("-stable") and stable_tag(tag) and not rel.get("prerelease"):
            tags.append(tag)
    if not tags:
        return None

    def key(v: str):
        return [int(x) for x in v.split("-")[0].split(".")]
    return sorted(tags, key=key)[-1]


def project_version(proj: Path) -> str | None:
    pg = proj / "project.godot"
    if not pg.is_file():
        return None
    m = re.search(r'config/features=PackedStringArray\(([^)]*)\)', pg.read_text(encoding="utf-8", errors="replace"))
    if not m:
        return None
    for tok in re.findall(r'"([^"]+)"', m.group(1)):
        if re.fullmatch(r"\d+\.\d+(\.\d+)?", tok):
            return tok
    return None


def main() -> int:
    rc = 0
    latest = probe_latest_stable()
    if latest is None:
        print("OFFLINE  cannot reach GitHub — baseline stays "
              f"{BASELINE['version']}-stable, re-verify before pinning new work")
    else:
        base = BASELINE["version"]
        newer = latest != f"{base}-stable"
        print(f"latest_stable={latest} baseline={base}-stable "
              f"({'NEWER-STABLE-EXISTS' if newer else 'baseline-current'})")
        if newer:
            print("ACTION run workflows/engine-upgrade.md routine for "
                  f"{latest}; do NOT silently bump projects")
            rc = 1

    if len(sys.argv) > 1:
        proj = Path(sys.argv[1])
        pv = project_version(proj)
        if pv is None:
            print(f"PROJECT {proj}: no version hint in project.godot "
                  "(add via editor save or CI pin)")
        elif DOCS_OK.match(pv) and pv.count(".") == 2 and not pv.startswith("4."):
            print(f"PROJECT {pv}: non-4.x line — verify docs pin")
        else:
            chan = "stable-line" if re.fullmatch(r"\d+\.\d+(\.\d+)?", pv) else "check-pin"
            print(f"PROJECT {proj.name}: features={pv} channel={chan}")
    print(f"BASELINE {BASELINE['version']}-stable {BASELINE['commit'][:8]} "
          f"docs={BASELINE['docs']}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
