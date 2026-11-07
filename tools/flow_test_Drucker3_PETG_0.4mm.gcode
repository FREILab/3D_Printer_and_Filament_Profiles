; *** CNC Kitchen Auto Flow Pattern Generator 0.93
; *** 02/04/26 Stefan Hermann

;####### Settings
; Prusa LEGACY
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
; startFlow = 11.0
; flowOffset = 1.0
; flowSteps = 6
; startTemp = 240.0
; tempOffset = 0.0
; tempSteps = 1
; direction = 1

;####### Flow Rate Sequence
; Pile 1: 11.0mm3/s
; Pile 2: 12.0mm3/s
; Pile 3: 13.0mm3/s
; Pile 4: 14.0mm3/s
; Pile 5: 15.0mm3/s
; Pile 6: 16.0mm3/s

M104 S240 ; Set Nozzle Temperature
M140 S80 ; Set Bed Temperature
G90
G28 ; Move to home position
G0 Z10 ; Lift nozzle
G21; unit in mm
G92 E0; reset extruder
M83; set extruder to relative mode
M190 S80 ; Set Bed Temperature & Wait
M106 S0 ; Set Fan Speed

;####### 240C
G4 S0 ; Dwell
M109 R240

;####### Pile 1/6: 11.0mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 240C // 11.0mm3/s
G0 X5 Y5 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X30 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X45 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F13.72 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X5 Y5 F6000
G92 E0 ; Reset Extruder

;####### Pile 2/6: 12.0mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 240C // 12.0mm3/s
G0 X5 Y70 Z15.5 F6000
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
G0 X5 Y70 F6000
G92 E0 ; Reset Extruder

;####### Pile 3/6: 13.0mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 240C // 13.0mm3/s
G0 X5 Y135 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X30 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X45 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F16.21 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X5 Y135 F6000
G92 E0 ; Reset Extruder

;####### Pile 4/6: 14.0mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 240C // 14.0mm3/s
G0 X5 Y200 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X30 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X45 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F17.46 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X5 Y200 F6000
G92 E0 ; Reset Extruder

;####### Pile 5/6: 15.0mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 240C // 15.0mm3/s
G0 X85 Y5 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X110 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X125 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F18.71 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X85 Y5 F6000
G92 E0 ; Reset Extruder

;####### Pile 6/6: 16.0mm3/s
M400 ; wait for previous pile's moves to finish before updating display
M117 240C // 16.0mm3/s
G0 X85 Y70 Z15.5 F6000
G4 S20; Stabalize
G0 Z0.3 ; Drop down
G1 X110 E20 F300 ;Prime
G1 E-1 F3600; Retract
G0 X125 F6000 ; Wipe
G0 Z0.5 ; Lift
G1 E1 F3600 ; De-Retract
G1 Z10.5 E200 F19.96 ; Extrude
G1 E-1 F3600 ; Retract
G0 Z15.5; Lift
G0 X85 Y70 F6000
G92 E0 ; Reset Extruder

;####### End G-Code
G0 X245 Y215 ; Move to Corner
M104 S0 T0 ; Turn Off Hotend
M140 S0 ; Turn Off Bed
M84
