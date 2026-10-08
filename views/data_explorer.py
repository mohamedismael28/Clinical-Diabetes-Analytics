"""
Dataset Explorer and Verification View for Diabetes Analysis.
Allows dynamic filtering, variable inspection, summary statistics, and data exporting.
Features clean data views and a side-by-side Key Review for non-technical users.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from components.theme import (
    PRIMARY_BLUE, NAVY_HEADING, BG_LIGHT, CARD_BG, BORDER_COLOR,
    apply_plotly_theme
)
from components.cards import (
    render_page_header, render_kpis, render_key_review_card
)

def render_data_explorer_view(df: pd.DataFrame):
    # 1. Page Header
    render_page_header(
        title="Interactive Clinical Dataset Explorer",
        description="Filter, search, inspect distribution statistics, and verify cleaned dataset records across all 21 analytical features.",
        badge_text="DATASET AUDIT & EXPLORATION"
    )

    # Filtering controls in a clean card container
    st.markdown("""
    <div class="card-container">
        <div class="card-title">Exploration & Segment Filters</div>
        <div class="card-subtitle">Select cohorts to dynamically update the inspection table and summary statistics below</div>
    """, unsafe_allow_html=True)

    f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)

    with f_col1:
        diag_options = ["All Diagnoses"] + sorted(df["Diagnosis_Group"].dropna().unique().tolist())
        selected_diag = st.selectbox("Primary Diagnosis", diag_options)

    with f_col2:
        readm_options = ["All Outcomes", "No Readmission (NO)", "Late (>30 Days)", "Early (<30 Days)"]
        selected_readm = st.selectbox("Readmission Status", readm_options)

    with f_col3:
        gender_options = ["All Genders", "Male", "Female"]
        selected_gender = st.selectbox("Gender", gender_options)

    with f_col4:
        age_options = ["All Ages"] + sorted(df["age"].dropna().unique().tolist())
        selected_age = st.selectbox("Age Distribution", age_options)

    with f_col5:
        race_options = ["All Races"] + sorted(df["race"].dropna().unique().tolist())
        selected_race = st.selectbox("Race Distribution", race_options)

    st.markdown("</div>", unsafe_allow_html=True)

    # Apply filters
    filtered_df = df.copy()
    filtered_df = filtered_df[filtered_df["gender"].isin(["Male", "Female"])].copy()
    if selected_diag != "All Diagnoses":
        filtered_df = filtered_df[filtered_df["Diagnosis_Group"] == selected_diag]
    if selected_readm == "No Readmission (NO)":
        filtered_df = filtered_df[filtered_df["readmitted"] == "NO"]
    elif selected_readm == "Late (>30 Days)":
        filtered_df = filtered_df[filtered_df["readmitted"] == ">30"]
    elif selected_readm == "Early (<30 Days)":
        filtered_df = filtered_df[filtered_df["readmitted"] == "<30"]

    if selected_gender != "All Genders":
        filtered_df = filtered_df[filtered_df["gender"].isin([selected_gender])]
    if selected_age != "All Ages":
        filtered_df = filtered_df[filtered_df["age"] == selected_age]
    if selected_race != "All Races":
        filtered_df = filtered_df[filtered_df["race"] == selected_race]

    # 2. KPI Row for Filtered Segment
    f_total = len(filtered_df)
    f_early = (filtered_df["readmitted"] == "<30").sum()
    f_early_pct = (f_early / f_total * 100) if f_total else 0
    f_avg_stay = filtered_df["time_in_hospital"].mean() if f_total else 0
    f_avg_meds = filtered_df["num_medications"].mean() if f_total else 0

    kpis = [
        {
            "label": "Selected Cohort Encounters",
            "value": f"{f_total:,}",
            "caption": f"{(f_total / len(df) * 100):.1f}% of total population",
            "icon": "hospital"
        },
        {
            "label": "Cohort Early Readmissions",
            "value": f"{f_early_pct:.1f}%",
            "caption": f"{f_early:,} Encounters (<30d)",
            "icon": "alert"
        },
        {
            "label": "Cohort Average Stay",
            "value": f"{f_avg_stay:.2f} Days",
            "caption": "Hospitalization length",
            "icon": "clock"
        },
        {
            "label": "Avg Medications Administered",
            "value": f"{f_avg_meds:.1f} Meds",
            "caption": "Overall pharmaceutical volume",
            "icon": "pill"
        }
    ]
    render_kpis(kpis)

    # 3. Distribution View Selector + Chart
    c_chart, c_rev = st.columns([7, 5])

    with c_chart:
        with st.container(border=True):
            st.markdown(
                "<div style='margin-bottom: 10px;'><div class='card-title'>Population Distribution</div><div class='card-subtitle'>Review the filtered cohort by age, gender, or race</div></div>",
                unsafe_allow_html=True,
            )

            dist_df = filtered_df.groupby("gender").size().reset_index(name="Encounters")
            dist_df.columns = ["Gender", "Encounters"]
            fig = px.bar(
                dist_df,
                x="Gender",
                y="Encounters",
                text_auto=True,
                color_discrete_sequence=[PRIMARY_BLUE]
            )
            fig.update_layout(xaxis_title="Gender", yaxis_title="Encounters")

            apply_plotly_theme(fig, height=330, show_legend=False)
            st.plotly_chart(fig, use_container_width=True)

    with c_rev:
        render_key_review_card(
            title="Cohort Review",
            badge_text="LIVE AUDIT",
            highlight_stat=f"{f_total:,}",
            stat_label="Patients in Selected Segment",
            takeaways=[
                ("Live Recalculation", "All statistics, charts, and record counts update automatically whenever you choose a new filter above."),
                ("Cleaned Medical Data", "The dataset includes 101,745 inpatient records. Incomplete codes and confusing abbreviations were removed for clarity."),
                ("Easy Export for Teams", "You can download any filtered group of patients as a spreadsheet using the download button below.")
            ],
            bottom_note="Use the distribution selector to quickly compare how the cohort differs by age, gender, or race."
        )

    # 4. Side-by-Side: Data Table + Export
    c_table, c_space = st.columns([7, 5])

    with c_table:
        st.markdown("""
        <div class="card-container">
            <div class="card-title">Hospital Records Data Sample</div>
            <div class="card-subtitle">Displaying first 500 matching encounters across all 21 cleaned clinical columns</div>
        """, unsafe_allow_html=True)

        display_cols = [
            "race", "gender", "age", "admission_type_desc", "time_in_hospital",
            "Diagnosis_Group", "A1Cresult", "max_glu_serum", "diabetesMed",
            "change", "number_diabetic_drugs", "num_medications",
            "num_lab_procedures", "number_inpatient", "readmitted"
        ]
        existing_cols = [c for c in display_cols if c in filtered_df.columns]
        st.dataframe(filtered_df[existing_cols].head(500), use_container_width=True, height=360)

        csv_bytes = filtered_df[existing_cols].head(5000).to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv_bytes,
            file_name="filtered_diabetic_data_sample.csv",
            mime="text/csv"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Summary Statistics Table
    st.markdown("""
    <div class="card-container">
        <div class="card-title">Cohort Numerical Summary Statistics</div>
        <div class="card-subtitle">Distribution percentiles for hospital stay, lab testing, medications, and prior encounters</div>
    """, unsafe_allow_html=True)

    num_cols = ["time_in_hospital", "num_lab_procedures", "num_procedures", "num_medications", "number_diagnoses", "number_inpatient"]
    stats_df = filtered_df[num_cols].describe().round(2).T
    stats_df.rename(columns={
        "count": "Count", "mean": "Mean", "std": "Std Dev",
        "min": "Min", "25%": "Q1 (25%)", "50%": "Median (50%)",
        "75%": "Q3 (75%)", "max": "Max"
    }, inplace=True)
    st.dataframe(stats_df, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
