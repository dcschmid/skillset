"""hw_rules.py — pattern registry for the human-writing skill.

Detection rules only. A rule finds candidates; it never proves authorship and
never fires on a single isolated occurrence (density and context set severity
at report time). Findings carry: rule id, category, severity, line/col,
excerpt, why, fix hint.

Categories follow the skill's pattern taxonomy (references/patterns-core.md):
formulaic-structure, artificial-contrast, rule-of-three, signposting,
promotional-inflation, empty-conclusion, synthetic-enthusiasm, rhythm,
generic-transition, pseudo-profundity, hedging, synonym-cycling,
formatting-overuse, overexplaining, emotional-overstatement, repetition.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from hw_text import PROTECT_RE, detect_lang, paragraphs, repeated_phrases, rhythm, sentences

# id -> (category, default severity, why)
# severity: high = near-always fix; med = context dependent; low = density-only.
RULES: dict[str, tuple[str, str, str]] = {
    "de-filler-opener": ("signposting", "low", "Filler opener: ceremony, no information."),
    "en-filler-opener": ("signposting", "low", "Filler opener: announces the sentence instead of saying it."),
    "de-promo": ("promotional-inflation", "med", "Marketing inflation without a checkable claim."),
    "en-promo": ("promotional-inflation", "med", "Marketing inflation without a checkable claim."),
    "contrast": ("artificial-contrast", "med", "Contrast frame: only earns its place when the contrast is the point."),
    "triad": ("rule-of-three", "low", "List of three: fine as a device, telling as a habit."),
    "enthusiasm": ("synthetic-enthusiasm", "med", "Enthusiasm without a source or evidence."),
    "conclusion": ("empty-conclusion", "med", "Conclusion that only restates."),
    "transition": ("generic-transition", "low", "Transition glue: fine rarely, noise in bulk."),
    "profundity": ("pseudo-profundity", "med", "Sounding deep without saying what."),
    "hedging": ("hedging", "low", "Hedging stack: commit or cite."),
    "repetition": ("repetition", "med", "Same wording repeated; merge or cut."),
    "rhythm": ("rhythm", "low", "Uniform sentence rhythm reads as machine default."),
    "formatting": ("formatting-overuse", "med", "Formatting doing a structure's job without the structure."),
    "enthusiasm-punct": ("synthetic-enthusiasm", "low", "Exclamation stacking."),
}

# --------------------------------------------------------------- lexicons (de)
_DE = {
    "filler": [
        r"in der heutigen \w+[- ]?\w*welt", r"es ist wichtig[ ,]?\w* zu (?:betonen|erwähn\w+|unterstreich\w+)",
        r"es gilt zu beachten", r"abschließend lässt sich (?:festhalten|sagen)",
        r"zusammenfassend lässt sich sagen", r"eine entscheidende rolle spiel\w+",
        r"ein wichtiger aspekt ist", r"in diesem zusammenhang",
        r"darüber hinaus ist hervorzuheben", r"es eröffnet \w* neue möglichkeiten",
        r"ein umfassender überblick", r"ein bedeutender meilenstein",
        r"innovative\w* und zukunftsweisend\w*", r"lass(?: uns|t uns) gemeinsam? eintauchen",
        r"tauchen wir ein", r"im folgenden werden wir", r"die zukunft hat bereits begonnen",
        r"maßgeschneiderte lösung\w*", r"neue maßstäbe setzen", r"auf das nächste level",
        r"potenziale(?: voll)? ausschöpf\w+", r"wie wir alle wissen",
        r"es lohnt sich zu (?:erkennen|verstehen)", r"in anbetracht",
    ],
    "promo": [
        r"revolutionär\w*", r"bahnbrechend\w*", r"weltklasse", r"branchenführend",
        r"zukunftsweisend\w*", r"state[- ]of[- ]the[- ]art", r"nahtlos(?: e\w+| integrier\w+)",
        r"ganzheitlich\w*", r"synergien? nutzen", r"einzigartig\w* lösung\w*",
    ],
    "transition": [
        r"\b(?:außerdem|darüber hinaus|des weiteren|ferner|zudem|ebenso|gleichwohl)\b",
        r"\b(?:also|somit|folglich|mithin)\b", r"\b(?:jedoch|allerdings|dennoch|gleichzeitig)\b",
    ],
    "conclusion": [
        r"\b(?:zusammenfassend|abschließend|insgesamt|alles in allem|fazit|unterm strich)\b",
        r"letztlich zeigt sich",
    ],
    "hedge": [
        r"\b(?:in der regel|im grunde genommen|quasi|sozusagen|gewissermaßen|mehr oder weniger|"
        r"mit anderen worten|nicht zuletzt|soweit erkennbar|grundsätzlich|prinzipiell)\b",
    ],
    "profoundity": [
        r"im kern (?:geht es|bedeutet das)", r"der wahre wert liegt darin",
        r"die zukunft (?:ist|hat) bereits", r"weit mehr als nur", r"das ist mehr als (?:nur )?[\wäöüß]+",
    ],
    "enthusiasm": [
        r"\b(?:genial|grandios|beeindruckend|faszinierend|begeist(?:er|ert|erte)\w*|wunderbar)\b",
        r"\bich (?:freue mich|liebe)\b",
    ],
}
# --------------------------------------------------------------- lexicons (en)
_EN = {
    "filler": [
        r"in today['\u2019]s \w+[- ]?\w* (?:world|era|age)", r"it['\u2019]s (?:important|crucial|essential|worth) to (?:note|remember|mention)",
        r"let['\u2019]s (?:dive|delve|jump|explore) (?:in|into)", r"at its core", r"here['\u2019]s the thing",
        r"needless to say", r"the ever[- ]?evolving landscape", r"the future isn['\u2019]t coming",
        r"what nobody tells you", r"the part everyone misses", r"let that sink in",
        r"this highlights the importance", r"a testament to", r"a powerful reminder",
        r"unlock(?:ing)? the (?:power|potential)", r"game[- ]changer", r"seamlessly integrat\w+",
        r"navigate the complexities", r"a vibrant tapestry", r"play(?:s|ing)? a (?:crucial|vital|key|significant) role",
        r"whether you['\u2019]re a", r"in conclusion[,.]", r"to sum(?:mary| up)[,.]",
    ],
    "promo": [
        r"\b(?:revolutionary|groundbreaking|cutting[- ]edge|world[- ]class|industry[- ]leading|"
        r"next[- ]level|best[- ]in[- ]class|unprecedented)\b",
        r"\bunleash(?:ing)? \w+", r"\bempower(?:ing|s)? you to\b",
    ],
    "transition": [
        r"\b(?:moreover|furthermore|additionally|in addition|that being said|with that said|on top of that)\b",
        r"\b(?:however|nevertheless|nonetheless),", r"\b(?:therefore|thus|hence|consequently),",
    ],
    "conclusion": [r"\b(?:in conclusion|to summarize|in summary|all in all|at the end of the day|ultimately)[,.]"],
    "hedge": [
        r"\b(?:arguably|generally speaking|broadly speaking|it seems that|it can be said|"
        r"more often than not|to some extent|quite simply)\b",
    ],
    "profoundity": [
        r"it['\u2019]s (?:not|never) about \w+", r"at its (?:core|heart)", r"the real (?:power|value|question) lies",
        r"more than (?:just )?\w+",
    ],
    "enthusiasm": [r"\b(?:amazing|incredible|exciting|fascinating|brilliant|stunning|game[- ]changing)\b"],
}
_CONTRAST = {
    "de": [r"nicht (?:nur|um \w+ zu) .{0,60},? sondern", r"es geht nicht um .{0,50},? sondern um",
           r"\w+ ist nicht \w+[,.]?\s+es ist \w+"],
    "en": [r"not (?:just|about|only) .{0,60}, (?:but|it) ",
           r"\bit\s*['\u2019]?\s*(?:is|was|s)?\s*(?:not|never)\b[^.]{0,40}\.\s*it\s+(?:is|was|['\u2019]s)?\s?\w+",
           r"\w+ rather than \w+"],
}
_LEX = {"de": _DE, "en": _EN}
_RULEID = {"filler": ("de-filler-opener", "en-filler-opener"), "promo": ("de-promo", "en-promo"),
           "transition": ("transition", "transition"), "conclusion": ("conclusion", "conclusion"),
           "hedge": ("hedging", "hedging"), "profoundity": ("profundity", "profundity"),
           "enthusiasm": ("enthusiasm", "enthusiasm")}

# Tolerated surfaces: never penalised on their own.
_TOLERATED = ("—", "–", "-", ":", ";")


@dataclass
class Finding:
    rule: str
    line: int
    col: int
    excerpt: str
    why: str
    fix: str = ""

    def as_dict(self) -> dict:
        cat, sev, _ = RULES[self.rule]
        return {"rule": self.rule, "category": cat, "severity": sev, "line": self.line,
                "col": self.col, "excerpt": self.excerpt, "why": self.why, "fix": self.fix}


def _line_offsets(text: str) -> list[int]:
    offs, pos = [0], 0
    for ln in text.splitlines():
        pos += len(ln) + 1
        offs.append(pos)
    return offs


def _locate(abspos: int, offs: list[int]) -> tuple[int, int]:
    line = 1
    for i, off in enumerate(offs):
        if off > abspos:
            break
        line = i + 1
    return line, abspos - offs[line - 1] + 1


def scan(text: str, lang: str | None = None, max_findings: int = 400) -> list[Finding]:
    """Full rule pass over prose. lang: 'de'|'en'|None=auto-detect per text."""
    if lang not in ("de", "en"):
        d = detect_lang(text)
        lang = d if d in _LEX else "en"
    lex, offs, out = _LEX[lang], _line_offsets(text), []
    seen: set[tuple] = set()

    def emit(rid: str, matched: str, abspos: int, fix: str = "") -> None:
        key = (rid, abspos)
        if key in seen:
            return
        seen.add(key)
        line, col = _locate(abspos, offs)
        out.append(Finding(rid, line, col, " ".join(matched.split())[:120], RULES[rid][2], fix))

    for p in paragraphs(text):
        ppos = text.find(p)
        clean = PROTECT_RE.sub(" ", p)  # code/links stay out of prose matching
        for bucket, pats in lex.items():
            rid = _RULEID[bucket][0 if lang == "de" else 1]
            for pat in pats:
                for m in re.finditer(pat, clean, re.I):
                    emit(rid, m.group(0), ppos + m.start())
        for pat in _CONTRAST[lang]:
            for m in re.finditer(pat, clean, re.I | re.S):
                emit("contrast", m.group(0), ppos + m.start())
        dashes = sum(clean.count(c) for c in ("—", "–"))
        if dashes >= 3:
            emit("formatting", f"{dashes}× dash", ppos, "One dash is fine; a dash every sentence is a habit.")
        if p.count("**") >= 4:
            emit("formatting", "bold ×" + str(p.count("**") // 2), ppos, "Bold every other word and none stand out.")

    if len(sentences(text)) >= 5:
        r = rhythm(text)
        if r["uniform"]:
            line, col = _locate(len(text) // 2, offs)
            out.append(Finding("rhythm", line, col, f"cv={r['cv']} mean={r['mean']}w",
                               RULES["rhythm"][2], "Vary sentence length; split or merge one or two."))
    for gram, cnt in repeated_phrases(text, min_count=3):
        first = gram.split()[0]
        at = text.lower().find(first.lower())
        line, col = _locate(max(at, 0), offs)
        out.append(Finding("repetition", line, col, f"\u201c{gram}\u201d ×{cnt}", RULES["repetition"][2],
                           "Keep one instance or merge the duplicates."))
    if len(re.findall(r"!", text)) >= 4:
        out.append(Finding("enthusiasm-punct", 1, 1, "!" * 0 + "exclamations",
                           RULES["enthusiasm-punct"][2], "Cut to the one place excitement is earned."))

    out.sort(key=lambda f: (f.line, f.col))
    return out[:max_findings]
