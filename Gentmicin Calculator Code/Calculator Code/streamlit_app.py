import streamlit as st

from calculator import GentamicinCalculator


st.set_page_config(page_title="Gentamicin Dose Calculator", layout="centered")

st.title("Gentamicin Dose Calculator")
st.caption("Educational tool. Follow local guidelines and clinical judgement.")

calc = GentamicinCalculator()

with st.form("inputs"):
    col1, col2 = st.columns(2)
    with col1:
        weight_kg = st.number_input(
            "Weight (kg)",
            min_value=0.0,
            value=st.session_state.get("weight_kg", 70.0),
            step=0.1,
            format="%.1f",
            key="weight_kg",
        )
        height_cm = st.number_input(
            "Height (cm)",
            min_value=0.0,
            value=st.session_state.get("height_cm", 170.0),
            step=0.1,
            format="%.1f",
            key="height_cm",
        )
        age_years = st.number_input(
            "Age (years)", min_value=0, value=st.session_state.get("age_years", 40), step=1, key="age_years"
        )
    with col2:
        sex = st.selectbox(
            "Sex", ["male", "female"], index=0 if st.session_state.get("sex", "male") == "male" else 1, key="sex"
        )
        creatinine_umol_per_l = st.number_input(
            "Serum creatinine (µmol/L)",
            min_value=0.0,
            value=st.session_state.get("creatinine_umol_per_l", 100.0),
            step=1.0,
            format="%.1f",
            key="creatinine_umol_per_l",
        )

    submitted = st.form_submit_button("Calculate")
    # Use a callback for Clear so session state changes happen in a controlled callback context
    def _clear_inputs():
        st.session_state["weight_kg"] = 70.0
        st.session_state["height_cm"] = 170.0
        st.session_state["age_years"] = 40
        st.session_state["sex"] = "male"
        st.session_state["creatinine_umol_per_l"] = 100.0
        # Remove any stored report/result indicators
        for k in ["_gentamicin_result", "gentamicin_report"]:
            if k in st.session_state:
                del st.session_state[k]
        # Rerun to immediately reflect cleared UI
        st.experimental_rerun()

    _ = st.form_submit_button("Clear", on_click=_clear_inputs)

if submitted:
    try:
        result = calc.calculate_dose(
            float(st.session_state["weight_kg"]),
            float(st.session_state["height_cm"]),
            int(st.session_state["age_years"]),
            str(st.session_state["sex"]),
            float(st.session_state["creatinine_umol_per_l"]),
        )

        st.subheader("Result")

        if "dose_mg" in result:
            st.success(
                f"Recommended dose: **{result['dose_mg']} mg** ({result.get('dose_basis', '')})"
            )
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

        st.caption(
            "Dose rounding: nearest 10 mg (half-up), capped at 480 mg per current tool settings."
        )

        # Build a textual report like the desktop app
        report_lines = []
        report_lines.append("GENTAMICIN DOSAGE CALCULATOR")
        report_lines.append("============================")
        report_lines.append("Patient Details:")
        report_lines.append(
            f"- Weight: {st.session_state['weight_kg']:.1f} kg ({c['weight_lbs']:.1f} lbs)"
        )
        report_lines.append(
            f"- Height: {st.session_state['height_cm']:.1f} cm ({c['height_feet']}'{round(c['height_inches_remainder'])}\")"
        )
        report_lines.append(f"- Age: {st.session_state['age_years']} years")
        report_lines.append(f"- Sex: {str(st.session_state['sex']).capitalize()}")
        report_lines.append(
            f"- Serum Creatinine: {st.session_state['creatinine_umol_per_l']:.1f} µmol/L"
        )
        report_lines.append("")
        report_lines.append("Calculations:")
        report_lines.append(f"- BMI: {result['bmi']:.1f} kg/m² ({result['pathway']})")

        if "ibw" in result:
            report_lines.append(f"- Height (for IBW): {result['height_inches']:.1f} inches")
            report_lines.append(f"- IBW: {result['ibw']:.1f} kg")

        report_lines.append(f"- Dosing Weight: {result['dosing_weight']:.1f} kg")
        report_lines.append(f"- Creatinine Clearance: {result['creatinine_clearance']:.1f} ml/min")

        if "dose_mg" in result:
            basis = result.get("dose_basis", "")
            report_lines.append(f"- Recommended Dose: {result['dose_mg']} mg (nearest 10 mg; {basis})")
        else:
            report_lines.append(f"- Recommendation: {result.get('advisory')}")

        report_lines.append("")
        report_lines.append(
            "MEDICAL DISCLAIMER: This calculator is for educational/reference purposes only."
        )
        report_lines.append(
            "Always consult qualified healthcare professionals for actual medical decisions."
        )

        report = "\n".join(report_lines)

        st.subheader("Report")
        st.code(report, language="text")
        st.download_button("Download report", report, file_name="gentamicin_report.txt", mime="text/plain")

    except ValueError as e:
        st.error(str(e))

