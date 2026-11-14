#!/usr/bin/env python3
"""check_version.py — gate this skill's baseline against official Defold releases.

Fetches api.github.com/repos/defold/defold/releases (stdlib, no deps),
identifies the newest STABLE release, compares with the skill's pinned
baseline in references/version-compatibility.md. Non-destructive, read-only;
never changes any project. Exit 0 = baseline current; exit 1 = newer stable
exists or data unreadable → run the update routine in
references/version-compatibility.md.
Usage: python3 scripts/check_version.py [--offline]
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
RELEASES_API = "https://api.github.com/repos/defold/defold/releases?per_page=30"

def pinned_baseline():
    txt = (SKILL / "references/version-compatibility.md").read_text(encoding="utf-8")
    m = re.search(r"ENGINE_VERSION\s*=\s*([\d.]+)", txt)
    s = re.search(r"ENGINE_SHA\s*=\s*([0-9a-f]{7,40})", txt)
    return (m.group(1) if m else None, s.group(1) if s else None)

def newest_stable():
    req = urllib.request.Request(RELEASES_API, headers={"User-Agent": "defold-skill-check"})
    with urllib.request.urlopen(req, timeout=20) as r:
        rels = json.load(r)
    for rel in rels:
        if "stable" not in (rel.get("name") or "").lower():
            continue
        body = rel.get("body") or ""
        sha = re.search(r"sha1:\s*([0-9a-f]{7,40})", body)
        ver = re.match(r"v?([\d.]+)", rel.get("tag_name") or "")
        if ver and sha:
            return ver.group(1), sha.group(1)
    return None, None

def vtuple(v):
    return tuple(int(x) for x in v.split("."))

def main():
    offline = "--offline" in sys.argv
    pv, ps = pinned_baseline()
    if not pv:
        print("FAIL baseline version unreadable from version-compatibility.md")
        return 1
    print(f"pinned baseline: {pv} stable sha {ps[:7]}")
    if offline:
        print("== check_version: PASS (offline; baseline reported only)")
        return 0
    try:
        nv, ns = newest_stable()
    except Exception as e:  # network/doc drift -> explicit, non-destructive
        print(f"UNVERIFIED live check failed ({e}); baseline {pv} stands, verify manually")
        return 1
    if not nv:
        print("UNVERIFIED no stable release parsed from API")
        return 1
    print(f"newest official stable: {nv} sha {ns[:7]}")
    if vtuple(nv) == vtuple(pv) and ps.startswith(ns[:len(ps) if len(ps) < len(ns) else len(ns)][:8]):
        print("== check_version: PASS baseline is current stable")
        return 0
    if vtuple(nv) > vtuple(pv):
        print(f"NEWER STABLE EXISTS: {nv}. Run the update routine "
              "(references/version-compatibility.md). Projects are NOT auto-migrated.")
        return 1
    print("== check_version: baseline newer than parsed stable (channel ahead?) — verify manually")
    return 1

if __name__ == "__main__":
    sys.exit(main())
