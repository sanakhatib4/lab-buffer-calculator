from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Literal

import pandas as pd

from units import parse_concentration, Concentration


StockType = Literal["stock_solution", "powder"]


REQUIRED_COLUMNS = [
    "name",
    "type",  # stock_solution | powder
]

OPTIONAL_COLUMNS = [
    # For stock_solution
    "concentration_value",
    "concentration_unit",

    # For powder
    "mw_g_per_mol",     # required for molar-based powder calculations
    "purity_fraction",  # e.g., 0.98 (optional, defaults 1.0)

    # Helpful meta
    "solvent",
    "notes",
]


@dataclass
class StockItem:
    name: str
    type: StockType

    # Stock solution fields
    concentration: Optional[Concentration] = None

    # Powder fields
    mw_g_per_mol: Optional[float] = None
    purity_fraction: float = 1.0

    # Meta
    solvent: str = ""
    notes: str = ""


def _coerce_float(x) -> Optional[float]:
    if x is None:
        return None
    try:
        if pd.isna(x):
            return None
    except Exception:
        pass
    try:
        return float(x)
    except Exception:
        return None


def _coerce_str(x) -> str:
    if x is None:
        return ""
    try:
        if pd.isna(x):
            return ""
    except Exception:
        pass
    return str(x).strip()


def read_stocks_xlsx(path: str, sheet_name: str = "stocks") -> List[StockItem]:
    df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
    df.columns = [str(c).strip().lower() for c in df.columns]

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            raise ValueError(f"Missing required column '{col}' in stocks sheet '{sheet_name}'.")

    items: List[StockItem] = []

    for _, row in df.iterrows():
        name = _coerce_str(row.get("name"))
        if not name:
            continue

        typ = _coerce_str(row.get("type")).lower()
        if typ not in ("stock_solution", "powder"):
            raise ValueError(f"Invalid type '{typ}' for '{name}'. Use 'stock_solution' or 'powder'.")

        solvent = _coerce_str(row.get("solvent"))
        notes = _coerce_str(row.get("notes"))

        if typ == "stock_solution":
            cv = _coerce_float(row.get("concentration_value"))
            cu = _coerce_str(row.get("concentration_unit"))
            if cv is None or not cu:
                raise ValueError(
                    f"Stock solution '{name}' requires concentration_value and concentration_unit."
                )
            conc = parse_concentration(cv, cu)
            items.append(
                StockItem(
                    name=name,
                    type="stock_solution",
                    concentration=conc,
                    solvent=solvent,
                    notes=notes,
                )
            )
        else:
            mw = _coerce_float(row.get("mw_g_per_mol"))
            purity = _coerce_float(row.get("purity_fraction"))
            if purity is None:
                purity = 1.0
            if purity <= 0 or purity > 1.0:
                raise ValueError(f"purity_fraction for '{name}' must be in (0, 1].")

            items.append(
                StockItem(
                    name=name,
                    type="powder",
                    mw_g_per_mol=mw,
                    purity_fraction=float(purity),
                    solvent=solvent,
                    notes=notes,
                )
            )

    return items


def stocks_to_dict(items: List[StockItem]) -> Dict[str, StockItem]:
    return {i.name: i for i in items}
