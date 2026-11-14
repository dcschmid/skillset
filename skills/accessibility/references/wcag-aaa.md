# WCAG 2.2 AAA — extended quality tier

AAA is a quality goal, reported separately. Rules:
1. AAA findings NEVER mask AA status; reports show two blocks.
2. Never claim "AAA conformant" — claim per-criterion states:
   **satisfied / violated / not-applicable / needs-manual-review** (all 13
   AAA web SC below must each carry one).
3. Gate stays AA by default; `--strict-aaa` opts into AAA blocking.

## The AAA criteria a web project reports

| SC | Requirement (short) | Dev check |
|---|---|---|
| 1.2.6 Sign Language | prerecorded video has sign language | content decision |
| 1.2.7 Extended Audio Description | >8 s pauses or separate track | media pipeline |
| 1.2.8 Media Alternative | text alternative for all prerecorded media | transcript pipeline |
| 1.2.9 Audio-only Live | live text of live audio | live-caption infra |
| 1.4.6 Contrast Enhanced | 7:1 body, 4.5:1 large | tool: `color-contrast-enhanced` (off by default; `--level aaa` enables) |
| 1.4.7 Low or No Background Audio | ≤20 dB for prerecorded speech | audio mastering |
| 1.4.8 Visual Presentation | user-controlled text block/spacing/wrap | CSS + user prefs |
| 2.4.5 Multiple Ways | ≥2 navigation routes | sitemap+nav audit |
| 2.5.5 Target Size | ≥44×44 px | touch UIs; `target-size` covers AA 24 px |
| 3.1.5 Reading Level | supplementary summaries | content process |
| 3.1.6 Pronunciation | ruby/description for ambiguous | CJK/education UIs |
| 2.4.12 Focus Not Obscured (Enhanced) | focus never covered | 2.4.11 tests, stricter |
| 2.4.13 Focus Appearance | ≥2 px ring, 3:1 contrast | design tokens |
| 3.3.9 (2.2 addition, AAA? no — note) | — | 3.3.8 is AA; no AAA auth addition in 2.2 |

(AAA SC count differs across specs; report only what applies to YOUR content.
EN 301 549 mandates no AAA for public-sector web except where procurement says so.)

## Progress report template (per route)

```
SC 1.4.6  satisfied      7.2:1 measured (tool)
SC 1.4.7  N/A            no speech audio
SC 2.4.5  review         needs human route check
SC 2.5.5  violated       mobile targets 36 px (touch spec wants 44)
```

## When to chase AAA

Public content/reading-first sites (Astro docs, blogs) yes. Dense app
dashboards: evaluate cost/benefit — AAA media SC usually out of scope for
non-media apps (mark NOT APPLICABLE, not silent). AAA NEVER releases instead
of AA: an AAA-only report with open AA items is FAIL.
