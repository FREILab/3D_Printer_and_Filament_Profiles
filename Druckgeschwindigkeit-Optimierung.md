# Flussraten, Profile und Testskripte

Stand: 2026-11-07

`filament_max_volumetric_speed` (mm³/s) ist der entscheidende Hebel für die
Druckzeit — er begrenzt, wie schnell die Düse Material aufschmelzen kann. Alle
anderen Speed-Einstellungen im Druckprofil sind großzügiger und greifen selten
als echtes Limit. Ziel ist für jede Drucker-/Düsen-/Material-Kombination ein
**gemessener** statt geschätzter Wert.

Zwei Dinge, die bei jeder Zahl hier mitzudenken sind:

- Ein mvs-Wert gilt **nur für die Temperatur, bei der er gemessen wurde.**
  Belegt am 2026-11-07: PLA HF auf der XL war bei 220 °C bis 18 mm³/s sauber
  und riss bei 21 ab — bei 225 °C sauber bis 21, Abriss erst bei 23. +5 K
  haben die Decke um ~17 % gehoben.
- Ein geänderter Wert im Repo ist **nicht** auf den Druckern. PrusaSlicer und
  die hochgeladenen `.gcode`-Dateien müssen aktualisiert werden, sonst wird
  weiter mit dem alten Stand gedruckt. Das ist hier schon zweimal passiert.

Rohdaten aller Messreihen: [measurements/](measurements/) (eine Datei je
Drucker, Gewichte je Pile).

---

## 1. Flussraten je Drucker

Legende: ✅ am eigenen Material gemessen · ⚠️ geschätzt/übernommen, ungetestet
· ⛔ kein Profil vorhanden oder nicht zugelassen

**TPU nur auf Druckern ohne HF-Düse.** Zugelassen sind damit Drucker 2b und
Drucker 3 sowie die Tools 2+3 der XL. Durchgesetzt wird das über
`compatible_printers_condition`: `! nozzle_high_flow[0]` beim
MK3-/MK4S-Profil, `printer_notes!~/.*HF_NOZZLE.*/` beim XL-Profil. Eine
Einschränkung bleibt: auf der XL hängt die Bedingung am *Druckerprofil*, nicht
am einzelnen Tool — in `Drucker 4 - non-HF` sind Tool 0+1 trotzdem als HF
deklariert (`nozzle_high_flow = 1,1,0,0,0`). PrusaSlicer kann Filamentprofile
nicht pro Tool einschränken, hier muss man also beim Zuweisen aufpassen.

### Drucker 1 — Prusa MK3.5, 0.6 mm

Prusa bietet für die MK3.5 **keine** HF-Varianten an (weder Filament- noch
Druckerprofile). `nozzle_high_flow = 1` in `printer/Drucker 1` ist eine lokale
Setzung — die PLA-/PETG-Profile dieser Maschine unterscheiden deshalb nicht
nach HF. Wirkung hat die Setzung trotzdem: sie ist es, die TPU hier
ausschließt.

| Material | Wert | Status |
|---|---|---|
| PLA | ⚠️ 15 @220 °C | ungetestet, Prusa-Systemwert. Profil neu seit 2026-11-07. Testdatei bereit (9–25) |
| PETG | ⚠️ 14 @240 °C | ungetestet, Prusa-Systemwert. Profil neu seit 2026-11-07. Testdatei bereit (8–24) |
| TPU V2 | ⛔ | **nicht zugelassen** — auf HF-Düsen wird kein TPU gedruckt (Vorgabe FREILab). Profilbedingung seit 2026-11-07 entsprechend eingeengt |
| GreenTEC PRO | ⛔ | kein Profil — die Bedingung des GreenTEC-Profils trifft nur MK4-Modelle ohne HF-Düse |

### Drucker 2 — Prusa MK4S, 0.4 mm, HF-Hotend

