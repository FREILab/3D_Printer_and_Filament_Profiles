# Plan: Druckgeschwindigkeit / Volumetric Speed optimieren

Stand: 2026-08-03, bezieht sich auf `2026-07-23/filament/*.ini`

## Ausgangslage

`filament_max_volumetric_speed` ist der entscheidende Hebel für die
Druckgeschwindigkeit (er begrenzt, wie schnell die Düse Material aufschmelzen
kann — alle anderen Speed-Einstellungen im Druckprofil sind meist großzügiger
und greifen selten als echtes Limit). Bei der Konsistenzprüfung hat sich
gezeigt, dass diese Werte sehr unterschiedliche Herkunft/Vertrauenswürdigkeit
haben:

| Profil | Wert (mm³/s) | Herkunft |
|---|---|---|
| PLA (MK3) | 15 | Herstellerangabe dasfilament |
| PLA non-HF (MK4S) | 15 | Herstellerangabe dasfilament |
| PLA non-HF (XL) 0.4mm | 15 | Herstellerangabe (übernommen, nicht auf XL getestet) |
| PLA non-HF 0.6mm (XL) | 15.5 | Prusa-System-Default für 0.6mm, ungetestet |
| **PLA HF (MK4S)** | **21** | **experimentell ermittelt, wenig Beschwerden ✅** |
| PLA HF (XL) 0.4mm | 21 | von MK4S übernommen, nicht separat auf XL getestet |
| PLA HF 0.6mm (XL) | 30 | Prusa-System-Default, ungetestet |
| PETG (MK3) | 8 | uralt (2019), nie neu geprüft |
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

## Testmethode: Pile-Test (CNC Kitchen-Methode)

