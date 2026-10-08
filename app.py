"""
Main Application Controller for Diabetes 130-US Hospitals Clinical Analytics.
Implements unified medical design system, sidebar navigation, and page routing.
"""
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# Set page configuration with medical title (NO emojis)
st.set_page_config(
    page_title="Diabetes Inpatient Clinical Analytics",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import shared design system, data loader, and views
from components.theme import inject_custom_css, PRIMARY_BLUE, NAVY_HEADING, BORDER_COLOR
from components.data_loader import load_data
from views.overview import render_overview_view
from views.demographics import render_demographics_view
from views.clinical_lab import render_clinical_lab_view
from views.medications import render_medications_view
from views.readmission_risk import render_readmission_risk_view
from views.data_explorer import render_data_explorer_view

# 1. Inject Unified CSS Design System
inject_custom_css()

# 2. Cached Data Loading
df = load_data("cleaned_diabetic_data.csv")

# 3. Sidebar Navigation & Branding
with st.sidebar:
    # Sidebar Header: Title and Subtitle
    st.markdown("""<div class="sidebar-brand-box"><div class="sidebar-brand-title">Clinical Diabetes Analytics</div><div class="sidebar-brand-sub">130-US Hospitals Study (1999–2008)</div><div class="sidebar-badge">UCI Health Facts Database</div></div>""", unsafe_allow_html=True)

    # Sidebar Navigation Menu with Professional Bootstrap Icons
    selected_page = option_menu(
        menu_title="Navigation",
        options=[
            "Executive Overview",
            "Demographics & Admission",
            "Glycemic & Lab Testing",
            "Medication Regimens",
            "Readmission Risk Drivers",
            "Dataset Explorer"
        ],
        icons=[
            "speedometer2",
            "people",
            "clipboard2-pulse",
            "capsule",
            "shield-exclamation",
            "table"
        ],
        menu_icon="compass",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#1F6FB2", "font-size": "15px"},
            "nav-link": {
                "font-size": "13px",
                "text-align": "left",
                "margin": "4px 0",
                "padding": "10px 14px",
                "border-radius": "8px",
                "color": "#0F2D59",
                "font-family": "Inter, sans-serif",
                "font-weight": "500",
                "--hover-color": "#F0F7FD",
            },
            "nav-link-selected": {
                "background-color": "#1F6FB2",
                "color": "#FFFFFF !important",
                "font-weight": "600",
            },
        }
    )

    # Sidebar Footer Information
    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.775rem; color: #5A6A80; line-height: 1.5; padding: 0 4px;">
        <div style="font-weight: 600; color: #0F2D59; margin-bottom: 4px;">Dataset Summary</div>
        <div>• Total Encounters: <strong>101,745</strong></div>
        <div>• Cleaned Features: <strong>21 variables</strong></div>
        <div>• Baseline Study: <em>Strack et al. (2014)</em></div>
    </div>
    """, unsafe_allow_html=True)

# 4. Route to Selected Page View
if selected_page == "Executive Overview":
    render_overview_view(df)
elif selected_page == "Demographics & Admission":
    render_demographics_view(df)
elif selected_page == "Glycemic & Lab Testing":
    render_clinical_lab_view(df)
elif selected_page == "Medication Regimens":
    render_medications_view(df)
elif selected_page == "Readmission Risk Drivers":
    render_readmission_risk_view(df)
elif selected_page == "Dataset Explorer":
    render_data_explorer_view(df)
