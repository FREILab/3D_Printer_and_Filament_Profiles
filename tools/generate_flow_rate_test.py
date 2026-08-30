#!/usr/bin/env python3
"""
Generate a standalone G-code file for max-volumetric-speed ("flow rate")
benchmarking on the Prusa XL, following the CNC Kitchen pile method:
https://www.cnckitchen.com/blog/flow-rate-benchmarking-of-a-hotend

This script also includes the classic auto-flow benchmark pattern used in the
community reference pack on Printables:
https://www.printables.com/model/160335-hotend-benchmark-test-g-codes/

At each grid position the nozzle extrudes a fixed length of filament at a
target volumetric flow rate (sustained over tens of seconds, not a short
burst), then automatically snaps off the trailing string with a small
"curl" move (a tight octagon traveled while retracted) before moving on to
the next position at a higher flow rate. This reproduces sustained-flow
heat soak, which is what causes skipping on large prints with long infill
lines but not on small ones -- without any operator interaction.

The resulting .gcode file is uploaded/printed like any normal job (PrusaLink
web UI, USB) -- no G-code console or API access needed, and the whole run
is unattended (no pause, no manual string removal).

Supports three printer G-code dialects (--dialect):
  xl      Prusa XL (tool-changer): "T<n> S1 L0 D0" tool pick, split G28 XY / G28 Z.
  single  Buddy-firmware single-extruder printers (MK3.5, MK4S): plain G28.
  legacy  Older Marlin single-extruder printers (MK3S): "G28 W" (home,
          explicitly skipping the printer's automatic mesh probe).

Optional bed heating: can be enabled with --bed-temp. No mesh bed leveling
is used (mesh probing on a cold bed was giving bad compensation data that
made the nozzle dive too deep). Piles are extruded a bit higher above the
bed than a normal first layer to stay safe without any Z compensation.

Usage:
    python3 generate_flow_rate_test.py --out out.gcode --dialect xl \
        --tool 0 --temp 220 --bed-temp 60 \
        --flow-start 9 --flow-step 3 --flow-count 9 \
        --pile-length 500
"""
import argparse
import math
import shlex
import sys

FILAMENT_DIAMETER = 1.75
FILAMENT_AREA = 3.14159265 * (FILAMENT_DIAMETER / 2) ** 2  # mm^2, ~2.405
PILE_Z = 10.0  # mm above bed; elevated since there's no mesh compensation
CURL_RADIUS = 3.0  # mm, radius of the automatic string-snap move
EXTRUSION_RADIUS = 5.0  # mm, radius of circle around pile during extrusion


def feedrate_for_flow(flow_mm3_s: float) -> float:
    """Convert target volumetric flow (mm^3/s) to E feedrate (mm/min)."""
    return flow_mm3_s * 60.0 / FILAMENT_AREA


def motion_feedrate_for_flow(flow_mm3_s: float) -> float:
    """Map the benchmark flow index to a conservative XY motion feedrate.

    The total deposited filament per pile remains constant; only the motion
    speed changes, so the pile mass stays equal and can be verified on a scale.
    The feedrate is deliberately kept conservative because the extruder sees a
    large E burst if too much filament is pushed per path segment.
    """
    return max(80.0, min(260.0, flow_mm3_s * 7.5 + 65.0))


def curl_points(cx: float, cy: float, radius: float, n: int = 8):
    """Octagon points around (cx, cy) used to snap off a trailing string."""
    return [
        (cx + radius * math.cos(2 * math.pi * i / n),
         cy + radius * math.sin(2 * math.pi * i / n))
        for i in range(n)
    ]


def cnc_kitchen_feedrate_for_flow(flow_mm3_s: float) -> float:
    """Return the low E feedrate used in the classic CNC Kitchen pattern."""
    return flow_mm3_s * 60.0 / (FILAMENT_AREA * 20.0)


