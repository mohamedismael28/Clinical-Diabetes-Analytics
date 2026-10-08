"""
Demographics and Hospital Admission View for Diabetes Analysis.
Examines age groups, gender distribution, racial cohorts, and admission routes.
Strictly excludes the 3 'Unknown/Invalid' gender rows in gender visualizations.
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
from components.data_loader import get_gender_cleaned_data, AGE_ORDER

def render_demographics_view(df: pd.DataFrame):
    # 1. Page Header
    render_page_header(
        title="Patient Demographics & Admission Patterns",
        description="Comprehensive evaluation of patient age brackets, gender profiles, racial representation, and admission pathways.",
        badge_text="DEMOGRAPHIC PROFILE"
    )

    # 2. KPI Row
    total_enc = len(df)
    gender_df = get_gender_cleaned_data(df)
    total_gender = len(gender_df)
    female_cnt = (gender_df["gender"] == "Female").sum()
    female_pct = (female_cnt / total_gender * 100) if total_gender else 0
    top_age = df["age"].mode()[0] if not df.empty else "[70-80)"
    top_age_cnt = (df["age"] == top_age).sum()
    top_age_pct = (top_age_cnt / total_enc * 100) if total_enc else 0
    cauc_cnt = (df["race"] == "Caucasian").sum()
    cauc_pct = (cauc_cnt / total_enc * 100) if total_enc else 0

    kpis = [
        {
            "label": "Predominant Age Cohort",
            "value": f"{top_age}",
            "caption": f"{top_age_cnt:,} admissions ({top_age_pct:.1f}%)",
            "icon": "users"
        },
        {
            "label": "Gender Distribution",
            "value": f"{female_pct:.1f}% F / {100-female_pct:.1f}% M",
            "caption": "Cleaned valid cohorts (101,742)",
            "icon": "users"
        },
        {
            "label": "Primary Racial Group",
            "value": "Caucasian",
            "caption": f"{cauc_cnt:,} admissions ({cauc_pct:.1f}%)",
            "icon": "hospital"
        },
        {
            "label": "African American Cohort",
            "value": "18.9%",
            "caption": f"{(df['race']=='AfricanAmerican').sum():,} admissions",
            "icon": "users"
        }
    ]
    render_kpis(kpis)

    # 3. Charts with Side-by-Side Key Reviews

    # --- ROW 1: Age Cohort Encounters ---
    c1_chart, c1_rev = st.columns([7, 5])
    with c1_chart:
        with st.container(border=True):
            render_card_title(
                title="Patient Admissions by Age Bracket",
                subtitle="Total hospital encounters across 10-year age deciles [0–10) to [90–100)"
            )

            age_summary = df.groupby("age", as_index=False).agg(
                Encounters=("time_in_hospital", "count"),
                EarlyReadmits=("is_early_readmitted", "sum")
            )
            age_summary["age_cat"] = pd.Categorical(age_summary["age"], categories=AGE_ORDER, ordered=True)
            age_summary = age_summary.sort_values("age_cat")

            fig_age = px.bar(
                age_summary,
                x="age",
                y="Encounters",
                text_auto=True,
                color_discrete_sequence=[PRIMARY_BLUE]
            )
            fig_age.update_traces(
                textposition="outside",
                hovertemplate="<b>Age %{x}</b><br>Encounters: %{y:,}<extra></extra>"
            )
            fig_age.update_layout(xaxis_title="Age Decile", yaxis_title="Patient Encounters")
            apply_plotly_theme(fig_age, height=330, show_legend=False)
            st.plotly_chart(fig_age, use_container_width=True)

    with c1_rev:
        render_key_review_card(
            title="Age Demographics",
            badge_text="AGE DISTRIBUTION",
            highlight_stat="26,064",
            stat_label="Patients in Age Group [70–80)",
            takeaways=[
                ("Senior Clustering", "Patients aged 60 and older represent nearly two-thirds (64.6%) of all hospitalizations in this study."),
                ("Low Pediatric Volume", "Children and young adults under 30 make up less than 2.5% of total admissions (2,508 encounters)."),
                ("Geriatric Care Focus", "Because older patients typically have more complex medical histories, discharge planning must focus heavily on senior support services.")
            ],
            bottom_note="Clinical protocols must be tailored to geriatric patients with reduced mobility and multiple home medications."
        )

    # --- ROW 2: Gender Distribution & Readmission Parity ---
    c2_chart, c2_rev = st.columns([7, 5])
    with c2_chart:
        with st.container(border=True):
            render_card_title(
                title="Gender Distribution & Readmission Comparison",
                subtitle="Percentage breakdown of discharge outcomes by gender (excluding 3 unclassified records)"
            )

            gender_cross = pd.crosstab(
                gender_df["gender"], 
                gender_df["readmitted"], 
                normalize="index"
            ) * 100
            gender_plot_df = gender_cross.reset_index().melt(
                id_vars="gender", 
                value_name="Percentage", 
                var_name="Outcome"
            )
            gender_plot_df["OutcomeLabel"] = gender_plot_df["Outcome"].map({
                "NO": "No Readmission",
                ">30": "Readmitted > 30d",
                "<30": "Early (< 30d)"
            })
            gender_plot_df["Percentage"] = gender_plot_df["Percentage"].round(1)

            fig_gender = px.bar(
                gender_plot_df,
                x="gender",
                y="Percentage",
                color="OutcomeLabel",
                text_auto=True,
                color_discrete_map={
                    "No Readmission": "#1F6FB2",
                    "Readmitted > 30d": "#60A5FA",
                    "Early (< 30d)": "#DC2626"
                }
            )
            fig_gender.update_traces(
                textposition="outside",
                hovertemplate="<b>%{x} - %{data.name}</b><br>Share: %{y:.1f}%<extra></extra>"
            )
            fig_gender.update_layout(
                barmode="group",
                xaxis_title="Gender",
                yaxis_title="Proportion of Gender Cohort (%)"
            )
            apply_plotly_theme(fig_gender, height=330)
            st.plotly_chart(fig_gender, use_container_width=True)

    with c2_rev:
        render_key_review_card(
            title="Gender Balance & Outcomes",
            badge_text="GENDER COMPARISON",
            highlight_stat="11.2% vs 11.1%",
            stat_label="Female vs Male 30-Day Readmission Rate",
            takeaways=[
                ("Balanced Patient Population", "Women account for 53.8% (54,703 encounters) and men account for 46.2% (47,039 encounters)."),
                ("Identical Outcome Risk", "Early 30-day readmission is 11.2% for women and 11.1% for men, demonstrating nearly identical post-discharge trajectories."),
                ("Cleaned Records", "In accordance with study criteria, 3 encounters coded as 'Unknown/Invalid' were excluded from this gender comparison.")
            ],
            bottom_note="Gender alone does not drive hospital readmission risk; clinical factors play a far larger role."
        )

    # --- ROW 3: Racial Representation Breakdown ---
    c3_chart, c3_rev = st.columns([7, 5])
    with c3_chart:
        with st.container(border=True):
            render_card_title(
                title="Hospital Admissions by Racial Cohort",
                subtitle="Total patient admissions documented across racial groups"
            )

            race_summary = df.groupby("race", as_index=False).agg(
                Encounters=("time_in_hospital", "count")
            ).sort_values("Encounters", ascending=True)

            fig_race = px.bar(
                race_summary,
                x="Encounters",
                y="race",
                orientation="h",
                text_auto=True,
                color_discrete_sequence=[PRIMARY_BLUE]
            )
            fig_race.update_traces(
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Encounters: %{x:,}<extra></extra>"
            )
            fig_race.update_layout(
                xaxis_title="Number of Patient Encounters",
                yaxis_title=""
            )
            apply_plotly_theme(fig_race, height=320, show_legend=False)
            st.plotly_chart(fig_race, use_container_width=True)

    with c3_rev:
        render_key_review_card(
            title="Racial Cohorts",
            badge_text="ETHNIC DIVERSITY",
            highlight_stat="74.8%",
            stat_label="Caucasian Share of Patient Population",
            takeaways=[
                ("Primary Demographics", "Caucasian patients (76,092) and African American patients (19,201) constitute 93.7% of all recorded hospitalizations."),
                ("Smaller Groups", "Hispanic (2,035) and Asian (640) cohorts make up smaller proportions in this multi-hospital sample."),
                ("Consistent Readmission Pattern", "Early 30-day readmissions show similar rates between Caucasian (11.3%) and African American (11.1%) patients.")
            ],
            bottom_note="Clinical protocols should remain equitable and universally applied across all racial and ethnic groups."
        )

    # --- ROW 4: Admission Route vs Length of Stay ---
    c4_chart, c4_rev = st.columns([7, 5])
    with c4_chart:
        with st.container(border=True):
            render_card_title(
                title="Admission Route vs Hospital Stay Duration",
                subtitle="Average hospitalization days by hospital admission route"
            )

            adm_los = df.groupby("admission_type_desc", as_index=False)["time_in_hospital"].mean()
            adm_los["time_in_hospital"] = adm_los["time_in_hospital"].round(2)
            adm_los = adm_los.sort_values("time_in_hospital", ascending=False).head(5)

            fig_adm_los = px.bar(
                adm_los,
                x="admission_type_desc",
                y="time_in_hospital",
                text_auto=True,
                color_discrete_sequence=["#2B6CB0"]
            )
            fig_adm_los.update_traces(
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Average Stay: %{y:.2f} Days<extra></extra>"
            )
            fig_adm_los.update_layout(xaxis_title="", yaxis_title="Average Inpatient Days")
            apply_plotly_theme(fig_adm_los, height=320, show_legend=False)
            st.plotly_chart(fig_adm_los, use_container_width=True)

    with c4_rev:
        render_key_review_card(
            title="Admission Route Impact",
            badge_text="STAY COMPARISON",
            highlight_stat="4.50 Days",
            stat_label="Emergency Average Inpatient Stay",
            takeaways=[
                ("Higher Emergency Acuity", "Patients admitted through the emergency room stay nearly half a day longer (4.50 days) than scheduled elective patients (4.04 days)."),
                ("Urgent Clinic Transfers", "Patients arriving through urgent physician referrals stay an average of 4.41 days."),
                ("Planned Procedures Are Shorter", "Elective admissions have shorter, more predictable stays, making post-discharge care easier to coordinate.")
            ],
            bottom_note="Hospital discharge teams should give extra attention to patients arriving via emergency admission."
        )
