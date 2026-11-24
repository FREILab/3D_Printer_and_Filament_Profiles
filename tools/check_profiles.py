#!/usr/bin/env python3
"""Validate all FREILab PrusaSlicer profiles (filament, printer, physical_printer).

Catches issues such as:
- Missing/zero filament_cost or filament_density (causes 0 EUR / missing cost in PrusaSlicer)
- Wrong/default filament prices (e.g. Prusa defaults 25.4 / 27.82 instead of FREILab tariffs)
- Stripped hand-written user .ini files (PrusaSlicer does NOT inherit missing keys from
  'inherits' in user .ini files; missing keys fall back to hardcoded defaults!)
- Empty 'inherits' on printer profiles
- Broken physical_printer -> printer references
- Missing PLA/PETG coverage for active printers, or TPU accidentally enabled on HF printers
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILAMENT_KEYS = [
    "bed_temperature",
    "bridge_fan_speed",
    "compatible_printers_condition",
    "cooling",
    "disable_fan_first_layers",
    "end_filament_gcode",
    "extrusion_multiplier",
    "fan_always_on",
    "filament_cost",
    "filament_density",
    "filament_diameter",
    "filament_max_volumetric_speed",
    "filament_type",
    "first_layer_bed_temperature",
    "first_layer_temperature",
    "inherits",
    "max_fan_speed",
    "min_fan_speed",
    "min_print_speed",
    "slowdown_below_layer_time",
    "start_filament_gcode",
    "temperature",
]

REQUIRED_PRINTER_KEYS = [
    "bed_shape",
    "end_gcode",
    "inherits",
    "max_layer_height",
    "min_layer_height",
    "nozzle_diameter",
    "nozzle_high_flow",
    "printer_model",
    "printer_notes",
    "start_gcode",
]

# FREILab standard tariffs (EUR/kg) and densities (g/cm3) per material family.
EXPECTED_TARIFFS: dict[str, tuple[float, float]] = {
    "GREENTEC": (56.23, 1.35),
    "PLA": (30.0, 1.24),
    "PETG": (40.0, 1.27),
    "TPU": (45.0, 1.23),
}


def parse_ini(path: Path) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    kv: dict[str, str] = {}
    text = path.read_text(encoding="utf-8")
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            errors.append(f"{path.relative_to(ROOT)}:{lineno}: invalid line (no '='): {line!r}")
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()
        if key in kv:
            errors.append(f"{path.relative_to(ROOT)}:{lineno}: duplicate key {key!r}")
        kv[key] = val
    return kv, errors


def parse_float_list(val: str) -> list[float]:
    return [float(x.strip()) for x in val.split(",") if x.strip()]


def parse_int_list(val: str) -> list[int]:
    return [int(x.strip()) for x in val.split(",") if x.strip()]


def material_family(path: Path, kv: dict[str, str]) -> str | None:
    name_up = path.stem.upper()
    if "GREENTEC" in name_up:
        return "GREENTEC"
    if "TPU" in name_up or kv.get("filament_type", "").upper() == "FLEX":
        return "TPU"
    if "PETG" in name_up or kv.get("filament_type", "").upper() == "PETG":
        return "PETG"
    if "PLA" in name_up or kv.get("filament_type", "").upper() == "PLA":
        return "PLA"
    return None


def eval_condition(expr: str, printer_kv: dict[str, str]) -> bool:
    """Evaluate a PrusaSlicer compatible_printers_condition expression against a printer."""
    expr = expr.strip()
    if not expr:
        return True

    model = printer_kv.get("printer_model", "")
    notes = printer_kv.get("printer_notes", "").replace("\\n", "\n")
    nozzles = parse_float_list(printer_kv.get("nozzle_diameter", "0.4"))
    hf_flags = parse_int_list(printer_kv.get("nozzle_high_flow", "0"))
    semm = int(printer_kv.get("single_extruder_multi_material", "0"))

    def lookup_str(var: str) -> str:
        if var == "printer_model":
            return model
        if var == "printer_notes":
            return notes
        raise ValueError(f"Unsupported string variable: {var}")

    def lookup_num(var: str, idx: int) -> float:
        if var == "nozzle_diameter":
            return nozzles[idx]
        if var == "nozzle_high_flow":
            return float(hf_flags[idx])
        raise ValueError(f"Unsupported indexed variable: {var}[{idx}]")

    # Tokenize PrusaSlicer condition syntax
    token_re = re.compile(
        r"""
        \s*(?:
            (?P<LPAREN>\()
          | (?P<RPAREN>\))
          | (?P<REGEX_OP>=~/|!~/)
          | (?P<CMP>==|!=|>=|<=|>|<)
          | (?P<BANG>!)
          | (?P<STR>"[^"]*")
          | (?P<NUM>\d+(?:\.\d+)?)
          | (?P<IDENT>[A-Za-z_][A-Za-z0-9_]*)
          | (?P<LBRACK>\[)
          | (?P<RBRACK>\])
        )
        """,
        re.VERBOSE,
    )

    tokens: list[tuple[str, str]] = []
    pos = 0
    while pos < len(expr):
        if expr[pos].isspace():
            pos += 1
            continue
        m = token_re.match(expr, pos)
        if not m:
            raise ValueError(f"Cannot parse condition near {expr[pos:]!r} in {expr!r}")
        kind = m.lastgroup
        val = m.group(kind)
        pos = m.end()
        if kind == "REGEX_OP":
            # Read until unescaped '/'
            end = pos
            while end < len(expr):
                if expr[end] == "/" and (end == pos or expr[end - 1] != "\\"):
                    break
                end += 1
            if end >= len(expr):
                raise ValueError(f"Unterminated regex in {expr!r}")
            pattern = expr[pos:end]
            pos = end + 1
            tokens.append((val, pattern))
        else:
            tokens.append((kind, val))

    idx = 0

    def peek() -> tuple[str, str] | None:
        return tokens[idx] if idx < len(tokens) else None

    def consume() -> tuple[str, str]:
        nonlocal idx
        tok = tokens[idx]
        idx += 1
        return tok

    def parse_or() -> bool:
        left = parse_and()
        while (t := peek()) and t == ("IDENT", "or"):
            consume()
            right = parse_and()
            left = left or right
        return left

    def parse_and() -> bool:
        left = parse_not()
        while (t := peek()) and t == ("IDENT", "and"):
            consume()
            right = parse_not()
            left = left and right
        return left

    def parse_not() -> bool:
        if (t := peek()) and t[0] == "BANG":
            consume()
            return not parse_not()
        return parse_atom()

    def parse_atom() -> bool:
        t = peek()
        if not t:
            raise ValueError(f"Unexpected end of expression: {expr!r}")
        if t[0] == "LPAREN":
            consume()
            val = parse_or()
            if consume()[0] != "RPAREN":
                raise ValueError(f"Missing ')' in {expr!r}")
            return val
        if t[0] != "IDENT":
            raise ValueError(f"Unexpected token {t} in {expr!r}")
        ident = consume()[1]
        index: int | None = None
        if (nt := peek()) and nt[0] == "LBRACK":
            consume()
            num_tok = consume()
            if num_tok[0] != "NUM":
                raise ValueError(f"Expected index in {expr!r}")
            index = int(num_tok[1])
            if consume()[0] != "RBRACK":
                raise ValueError(f"Missing ']' in {expr!r}")

        nxt = peek()
        if nxt and nxt[0] in ("=~/", "!~/"):
            op, pattern = consume()
            s = lookup_str(ident)
            # PrusaSlicer =~ /.../ uses full-string match (boost::regex_match)
            matched = re.fullmatch(pattern, s, re.DOTALL) is not None
            return matched if op == "=~/" else not matched

        if nxt and nxt[0] == "CMP":
            op = consume()[1]
            rhs_tok = consume()
            if rhs_tok[0] == "STR":
                lhs = lookup_str(ident)
                rhs = rhs_tok[1][1:-1]
                if op == "==":
                    return lhs == rhs
                if op == "!=":
                    return lhs != rhs
                raise ValueError(f"Unsupported string op {op}")
            if rhs_tok[0] == "NUM":
                if index is None:
                    raise ValueError(f"Numeric var {ident} without index in {expr!r}")
                lhs_f = lookup_num(ident, index)
                rhs_f = float(rhs_tok[1])
                return {
                    "==": lhs_f == rhs_f,
                    "!=": lhs_f != rhs_f,
                    ">=": lhs_f >= rhs_f,
                    "<=": lhs_f <= rhs_f,
                    ">": lhs_f > rhs_f,
                    "<": lhs_f < rhs_f,
                }[op]
            raise ValueError(f"Unexpected RHS {rhs_tok} in {expr!r}")

        # Bare boolean identifier (e.g. nozzle_high_flow[0], single_extruder_multi_material)
        if ident == "single_extruder_multi_material":
            return bool(semm)
        if index is not None:
            return bool(lookup_num(ident, index))
        raise ValueError(f"Unsupported bare identifier {ident!r} in {expr!r}")

    result = parse_or()
    if idx != len(tokens):
        raise ValueError(f"Trailing tokens {tokens[idx:]} in {expr!r}")
    return result


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    filament_files = sorted((ROOT / "filament").glob("*.ini"))
    printer_files = sorted((ROOT / "printer").glob("*.ini"))
    physical_files = sorted((ROOT / "physical_printer").glob("*.ini"))

    if not filament_files:
        errors.append("No filament/*.ini files found.")
    if not printer_files:
        errors.append("No printer/*.ini files found.")
    if not physical_files:
        errors.append("No physical_printer/*.ini files found.")

    filaments: dict[Path, dict[str, str]] = {}
    printers: dict[str, tuple[Path, dict[str, str]]] = {}
    physicals: dict[Path, dict[str, str]] = {}

    # 1. Validate filament profiles
    for path in filament_files:
        kv, parse_errs = parse_ini(path)
        errors.extend(parse_errs)
        filaments[path] = kv
        rel = path.relative_to(ROOT)

        missing = [k for k in REQUIRED_FILAMENT_KEYS if k not in kv]
        if missing:
            errors.append(
                f"{rel}: missing required keys ({len(missing)}): {', '.join(missing)} "
                "(PrusaSlicer does NOT inherit missing keys in user .ini files!)"
            )

        # Cost check (mandatory > 0)
        if "filament_cost" in kv:
            try:
                cost = float(kv["filament_cost"])
                if cost <= 0:
                    errors.append(f"{rel}: filament_cost must be > 0 (got {cost})")
            except ValueError:
                errors.append(f"{rel}: filament_cost is not numeric: {kv['filament_cost']!r}")
                cost = -1.0
        else:
            cost = -1.0

        # Density check (mandatory > 0, needed for g and EUR calculation!)
        if "filament_density" in kv:
            try:
                density = float(kv["filament_density"])
                if density <= 0:
                    errors.append(f"{rel}: filament_density must be > 0 (got {density})")
            except ValueError:
                errors.append(f"{rel}: filament_density is not numeric: {kv['filament_density']!r}")
                density = -1.0
        else:
            density = -1.0

        # Material tariff & density consistency check
        fam = material_family(path, kv)
        if fam in EXPECTED_TARIFFS:
            exp_cost, exp_density = EXPECTED_TARIFFS[fam]
            if cost > 0 and abs(cost - exp_cost) > 1e-6:
                errors.append(
                    f"{rel}: filament_cost={cost} does not match FREILab {fam} tariff ({exp_cost} EUR/kg)"
                )
            if density > 0 and abs(density - exp_density) > 1e-6:
                errors.append(
                    f"{rel}: filament_density={density} does not match expected {fam} density ({exp_density} g/cm3)"
                )

        # Diameter & multiplier
        if "filament_diameter" in kv:
            try:
                if abs(float(kv["filament_diameter"]) - 1.75) > 1e-6:
                    errors.append(f"{rel}: unexpected filament_diameter={kv['filament_diameter']}")
            except ValueError:
                errors.append(f"{rel}: filament_diameter not numeric: {kv['filament_diameter']!r}")

        if "extrusion_multiplier" in kv:
            try:
                if float(kv["extrusion_multiplier"]) <= 0:
                    errors.append(f"{rel}: extrusion_multiplier must be > 0")
            except ValueError:
                errors.append(f"{rel}: extrusion_multiplier not numeric")

        # Temperatures & volumetric speed
        for tk in ("temperature", "first_layer_temperature"):
            if tk in kv:
                try:
                    if float(kv[tk]) < 170:
                        errors.append(f"{rel}: {tk}={kv[tk]} is implausibly low (< 170 C)")
                except ValueError:
                    errors.append(f"{rel}: {tk} not numeric: {kv[tk]!r}")

        if "filament_max_volumetric_speed" in kv:
            try:
                if float(kv["filament_max_volumetric_speed"]) <= 0:
                    errors.append(f"{rel}: filament_max_volumetric_speed must be > 0")
            except ValueError:
                errors.append(f"{rel}: filament_max_volumetric_speed not numeric")

        # start_filament_gcode sanity
        if "start_filament_gcode" in kv and kv["start_filament_gcode"] in ("", '""'):
            errors.append(f"{rel}: start_filament_gcode is empty")

    # 2. Validate printer profiles
    for path in printer_files:
        kv, parse_errs = parse_ini(path)
        errors.extend(parse_errs)
        printers[path.stem] = (path, kv)
        rel = path.relative_to(ROOT)

        missing = [k for k in REQUIRED_PRINTER_KEYS if k not in kv]
        if missing:
            errors.append(f"{rel}: missing required printer keys: {', '.join(missing)}")

        if not kv.get("inherits", "").strip():
            errors.append(f"{rel}: 'inherits' is empty (printer profile is detached from Prusa system preset)")

        try:
            nozzles = parse_float_list(kv.get("nozzle_diameter", ""))
            min_lh = parse_float_list(kv.get("min_layer_height", ""))
            max_lh = parse_float_list(kv.get("max_layer_height", ""))
            if not nozzles or any(n <= 0 for n in nozzles):
                errors.append(f"{rel}: invalid nozzle_diameter={kv.get('nozzle_diameter')!r}")
            if len(min_lh) != len(nozzles) or len(max_lh) != len(nozzles):
                errors.append(f"{rel}: min/max_layer_height count does not match nozzle_diameter count")
            elif any(lo >= hi for lo, hi in zip(min_lh, max_lh)):
                errors.append(f"{rel}: min_layer_height >= max_layer_height")
        except ValueError as exc:
            errors.append(f"{rel}: invalid numeric nozzle/layer height: {exc}")

        variant = kv.get("printer_variant", "")
        notes = kv.get("printer_notes", "")
        hf = parse_int_list(kv.get("nozzle_high_flow", "0"))
        if variant.startswith("HF"):
            if not hf or hf[0] != 1:
                errors.append(f"{rel}: printer_variant={variant!r} requires nozzle_high_flow[0]=1")
            if "HF_NOZZLE" not in notes:
                errors.append(f"{rel}: printer_variant={variant!r} requires HF_NOZZLE in printer_notes")

    # 3. Validate physical printers
    active_printer_presets: set[str] = set()
    for path in physical_files:
        kv, parse_errs = parse_ini(path)
        errors.extend(parse_errs)
        physicals[path] = kv
        rel = path.relative_to(ROOT)

        preset = kv.get("preset_name", "").strip()
        if not preset:
            errors.append(f"{rel}: preset_name is empty")
        elif preset not in printers:
            errors.append(f"{rel}: preset_name {preset!r} does not match any printer/*.ini file")
        else:
            active_printer_presets.add(preset)

        if not kv.get("print_host", "").strip():
            errors.append(f"{rel}: print_host is empty")

    # 4. Cross-check matrix: Printer <-> Filament matching
    print("=== FREILab Profile Matrix ===")
    matched_filaments_anywhere: set[Path] = set()

    for pname, (ppath, pkv) in sorted(printers.items()):
        is_active = pname in active_printer_presets
        tag = "ACTIVE" if is_active else "backup"
        matched: list[Path] = []

        for fpath, fkv in filaments.items():
            cond = fkv.get("compatible_printers_condition", "")
            try:
                if eval_condition(cond, pkv):
                    matched.append(fpath)
                    matched_filaments_anywhere.add(fpath)
            except ValueError as exc:
                errors.append(f"{fpath.relative_to(ROOT)}: failed to evaluate condition against {pname}: {exc}")

        nozzles = parse_float_list(pkv.get("nozzle_diameter", "0.4"))
        hf_flags = parse_int_list(pkv.get("nozzle_high_flow", "0"))
        notes = pkv.get("printer_notes", "")
        is_hf_single = len(nozzles) == 1 and hf_flags[0] == 1
        is_hf_notes = "HF_NOZZLE" in notes

        print(f"\n[{tag}] {pname} (nozzle={pkv.get('nozzle_diameter')}, hf={pkv.get('nozzle_high_flow')})")
        families_present: set[str] = set()
        for fpath in matched:
            fkv = filaments[fpath]
            fam = material_family(fpath, fkv) or "?"
            families_present.add(fam)
            print(
                f"  - {fpath.stem:36s} | cost={fkv.get('filament_cost', '?'):>5s} EUR/kg "
                f"| dens={fkv.get('filament_density', '?'):>4s} "
                f"| mvs={fkv.get('filament_max_volumetric_speed', '?'):>4s} "
                f"| T={fkv.get('temperature', '?')}/{fkv.get('bed_temperature', '?')} C"
            )
            if fam == "TPU" and (is_hf_single or is_hf_notes):
                errors.append(
                    f"Lab rule violation: TPU profile {fpath.name!r} matches HF printer {pname!r}!"
                )

        if is_active:
            for req_fam in ("PLA", "PETG"):
                if req_fam not in families_present:
                    errors.append(f"Active printer {pname!r} has NO matching {req_fam} filament profile!")

    # Check for orphan filament profiles (allow XL 0.6mm manual-swap profiles explicitly)
    for fpath in filaments:
        if fpath not in matched_filaments_anywhere:
            if "0.6mm (XL)" in fpath.name:
                continue
            warnings.append(f"{fpath.relative_to(ROOT)}: does not match any printer/*.ini profile")

    print("\n=== Validation Result ===")
    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  WARN: {w}")
    if errors:
        print(f"FAILED with {len(errors)} error(s):")
        for e in errors:
            print(f"  ERROR: {e}")
        return 1

    print(f"OK: {len(filament_files)} filaments, {len(printer_files)} printers, {len(physical_files)} physical printers verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