| Material | Wert | Status |
|---|---|---|
| PETG HF | ✅ 20 @245 °C | gemessen 2026-11-07, 3× (melonengelb). Sauber bis 21, Massenabfall bei 24, Abriss bei 27. **Feinmessung 22–26 offen** |
| PLA HF | ⚠️ 21 @220 °C | nie am Pile-Test verifiziert, nur „experimentell ermittelt, wenig Beschwerden". Testdatei bereit (6–27). Offen: ob auch hier 225 °C sinnvoll sind (auf der XL +17 % Durchsatz) |
| TPU V2 | ⛔ | **nicht zugelassen** — HF-Düse, siehe Drucker 1 |
| GreenTEC PRO | ⛔ | kein Profil — Bedingung schließt HF-Düsen aus, nur auf Drucker 2b |

### Drucker 2b — Prusa MK4S, 0.4 mm, Standard-Hotend

| Material | Wert | Status |
|---|---|---|
| PLA non-HF | ⚠️ 15 @220 °C | Herstellerangabe dasfilament, ungetestet. Testdatei bereit (6–27) |
| PETG non-HF | ⚠️ 9 @245 °C | 2026-08-03 von der XL übernommen, ungetestet. Testdatei bereit (6–27) |
| GreenTEC PRO | ⚠️ 15 @220 °C | Herkunft unbekannt, ungetestet. Testdatei bereit (6–27) |
| TPU V2 | ✅ 1.5 @230 °C | Testturm-Wert. Einer von zwei Druckern, auf denen TPU überhaupt zugelassen ist |

### Drucker 3 — Prusa MK3S, 0.4 mm

| Material | Wert | Status |
|---|---|---|
| PETG | ✅ 12 @240 °C | zwei Messungen mit **widersprüchlichem** Ergebnis, 12 trägt beide. Schwarz (2026-08-30, Bett 60): Abriss bei 15. Weiß (2026-11-07, Bett 80): kein Klicken bis 16, Decke nicht erreicht. **Offen:** weiß nach oben (16–24) und schwarz bei Bett 80 wiederholen |
| PLA | ✅ 7 @210 °C | gemessen 2026-08-30, 4 Messreihen. Sauber bis 8, Grauzone bei 10 (1 von 3 sauber). Feinmessung 8–11 möglich, bringt aber max. 1 mm³/s |
| TPU V2 | ✅ 1.5 @230 °C | Testturm-Wert, Originalhardware |

### Drucker 4 — Prusa XL 5T

**Tool 0+1 — 0.4 mm, HF-Hotend**

| Material | Wert | Status |
|---|---|---|
| PLA HF | ✅ 21 @225 °C | gemessen 2026-11-07, 3× (Kopf 1, metallic rot). Sauber bis 21, Massenabfall bei 22, Abriss bei 23. Zusätzlich im Realdruck bestätigt. Marge nur eine Stufe — 20 wäre konservativ |
| PETG HF | ✅ 18 @245 °C | gemessen 2026-09-09, 3× (Rubinrot). Sauber bis 21, Abriss bei 24. Nebenbefund: die MK4S hat bei gleichem Muster 20 bekommen — Feinmessung 22–26 könnte hier ebenfalls heben |

**Tool 2+3 — 0.4 mm, Standard-Hotend**

