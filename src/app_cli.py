from __future__ import annotations

import argparse
from typing import List

from stocks_io import read_stocks_xlsx, stocks_to_dict
from calculator import TargetComponent, compute_recipe
from export import export_recipe_csv


def parse_targets(target_args: List[str]) -> List[TargetComponent]:
    """
    Accepts repeated: --target "Tris-HCl,50,mM"
                      --target "NaCl,150,mM"
                      --target "BSA,0.1,mg/mL"
    """
    targets: List[TargetComponent] = []
    for s in target_args:
        parts = [p.strip() for p in s.split(",")]
        if len(parts) != 3:
            raise ValueError(f"Invalid --target format: '{s}'. Use 'Name,value,unit'")
        name, value_s, unit = parts
        targets.append(TargetComponent(name=name, final_value=float(value_s), final_unit=unit))
    return targets


def main() -> None:
    p = argparse.ArgumentParser(description="Buffer Builder (stocks + targets -> recipe)")
    p.add_argument("--stocks", required=True, help="Path to stocks .xlsx")
    p.add_argument("--sheet", default="stocks", help="Sheet name inside the xlsx (default: stocks)")
    p.add_argument("--final-volume", required=True, type=float, help="Final volume value")
    p.add_argument("--final-unit", default="mL", help="Final volume unit (e.g., mL, uL, L)")
    p.add_argument("--target", action="append", default=[], help="Target 'Name,value,unit' (repeatable)")
    p.add_argument("--out", default="", help="Output CSV path (optional)")
    p.add_argument("--vol-unit", default="uL", help="Output volume unit for additions (default uL)")
    p.add_argument("--mass-unit", default="mg", help="Output mass unit for powders (default mg)")

    args = p.parse_args()

    items = read_stocks_xlsx(args.stocks, sheet_name=args.sheet)
    stocks = stocks_to_dict(items)

    targets = parse_targets(args.target)
    result = compute_recipe(
        stocks=stocks,
        targets=targets,
        final_volume_value=args.final_volume,
        final_volume_unit=args.final_unit,
        output_volume_unit=args.vol_unit,
        output_mass_unit=args.mass_unit,
    )

    print(f"Final volume: {result.final_volume_value} {result.final_volume_unit}")
    if result.warnings:
        print("\nWARNINGS:")
        for w in result.warnings:
            print(" -", w)

    print("\nRECIPE:")
    for line in result.lines:
        if line.source_type == "powder":
            print(f"- {line.name}: {line.add_mass_value:.6g} {line.add_mass_unit}  ({line.notes})")
        else:
            print(f"- {line.name}: {line.add_volume_value:.6g} {line.add_volume_unit}  ({line.notes})")

    if args.out:
        export_recipe_csv(result, args.out)
        print(f"\nSaved CSV: {args.out}")


if __name__ == "__main__":
    main()