PrusaSlicer hat **keinen** eingebauten Volumetric-Speed-Testkörper (das
gelegentlich kursierende "Rechtsklick auf die Platte → Add Volumetric speed
test" existiert in unserer Version nicht — das zugehörige Feature wurde nur
als offener, nie gemergter PR #15322 vorgeschlagen). Statt eines Testkörpers
verwenden wir die "Pile"-Methode von CNC Kitchen
([Blogpost](https://www.cnckitchen.com/blog/flow-rate-benchmarking-of-a-hotend)):
An einer festen Position wird ohne XY-Bewegung eine definierte Filamentlänge
am Stück bei einer festen Ziel-Flussrate extrudiert (Dutzende Sekunden statt
weniger Sekunden), danach zur nächsten Position mit höherer Flussrate
weitergefahren. Das bildet den Wärmestau bei anhaltend hoher Flussrate ab —
genau das Szenario, das bei langen Infill-Bahnen in großen Objekten zu
Extruder-Skipping führt, bei kurzen Testkörpern aber oft nicht auffällt.

1. Fertiges G-Code-File aus `tools/` verwenden (siehe Tabelle unten) — kein
   Slicing nötig, keine Konsole/API nötig. Datei genau wie einen normalen
   Druckjob hochladen (PrusaLink-Weboberfläche, USB) und starten.
2. Der Druck heizt nur die Düse (kein Bett, kein Mesh-Leveling — beides
   unnötig für diesen Test, siehe unten) und fährt dann automatisch und
   **unbeaufsichtigt** ein Positionsraster ab. Nach jedem Pile bricht ein
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

Bett und Mesh-Leveling sind bewusst weggelassen: Piles brauchen keine
Betthaftung, und ein Mesh-Probe auf kaltem Bett lieferte in der Praxis
falsche Kompensationsdaten, wodurch die Düse viel zu tief fuhr. Stattdessen
wird auf fester, sicher hoher Z-Höhe (4mm) ohne Kompensation extrudiert.

Alle Testdateien laufen mit demselben Flussbereich **6–48 mm³/s in 15
Schritten à 3 mm³/s** (1500mm Filament pro Pile, ≈3.5–4g je nach Material),
unabhängig vom aktuell im Profil stehenden Wert — damit sind Ergebnisse
zwischen Materialien direkt vergleichbar. Die Pile-Länge ist bewusst so
gewählt, dass sich jeder Blob auf einer haushaltsüblichen Feinwaage
(0.1g-Auflösung) noch mit ca. 3% Genauigkeit wiegen lässt (500mm/~1.5g wäre
zu ungenau gewesen). Gesamtlaufzeit pro Datei dadurch ca. 45–50 Minuten
(unbeaufsichtigt). Ausnahme: TPU (0.75–2.5 mm³/s in acht 0.25er-Schritten,
100mm-Piles) — dort bleibt die Beurteilung visuell/akustisch, da eine
wägbare Masse bei diesen Flussraten unpraktikabel lange Extrusionszeiten
bräuchte.

Erzeugt werden die Dateien mit [tools/generate_flow_rate_test.py](tools/generate_flow_rate_test.py)
(jede Datei enthält als Kommentar im Kopf den genauen Aufruf, mit dem sie
erzeugt wurde — für abweichende Materialien/Flussbereiche/Drucker einfach
das Skript mit anderen Parametern erneut aufrufen).

| Datei | Drucker-Dialekt | Düsentemp |
|---|---|---|
| `tools/flow_test_PLA_HF_0.4mm.gcode` | XL | 220°C |
| `tools/flow_test_PETG_HF_0.4mm.gcode` | XL | 245°C |
| `tools/flow_test_PETG_nonHF_0.4mm.gcode` | single (MK4S) | 245°C |
| `tools/flow_test_PLA_nonHF_0.4mm.gcode` | single (MK4S) | 220°C |
| `tools/flow_test_GreenTEC_PRO_0.4mm.gcode` | single (MK4S) | 220°C |
| `tools/flow_test_PLA_MK3.gcode` | legacy (MK3S) | 210°C |
| `tools/flow_test_PETG_MK3.gcode` | legacy (MK3S) | 240°C |
| `tools/flow_test_PLA_HF_0.6mm.gcode` | XL | 220°C |
| `tools/flow_test_PETG_HF_0.6mm.gcode` | XL | 240°C |
| `tools/flow_test_PETG_nonHF_0.6mm.gcode` | XL | 240°C |
| `tools/flow_test_PLA_nonHF_0.6mm.gcode` | XL | 220°C |
| `tools/flow_test_TPU_XL.gcode` | XL | 230°C |

TPU (MK3/MK4S) ist nicht dabei — laut Tabelle oben bereits am Testturm
verifiziert (✅, 1.5 mm³/s), kein erneuter Test nötig.

Temperaturen/Bett-Werte in allen Dateien stammen aus den `FREILab *.ini`-Profilen
und gelten für **Das Filament**-PLA/-PETG (`filament_vendor = Das Filament`),
nicht für generisches PLA/PETG oder Prusament — bei Wechsel des
Filamentherstellers müssen Temp/Bett neu aus dem jeweiligen Profil übernommen
und die Dateien neu generiert werden.

## Priorisierte Testreihenfolge

**Hohe Priorität** (Werte, die aktuell unbegründet hoch *oder* unbegründet
niedrig sein könnten, direkte Auswirkung auf Alltag):
1. `PETG HF (MK4S)` / `PETG HF (XL)` — 22 mm³/s ist ein reiner Prusa-Systemwert
   für generisches PETG, nie für dasfilament-PETG verifiziert. Meistgenutztes
   Material auf dem meistgenutzten Drucker.
2. `PETG non-HF (MK4S)` — gerade erst (grob) von der XL übernommen, verdient
   eigene Verifikation auf der MK4S-Hardware.
3. `PLA HF (XL)` 0.4mm — von MK4S übernommener Wert (21), auf der XL bisher
   nicht separat bestätigt.
4. `TPU (XL)` — 2.0 ist nur eine Annahme („Nextruder ist stärker"), noch nicht
   verifiziert. Bei Rutschen/Clicking sofort wieder senken.

**Mittlere Priorität** (0.6mm-Düsen-Varianten, seltener genutzt, aber große
Sprünge zum 0.4mm-Wert):
5. `PLA HF 0.6mm (XL)` (30), `PETG HF 0.6mm (XL)` (33), `PETG non-HF 0.6mm (XL)` (17)

**Niedrige Priorität** (alte/konservative Werte, eher zu niedrig als
riskant — hier bringt Testen Zeitersparnis, aber kein Sicherheitsrisiko):
6. `PETG (MK3)` — 8 mm³/s ist vermutlich veraltet und unnötig konservativ
   für die heutige MK3S-Hardware.
7. `GreenTEC PRO (MK4S)` — Wert unbekannter Herkunft, generell eher
   langsameres Material, aber ungeprüft.

## Ergebnisse

| Datum | Profil | Getestet | Ergebnis | Schlussfolgerung |
|---|---|---|---|---|
| 2026-08-29 | PETG (MK3) | `tools/flow_test_PETG_MK3.gcode`, alle 15 Stufen 6–48 mm³/s | Kein Skipping/Rattern über den gesamten Bereich | Aktueller Wert (8) ist deutlich zu konservativ. Echte Obergrenze liegt über 48 mm³/s (Testbereich ausgeschöpft) — für einen belastbaren neuen `filament_max_volumetric_speed` müsste mit höherem `--flow-start`/`--flow-count` erneut getestet werden, um die tatsächliche Grenze zu finden. Bis dahin nicht einfach auf 48 setzen (Sicherheitsmarge, ungetestete Zone). |

## Vorgehen

- Testtürme können nebenbei mitlaufen (kein Sonderslot nötig), am besten
  jeweils direkt nach einem regulären Druckjob auf dem entsprechenden Drucker.
- Ergebnisse zentral in dieser Datei oder direkt in den `.ini`-Notizen
  festhalten, damit klar bleibt, was schon verifiziert ist (✅) und was noch
  aus System-Defaults stammt.
- Nach Abschluss aller Tests: Tabelle oben aktualisieren, „Herkunft"-Spalte
  auf „getestet TT-JJJJ-MM-TT" setzen.