def build_cnc_kitchen_gcode(args) -> str:
    lines = []
    a = lines.append

    temp_start = float(args.temp)
    temp_step = float(getattr(args, "temp_step", 0.0))
    temp_count = int(getattr(args, "temp_count", 1))
    if temp_count <= 0:
        raise SystemExit("--temp-count must be >= 1")

    x_positions = [5.0, 85.0, 165.0]
    y_positions = [5.0, 55.0, 105.0, 155.0]

    a("; *** CNC Kitchen Auto Flow Pattern Generator 0.93")
    a("; *** 02/04/26 Stefan Hermann")
    a("")
    a(";####### Settings")
    a(f"; Prusa {args.dialect.upper() if args.dialect else 'Printer'}")
    a("; bedWidth = 250")
    a("; bedLength = 220")
    a("; bedMargin = 5")
    a("; filamentDiameter = 1.75")
    a("; movementSpeed = 100")
    a("; stabilizationTime = 20")
    a(f"; bedTemp = {int(args.bed_temp) if args.bed_temp else 40}")
    a("; primeLength = 25")
    a("; primeAmount = 20")
    a("; primeSpeed = 5")
    a("; retractionDistance = 1")
    a("; retractionSpeed = 60")
    a("; blobHeight = 10")
    a("; extrusionAmount = 200")
    a("; xSpacing = 40")
    a("; ySpacing = 50")
    a(f"; startFlow = {args.flow_start}")
    a(f"; flowOffset = {args.flow_step}")
    a(f"; flowSteps = {args.flow_count}")
    a(f"; startTemp = {temp_start}")
    a(f"; tempOffset = {temp_step}")
    a(f"; tempSteps = {temp_count}")
    a("; direction = 1")
    a("")
    a(";####### Flow Rate Sequence")
    for flow_idx in range(args.flow_count):
        flow = args.flow_start + flow_idx * args.flow_step
        a(f"; Pile {flow_idx + 1}: {flow}mm3/s")
    a("")

    a(f"M104 S{temp_start:.0f} ; Set Nozzle Temperature")
    a(f"M140 S{int(args.bed_temp) if args.bed_temp else 40} ; Set Bed Temperature")
    a("G90")
    a("G28 ; Move to home position")
    a("G0 Z10 ; Lift nozzle")
    a("G21; unit in mm")
    a("G92 E0; reset extruder")
    a("M83; set extruder to relative mode")
    a(f"M190 S{int(args.bed_temp) if args.bed_temp else 40} ; Set Bed Temperature & Wait")
    a("M106 S0 ; Set Fan Speed")
    a("")

    for temp_idx in range(temp_count):
        temp = temp_start + temp_idx * temp_step
        a(f";####### {temp:.0f}C")
        a("G4 S0 ; Dwell")
        a(f"M109 R{temp:.0f}")
        a("")

        for flow_idx in range(args.flow_count):
            flow = args.flow_start + flow_idx * args.flow_step
            col = flow_idx // len(y_positions)
            row = flow_idx % len(y_positions)
            x = x_positions[col]
            y = y_positions[row]
            prime_x = x + 25
            wipe_x = x + 40
            feed = cnc_kitchen_feedrate_for_flow(flow)

            a(f";####### Pile {flow_idx + 1}/{args.flow_count}: {flow}mm3/s")
            a("M400 ; wait for previous pile's moves to finish before updating display")
            a(f"M117 {temp:.0f}C // {flow}mm3/s")
            a(f"G0 X{x:.0f} Y{y:.0f} Z15.5 F6000")
            a("G4 S20; Stabalize")
            a("G0 Z0.3 ; Drop down")
            a(f"G1 X{prime_x:.0f} E20 F300 ;Prime")
            a("G1 E-1 F3600; Retract")
            a(f"G0 X{wipe_x:.0f} F6000 ; Wipe")
            a("G0 Z0.5 ; Lift")
            a("G1 E1 F3600 ; De-Retract")
            a(f"G1 Z10.5 E200 F{feed:.2f} ; Extrude")
            a("G1 E-1 F3600 ; Retract")
            a("G0 Z15.5; Lift")
            a(f"G0 X{x:.0f} Y{y:.0f} F6000")
            a("G92 E0 ; Reset Extruder")
            a("")

    a(";####### End G-Code")
    a("G0 X245 Y215 ; Move to Corner")
    a("M104 S0 T0 ; Turn Off Hotend")
    a("M140 S0 ; Turn Off Bed")
    a("M84")
    return "\n".join(lines) + "\n"


