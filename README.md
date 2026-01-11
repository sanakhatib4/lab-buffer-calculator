# Buffer Builder: A Stock-Aware Buffer Composition Calculator for Biochemists

---

## Project Motivation

Preparing buffers is a routine but critical task in biochemical and molecular biology laboratories.  
Despite being common, buffer preparation often requires repetitive manual calculations that are time-consuming, error-prone, and mentally demanding—especially when working under time pressure or with complex buffers containing many components.

This project aims to build a **simple, user-friendly application** that helps researchers quickly calculate buffer compositions based on available stock solutions. The goal is to reduce calculation time, minimize mistakes, and standardize buffer preparation, while keeping the tool lightweight and practical for everyday laboratory use.

The project is intentionally designed to be closely aligned with real laboratory workflows.

---

## Project Description

The proposed application allows a user to define a buffer recipe by specifying:
- the final buffer volume
- the desired final concentration of each component

Based on **predefined stock** concentrations, the program calculates how much volume of each stock solution should be added to reach the target concentrations.

---

## Required Inputs

The application requires the following inputs:

1. **Stock solutions information**
   - Name of each reagent
   - Stock concentration
   - Stock concentration unit  
     (supported units: `nM`, `µM`, `mM`, `M`, `mg/mL`)

2. **Buffer recipe**
   - Final desired buffer volume
   - List of buffer components
   - Desired final concentration for each component (same supported units)

3. **Optional user interaction**
   - Confirmation or correction of reagent names if a typo is detected

---

## Key Features

### 1. Flexible Unit Support
The application supports concentration units commonly used in biochemistry:
- molar units: `nM`, `µM`, `mM`, `M`
- mass concentration: `mg/mL`


---

### 2. Automatic Volume Calculation
For each buffer component, the program calculates:
- the volume of stock solution required (in `µL` or `mL`)
- the remaining volume to be completed with solvent (e.g., water or buffer base)


---

### 3. Intelligent Dilution Suggestions
If the calculated volume of a stock solution is **less than 1 µL**, the program:
- flags this as impractical for accurate pipetting
- automatically suggests the **closest reasonable intermediate dilution** (e.g. 1:10, 1:50, 1:100)
- recalculates the volume to pipette from the diluted stock

---

### 4. Typo-Tolerant Ingredient Matching
To improve usability, the program includes automatic correction of reagent names:
- detects likely spelling mistakes in user input
- suggests or applies the closest matching reagent name
- prevents failed lookups due to minor typos

---

### 5. User-Friendly Design
The project is designed with a clear separation between:
- calculation logic
- user interaction

---

## Expected Outputs

For a given buffer recipe, the application outputs:

- A clear list of buffer components
- For each component:
  - stock concentration
  - desired final concentration
  - volume to add (µL or mL)
- Suggested intermediate dilutions when necessary
- Final instructions that can be followed directly during buffer preparation



The final result will be a small but genuinely useful application that reflects both programming skills and domain-specific understanding.
