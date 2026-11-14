#!/usr/bin/env python3
"""test_skill.py — design-authenticity validation (repo convention: python3
runner, parseable VERDICT). Covers: structure, config example, detection engine
scenarios A-J, browser-gating honesty. No browser required to PASS; where a
browser gates a check, the test asserts honest reporting, not a fake pass."""
import re, subprocess, sys
from pathlib import Path

skill = Path(__file__).resolve().parent.parent
repo = skill.parents[1]
failures: list[str] = []

def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"{'ok  ' if ok else 'FAIL'} {name}" + (f"  {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(name)

# --- structure -------------------------------------------------------------
check("SKILL.md exists", (skill / "SKILL.md").is_file())
fm = (skill / "SKILL.md").read_text(encoding="utf-8")
check("frontmatter name==dir", "name: design-authenticity" in fm.split("---")[1])
check("description mentions modes", all(m in fm for m in
      ("CREATE", "REVIEW", "REFACTOR", "GUARD", "AUDIT", "MODERNIZATION",
       "SLOP_CLEANUP", "REGRESSION")))
refs = ["design-principles", "anti-ai-patterns", "typography", "color-and-composition",
        "design-directions", "accessibility-integration", "visual-quality-gates",
        "framework-integration", "project-discovery", "safe-auto-fix",
        "visual-regression", "audit-report-format"]
check("references complete", all((skill / "references" / f"{r}.md").is_file() for r in refs))
wfs = ["create", "review", "refactor", "guard", "existing-project-audit", "audit-and-fix",
       "design-modernization", "anti-ai-slop-cleanup", "visual-regression-review"]
check("workflows complete", all((skill / "workflows" / f"{w}.md").is_file() for w in wfs))
check("examples complete", all((skill / "examples" / f).is_file() for f in
      ("design-config.example.yaml", "design-review.example.md",
       "existing-project-config.example.yaml", "existing-project-audit.example.md")))
# every references/... path mentioned in SKILL.md resolves
missing = [p for p in set(re.findall(r"(references/[\w-]+\.md|workflows/[\w-]+\.md"
            r"|examples/[\w.-]+\.yaml|examples/[\w.-]+\.md|scripts/[\w_.]+)", fm))
           if not (skill / p).is_file()]
check("SKILL.md links resolve", not missing, str(missing))
# no empty placeholders anywhere
check("no empty files", all(f.stat().st_size > 100 for f in skill.rglob("*.md")
      if "__pycache__" not in str(f)))

# --- config validator vs example --------------------------------------------
r = subprocess.run(["node", str(skill / "scripts/validate_config.mjs"),
                    str(skill / "examples/design-config.example.yaml")],
                   capture_output=True, text=True, timeout=60)
check("config example validates", "CONFIG PASS" in r.stdout, r.stdout + r.stderr)
bad = Path("/tmp/da_bad.yaml"); bad.write_text("strictness: ultra\nminimum_quality: 150\n")
r = subprocess.run(["node", str(skill / "scripts/validate_config.mjs"), str(bad)],
                   capture_output=True, text=True, timeout=60)
check("bad config rejected", "CONFIG FAIL" in r.stdout, r.stdout)

# --- detection engine: scenario fixtures (deterministic mirrors of rules) ----
# A/G engine (anti-ai-patterns.md): generic-color + filler-copy detectors.
def find_generic_color(css: str) -> bool:
    return bool(re.search(r"(from-(indigo|violet|blue)-\d+.*to-(indigo|violet|blue)-\d+"
                r"|\b#6366f1\b|linear-gradient\([^)]*(violet|indigo)[^)]*blue)", css))
def find_filler(text: str) -> bool:
    return bool(re.search(r"\b(Unleash|Empower|Seamless|Unlock the|elevate your)\b", text, re.I))

# Test A/G fixtures would catch generic SaaS landing (hero gradient + filler)
generic = ('class="bg-gradient-to-r from-indigo-500 to-blue-600"', "Unleash the future")
check("scenario generic-landing detected", find_generic_color(generic[0]) and find_filler(generic[1]))
# Test G false-positive guard: deliberate brand violet + real card copy = clean
deliberate = ("--accent: #6a2c91; /* brand orchid, brandbook p.3 */", "Ferry 14:20 departs Pier 4")
check("scenario deliberate-choices not flagged",
      not find_generic_color(deliberate[0]) and not find_filler(deliberate[1]))
# Test G: a legitimate card is not a defect — engine filter is documented, not regex:
engine = (skill / "references/anti-ai-patterns.md").read_text(encoding="utf-8")
check("no-false-positives rule documented", "well-built card is not a defect" in engine
      and "Classification filter" in engine)

# Test D (dashboard): engine prescribes findings w/ schema fields
check("finding schema complete", all(k in engine for k in
      ("severity", "component", "observation", "rationale", "fix")))
# Test I: framework delegation exists and names repo skills
fi = (skill / "references/framework-integration.md").read_text(encoding="utf-8")
sibling_ok = all((repo / "skills" / s).is_dir() for s in
                 ("astro", "react-nextjs", "accessibility", "godot", "defold-development"))
check("scenario framework-delegation", sibling_ok and all(s in fi for s in
      ("astro", "react-nextjs", "accessibility")), f"siblings={sibling_ok}")
# Test E (game UI): gaming direction guidance exists, anti-dashboard stated
dirs = (skill / "references/design-directions.md").read_text(encoding="utf-8")
check("scenario game-ui direction", "Gaming" in dirs and "dashboard" in dirs.lower())

# --- browser gating honesty (Test J) ------------------------------------------
# screenshot_audit.sh must either produce artifacts+manifest or report
# BROWSER_UNAVAILABLE exit 3 — never a silent success.
shot = skill / "scripts/screenshot_audit.sh"
page = Path("/tmp/da_page.html"); page.write_text("<!doctype html><title>da</title><h1>ok</h1>")
r = subprocess.run(["bash", str(shot), f"file://{page}", "/tmp/da_shots", "390x844"],
                   capture_output=True, text=True, timeout=180)
produced = any(Path("/tmp/da_shots").glob("390x844.*.png")) if Path("/tmp/da_shots").exists() else False
reported_unavailable = r.returncode == 3 and "BROWSER_UNAVAILABLE" in r.stdout
check("screenshot audit honest (artifact or BROWSER_UNAVAILABLE)",
      reported_unavailable or produced, f"rc={r.returncode} out={r.stdout[-200:]}")

# --- existing-project extension (AUDIT modes) --------------------------------
pd = " ".join((skill / "references/project-discovery.md").read_text(encoding="utf-8").split())
sa = " ".join((skill / "references/safe-auto-fix.md").read_text(encoding="utf-8").split())
vr = " ".join((skill / "references/visual-regression.md").read_text(encoding="utf-8").split())
ep_cfg = (skill / "examples/existing-project-config.example.yaml")
r = subprocess.run(["node", str(skill / "scripts/validate_config.mjs"), str(ep_cfg)],
                   capture_output=True, text=True, timeout=60)
check("existing-project config validates", "CONFIG PASS" in r.stdout, r.stdout + r.stderr)
# T4 preservation + T8 audit-no-changes + T5 uncommitted + T10 safe-fix
check("safe-auto-fix binds", all(k in sa for k in
      ("git status", "uncommitted", "becomes a refactor", "reversible")))
# T6 no-browser transparency + T7 regression classification
check("regression discipline", all(k in vr for k in
      ("dynamic", "technical", "NOT AVAILABLE", "parity", "fake PASS")))
# T1/T2/T3 discovery covers astro/react/next + responsive/consistency signals
check("discovery matrix covers stacks", all(k in pd.lower() for k in
      ("astro", "react", "next", "tokens", "routing", "ci")))
# selective audit (T9): scope vocabulary exists in SKILL.md + config
sk = (skill / "SKILL.md").read_text(encoding="utf-8")
check("selective scope vocabulary", "selective" in sk.lower() and "scope" in sk.lower()
      and "target:" in ep_cfg.read_text(encoding="utf-8"))
# score-before-after rule: real numbers only
check("before/after score honesty", "before/after" in sk.lower()
      and "never invented" in sk.lower())
# modes routed: every new mode names a workflow file from SKILL.md
check("modes routed", all(f"workflows/{w}.md" in sk for w in
      ("existing-project-audit", "audit-and-fix", "design-modernization",
       "anti-ai-slop-cleanup", "visual-regression-review")))

# Test H (small change -> no ceremony): GUARD spec caps itself
guard = (skill / "workflows/guard.md").read_text(encoding="utf-8")
check("guard stays proportional", "One pass per logical change" in guard and "no ceremony" in guard)
# Test F (a11y floor): integration doc binds AA floor + no-trade rule
a11y = (skill / "references/accessibility-integration.md").read_text(encoding="utf-8")
check("a11y floor binding", "AA" in a11y and "never a trade-off" in a11y.lower()
      and "contrast" in a11y and "focus" in a11y)

print(f"--- design-authenticity: {len(failures)} failure(s)")
print("VERDICT PASS" if not failures else "VERDICT FAIL")
sys.exit(0 if not failures else 1)
