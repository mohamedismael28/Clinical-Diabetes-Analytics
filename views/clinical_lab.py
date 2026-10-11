"""
Clinical Lab Procedures and Glycemic Monitoring View for Diabetes Analysis.
Examines the impact of HbA1c testing, serum glucose, and diagnostic volume.
Grounded in the research findings of Strack et al. (2014).
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

def render_clinical_lab_view(df: pd.DataFrame):
    # 1. Page Header
    render_page_header(
        title="Glycemic Monitoring & Clinical Testing",
        description="Evaluating the role of HbA1c testing, lab testing intensity, and diagnostic comorbidity in shaping inpatient outcomes.",
        badge_text="CLINICAL LAB METRICS"
    )

    # 2. KPI Row
    total_enc = len(df)
    hba1c_tested = (df["A1Cresult"] != "test not performed").sum()
    hba1c_pct = (hba1c_tested / total_enc * 100) if total_enc else 0
    hba1c_high = (df["A1Cresult"] == ">8").sum()
    avg_lab = df["num_lab_procedures"].mean() if total_enc else 0
    avg_diag = df["number_diagnoses"].mean() if total_enc else 0

    kpis = [
        {
            "label": "HbA1c Testing Rate",
            "value": f"{hba1c_pct:.1f}%",
            "caption": f"{hba1c_tested:,} Tested ({total_enc - hba1c_tested:,} Untested)",
            "icon": "lab"
        },
        {
            "label": "Elevated HbA1c (>8%)",
            "value": f"{hba1c_high:,}",
            "caption": f"{(hba1c_high / hba1c_tested * 100):.1f}% of tested patients",
            "icon": "alert"
        },
        {
            "label": "Average Lab Tests",
            "value": f"{avg_lab:.1f} Tests",
            "caption": "Range: 1–132 procedures",
            "icon": "activity"
        },
        {
            "label": "Average Diagnoses",
            "value": f"{avg_diag:.1f} Diagnoses",
            "caption": "High multi-morbidity burden",
            "icon": "shield"
        }
    ]
    render_kpis(kpis)

    # 3. Charts with Side-by-Side Key Reviews

    # --- ROW 1: HbA1c Test Ordering Breakdown ---
    c1_chart, c1_rev = st.columns([7, 5])
    with c1_chart:
        with st.container(border=True):
            render_card_title(
                title="HbA1c Blood Sugar Test Ordering",
                subtitle="Distribution of hemoglobin A1c testing across all 101,745 inpatient admissions"
            )

            a1c_counts = df["A1Cresult"].value_counts().reset_index()
            a1c_counts.columns = ["ResultCode", "Encounters"]
            a1c_counts["ResultLabel"] = a1c_counts["ResultCode"].map({
                "test not performed": "Untested (No Lab)",
                ">8": "Elevated (>8%)",
                "Norm": "Normal",
                ">7": "Moderately High (>7%)"
            })

            fig_a1c_donut = px.pie(
                a1c_counts,
                values="Encounters",
                names="ResultLabel",
                hole=0.55,
                color="ResultLabel",
                color_discrete_map={
                    "Untested (No Lab)": "#93C5FD",
                    "Normal": "#10B981",
                    "Moderately High (>7%)": "#F59E0B",
                    "Elevated (>8%)": "#DC2626"
                }
            )
            fig_a1c_donut.update_traces(
                textposition="inside",
                textinfo="percent+value",
                hovertemplate="<b>%{label}</b><br>Patients: %{value:,}<br>Share: %{percent}<extra></extra>"
            )
            apply_plotly_theme(fig_a1c_donut, height=330, show_legend=True)
            st.plotly_chart(fig_a1c_donut, use_container_width=True)

    with c1_rev:
        render_key_review_card(
            title="Testing Frequency",
            badge_text="LAB TESTING GAP",
            highlight_stat="83.3%",
            stat_label="Patients Admitted Without HbA1c Test",
            takeaways=[
                ("Infrequent Blood Testing", "In over 84,700 hospital stays, doctors did not order an HbA1c test, leaving long-term blood sugar levels unmeasured."),
                ("High Blood Sugar Found", "When the test was performed, nearly half of patients (48.3% / 8,214 patients) had high levels (>8%), showing serious blood sugar issues."),
                ("Actionable Information", "Testing HbA1c reveals whether patients have poorly managed diabetes and gives doctors the data needed to adjust treatment.")
            ],
            bottom_note="Clinical guidelines recommend checking HbA1c for every diabetic patient admitted to the hospital."
        )

    # --- ROW 2: HbA1c Testing vs 30-Day Readmission ---
    c2_chart, c2_rev = st.columns([7, 5])
    with c2_chart:
        with st.container(border=True):
            render_card_title(
                title="HbA1c Testing vs 30-Day Readmission Rate",
                subtitle="Early hospital readmission percentage (<30 days) by HbA1c test result"
            )

            a1c_readmit = df.groupby("A1Cresult", as_index=False).agg(
                Encounters=("time_in_hospital", "count"),
                EarlyRate=("is_early_readmitted", lambda s: s.mean() * 100)
            )
            a1c_readmit["Label"] = a1c_readmit["A1Cresult"].map({
                "Norm": "Normal Result",
                ">8": "Very High (>8%)",
                ">7": "High (>7%)",
                "test not performed": "Untested (No Lab)"
            })
            a1c_readmit["EarlyRate"] = a1c_readmit["EarlyRate"].round(1)
            a1c_readmit = a1c_readmit.sort_values("EarlyRate", ascending=True)

            fig_a1c_bar = px.bar(
                a1c_readmit,
                x="Label",
                y="EarlyRate",
                text_auto=True,
                color="Label",
                color_discrete_map={
                    "Normal Result": "#10B981",
                    "Very High (>8%)": "#042A67",
                    "High (>7%)": "#60A5FA",
                    "Untested (No Lab)": "#DC2626"
                }
            )
            fig_a1c_bar.update_traces(
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Early Readmission Rate: %{y:.1f}%<extra></extra>"
            )
            fig_a1c_bar.update_layout(
                xaxis_title="",
                yaxis_title="30-Day Readmission Rate (%)",
                yaxis_range=[0, 15]
            )
            apply_plotly_theme(fig_a1c_bar, height=330, show_legend=False)
            st.plotly_chart(fig_a1c_bar, use_container_width=True)

    with c2_rev:
        render_key_review_card(
            title="Readmission Protection",
            badge_text="STUDY VALIDATION",
            highlight_stat="9.6% vs 11.4%",
            stat_label="Tested Normal vs Untested 30-Day Bounce-Backs",
            takeaways=[
                ("Testing Helps Patients", "Patients who had their HbA1c checked had lower readmission rates (9.6% to 10.0%) compared to those who were not tested (11.4%)."),
                ("Confirms Published Medical Study", "This directly supports the findings of Strack et al. (2014), proving that measuring blood sugar control is linked to better outcomes."),
                ("Doctor Attention Matters", "Ordering the test prompts doctors to review medications, which helps patients leave the hospital with a safer treatment plan.")
            ],
            bottom_note="Simply performing an HbA1c test during hospitalization helps reduce return hospital visits."
        )
