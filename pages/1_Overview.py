import streamlit as st
from components.theme import inject_custom_css
from components.data_loader import load_data
from views.overview import render_overview_view

st.set_page_config(
    page_title="Executive Overview - Diabetes Analytics",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()
df = load_data("cleaned_diabetic_data.csv")

with st.sidebar:
    st.markdown("""<div class="sidebar-brand-box"><div class="sidebar-brand-title">Clinical Diabetes Analytics</div><div class="sidebar-brand-sub">130-US Hospitals Study (1999–2008)</div><div class="sidebar-badge">UCI Health Facts Database</div></div>""", unsafe_allow_html=True)
    st.info("Tip: Run `app.py` for full integrated sidebar navigation across all pages.")

render_overview_view(df)
