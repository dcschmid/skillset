"""hw_text.py — shared text utilities for the human-writing skill.

Stdlib-only. Language detection, sentence/word segmentation with protected
spans (code, links, quotes, numbers), repeated-ngram counting, and the
text-level stats every consumer (linter, website audit, project audit) needs.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from statistics import pstdev

# ---------------------------------------------------------------- protected spans
# Code fences, inline code, HTML blocks, images/links, URLs, and numbers are
# never rewritten by any analysis and never counted as prose.
PROTECT_RE = re.compile(
    r"```.*?```"
    r"|~~~.*?~~~"
    r"|`[^`\n]+`"
    r"|<(?:pre|code|script|style|kbd)[^>]*>.*?</(?:pre|code|script|style|kbd)>"
    r"|\[[^\]]*\]\([^)]*\)"
    r"|!\[[^\]]*\]\([^)]*\)"
    r"|\{\{[^}]*\}\}|\{[^{}\n]{1,80}\}"
    r"|https?://\S+",
    re.S | re.I,
)

# Link text inside a protected link is visible prose; audits may inspect it.
_LINKTEXT_RE = re.compile(r"^\[([^\]]+)\]\(", re.S)

_ABBREV = {
    "z", "b", "etc", "i.e", "e.g", "cf", "vs", "u.s.w", "usw", "usf", "d.h",
    "ca", "ff", "h.c", "Inc", "Jr", "Sr", "Dr", "Prof", "Mr", "Mrs", "Ms",
}
_NUM_CTX = re.compile(r"\d[.,]\d|\d\s*$|^[.,]\d")

_SENT_SPLIT = re.compile(r"(?<=[.!?。！？])\s+(?=[\"'“„»\(\[]?[A-ZÄÖÜÄÖÜß0-9„“])")
_PARA_SPLIT = re.compile(r"\n\s*\n")


def strip_code(text: str) -> str:
    """Replace protected spans with placeholders so prose stats stay clean."""
    spans: list[str] = []

    def _keep(m: re.Match) -> str:
        spans.append(m.group(0))
        return "\x00%d\x00" % (len(spans) - 1)

    return PROTECT_RE.sub(_keep, text), spans


def restore(text: str, spans: list[str]) -> str:
    return re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], text)


def link_texts(text: str) -> list[str]:
    out = []
    for m in PROTECT_RE.finditer(text):
        lm = _LINKTEXT_RE.match(m.group(0))
        if lm:
            out.append(lm.group(1).strip())
    return out


# ---------------------------------------------------------------- segmentation
def paragraphs(text: str) -> list[str]:
    return [p.strip() for p in _PARA_SPLIT.split(text.strip()) if p.strip()]


def sentences(text: str) -> list[str]:
    """Prose sentences: decimal-point and abbreviation safe, code-free."""
    clean, _ = strip_code(text)
    clean = re.sub(r"\s+", " ", clean).strip()
    parts: list[str] = []
    for chunk in _SENT_SPLIT.split(clean):
        if not chunk:
            continue
        if parts and _continues(parts[-1], chunk):
            parts[-1] = parts[-1] + " " + chunk
        else:
            parts.append(chunk)
    return [p for p in parts if re.search(r"[\wäöüßÄÖÜ]", p)]


def _continues(prev: str, nxt: str) -> bool:
    """True when a period ended an abbreviation/number, not a sentence."""
    if not prev.endswith("."):
        return False
    last = prev.rstrip('".“”»)').rsplit(" ", 1)[-1].rstrip(".")
    if last in _ABBREV or re.fullmatch(r"[A-Z]", last or " "):
        return True
    if _NUM_CTX.search(prev[-6:] + "|" + nxt[:6]):
        return True
    return nxt[:1].islower() and bool(last) and last.isalpha() and len(last) <= 4


WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß0-9]+(?:[-'][A-Za-zäöüß]+)*")


def words(text: str) -> list[str]:
    clean, _ = strip_code(text)
    return WORD_RE.findall(clean)


# ---------------------------------------------------------------- language
_DE_MARKERS = re.compile(
    r"\b(der|die|das|und|ist|sind|nicht|ein|eine|mit|auf|für|von|den|dem|des|"
    r"wird|werden|kann| muss|auch|wie|aber|wenn|dann|hier|diese|r|um|zu|zur|"
    r"bei|aus|nach|über|unter|sehr|mehr|schon|noch|nur|oder|weil|dass|man)\b"
)
_EN_MARKERS = re.compile(
    r"\b(the|and|is|are|of|to|that|this|with|for|you|your|it|its|from|have|"
    r"has|was|were|can|will|not|but|what|when|which|their|there)\b", re.I
)
_DE_HARD = re.compile(r"[äöüßÄÖÜ„“«»]|\bum\s+\w+\s+zu\b")


def detect_lang(text: str) -> str:
    """'de' | 'en' | 'mixed' | 'unknown'. Markers only — honest heuristics."""
    de = len(_DE_MARKERS.findall(text)) + len(_DE_HARD.findall(text)) * 3
    en = len(_EN_MARKERS.findall(text))
    if de == 0 and en == 0:
        return "unknown"
    if de >= 3 and en >= 3 and min(de, en) / max(de, en) > 0.5:
        return "mixed"
    return "de" if de >= en else "en"


# ---------------------------------------------------------------- n-grams / shape
_STOP = re.compile(
    r"^(der|die|das|und|ist|sind|zu|von|mit|für|auf|in|im|an|am|bei|ein|eine|"
    r"den|dem|des|auch|als|wie|nicht|es|er|sie|wir|ihr|the|and|is|are|of|to|"
    r"that|this|with|for|you|your|it|its|from|have|was|were)$", re.I
)


def repeated_phrases(text: str, n: int = 3, min_count: int = 2, max_report: int = 12) -> list[tuple[str, int]]:
    """Repeated word n-grams (default trigrams) worth flagging. Stopword-only
    grams and protected spans are noise and dropped."""
    clean, _ = strip_code(text)
    toks = [w.lower() for w in WORD_RE.findall(clean)]
    counts: dict[str, int] = {}
    for i in range(len(toks) - n + 1):
        gram = toks[i : i + n]
        if all(_STOP.match(t) for t in gram):
            continue
        if any(len(t) > 20 for t in gram):
            continue
        counts[" ".join(gram)] = counts.get(" ".join(gram), 0) + 1
    hits = [(g, c) for g, c in counts.items() if c >= min_count]
    hits.sort(key=lambda gc: -gc[1])
    return hits[:max_report]


def para_shape(para: str) -> tuple[int, int]:
    """(sentences, words) — the paragraph-shape fingerprint."""
    clean = re.sub(r"^#{1,6}\s+", "", para)
    return len(sentences(clean)), len(words(clean))


def rhythm(text: str) -> dict:
    """Sentence-length profile. CV = std/mean of sentence word counts."""
    lens = [len(words(s)) for s in sentences(text)]
    if not lens:
        return {"sentences": 0, "mean": 0.0, "cv": 0.0, "longest": 0, "shortest": 0,
                "open_starts": {}, "uniform": False}
    mean = sum(lens) / len(lens)
    cv = pstdev(lens) / mean if mean else 0.0
    opens: dict[str, int] = {}
    for s in sentences(text):
        w = words(s)
        if w:
            key = " ".join(w[:2]).lower()
            opens[key] = opens.get(key, 0) + 1
    return {
        "sentences": len(lens),
        "mean": round(mean, 1),
        "cv": round(cv, 2),
        "longest": max(lens),
        "shortest": min(lens),
        "open_starts": {k: v for k, v in opens.items() if v >= 2},
        "uniform": len(lens) >= 5 and cv < 0.25,
    }
