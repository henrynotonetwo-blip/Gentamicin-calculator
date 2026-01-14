## Gentamicin Dosage Calculator (Python + tkinter)

### Overview
This application computes a recommended Gentamicin dose using BMI-based dosing weight selection and the Cockcroft–Gault equation for renal function, then applies dosing rules by creatinine clearance bands. It includes a simple GUI (tkinter), detailed output with intermediate values, and automated tests.


### How it works
The calculation pipeline follows these exact steps:

1) BMI calculation
- Formula: BMI = weight_kg / (height_m)^2, where height_m = height_cm / 100.

2) Dosing weight determination
- If BMI < 30: dosing_weight = actual_weight_kg (normal pathway).
- If BMI ≥ 30: use adjusted pathway:
  - Convert height_cm → inches.
  - Male IBW = 50 + 2.3 × (inches − 60)
  - Female IBW = 45.5 + 2.3 × (inches − 60)
  - Adjusted (Dose Determining) Weight = IBW + 0.4 × (actual − IBW)
  - dosing_weight = adjusted weight

3) Creatinine clearance (Cockcroft–Gault)
- Important: Uses actual body weight (the input weight), not the dosing weight.
- Male: CrCl = (140 − age) × actual_weight_kg × 1.23 / serum_creatinine
- Female: CrCl = (140 − age) × actual_weight_kg × 1.04 / serum_creatinine

4) Final dose calculation
- If CrCl > 30: dose = 5 × dosing_weight (mg)
- If 20 ≤ CrCl ≤ 30: dose = 3 × dosing_weight (mg)
- If CrCl < 20: advise “Seek microbiology advice as CrCl < 20”
- Rounding: final recommended dose is rounded to the nearest 10 mg (half-up), then capped at a maximum of 480 mg.

5) Display and unit conversions
- Height is also shown in feet/inches.
- Weight is also shown in pounds (lbs).
- All intermediate values are shown with units and to 1 decimal place (final dose is a whole number mg).

### Inputs and validation
- Weight (kg): positive; 1–500
- Height (cm): positive; 30–300
- Age (years): integer; 1–120
- Sex: “male” or “female” (case-insensitive)
- Serum creatinine (µmol/L): 10–1000

If BMI ≥ 30, height must be > 60 inches for IBW to be valid. Non-physiologic results raise specific errors.

### Output
The app prints a labeled summary including:
- BMI and pathway used
- Height in inches (for IBW), IBW (if BMI ≥ 30)
- Dosing weight (kg)
- Creatinine clearance (ml/min)
- Recommended dose (mg) or an advisory message

Example (abbreviated):
```
GENTAMICIN DOSAGE CALCULATOR
============================
Patient Details:
- Weight: 85.0 kg (187.4 lbs)
- Height: 175.0 cm (5'9")
- Age: 45 years
- Sex: Male
- Serum Creatinine: 120.0 µmol/L

Calculations:
- BMI: 27.8 kg/m² (Normal weight pathway)
- Dosing Weight: 85.0 kg
- Creatinine Clearance: 82.8 ml/min
- Recommended Dose: 430 mg (nearest 10 mg; 5 mg/kg)
```

### Running the app
From a PowerShell window:


### Pre-built Windows executable
If you have the generated `.exe`, run:
```
dist\GentamicinCalculator.exe
```

### Run as a website (local)
You do **not** need to buy a domain to do this. You can run the calculator locally first, then deploy it, and only add a custom domain later if you want.

1) Install Python dependencies (from the project root):
```
python -m pip install -r requirements.txt
```

2) Start the web app (from `Gentmicin Calculator Code\Calculator Code`):
```
python -m streamlit run streamlit_app.py
```

Streamlit will open a local URL (usually `http://localhost:8501`) that works like a website in your browser.

### Domain / deployment (high level)
- If you deploy to a hosting provider, you’ll get a temporary/public URL first.
- Buying a domain is optional and can be done afterwards to point to the deployed app.


