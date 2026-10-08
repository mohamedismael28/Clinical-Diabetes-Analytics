"""
UI Component Helpers for Diabetes Analytics App.
Provides uniform KPI cards, page headers, takeaway badges, and side-by-side key reviews.
All HTML is strictly formatted flush (zero leading indentation) to prevent Markdown
from treating HTML as indented code blocks (<pre><code>).
"""
import streamlit as st
import textwrap

# Clean medical SVG icons (crisp vector graphics, no external CDN dependencies)
SVG_ICONS = {
    "hospital": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1F6FB2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18M5 21V7l8-4 8 4v14M9 10h6M12 7v6"/></svg>',
    "activity": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1F6FB2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "clock": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1F6FB2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "pill": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1F6FB2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m10.5 20.5 10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7Z"/><path d="m8.5 8.5 7 7"/></svg>',
    "users": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1F6FB2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "alert": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "lab": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1F6FB2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2v7.31L4.1 18.2A2 2 0 0 0 5.8 21h12.4a2 2 0 0 0 1.7-2.8L14 9.31V2"/><line x1="8" y1="2" x2="16" y2="2"/><line x1="8.5" y1="14" x2="15.5" y2="14"/></svg>',
    "shield": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1F6FB2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "chart": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1F6FB2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "check": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0D9488" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
}

def safe_html(html_str: str):
    """Safely renders HTML stripped of leading indentation."""
    st.markdown(textwrap.dedent(html_str).strip(), unsafe_allow_html=True)

def render_page_header(title: str, description: str, badge_text: str = "CLINICAL STUDY ANALYSIS"):
    """Renders standard top page title and descriptive subtitle."""
    html = f"""<div class="page-header-box"><span style="display:inline-block; font-size:0.75rem; font-weight:700; color:#1F6FB2; background:#EBF3FA; padding:3px 10px; border-radius:4px; letter-spacing:0.06em; margin-bottom:8px;">{badge_text}</span><div class="page-title">{title}</div><div class="page-subtitle">{description}</div></div>"""
    st.markdown(html, unsafe_allow_html=True)

def render_kpis(kpi_data_list: list):
    """
    Renders a row of uniform KPI cards.
    Each item in kpi_data_list is a dict:
    {'label': str, 'value': str, 'caption': str, 'icon': str (key in SVG_ICONS)}
    """
    cols = st.columns(len(kpi_data_list))
    for col, data in zip(cols, kpi_data_list):
        icon_svg = SVG_ICONS.get(data.get("icon", "activity"), SVG_ICONS["activity"])
        html = f"""<div class="kpi-card"><div class="kpi-top-row"><span class="kpi-label">{data.get('label', '')}</span><div class="kpi-icon-badge">{icon_svg}</div></div><div class="kpi-value">{data.get('value', '')}</div><div class="kpi-caption">{data.get('caption', '')}</div></div>"""
        with col:
            st.markdown(html, unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 1.25rem;'></div>", unsafe_allow_html=True)

def render_card_title(title: str, subtitle: str = ""):
    """Renders a card title and subtitle without code block issues."""
    sub_part = f'<div class="card-subtitle">{subtitle}</div>' if subtitle else ""
    html = f"""<div style="margin-bottom: 10px;"><div class="card-title">{title}</div>{sub_part}</div>"""
    st.markdown(html, unsafe_allow_html=True)

def render_takeaway(bold_prefix: str, text: str):
    """Renders a single-line clinical takeaway banner below charts."""
    html = f"""<div class="takeaway-badge"><span class="takeaway-bold">{bold_prefix}:</span> {text}</div>"""
    st.markdown(html, unsafe_allow_html=True)

def render_key_review_card(
    title: str = "Key Review",
    badge_text: str = "EXECUTIVE SUMMARY",
    highlight_stat: str = None,
    stat_label: str = None,
    takeaways: list = None,
    bottom_note: str = None
):
    """
    Renders an executive Key Review card designed to sit alongside a chart.
    Written in plain, non-technical language for non-technical stakeholders.
    Guaranteed zero indentation so markdown never renders it as a code block.
    """
    stat_html = ""
    if highlight_stat:
        lbl_html = f'<div class="review-stat-label">{stat_label}</div>' if stat_label else ""
        stat_html = f'<div class="review-stat-box"><div class="review-stat-value">{highlight_stat}</div>{lbl_html}</div>'

    bullets_html = ""
    if takeaways:
        for t in takeaways:
            if isinstance(t, tuple):
                b_head, b_body = t
                bullets_html += f'<div class="review-item"><strong>{b_head}:</strong> {b_body}</div>'
            else:
                bullets_html += f'<div class="review-item">{t}</div>'

    footer_html = f'<div class="review-takeaway-footer">{bottom_note}</div>' if bottom_note else ""

    html = f"""<div class="key-review-card"><div class="review-header">{SVG_ICONS['shield']}<span class="review-title">{title}</span><span class="review-badge" style="margin-left: auto;">{badge_text}</span></div>{stat_html}<div style="margin-top: 4px;">{bullets_html}</div>{footer_html}</div>"""
    st.markdown(html, unsafe_allow_html=True)
