; *** CNC Kitchen Auto Flow Pattern Generator 0.93
; *** 02/04/26 Stefan Hermann

;####### Settings
; Prusa XL
; bedWidth = 250
; bedLength = 220
; bedMargin = 5
; filamentDiameter = 1.75
; movementSpeed = 100
; stabilizationTime = 20
; bedTemp = 40
; primeLength = 25
; primeAmount = 20
; primeSpeed = 5
; retractionDistance = 1
; retractionSpeed = 60
; blobHeight = 10
; extrusionAmount = 200
; xSpacing = 40
; ySpacing = 65
; startFlow = 0.75
; flowOffset = 0.25
; flowSteps = 8
; startTemp = 230.0
; tempOffset = 0.0
; tempSteps = 1
; direction = 1

;####### Flow Rate Sequence
; Pile 1: 0.75mm3/s
; Pile 2: 1.0mm3/s
; Pile 3: 1.25mm3/s
; Pile 4: 1.5mm3/s
; Pile 5: 1.75mm3/s
; Pile 6: 2.0mm3/s
; Pile 7: 2.25mm3/s
; Pile 8: 2.5mm3/s

M104 S230 ; Set Nozzle Temperature
M140 S40 ; Set Bed Temperature
G90
G28 ; Move to home position
G0 Z10 ; Lift nozzle
G21; unit in mm
G92 E0; reset extruder
M83; set extruder to relative mode
M190 S40 ; Set Bed Temperature & Wait
M106 S0 ; Set Fan Speed

;####### 230C
G4 S0 ; Dwell
M109 R230

;####### Pile 1/8: 0.75mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 230C // 0.75mm3/s
G0 X5 Y5 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X30 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X45 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F0.94 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X5 Y5 F6000
G92 E0 ; Reset Extruder

;####### Pile 2/8: 1.0mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 230C // 1.0mm3/s
G0 X5 Y95 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X30 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X45 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F1.25 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X5 Y95 F6000
G92 E0 ; Reset Extruder

;####### Pile 3/8: 1.25mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 230C // 1.25mm3/s
G0 X5 Y185 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X30 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X45 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F1.56 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X5 Y185 F6000
G92 E0 ; Reset Extruder

;####### Pile 4/8: 1.5mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 230C // 1.5mm3/s
G0 X5 Y275 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X30 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X45 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F1.87 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X5 Y275 F6000
G92 E0 ; Reset Extruder

;####### Pile 5/8: 1.75mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 230C // 1.75mm3/s
G0 X95 Y5 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X120 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X135 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F2.18 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X95 Y5 F6000
G92 E0 ; Reset Extruder

;####### Pile 6/8: 2.0mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 230C // 2.0mm3/s
G0 X95 Y95 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X120 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X135 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F2.49 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X95 Y95 F6000
G92 E0 ; Reset Extruder

;####### Pile 7/8: 2.25mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 230C // 2.25mm3/s
G0 X95 Y185 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X120 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X135 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F2.81 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X95 Y185 F6000
G92 E0 ; Reset Extruder

;####### Pile 8/8: 2.5mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 230C // 2.5mm3/s
G0 X95 Y275 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X120 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X135 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F3.12 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X95 Y275 F6000
G92 E0 ; Reset Extruder

;####### End G-Code
G0 X245 Y215 ; Move to Corner
M104 S0 T0 ; Turn Off Hotend
M140 S0 ; Turn Off Bed
M84
