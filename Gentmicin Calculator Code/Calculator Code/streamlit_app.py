import streamlit as st

from calculator import GentamicinCalculator


st.set_page_config(page_title="Gentamicin Dose Calculator", layout="centered")

st.title("Gentamicin Dose Calculator")
st.caption("Educational tool. Follow local guidelines and clinical judgement.")

calc = GentamicinCalculator()

with st.form("inputs"):
    col1, col2 = st.columns(2)
    with col1:
        weight_kg = st.number_input("Weight (kg)", min_value=0.0, value=70.0, step=0.1, format="%.1f")
        height_cm = st.number_input("Height (cm)", min_value=0.0, value=170.0, step=0.1, format="%.1f")
        age_years = st.number_input("Age (years)", min_value=0, value=40, step=1)
    with col2:
        sex = st.selectbox("Sex", ["male", "female"], index=0)
        creatinine_umol_per_l = st.number_input(
            "Serum creatinine (µmol/L)", min_value=0.0, value=100.0, step=1.0, format="%.1f"
        )

    submitted = st.form_submit_button("Calculate")

if submitted:
    try:
        result = calc.calculate_dose(
            float(weight_kg),
            float(height_cm),
            int(age_years),
            str(sex),
            float(creatinine_umol_per_l),
        )

        st.subheader("Result")

        if "dose_mg" in result:
            st.success(f"Recommended dose: **{result['dose_mg']} mg** ({result.get('dose_basis', '')})")
        else:
            st.warning(result.get("advisory", "No dose calculated."))

        st.divider()
        st.subheader("Details")

        c = result["conversions"]
        st.write(
            {
                "BMI (kg/m²)": round(result["bmi"], 1),
                "Pathway": result["pathway"],
                "Dosing weight (kg)": round(result["dosing_weight"], 1),
                "Creatinine clearance (mL/min)": round(result["creatinine_clearance"], 1),
                "Weight (lbs)": round(c["weight_lbs"], 1),
                "Height (ft/in)": f"{c['height_feet']}'{round(c['height_inches_remainder'])}\"",
            }
        )

        if "ibw" in result:
            st.write(
                {
                    "Height for IBW (inches)": round(result["height_inches"], 1),
                    "IBW (kg)": round(result["ibw"], 1),
                }
            )

        st.caption("Dose rounding: nearest 10 mg (half-up), capped at 480 mg per current tool settings.")

    except ValueError as e:
        st.error(str(e))

