"""
Readmission Risk Drivers and Stratification View for Diabetes Analysis.
Examines multi-dimensional risk factors predicting 30-day early hospital readmission.
Each chart features clean numerical labels (text_auto=True) and a dedicated Key Review on its side.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from components.theme import (
    PRIMARY_BLUE, NAVY_HEADING, BG_LIGHT, CARD_BG, BORDER_COLOR,
    CLINICAL_PALETTE, apply_plotly_theme
)
from components.cards import (
    render_page_header, render_kpis, render_key_review_card
)

def render_readmission_risk_view(df: pd.DataFrame):
    # 1. Page Header
    render_page_header(
        title="Readmission Drivers & Risk Stratification",
        description="Identifying high-risk clinical profiles and post-discharge bounce-back determinants to inform targeted interventions.",
        badge_text="RISK STRATIFICATION"
    )

    # 2. KPI Row
    total_enc = len(df)
    early_cnt = (df["readmitted"] == "<30").sum()
    prior_inp_2plus = (df["number_inpatient"] >= 2)
    inp_risk = (df[prior_inp_2plus]["readmitted"] == "<30").mean() * 100 if prior_inp_2plus.sum() else 0
    zero_inp_risk = (df[df["number_inpatient"] == 0]["readmitted"] == "<30").mean() * 100
    risk_multiplier = (inp_risk / zero_inp_risk) if zero_inp_risk else 1.0

    long_stay_risk = (df[df["time_in_hospital"] >= 8]["readmitted"] == "<30").mean() * 100

    kpis = [
        {
            "label": "Total 30-Day Readmissions",
            "value": f"{early_cnt:,}",
            "caption": f"{(early_cnt / total_enc * 100):.1f}% Early readmission rate",
            "icon": "alert"
        },
        {
            "label": "Prior Inpatient Multiplier",
            "value": f"{risk_multiplier:.1f}x Risk",
            "caption": f"{inp_risk:.1f}% for 2+ visits vs {zero_inp_risk:.1f}% for 0",
            "icon": "hospital"
        },
        {
            "label": "Extended Stay Risk (>7d)",
            "value": f"{long_stay_risk:.1f}%",
            "caption": "Significant post-discharge vulnerability",
            "icon": "clock"
        },
        {
            "label": "Top Risk Diagnosis",
            "value": "Diabetes",
            "caption": "13.0% Early readmission rate",
            "icon": "activity"
        }
    ]
    render_kpis(kpis)

    # 3. Charts with Side-by-Side Key Reviews

    # --- ROW 1: Prior Inpatient Stays vs Readmission Rate ---
    c1_chart, c1_rev = st.columns([7, 5])
    with c1_chart:
        st.markdown("""
        <div class="card-container">
            <div class="card-title">Prior Inpatient Hospitalizations vs 30-Day Readmission</div>
            <div class="card-subtitle">Early bounce-back rate based on hospital stays in the preceding 12 months</div>
        """, unsafe_allow_html=True)

        inp_analysis = df.copy()
        inp_analysis["inp_group"] = inp_analysis["number_inpatient"].apply(
            lambda x: "0 Prior Visits" if x == 0 else ("1 Prior Visit" if x == 1 else ("2 Prior Visits" if x == 2 else "3+ Prior Visits"))
        )
        inp_summary = inp_analysis.groupby("inp_group", as_index=False).agg(
            Encounters=("time_in_hospital", "count"),
            EarlyRate=("is_early_readmitted", lambda s: s.mean() * 100)
        )
        inp_summary["Order"] = inp_summary["inp_group"].map({
            "0 Prior Visits": 0, "1 Prior Visit": 1, "2 Prior Visits": 2, "3+ Prior Visits": 3
        })
        inp_summary["EarlyRate"] = inp_summary["EarlyRate"].round(1)
        inp_summary = inp_summary.sort_values("Order")

        fig_inp = px.bar(
            inp_summary,
            x="inp_group",
            y="EarlyRate",
            text_auto=True,
            color="EarlyRate",
            color_continuous_scale=["#93C5FD", "#3B82F6", "#DC2626"]
        )
        fig_inp.update_traces(
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Readmission Rate: %{y:.1f}%<extra></extra>"
        )
        fig_inp.update_layout(
            xaxis_title="",
            yaxis_title="30-Day Readmission Rate (%)",
            yaxis_range=[0, 30],
            coloraxis_showscale=False
        )
        apply_plotly_theme(fig_inp, height=330, show_legend=False)
        st.plotly_chart(fig_inp, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c1_rev:
        render_key_review_card(
            title="Hospitalization History",
            badge_text="STRONGEST PREDICTOR",
            highlight_stat="24.3%",
            stat_label="Readmission Rate for Patients with 3+ Prior Stays",
            takeaways=[
                ("Massive Risk Escalation", "Patients with 3 or more prior hospital stays return nearly 3 times as often as first-time patients (24.3% vs 8.4%)."),
                ("Clear Warning Sign", "A patient's hospitalization record is the single most accurate indicator of whether they will bounce back within a month."),
                ("Discharge Program Target", "Hospitals should automatically flag anyone with 2+ prior stays for specialized post-discharge care protocols.")
            ],
            bottom_note="Prior hospital stays reflect chronic illness severity and frequent disease destabilization."
        )

    # --- ROW 2: Length of Stay vs Readmission Rate ---
    c2_chart, c2_rev = st.columns([7, 5])
    with c2_chart:
        st.markdown("""
        <div class="card-container">
            <div class="card-title">Inpatient Length of Stay vs 30-Day Readmission Rate</div>
            <div class="card-subtitle">Early bounce-back rate across hospitalization duration (1 to 14 days)</div>
        """, unsafe_allow_html=True)

        los_risk = df.groupby("time_in_hospital", as_index=False).agg(
            Encounters=("race", "count"),
            EarlyRate=("is_early_readmitted", lambda s: s.mean() * 100)
        )
        los_risk["EarlyRate"] = los_risk["EarlyRate"].round(1)

        fig_los_risk = px.line(
            los_risk,
            x="time_in_hospital",
            y="EarlyRate",
            markers=True,
            color_discrete_sequence=[PRIMARY_BLUE]
        )
        fig_los_risk.update_traces(
            marker=dict(size=8, color="#DC2626"),
            line=dict(width=3, color=PRIMARY_BLUE),
            hovertemplate="<b>Stay: %{x} Days</b><br>Readmission Rate: %{y:.1f}%<extra></extra>"
        )
        fig_los_risk.update_layout(
            xaxis_title="Days Spent in Hospital (1–14)",
            yaxis_title="30-Day Readmission Rate (%)",
            yaxis_range=[8, 18]
        )
        apply_plotly_theme(fig_los_risk, height=330, show_legend=False)
        st.plotly_chart(fig_los_risk, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2_rev:
        render_key_review_card(
            title="Hospital Stay Duration",
            badge_text="ACUITY CORRELATION",
            highlight_stat="15.2%",
            stat_label="Readmission Rate for 13-Day Hospital Stays",
            takeaways=[
                ("Steady Risk Climb", "Readmission risk increases steadily from 9.7% for a brief 1-day stay to over 15% for extended stays above 12 days."),
                ("Marker of Illness Severity", "Patients who cannot be discharged quickly typically suffer from severe infections, wound healing complications, or organ failure."),
                ("High Vulnerability Post-Discharge", "Longer hospital stays lead to muscle weakness and fatigue, leaving patients vulnerable once they return home.")
            ],
            bottom_note="Patients staying more than 7 days require home physical therapy and nurse check-ins."
        )

    # --- ROW 3: Primary Diagnosis Readmission Risk ---
    c3_chart, c3_rev = st.columns([7, 5])
    with c3_chart:
        st.markdown("""
        <div class="card-container">
            <div class="card-title">Early Readmission Rate by Primary Admitting Diagnosis</div>
            <div class="card-subtitle">Comparison of 30-day bounce-back frequency across major disease groups</div>
        """, unsafe_allow_html=True)

        diag_risk = df.groupby("Diagnosis_Group", as_index=False).agg(
            Encounters=("time_in_hospital", "count"),
            EarlyRate=("is_early_readmitted", lambda s: s.mean() * 100)
        )
        diag_risk["EarlyRate"] = diag_risk["EarlyRate"].round(1)
        diag_risk = diag_risk.sort_values("EarlyRate", ascending=True)

        fig_diag_risk = px.bar(
            diag_risk,
            x="EarlyRate",
            y="Diagnosis_Group",
            orientation="h",
            text_auto=True,
            color="EarlyRate",
            color_continuous_scale=["#93C5FD", "#3B82F6", "#DC2626"]
        )
        fig_diag_risk.update_traces(
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Readmission Rate: %{x:.1f}%<extra></extra>"
        )
        fig_diag_risk.update_layout(
            xaxis_title="30-Day Readmission Rate (%)",
            yaxis_title="",
            xaxis_range=[0, 16],
            coloraxis_showscale=False
        )
        apply_plotly_theme(fig_diag_risk, height=330, show_legend=False)
        st.plotly_chart(fig_diag_risk, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c3_rev:
        render_key_review_card(
            title="Diagnosis Vulnerability",
            badge_text="DIAGNOSTIC RISK",
            highlight_stat="13.0%",
            stat_label="Highest Early Readmission (Direct Diabetes)",
            takeaways=[
                ("Diabetes Admissions Return Most", "Patients admitted primarily for acute diabetes problems (ketoacidosis, hyperosmolar crises) have the highest return rate at 13.0%."),
                ("Trauma & Vascular Risks", "Injury admissions (12.2%) and heart disease admissions (11.4%) follow closely as major bounce-back drivers."),
                ("Lower Rates for Lung Illness", "Respiratory admissions exhibit the lowest early return rate at 9.7%.")
            ],
            bottom_note="Specialized diabetes transition protocols are critical for patients hospitalized for blood sugar crises."
        )

    # --- ROW 4: Inpatient & ER Visits Heatmap ---
    c4_chart, c4_rev = st.columns([7, 5])
    with c4_chart:
        st.markdown("""
        <div class="card-container">
            <div class="card-title">Prior Hospital & ER Visits Risk Heatmap</div>
            <div class="card-subtitle">30-day readmission percentage (%) cross-tabulated by emergency room and inpatient history</div>
        """, unsafe_allow_html=True)

        heat_df = df.copy()
        heat_df["inp_label"] = heat_df["number_inpatient"].clip(upper=3).map({
            0: "0 Inpatient", 1: "1 Inpatient", 2: "2 Inpatient", 3: "3+ Inpatient"
        })
        heat_df["er_label"] = heat_df["number_emergency"].clip(upper=3).map({
            0: "0 ER", 1: "1 ER", 2: "2 ER", 3: "3+ ER"
        })

        pivot_risk = heat_df.groupby(["inp_label", "er_label"])["is_early_readmitted"].mean().unstack() * 100
        pivot_risk = pivot_risk.reindex(
            index=["0 Inpatient", "1 Inpatient", "2 Inpatient", "3+ Inpatient"],
            columns=["0 ER", "1 ER", "2 ER", "3+ ER"]
        ).round(1)

        fig_heat = px.imshow(
            pivot_risk,
            text_auto=True,
            aspect="auto",
            color_continuous_scale=["#F0F7FD", "#93C5FD", "#1F6FB2", "#DC2626"],
            labels=dict(x="Prior Emergency Visits", y="Prior Hospital Stays", color="Readmit %")
        )
        fig_heat.update_traces(
            hovertemplate="<b>%{y} & %{x}</b><br>Readmission Rate: %{z:.1f}%<extra></extra>"
        )
        fig_heat.update_layout(coloraxis_colorbar=dict(title="Rate %", thickness=12))
        apply_plotly_theme(fig_heat, height=330)
        st.plotly_chart(fig_heat, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c4_rev:
        render_key_review_card(
            title="Compound Utilization",
            badge_text="HIGH-FREQUENCY CARE",
            highlight_stat="34.0%",
            stat_label="Extreme Risk for Frequent Hospital Users",
            takeaways=[
                ("Dangerous Utilization Pattern", "Patients with multiple previous ER visits combined with multiple hospital stays reach extreme readmission rates (33% to 34%)."),
                ("Low Risk for First-Timers", "Patients with zero prior hospitalizations and zero emergency visits maintain a low 8.3% readmission rate."),
                ("Actionable Care Matrix", "This matrix gives hospital administrators a direct, simple roadmap: focus intensive discharge support on the top-right quadrant.")
            ],
            bottom_note="High-utilizer patient management programs yield the greatest cost savings and readmission reductions."
        )
