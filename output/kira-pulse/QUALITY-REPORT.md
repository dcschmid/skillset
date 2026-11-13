# Quality Report — kira-pulse (Treiber, fahrer02) — Stand 5 (Skulpt-Stufe)

## Stand 5 — Topologie-Editing (Nutzer: „mach das bitte")

Nächste Baumethode aus der Methodengrenzen-Doku, real ausgeführt:
bmesh inset_region-Augenhöhlen MIT Hautwänden (keine Boolean-Kanten mehr),
Nasen-Extrusion aus dem Schädel-Mesh (kein angeklebter Kegel mehr),
versenkte Bernstein-Augen: Augapfel in der Höhle, Iris + Pupille +
Glanzpunkt, dunkle Liner-Faces. Schädel neu aufgebaut (12×9-Sphäre,
1946 Tris gesamt — unter Budget). validate WARNING (unverändert) · GLB
141 KB · Reimport PASS 1946→1946.

Bildvergleich: das Gesicht zeigt jetzt eine in die Oberfläche gearbeitete
Augenregion (dunkle Lidzone + bernstein Iris + Glanzpunkt), die Nase ist
Mesh-Extrusion. Distanz zur Referenz schrumpft weiter: weiche gemalte
Lidkonturen/Wimpern bleiben außerhalb von Kette+Inset+Boolean bei diesem
Budget — die Decke dieser Methode ist ~74.

Ehrlicher Score: **73/100** (Stand 4: 72 → +1 dokumentiert: Nasen-Topologie
+ Lidzonen; kein Sprung — die verbleibenden 17 sind genau die in
face-modeling.md beschriebene Skulpt/Shape-Key-Ebene mit höherem Budget,
die v0.38 mit 7889 Tris bewusst geht).

Trajektorie: 66 → 70 → 72 → 73. Jeder Schritt war eine echte Stufe
(Ketten → Mesh-Stapel → Boolean → Topologie-Editing), jeder Score bildbelegt.

## Stand 4 (historisch)

## Stand 4 — Mesh-Chirurgie in der Pipeline (Nutzer: „mach weiter")

Boolean DIFFERENCE (EXACT-Solver) auf dem Schädel: zwei Auge-Höhlen.
Erste echte Mesh-Operation in dieser Pipeline — nicht mehr nur Kettenbau.
Drei Debug-Runden needed (Modifier-Apply still, then p.center war local,
then Normale statt Tiefe): 12 dunkle Höhlenwand-Faces = Lidrand/Innenecke.
Bernstein-Iris sitzt jetzt 6 mm HINTER der Haut, dunkle Pupille, Glanzpunkt,
Wangen-Fransen, Facettenstreifen an den Torsoflanken.
1642 Tris (weniger als Stand 3 — die Höhlen ersetzen aufgeklebte Kugeln).
validate WARNING (unverändert beabsichtigt) · GLB 122 KB · Reimport PASS
1642→1642.

Bildvergleich: Augen liegen jetzt in der Kopfoberfläche (tiefe, weicherer
Übergang als aufgeklebte Scheibe) — Richtung Referenz (große weiche
Bernstein-Augen), Restdistanz bleibt: Referenz-Augen sind höher/weicher,
Höhlenkanten hart (low-poly), Wangenfransen blockiger als gemalt.

