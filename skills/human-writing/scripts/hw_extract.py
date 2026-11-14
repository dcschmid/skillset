"""hw_extract.py — HTML/Markdown/MDX/JSON content extraction for audits.

Stdlib-only HTMLParser (no bs4 dependency). Separates main content from
chrome (nav/footer/header/aside) so repeated site furniture is not reported
per page. Handles Astro/React/Vue/Svelte SSG output because it parses the
delivered HTML, not the framework.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser

CHROME_TAGS = {"nav", "footer", "header", "aside", "form"}
DROP_TAGS = {"script", "style", "noscript", "template"}
BLOCK_TAGS = {"p", "div", "li", "section", "article", "main", "br", "tr",
              "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "table", "blockquote", "dd", "dt"}


@dataclass
class Page:
    url: str
    title: str = ""
    meta_description: str = ""
    lang: str = ""
    main_text: str = ""
    blocks: list[tuple[str, str]] = field(default_factory=list)  # (kind, text) main
    chrome_blocks: list[tuple[str, str]] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    headings: list[tuple[int, str]] = field(default_factory=list)
    alt_texts: list[str] = field(default_factory=list)
    link_texts: list[str] = field(default_factory=list)
    repeated: bool = False  # page-level: chrome noise removed

    @property
    def prose(self) -> str:
        return "\n\n".join(t for k, t in self.blocks if k == "p" or k.startswith("h"))


class _Extractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.meta_desc = ""
        self.lang = ""
        self.blocks: list[tuple[str, str]] = []
        self.chrome: list[tuple[str, str]] = []
        self.links: list[str] = []
        self.alts: list[str] = []
        self.link_texts: list[str] = []
        self._stack: list[str] = []
        self._in_chrome = 0
        self._buf: list[str] = []
        self._kind = "p"
        self._in_title = False
        self._skip = 0
        self._link_mark: int | None = None

    def _flush(self) -> None:
        text = " ".join("".join(self._buf).split())
        self._buf = []
        if not text:
            return
        (self.chrome if self._in_chrome else self.blocks).append((self._kind, text))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in DROP_TAGS:
            self._skip += 1
            return
        if self._skip:
            return
        if tag == "title":
            self._in_title = True
        elif tag == "html" and a.get("lang"):
            self.lang = a["lang"]
        elif tag == "meta" and a.get("name", "").lower() == "description":
            self.meta_desc = a.get("content", "")
        elif tag == "img" and a.get("alt"):
            self.alts.append(a["alt"])
        elif tag == "a":
            href = a.get("href", "")
            if href and not href.startswith(("#", "mailto:", "javascript:")):
                self.links.append(href)
            self._link_mark = len(self._buf)
        if tag in CHROME_TAGS:
            self._in_chrome += 1
        if tag in BLOCK_TAGS:
            self._flush()
            self._kind = tag if tag.startswith("h") else "p"
        self._stack.append(tag)

    def handle_endtag(self, tag):
        if tag in DROP_TAGS:
            self._skip = max(0, self._skip - 1)
            return
        if self._skip:
            return
        if tag == "title":
            self._in_title = False
        if tag == "a" and self._link_mark is not None:
            anchor = " ".join("".join(self._buf[self._link_mark:]).split())
            if anchor:
                self.link_texts.append(anchor)
            self._link_mark = None
        if tag in CHROME_TAGS:
            self._flush()
            self._in_chrome = max(0, self._in_chrome - 1)
        if tag in BLOCK_TAGS:
            self._flush()
        if self._stack and self._stack[-1] == tag:
            self._stack.pop()

    def handle_data(self, data):
        if self._skip:
            return
        if self._in_title:
            self.title += data
            return
        self._buf.append(data)

    def finish(self):
        self.close()  # flush pending buffers before reading results
        self._flush()
        return self


def extract_html(html: str, url: str = "") -> Page:
    ex = _Extractor()
    ex.feed(html)
    p = ex.finish()
    page = Page(url=url, title=" ".join(p.title.split()), meta_description=p.meta_desc,
                lang=p.lang, links=p.links, alt_texts=p.alts)
    page.blocks = [(k, t) for k, t in p.blocks]
    page.chrome_blocks = [(k, t) for k, t in p.chrome]
    page.link_texts = p.link_texts
    page.headings = [(int(k[1]), t) for k, t in page.blocks if k.startswith("h") and k[1:].isdigit()]
    main = [t for k, t in page.blocks if k == "p" or k.startswith("h")]
    page.main_text = "\n\n".join(main)
    return page


def is_sitemap(body: str) -> bool:
    head = body[:400]
    return "<urlset" in head or "sitemapindex" in head or "<url>" in head


def sitemap_urls(body: str) -> list[str]:
    return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body, re.I)


def extract_markdown(text: str, url: str = "") -> Page:
    """Markdown/MDX: prose from paragraphs and headings; code fences dropped."""
    body = re.sub(r"```.*?```", "", text, flags=re.S)
    fm = re.match(r"^---\n.*?\n---\n", body, re.S)
    meta = {}
    if fm:
        for line in fm.group(0).splitlines()[1:-1]:
            if ":" in line:
                k, _, v = line.partition(":")
                meta[k.strip()] = v.strip().strip("\"'")
        body = body[fm.end():]
    page = Page(url=url, title=meta.get("title", "") or meta.get("description", ""))
    page.meta_description = meta.get("description", "")
    for m in re.finditer(r"^(#{1,6})\s+(.+)$", body, re.M):
        page.blocks.append(("h" + str(len(m.group(1))), " ".join(m.group(2).split())))
    prose = re.sub(r"^(#{1,6})\s+.+$", "", body, flags=re.M)
    for para in re.split(r"\n\s*\n", prose):
        t = " ".join(re.sub(r"<[^>]+>", " ", para).split())  # drop JSX/markup
        t = re.sub(r"[{}|]", " ", t)
        if len(t) > 20 and not t.startswith(("import ", "export ", "const ", "export{")):
            page.blocks.append(("p", t))
    page.headings = [(int(k[1]), t) for k, t in page.blocks if k[1:].isdigit()]
    page.main_text = "\n\n".join(t for _, t in page.blocks)
    return page


def extract_json_content(raw: str, url: str = "") -> Page:
    """JSON content files / CMS exports: string values that look like prose."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return Page(url=url)
    texts: list[str] = []

    def walk(node) -> None:
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
        elif isinstance(node, str) and len(node.split()) >= 4:
            texts.append(" ".join(node.split()))

    walk(data)
    page = Page(url=url, main_text="\n\n".join(texts))
    page.blocks = [("p", t) for t in texts]
    return page
