import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest

from stocks_io import StockItem
from units import parse_concentration
from calculator import TargetComponent, compute_recipe


def _get_line(result, name: str):
    for line in result.lines:
        if line.name == name:
            return line
    raise KeyError(f"Missing line '{name}' in recipe output.")


def test_stock_solution_molar_target_volume():
    # 1 M Tris stock, want 50 mM final in 100 mL:
    # Vadd = Cfinal/Cstock * Vfinal = 0.05/1 * 100 mL = 5 mL = 5000 uL
    stocks = {
        "Tris-HCl": StockItem(
            name="Tris-HCl",
            type="stock_solution",
            concentration=parse_concentration(1.0, "M"),
        )
    }

    result = compute_recipe(
        stocks=stocks,
        targets=[TargetComponent("Tris-HCl", 50, "mM")],
        final_volume_value=100,
        final_volume_unit="mL",
        output_volume_unit="uL",
    )

    line = _get_line(result, "Tris-HCl")
    assert line.source_type == "stock_solution"
    assert line.add_volume_unit == "uL"
    assert line.add_volume_value == pytest.approx(5000.0, rel=1e-9)


def test_stock_solution_massvol_target_volume():
    # 10 mg/mL BSA stock, want 1 mg/mL final in 10 mL:
    # Vadd = 1/10 * 10 mL = 1 mL = 1000 uL
    stocks = {
        "BSA": StockItem(
            name="BSA",
            type="stock_solution",
            concentration=parse_concentration(10.0, "mg/mL"),
        )
    }

    result = compute_recipe(
        stocks=stocks,
        targets=[TargetComponent("BSA", 1.0, "mg/mL")],
        final_volume_value=10,
        final_volume_unit="mL",
        output_volume_unit="uL",
    )

    line = _get_line(result, "BSA")
    assert line.add_volume_value == pytest.approx(1000.0, rel=1e-9)


def test_powder_molar_target_mass():
    # NaCl powder MW=58.44 g/mol, want 150 mM in 100 mL:
    # moles = 0.150 mol/L * 0.1 L = 0.015 mol
    # grams = 0.015 * 58.44 = 0.8766 g = 876.6 mg
    stocks = {
        "NaCl": StockItem(
            name="NaCl",
            type="powder",
            mw_g_per_mol=58.44,
            purity_fraction=1.0,
        )
    }

    result = compute_recipe(
        stocks=stocks,
        targets=[TargetComponent("NaCl", 150, "mM")],
        final_volume_value=100,
        final_volume_unit="mL",
        output_mass_unit="mg",
    )

    line = _get_line(result, "NaCl")
    assert line.source_type == "powder"
    assert line.add_mass_unit == "mg"
    assert line.add_mass_value == pytest.approx(876.6, rel=1e-6)


def test_powder_purity_adjustment_adds_warning_and_increases_mass():
    # Same as above but purity=0.9 => required mass / 0.9
    stocks = {
        "NaCl": StockItem(
            name="NaCl",
            type="powder",
            mw_g_per_mol=58.44,
            purity_fraction=0.9,
        )
    }

    result = compute_recipe(
        stocks=stocks,
        targets=[TargetComponent("NaCl", 150, "mM")],
        final_volume_value=100,
        final_volume_unit="mL",
        output_mass_unit="mg",
    )

    line = _get_line(result, "NaCl")
    assert line.add_mass_value == pytest.approx(876.6 / 0.9, rel=1e-6)
    assert any("purity_fraction" in w for w in result.warnings)


def test_bring_to_final_volume_line_exists():
    stocks = {
        "Tris-HCl": StockItem(
            name="Tris-HCl",
            type="stock_solution",
            concentration=parse_concentration(1.0, "M"),
        )
    }

    result = compute_recipe(
        stocks=stocks,
        targets=[TargetComponent("Tris-HCl", 50, "mM")],
        final_volume_value=100,
        final_volume_unit="mL",
        output_volume_unit="uL",
    )

    line = _get_line(result, "Bring to final volume (solvent/buffer)")
    assert line.add_volume_value is not None
    assert line.add_volume_value == pytest.approx(100000.0 - 5000.0, rel=1e-9)  # 100 mL = 100000 uL


def test_mismatched_target_and_stock_type_raises():
    # molar target but mass/vol stock should raise
    stocks = {
        "Tris-HCl": StockItem(
            name="Tris-HCl",
            type="stock_solution",
            concentration=parse_concentration(10.0, "mg/mL"),
        )
    }

    with pytest.raises(ValueError):
        compute_recipe(
            stocks=stocks,
            targets=[TargetComponent("Tris-HCl", 50, "mM")],
            final_volume_value=100,
            final_volume_unit="mL",
        )


def test_volvol_stock_solution_target_volume():
    # 100% glycerol stock, want 10% final in 100 mL:
    # Vadd = fraction_final/fraction_stock * Vfinal = 0.1/1.0 * 100 mL = 10 mL = 10000 uL
    stocks = {
        "Glycerol": StockItem(
            name="Glycerol",
            type="stock_solution",
            concentration=parse_concentration(100, "%"),
        )
    }

    result = compute_recipe(
        stocks=stocks,
        targets=[TargetComponent("Glycerol", 10, "%")],
        final_volume_value=100,
        final_volume_unit="mL",
        output_volume_unit="uL",
    )

    line = _get_line(result, "Glycerol")
    assert line.source_type == "stock_solution"
    assert line.add_volume_unit == "uL"
    assert line.add_volume_value == pytest.approx(10000.0, rel=1e-9)


def test_volvol_with_powder_raises():
    # v/v% cannot be used with powder stocks
    stocks = {
        "NaCl": StockItem(
            name="NaCl",
            type="powder",
            mw_g_per_mol=58.44,
            purity_fraction=1.0,
        )
    }

    with pytest.raises(ValueError):
        compute_recipe(
            stocks=stocks,
            targets=[TargetComponent("NaCl", 10, "%")],
            final_volume_value=100,
            final_volume_unit="mL",
        )
