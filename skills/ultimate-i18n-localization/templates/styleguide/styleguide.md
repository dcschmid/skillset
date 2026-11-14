# Localization styleguide (seed — copy into the project, edit per product)

## per-locale defaults
- de: Sie (formal) unless product is casual; dates TT.MM.JJJJ; 1.234,56
- en-US: dates MM/DD/JJJJ, 1,234.56; en-GB: DD/MM/JJJJ
- register fixed per locale before first translation, not per string

## UI text
- buttons: imperative, shortest correct verb; no trailing period
- errors: what happened + what to do; translate full sentences, never fragments
- keep placeholders ({name}) byte-identical across locales; no concatenation
  of translated fragments — one key per full sentence

## workflow
mt output = draft; human review flips reviewed→approved; legal/safety text
needs sign-off. Stale = source hash changed; re-translate, don't hand-patch.