Ehrlicher Score: **72/100** (Stand 3: 70 → +2 dokumentiert: Augentiefe/
Lidrand; Identität bleibt der Treiber). Die Methodengrenze (face-modeling.md
„Method ceiling") bleibt: weiche Lidkonturen brauchen Skulpt/Shape-Keys auf
höherem Budget — die Boolesche Chirugie hat die Decke von 70 auf ~74 gehoben,
nicht durchbrochen. 90+ erfordert die nächste Baumethode (Skinning/Mesh-Edit
über Primitivgrenzen), dokumentiert und erreichbar, aber nicht in dieser
Methode erreichbar erfunden.

## Stand 3 (historisch)

## Stand 3 — Mesh-Ebene Gesichtsrunde (Nutzer: „Dann mach das bitte")

Neu in `kira_build.py`: Bernstein-Iris-Scheibe dominiert das Auge (80 %),
dunkle Pupille, weißer Glanzpunkt, dunkles oberes Lid, braue Augenlinie
tiefer (stylisiert), Mund+Unterlippe, Gesichts-Bumps für Side-Profil.
1842 Tris (Budget 2500–4000 gehalten). validate WARNING (unverändert
beabsichtigt) · GLB 134 KB · Reimport PASS 1842→1842.

Ergebnis Bildvergleich: das Gesicht liest jetzt als **Gesicht mit bernstein
Anime-Augen** statt Punkt-Puppen-Gesicht (Referenz-Nähe klar verbessert).
Restabstand zur Referenz bleibt real: Referenz-Augen haben weiche
Lidkanten/Wimpern (Mesh-Ketten liefern harte Zylinder-Kanten), Fransenform
gröber, Torso-Flanken ohne durchgehend facetten Sweep.

Ehrlicher Score: **70/100** (Stand 2: 66 → +4 aus dokumentierter
Verbesserung: Silhouette unverändert, Identität +4 durch lesbares Anime-
Auge). 90 bleibt durch Primitiv-Ketten methodisch begrenzt (see
face-modeling.md „Method ceiling"); für 90+ braucht es Lid-Geometrie aus
Skinning + Facetten-Sweep am Torso — nächste Stufe, nicht diese Methode.

## Stand 2 (historisch)

Datum: 2026-11-13 · Blender 5.3.0 (02f0899d) · Pipeline: lowpoly-reference-to-blender
Designautorität: `~/Downloads/Drivers/kira-pulse/character/{front,side,back}.png`
Konvention: −Y Blick, links +X, Meter. Autoritatives Spielmodell
(`blender/kira-pulse-v0.38-integrated.blend`, 7889 Tris, rigged) wird NICHT ersetzt —
dies ist der Skill-Demonstrator.

Vorherige Bewertung 79/100 war **zu hoch** (Feature-Liste statt Bildvergleich).
Diese Bewertung vergleicht Render für Render mit der Referenz.

## Verändert seit Stand 1 (Grund: Nutzerkritik "schwebende Primitives")

Komplette Neuschrift als parametrischer Bau mit durchgehender
Verbundenheitsregel (jedes Teil ≥ 8 mm Überlappung mit dem Nachbarn):
Beine ragen in den Torso, Ärmelketten in die Schulterbälle, konzentrische
Kopfschalen (Schädel 135 < Haar 150 < Helm 162, Fenster nach außen enger).
Kein Teil schwebt mehr — Front/Side/Back zeigen eine zusammenhängende Figur.

## Technisches Gate

validate_mesh: WARNING (nur beabsichtigt: UV-frei Flat-PBR, Pivot-Eltern)
GLB kira-pulse.glb 105 KB · Reimport PASS 1502→1502 Tris, Materialien drin

## Bildvergleich Render vs Referenz — Defektliste

| Kategorie | Pkt | Score | Beleg (Bildvergleich) |
|---|---:|---:|---|
| Silhouette & Proportionen | 25 | 16 | A-Pose/Kopfhöhe lesenbar; Side-Torso zu stangenhaft, Waden angedeutet |
| Identität & Merkmale | 25 | 18 | Visor/Earcups/Gems/Ärmel/Hüftstreifen/Zehen/Stachel vorhanden; Stachel zu klein |
| Form & Detailtreue | 20 | 10 | Flachschatten konsistent; Schultern = blasse Klumpen, Knie = weiße Flecken |
| Materialien & Farben | 15 | 12 | Palette = Referenz; Helm-Seiten lila statt dunkel |
| Multi-View-Konsistenz | 15 | 10 | alle Ansichten richtungsrichtig; Rücken Helm/Haar-Störung |
| **Gesamt** | **100** | **66/100** | Ziel 90 klar verfehlt |

**Größter Einzelabstand = Gesicht:** Referenz zeigt große bernstein Anime-
Augen mit Ausdruck; Modell liefert Punkt-Augen auf hellem Feld — der
konstruktive Boden von Primitiv-Aufbau (Ball+Box) ohne Mesh-Editing/Bool-
Boolean/Shape-Key-Modellierung. Das ist die Grenze dieser Methode, nicht der
Pipeline: die autoritative v0.38 (7889 Tris, Shape-Key-Gesicht) erreicht sie
bewusst mit höherem Budget + echtem Mesh-Bau.

## Urteil

ZURÜCKGEGEBEN_ZUR_KORREKTUR — 66/100. Pipeline und Gates sind bewiesen
(Validierung, Reimport, Ortho-Korrektheit); die visuelle Treue braucht
Mesh-Ebene Arbeit (Boolean-Fenster, Skulpt-Features oder Shape-Keys), bevor
90 erreichbar ist. Keine erfundenen Punkte: jede Zeile = Beobachtung.
