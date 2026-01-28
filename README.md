# Buffer Builder: A Stock-Aware Buffer Composition Calculator for Biochemists

---

## Project Motivation

Preparing buffers is a routine but critical task in biochemical and molecular biology laboratories.  
Despite being common, buffer preparation often requires repetitive manual calculations that are time-consuming, error-prone, and mentally demanding—especially when working under time pressure or with complex buffers containing many components.

The project is intentionally designed to make the lives of many biochemists like me easier!

---

## Project Description

This **buffer composition calculator** is designed to assist biochemists in preparing laboratory buffers quickly and accurately. The tool allows users to define their laboratory stock solutions once, after which the program automatically remembers and reuses this information for future calculations. Users then only need to specify the desired buffer recipe—final volume and target concentrations—and the application outputs precise pipetting volumes for each component.

---

## 🚀 What This Project Does

- ✅ Reads an Excel file of lab stocks (liquid stocks + powders)
- ✅ Lets you choose buffer components and target concentrations
- ✅ Automatically calculates volumes for liquid stocks
- ✅ Automatically calculates masses for powder reagents
- ✅ Handles unit conversions (M, mM, %, mg/mL, g/L, etc.)
- ✅ Exports results as a CSV file (ready to print or share)
- ✅ Works as both a command-line tool and GUI application

---

## 📁 Project Structure

```
lab-buffer-calculator/
├── src/
│   ├── app_cli.py          # Command-line interface
│   ├── app_gui.py          # GUI interface
│   ├── stocks_io.py        # Reading & validating Excel stock files
│   ├── units.py            # Unit conversion logic
│   ├── calculator.py       # Core buffer calculations
│   ├── fuzzy_match.py      # Smart matching of component names
│   └── export.py           # Export results to CSV
├── data/
│   └── stocks_template.xlsx # Excel template for lab stocks
├── tests/
│   ├── test_units.py
│   └── test_calculator.py
├── README.md
└── .gitignore
```

---

## 📊 Stock File (What You Need to Provide)

You must provide an Excel file describing your lab stocks with the following structure:

### Required Columns

| Column | Type | Example | Notes |
|--------|------|---------|-------|
| **name** | String | Tris-HCl | Component name |
| **type** | String | stock_solution or powder | Type of stock |
| **concentration_value** | Float | 1, 0.5 | For liquids only |
| **concentration_unit** | String | M, mM, mg/mL, % | For liquids only |
| **mw_g_per_mol** | Float | 58.44 | For powders only (molecular weight) |
| **purity_fraction** | Float | 0.98 | Optional, defaults to 1.0 |
| **solvent** | String | Water, DMSO | Optional |
| **notes** | String | pH adjusted | Optional |

**Use the provided template:** `data/stocks_template.xlsx`

---

## 🧰 Installation & Requirements

### Python Version
Python 3.9+ recommended

### Install Dependencies

```bash
pip install pandas openpyxl
```

### Optional (for GUI only)
Most systems have tkinter pre-installed with Python. If needed:
```bash
pip install tkinter
```

---

## ▶️ How to Run

### Command Line
```bash
cd lab-buffer-calculator
python src/app_cli.py --stocks data/stocks.xlsx --final-volume 100 --final-unit mL --target "Tris-HCl,50,mM" --target "NaCl,150,mM" --out buffer_recipe.csv
```

### GUI Application (Interactive)
```bash
cd lab-buffer-calculator
python src/app_gui.py
```

The GUI allows:
- File selection via dialog
- Interactive component selection
- Real-time fuzzy matching for component names
- Automatic calculation and validation
- One-click CSV export

---

## 📤 Output Example

The program generates a CSV file containing:

| name | source_type | add_volume_value | add_volume_unit | add_mass_value | add_mass_unit | notes |
|------|-------------|-----------------|-----------------|----------------|---------------|-------|
| Tris-HCl | stock_solution | 5000 | uL | | | pH 8.0 |
| NaCl | powder | | | 876.6 | mg | |
| Glycerol | stock_solution | 10000 | uL | | | v/v% |
| Bring to final volume (solvent/buffer) | stock_solution | 84124 | uL | | | Add solvent/buffer to reach final volume. |

---

## 🧠 Features

### Smart Component Matching
The tool uses fuzzy matching to automatically recognize component names, even if you make typos or use shortcuts:
- "tris ph 8" → matches "Tris-HCl pH=8"
- "imidazole" → matches "Imidazole"
- Minor typos are automatically corrected

### Multiple Concentration Types
Support for:
- **Molar**: M, mM, µM, nM, pM
- **Mass/Volume**: g/L, mg/mL, µg/mL, mg/L
- **Volume/Volume**: % (v/v%)

### Purity Corrections
Automatically accounts for reagent purity when calculating masses needed.

### Unit Conversions
Handles conversions between:
- Volume units (uL, mL, L)
- Mass units (ng, µg, mg, g)
- Concentration units

### Validation & Warnings
- Checks for impossible concentrations
- Warns if total stock volume exceeds final volume
- Validates all inputs before calculation

---

## ✅ Testing

Run the full test suite:
```bash
pytest tests/ -v
```

Test coverage includes:
- Unit conversions (all supported units)
- Buffer calculations (molar, mass/vol, v/v%)
- Purity corrections
- Error handling
- Edge cases

---

## 📚 Best Practices

1. **Validate your stock file** - Always double-check units and concentrations
2. **Use consistent naming** - Standardize component names across your lab
3. **Keep templates updated** - Maintain one shared template per lab
4. **Version control** - Commit stock templates to version control for reproducibility
5. **Export recipes** - Keep CSV exports for reference and lab notebooks

---

## 👥 Who This Is For

- Wet-lab scientists preparing buffers frequently
- Students learning buffer preparation techniques
- Labs aiming to reduce calculation mistakes
- Anyone tired of manual Excel calculations! 😄

---

## 📝 License & Usage

This tool is designed for research and educational purposes. Feel free to adapt it to your lab's needs.

