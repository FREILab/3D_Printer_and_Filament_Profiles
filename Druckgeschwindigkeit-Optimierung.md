# Plan: Druckgeschwindigkeit / Volumetric Speed optimieren

Stand: 2026-08-30, bezieht sich auf aktuelle `filament/*.ini` (Bettheizung seit 2026-08-30 aktiviert)

## Ausgangslage

`filament_max_volumetric_speed` ist der entscheidende Hebel für die
Druckgeschwindigkeit (er begrenzt, wie schnell die Düse Material aufschmelzen
kann — alle anderen Speed-Einstellungen im Druckprofil sind meist großzügiger
und greifen selten als echtes Limit). Bei der Konsistenzprüfung hat sich
gezeigt, dass diese Werte sehr unterschiedliche Herkunft/Vertrauenswürdigkeit
haben:

| Profil | Wert (mm³/s) | Herkunft |
|---|---|---|
| PLA (MK3) | ~~15~~ **7** | ~~Herstellerangabe~~ **per Pile-Test ermittelt 2026-08-30 ✅ (war deutlich zu hoch!)** |
| PLA non-HF (MK4S) | 15 | Herstellerangabe dasfilament |
| PLA non-HF (XL) 0.4mm | 15 | Herstellerangabe (übernommen, nicht auf XL getestet) |
| PLA non-HF 0.6mm (XL) | 15.5 | Prusa-System-Default für 0.6mm, ungetestet |
| **PLA HF (MK4S)** | **21** | **experimentell ermittelt, wenig Beschwerden ✅** |
| PLA HF (XL) 0.4mm | ~~21~~ **15** | ~~von MK4S übernommen~~ **per Pile-Test ermittelt 2026-09-09 ✅ (war zu hoch!)** |
| PLA HF 0.6mm (XL) | 30 | Prusa-System-Default, ungetestet |
| PETG (MK3) | ~~8~~ **10** | ~~uralt (2019)~~ **per Pile-Test ermittelt 2026-08-30 ✅** |
| PETG HF (MK4S) | 22 | Prusa-System-Default „Generic PETG", ungetestet |
| PETG non-HF (MK4S) | 9 | von XL non-HF übernommen (2026-08-03 neu gesplittet), ungetestet |
| PETG HF (XL) 0.4mm | 22 | Prusa-System-Default, ungetestet |
| PETG HF 0.6mm (XL) | 33 | Prusa-System-Default, ungetestet |
| PETG non-HF (XL) 0.4mm | 9 | Prusa-System-Default, ungetestet |
| PETG non-HF 0.6mm (XL) | 17 | Prusa-System-Default, ungetestet |
| GreenTEC PRO (MK4S) | 15 | unbekannt/übernommen |
| TPU (MK3-MK4S) | 1.5 | **per Testturm ermittelt, dokumentiert (U. Hornstein, 24.1.24) ✅** |
| TPU (XL) | 2.0 | 2026-08-03 auf Materialobergrenze gesetzt, noch nicht auf XL getestet |

Nur zwei Werte (PLA HF MK4S, TPU MK3/MK4S) sind nachweislich am eigenen
Testturm ermittelt. Der Rest sind entweder Herstellerangaben (grundsätzlich
vertrauenswürdig, aber konservativ) oder unveränderte Prusa-System-Presets
(reine Schätzwerte, die nie für euer tatsächliches Filament geprüft wurden).

## Ziel

Für jedes Material/Drucker/Düsen-Kombination einen **geprüften** statt
geschätzten `filament_max_volumetric_speed`-Wert hinterlegen — höher wo
möglich (kürzere Druckzeiten), niedriger wo nötig (Qualität/Stabilität).

## Testmethode: CNC-Kitchen Auto-Flow-Pattern

