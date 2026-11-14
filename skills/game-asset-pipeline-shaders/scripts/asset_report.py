#!/usr/bin/env python3
"""asset_report.py — aggregate script outputs into JSON+Markdown reports.

Combines texture/model/material lanes into one before/after or point-in-time
report; estimates stay labeled `estimated`; NOT_RUN lanes stay NOT_RUN.
CI usage: exit 1 only on Critical (release-blocking) findings.
Usage: python3 scripts/asset_report.py PROJECT_DIR [--json OUT.json] [--md OUT.md]
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _run(script, *args):
    r = subprocess.run([sys.executable, str(HERE / script), *args],
                       capture_output=True, text=True)
    return r.returncode, r.stdout


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    root = Path(argv[0])
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2
    oj = argv[argv.index("--json") + 1] if "--json" in argv else None
    om = argv[argv.index("--md") + 1] if "--md" in argv else None
    lanes = {}
    for name, script in (("audit", "asset_audit.py"), ("textures", "texture_analyze.py"),
                         ("materials", "material_audit.py")):
        rc, out = _run(script, str(root))
        lanes[name] = {"exit": rc, "report_exit_1_blocking": rc == 1,
                       "summary": out.strip().splitlines()[:80]}
    crit = sum(1 for ln in lanes.values() if ln["report_exit_1_blocking"])
    doc = {"project": str(root), "lanes": lanes,
           "blocking_lanes": crit,
           "gate": "G1-asset-validity/G2/G6: " + ("FAIL" if crit else
                   "PASS-at-STATIC (HEADLESS/RENDER NOT_RUN — engine lanes not executed)"),
           "levels": {"STATIC": "run", "HEADLESS": "NOT_RUN (engine not invoked here)",
                      "RENDER": "NOT_RUN (no render target)",
                      "MEASURED": "NOT_RUN (no profiler)"}}
    js = json.dumps(doc, indent=1)
    if oj:
        Path(oj).write_text(js, encoding="utf-8")
    md = [f"# asset report — {root}", "",
          "```", js, "```"]
    if om:
        Path(om).write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    return 1 if crit else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
