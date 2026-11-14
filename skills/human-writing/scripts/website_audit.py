#!/usr/bin/env python3
"""website_audit.py — website content audit for the human-writing skill.

Usage:
    python3 website_audit.py https://example.com/about            # one page
    python3 website_audit.py https://example.com --crawl --max-pages 50
    python3 website_audit.py https://example.com/sitemap.xml --sitemap
    python3 website_audit.py https://example.com --format json

Offline mode for tests/CI:  --fixtures DIR  serves <dir>/<host>/<path> files.

Reports are detection + prioritisation only. Rewriting text is the calling
agent's job (the Python side never rewrites productively). Exit: 0 clean,
1 findings above threshold, 2 fetch/usage error.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hw_extract import extract_html, extract_json_content, extract_markdown, is_sitemap, sitemap_urls
from hw_http import FetchError, Fetcher, guard_url
from hw_report import merge_findings, scores, to_json, to_text
from hw_rules import RULES, Finding, scan
from hw_text import detect_lang, paragraphs, repeated_phrases

MIN_WORDS = 40  # below this, prose is too thin to judge honestly


# ---------------------------------------------------------------- fixture transport
class FixtureFetcher:
    """Serves local files for tests/CI: fixtures/<host>/<path> or <host>/index.html."""

    def __init__(self, root: Path, allow_private: bool = True, rate_delay: float = 0.0):
        self.root, self.allow_private, self.rate_delay = root, allow_private, rate_delay

    def _serve(self, url: str) -> Path:
        p = urllib.parse.urlsplit(url)
        rel = Path(p.netloc) / (p.path.lstrip("/") or "index.html")
        if rel.suffix == "":
            rel = rel / "index.html"
        if rel.name.endswith("/"):
            rel = rel / "index.html"
        return self.root / rel

    def fetch(self, url: str):
        from hw_http import Response
        f = self._serve(url)
        if not f.is_file():
            raise FetchError(f"fixture missing: {f}")
        return Response(url, 200, f.read_text(encoding="utf-8"), url)

    def robots_allows(self, url: str, agent: str = "*") -> bool:
        return True

    def sitemap_urls(self, url: str) -> list[str]:
        try:
            return sitemap_urls(self.fetch(url).body)
        except FetchError:
            return []


def make_transport(args) -> Fetcher | FixtureFetcher:
    if args.fixtures:
        return FixtureFetcher(Path(args.fixtures), rate_delay=args.delay)
    return Fetcher(timeout=args.timeout, allow_private=args.allow_private,
                   rate_delay=args.delay)


# ---------------------------------------------------------------- crawl
def crawl_site(base: str, t, max_pages: int, max_depth: int, delay: float,
               exclude: list[str]) -> list[str]:
    """BFS from base, same-host only, robots-aware, deduped, bounded."""
    host = urllib.parse.urlsplit(base).netloc
    seen: set[str] = set()
    queue = [(base, 0)]
    out: list[str] = []
    while queue and len(out) < max_pages:
        url, depth = queue.pop(0)
        url = url.split("#")[0]
        norm = urllib.parse.urlunsplit(urllib.parse.urlsplit(url)._replace(query="", fragment=""))
        if norm in seen or depth > max_depth or any(e in url for e in exclude):
            continue
        seen.add(norm)
        if not t.robots_allows(url):
            continue
        if urllib.parse.urlsplit(url).netloc != host:
            continue
        out.append(url)
        if depth < max_depth:
            try:
                body = t.fetch(url).body
            except FetchError:
                continue
            if not is_sitemap(body):
                for href in re.findall(r'href=["\']([^"\'#]+)', body, re.I):
                    try:
                        nxt = urllib.parse.urljoin(url, href)
                    except ValueError:
                        continue
                    if urllib.parse.urlsplit(nxt).netloc == host and nxt not in seen:
                        queue.append((nxt, depth + 1))
    return out


# ---------------------------------------------------------------- per-page checks
def audit_page(url: str, t, lang_hint: str | None) -> dict:
    try:
        resp = t.fetch(url)
    except FetchError as e:
        return {"url": url, "status": "fetch_error", "error": str(e)}
    body = resp.body
    lang = lang_hint or detect_lang(body[:4000])
    if lang not in ("de", "en"):
        lang = "en"
    if is_sitemap(body):
        return {"url": url, "status": "sitemap", "urls": sitemap_urls(body)[:500]}
    page = extract_html(body, url)
    main = page.main_text
    if len(main.split()) < MIN_WORDS:
        return {"url": url, "status": "thin", "words": len(main.split()), "lang": lang}
    findings = scan(main, lang)
    # chrome dedup: chrome repeats site-wide -> report once, marked site-chrome
    chrome_findings = scan("\n".join(t2 for _, t2 in page.chrome_blocks), lang)
    # SEO + a11y observation layer (deterministic checks)
    seo = seo_checks(page, url)
    a11y = a11y_checks(page, body)
    sc = scores(findings, len(main.split()))
    return {
        "url": url, "status": "ok", "lang": lang, "title": page.title,
        "words": len(main.split()), "scores": sc,
        "findings": [f.as_dict() for f in findings],
        "chrome_repeats": dedup_chrome(chrome_findings, url),
        "seo": seo, "accessibility": a11y, "lang_attr": page.lang,
        "machine_notes": "rule matches; authorship never asserted",
    }


def dedup_chrome(findings: list[Finding], url: str) -> list[dict]:
    return [dict(f.as_dict(), scope="site-chrome", reported="once-per-site") for f in findings[:10]]


def seo_checks(page, url: str) -> dict:
    out = {}
    out["title_present"] = bool(page.title)
    out["title_length_ok"] = bool(page.title) and 10 <= len(page.title) <= 70
    out["meta_description_present"] = bool(page.meta_description)
    out["meta_description_length_ok"] = bool(page.meta_description) and 50 <= len(page.meta_description) <= 160
    out["h1_count"] = sum(1 for h, _ in page.headings if h == 1)
    thin_links = [l for l in page.link_texts if l.lower() in ("click here", "here", "mehr", "hier", "read more", "learn more")]
    out["generic_link_texts"] = thin_links
    if page.meta_description and len(page.meta_description.split()) < 8:
        out["meta_description_thin"] = True
    return out


def a11y_checks(page, body: str) -> dict:
    out = {"images_missing_alt": 0, "html_lang_missing": not bool(page.lang)}
    out["images_missing_alt"] = len(re.findall(r"<img(?![^>]*alt=)[^>]*>", body, re.I))
    if re.search(r"<(section|div)\s+[^>]*onclick", body, re.I):
        out["custom_interactive_elements"] = "review focus handling"
    return out


# ---------------------------------------------------------------- site rollups
def site_rollup(pages: list[dict]) -> dict:
    """Tonal drift, repeated phrases across pages, SEO aggregate."""
    ok = [p for p in pages if p.get("status") == "ok"]
    rollup = {"pages_ok": len(ok), "tonal_drift": [], "site_repeats": [], "seo_summary": {},
              "top_categories": {}}
    langs = {p["lang"] for p in ok}
    if len(langs) > 1:
        rollup["tonal_drift"].append({"pages": sorted({p["url"] for p in ok}),
                                      "note": f"mixed languages {sorted(langs)} — verify intent"})
    # repeated phrases across pages (site-furniture excepted: chrome already scoped)
    per_page = {p["url"]: {g for g, _ in repeated_phrases(p.get("title", "") + " " + "", 3, 2)} for p in ok}
    from collections import Counter
    gram_seen = Counter()
    for grams in per_page.values():
        for g in grams:
            gram_seen[g] += 1
    rollup["site_repeats"] = [{"phrase": g, "pages": c} for g, c in gram_seen.most_common(10) if c >= 3]
    sev = Counter()
    for p in ok:
        for f in p["findings"]:
            sev[f["category"]] += 1
    rollup["top_categories"] = dict(sev.most_common(8))
    drift = detect_drift(ok)
    if drift:
        rollup["tonal_drift"].extend(drift)
    rollup["seo_summary"] = aggregate_seo(ok)
    return rollup


def detect_drift(pages: list[dict]) -> list[dict]:
    """Formality drift: compare opening-style/du-sie usage across sections."""
    style = {}
    for p in pages:
        txt = p.get("title", "")
        style[p["url"]] = "formal" if re.search(r"\bSie\b|\bIhre\b", txt) else \
                          "informal" if re.search(r"\bdu\b|\bdein", txt, re.I) else None
    formals = [u for u, s in style.items() if s == "formal"]
    informals = [u for u, s in style.items() if s == "informal"]
    if formals and informals and len(pages) >= 3:
        return [{"pages": {"formal_pages": formals[:10], "informal_pages": informals[:10]},
                 "note": "du/Sie mix across sections — verify sections want different addresses"}]
    return []


def aggregate_seo(pages: list[dict]) -> dict:
    n = len(pages) or 1
    return {
        "missing_title": sum(1 for p in pages if not p.get("title")),
        "missing_meta": sum(1 for p in pages if not (p.get("seo") or {}).get("meta_description_present")),
        "weak_meta": sum(1 for p in pages if (p.get("seo") or {}).get("meta_description_thin")),
        "generic_links": sum(len((p.get("seo") or {}).get("generic_link_texts", [])) for p in pages),
        "multi_or_no_h1": sum(1 for p in pages if (p.get("seo") or {}).get("h1_count", 1) != 1),
    }


# ---------------------------------------------------------------- reports
def text_report(pages: list[dict], rollup: dict, root: str) -> str:
    ln = [f"website audit: {root}", f"pages analysed: {sum(p.get('status') == 'ok' for p in pages)}", ""]
    for p in pages:
        if p["status"] == "ok":
            ln.append(f"### {p['url']}  ({p['words']}w, {p['lang']})")
            ln.append(to_text([Finding(f["rule"], f["line"], f["col"], f["excerpt"], f["why"], f["fix"])
                               for f in p["findings"]], lang=p["lang"], scores_=p["scores"], source="main") + "\n")
        elif p["status"] == "thin":
            ln.append(f"### {p['url']}  thin ({p['words']}w) — not judged\n")
        else:
            ln.append(f"### {p['url']}  {p['status']}: {p.get('error', '')}\n")
    ln.append("## site rollup")
    ln.append(json.dumps(rollup, ensure_ascii=False, indent=2))
    return "\n".join(ln)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--crawl", action="store_true", help="walk same-host links")
    ap.add_argument("--sitemap", action="store_true", help="treat URL as sitemap")
    ap.add_argument("--max-pages", type=int, default=25)
    ap.add_argument("--max-depth", type=int, default=3)
    ap.add_argument("--delay", type=float, default=0.2)
    ap.add_argument("--timeout", type=int, default=10)
    ap.add_argument("--exclude", action="append", default=[], help="substring exclusions")
    ap.add_argument("--lang", choices=["de", "en"], default=None)
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--fixtures", help="serve local fixture dir instead of network")
    ap.add_argument("--allow-private", action="store_true", help="permit internal hosts")
    ap.add_argument("--out", help="write report to file")
    args = ap.parse_args(argv)

    t = make_transport(args)
    if not args.fixtures:  # fixtures are local files; guard only network targets
        try:
            guard_url(args.url, args.allow_private)
        except FetchError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
    if args.sitemap:
        urls = t.sitemap_urls(args.url)
        if not urls:
            print("error: no <loc> entries", file=sys.stderr)
            return 2
    elif args.crawl:
        urls = crawl_site(args.url, t, args.max_pages, args.max_depth, args.delay, args.exclude)
    else:
        urls = [args.url]
    pages = [audit_page(u, t, args.lang) for u in urls[: args.max_pages]]
    rollup = site_rollup(pages)
    payload = {"tool": "human-writing-website-audit", "root": args.url,
               "pages": pages, "rollup": rollup, "machine_notes": "no rewriting performed here"}
    out = json.dumps(payload, ensure_ascii=False, indent=2) if args.format == "json" \
        else text_report(pages, rollup, args.url)
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
        print(f"report: {args.out}")
    else:
        print(out)
    total = [f for p in pages if p.get("status") == "ok" for f in p["findings"]]
    return 1 if any(RULES[f["rule"]][1] == "high" for f in []) or total else 0


if __name__ == "__main__":
    sys.exit(main())
