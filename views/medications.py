"""
Medication Regimens and Pharmacotherapy View for Diabetes Analysis.
Examines diabetes medication prescribing, dosage titration, and multi-drug therapy.
Each chart features clean numerical labels (text_auto=True) and a dedicated Key Review on its side.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from components.theme import (
    PRIMARY_BLUE, NAVY_HEADING, BG_LIGHT, CARD_BG, BORDER_COLOR,
    CLINICAL_PALETTE, apply_plotly_theme
)
from components.cards import (
    render_page_header, render_kpis, render_card_title, render_key_review_card
)

def render_medications_view(df: pd.DataFrame):
    # 1. Page Header
    render_page_header(
        title="Pharmacotherapy & Medication Regimens",
        description="Analysis of antidiabetic drug regimens, active dosage modifications, and the impact of polypharmacy on patient outcomes.",
        badge_text="PHARMACOTHERAPY DYNAMICS"
    )

    # 2. KPI Row
    total_enc = len(df)
    med_prescribed = (df["diabetesMed"] == "Yes").sum()
    med_prescribed_pct = (med_prescribed / total_enc * 100) if total_enc else 0
    dose_changed = (df["change"] == "Ch").sum()
    dose_changed_pct = (dose_changed / total_enc * 100) if total_enc else 0
    avg_diab_drugs = df["number_diabetic_drugs"].mean() if total_enc else 0
    multi_drug = (df["number_diabetic_drugs"] >= 2).sum()
    multi_drug_pct = (multi_drug / total_enc * 100) if total_enc else 0

    kpis = [
        {
            "label": "Prescribed Diabetes Meds",
            "value": f"{med_prescribed_pct:.1f}%",
            "caption": f"{med_prescribed:,} Patient encounters",
            "icon": "pill"
        },
        {
            "label": "Dosage Modification Rate",
            "value": f"{dose_changed_pct:.1f}%",
            "caption": f"{dose_changed:,} Active regimen changes",
            "icon": "activity"
        },
        {
            "label": "Average Diabetic Drugs",
            "value": f"{avg_diab_drugs:.2f} Drugs",
            "caption": "Range: 0 to 4 concurrent agents",
            "icon": "pill"
        },
        {
            "label": "Multi-Drug Polypharmacy",
            "value": f"{multi_drug_pct:.1f}%",
            "caption": f"{multi_drug:,} on 2+ diabetic agents",
            "icon": "shield"
        }
    ]
    render_kpis(kpis)

    # 3. Charts with Side-by-Side Key Reviews

    # --- ROW 1: Medication Dosage Change vs Readmission ---
    c1_chart, c1_rev = st.columns([7, 5])
    with c1_chart:
        with st.container(border=True):
            render_card_title(
                title="Medication Change vs Readmission Outcomes",
                subtitle="Outcome proportions (%) for encounters with dosage changes vs unchanged regimens"
            )

            change_cross = pd.crosstab(df["change"], df["readmitted"], normalize="index") * 100
            change_plot = change_cross.reset_index().melt(id_vars="change", value_name="Percentage", var_name="Outcome")
            change_plot["ChangeLabel"] = change_plot["change"].map({"Ch": "Medication Changed", "No": "No Change"})
            change_plot["OutcomeLabel"] = change_plot["Outcome"].map({
                "NO": "No Readmission",
                ">30": "Readmitted > 30d",
                "<30": "Early (< 30d)"
            })
            change_plot["Percentage"] = change_plot["Percentage"].round(1)

            fig_chg = px.bar(
                change_plot,
                x="ChangeLabel",
                y="Percentage",
                color="OutcomeLabel",
                barmode="group",
                text_auto=True,
                color_discrete_map={
                    "No Readmission": "#1F6FB2",
                    "Readmitted > 30d": "#60A5FA",
                    "Early (< 30d)": "#DC2626"
                }
            )
            fig_chg.update_traces(
                textposition="outside",
                hovertemplate="<b>%{x} - %{data.name}</b><br>Share: %{y:.1f}%<extra></extra>"
            )
            fig_chg.update_layout(xaxis_title="", yaxis_title="Cohort Proportion (%)", yaxis_range=[0, 65])
            apply_plotly_theme(fig_chg, height=330)
            st.plotly_chart(fig_chg, use_container_width=True)

    with c1_rev:
        render_key_review_card(
            title="Medication Titration",
            badge_text="REGIMEN ADJUSTMENT",
            highlight_stat="11.8% vs 10.6%",
            stat_label="Changed vs Unchanged 30-Day Readmission",
            takeaways=[
                ("Proactive Dosing Changes", "Doctors changed diabetes medication doses in 46.2% of hospital visits (47,003 encounters)."),
                ("Why Changed Patients Return", "Patients who had medication adjustments show slightly higher readmission (11.8% vs 10.6%) because doctors only change medications when a patient's diabetes is unstable."),
                ("Discharge Counseling Needed", "When a patient receives new medication doses, clear discharge instructions are essential to prevent confusion at home.")
            ],
            bottom_note="Patients with changed prescriptions should have a pharmacist review their medications prior to discharge."
        )

    # --- ROW 2: Concurrent Diabetic Drugs vs Readmission ---
    c2_chart, c2_rev = st.columns([7, 5])
    with c2_chart:
        with st.container(border=True):
            render_card_title(
                title="Number of Concurrent Diabetes Drugs vs 30-Day Readmission",
                subtitle="Early bounce-back rate across patients taking 0, 1, 2, 3, or 4 diabetes medications"
            )

            drug_risk = df.groupby("number_diabetic_drugs", as_index=False).agg(
                Encounters=("time_in_hospital", "count"),
                EarlyRate=("is_early_readmitted", lambda s: s.mean() * 100)
            )
            drug_risk["EarlyRate"] = drug_risk["EarlyRate"].round(1)

            fig_drugs = px.bar(
                drug_risk,
                x="number_diabetic_drugs",
                y="EarlyRate",
                text_auto=True,
                color_discrete_sequence=[PRIMARY_BLUE]
            )
            fig_drugs.update_traces(
                textposition="outside",
                hovertemplate="<b>%{x} Drugs</b><br>Early Readmission Rate: %{y:.1f}%<extra></extra>"
            )
            fig_drugs.update_layout(
                xaxis_title="Number of Concurrent Diabetes Drugs",
                yaxis_title="30-Day Readmission Rate (%)",
                yaxis_range=[0, 16]
            )
            apply_plotly_theme(fig_drugs, height=330, show_legend=False)
            st.plotly_chart(fig_drugs, use_container_width=True)

    with c2_rev:
        render_key_review_card(
            title="Polypharmacy Risks",
            badge_text="DRUG BURDEN",
            highlight_stat="13.4%",
            stat_label="Readmission Rate on 4 Diabetes Drugs",
            takeaways=[
                ("Multi-Drug Complexity", "Readmission risk climbs steadily with each additional diabetes drug, rising from 10.0% for 0 drugs to 13.4% for 4 drugs."),
                ("Insulin & Oral Combinations", "Patients requiring 3 or 4 medications typically have severe, long-standing diabetes with advanced complications."),
                ("Medication Adherence Challenge", "Managing 3 or more daily diabetes medications creates confusion and missed doses once the patient returns home.")
            ],
            bottom_note="Simplifying medication regimens where possible reduces patient confusion and improves compliance."
        )

    # --- ROW 3: Dosage Changes vs Inpatient Length of Stay ---
    c3_chart, c3_rev = st.columns([7, 5])
    with c3_chart:
        with st.container(border=True):
            render_card_title(
                title="Dosage Adjustments vs Hospital Stay Duration",
                subtitle="Average hospitalization days by number of active dosage changes (0, 1, or 2+)"
            )

            df_dose_grp = df.copy()
            df_dose_grp["dose_bracket"] = df_dose_grp["number_doses_changed"].apply(
                lambda x: "0 Changes" if x == 0 else ("1 Change" if x == 1 else "2+ Changes")
            )
            dose_los = df_dose_grp.groupby("dose_bracket", as_index=False)["time_in_hospital"].mean()
            dose_los["time_in_hospital"] = dose_los["time_in_hospital"].round(2)
            dose_los["order"] = dose_los["dose_bracket"].map({"0 Changes": 1, "1 Change": 2, "2+ Changes": 3})
            dose_los = dose_los.sort_values("order")

            fig_dose_los = px.bar(
                dose_los,
                x="dose_bracket",
                y="time_in_hospital",
                text_auto=True,
                color_discrete_sequence=["#2B6CB0"]
            )
            fig_dose_los.update_traces(
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Average Stay: %{y:.2f} Days<extra></extra>"
            )
            fig_dose_los.update_layout(
                xaxis_title="",
                yaxis_title="Average Inpatient Days",
                yaxis_range=[0, 7]
            )
            apply_plotly_theme(fig_dose_los, height=320, show_legend=False)
            st.plotly_chart(fig_dose_los, use_container_width=True)

    with c3_rev:
        render_key_review_card(
            title="Titration Stays",
            badge_text="HOSPITAL STAY IMPACT",
            highlight_stat="5.52 Days",
            stat_label="Average Stay for 2+ Dosage Changes",
            takeaways=[
                ("Longer Stays for Medication Changes", "Patients who have 2 or more dosage adjustments stay an extra 1.4 days in the hospital compared to those with no changes (5.52 vs 4.14 days)."),
                ("Necessary Safety Monitoring", "Doctors keep patients longer to verify that higher doses do not cause dangerous hypoglycemia (low blood sugar)."),
                ("Care Coordination Opportunity", "The extra hospital day allows diabetes educators to teach patients how to take their newly prescribed doses.")
            ],
            bottom_note="Early inpatient medication adjustments can prevent costly post-discharge complications."
        )

    # --- ROW 4: Diabetes Medication Rate by Admitting Condition ---
    c4_chart, c4_rev = st.columns([7, 5])
    with c4_chart:
        with st.container(border=True):
            render_card_title(
                title="Diabetes Medication Prescription Rate by Admitting Condition",
                subtitle="Share (%) of patients actively receiving prescribed diabetes medications"
            )

            diag_med = pd.crosstab(df["Diagnosis_Group"], df["diabetesMed"], normalize="index") * 100
            diag_med_plot = diag_med.reset_index()
            diag_med_plot["Yes"] = diag_med_plot["Yes"].round(1)
            diag_med_plot = diag_med_plot.sort_values("Yes", ascending=True)

            fig_diag_med = px.bar(
                diag_med_plot,
                x="Yes",
                y="Diagnosis_Group",
                orientation="h",
                text_auto=True,
                color_discrete_sequence=[PRIMARY_BLUE]
            )
            fig_diag_med.update_traces(
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Medication Rate: %{x:.1f}%<extra></extra>"
            )
            fig_diag_med.update_layout(
                xaxis_title="Patients Prescribed Diabetes Medication (%)",
                yaxis_title="",
                xaxis_range=[0, 100]
            )
            apply_plotly_theme(fig_diag_med, height=320, show_legend=False)
            st.plotly_chart(fig_diag_med, use_container_width=True)

    with c4_rev:
        render_key_review_card(
            title="Condition Coverage",
            badge_text="CLINICAL ATTENTION",
            highlight_stat="88.3%",
            stat_label="Medication Rate for Primary Diabetes Admissions",
            takeaways=[
                ("High Focus During Diabetes Crises", "Patients admitted specifically for diabetes receive the highest rate of active medication management (88.3%)."),
                ("Lower Attention in Non-Diabetic Admissions", "Patients admitted for injuries (73.8%) or musculoskeletal issues receive diabetes medication less often."),
                ("Inpatient Oversight Gap", "When diabetes is not the main reason for admission, hospital teams may inadvertently deprioritize blood sugar management.")
            ],
            bottom_note="All diabetic patients, regardless of admitting diagnosis, require blood sugar monitoring during hospital stays."
        )