| Material | Wert | Status |
|---|---|---|
| PLA non-HF | ⚠️ 15 @225 °C | Herstellerangabe, nie auf der XL getestet. Testdatei bereit (6–27) |
| PETG non-HF | ⚠️ 9 @240 °C | Prusa-Systemwert, ungetestet. Testdatei bereit (6–27) |
| TPU V2 | ⚠️ 2.0 @230 °C | reine Annahme („Nextruder ist stärker"), ungetestet. Testdatei bereit (0.75–2.5). Nur unter dem Druckerprofil `Drucker 4 - non-HF` auswählbar |

**0.6 mm — manueller Düsentausch, kein fester Tool-Slot**

| Material | Wert | Status |
|---|---|---|
| PETG HF 0.6 | ⚠️ 33 @240 °C | Prusa-Systemwert, ungetestet. Testdatei bereit (6–27) |
| PLA HF 0.6 | ⚠️ 30 @225 °C | Prusa-Systemwert, ungetestet. Testdatei bereit (15–36) |
| PETG non-HF 0.6 | ⚠️ 17 @240 °C | Prusa-Systemwert, ungetestet. Testdatei bereit (6–27) |
| PLA non-HF 0.6 | ⚠️ 15.5 @225 °C | Prusa-Systemwert, ungetestet. Testdatei bereit (6–27) |

**Tool 4 — 0.25 mm:** ⛔ kein Filamentprofil hinterlegt, nicht geplant.
**GreenTEC PRO:** ⛔ kein XL-Profil.

### Stand insgesamt

6 von 19 Profilen haben einen belegten Wert (5 per Pile-Test, TPU per
Testturm), 13 sind weiterhin Schätzungen. Empfohlene Reihenfolge der offenen
Tests, nach erwartetem Zeitgewinn:

1. **PETG (MK3) weiß nach oben** (16–24) und schwarz bei Bett 80 — der einzige
   Fall, wo eine Decke nachweislich noch nicht erreicht ist
2. **PETG HF (MK4S) Feinmessung** (22–26) — meistgenutztes Material, Decke
   liegt zwischen 21 und 24
3. **die vier 0.6mm-Profile der XL** — größte unbelegte Systemwerte (30/33)
4. **die drei Drucker-2b-Profile** — alle ungetestet
5. **Drucker 1** (PLA, PETG) — neue Profile, reine Systemwerte
6. **XL non-HF 0.4 mm** (PLA, PETG, TPU)
7. **PLA (MK3) Feinmessung** — geringster Gewinn im Set

---

## 2. Profilliste

19 Filamentprofile in [filament/](filament/). Die Zuordnung zum Drucker
erfolgt über `compatible_printers_condition` (Modell, Düsendurchmesser,
`nozzle_high_flow`), nicht über den Dateinamen.

| Profil | Drucker | mvs | Düse/1. Lage | Bett |
|---|---|---|---|---|
| PLA (MK3) | 3 (MK3S) | 7 | 210 / 215 | 60 |
| PETG (MK3) | 3 (MK3S) | 12 | 240 / 230 | 80 |
| PLA 0.6mm (MK3.5) | 1 | 15 | 220 / 230 | 60 |
| PETG 0.6mm (MK3.5) | 1 | 14 | 240 / 240 | 80 |
| PLA HF (MK4S) | 2 | 21 | 220 / 230 | 60 |
| PETG HF (MK4S) | 2 | 20 | 245 / 245 | 80 |
| PLA non-HF (MK4S) | 2b | 15 | 220 / 230 | 60 |
| PETG non-HF (MK4S) | 2b | 9 | 245 / 245 | 80 |
| GREENTEC PRO (MK4S) | 2b | 15 | 220 / 230 | 60 |
| PLA HF (XL) | 4, Tool 0+1 | 21 | 225 / 230 | 60 |
| PETG HF (XL) | 4, Tool 0+1 | 18 | 245 / 245 | 80 |
| PLA non-HF (XL) | 4, Tool 2+3 | 15 | 225 / 230 | 60 |
| PETG non-HF (XL) | 4, Tool 2+3 | 9 | 240 / 240 | 80 |
| PLA HF 0.6mm (XL) | 4, 0.6 mm | 30 | 225 / 230 | 60 |
| PETG HF 0.6mm (XL) | 4, 0.6 mm | 33 | 240 / 240 | 80 |
| PLA non-HF 0.6mm (XL) | 4, 0.6 mm | 15.5 | 225 / 230 | 60 |
| PETG non-HF 0.6mm (XL) | 4, 0.6 mm | 17 | 240 / 240 | 80 |
| TPU V2 (MK3-MK4S) | 2b, 3 | 1.5 | 230 / 230 | aus |
| TPU V2 (XL) | 4, Tool 2+3 | 2.0 | 230 / 230 | aus |

Die Begründung jedes einzelnen Werts steht in den `filament_notes` des
jeweiligen Profils — sichtbar auch direkt in PrusaSlicer.

---

## 3. Testskripte

### Generator

Alle Testdateien entstehen aus **[tools/generate_flow_rate_test.py](tools/generate_flow_rate_test.py)**.
Das Skript erzeugt eine fertige, unbeaufsichtigt laufende `.gcode`-Datei nach
der Pile-Methode von CNC Kitchen: An festen Gitterpositionen wird jeweils ohne
XY-Bewegung eine feste Filamentlänge bei konstanter Ziel-Flussrate extrudiert
(20 s Stabilisierung, Prime, Wipe, dann die Extrusion), danach weiter zur
nächsten Position mit höherer Rate. Das bildet den Wärmestau bei anhaltend
hohem Fluss ab — genau das Szenario, das bei großen Drucken zu Klicken führt
und bei kleinen nicht. Hochladen und drucken wie einen normalen Job, kein
G-Code-Terminal nötig.

```
python3 tools/generate_flow_rate_test.py --out tools/<datei>.gcode \
    --dialect <xl|single|legacy> --temp <C> --bed-temp <C> \
    --flow-start <mm3/s> --flow-step <mm3/s> --flow-count <n>
```

`--dialect` nach Firmware: `xl` für die XL, `single` für MK3.5/MK4S (Buddy),
`legacy` für die MK3S (`G28 W`). Maximal **12 Piles** pro Datei (Gitter 3×4).
Temperatur und Bett **immer** aus dem passenden `.ini`-Profil übernehmen, nicht
pauschal — ein zu kalter Lauf klickt schon beim Prime-Move und verdirbt die
Messung (passiert am 2026-09-09 mit 210 statt 220 °C).

### Vorhandene Testdateien

Die Parameter sind aus den Dateiköpfen ausgelesen, nicht abgetippt. Zum
Neuerzeugen den Aufruf oben mit diesen Werten verwenden.

| Datei (`tools/`) | Dialekt | Düse | Bett | Stufen mm³/s |
|---|---|---|---|---|
| `flow_test_Drucker1_PLA_0.6mm.gcode` | single | 220 | 60 | 9–25 (9×2) |
| `flow_test_Drucker1_PETG_0.6mm.gcode` | single | 240 | 80 | 8–24 (9×2) |
| `flow_test_Drucker2_PLA_HF_0.4mm.gcode` | single | 220 | 60 | 6–27 (8×3) |
| `flow_test_Drucker2_PETG_HF_0.4mm.gcode` | single | 245 | 80 | 6–27 (8×3) |
| `flow_test_Drucker2_PETG_HF_0.4mm_fein.gcode` | single | 245 | 80 | 22–26 (5×1) |
| `flow_test_Drucker2b_PLA_nonHF_0.4mm.gcode` | single | 220 | 60 | 6–27 (8×3) |
| `flow_test_Drucker2b_PETG_nonHF_0.4mm.gcode` | single | 245 | 80 | 6–27 (8×3) |
| `flow_test_Drucker2b_GreenTEC_PRO_0.4mm.gcode` | single | 220 | 60 | 6–27 (8×3) |
| `flow_test_Drucker3_PLA_0.4mm.gcode` | legacy | 210 | 60 | 6–12 (4×2) |
| `flow_test_Drucker3_PETG_0.4mm.gcode` | legacy | 240 | 80 | 11–16 (6×1) |
| `flow_test_Drucker3_PETG_0.4mm_hoch.gcode` | legacy | 240 | 80 | 16–24 (5×2) |
| `flow_test_Drucker4_PLA_HF_0.4mm.gcode` | xl | 225 | 60 | 16–23 (8×1) |
| `flow_test_Drucker4_PETG_HF_0.4mm.gcode` | xl | 245 | 80 | 6–27 (8×3) |
| `flow_test_Drucker4_PLA_nonHF_0.4mm.gcode` | xl | 225 | 60 | 6–27 (8×3) |
| `flow_test_Drucker4_PETG_nonHF_0.4mm.gcode` | xl | 240 | 80 | 6–27 (8×3) |
| `flow_test_Drucker4_PLA_HF_0.6mm.gcode` | xl | 225 | 60 | 15–36 (8×3) |
| `flow_test_Drucker4_PETG_HF_0.6mm.gcode` | xl | 240 | 80 | 6–27 (8×3) |
| `flow_test_Drucker4_PLA_nonHF_0.6mm.gcode` | xl | 225 | 60 | 6–27 (8×3) |
| `flow_test_Drucker4_PETG_nonHF_0.6mm.gcode` | xl | 240 | 80 | 6–27 (8×3) |
| `flow_test_Drucker4_TPU_0.4mm.gcode` | xl | 230 | (40) | 0.75–2.5 (8×0.25) |

Längere Notizen zu einzelnen Dateien: [tools/flow_test_plan.txt](tools/flow_test_plan.txt).

### Bekannte Schwächen des Generators

- `--bed-temp 0` ist laut Hilfe „disabled", fällt im cnc-kitchen-Pattern aber
  auf 40 °C zurück und wartet darauf
  (`generate_flow_rate_test.py:137,144`). Betrifft nur die TPU-Datei, deren
  Profil ein unbeheiztes Bett vorsieht. Für die Extrusion unerheblich.
- Der Mehrtemperatur-Modus (`--temp-count > 1`) ist unbrauchbar: die
  Gitterposition wird nur aus `flow_idx` berechnet
  (`generate_flow_rate_test.py:157-160`), jeder Temperaturblock setzt seine
  Piles also auf dieselben Stellen. Wäre reparabel und würde einen
  220-vs-225-Vergleich in einem Druck erlauben — nicht behoben, weil für die
  offenen Tests nicht gebraucht.
- `--flow-count > 12` läuft in einen IndexError.

---

## 4. Messprotokoll

- **Drei Messreihen** pro Kombination. Bei PLA (MK3) war 10 mm³/s in einer von
  drei Reihen sauber und in zwei nicht — mit einem einzigen Lauf hätte man den
  Wert zu hoch angesetzt.
- **Waage nicht auf das Heizbett stellen.** Messreihe 1 vom 2026-09-09 ist
  deswegen unbrauchbar (Drift).
- Jede Pile wiegen. Der Massenabfall zeigt Unterextrusion auch dann, wenn kein
  Klicken zu hören ist — typisch 3–5 % eine Stufe vor dem harten Abriss.
- Auswertung: höchste durchgehend saubere Stufe nehmen, dann Sicherheitsmarge
  abziehen. Bei groben 3er-Schritten waren das bisher 2–3 mm³/s; bei
  1er-Auflösung genügt weniger.
- Ergebnis in die `filament_notes` des Profils **und** in die Tabelle oben.

## 5. Messhistorie

| Datum | Profil | Ergebnis |
|---|---|---|
| 2024-01-24 | TPU V2 (MK3-MK4S) | Testturm, 1.5 mm³/s (U. Hornstein) |
| 2026-08-30 | PETG (MK3), schwarz | sauber bis 12, Abriss 15 → mvs 8 auf 10 |
| 2026-08-30 | PLA (MK3) | sauber bis 8, Grauzone 10 → mvs 15 auf 7 (Herstellerangabe war weit zu hoch) |
| 2026-09-09 | PLA HF (XL) @220 | sauber bis 18, Abriss 21 → mvs 21 auf 15 |
| 2026-09-09 | PETG HF (XL) | sauber bis 21, Abriss 24 → mvs 22 auf 18 |
| 2026-11-04 | PLA HF (XL) | Klicken im 0.28mm-DRAFT-Druck bei 220 °C; mit 224 °C klickfrei → Versuch mit 225 °C und mvs 21 |
| 2026-11-07 | PLA HF (XL) @225 | sauber bis 21, Massenabfall 22, Abriss 23 → mvs bleibt 21, Temperatureffekt belegt |
| 2026-11-07 | PETG HF (MK4S) | sauber bis 21, Massenabfall 24, Abriss 27 → mvs 22 auf 20 |
| 2026-11-07 | PETG (MK3), weiß | kein Klicken bis 16 → mvs 10 auf 12, Decke offen |

Verworfen: ein erster PETG-(MK3)-Lauf vom 2026-08-29 („sauber über alle 15
Stufen 6–48") — die Datei hatte real nur 8 Stufen bis 27 und lief vor dem
Dialect-Fix (`5652ce0`).
