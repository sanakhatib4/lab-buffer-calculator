import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest

from units import (
    to_liters,
    from_liters,
    to_grams,
    from_grams,
    molar_to_M,
    M_to_molar,
    massvol_to_g_per_L,
    g_per_L_to_massvol,
    volvol_to_fraction,
    fraction_to_volvol,
    parse_concentration,
)


def test_volume_roundtrip():
    x = 12.34
    for unit in ["uL", "mL", "L", "nL"]:
        L = to_liters(x, unit)
        back = from_liters(L, unit)
        assert back == pytest.approx(x, rel=1e-12, abs=0.0)


def test_mass_roundtrip():
    x = 5.678
    for unit in ["ng", "ug", "mg", "g"]:
        g = to_grams(x, unit)
        back = from_grams(g, unit)
        assert back == pytest.approx(x, rel=1e-12, abs=0.0)


def test_molar_conversions():
    assert molar_to_M(1, "M") == pytest.approx(1.0)
    assert molar_to_M(1, "mM") == pytest.approx(1e-3)
    assert molar_to_M(250, "uM") == pytest.approx(250e-6)
    assert M_to_molar(1e-3, "mM") == pytest.approx(1.0)
    assert M_to_molar(250e-6, "uM") == pytest.approx(250.0)


def test_massvol_conversions():
    # base is g/L
    assert massvol_to_g_per_L(1, "g/L") == pytest.approx(1.0)
    assert massvol_to_g_per_L(1, "mg/mL") == pytest.approx(1.0)   # 1 mg/mL = 1 g/L
    assert massvol_to_g_per_L(100, "ug/mL") == pytest.approx(0.1)  # 100 ug/mL = 0.1 g/L

    assert g_per_L_to_massvol(1.0, "mg/mL") == pytest.approx(1.0)
    assert g_per_L_to_massvol(0.1, "ug/mL") == pytest.approx(100.0)


def test_parse_concentration_kind():
    c1 = parse_concentration(50, "mM")
    assert c1.kind == "molar"
    assert c1.as_M() == pytest.approx(0.05)

    c2 = parse_concentration(2, "mg/mL")
    assert c2.kind == "massvol"
    assert c2.as_g_per_L() == pytest.approx(2.0)

    c3 = parse_concentration(10, "%")
    assert c3.kind == "volvol"
    assert c3.as_fraction() == pytest.approx(0.1)


def test_volvol_conversions():
    # base is fraction
    assert volvol_to_fraction(1, "%") == pytest.approx(0.01)
    assert volvol_to_fraction(50, "%") == pytest.approx(0.5)
    assert volvol_to_fraction(100, "%") == pytest.approx(1.0)
    
    assert fraction_to_volvol(0.01, "%") == pytest.approx(1.0)
    assert fraction_to_volvol(0.5, "%") == pytest.approx(50.0)
    assert fraction_to_volvol(1.0, "%") == pytest.approx(100.0)


def test_unsupported_units_raise():
    with pytest.raises(ValueError):
        to_liters(1, "cup")

    with pytest.raises(ValueError):
        molar_to_M(1, "ppm")

    with pytest.raises(ValueError):
        parse_concentration(1, "weird_unit")
