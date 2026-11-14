# Voice profiles & calibration

Nine preset profiles (`assets/voice-profile.template.md` fields): Natural,
Professional, Casual, Technical, Editorial, Storytelling, Dialogue,
Marketing, Minimal. Each carries: language + variant, audience, tone,
formality, rhythm, density, vocabulary, humor, quirks, preferred phrasings,
banned phrasings, typical length, genre, goal.

## Calibration from user samples (Mode F)

1. Ask user for 2–4 texts they consider good (never invent samples).
2. Measure: sentence-length distribution, paragraph size, formality markers
   (Du/Sie, you/we), humor density, term choices, recurring openings/closers,
   punctuation habits (dash, ellipsis, exclamation), directness.
3. Write the profile with `assets/voice-profile.template.md`; mark each trait
   with evidence ("short sentences — median 11w across 3 samples") and note
   uncertainty. Do not store the samples themselves without asking.
4. Profiles beat style rules (priority list, SKILL.md). Linter never beats
   the profile.

## Priority (binding)

facts → intent → user instructions → voice profile → genre → style rules →
linter.

## Preset defaults when no profile and no samples

Natural: varied rhythm, direct verbs, concrete nouns, low hedging, no
booster adjectives. Professional adds fixed Du/Sie + structured close.
Technical strips metaphor; Marketing keeps concrete benefit per sentence;
Minimal halves sentence count and length. Never substitute one preset for a
measured voice silently — say which preset is in force.
