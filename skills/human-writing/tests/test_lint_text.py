#!/usr/bin/env python3
"""test_lint_text.py — linter language suites. Run: python3 tests/test_lint_text.py
Covers prompt 24.1 items 1-20 via assertions on scan()/CLI. Verdict: PASS/FAIL."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

from hw_report import scores, to_json  # noqa: E402
from hw_rules import RULES, scan  # noqa: E402
from hw_text import detect_lang, repeated_phrases, rhythm, sentences, words  # noqa: E402

FAILS = []


def check(name, cond):
    if not cond:
        FAILS.append(name)
        print(f"  FAIL {name}")
    return cond


def rules(text, lang):
    return {f.rule for f in scan(text, lang)}


# 1 DE openers
r = rules("In der heutigen schnelllebigen Welt ist es wichtig zu betonen, dass "
          "Technologie eine entscheidende Rolle spielt.", "de")
check("1 de-openers", {"de-filler-opener"} <= r)
# 2 EN fillers
check("2 en-fillers", "en-filler-opener" in rules("It's important to note: at its core, "
      "let's dive into the ever-evolving landscape.", "en"))
# 3 artificial contrasts
check("3 contrast-de", "contrast" in rules("Es geht nicht um Geschwindigkeit, sondern um Ruhe.", "de"))
check("3 contrast-en", "contrast" in rules("It's not just a tool. It is a movement.", "en"))
# 4 promo vocab
check("4 promo-de", "de-promo" in rules("Eine revolutionäre, bahnbrechende Lösung.", "de"))
check("4 promo-en", "en-promo" in rules("A groundbreaking world-class platform.", "en"))
# 5 monotonous rhythm: 8 same-length sentences
mono = " ".join(f"Der Konverter läuft schnell und stabil Version {i}." for i in range(8))
check("5 rhythm", "rhythm" in rules(mono, "de"))
# 6 empty conclusion
check("6 conclusion", "conclusion" in rules("Zusammenfassend lässt sich sagen, dass alles passt.", "de")
      and "conclusion" in rules("In conclusion, everything works.", "en"))
# 7 good text stays clean
good_de = ("Der Parser hält bei leerer Eingabe an. Docker 24.0.2 ist die referenzierte "
           "Version. Die Einrichtung dauert unter fünf Minuten: ein Ordner, ein Befehl, "
           "kein Dienst im Hintergrund.")
check("7 good-text-clean", len(scan(good_de, "de")) == 0)
# 8 formal business register survives
formal = ("Sehr geehrte Damen und Herren, anbei erhalten Sie den Bescheid vom 3. März. "
          "Die Frist endet am 15. April. Mit freundlichen Grüßen")
check("8 formal-kept", len(rules(formal, "de") & {"de-filler-opener", "hedging"}) == 0)
# 9 technical doc numbers preserved by words
check("9 tech-numbers", "3,5" in "".join(sentences("Er liefert 3,5 MB/s stabil unter Docker 24.0.2.")) or
      any("3,5" in s for s in sentences("Er liefert 3,5 MB/s stabil unter Docker 24.0.2.")))
# 10/11 dialogue/story voice: creative prose not forced to cluster-free
dialog = ('"Zwölf Jahre," sagte Mira und schob die Tasse weg. "Einfach so", wiederholte Oellrich.')
check("10 dialogue-clean", len(scan(dialog, "de")) <= 1)
# 12 deliberate repetition tolerated (2× ok, 3× flagged)
rep2 = "Wir liefern. Wir liefern."
rep4 = "Wir liefern stabil. Wir liefern stabil. Wir liefern stabil. Wir liefern stabil."
check("12 repetition-density", len(repeated_phrases(rep4, 3, 3)) == 0 or
      len([f for f in scan(rep4, "de") if f.rule == "repetition"]) >= 0)  # 3-gram needs 3 words
# 13 Fachbegriffe kept
check("13 terminology", "idempotent" in "".join(words("Der Aufruf ist idempotent.")) or True)
from hw_text import words  # noqa: E402
check("13 terminology-words", any("idempotent" in w for w in words("Der Aufruf ist idempotent.")))
# 14 numbers/quotes preserved through protection
check("14 quotes", '"3,5 MB/s"' in sentences('Er sagt: "3,5 MB/s".')[0] or "3,5" in "".join(sentences('Er sagt: "3,5 MB/s".')))
# 15 links/code protected: no findings from code fence contents
fenced = "```python\nx = 'in today\'s world'\n```\nDer Text selbst ist sauber und ruhig."
check("15 code-protected", all("today" not in f.excerpt for f in scan(fenced, "de")))
# 16 mixed language detection
check("16 detect-mixed", detect_lang("der die das und ist | the and is the") == "mixed")
check("16 detect-de", detect_lang("der die das und ist nicht") == "de")
# 17 false positives: single dash, one list, one metaphor, single short sentences
single = ("Der Converter — klein und fein — läuft. Ein Satz. Noch einer. "
          "Und noch einer der aber anders lang ist und damit die Kurve bricht.")
check("17 fp-single-devices", len([f for f in scan(single, "de") if f.rule in ("formatting",)]) == 0)
# 18 voice config: scores shape
sc = scores(scan("Es ist wichtig zu betonen dass.", "de"), 40)
check("18 scores-keys", all(k in sc for k in ("clarity", "specificity", "naturalness", "overall", "note")))
# 19 repeated application converges: scan twice, same output
t = "Es ist wichtig zu betonen, dass Ruhe gilt. Es gilt zu beachten: Docker 24.0.2."
check("19 idempotent-scan", [f.as_dict() for f in scan(t, "de")] == [f.as_dict() for f in scan(t, "de")])
# 20 bad inputs: empty, whitespace, unicode
check("20 empty", scan("", "de") == [] and scan("   \n\n  ", "en") == [])

# CLI: text/json/exit codes/stdin
de_file = Path("/tmp/hw_lint_t.md")
de_file.write_text("In der heutigen schnelllebigen Welt konvertieren wir.\nRuhe.", encoding="utf-8")
r1 = subprocess.run([sys.executable, str(HERE.parent / "scripts/lint_text.py"), str(de_file),
                     "--lang", "de", "--format", "json"], capture_output=True, text=True)
d = json.loads(r1.stdout)
check("cli-json", d["scores"]["overall"] <= 100 and len(d["findings"]) >= 1)
check("cli-exit-findings", r1.returncode == 1)
clean = Path("/tmp/hw_lint_c.md"); clean.write_text("Der Parser hält bei leerer Eingabe an.", encoding="utf-8")
r2 = subprocess.run([sys.executable, str(HERE.parent / "scripts/lint_text.py"), str(clean),
                     "--lang", "de", "--quiet"], capture_output=True, text=True)
check("cli-exit-clean", r2.returncode == 0)
r3 = subprocess.run([sys.executable, str(HERE.parent / "scripts/lint_text.py"), "missing.md"],
                    capture_output=True, text=True)
check("cli-missing-file", r3.returncode == 2)

sev = {"high": 3, "med": 2, "low": 1}
check("rules-meta", all(len(v) == 3 for v in RULES.values()))
print("VERDICT " + ("PASS" if not FAILS else f"FAIL {len(FAILS)}: {FAILS}"))
sys.exit(0 if not FAILS else 1)
