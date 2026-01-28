from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Number = float


def _norm_unit(u: str) -> str:
    if not u:
        return ""
    return u.strip().replace("µ", "u").replace("μ", "u")


# -------- Volume --------
_VOLUME_TO_L = {
    "l": 1.0,
    "ml": 1e-3,
    "ul": 1e-6,
    "nl": 1e-9,
}

# -------- Mass --------
_MASS_TO_G = {
    "g": 1.0,
    "mg": 1e-3,
    "ug": 1e-6,
    "ng": 1e-9,
}

# -------- Amount (moles) --------
_MOL_TO_MOL = {
    "mol": 1.0,
    "mmol": 1e-3,
    "umol": 1e-6,
    "nmol": 1e-9,
    "pmol": 1e-12,
}

# -------- Concentration: molar --------
_MOLAR_TO_M = {
    "m": 1.0,
    "mm": 1e-3,
    "um": 1e-6,
    "nm": 1e-9,
    "pm": 1e-12,
}

# -------- Concentration: mass/vol --------
# base = g/L
_MASSVOL_TO_G_PER_L = {
    "g/l": 1.0,
    "mg/ml": 1.0,      # 1 mg/mL = 1 g/L
    "ug/ml": 1e-3,     # 1 ug/mL = 1e-3 g/L
    "ng/ml": 1e-6,
    "mg/l": 1e-3,
    "ug/ul": 1.0,      # 1 ug/uL = 1 g/L
}

# -------- Concentration: volume/volume (v/v%) --------
# base = fraction (0.01 = 1%)
_VOLVOL_TO_FRACTION = {
    "%": 0.01,         # 1% (v/v) = 0.01 fraction
    "v/v%": 0.01,
}


def to_liters(value: Number, unit: str) -> Number:
    u = _norm_unit(unit).lower()
    if u not in _VOLUME_TO_L:
        raise ValueError(f"Unsupported volume unit: {unit}")
    return float(value) * _VOLUME_TO_L[u]


def from_liters(liters: Number, unit: str) -> Number:
    u = _norm_unit(unit).lower()
    if u not in _VOLUME_TO_L:
        raise ValueError(f"Unsupported volume unit: {unit}")
    return float(liters) / _VOLUME_TO_L[u]


def to_grams(value: Number, unit: str) -> Number:
    u = _norm_unit(unit).lower()
    if u not in _MASS_TO_G:
        raise ValueError(f"Unsupported mass unit: {unit}")
    return float(value) * _MASS_TO_G[u]


def from_grams(grams: Number, unit: str) -> Number:
    u = _norm_unit(unit).lower()
    if u not in _MASS_TO_G:
        raise ValueError(f"Unsupported mass unit: {unit}")
    return float(grams) / _MASS_TO_G[u]


def to_moles(value: Number, unit: str) -> Number:
    u = _norm_unit(unit).lower()
    if u not in _MOL_TO_MOL:
        raise ValueError(f"Unsupported amount unit: {unit}")
    return float(value) * _MOL_TO_MOL[u]


def from_moles(moles: Number, unit: str) -> Number:
    u = _norm_unit(unit).lower()
    if u not in _MOL_TO_MOL:
        raise ValueError(f"Unsupported amount unit: {unit}")
    return float(moles) / _MOL_TO_MOL[u]


def molar_to_M(value: Number, unit: str) -> Number:
    u = _norm_unit(unit).lower()
    if u not in _MOLAR_TO_M:
        raise ValueError(f"Unsupported molar unit: {unit}")
    return float(value) * _MOLAR_TO_M[u]


def M_to_molar(M: Number, unit: str) -> Number:
    u = _norm_unit(unit).lower()
    if u not in _MOLAR_TO_M:
        raise ValueError(f"Unsupported molar unit: {unit}")
    return float(M) / _MOLAR_TO_M[u]


def massvol_to_g_per_L(value: Number, unit: str) -> Number:
    u = _norm_unit(unit).lower()
    if u not in _MASSVOL_TO_G_PER_L:
        raise ValueError(f"Unsupported mass/vol unit: {unit}")
    return float(value) * _MASSVOL_TO_G_PER_L[u]


def g_per_L_to_massvol(g_per_L: Number, unit: str) -> Number:
    u = _norm_unit(unit).lower()
    if u not in _MASSVOL_TO_G_PER_L:
        raise ValueError(f"Unsupported mass/vol unit: {unit}")
    return float(g_per_L) / _MASSVOL_TO_G_PER_L[u]


def volvol_to_fraction(value: Number, unit: str) -> Number:
    u = _norm_unit(unit).lower()
    if u not in _VOLVOL_TO_FRACTION:
        raise ValueError(f"Unsupported v/v unit: {unit}")
    return float(value) * _VOLVOL_TO_FRACTION[u]


def fraction_to_volvol(fraction: Number, unit: str) -> Number:
    u = _norm_unit(unit).lower()
    if u not in _VOLVOL_TO_FRACTION:
        raise ValueError(f"Unsupported v/v unit: {unit}")
    return float(fraction) / _VOLVOL_TO_FRACTION[u]


@dataclass(frozen=True)
class Concentration:
    """Represents molar (M), mass/volume (g/L), or volume/volume (v/v) concentration."""
    kind: Literal["molar", "massvol", "volvol"]
    value: float
    unit: str

    def as_M(self) -> float:
        if self.kind != "molar":
            raise ValueError("Concentration is not molar.")
        return molar_to_M(self.value, self.unit)

    def as_g_per_L(self) -> float:
        if self.kind != "massvol":
            raise ValueError("Concentration is not mass/vol.")
        return massvol_to_g_per_L(self.value, self.unit)

    def as_fraction(self) -> float:
        if self.kind != "volvol":
            raise ValueError("Concentration is not v/v.")
        return volvol_to_fraction(self.value, self.unit)


def parse_concentration(value: float, unit: str) -> Concentration:
    u = _norm_unit(unit).lower()
    if u in _MOLAR_TO_M:
        return Concentration("molar", float(value), u)
    if u in _MASSVOL_TO_G_PER_L:
        return Concentration("massvol", float(value), u)
    if u in _VOLVOL_TO_FRACTION:
        return Concentration("volvol", float(value), u)
    raise ValueError(f"Unrecognized concentration unit: {unit}")