PrusaSlicer hat **keinen** eingebauten Volumetric-Speed-Testkörper (das
gelegentlich kursierende "Rechtsklick auf die Platte → Add Volumetric speed
test" existiert in unserer Version nicht — das zugehörige Feature wurde nur
als offener, nie gemergter PR #15322 vorgeschlagen). Statt eines Testkörpers
verwenden wir das klassische "Auto Flow Pattern" von CNC Kitchen / Stefan
Hermann, bekannt aus dem
[Printables-Referenzpaket](https://www.printables.com/model/160335-hotend-benchmark-test-g-codes/)
(Hintergrund zur Methode auch im
[CNC-Kitchen-Blogpost](https://www.cnckitchen.com/blog/flow-rate-benchmarking-of-a-hotend)):
An festen Gitterpositionen wird jeweils ohne XY-Bewegung eine definierte
Filamentlänge am Stück bei einer festen Ziel-Flussrate extrudiert (20s
Stabilisierungspause, Prime, Wipe, dann die eigentliche Extrusion),
danach zur nächsten Position mit höherer Flussrate weitergefahren. Das
bildet den Wärmestau bei anhaltend hoher Flussrate ab — genau das Szenario,
das bei langen Infill-Bahnen in großen Objekten zu Extruder-Skipping führt,
bei kurzen Testkörpern aber oft nicht auffällt.

**Hinweis:** Frühere Versionen dieses Dokuments beschrieben eine selbstgebaute
"Pile"-Methode (bewegter Kreis statt fixer Position, 1500mm/Pile, 15 Stufen
6–48 mm³/s). Diese wurde in Commit `2a43877` ("adopt cnc kitchen") zugunsten
des oben beschriebenen CNC-Kitchen-Musters verworfen — das Skript
(`--pattern cnc-kitchen`) ist jetzt der Standard, alle Dateien in `tools/`
sind bereits im neuen Format.

1. Fertiges G-Code-File aus `tools/` verwenden (siehe Tabelle unten) — kein
   Slicing nötig, keine Konsole/API nötig. Datei genau wie einen normalen
   Druckjob hochladen (PrusaLink-Weboberfläche, USB) und starten.
2. Der Druck heizt die Düse und das Bett (aktuell einheitlich **60°C** bei
   allen Dateien, siehe Tabelle unten — nicht materialspezifisch aus dem
   `.ini`-Profil übernommen) und fährt dann automatisch und
   **unbeaufsichtigt** ein Positionsraster ab (3 Spalten × 4 Zeilen, bis zu
   12 Piles). Kein Mesh-Leveling nötig. Nach jedem Pile bricht ein
   automatischer Kringel-Move (kleines Achteck, zurückgezogen) den Faden
   selbst ab, kein manuelles Eingreifen nötig.
3. Während/nach jeder Position: auf Klicken/Rattern am Extruder achten
   (Skipping) und den Blob anschauen (gleichmäßig rund + konstanter
   Durchmesser = ok; ausgefranst/dünner werdend/unterbrochen = beginnende
   Unterextrusion).
4. Höchste saubere Position notieren, **10–15 % Sicherheitsmarge** abziehen
   → das wird der neue `filament_max_volumetric_speed`.
5. Ergebnis in der jeweiligen `.ini` eintragen (Feld
   `filament_max_volumetric_speed`) und kurz dokumentieren (Datum, wer
   getestet hat) — am besten direkt im `filament_notes`-Feld, wie beim
   TPU-Profil schon gehandhabt.

Mesh-Leveling ist bewusst weggelassen: Ein Mesh-Probe auf kaltem Bett
lieferte in der Praxis falsche Kompensationsdaten, wodurch die Düse viel zu
tief fuhr. Stattdessen wird auf fester, sicher hoher Z-Höhe ohne
Kompensation extrudiert.

Alle Testdateien laufen aktuell mit demselben Flussbereich **6–27 mm³/s in
8 Schritten à 3 mm³/s** (200mm Filament pro Pile, ≈0.6g je Pile — auf einer
haushaltsüblichen Feinwaage mit 0.1g-Auflösung noch grob wägbar, siehe
[measurements/](measurements/)), unabhängig vom aktuell im Profil stehenden
Wert. Gesamtlaufzeit pro Datei dadurch deutlich kürzer als bei der alten
Pile-Methode, ca. 10–15 Minuten (unbeaufsichtigt).

**Bekanntes Problem — Flussbereich passt nicht für jedes Material:** Der
gemeinsame 6–27-Bereich in 3er-Schritten ist zu grob bzw. an der falschen
Stelle für Materialien, deren reale Grenze weit unter oder mitten im
Testbereich liegt:
- **MK3 (legacy):** PETG klickt bereits konsistent bei 15 mm³/s (siehe
  Ergebnisse unten) — 3er-Schritte sind zu grob, um die Schwelle zwischen 12
  und 15 einzugrenzen.
- **TPU (XL):** `flow_test_TPU_XL.gcode` nutzt aktuell denselben 6–27
  mm³/s-Bereich wie alle anderen Materialien. Die bisher angenommene
  Materialobergrenze liegt bei 1.5–2.0 mm³/s (siehe Tabelle oben) — der
  gesamte Testbereich läge damit weit über einer sinnvollen TPU-Flussrate.
  Vor einem TPU-Test auf der XL sollte die Datei mit einem passenden,
  niedrigeren `--flow-start`/`--flow-step` (z. B. 0.75–2.5 mm³/s in
  0.25er-Schritten, wie ursprünglich für TPU vorgesehen) neu erzeugt werden.

Erzeugt werden die Dateien mit [tools/generate_flow_rate_test.py](tools/generate_flow_rate_test.py)
(`--pattern cnc-kitchen`, jetzt Standard). Anders als beim alten Pile-Muster
schreibt der CNC-Kitchen-Generator den genauen Aufruf **nicht** als Kommentar
in die Datei — für abweichende Materialien/Flussbereiche/Drucker das Skript
mit den unten passenden `--dialect`/`--temp`/`--flow-*`-Parametern erneut
aufrufen (Werte siehe Tabelle, per `grep -E "Prusa |bedTemp|startFlow|flowOffset|flowSteps|startTemp" tools/flow_test_*.gcode` aus den bestehenden Dateien ablesbar).

Die Dateinamen enthalten seit der letzten Regenerierung den Drucker
(`flow_test_Drucker<N>_...`), um z. B. MK4S-0.4mm nicht mit XL-0.4mm zu
verwechseln — vollständige Zuordnung Drucker → Nozzle → Material inkl.
Generator-Parametern siehe [tools/flow_test_plan.txt](tools/flow_test_plan.txt).

| Datei | Drucker | Düsentemp | Bettheizung | Flussbereich |
|---|---|---|---|---|
| `tools/flow_test_Drucker1_PLA_HF_0.6mm.gcode` | Drucker 1 (MK3.5, 0.6mm, HF) | 220°C | 60°C | 6–27 mm³/s, 8×3er |
| `tools/flow_test_Drucker1_PETG_HF_0.6mm.gcode` | Drucker 1 (MK3.5, 0.6mm, HF) | 240°C | 80°C | 6–27 mm³/s, 8×3er |
| `tools/flow_test_Drucker2_PLA_HF_0.4mm.gcode` | Drucker 2 (MK4S, 0.4mm, HF) | 220°C | 60°C | 6–27 mm³/s, 8×3er |
| `tools/flow_test_Drucker2_PETG_HF_0.4mm.gcode` | Drucker 2 (MK4S, 0.4mm, HF) | 245°C | 80°C | 6–27 mm³/s, 8×3er |
| `tools/flow_test_Drucker2b_PLA_nonHF_0.4mm.gcode` | Drucker 2b (MK4S, 0.4mm, non-HF) | 220°C | 60°C | 6–27 mm³/s, 8×3er |
| `tools/flow_test_Drucker2b_PETG_nonHF_0.4mm.gcode` | Drucker 2b (MK4S, 0.4mm, non-HF) | 245°C | 80°C | 6–27 mm³/s, 8×3er |
| `tools/flow_test_Drucker2b_GreenTEC_PRO_0.4mm.gcode` | Drucker 2b (MK4S, 0.4mm, non-HF) | 220°C | 60°C | 6–27 mm³/s, 8×3er |
| `tools/flow_test_Drucker3_PLA_0.4mm.gcode` | Drucker 3 (MK3S, legacy) | 210°C | 60°C | 6–12 mm³/s, 4×2er (verfeinert nach MK3-PETG-Ergebnis) |
| `tools/flow_test_Drucker3_PETG_0.4mm.gcode` | Drucker 3 (MK3S, legacy) | 240°C | 80°C | 6–27 mm³/s, 8×3er (getestet, s. Ergebnisse — Auflösung zu grob) |
| `tools/flow_test_Drucker4_PLA_HF_0.4mm.gcode` | Drucker 4 (XL, Tool 0/1, 0.4mm HF) | 220°C | 60°C | 6–27 mm³/s, 8×3er |
| `tools/flow_test_Drucker4_PETG_HF_0.4mm.gcode` | Drucker 4 (XL, Tool 0/1, 0.4mm HF) | 245°C | 80°C | 6–27 mm³/s, 8×3er |
| `tools/flow_test_Drucker4_PLA_nonHF_0.4mm.gcode` | Drucker 4 (XL, Tool 2/3, 0.4mm non-HF) | 220°C | 60°C | 6–27 mm³/s, 8×3er |
| `tools/flow_test_Drucker4_PETG_nonHF_0.4mm.gcode` | Drucker 4 (XL, Tool 2/3, 0.4mm non-HF) | 240°C | 80°C | 6–27 mm³/s, 8×3er |
| `tools/flow_test_Drucker4_PLA_HF_0.6mm.gcode` | Drucker 4 (XL, 0.6mm Tausch-Düse) | 220°C | 60°C | 6–27 mm³/s, 8×3er |
| `tools/flow_test_Drucker4_PETG_HF_0.6mm.gcode` | Drucker 4 (XL, 0.6mm Tausch-Düse) | 240°C | 80°C | 6–27 mm³/s, 8×3er |
| `tools/flow_test_Drucker4_PLA_nonHF_0.6mm.gcode` | Drucker 4 (XL, 0.6mm Tausch-Düse) | 220°C | 60°C | 6–27 mm³/s, 8×3er |
| `tools/flow_test_Drucker4_PETG_nonHF_0.6mm.gcode` | Drucker 4 (XL, 0.6mm Tausch-Düse) | 240°C | 80°C | 6–27 mm³/s, 8×3er |
| `tools/flow_test_Drucker4_TPU_0.4mm.gcode` | Drucker 4 (XL, 0.4mm) | 230°C | unbeheizt | 6–27 mm³/s, 8×3er (⚠️ zu hoch für TPU, vor Nutzung neu generieren) |

TPU (MK3/MK4S) ist nicht dabei — laut Tabelle oben bereits am Testturm
verifiziert (✅, 1.5 mm³/s), kein erneuter Test nötig.

Werte oben aus den exakten `.ini`-Profilen übernommen (Stand 2026-09-09,
siehe [tools/flow_test_plan.txt](tools/flow_test_plan.txt) für die
Zuordnung Datei ↔ passendes `.ini`-Profil ↔ Drucker-Hardware, gegen
`printer/*.ini` und `filament/*.ini` geprüft). Vorher liefen alle Dateien
mit vereinheitlichten, gerundeten Werten (PLA 210°C, PETG 230°C, Bett
immer 60°C) — das führte auf der XL beim PLA-HF-Test zu Klicken während
des Prime-Moves, weil die echte Solltemperatur (220°C) nicht erreicht war.
Seit 2026-09-09 nutzt jede Datei die materialspezifische `.ini`-Temperatur
und -Betttemperatur. Bei Wechsel des Filamentherstellers oder Änderung der
`.ini`-Werte müssen die Dateien mit den passenden `--temp`/`--bed-temp`-Werten
neu
generiert werden.

## Priorisierte Testreihenfolge

**Hohe Priorität** (Werte, die aktuell unbegründet hoch *oder* unbegründet
niedrig sein könnten, direkte Auswirkung auf Alltag):
1. `PETG HF (MK4S)` / `PETG HF (XL)` — 22 mm³/s ist ein reiner Prusa-Systemwert
   für generisches PETG, nie für dasfilament-PETG verifiziert. Meistgenutztes
   Material auf dem meistgenutzten Drucker.
2. `PETG non-HF (MK4S)` — gerade erst (grob) von der XL übernommen, verdient
   eigene Verifikation auf der MK4S-Hardware.
3. ~~`PLA HF (XL)` 0.4mm~~ — ✅ erledigt 2026-09-09, neuer Wert 15 (siehe Ergebnisse).
4. `TPU (XL)` — 2.0 ist nur eine Annahme („Nextruder ist stärker"), noch nicht
   verifiziert. Bei Rutschen/Clicking sofort wieder senken.

**Mittlere Priorität** (0.6mm-Düsen-Varianten, seltener genutzt, aber große
Sprünge zum 0.4mm-Wert):
5. `PLA HF 0.6mm (XL)` (30), `PETG HF 0.6mm (XL)` (33), `PETG non-HF 0.6mm (XL)` (17)

**Niedrige Priorität** (alte/konservative Werte, eher zu niedrig als
riskant — hier bringt Testen Zeitersparnis, aber kein Sicherheitsrisiko):
6. ~~`PETG (MK3)`~~ — ✅ erledigt 2026-08-30, neuer Wert 10 (siehe Ergebnisse).
7. `GreenTEC PRO (MK4S)` — Wert unbekannter Herkunft, generell eher
   langsameres Material, aber ungeprüft.

**Nicht ursprünglich priorisiert, aber erledigt:**
8. ~~`PLA (MK3)`~~ — ✅ erledigt 2026-08-30, war fälschlich als "Herstellerangabe,
   vertrauenswürdig" eingestuft; tatsächlich deutlich zu hoch (15 → 7). Zeigt,
   dass auch Herstellerangaben nicht blind übernommen werden sollten.

## Ergebnisse

| Datum | Profil | Getestet | Ergebnis | Schlussfolgerung |
|---|---|---|---|---|
| ~~2026-08-29~~ | ~~PETG (MK3)~~ | ~~`tools/flow_test_PETG_MK3.gcode`, alle 15 Stufen 6–48 mm³/s~~ | ~~Kein Skipping/Rattern über den gesamten Bereich~~ | **Verworfen/falsch.** Die Datei nutzt für MK3 (legacy) tatsächlich das klassische CNC-Kitchen-Muster mit nur 8 Stufen 6–27 mm³/s (3er-Schritten), nicht 15 Stufen bis 48 — und wurde vor dem Dialect-Fix (Commit `5652ce0`) gelaufen. Ergebnis unten (2026-08-30) ersetzt diesen Eintrag. |
| 2026-08-30 | PETG (MK3) Schwarz | `tools/flow_test_PETG_MK3.gcode`, 3× Messreihe, Stufen 6–27 mm³/s (3er-Schritte) | Konsistent über alle 3 Messreihen: 6/9/12 mm³/s sauber (Masse 0,60–0,64 g je Pile), **15 mm³/s klickt + Massenabfall auf 0,58–0,59 g**, 18 mm³/s abgebrochen, 21–27 nicht erreicht. Massenabfall bestätigt die Klick-Beobachtung unabhängig von der (damals noch fehlerhaften) Live-Anzeige — siehe Display-Bug-Fix (Commit `2e776da`), betrifft aber nur die Live-Anzeige, nicht die Pile-Zuordnung der Gewichte. | **Ergebnis:** sauber bis 12, Grenze bei 15. Mit Sicherheitsmarge auf 12 abgezogen → **neuer `filament_max_volumetric_speed` = 10 mm³/s** (bisher 8). Bereits in `filament/FREILab PETG (MK3).ini` eingetragen (2026-08-30). |
| 2026-08-30 | PLA (MK3) Das Filament | 4 Messreihen: 1× `flow_test_PLA_MK3.gcode` (alt, 6–27 in 3er-Schritten, vor Display-Fix), 3× nach Verfeinerung auf 6–12 mm³/s in 2er-Schritten (nach Display-Fix, Commit `2e776da`) | Grobe Messreihe: 6/9 sauber, **12 mm³/s klickt** (Masse 0,52 g vs. ~0,60 g). Feine Messreihen: 6/8 mm³/s durchgehend sauber (0,59–0,62 g) in allen 3 Wiederholungen; bei **10 mm³/s** uneinheitlich — 1 von 3 Messreihen sauber (0,58 g), 2 von 3 klicken bereits (0,55–0,57 g); 12 mm³/s in den feinen Messreihen nicht mehr erreicht (abgebrochen). | **Ergebnis:** einzige durchgehend sichere Stufe ist 8 mm³/s, 10 mm³/s ist eine Grauzone (Mehrheit der Messungen zeigt bereits Unterextrusion). Alter Profilwert (15, Herstellerangabe) war **deutlich zu hoch** — real liegt die Grenze bei etwa einem Drittel davon. Mit Sicherheitsmarge unter der sauberen Stufe (8) → **neuer `filament_max_volumetric_speed` = 7 mm³/s** (bisher 15). Bereits in `filament/FREILab PLA (MK3).ini` eingetragen (2026-08-30). |
| 2026-09-09 | PLA HF (XL) Kopf1, metallic rot | `tools/flow_test_Drucker4_PLA_HF_0.4mm.gcode` (220°C, korrigierte .ini-Temp), 3× Messreihe, Stufen 6–27 mm³/s (3er-Schritte) — siehe `measurements/Drucker 4` | Messreihe 1 (⚠️ Waage stand auf dem Heizbett, driftete massiv — Massewerte nicht belastbar): 6–18 mm³/s liefen durch (0,55–0,62 g), 21 mm³/s klickt/abgebrochen. Messreihen 2+3 (Waage korrekt neben dem Bett): konsistent 6/9/12/15/18 mm³/s sauber (Masse 0,56–0,58 g), **21 mm³/s klickt in beiden Reihen, abgebrochen**. Klick-Grenze bei 21 mm³/s über alle 3 Reihen reproduziert. | **Ergebnis:** sauber bis 18, Grenze bei 21. Mit Sicherheitsmarge auf 18 abgezogen → **neuer `filament_max_volumetric_speed` = 15 mm³/s** (bisher 21, von MK4S übernommen). Bereits in `filament/FREILab PLA HF (XL).ini` eingetragen (2026-09-09). |

## Vorgehen

- Testtürme können nebenbei mitlaufen (kein Sonderslot nötig), am besten
  jeweils direkt nach einem regulären Druckjob auf dem entsprechenden Drucker.
- Ergebnisse zentral in dieser Datei oder direkt in den `.ini`-Notizen
  festhalten, damit klar bleibt, was schon verifiziert ist (✅) und was noch
  aus System-Defaults stammt.
- Nach Abschluss aller Tests: Tabelle oben aktualisieren, „Herkunft"-Spalte
  auf „getestet TT-JJJJ-MM-TT" setzen.
