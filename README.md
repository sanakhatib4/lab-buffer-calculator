# Buffer Builder: A Stock-Aware Buffer Composition Calculator for Biochemists

---

## Project motivation

Preparing buffers is a routine but critical task in biochemical and molecular biology laboratories.  
Despite being common, buffer preparation often requires repetitive manual calculations that are time-consuming, error-prone, and mentally demanding—especially when working under time pressure or with complex buffers containing many components.

This project aims to build a **simple, user-friendly application** that helps researchers quickly calculate buffer compositions based on available stock solutions. The goal is to reduce calculation time, minimize mistakes, and standardize buffer preparation, while keeping the tool lightweight and practical for everyday laboratory use.

The project is intentionally designed to make the lives of many biochemists like me easier!

---

## Project description

This project proposes the development of an automated **buffer composition calculator** designed to assist biochemists in preparing laboratory buffers quickly and accurately. The tool allows users to define their laboratory stock solutions once, after which the program automatically remembers and reuses this information for future calculations. Users then only need to specify the desired buffer recipe—final volume and target concentrations—and the application outputs precise pipetting volumes for each component.

The calculator supports commonly used concentration units (`nM`, `µM`, `mM`, `M`, and `mg/mL`) and is designed to be tolerant to minor input errors, including automatic correction of reagent name typos. To improve practical usability, the program detects when calculated volumes fall below 1 µL and suggests the closest feasible intermediate dilution, helping prevent common pipetting inaccuracies in the lab.

Overall, the project focuses on building a **simple and reliable tool** that mirrors real biochemical workflows. By prioritizing usability, clarity, and realistic laboratory constraints, the application aims to reduce repetitive manual calculations and provide a small but meaningful productivity improvement for experimental researchers.

