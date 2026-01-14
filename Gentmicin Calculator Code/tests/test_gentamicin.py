import math
import pathlib
import sys
import pytest


# Ensure the module directory is importable (Calculator Code/)
PROJECT_DIR = pathlib.Path(__file__).resolve().parents[1] / "Calculator Code"
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


from calculator import GentamicinCalculator  # noqa: E402


def test_normal_bmi_male_crcl_gt30():
    calc = GentamicinCalculator()
    # 85 kg, 175 cm, 45 years, male, SCr 120 µmol/L
    result = calc.calculate_dose(85.0, 175.0, 45, "male", 120.0)

    assert result["pathway"] == "Normal weight pathway"
    assert "ibw" not in result
    # CrCl approx 82.77
    assert result["creatinine_clearance"] == pytest.approx(82.77, rel=1e-2)
    # Dose: 5 mg/kg of 85 kg = 425 -> nearest 10 mg => 430 mg
    assert result["dose_mg"] == 430


def test_normal_bmi_female_crcl_gt30():
    calc = GentamicinCalculator()
    result = calc.calculate_dose(60.0, 165.0, 35, "female", 80.0)

    assert result["pathway"] == "Normal weight pathway"
    # CrCl approx 81.9
    assert result["creatinine_clearance"] == pytest.approx(81.9, rel=1e-2)
    # Dose: 5 mg/kg of 60 kg = 300 mg
    assert result["dose_mg"] == 300


def test_obese_uses_adjusted_weight_and_ibw_shown():
    calc = GentamicinCalculator()
    # Obese male example: BMI > 30
    result = calc.calculate_dose(120.0, 175.0, 45, "male", 120.0)

    assert result["pathway"] == "Adjusted weight pathway"
    assert "ibw" in result
    # Dosing weight should be adjusted weight ~ 90.3 kg
    assert result["dosing_weight"] == pytest.approx(90.28, rel=1e-3)
    # Dose 5 mg/kg -> ~451.4 -> nearest 10 => 450 mg
    assert result["dose_mg"] == 450


def test_crcl_between_20_and_30_gets_3mgkg():
    calc = GentamicinCalculator()
    # Female with CrCl ~20.8
    result = calc.calculate_dose(50.0, 160.0, 80, "female", 150.0)
    assert 20 <= result["creatinine_clearance"] <= 30
    # 3 mg/kg * 50 = 150 mg
    assert result["dose_mg"] == 150


def test_crcl_below_20_advisory():
    calc = GentamicinCalculator()
    # Female with CrCl ~17.3
    result = calc.calculate_dose(50.0, 160.0, 80, "female", 180.0)
    assert result.get("advisory") == "Seek microbiology advice as CrCl < 20"
    assert "dose_mg" not in result


def test_bmi_exactly_30_uses_adjusted_pathway():
    calc = GentamicinCalculator()
    # BMI = 30 at 170 cm => weight = 30 * (1.7^2) = 86.7 kg
    weight = 30.0 * (1.7 ** 2)
    result = calc.calculate_dose(weight, 170.0, 40, "male", 100.0)
    assert result["pathway"] == "Adjusted weight pathway"
    # Expected adjusted weight ~ 74.24 kg; dose 5* -> ~371.2 => 370 mg
    assert result["dose_mg"] == 370


def test_dose_is_capped_at_480_when_crcl_gt30():
    calc = GentamicinCalculator()
    # Very tall to keep BMI < 30 so dosing weight = actual weight = 150 kg
    # Dose 5 mg/kg => 750 mg -> rounds 750 -> capped to 480 mg
    result = calc.calculate_dose(150.0, 250.0, 30, "male", 100.0)
    assert result["pathway"] == "Normal weight pathway"
    assert result["dose_mg"] == 480


def test_dose_is_capped_at_480_when_crcl_between_20_and_30():
    calc = GentamicinCalculator()
    # Keep BMI < 30 so dosing weight = 170 kg; 3 mg/kg => 510 -> capped to 480
    # Choose SCr to make CrCl ~25: (140-80)*170*1.04 / SCr = 25 -> SCr ~ 416.96
    result = calc.calculate_dose(170.0, 250.0, 80, "female", 420.0)
    assert 20 <= result["creatinine_clearance"] <= 30
    assert result["dose_mg"] == 480


def test_crcl_equal_30_uses_3mgkg_band():
    calc = GentamicinCalculator()
    # Male: (140-40)*80*1.23 / 328 = 30
    result = calc.calculate_dose(80.0, 175.0, 40, "male", 328.0)
    assert result["creatinine_clearance"] == pytest.approx(30.0, rel=1e-6)
    assert result["dose_mg"] == 240  # 3 mg/kg * 80 => 240


def test_crcl_equal_20_is_still_dosed_not_advisory():
    calc = GentamicinCalculator()
    # Female: (140-60)*50*1.04 / 208 = 20
    result = calc.calculate_dose(50.0, 165.0, 60, "female", 208.0)
    assert result["creatinine_clearance"] == pytest.approx(20.0, rel=1e-6)
    assert result["dose_mg"] == 150  # 3 mg/kg * 50 => 150


def test_obese_female_uses_adjusted_weight_and_shows_ibw():
    calc = GentamicinCalculator()
    # Obese female example to exercise IBW/adjusted pathway
    result = calc.calculate_dose(110.0, 160.0, 50, "female", 100.0)
    assert result["pathway"] == "Adjusted weight pathway"
    assert "ibw" in result

def test_invalid_inputs_raise():
    calc = GentamicinCalculator()
    # Invalid sex
    with pytest.raises(ValueError):
        calc.calculate_dose(70.0, 170.0, 40, "other", 100.0)
    # Negative weight
    with pytest.raises(ValueError):
        calc.calculate_dose(-5.0, 170.0, 40, "male", 100.0)


def test_ibw_height_validation_raises_for_short_height_when_bmi_ge_30():
    calc = GentamicinCalculator()
    # Height 150 cm (< 60 in) with BMI >= 30 must raise during IBW stage
    # Choose weight to make BMI >= 30: BMI = 90 / (1.5^2) = 40
    with pytest.raises(ValueError):
        calc.calculate_dose(90.0, 150.0, 40, "female", 100.0)


