"""
Cached Data Loader and Utilities for Diabetes 130-US Hospitals Dataset.
Handles cached reading, data validation, and clinical feature mappings.
"""
import streamlit as st
import pandas as pd
import numpy as np

# Admission type mapping according to UCI Health Facts documentation
ADMISSION_TYPE_MAP = {
    1: "Emergency",
    2: "Urgent",
    3: "Elective",
    4: "Newborn",
    5: "Other",
    6: "Other",
    7: "Trauma Center",
    8: "Other"
}

READMISSION_LABEL_MAP = {
    "NO": "No Readmission",
    ">30": "Readmitted > 30 Days",
    "<30": "Early Readmitted (< 30 Days)"
}

AGE_ORDER = [
    "[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)",
    "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)"
]

@st.cache_data(show_spinner="Loading hospital dataset...")
def load_data(filepath: str = "cleaned_diabetic_data.csv") -> pd.DataFrame:
    """
    Loads and caches the cleaned diabetic hospital encounters dataset.
    Adds human-readable descriptive columns for admission types and readmissions.
    """
    df = pd.read_csv(filepath)
    
    # Add descriptive labels
    df["admission_type_desc"] = df["admission_type_id"].map(ADMISSION_TYPE_MAP).fillna("Other")
    df["readmitted_label"] = df["readmitted"].map(READMISSION_LABEL_MAP).fillna(df["readmitted"])
    
    # Categorize inpatient visit history
    df["inpatient_bracket"] = df["number_inpatient"].apply(
        lambda x: "0 Visits" if x == 0 else ("1 Visit" if x == 1 else "2+ Visits")
    )
    
    # Categorize emergency visit history
    df["emergency_bracket"] = df["number_emergency"].apply(
        lambda x: "0 Visits" if x == 0 else ("1 Visit" if x == 1 else "2+ Visits")
    )
    
    # Binary early readmission flag
    df["is_early_readmitted"] = (df["readmitted"] == "<30").astype(int)
    
    return df

def get_gender_cleaned_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns data excluding the 3 encounters where gender is 'Unknown/Invalid',
    as specified by the dataset cleaning rules.
    """
    return df[df["gender"].isin(["Male", "Female"])].copy()

def compute_overall_kpis(df: pd.DataFrame) -> dict:
    """Computes headline KPIs across the current dataframe slice."""
    total_encounters = len(df)
    early_readmit_count = (df["readmitted"] == "<30").sum()
    early_readmit_pct = (early_readmit_count / total_encounters * 100) if total_encounters > 0 else 0
    avg_los = df["time_in_hospital"].mean() if total_encounters > 0 else 0
    med_change_pct = ((df["change"] == "Ch").sum() / total_encounters * 100) if total_encounters > 0 else 0
    
    return {
        "total_encounters": f"{total_encounters:,}",
        "early_readmit_count": f"{early_readmit_count:,}",
        "early_readmit_pct": f"{early_readmit_pct:.1f}%",
        "avg_los": f"{avg_los:.2f} Days",
        "med_change_pct": f"{med_change_pct:.1f}%"
    }
