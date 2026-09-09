; *** CNC Kitchen Auto Flow Pattern Generator 0.93
; *** 02/04/26 Stefan Hermann

;####### Settings
; Prusa SINGLE
; bedWidth = 250
; bedLength = 220
; bedMargin = 5
; filamentDiameter = 1.75
; movementSpeed = 100
; stabilizationTime = 20
; bedTemp = 80
; primeLength = 25
; primeAmount = 20
; primeSpeed = 5
; retractionDistance = 1
; retractionSpeed = 60
; blobHeight = 10
; extrusionAmount = 200
; xSpacing = 40
; ySpacing = 65
; startFlow = 6.0
; flowOffset = 3.0
; flowSteps = 8
; startTemp = 245.0
; tempOffset = 0.0
; tempSteps = 1
; direction = 1

;####### Flow Rate Sequence
; Pile 1: 6.0mm3/s
; Pile 2: 9.0mm3/s
; Pile 3: 12.0mm3/s
; Pile 4: 15.0mm3/s
; Pile 5: 18.0mm3/s
; Pile 6: 21.0mm3/s
; Pile 7: 24.0mm3/s
; Pile 8: 27.0mm3/s

M104 S245 ; Set Nozzle Temperature
M140 S80 ; Set Bed Temperature
G90
G28 ; Move to home position
G0 Z10 ; Lift nozzle
G21; unit in mm
G92 E0; reset extruder
M83; set extruder to relative mode
M190 S80 ; Set Bed Temperature & Wait
M106 S0 ; Set Fan Speed

;####### 245C
G4 S0 ; Dwell
M109 R245

;####### Pile 1/8: 6.0mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 245C // 6.0mm3/s
G0 X5 Y5 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X30 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X45 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F7.48 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X5 Y5 F6000
G92 E0 ; Reset Extruder

;####### Pile 2/8: 9.0mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 245C // 9.0mm3/s
G0 X5 Y70 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X30 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X45 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F11.23 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X5 Y70 F6000
G92 E0 ; Reset Extruder

;####### Pile 3/8: 12.0mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 245C // 12.0mm3/s
G0 X5 Y135 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X30 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X45 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F14.97 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X5 Y135 F6000
G92 E0 ; Reset Extruder

;####### Pile 4/8: 15.0mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 245C // 15.0mm3/s
G0 X5 Y200 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X30 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X45 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F18.71 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X5 Y200 F6000
G92 E0 ; Reset Extruder

;####### Pile 5/8: 18.0mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 245C // 18.0mm3/s
G0 X85 Y5 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X110 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X125 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F22.45 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X85 Y5 F6000
G92 E0 ; Reset Extruder

;####### Pile 6/8: 21.0mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 245C // 21.0mm3/s
G0 X85 Y70 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X110 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X125 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F26.19 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X85 Y70 F6000
G92 E0 ; Reset Extruder

;####### Pile 7/8: 24.0mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 245C // 24.0mm3/s
G0 X85 Y135 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X110 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X125 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F29.93 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X85 Y135 F6000
G92 E0 ; Reset Extruder

;####### Pile 8/8: 27.0mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 245C // 27.0mm3/s
G0 X85 Y200 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X110 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X125 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F33.68 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X85 Y200 F6000
G92 E0 ; Reset Extruder

;####### End G-Code
G0 X245 Y215 ; Move to Corner
M104 S0 T0 ; Turn Off Hotend
M140 S0 ; Turn Off Bed
M84
