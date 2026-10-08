"""
Shared Theme and Design System for Diabetes Clinical Analytics.
Defines unified color palette, custom CSS injection, and Plotly styling templates.
"""
import streamlit as st
import plotly.graph_objects as go

# --- COLOR PALETTE (Medical Blue & White) ---
PRIMARY_BLUE = "#1F6FB2"
NAVY_HEADING = "#0F2D59"
BG_LIGHT = "#F8FAFC"
CARD_BG = "#FFFFFF"
BORDER_COLOR = "#E2E8F0"
ACCENT_BLUE = "#2B6CB0"
LIGHT_BLUE_BG = "#F0F7FD"
TEXT_MUTED = "#5A6A80"
TEXT_DARK = "#1A202C"

# Status Accents
COLOR_SUCCESS = "#0D9488"
COLOR_WARNING = "#D97706"
COLOR_DANGER = "#DC2626"
COLOR_INFO = "#2563EB"

# Plotly Discrete Palettes
CLINICAL_PALETTE = [
    "#1F6FB2", "#3B82F6", "#60A5FA", "#93C5FD", 
    "#0F2D59", "#0284C7", "#0D9488", "#F59E0B"
]

READMISSION_PALETTE = {
    "NO": "#1F6FB2",
    ">30": "#F59E0B",
    "<30": "#DC2626"
}

READMISSION_COLORS_ORDERED = ["#1F6FB2", "#F59E0B", "#DC2626"]

# --- UNIFIED CSS STYLES ---
CUSTOM_CSS = """
<style>
/* Import Modern Google Fonts: Inter and Poppins */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@500;600;700&display=swap');

/* Global Reset and Typography */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    color: #1A202C;
    background-color: #F8FAFC;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #0F2D59 !important;
    letter-spacing: -0.02em;
}

/* Hide Default Streamlit Branding */
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
header {visibility: hidden !important;}
[data-testid="stSidebarNav"] {display: none !important;}

/* Adjust Page Spacing */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 1400px;
}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0;
    padding-top: 1rem;
}

section[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem !important;
}

/* App Header in Main Area */
.page-header-box {
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #E2E8F0;
}

.page-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: #0F2D59 !important;
    margin-bottom: 0.25rem;
    line-height: 1.25;
}

.page-subtitle {
    font-size: 0.95rem;
    color: #5A6A80;
    margin-top: 0;
    line-height: 1.4;
}

/* KPI Cards Row */
.kpi-grid {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.75rem;
    flex-wrap: wrap;
}

.kpi-card {
    background: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #E2E8F0;
    border-left: 4px solid #1F6FB2;
    box-shadow: 0 3px 10px rgba(15, 45, 89, 0.04);
    padding: 16px 20px;
    height: 100%;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(15, 45, 89, 0.08);
}

.kpi-top-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}

.kpi-label {
    font-size: 0.8125rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #5A6A80;
}

.kpi-icon-badge {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background-color: #F0F7FD;
    color: #1F6FB2;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
}

.kpi-value {
    font-family: 'Poppins', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: #0F2D59;
    line-height: 1.2;
    margin-bottom: 4px;
}

.kpi-caption {
    font-size: 0.8125rem;
    color: #5A6A80;
    line-height: 1.3;
}

/* Card Container */
.card-container {
    background: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 2px 8px rgba(15, 45, 89, 0.04);
    padding: 22px 24px;
    margin-bottom: 1.5rem;
}

.card-title {
    font-family: 'Poppins', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: #0F2D59;
    margin-bottom: 0.25rem;
}

.card-subtitle {
    font-size: 0.84rem;
    color: #5A6A80;
    margin-bottom: 1rem;
}

/* Takeaway Badge Under Charts */
.takeaway-badge {
    background: #F0F7FD;
    border-left: 3px solid #1F6FB2;
    padding: 10px 14px;
    border-radius: 0 8px 8px 0;
    font-size: 0.86rem;
    color: #0F2D59;
    line-height: 1.45;
    margin-top: 10px;
}

.takeaway-bold {
    font-weight: 700;
    color: #1F6FB2;
    margin-right: 4px;
}

/* Key Review Panel (Side of Chart) */
.key-review-card {
    background: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #E2E8F0;
    border-left: 4px solid #1F6FB2;
    box-shadow: 0 2px 8px rgba(15, 45, 89, 0.04);
    padding: 22px 24px;
    height: 100%;
    box-sizing: border-box;
}

.review-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
}

.review-badge {
    background: #EBF3FA;
    color: #1F6FB2;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 3px 8px;
    border-radius: 4px;
}

.review-title {
    font-family: 'Poppins', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #0F2D59;
    margin: 0;
}

.review-stat-box {
    background: #F0F7FD;
    border-radius: 8px;
    padding: 12px 14px;
    margin: 8px 0 14px 0;
    border: 1px solid #D0E1F9;
}

.review-stat-value {
    font-family: 'Poppins', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: #1F6FB2;
    line-height: 1.1;
}

.review-stat-label {
    font-size: 0.8rem;
    color: #5A6A80;
    margin-top: 2px;
}

.review-item {
    font-size: 0.88rem;
    color: #2D3748;
    line-height: 1.5;
    margin-bottom: 10px;
    padding-left: 16px;
    position: relative;
}

.review-item::before {
    content: "•";
    position: absolute;
    left: 0;
    color: #1F6FB2;
    font-weight: bold;
    font-size: 1.1rem;
    line-height: 1;
}

.review-takeaway-footer {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px dashed #E2E8F0;
    font-size: 0.82rem;
    color: #5A6A80;
    font-style: italic;
}


/* Sidebar App Header */
.sidebar-brand-box {
    padding: 10px 8px 18px 8px;
    border-bottom: 1px solid #E2E8F0;
    margin-bottom: 14px;
}

.sidebar-brand-title {
    font-family: 'Poppins', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #0F2D59;
    margin: 0;
    line-height: 1.25;
}

.sidebar-brand-sub {
    font-size: 0.775rem;
    color: #5A6A80;
    margin-top: 4px;
    margin-bottom: 0;
}

.sidebar-badge {
    display: inline-block;
    background: #EBF3FA;
    color: #1F6FB2;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
    margin-top: 8px;
}

/* Table and DataFrame Styling */
[data-testid="stDataFrame"] {
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    overflow: hidden;
}
</style>
"""

def inject_custom_css():
    """Injects the global CSS design tokens into the Streamlit app."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def apply_plotly_theme(fig, height=380, show_legend=True):
    """
    Applies the medical blue and clean white theme to any Plotly figure.
    Ensures high legibility, clean gridlines, and container responsiveness.
    """
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=40, r=25, t=50, b=40),
        font=dict(
            family="Inter, -apple-system, sans-serif",
            color=TEXT_DARK,
            size=12
        ),
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=TEXT_MUTED)
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_size=12,
            font_family="Inter, sans-serif",
            bordercolor=BORDER_COLOR
        )
    )
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="#F1F5F9",
        linecolor="#CBD5E1",
        tickfont=dict(size=11, color=TEXT_MUTED),
        title_font=dict(size=12, color=NAVY_HEADING)
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="#F1F5F9",
        linecolor="#CBD5E1",
        tickfont=dict(size=11, color=TEXT_MUTED),
        title_font=dict(size=12, color=NAVY_HEADING)
    )
    return fig
