#!/usr/bin/env python3
"""test_skill.py — skill validation entry (repo convention: python3 runner).
Delegates to the real tool suite; prints parseable VERDICT. Headless-safe:
SR verdict is environment-declared, never faked."""
import subprocess, sys
from pathlib import Path

here = Path(__file__).resolve().parent
suite = here.parent / "tooling" / "a11y-audit" / "tests" / "run.mjs"

def main() -> int:
    r = subprocess.run(["node", str(suite)], capture_output=True, text=True, timeout=600)
    sys.stdout.write(r.stdout)
    if r.returncode not in (0, 1):
        sys.stdout.write(r.stderr[-2000:])
        print("VERDICT FAIL suite-crash")
        return 1
    print("SR layer: environment-declared (out/sr-verdict.txt); DOM/AT checks separate.")
    return 0 if "VERDICT PASS" in r.stdout else 1

if __name__ == "__main__":
    sys.exit(main())
