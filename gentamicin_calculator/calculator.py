import math


class GentamicinCalculator:
    """Calculator for Gentamicin dosing with Cockcroft-Gault renal adjustment.

    Implements BMI, IBW (Devine), Adjusted Body Weight, and dosing rules.
    Notes on medical reasoning:
    - BMI threshold of 30: Obesity threshold; above or equal to this uses adjusted (dose determining) weight.
    - IBW (Devine): 50 kg (male) / 45.5 kg (female) + 2.3 kg per inch over 60 in.
    - Adjusted body weight: IBW + 0.4 × (Actual − IBW) to account for partial drug distribution into adipose.
    - Cockcroft-Gault constants with creatinine in µmol/L: 1.23 (male), 1.04 (female).
    - Dosing: 5 mg/kg if CrCl > 30 ml/min; 3 mg/kg if 20–30 ml/min; advise specialist if < 20 ml/min.
    """

    # Clinical constants
    OBESITY_BMI_THRESHOLD = 30.0
    MAX_DOSE_MG = 480
    HIGH_CRCL_THRESHOLD = 30.0
    LOW_CRCL_THRESHOLD = 20.0

    def __init__(self) -> None:
        pass

    # ---------------------------- Validation ----------------------------
    def _validate_common_inputs(
        self,
        weight_kg: float,
        height_cm: float,
        age_years: int,
        sex: str,
        creatinine_umol_per_l: float,
    ) -> str:
        """Validate all inputs and return normalized sex.

        Raises ValueError with a clear message for any invalid inputs.
        """
        # Numeric positivity
        for name, value in (
            ("Weight (kg)", weight_kg),
            ("Height (cm)", height_cm),
            ("Age (years)", age_years),
            ("Serum Creatinine (µmol/L)", creatinine_umol_per_l),
        ):
            if value is None:
                raise ValueError(f"{name} is required.")
            if not isinstance(value, (int, float)):
                raise ValueError(f"{name} must be a number.")
            if value <= 0:
                raise ValueError(f"{name} must be positive.")

        # Range checks
        if not (1 <= age_years <= 120):
            raise ValueError("Age must be between 1 and 120 years.")
        if not (1 <= weight_kg <= 1000):
            raise ValueError("Weight must be between 1 and 1000 kg.")
        if not (30 <= height_cm <= 300):
            raise ValueError("Height must be between 30 and 300 cm.")
        if not (1 <= creatinine_umol_per_l <= 1000):
            raise ValueError("Serum creatinine must be between 1 and 1000 µmol/L.")

        # Sex validation
        if not isinstance(sex, str):
            raise ValueError("Sex must be 'male' or 'female'.")
        normalized_sex = sex.strip().lower()
        if normalized_sex not in {"male", "female"}:
            raise ValueError("Sex must be 'male' or 'female'.")

        return normalized_sex

    # ---------------------------- Conversions ----------------------------
    @staticmethod
    def cm_to_inches(height_cm: float) -> float:
        return height_cm / 2.54

    @staticmethod
    def kg_to_lbs(weight_kg: float) -> float:
        return weight_kg * 2.2046226218

    @staticmethod
    def inches_to_feet_inches(height_inches: float) -> tuple[int, float]:
        feet = int(height_inches // 12)
        inches = height_inches - feet * 12
        return feet, inches

    # ---------------------------- Calculations ----------------------------
    def calculate_bmi(self, weight_kg: float, height_cm: float) -> float:
        """BMI = weight_kg / (height_m)^2"""
        height_m = height_cm / 100
        if height_m <= 0:
            raise ValueError("Height must be > 0 cm.")
        return weight_kg / (height_m**2)

    def calculate_ibw(self, height_cm: float, sex: str) -> tuple[float, float]:
        """Ideal Body Weight (Devine). Returns (ibw_kg, height_inches).

        Requires height > 60 inches by specification; otherwise raises.
        """
        normalized_sex = sex.strip().lower()
        height_inches = self.cm_to_inches(height_cm)
        if height_inches <= 60:
            raise ValueError("Height must be > 60 inches (152.4 cm) for IBW calculation.")

        inches_over_60 = height_inches - 60
        if normalized_sex == "male":
            ibw = 50.0 + 2.3 * inches_over_60
        else:
            ibw = 45.5 + 2.3 * inches_over_60

        if ibw <= 0:
            raise ValueError("Calculated IBW is non-physiologic; please check inputs.")

        return ibw, height_inches

    def calculate_dosing_weight(self, weight_kg: float, height_cm: float, sex: str) -> tuple[float, dict]:
        """Determine dosing weight based on BMI and potential adjusted body weight.

        Returns (dosing_weight, details_dict) where details_dict includes bmi, height_inches,
        ibw (if used), and pathway string.
        """
        bmi = self.calculate_bmi(weight_kg, height_cm)
        details: dict = {"bmi": bmi}

        if bmi < self.OBESITY_BMI_THRESHOLD:
            details.update(
                {
                    "pathway": "Normal weight pathway",
                    "height_inches": self.cm_to_inches(height_cm),
                }
            )
            return weight_kg, details

        # BMI >= 30 uses adjusted body weight
        ibw, height_inches = self.calculate_ibw(height_cm, sex)
        adjusted = ibw + 0.4 * (weight_kg - ibw)
        details.update(
            {
                "pathway": "Adjusted weight pathway",
                "height_inches": height_inches,
                "ibw": ibw,
            }
        )
        return adjusted, details

    def calculate_creatinine_clearance(
        self,
        age_years: int,
        actual_weight_kg: float,
        sex: str,
        creatinine_umol_per_l: float,
    ) -> float:
        """Cockcroft-Gault using ACTUAL weight (per spec) and SCr in µmol/L.

        Male:   CrCl = (140 - age) × weight × 1.23 / SCr
        Female: CrCl = (140 - age) × weight × 1.04 / SCr
        """
        normalized_sex = sex.strip().lower()
        denominator = creatinine_umol_per_l
        if denominator <= 0:
            raise ValueError("Serum creatinine must be > 0.")

        if normalized_sex == "male":
            factor = 1.23
        else:
            factor = 1.04

        return ((140 - age_years) * actual_weight_kg * factor) / denominator

    # ---------------------------- Dosing and Rounding ----------------------------
    @staticmethod
    def round_to_nearest_10(value: float) -> int:
        """Round to nearest 10 mg with halves rounded up (away from zero)."""
        return int(math.floor(value / 10.0 + 0.5) * 10)

    def calculate_dose(
        self,
        weight_kg: float,
        height_cm: float,
        age_years: int,
        sex: str,
        creatinine_umol_per_l: float,
    ) -> dict:
        """Full calculation pipeline returning a details dictionary to drive UI/reporting.

        Returns keys:
        - bmi, height_inches, ibw (optional), dosing_weight, pathway
        - creatinine_clearance
        - dose_mg (int) or advisory (str)
        - conversions: weight_lbs, height_feet, height_inches_remainder
        """
        normalized_sex = self._validate_common_inputs(
            weight_kg, height_cm, age_years, sex, creatinine_umol_per_l
        )

        dosing_weight, details = self.calculate_dosing_weight(weight_kg, height_cm, normalized_sex)
        crcl = self.calculate_creatinine_clearance(age_years, weight_kg, normalized_sex, creatinine_umol_per_l)

        # Determine dose based on CrCl bands
        dose_info: dict
        if crcl > self.HIGH_CRCL_THRESHOLD:
            raw_dose = 5.0 * dosing_weight
            final_dose = min(self.MAX_DOSE_MG, self.round_to_nearest_10(raw_dose))
            dose_info = {"dose_mg": final_dose, "dose_basis": "5 mg/kg"}
        elif self.LOW_CRCL_THRESHOLD <= crcl <= self.HIGH_CRCL_THRESHOLD:
            raw_dose = 3.0 * dosing_weight
            final_dose = min(self.MAX_DOSE_MG, self.round_to_nearest_10(raw_dose))
            dose_info = {"dose_mg": final_dose, "dose_basis": "3 mg/kg"}
        else:
            dose_info = {"advisory": "Seek microbiology advice as CrCl < 20"}

        height_inches_total = details["height_inches"]
        feet, inches_remainder = self.inches_to_feet_inches(height_inches_total)
        result = {
            **details,
            "dosing_weight": dosing_weight,
            "creatinine_clearance": crcl,
            **dose_info,
            "conversions": {
                "weight_lbs": self.kg_to_lbs(weight_kg),
                "height_feet": feet,
                "height_inches_remainder": inches_remainder,
            },
        }
        return result

