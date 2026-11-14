#!/usr/bin/env python3
"""test_website_audit.py — audit CLI suite, fully offline via fixture transport.
Covers prompt 24.2 (single, crawl, sitemap, dedup, limits, robots, errors,
chrome, SEO, a11y, drift, reports, dry-run posture, SSRF). VERDICT PASS/FAIL."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "fixtures" / "site"
SCRIPT = HERE.parent / "scripts" / "website_audit.py"
sys.path.insert(0, str(HERE.parent / "scripts"))

FAILS = []


def check(name, cond):
    if not cond:
        FAILS.append(name); print(f"  FAIL {name}")


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def build_fixtures():
    (FIX / "test.example" / "about").mkdir(parents=True, exist_ok=True)
    (FIX / "test.example" / "sitemap.xml").write_text(
        '<?xml version="1.0"?><urlset><url><loc>https://test.example/</loc></url>'
        '<url><loc>https://test.example/about/</loc></url></urlset>', encoding="utf-8")
    (FIX / "test.example" / "sitemap-index.xml").write_text(
        '<?xml version="1.0"?><sitemapindex><sitemap><loc>https://test.example/sitemap.xml</loc>'
        '</sitemap></sitemapindex>', encoding="utf-8")
    main_p = ("Der Converter verarbeitet 3,5 MB pro Sekunde auf einem Laptop von 2019 und "
              "braucht keinen Cloud-Dienst im Hintergrund. Die Einrichtung dauert keine "
              "fünf Minuten. In der heutigen schnelllebigen Welt ist es wichtig zu "
              "betonen dass Ruhe zählt. Es ist wichtig zu betonen dass Stabilität gilt.")
    about_p = ("Das Team arbeitet seit 2021 an Konvertern und publiziert zwei Mal im "
               "Monat. Wir sind sechs Leute in drei Städten und liefern stabile Wochenbau-"
               "Versionen. Die Zukunft hat bereits begonnen. Abschließend lässt sich "
               "sagen dass die Liste wächst und jeder Konverter Tests besitzt.")
    tpl = ('<!doctype html><html lang="de"><head><title>{t}</title>'
           '<meta name="description" content="{d}"></head><body>'
           '<nav><a href="/about">click here</a></nav><main><h1>{h}</h1><p>{p}</p>'
           '<p><img src="x.png"></p></main><footer><p>Impressum Datenschutz</p>'
           '<a href="/impressum">click here</a></footer></body></html>')
    (FIX / "test.example" / "index.html").write_text(
        tpl.format(t="Converter 3,5 MB/s", d="offline Konverter für Teams",
                   h="In der heutigen schnelllebigen Welt", p=main_p), encoding="utf-8")
    (FIX / "test.example" / "about" / "index.html").write_text(
        tpl.format(t="Ueber uns — sechs Leute", d="Team seit 2021",
                   h="Wir sind sechs", p=about_p), encoding="utf-8")


build_fixtures()

r = run("https://test.example/", "--fixtures", str(FIX), "--format", "json")
check("single-page-exit1", r.returncode == 1)
d = json.loads(r.stdout)
p = d["pages"][0]
check("single-ok", p["status"] == "ok" and p["words"] > 40)
check("title", p["title"] == "Converter 3,5 MB/s")
check("findings", any(f["rule"] == "de-filler-opener" for f in p["findings"]))
check("linecols", all(f["line"] >= 1 and f["col"] >= 1 for f in p["findings"]))
check("chrome-scoped", all(c.get("scope") == "site-chrome" for c in p["chrome_repeats"]))
check("seo-generic-links", any("click here" in t for t in (p.get("seo") or {}).get("generic_link_texts", [])))
check("a11y-present", "images_missing_alt" in (p.get("accessibility") or {}))

r2 = run("https://test.example/", "--crawl", "--fixtures", str(FIX), "--format", "json")
d2 = json.loads(r2.stdout)
urls = {p["url"] for p in d2["pages"]}
check("crawl-pages", "https://test.example/about" in urls and len(d2["pages"]) >= 2)
check("dedup", len(urls) == len(d2["pages"]))
check("rollup-keys", {"tonal_drift", "site_repeats", "seo_summary"} <= set(d2["rollup"]))
check("machine-notes", "no rewriting" in d2["machine_notes"])

r3 = run("https://test.example/sitemap.xml", "--sitemap", "--fixtures", str(FIX), "--format", "json")
d3 = json.loads(r3.stdout)
check("sitemap-audits-locs", len(d3["pages"]) == 2 and d3["pages"][0]["status"] == "ok")
r3b = run("https://test.example/sitemap-index.xml", "--sitemap", "--fixtures", str(FIX), "--format", "json")
check("sitemap-index", json.loads(r3b.stdout)["pages"][0]["status"] == "sitemap")

r4 = run("https://test.example/", "--crawl", "--max-pages", "1", "--fixtures", str(FIX), "--format", "json")
check("max-pages", len(json.loads(r4.stdout)["pages"]) == 1)
r5 = run("https://test.example/", "--crawl", "--max-depth", "0", "--fixtures", str(FIX), "--format", "json")
check("depth0-root-only", len(json.loads(r5.stdout)["pages"]) == 1)

r6 = run("https://test.example/", "--fixtures", str(FIX), "--format", "text")
check("text-report", "website audit:" in r6.stdout and "site rollup" in r6.stdout)
r7 = run("https://missing.example/", "--fixtures", str(FIX), "--format", "json")
d7 = json.loads(r7.stdout)
check("missing-page-error", d7["pages"][0]["status"] == "fetch_error" and d7["pages"][0]["error"])

# SSRF guard (network-free checks)
import hw_http  # noqa: E402
try:
    hw_http.guard_url("http://127.0.0.1:8080/x"); check("ssrf-loopback", False)
except hw_http.FetchError:
    check("ssrf-loopback", True)
try:
    hw_http.guard_url("ftp://host/x"); check("ssrf-scheme", False)
except hw_http.FetchError:
    check("ssrf-scheme", True)
check("guard-allows-public", hw_http.guard_url("https://example.com") == "https://example.com")

# rewrite posture: CLI never rewrites productively
check("no-productive-rewrite", "no rewriting performed here" in d2["machine_notes"])

# robots via stubbed transport
_orig = hw_http.Fetcher.fetch
def fake(self, url, **k):
    if str(url).endswith("robots.txt"):
        return hw_http.Response(url, 200, "User-agent: *\nDisallow: /private/\n", url)
    raise hw_http.FetchError("offline")
hw_http.Fetcher.fetch = fake
fr = hw_http.Fetcher()
check("robots-disallow", fr.robots_allows("https://site.test/private/a") is False)
check("robots-allow", fr.robots_allows("https://site.test/public") is True)
hw_http.Fetcher.fetch = _orig

print("VERDICT " + ("PASS" if not FAILS else f"FAIL {len(FAILS)}: {FAILS}"))
sys.exit(0 if not FAILS else 1)
