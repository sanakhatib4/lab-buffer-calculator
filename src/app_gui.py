from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from typing import List, Dict

from stocks_io import read_stocks_xlsx, stocks_to_dict, StockItem
from fuzzy_match import best_match, top_matches
from calculator import TargetComponent, compute_recipe
from export import export_recipe_csv


class BufferBuilderGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Buffer Builder")
        self.geometry("980x650")

        self.stocks_path = tk.StringVar(value="")
        self.sheet_name = tk.StringVar(value="stocks")

        self.final_volume_value = tk.StringVar(value="100")
        self.final_volume_unit = tk.StringVar(value="mL")

        self.out_vol_unit = tk.StringVar(value="uL")
        self.out_mass_unit = tk.StringVar(value="mg")

        self._stocks_items: List[StockItem] = []
        self._stocks_dict: Dict[str, StockItem] = {}

        self._build_ui()

    def _build_ui(self):
        frm_top = ttk.Frame(self, padding=10)
        frm_top.pack(fill="x")

        ttk.Label(frm_top, text="Stocks file:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm_top, textvariable=self.stocks_path, width=70).grid(row=0, column=1, sticky="we", padx=5)
        ttk.Button(frm_top, text="Browse...", command=self._browse_stocks).grid(row=0, column=2)

        ttk.Label(frm_top, text="Sheet:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(frm_top, textvariable=self.sheet_name, width=20).grid(row=1, column=1, sticky="w", padx=5, pady=(6, 0))
        ttk.Button(frm_top, text="Load stocks", command=self._load_stocks).grid(row=1, column=2, pady=(6, 0))

        frm_top.columnconfigure(1, weight=1)

        sep = ttk.Separator(self, orient="horizontal")
        sep.pack(fill="x", padx=10, pady=10)

        frm_mid = ttk.Frame(self, padding=10)
        frm_mid.pack(fill="both", expand=True)

        # Left: add target
        frm_left = ttk.LabelFrame(frm_mid, text="Add target component", padding=10)
        frm_left.pack(side="left", fill="y")

        self.target_name = tk.StringVar(value="")
        self.target_value = tk.StringVar(value="50")
        self.target_unit = tk.StringVar(value="mM")

        ttk.Label(frm_left, text="Name (as in stocks):").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm_left, textvariable=self.target_name, width=28).grid(row=1, column=0, sticky="we", pady=(0, 8))

        ttk.Label(frm_left, text="Final value:").grid(row=2, column=0, sticky="w")
        ttk.Entry(frm_left, textvariable=self.target_value, width=10).grid(row=3, column=0, sticky="w")

        ttk.Label(frm_left, text="Unit:").grid(row=4, column=0, sticky="w", pady=(8, 0))
        unit_box = ttk.Combobox(frm_left, textvariable=self.target_unit, width=10, values=[
            "M", "mM", "uM", "nM",
            "g/L", "mg/mL", "ug/mL", "mg/L",
            "%",
        ])
        unit_box.grid(row=5, column=0, sticky="w")

        ttk.Button(frm_left, text="Add target", command=self._add_target).grid(row=6, column=0, sticky="we", pady=(12, 0))
        ttk.Button(frm_left, text="Remove selected", command=self._remove_target).grid(row=7, column=0, sticky="we", pady=(6, 0))
        ttk.Button(frm_left, text="Suggest match", command=self._suggest_match).grid(row=8, column=0, sticky="we", pady=(6, 0))

        # Center: target list
        frm_center = ttk.LabelFrame(frm_mid, text="Targets", padding=10)
        frm_center.pack(side="left", fill="both", expand=True, padx=10)

        self.targets_list = tk.Listbox(frm_center, height=10)
        self.targets_list.pack(fill="both", expand=True)

        # Right: options + results
        frm_right = ttk.LabelFrame(frm_mid, text="Compute + Export", padding=10)
        frm_right.pack(side="left", fill="y")

        ttk.Label(frm_right, text="Final volume:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm_right, textvariable=self.final_volume_value, width=10).grid(row=0, column=1, sticky="w")
        ttk.Combobox(frm_right, textvariable=self.final_volume_unit, width=6, values=["uL", "mL", "L"]).grid(row=0, column=2, sticky="w")

        ttk.Label(frm_right, text="Output vol unit:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Combobox(frm_right, textvariable=self.out_vol_unit, width=6, values=["uL", "mL", "L"]).grid(row=1, column=1, sticky="w", pady=(8, 0))

        ttk.Label(frm_right, text="Output mass unit:").grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Combobox(frm_right, textvariable=self.out_mass_unit, width=6, values=["mg", "g", "ug"]).grid(row=2, column=1, sticky="w", pady=(8, 0))

        ttk.Button(frm_right, text="Compute recipe", command=self._compute).grid(row=3, column=0, columnspan=3, sticky="we", pady=(14, 0))
        ttk.Button(frm_right, text="Export CSV...", command=self._export_csv).grid(row=4, column=0, columnspan=3, sticky="we", pady=(6, 0))

        self.warnings_text = tk.Text(frm_right, height=7, width=34)
        self.warnings_text.grid(row=5, column=0, columnspan=3, sticky="we", pady=(10, 0))

        sep2 = ttk.Separator(self, orient="horizontal")
        sep2.pack(fill="x", padx=10, pady=10)

        frm_bottom = ttk.LabelFrame(self, text="Recipe", padding=10)
        frm_bottom.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        cols = ("name", "type", "add_volume", "add_mass", "notes")
        self.tree = ttk.Treeview(frm_bottom, columns=cols, show="headings", height=10)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=160 if c != "notes" else 360, anchor="w")
        self.tree.pack(fill="both", expand=True)

        self._last_result = None

    def _browse_stocks(self):
        path = filedialog.askopenfilename(
            title="Select stocks .xlsx",
            filetypes=[("Excel files", "*.xlsx")],
        )
        if path:
            self.stocks_path.set(path)

    def _load_stocks(self):
        try:
            path = self.stocks_path.get().strip()
            if not path:
                messagebox.showerror("Error", "Please choose a stocks .xlsx file.")
                return
            self._stocks_items = read_stocks_xlsx(path, sheet_name=self.sheet_name.get().strip() or "stocks")
            self._stocks_dict = stocks_to_dict(self._stocks_items)
            messagebox.showinfo("Loaded", f"Loaded {len(self._stocks_items)} stock items.")
        except Exception as e:
            messagebox.showerror("Load error", str(e))

    def _add_target(self):
        name = self.target_name.get().strip()
        if not name:
            return
        try:
            val = float(self.target_value.get().strip())
        except Exception:
            messagebox.showerror("Error", "Final value must be a number.")
            return
        unit = self.target_unit.get().strip()
        
        # Auto-match: if stocks are loaded and exact name not found, try fuzzy match
        matched_name = name
        if self._stocks_dict:
            if name not in self._stocks_dict:
                # Try fuzzy matching automatically
                m = best_match(name, self._stocks_dict.keys(), min_score=0.5)
                if m:
                    # Ask user to confirm the match
                    response = messagebox.askyesno(
                        "Fuzzy Match Found",
                        f"'{name}' not found exactly.\n\n"
                        f"Did you mean '{m.candidate}'? (score={m.score:.2f})\n\n"
                        f"Click Yes to use '{m.candidate}' or No to use '{name}' as-is."
                    )
                    if response:
                        matched_name = m.candidate
                        self.target_name.set(matched_name)  # Update the entry field
        
        self.targets_list.insert("end", f"{matched_name} | {val} {unit}")

    def _remove_target(self):
        sel = list(self.targets_list.curselection())
        sel.reverse()
        for i in sel:
            self.targets_list.delete(i)

    def _suggest_match(self):
        if not self._stocks_dict:
            messagebox.showerror("Error", "Load stocks first.")
            return
        q = self.target_name.get().strip()
        if not q:
            return
        m = best_match(q, self._stocks_dict.keys(), min_score=0.5)
        if not m:
            suggestions = top_matches(q, self._stocks_dict.keys(), n=5)
            if not suggestions:
                messagebox.showinfo("No match", "No similar names found.")
                return
            msg = "\n".join([f"{s.candidate}  (score={s.score:.2f})" for s in suggestions])
            messagebox.showinfo("Suggestions", msg)
            return
        self.target_name.set(m.candidate)
        messagebox.showinfo("Match", f"Best match: {m.candidate} (score={m.score:.2f})")

    def _parse_targets_from_listbox(self) -> List[TargetComponent]:
        targets: List[TargetComponent] = []
        for i in range(self.targets_list.size()):
            s = self.targets_list.get(i)
            # "Name | value unit"
            try:
                left, right = [x.strip() for x in s.split("|", 1)]
                val_s, unit = right.split(None, 1)
                targets.append(TargetComponent(name=left, final_value=float(val_s), final_unit=unit.strip()))
            except Exception:
                raise ValueError(f"Cannot parse target line: '{s}'")
        return targets

    def _compute(self):
        if not self._stocks_dict:
            messagebox.showerror("Error", "Load stocks first.")
            return
        try:
            targets = self._parse_targets_from_listbox()
            fv = float(self.final_volume_value.get().strip())
            fu = self.final_volume_unit.get().strip()
            result = compute_recipe(
                stocks=self._stocks_dict,
                targets=targets,
                final_volume_value=fv,
                final_volume_unit=fu,
                output_volume_unit=self.out_vol_unit.get().strip(),
                output_mass_unit=self.out_mass_unit.get().strip(),
            )
            self._last_result = result

            # warnings
            self.warnings_text.delete("1.0", "end")
            if result.warnings:
                self.warnings_text.insert("end", "WARNINGS:\n" + "\n".join(f"- {w}" for w in result.warnings))
            else:
                self.warnings_text.insert("end", "No warnings.")

            # table
            for row in self.tree.get_children():
                self.tree.delete(row)

            for line in result.lines:
                add_vol = ""
                add_mass = ""
                if line.add_volume_value is not None:
                    add_vol = f"{line.add_volume_value:.6g} {line.add_volume_unit}"
                if line.add_mass_value is not None:
                    add_mass = f"{line.add_mass_value:.6g} {line.add_mass_unit}"

                self.tree.insert(
                    "", "end",
                    values=(line.name, line.source_type, add_vol, add_mass, line.notes)
                )

        except Exception as e:
            messagebox.showerror("Compute error", str(e))

    def _export_csv(self):
        if not self._last_result:
            messagebox.showerror("Error", "Compute a recipe first.")
            return
        path = filedialog.asksaveasfilename(
            title="Save recipe as CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return
        try:
            export_recipe_csv(self._last_result, path)
            messagebox.showinfo("Saved", f"Saved CSV:\n{path}")
        except Exception as e:
            messagebox.showerror("Export error", str(e))


def main():
    app = BufferBuilderGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
