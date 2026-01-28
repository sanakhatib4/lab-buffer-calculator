from __future__ import annotations

from typing import List, Dict, Any
import csv

from calculator import RecipeResult


def recipe_to_rows(result: RecipeResult) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for line in result.lines:
        rows.append(
            {
                "name": line.name,
                "source_type": line.source_type,
                "add_volume_value": line.add_volume_value if line.add_volume_value is not None else "",
                "add_volume_unit": line.add_volume_unit if line.add_volume_value is not None else "",
                "add_mass_value": line.add_mass_value if line.add_mass_value is not None else "",
                "add_mass_unit": line.add_mass_unit if line.add_mass_value is not None else "",
                "notes": line.notes or "",
            }
        )
    return rows


def export_recipe_csv(result: RecipeResult, path: str) -> None:
    rows = recipe_to_rows(result)
    fieldnames = [
        "name",
        "source_type",
        "add_volume_value",
        "add_volume_unit",
        "add_mass_value",
        "add_mass_unit",
        "notes",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
