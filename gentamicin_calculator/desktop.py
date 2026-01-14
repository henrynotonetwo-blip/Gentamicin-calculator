import tkinter as tk
from tkinter import messagebox, ttk

from calculator import GentamicinCalculator

class GentamicinApp:
    """tkinter GUI wrapper for GentamicinCalculator."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Gentamicin Dosage Calculator")
        self.calculator = GentamicinCalculator()
        self._build_ui()

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Inputs
        self.weight_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.sex_var = tk.StringVar(value="male")
        self.creatinine_var = tk.StringVar()

        row = 0
        ttk.Label(main, text="Weight (kg):").grid(row=row, column=0, sticky="w")
        ttk.Entry(main, textvariable=self.weight_var, width=15).grid(row=row, column=1, sticky="ew")

        row += 1
        ttk.Label(main, text="Height (cm):").grid(row=row, column=0, sticky="w")
        ttk.Entry(main, textvariable=self.height_var, width=15).grid(row=row, column=1, sticky="ew")

        row += 1
        ttk.Label(main, text="Age (years):").grid(row=row, column=0, sticky="w")
        ttk.Entry(main, textvariable=self.age_var, width=15).grid(row=row, column=1, sticky="ew")

        row += 1
        ttk.Label(main, text="Sex:").grid(row=row, column=0, sticky="w")
        sex_combo = ttk.Combobox(main, textvariable=self.sex_var, values=["male", "female"], state="readonly", width=13)
        sex_combo.grid(row=row, column=1, sticky="ew")

        row += 1
        ttk.Label(main, text="Serum Creatinine (µmol/L):").grid(row=row, column=0, sticky="w")
        ttk.Entry(main, textvariable=self.creatinine_var, width=15).grid(row=row, column=1, sticky="ew")

        # Buttons
        row += 1
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=(8, 4), sticky="ew")
        ttk.Button(btn_frame, text="Calculate", command=self.on_calculate).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btn_frame, text="Clear", command=self.on_clear).grid(row=0, column=1)

        # Results
        row += 1
        ttk.Label(main, text="Results:").grid(row=row, column=0, columnspan=2, sticky="w")
        row += 1
        self.results = tk.Text(main, height=20, width=60, wrap="word")
        self.results.grid(row=row, column=0, columnspan=2, sticky="nsew")
        main.rowconfigure(row, weight=1)

    def _parse_float(self, s: str, field: str) -> float:
        try:
            return float(s)
        except (ValueError, TypeError):
            raise ValueError(f"{field} must be a number.")

    def _parse_int(self, s: str, field: str) -> int:
        try:
            v = int(float(s))  # allow '45.0'
            return v
        except (ValueError, TypeError):
            raise ValueError(f"{field} must be an integer.")

    def on_clear(self) -> None:
        self.weight_var.set("")
        self.height_var.set("")
        self.age_var.set("")
        self.sex_var.set("male")
        self.creatinine_var.set("")
        self.results.delete("1.0", tk.END)

    def on_calculate(self) -> None:
        try:
            weight = self._parse_float(self.weight_var.get(), "Weight (kg)")
            height = self._parse_float(self.height_var.get(), "Height (cm)")
            age = self._parse_int(self.age_var.get(), "Age (years)")
            sex = self.sex_var.get()
            creat = self._parse_float(self.creatinine_var.get(), "Serum Creatinine (µmol/L)")

            result = self.calculator.calculate_dose(weight, height, age, sex, creat)
            self._display_result(weight, height, age, sex, creat, result)
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def _display_result(self, weight_kg: float, height_cm: float, age: int, sex: str,
                        creat: float, result: dict) -> None:
        self.results.delete("1.0", tk.END)

        weight_lbs = result["conversions"]["weight_lbs"]
        feet = result["conversions"]["height_feet"]
        inches_rem = result["conversions"]["height_inches_remainder"]

        lines = []
        lines.append("GENTAMICIN DOSAGE CALCULATOR")
        lines.append("============================")
        lines.append("Patient Details:")
        lines.append(f"- Weight: {weight_kg:.1f} kg ({weight_lbs:.1f} lbs)")
        lines.append(f"- Height: {height_cm:.1f} cm ({feet}'{inches_rem:.0f}\")")
        lines.append(f"- Age: {age} years")
        lines.append(f"- Sex: {sex.capitalize()}")
        lines.append(f"- Serum Creatinine: {creat:.1f} µmol/L")
        lines.append("")
        lines.append("Calculations:")
        bmi = result["bmi"]
        pathway = result["pathway"]
        lines.append(f"- BMI: {bmi:.1f} kg/m² ({pathway})")

        if "ibw" in result:
            height_inches_total = result["height_inches"]
            lines.append(f"- Height (for IBW): {height_inches_total:.1f} inches")
            lines.append(f"- IBW: {result['ibw']:.1f} kg")

        lines.append(f"- Dosing Weight: {result['dosing_weight']:.1f} kg")
        lines.append(f"- Creatinine Clearance: {result['creatinine_clearance']:.1f} ml/min")

        if "dose_mg" in result:
            basis = result.get("dose_basis", "")
            lines.append(f"- Recommended Dose: {result['dose_mg']} mg (nearest 10 mg; {basis})")
        else:
            lines.append(f"- Recommendation: {result['advisory']}")

        self.results.insert("1.0", "\n".join(lines))


def main() -> None:
    root = tk.Tk()
    app = GentamicinApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()


