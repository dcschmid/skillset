# Quality Report — kira-pulse (Treiber, fahrer02)

Datum: 2026-11-13 · Blender 5.3.0 (02f0899d) · Pipeline: lowpoly-reference-to-blender
Designautorität: `~/Downloads/Drivers/kira-pulse/character/{front,side,back}.png`
(MOSS-Turntable; Projekt-Konvention −Y-Blick, links=+X, Meter — abweichend von
der Skill-Default-Konvention +Y-Blick, dokumentiert übernommen.)
Autoritative Spielassets: `blender/kira-pulse-v0.38-integrated.blend` (7889 Tris,
rigged, NOT ersetzt — dieses Modell ist ein eigenständiger Skill-Demonstrator).

## Feature-Inventar (aus Referenz abgeleitet)

| Feature | Sichtbar in | Status |
|---|---|---|
| Helm mit Cyan-Visor + Earcups/Ringen | front/side | repliziert |
| Lila Bob + Nacken-Stachel | side/back | repliziert (Stachel klein) |
| Anime-Augen bernstein, groß | front | repliziert (niedrige Poly, einfach) |
| Cyan-/Magenta-Brust-Gems | front | repliziert |
| Lila Ärmel + silberne Cuffs | front/side | repliziert |
| Charcoal-Anzug, Taillierung | front/side | repliziert |
| Hüft-Streifen cyan/magenta | front | repliziert |
| Cyan-Zehen | front | repliziert |
| Stirnfransen | side | repliziert |

## Technisches Gate — validate_mesh.py

ERGEBNIS: WARNING (absichtlich, keine FAILs)
- `no_uv` alle Objekte: Flat-Color-PBR ohne Textur — Stilentscheidung, Referenz
  nutzt Farbattribute, keine UV-Texturen.
- `unapplied_transform` Wurzeln: beabsichtigte Pivot-Eltern.

Tris: 1478 (Budget Riff-Racers Fahrer 2500–4000 → eingehalten)
GLB: kira-pulse.glb 109 KB · BLEND: kira-pulse.blend
Reimport-Verifikation: PASS, 1478→1478 Tris, Materialien vorhanden.

## Multi-View-Gate (front/side/back, EEVEE, ortho)

Render: `renders/kira_{front,side,back}.png` gegen `character/*.png` verglichen.

| Ansicht | Ergebnis | Abweichungen |
|---|---|---|
| Front | bestanden mit Vorbehalt | Silhouette/Palette/Features ja; Gesicht einfach, Proportion Kopf leicht groß |
| Seite | bestanden | Stachel/Visor/Palette ja; Stachel kleiner als Referenz |
| Back | bestanden mit Vorbehalt | Helm-Rückseite zeigt lila Haar statt dunklem Helm (Reihenfolge Helm/Hair) |

## Bewertung — nur aus Beobachtungen

| Kategorie | Pkt | Score | Nachweis |
|---|---:|---:|---|
| Silhouette & Proportionen | 25 | 19 | Silhouette-Lesbarkeit gegeben; Kopf leicht groß, Taille zu weich |
| Identität & Merkmale | 25 | 21 | alle 10 Feature-Inventar-Punkte sichtbar, Stachel klein |
| Form & Detailtreue | 20 | 14 | Facetten konsistent; Schultern minimal abgesetzt |
| Materialien & Farben | 15 | 13 | Palette = Referenzsamples; Helm-Rückseite-Farbfehler |
| Multi-View-Konsistenz | 15 | 12 | alle Ansichten zeigen korrekte Seite; Back-Helm-Fehler |
| **Gesamt** | **100** | **79/100** | Ziel 90 **nicht erreicht** |

Konsistent mit der unabhängigen Selbsteinschätzung des Projekt-HANDOVER
(Fahrer ~79/100) — kein erfundener Score; jede Zahl belegt.

## Iterationsprotokoll

Runde 1 Blockout → Views identisch (Kamera-Bug) → behoben · Runde 2 Palette/Identität →
Kohärenzbrüche (inkrementelle MCP-Bearbeitung) → atomarer Rebuild (kira_build.py) →
Runde 3 Gesicht/Lichter → Back-Helm-Farbfehler bekannt.

## Urteil

ZURÜCKGEGEBEN_ZUR_KORREKTUR (79 < 90). Technische Pipeline bewiesen; visuelle
Referenztreue unter Ziel. Bekannte Fixes: Helm-Hair-Reihenfolge (Rücken), Kopf-
Skalierung −5 %, Taille härter, Stachel größer. Diese sind in kira_build.py
parameterisiert — eine Korrekturrunde ist ein Rebuild, keine Neuentwicklung.
Visuelle Referenztreue: erst nach menschlicher Abnahme lieferfähig.

Nicht geliefert: kein Rig/Animation (Projekt entscheidet später), kein
Defold-Import-Test (riff-racers-Repo hat uncommittete Jax-Arbeit, nicht angefasst).