def build_pile_gcode(args) -> str:
    lines = []
    a = lines.append

    a("; Flow rate / max volumetric speed benchmark (CNC Kitchen pile method)")
    a("; Generated by tools/generate_flow_rate_test.py with:")
    a(f"; {shlex.join(sys.argv[1:])}")
    if args.bed_temp:
        a(f"; tool={args.tool} nozzle={args.temp}C bed={args.bed_temp}C")
    else:
        a(f"; tool={args.tool} nozzle={args.temp}C (bed unheated)")
    a(f"; flow: start={args.flow_start} step={args.flow_step} "
      f"count={args.flow_count} mm3/s, pile_length={args.pile_length}mm")
    a("")
    a("M17 ; enable steppers")
    a("G90 ; absolute positioning")
    a("M83 ; relative extruder mode")

    margin = args.margin
    spacing = args.spacing
    row_spacing = args.row_spacing

    # Start bed heating early so it warms up during homing
    if args.bed_temp:
        a(f"M140 S{args.bed_temp} ; set bed temp early")

    if args.dialect == "legacy":
        a(f"M104 S{args.temp} ; set extruder temp")
        a(f"M109 S{args.temp} ; wait for extruder temp")
        if args.bed_temp:
            a(f"M190 S{args.bed_temp} ; wait for bed temp")
        a("G28 W ; home, explicitly skip automatic mesh probe")
    else:
        if args.dialect == "xl":
            a("G28 XY ; home XY")
            a(f"T{args.tool} S1 L0 D0 ; pick tool")
            a("G28 Z ; home Z")
        else:  # single (MK3.5 / MK4S)
            a("G28 ; home all axes")

        a(f"M104 S{args.temp} T{args.tool} ; set nozzle temp")
        a(f"M109 S{args.temp} T{args.tool} ; wait for nozzle temp")
        if args.bed_temp:
            a(f"M190 S{args.bed_temp} ; wait for bed temp")

    a("G1 Z5 F600")
    a("")
    a("; Purge line to prime the extruder")
    a("G92 E0 ; reset extruder position")
    a("G1 X20 Y10 Z0.4 F4800 ; move to purge location")
    a("G1 E15 X40 Y10 Z0.4 F500 ; extrude while moving to prime")
    a("G1 Z5 F600 ; z hop after purge")
    a("G92 E0 ; reset extruder position again before testing")
    a("")
    max_x = args.bed_x - margin
    max_y = args.bed_y - margin
    x = margin
    y = margin

    for i in range(args.flow_count):
        flow = args.flow_start + i * args.flow_step
        feed = feedrate_for_flow(flow)
        if x > max_x:
            x = margin
            y += row_spacing
        if y > max_y:
            raise SystemExit(
                f"Grid does not fit on bed: pile {i} would land at Y={y}, "
                f"max is {max_y}. Reduce --flow-count, --spacing or --row-spacing."
            )
        a(f"; --- pile {i + 1}/{args.flow_count}: {flow:.1f} mm3/s "
          f"(F{feed:.0f}) ---")
        a(f"G1 X{x:.1f} Y{y:.1f} F6000")
        a(f"G1 Z{PILE_Z} F600")
        a("G92 E0 ; reset extruder position before each pile")
        a("G4 S1")
        # The benchmark varies only the motion speed. The total filament per
        # pile stays constant so the piles can be weighed and validated as equal.
        # Spread the same filament over more segments to avoid a massive E burst
        # on the first pile. The total mass per pile stays equal; only the path
        # speed changes between flow levels.
        circle_points = curl_points(x, y, EXTRUSION_RADIUS, n=32)
        extrusion_per_point = args.pile_length / len(circle_points)
        motion_f = motion_feedrate_for_flow(flow)
        for px, py in circle_points:
            a(f"G1 E{extrusion_per_point:.3f} X{px:.2f} Y{py:.2f} F{motion_f:.0f}")
        # Return to start point for curl move at slow speed
        a(f"G1 X{x:.1f} Y{y:.1f} F{motion_f:.0f}")
        a("G1 E-2 F1800 ; retract")
        a(f"G1 Z{PILE_Z + 2} F600 ; small Z hop")
        a("; curl move: snap off the trailing string automatically, no operator needed")
        for px, py in curl_points(x, y, CURL_RADIUS):
            a(f"G1 X{px:.2f} Y{py:.2f} F4000")
        a(f"G1 X{x:.1f} Y{y:.1f} F4000")
        a("")
        x += spacing

    if args.dialect == "legacy":
        a("M104 S0")
    else:
        a(f"M104 S0 T{args.tool}")
    a("G1 Z50 F600")
    a("M84")
    return "\n".join(lines) + "\n"


