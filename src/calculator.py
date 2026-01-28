from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Literal, Dict

from units import (
    to_liters,
    from_liters,
    parse_concentration,
    molar_to_M,
    massvol_to_g_per_L,
    volvol_to_fraction,
    from_grams,
)
from stocks_io import StockItem


TargetKind = Literal["molar", "massvol", "volvol"]


@dataclass
class TargetComponent:
    """What the user wants in the final buffer."""
    name: str
    final_value: float
    final_unit: str   # e.g. mM, uM, mg/mL, g/L


@dataclass
class RecipeLine:
    name: str
    source_type: Literal["stock_solution", "powder"]
    # for stock_solution
    add_volume_value: Optional[float] = None
    add_volume_unit: str = "uL"
    # for powder
    add_mass_value: Optional[float] = None
    add_mass_unit: str = "mg"
    # info
    notes: str = ""


@dataclass
class RecipeResult:
    final_volume_value: float
    final_volume_unit: str
    lines: List[RecipeLine]
    warnings: List[str]


def _target_kind_from_unit(unit: str) -> TargetKind:
    u = (unit or "").strip().lower().replace("µ", "u").replace("μ", "u")
    # molar: M, mM, uM ...
    if u in ("m", "mm", "um", "nm", "pm"):
        return "molar"
    # mass/vol
    if u in ("g/l", "mg/ml", "ug/ml", "ng/ml", "mg/l", "ug/ul"):
        return "massvol"
    # v/v percent
    if u in ("%", "v/v%"):
        return "volvol"
    raise ValueError(f"Unsupported target unit: {unit}")


def compute_recipe(
    stocks: Dict[str, StockItem],
    targets: List[TargetComponent],
    final_volume_value: float,
    final_volume_unit: str = "mL",
    output_volume_unit: str = "uL",
    output_mass_unit: str = "mg",
) -> RecipeResult:
    warnings: List[str] = []

    V_L = to_liters(final_volume_value, final_volume_unit)

    lines: List[RecipeLine] = []
    total_stock_vol_L = 0.0

    for t in targets:
        if t.name not in stocks:
            raise KeyError(f"Component '{t.name}' not found in stocks.")

        item = stocks[t.name]
        kind = _target_kind_from_unit(t.final_unit)

        if item.type == "stock_solution":
            if item.concentration is None:
                raise ValueError(f"Stock solution '{item.name}' missing concentration in stocks file.")

            # Determine stock conc in same "space" (molar or mass/vol or v/v)
            if kind == "molar":
                C_final_M = molar_to_M(t.final_value, t.final_unit)
                if item.concentration.kind != "molar":
                    raise ValueError(
                        f"Target for '{t.name}' is molar ({t.final_unit}) but stock is {item.concentration.kind} "
                        f"({item.concentration.unit}). Use a molar stock or change target unit."
                    )
                C_stock_M = item.concentration.as_M()
                if C_stock_M <= 0:
                    raise ValueError(f"Invalid stock concentration for '{t.name}'.")
                V_add_L = (C_final_M * V_L) / C_stock_M

            elif kind == "massvol":
                g_per_L_final = massvol_to_g_per_L(t.final_value, t.final_unit)
                if item.concentration.kind != "massvol":
                    raise ValueError(
                        f"Target for '{t.name}' is mass/vol ({t.final_unit}) but stock is {item.concentration.kind} "
                        f"({item.concentration.unit}). Use a mass/vol stock or change target unit."
                    )
                g_per_L_stock = item.concentration.as_g_per_L()
                if g_per_L_stock <= 0:
                    raise ValueError(f"Invalid stock concentration for '{t.name}'.")
                V_add_L = (g_per_L_final * V_L) / g_per_L_stock

            else:  # kind == "volvol"
                # For v/v%, the calculation is simple: final_fraction * final_volume = volume_to_add
                fraction_final = volvol_to_fraction(t.final_value, t.final_unit)
                if item.concentration.kind != "volvol":
                    raise ValueError(
                        f"Target for '{t.name}' is v/v ({t.final_unit}) but stock is {item.concentration.kind} "
                        f"({item.concentration.unit}). Use a v/v stock or change target unit."
                    )
                fraction_stock = item.concentration.as_fraction()
                if fraction_stock <= 0:
                    raise ValueError(f"Invalid stock concentration for '{t.name}'.")
                V_add_L = (fraction_final * V_L) / fraction_stock

            total_stock_vol_L += V_add_L
            lines.append(
                RecipeLine(
                    name=item.name,
                    source_type="stock_solution",
                    add_volume_value=from_liters(V_add_L, output_volume_unit),
                    add_volume_unit=output_volume_unit,
                    notes=(item.notes or "").strip(),
                )
            )

        elif item.type == "powder":
            # For powder, we compute mass needed for final concentration.
            # Note: v/v% is not applicable for powder stocks
            if kind == "volvol":
                raise ValueError(
                    f"Cannot use v/v% concentration ({t.final_unit}) with powder stock for '{t.name}'. "
                    f"Use molar or mass/vol units instead."
                )
            
            if kind == "massvol":
                # final g/L * V(L) = grams
                g_per_L_final = massvol_to_g_per_L(t.final_value, t.final_unit)
                grams = g_per_L_final * V_L

            else:
                # molar target requires MW
                if item.mw_g_per_mol is None or item.mw_g_per_mol <= 0:
                    raise ValueError(
                        f"Powder '{item.name}' requires mw_g_per_mol in stocks file for molar targets."
                    )
                C_final_M = molar_to_M(t.final_value, t.final_unit)
                moles = C_final_M * V_L
                grams = moles * float(item.mw_g_per_mol)

            # Correct for purity
            if item.purity_fraction < 1.0:
                grams = grams / item.purity_fraction
                warnings.append(
                    f"'{item.name}': adjusted mass for purity_fraction={item.purity_fraction:g}."
                )

            lines.append(
                RecipeLine(
                    name=item.name,
                    source_type="powder",
                    add_mass_value=from_grams(grams, output_mass_unit),
                    add_mass_unit=output_mass_unit,
                    notes=(item.notes or "").strip(),
                )
            )
        else:
            raise ValueError(f"Unknown stock type: {item.type}")

    if total_stock_vol_L > V_L:
        warnings.append(
            f"Total stock volumes ({total_stock_vol_L:.6g} L) exceed final volume "
            f"({V_L:.6g} L). Check targets/stock concentrations."
        )

    remaining_L = max(0.0, V_L - total_stock_vol_L)
    # Add "water/buffer to volume" helper line
    lines.append(
        RecipeLine(
            name="Bring to final volume (solvent/buffer)",
            source_type="stock_solution",
            add_volume_value=from_liters(remaining_L, output_volume_unit),
            add_volume_unit=output_volume_unit,
            notes="Add solvent/buffer to reach final volume.",
        )
    )

    return RecipeResult(
        final_volume_value=final_volume_value,
        final_volume_unit=final_volume_unit,
        lines=lines,
        warnings=warnings,
    )
