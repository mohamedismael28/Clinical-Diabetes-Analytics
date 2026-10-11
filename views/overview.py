"""
Executive Overview View for Diabetes Inpatient Analysis.
Displays population KPIs, primary diagnosis mix, length of stay, and readmission breakdown.
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

def render_overview_view(df: pd.DataFrame):
    # 1. Page Header
    render_page_header(
        title="Executive Clinical Overview",
        description="High-level performance metrics, disease distributions, and hospital encounter dynamics across 101,745 inpatient diabetes admissions.",
        badge_text="POPULATION BENCHMARKS"
    )

    # 2. KPI Row
    total_enc = len(df)
    early_readm = (df["readmitted"] == "<30").sum()
    early_pct = (early_readm / total_enc * 100) if total_enc else 0
    avg_stay = df["time_in_hospital"].mean() if total_enc else 0
    med_chg = (df["change"] == "Ch").sum()
    med_pct = (med_chg / total_enc * 100) if total_enc else 0

    kpis = [
        {
            "label": "Total Encounters",
            "value": f"{total_enc:,}",
            "caption": "130 Hospitals (1999–2008)",
            "icon": "hospital"
        },
        {
            "label": "30-Day Readmission",
            "value": f"{early_pct:.1f}%",
            "caption": f"{early_readm:,} Early bounce-backs",
            "icon": "alert"
        },
        {
            "label": "Average Length of Stay",
            "value": f"{avg_stay:.2f} Days",
            "caption": "Median: 4.0 Days (Range 1–14)",
            "icon": "clock"
        },
        {
            "label": "Medication Change Rate",
            "value": f"{med_pct:.1f}%",
            "caption": f"{med_chg:,} Dosage titrations",
            "icon": "pill"
        }
    ]
    render_kpis(kpis)

    # 3. Charts with Side-by-Side Key Reviews

    # --- ROW 1: Readmission Outcome Distribution ---
    c1_chart, c1_rev = st.columns([7, 5])
    with c1_chart:
        with st.container(border=True):
            render_card_title(
                title="Readmission Outcome Distribution",
                subtitle="Hospital discharge outcomes: No Readmission vs Late (>30d) vs Early (<30d)"
            )

            readmit_df = df["readmitted"].value_counts().reset_index()
            readmit_df.columns = ["OutcomeCode", "Encounters"]
            readmit_df["OutcomeLabel"] = readmit_df["OutcomeCode"].map({
                "NO": "No Readmission",
                ">30": "Readmitted > 30 Days",
                "<30": "Early Readmitted (< 30 Days)"
            })

            fig_donut = px.pie(
                readmit_df,
                values="Encounters",
                names="OutcomeLabel",
                hole=0.5,
                color="OutcomeLabel",
                color_discrete_map={
                    "No Readmission": "#1F6FB2",
                    "Readmitted > 30 Days": "#60A5FA",
                    "Early Readmitted (< 30 Days)": "#DC2626"
                }
            )
            fig_donut.update_traces(
                textposition="inside",
                textinfo="percent+value",
                hovertemplate="<b>%{label}</b><br>Patients: %{value:,}<br>Share: %{percent}<extra></extra>"
            )
            apply_plotly_theme(fig_donut, height=330, show_legend=True)
            st.plotly_chart(fig_donut, use_container_width=True)

    with c1_rev:
        render_key_review_card(
            title="Readmission Outcomes",
            badge_text="OUTCOME SUMMARY",
            highlight_stat="46.1%",
            stat_label="Total Patient Bounce-Back Rate",
            takeaways=[
                ("High Return Rate", "Nearly half of all admitted diabetic patients (46,893 individuals) return to the hospital after discharge."),
                ("Critical Early Window", "11.2% (11,352 patients) are readmitted within 30 days, representing the most urgent target for clinical intervention."),
                ("Stable Discharges", "53.9% of encounters successfully resolve without subsequent hospital readmission during the 10-year tracking period.")
            ],
            bottom_note="Hospital readmissions within 30 days incur substantial penalties under national hospital quality programs."
        )

    # --- ROW 2: Primary Diagnosis Breakdown ---
    c2_chart, c2_rev = st.columns([7, 5])
    with c2_chart:
        with st.container(border=True):
            render_card_title(
                title="Primary Diagnosis Breakdown",
                subtitle="Number of hospital encounters by primary admitting condition (ICD-9 grouped)"
            )

            diag_counts = df["Diagnosis_Group"].value_counts().reset_index()
            diag_counts.columns = ["Diagnosis", "Encounters"]
            diag_counts = diag_counts.sort_values(by="Encounters", ascending=True)

            fig_diag = px.bar(
                diag_counts,
                x="Encounters",
                y="Diagnosis",
                orientation="h",
                text_auto=True,
                color_discrete_sequence=[PRIMARY_BLUE]
            )
            fig_diag.update_traces(
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Encounters: %{x:,}<extra></extra>"
            )
            fig_diag.update_layout(xaxis_title="Patient Encounters", yaxis_title="")
            apply_plotly_theme(fig_diag, height=330, show_legend=False)
            st.plotly_chart(fig_diag, use_container_width=True)

    with c2_rev:
        render_key_review_card(
            title="Primary Diagnoses",
            badge_text="DISEASE BURDEN",
            highlight_stat="30,437",
            stat_label="Circulatory Admissions (29.9% of All)",
            takeaways=[
                ("Heart & Vascular Dominance", "Circulatory diseases (heart disease, stroke, hypertension) are the leading cause of admission, outnumbering direct diabetes admissions by more than 3 to 1."),
                ("Respiratory & Digestive Burden", "Lung and gastrointestinal illnesses account for an additional 23.5% of total admissions combined."),
                ("Secondary Complication Pattern", "Most diabetic patients are hospitalized not for blood sugar crises alone, but for acute cardiovascular and organ damage.")
            ],
            bottom_note="Effective inpatient diabetes care requires collaboration between cardiologists and endocrinologists."
        )

    # --- ROW 3: Length of Stay Distribution ---
    c3_chart, c3_rev = st.columns([7, 5])
    with c3_chart:
        with st.container(border=True):
            render_card_title(
                title="Hospital Length of Stay (Days)",
                subtitle="Distribution of hospitalization days between admission and discharge (1–14 days)"
            )

            los_counts = df["time_in_hospital"].value_counts().sort_index().reset_index()
            los_counts.columns = ["Days", "Encounters"]

            fig_los = px.bar(
                los_counts,
                x="Days",
                y="Encounters",
                text_auto=True,
                color_discrete_sequence=["#2B6CB0"]
            )
            fig_los.update_traces(
                textposition="outside",
                hovertemplate="<b>Stay: %{x} Days</b><br>Encounters: %{y:,}<extra></extra>"
            )
            fig_los.add_vline(
                x=avg_stay,
                line_dash="dash",
                line_color="#DC2626",
                annotation_text=f"Mean: {avg_stay:.1f}d",
                annotation_position="top right"
            )
            fig_los.update_layout(xaxis_title="Days in Hospital (1–14)", yaxis_title="Number of Admissions")
            apply_plotly_theme(fig_los, height=320, show_legend=False)
            st.plotly_chart(fig_los, use_container_width=True)

    with c3_rev:
        render_key_review_card(
            title="Length of Stay Profile",
            badge_text="BED OCCUPANCY",
            highlight_stat="4.4 Days",
            stat_label="Average Hospitalization Duration",
            takeaways=[
                ("Peak Stay Window", "Over 65% of patients stay between 2 and 5 days, with 3 days being the single most common duration (17,752 encounters)."),
                ("Adequate Care Opportunity", "A 4-day inpatient stay provides ample time for hospital staff to test glucose control and adjust home prescriptions."),
                ("Extended Stays", "Less than 10% of patients remain hospitalized beyond 8 days, but these longer-stay patients consume a disproportionate share of hospital resources.")
            ],
            bottom_note="Optimizing inpatient care within the first 72 hours helps ensure safe discharge without prolonged stays."
        )

    # --- ROW 4: Admission Route Breakdown ---
 
    c4_chart, c4_rev = st.columns([7, 5])
    with c4_chart:
        with st.container(border=True):
            render_card_title(
                title="Admission Route Breakdown",
                subtitle="Patient entry point into the hospital system (Emergency, Elective, Urgent, Other)"
            )
            df['admission_type_id'] = df['admission_type_id'].replace({1: 'Emergency', 2: 'Urgent', 3: 'Elective', 4: 'Newborn', 7: 'Trauma Center', 5: 'Other', 6: 'Other', 8: 'Other'})
            admission_type = df["admission_type_id"].value_counts().reset_index()
            admission_type.columns = ["admission_type_id", "Encounters"]
            admission_type = admission_type.sort_values(by="Encounters", ascending=False)
            fig_adm = px.bar(
                admission_type,
                x="admission_type_id",
                y="Encounters",
                text_auto=True,
                color="admission_type_id",
                color_discrete_sequence=CLINICAL_PALETTE
            )
            fig_adm.update_traces(
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Encounters: %{y:,}<extra></extra>"
            )
            fig_adm.update_layout(xaxis_title="", yaxis_title="Number of Encounters")
            apply_plotly_theme(fig_adm, height=320, show_legend=False)
            st.plotly_chart(fig_adm, use_container_width=True)

    with c4_rev:
        render_key_review_card(
            title="Admission Routes",
            badge_text="ENTRY POINT",
            highlight_stat="53,979",
            stat_label="Emergency Room Admissions (53.1%)",
            takeaways=[
                ("Heavy Emergency Reliance", "More than half of all hospitalizations begin in the emergency department, pointing to sudden acute medical events."),
                ("Scheduled Surgeries & Referrals", "Elective admissions represent 18.5% (18,862 encounters), while Urgent clinic transfers make up 18.2% (18,478 encounters)."),
                ("Preventative Opportunity", "Strengthening outpatient diabetes follow-up can prevent acute crises that result in emergency room drop-ins.")
            ],
            bottom_note="Emergency admissions consistently show higher risk for complex hospitalizations and bounce-backs."
        )