def build_gcode(args) -> str:
    if getattr(args, "pattern", "pile") == "cnc-kitchen":
        return build_cnc_kitchen_gcode(args)
    return build_pile_gcode(args)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", required=True, help="output .gcode file path")
    p.add_argument("--dialect", choices=["xl", "single", "legacy"], default="single",
                    help="printer G-code dialect: xl (XL tool-changer), "
                         "single (MK3.5/MK4S), legacy (MK3S)")
    p.add_argument("--pattern", choices=["pile", "cnc-kitchen"], default="cnc-kitchen",
                    help="benchmark pattern: pile (new pile method), "
                         "cnc-kitchen (classic sequence of temp/flow blocks)")
    p.add_argument("--tool", type=int, default=0, help="tool/extruder index (XL: 0-4)")
    p.add_argument("--temp", type=float, required=True, help="nozzle temp, C")
    p.add_argument("--temp-step", type=float, default=0.0,
                    help="temperature step for multi-temp classic pattern (C)")
    p.add_argument("--temp-count", type=int, default=1,
                    help="number of temperatures for classic pattern")
    p.add_argument("--bed-temp", type=float, default=0, help="bed temp, C (0 = disabled)")
    p.add_argument("--flow-start", type=float, default=6.0, help="mm3/s")
    p.add_argument("--flow-step", type=float, default=3.0, help="mm3/s")
    p.add_argument("--flow-count", type=int, default=15, help="number of piles / flow blocks")
    p.add_argument("--pile-length", type=float, default=500.0,
                    help="filament length extruded per pile, mm")
    p.add_argument("--bed-x", type=float, default=None)
    p.add_argument("--bed-y", type=float, default=None)
    p.add_argument("--margin", type=float, default=40.0)
    p.add_argument("--spacing", type=float, default=35.0)
    p.add_argument("--row-spacing", type=float, default=40.0,
                    help="Y distance between rows when a row is full")
    args = p.parse_args()

    # Set default bed sizes based on dialect if not explicitly specified
    if args.bed_x is None:
        if args.dialect == "xl":
            args.bed_x = 360.0
        else:  # single or legacy (MK3.5/MK4S/MK3S)
            args.bed_x = 250.0
    if args.bed_y is None:
        if args.dialect == "xl":
            args.bed_y = 360.0
        else:  # single or legacy (MK3.5/MK4S/MK3S)
            args.bed_y = 210.0

    gcode = build_gcode(args)
    with open(args.out, "w") as f:
        f.write(gcode)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
