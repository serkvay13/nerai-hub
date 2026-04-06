"""
NERAI Intelligence Hub — Premium CSS Foundation
================================================
Bu dosyayı gdelt_dashboard.py'nin EN BAŞINA (st.set_page_config'den hemen sonra) ekleyin.

Kullanım:
    import nerai_premium_css
    nerai_premium_css.inject_all()

Veya doğrudan:
    from nerai_premium_css import inject_all
    inject_all()
"""

import streamlit as st
import streamlit.components.v1 as _stc

# ─────────────────────────────────────────────────
# NERAI BRAND TOKENS  (logo: cyan + black)
# ─────────────────────────────────────────────────
TOKENS = {
    # Backgrounds
    "bg_primary":     "#0a0e17",
    "bg_secondary":   "#0d1220",
    "bg_card":        "#111827",
    "bg_card_hover":  "#162032",
    "bg_surface":     "#1a2338",
    "bg_elevated":    "#1e293b",

    # Brand accent (from NERAI logo)
    "cyan":           "#00d4ff",
    "cyan_dim":       "#0099cc",
    "cyan_glow":      "rgba(0,212,255,0.12)",
    "cyan_border":    "rgba(0,212,255,0.18)",
    "cyan_hover":     "rgba(0,212,255,0.25)",

    # Risk signaling
    "red":            "#ff4757",
    "red_dim":        "rgba(255,71,87,0.12)",
    "amber":          "#ffb347",
    "amber_dim":      "rgba(255,179,71,0.12)",
    "green":          "#00e676",
    "green_dim":      "rgba(0,230,118,0.12)",

    # Typography
    "text_primary":   "#e8edf4",
    "text_secondary": "#8a9bb5",
    "text_muted":     "#4a5d75",
    "text_inverse":   "#0a0e17",

    # Borders & Lines
    "border":         "rgba(0,212,255,0.08)",
    "border_strong":  "rgba(0,212,255,0.18)",
    "divider":        "rgba(255,255,255,0.04)",

    # Shadows
    "shadow_sm":      "0 1px 3px rgba(0,0,0,0.3)",
    "shadow_md":      "0 4px 16px rgba(0,0,0,0.4)",
    "shadow_lg":      "0 8px 32px rgba(0,0,0,0.5)",
    "shadow_glow":    "0 0 30px rgba(0,212,255,0.08)",

    # Spacing
    "radius_sm":      "8px",
    "radius_md":      "12px",
    "radius_lg":      "16px",
    "radius_xl":      "20px",
}


def inject_global_css():
    """Ana global CSS — tüm sayfaları etkiler."""
    st.markdown(f"""
    <style>
    /* ══════════════════════════════════════════
       NERAI PREMIUM CSS FOUNDATION v1.0
       Bloomberg × Apple Hybrid Dark Theme
       ══════════════════════════════════════════ */

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── ROOT RESET ── */
    .stApp {{
        background: {TOKENS['bg_primary']} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }}

    /* ── Protect Streamlit icon fonts ── */
    .stApp .material-symbols-rounded,
    .stApp .material-symbols-outlined,
    .stApp [data-testid="collapsedControl"] span,
    .stApp [data-testid="stSidebarCollapsedControl"] span,
    .stApp [data-testid="stSidebarCollapseButton"] span,
    .stApp [data-testid="stSidebarCollapseButton"] span span,
    .stApp [data-testid="stBaseButton-headerNoPadding"] span,
    .stApp [data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"] span,
    .stApp [data-testid="stSidebar"] button span.material-symbols-rounded {{
        font-family: 'Material Symbols Rounded', sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }}

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: {TOKENS['bg_primary']};
    }}
    ::-webkit-scrollbar-thumb {{
        background: {TOKENS['bg_elevated']};
        border-radius: 3px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {TOKENS['cyan_dim']};
    }}

    /* ── SELECTION ── */
    ::selection {{
        background: rgba(0,212,255,0.25);
        color: #fff;
    }}

    /* ══════════════════════════════════════
       SIDEBAR — Premium Navigation
       ══════════════════════════════════════ */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {TOKENS['bg_secondary']} 0%, {TOKENS['bg_primary']} 100%) !important;
        border-right: 1px solid {TOKENS['border']} !important;
    }}

    /* ── Sidebar Collapse/Expand Button Fix ── */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    .css-1rs6os.edgvbvh3,
    [data-testid="stSidebar"] button[aria-label="Close"],
    [data-testid="stSidebar"] [data-testid="stSidebarNavCollapseIcon"],
    section[data-testid="stSidebar"] > div > button:first-child {{
        color: {TOKENS['cyan']} !important;
        background: {TOKENS['bg_card']} !important;
        border: 1px solid {TOKENS['cyan_border']} !important;
        border-radius: 8px !important;
        opacity: 1 !important;
        visibility: visible !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        z-index: 999999 !important;
        position: fixed !important;
    }}
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {{
        top: 0.5rem !important;
        left: 0.5rem !important;
        width: 2rem !important;
        height: 2rem !important;
    }}
    [data-testid="collapsedControl"]:hover,
    [data-testid="stSidebarCollapsedControl"]:hover {{
        background: {TOKENS['cyan_glow']} !important;
        border-color: {TOKENS['cyan']} !important;
    }}
    /* Ensure icon font renders in collapse button */
    [data-testid="collapsedControl"] span,
    [data-testid="stSidebarCollapsedControl"] span {{
        font-family: 'Material Symbols Rounded' !important;
        font-size: 20px !important;
    }}

    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1rem !important;
    }}

    /* Sidebar nav buttons */
    [data-testid="stSidebar"] .stButton > button {{
        background: transparent !important;
        color: {TOKENS['text_secondary']} !important;
        border: 1px solid transparent !important;
        border-radius: {TOKENS['radius_md']} !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.5px !important;
        text-align: left !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }}

    [data-testid="stSidebar"] .stButton > button:hover {{
        background: {TOKENS['cyan_glow']} !important;
        color: {TOKENS['text_primary']} !important;
        border-color: {TOKENS['border_strong']} !important;
    }}

    /* Active page button override — add class .nav-active via st.markdown */
    [data-testid="stSidebar"] .stButton > button[kind="primary"],
    [data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"] {{
        background: linear-gradient(135deg, rgba(0,60,90,0.5) 0%, rgba(0,40,60,0.3) 100%) !important;
        color: {TOKENS['cyan']} !important;
        border: 1px solid {TOKENS['cyan_border']} !important;
        font-weight: 600 !important;
        box-shadow: {TOKENS['shadow_glow']} !important;
    }}

    /* Sidebar slider fix */
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stSlider [data-testid="stTickBarMin"],
    [data-testid="stSidebar"] .stSlider [data-testid="stTickBarMax"],
    [data-testid="stSidebar"] .stNumberInput label {{
        color: {TOKENS['text_muted']} !important;
    }}

    [data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"] {{
        color: {TOKENS['cyan']} !important;
    }}

    [data-testid="stSidebar"] .stNumberInput input {{
        background: {TOKENS['bg_card']} !important;
        color: {TOKENS['text_primary']} !important;
        border: 1px solid {TOKENS['cyan_border']} !important;
    }}

    [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] [role="slider"] {{
        background: {TOKENS['bg_elevated']} !important;
        border: 2px solid {TOKENS['cyan']} !important;
    }}

    /* ══════════════════════════════════════
       MAIN CONTENT — Typography & Layout
       ══════════════════════════════════════ */

    /* Headings */
    .stApp h1, .stApp h2, .stApp h3 {{
        font-family: 'Inter', sans-serif !important;
        color: {TOKENS['text_primary']} !important;
        letter-spacing: -0.5px !important;
    }}

    .stApp h1 {{ font-weight: 800 !important; }}
    .stApp h2 {{ font-weight: 700 !important; }}
    .stApp h3 {{ font-weight: 600 !important; }}

    /* Paragraphs & default text — exclude icon spans */
    .stApp p,
    .stApp label {{
        font-family: 'Inter', sans-serif !important;
    }}
    .stApp span {{
        font-family: 'Inter', sans-serif;
    }}
    /* Re-force icon font on Streamlit icon elements */
    .stApp [data-testid="stSidebarCollapseButton"] span,
    .stApp [data-testid="stBaseButton-headerNoPadding"] span,
    .stApp [data-testid="collapsedControl"] span,
    .stApp [data-testid="stSidebarCollapsedControl"] span {{
        font-family: 'Material Symbols Rounded' !important;
    }}

    /* Links */
    .stApp a {{
        color: {TOKENS['cyan']} !important;
        text-decoration: none !important;
    }}
    .stApp a:hover {{
        text-decoration: underline !important;
    }}

    /* ══════════════════════════════════════
       METRICS & KPIs
       ══════════════════════════════════════ */
    [data-testid="stMetric"] {{
        background: {TOKENS['bg_card']} !important;
        border: 1px solid {TOKENS['border']} !important;
        border-radius: {TOKENS['radius_lg']} !important;
        padding: 1.25rem !important;
        transition: all 0.2s ease !important;
    }}

    [data-testid="stMetric"]:hover {{
        border-color: {TOKENS['cyan_border']} !important;
        box-shadow: {TOKENS['shadow_glow']} !important;
    }}

    [data-testid="stMetric"] label {{
        color: {TOKENS['text_muted']} !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
    }}

    [data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: {TOKENS['text_primary']} !important;
        font-weight: 800 !important;
        font-size: 1.8rem !important;
        letter-spacing: -1px !important;
    }}

    [data-testid="stMetric"] [data-testid="stMetricDelta"] {{
        font-weight: 600 !important;
    }}

    /* ══════════════════════════════════════
       FORMS & INPUTS
       ══════════════════════════════════════ */
    [data-testid="stForm"] {{
        background: linear-gradient(135deg, {TOKENS['bg_secondary']} 0%, {TOKENS['bg_card']} 100%) !important;
        border: 1px solid {TOKENS['cyan_border']} !important;
        border-radius: {TOKENS['radius_lg']} !important;
        padding: 2.5rem !important;
        box-shadow: 0 0 60px {TOKENS['cyan_glow']} !important;
        max-width: 420px !important;
        margin: 60px auto !important;
    }}

    [data-testid="stForm"] input {{
        background: {TOKENS['bg_primary']} !important;
        border: 1px solid {TOKENS['cyan_border']} !important;
        color: {TOKENS['text_primary']} !important;
        border-radius: {TOKENS['radius_sm']} !important;
        font-family: 'Inter', sans-serif !important;
    }}

    [data-testid="stForm"] input:focus {{
        border-color: {TOKENS['cyan']} !important;
        box-shadow: 0 0 12px {TOKENS['cyan_glow']} !important;
    }}

    [data-testid="stForm"] button {{
        background: linear-gradient(135deg, {TOKENS['cyan']} 0%, {TOKENS['cyan_dim']} 100%) !important;
        color: {TOKENS['text_inverse']} !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: {TOKENS['radius_sm']} !important;
    }}

    [data-testid="stForm"] button:hover {{
        box-shadow: 0 0 20px rgba(0,212,255,0.4) !important;
    }}

    /* ══════════════════════════════════════
       SELECT BOXES & DROPDOWNS
       ══════════════════════════════════════ */
    [data-baseweb="select"] {{
        font-family: 'Inter', sans-serif !important;
    }}

    [data-baseweb="select"] > div {{
        background: {TOKENS['bg_card']} !important;
        border: 1px solid {TOKENS['border_strong']} !important;
        border-radius: {TOKENS['radius_sm']} !important;
        color: {TOKENS['text_primary']} !important;
    }}

    [data-baseweb="select"] > div:hover {{
        border-color: {TOKENS['cyan_border']} !important;
    }}

    /* Dropdown menu */
    [data-baseweb="popover"] {{
        background: {TOKENS['bg_card']} !important;
        border: 1px solid {TOKENS['border_strong']} !important;
        border-radius: {TOKENS['radius_md']} !important;
    }}

    [data-baseweb="popover"] li {{
        color: {TOKENS['text_secondary']} !important;
    }}

    [data-baseweb="popover"] li:hover {{
        background: {TOKENS['cyan_glow']} !important;
        color: {TOKENS['text_primary']} !important;
    }}

    /* ══════════════════════════════════════
       TABS
       ══════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0 !important;
        background: {TOKENS['bg_card']} !important;
        border-radius: {TOKENS['radius_md']} !important;
        padding: 4px !important;
        border: 1px solid {TOKENS['border']} !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: {TOKENS['radius_sm']} !important;
        color: {TOKENS['text_muted']} !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        padding: 0.5rem 1rem !important;
        letter-spacing: 0.3px !important;
    }}

    .stTabs [aria-selected="true"] {{
        background: {TOKENS['cyan_glow']} !important;
        color: {TOKENS['cyan']} !important;
        font-weight: 600 !important;
        border-bottom: none !important;
    }}

    .stTabs [data-baseweb="tab-highlight"] {{
        display: none !important;
    }}

    .stTabs [data-baseweb="tab-border"] {{
        display: none !important;
    }}

    /* ══════════════════════════════════════
       EXPANDERS
       ══════════════════════════════════════ */
    [data-testid="stExpander"] {{
        background: {TOKENS['bg_card']} !important;
        border: 1px solid {TOKENS['border']} !important;
        border-radius: {TOKENS['radius_md']} !important;
    }}

    [data-testid="stExpander"] summary {{
        color: {TOKENS['text_primary']} !important;
        font-weight: 600 !important;
    }}

    /* ══════════════════════════════════════
       DATAFRAMES & TABLES
       ══════════════════════════════════════ */
    [data-testid="stDataFrame"] {{
        border-radius: {TOKENS['radius_md']} !important;
        overflow: hidden !important;
    }}

    /* ══════════════════════════════════════
       CUSTOM COMPONENT CLASSES
       Use with st.markdown(unsafe_allow_html=True)
       ══════════════════════════════════════ */

    /* Section Headers */
    .nerai-section-header {{
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: {TOKENS['cyan']};
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid {TOKENS['divider']};
    }}

    /* KPI Card */
    .nerai-kpi {{
        background: {TOKENS['bg_card']};
        border: 1px solid {TOKENS['border']};
        border-radius: {TOKENS['radius_lg']};
        padding: 1.5rem;
        text-align: center;
        transition: all 0.25s ease;
        position: relative;
        overflow: hidden;
    }}
    .nerai-kpi:hover {{
        border-color: {TOKENS['cyan_border']};
        box-shadow: {TOKENS['shadow_glow']};
        transform: translateY(-2px);
    }}
    .nerai-kpi .kpi-value {{
        font-size: 2.4rem;
        font-weight: 900;
        color: {TOKENS['cyan']};
        letter-spacing: -2px;
        line-height: 1.1;
        font-family: 'Inter', sans-serif;
    }}
    .nerai-kpi .kpi-label {{
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: {TOKENS['text_muted']};
        margin-top: 0.5rem;
    }}

    /* Status Badge */
    .nerai-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 14px;
        border-radius: 100px;
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }}
    .nerai-badge.online {{
        background: {TOKENS['green_dim']};
        color: {TOKENS['green']};
        border: 1px solid rgba(0,230,118,0.2);
    }}
    .nerai-badge.warning {{
        background: {TOKENS['amber_dim']};
        color: {TOKENS['amber']};
        border: 1px solid rgba(255,179,71,0.2);
    }}
    .nerai-badge.critical {{
        background: {TOKENS['red_dim']};
        color: {TOKENS['red']};
        border: 1px solid rgba(255,71,87,0.2);
    }}

    /* Module Card (Home page) */
    .nerai-module-card {{
        background: {TOKENS['bg_card']};
        border: 1px solid {TOKENS['border']};
        border-radius: {TOKENS['radius_lg']};
        padding: 1.75rem;
        transition: all 0.3s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }}
    .nerai-module-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, {TOKENS['cyan']}, transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
    }}
    .nerai-module-card:hover {{
        border-color: {TOKENS['cyan_border']};
        box-shadow: {TOKENS['shadow_glow']};
        transform: translateY(-3px);
    }}
    .nerai-module-card:hover::before {{
        opacity: 1;
    }}
    .nerai-module-card h4 {{
        color: {TOKENS['text_primary']};
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}
    .nerai-module-card p {{
        color: {TOKENS['text_secondary']};
        font-size: 0.82rem;
        line-height: 1.5;
        margin: 0;
    }}

    /* Divider */
    .nerai-divider {{
        height: 1px;
        background: linear-gradient(90deg, transparent, {TOKENS['border_strong']}, transparent);
        margin: 2rem 0;
    }}

    /* Data Freshness Bar */
    .nerai-freshness {{
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        padding: 0.6rem 1.5rem;
        background: {TOKENS['bg_card']};
        border: 1px solid {TOKENS['border']};
        border-radius: 100px;
        font-size: 0.68rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: {TOKENS['text_muted']};
        margin: 1rem auto;
        width: fit-content;
    }}
    .nerai-freshness .dot {{
        width: 6px; height: 6px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
    }}
    .nerai-freshness .dot.live {{ background: {TOKENS['green']}; box-shadow: 0 0 8px {TOKENS['green']}; }}
    .nerai-freshness .dot.ok {{ background: {TOKENS['cyan']}; }}
    .nerai-freshness .dot.stale {{ background: {TOKENS['amber']}; }}

    /* Risk Level Colors */
    .risk-critical {{ color: {TOKENS['red']} !important; }}
    .risk-high {{ color: {TOKENS['amber']} !important; }}
    .risk-medium {{ color: {TOKENS['cyan']} !important; }}
    .risk-low {{ color: {TOKENS['green']} !important; }}

    /* ══════════════════════════════════════
       ANIMATIONS
       ══════════════════════════════════════ */
    @keyframes nerai-pulse {{
        0%, 100% {{ opacity: 0.4; }}
        50% {{ opacity: 1; }}
    }}

    @keyframes nerai-glow {{
        0%, 100% {{ box-shadow: 0 0 5px {TOKENS['cyan_glow']}; }}
        50% {{ box-shadow: 0 0 20px {TOKENS['cyan_glow']}; }}
    }}

    .nerai-pulse {{ animation: nerai-pulse 2s ease-in-out infinite; }}
    .nerai-glow {{ animation: nerai-glow 3s ease-in-out infinite; }}

    /* ══════════════════════════════════════
       HIDE STREAMLIT DEFAULTS
       ══════════════════════════════════════ */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{
        background: {TOKENS['bg_primary']} !important;
        border-bottom: 1px solid {TOKENS['border']} !important;
    }}

    /* Hide hamburger — but NOT sidebar collapse/expand buttons */
    .stApp > header button[kind="header"] {{ display: none !important; }}

    /* ══════════════════════════════════════════════════════
       PREMIUM HOME PAGE — WORLD CLASS UPGRADE
       ══════════════════════════════════════════════════════ */

    /* ── MODULE TILE CARDS — Glassmorphism ── */
    .stApp [data-testid="column"] > div > div {{
        background: linear-gradient(135deg,
            rgba(15, 23, 42, 0.85) 0%,
            rgba(10, 14, 23, 0.95) 100%) !important;
        border: 1px solid rgba(0, 212, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 28px 24px !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
    }}

    .stApp [data-testid="column"] > div > div::before {{
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 1px !important;
        background: linear-gradient(90deg,
            transparent 0%,
            rgba(0, 212, 255, 0.3) 50%,
            transparent 100%) !important;
    }}

    .stApp [data-testid="column"] > div > div:hover {{
        border-color: rgba(0, 212, 255, 0.25) !important;
        box-shadow:
            0 0 30px rgba(0, 212, 255, 0.06),
            0 8px 32px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(0, 212, 255, 0.1) !important;
        transform: translateY(-4px) !important;
    }}

    /* ── PREMIUM BUTTONS ── */
    .stApp .stButton > button {{
        background: linear-gradient(135deg,
            rgba(0, 212, 255, 0.12) 0%,
            rgba(0, 212, 255, 0.04) 100%) !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 10px !important;
        color: {TOKENS['cyan']} !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
        padding: 12px 28px !important;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        position: relative !important;
        overflow: hidden !important;
        width: 100% !important;
    }}

    .stApp .stButton > button::before {{
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg,
            transparent,
            rgba(0, 212, 255, 0.15),
            transparent) !important;
        transition: left 0.5s ease !important;
    }}

    .stApp .stButton > button:hover {{
        background: linear-gradient(135deg,
            rgba(0, 212, 255, 0.22) 0%,
            rgba(0, 212, 255, 0.10) 100%) !important;
        border-color: {TOKENS['cyan']} !important;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.15),
                    0 4px 16px rgba(0, 0, 0, 0.3) !important;
        transform: translateY(-2px) !important;
    }}

    .stApp .stButton > button:hover::before {{
        left: 100% !important;
    }}

    .stApp .stButton > button:active {{
        transform: translateY(0) !important;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.1) !important;
    }}

    /* ── STREAMLIT METRICS — Premium Style ── */
    .stApp [data-testid="stMetric"] {{
        background: linear-gradient(135deg,
            rgba(0, 212, 255, 0.06) 0%,
            rgba(15, 23, 42, 0.8) 100%) !important;
        border: 1px solid rgba(0, 212, 255, 0.1) !important;
        border-radius: 14px !important;
        padding: 20px 24px !important;
        transition: all 0.3s ease !important;
    }}

    .stApp [data-testid="stMetric"]:hover {{
        border-color: rgba(0, 212, 255, 0.25) !important;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.06) !important;
    }}

    .stApp [data-testid="stMetricValue"] {{
        color: {TOKENS['cyan']} !important;
        font-weight: 700 !important;
        font-size: 28px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }}

    .stApp [data-testid="stMetricLabel"] {{
        color: rgba(148, 163, 184, 0.8) !important;
        font-weight: 500 !important;
        font-size: 11px !important;
        letter-spacing: 1.2px !important;
        text-transform: uppercase !important;
    }}

    .stApp [data-testid="stMetricDelta"] > div {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
    }}

    /* ── HORIZONTAL BLOCKS — Even spacing ── */
    .stApp [data-testid="stHorizontalBlock"] {{
        gap: 16px !important;
    }}

    /* ── SECTION HEADERS ── */
    .stApp h1 {{
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
        color: #f0f4f8 !important;
        letter-spacing: -0.5px !important;
    }}

    .stApp h2 {{
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        color: #e2e8f0 !important;
        letter-spacing: -0.3px !important;
    }}

    .stApp h3 {{
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        color: #cbd5e1 !important;
        letter-spacing: 0 !important;
    }}

    /* ── MARKDOWN TEXT REFINEMENT ── */
    .stApp .stMarkdown p {{
        color: rgba(203, 213, 225, 0.85) !important;
        line-height: 1.65 !important;
    }}

    /* ── HORIZONTAL DIVIDERS ── */
    .stApp hr {{
        border-color: rgba(0, 212, 255, 0.08) !important;
        margin: 24px 0 !important;
    }}

    /* ── EXPANDER PREMIUM ── */
    .stApp [data-testid="stExpander"] {{
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(0, 212, 255, 0.08) !important;
        border-radius: 12px !important;
    }}

    .stApp [data-testid="stExpander"]:hover {{
        border-color: rgba(0, 212, 255, 0.15) !important;
    }}

    /* ── SELECTBOX / INPUT FIELDS ── */
    .stApp [data-testid="stSelectbox"],
    .stApp [data-testid="stMultiSelect"] {{
        background: rgba(15, 23, 42, 0.6) !important;
    }}

    .stApp .stSelectbox > div > div,
    .stApp .stMultiSelect > div > div {{
        background: rgba(15, 23, 42, 0.8) !important;
        border-color: rgba(0, 212, 255, 0.12) !important;
        border-radius: 10px !important;
    }}

    /* ── TABS PREMIUM ── */
    .stApp .stTabs [data-baseweb="tab-list"] {{
        gap: 4px !important;
        border-bottom: 1px solid rgba(0, 212, 255, 0.08) !important;
    }}

    .stApp .stTabs [data-baseweb="tab"] {{
        border-radius: 8px 8px 0 0 !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
        color: rgba(148, 163, 184, 0.7) !important;
        transition: all 0.25s ease !important;
    }}

    .stApp .stTabs [aria-selected="true"] {{
        color: {TOKENS['cyan']} !important;
        background: rgba(0, 212, 255, 0.06) !important;
        border-bottom: 2px solid {TOKENS['cyan']} !important;
    }}

    /* ── PLOTLY CHART CONTAINERS ── */
    .stApp [data-testid="stPlotlyChart"] {{
        border: 1px solid rgba(0, 212, 255, 0.06) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        background: rgba(10, 14, 23, 0.5) !important;
    }}

    /* ── DATAFRAME / TABLE ── */
    .stApp [data-testid="stDataFrame"] {{
        border: 1px solid rgba(0, 212, 255, 0.08) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }}

    /* ── SCROLLBAR PREMIUM ── */
    .stApp ::-webkit-scrollbar {{
        width: 6px !important;
        height: 6px !important;
    }}
    .stApp ::-webkit-scrollbar-track {{
        background: rgba(10, 14, 23, 0.3) !important;
    }}
    .stApp ::-webkit-scrollbar-thumb {{
        background: rgba(0, 212, 255, 0.15) !important;
        border-radius: 3px !important;
    }}
    .stApp ::-webkit-scrollbar-thumb:hover {{
        background: rgba(0, 212, 255, 0.3) !important;
    }}

    /* ── SIDEBAR PREMIUM INTERIOR ── */
    .stApp [data-testid="stSidebar"] {{
        background: linear-gradient(180deg,
            rgba(8, 12, 21, 0.98) 0%,
            rgba(10, 14, 23, 0.99) 100%) !important;
        border-right: 1px solid rgba(0, 212, 255, 0.06) !important;
    }}

    .stApp [data-testid="stSidebar"] [data-testid="stSelectbox"] label,
    .stApp [data-testid="stSidebar"] .stRadio label {{
        color: rgba(148, 163, 184, 0.7) !important;
        font-size: 11px !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
        font-weight: 500 !important;
    }}

    /* ── TOAST / ALERTS ── */
    .stApp [data-testid="stAlert"] {{
        border-radius: 12px !important;
        border-left: 3px solid {TOKENS['cyan']} !important;
        background: rgba(0, 212, 255, 0.04) !important;
    }}

    /* ── LOADING SPINNER ── */
    .stApp .stSpinner > div {{
        border-top-color: {TOKENS['cyan']} !important;
    }}

    </style>
    """, unsafe_allow_html=True)


def inject_home_hero():
    """
    Home page hero — Enhanced AI + Geopolitical Network visualization.
    Central AI core + city network + data packets + HUD indicators.
    World + AI + NERAI combined in one premium hero section.
    """
    _stc.html("""
    <style>
        html, body { margin:0; padding:0; background:#0a0e17; overflow:hidden; font-family:'Inter',sans-serif; }
        /* ── NERAI HERO — Scoped styles ── */
        #nerai-hero-wrap {
            position: relative;
            width: 100%;
            height: 520px;
            overflow: hidden;
            border-radius: 20px;
            background: radial-gradient(ellipse at 50% 50%, rgba(0,212,255,0.04) 0%, #0a0e17 70%);
            margin-bottom: 2rem;
        }
        #nerai-hero-wrap canvas {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        }

        /* Corner brackets */
        .nh-corner { position:absolute; width:28px; height:28px; pointer-events:none; }
        .nh-corner.tl { top:14px; left:14px; border-top:2px solid rgba(0,212,255,0.35); border-left:2px solid rgba(0,212,255,0.35); }
        .nh-corner.tr { top:14px; right:14px; border-top:2px solid rgba(0,212,255,0.35); border-right:2px solid rgba(0,212,255,0.35); }
        .nh-corner.bl { bottom:40px; left:14px; border-bottom:2px solid rgba(0,212,255,0.35); border-left:2px solid rgba(0,212,255,0.35); }
        .nh-corner.br { bottom:40px; right:14px; border-bottom:2px solid rgba(0,212,255,0.35); border-right:2px solid rgba(0,212,255,0.35); }

        /* HUD panels */
        .nh-hud { position:absolute; pointer-events:none; z-index:12;
                   font-family:'JetBrains Mono',monospace; }
        .nh-hud-tl { top:18px; left:18px; }
        .nh-hud-tr { top:18px; right:18px; text-align:right; }
        .nh-hud-bl { bottom:44px; left:18px; }
        .nh-hud-br { bottom:44px; right:18px; text-align:right; }
        .nh-hud-label { font-size:9px; letter-spacing:1.5px; color:rgba(0,212,255,0.45);
                        text-transform:uppercase; margin-bottom:2px; }
        .nh-hud-val { font-size:15px; font-weight:700; color:rgba(0,212,255,0.85);
                      text-shadow:0 0 12px rgba(0,212,255,0.2); }

        /* Branding overlay — bottom-left, compact */
        .nh-brand { position:absolute; bottom:36px; left:24px;
                    display:flex; align-items:center; gap:14px;
                    z-index:10; pointer-events:none; }
        .nh-brand svg { flex-shrink:0; filter:drop-shadow(0 0 10px rgba(0,212,255,0.25)); }
        .nh-brand .nh-brand-text h1 { font-family:'Inter',sans-serif; font-size:1.4rem; font-weight:900;
                       letter-spacing:-0.5px; color:#e8edf4; margin:0;
                       text-shadow:0 0 30px rgba(0,212,255,0.1); }
        .nh-brand .nh-brand-text h1 span { color:#00d4ff; }
        .nh-brand .nh-sub { font-size:0.5rem; font-weight:600; letter-spacing:3px;
                            text-transform:uppercase; color:rgba(0,212,255,0.45);
                            margin-top:2px; }
        .nh-brand .nh-desc { display:none; }

        /* Ticker */
        .nh-ticker { position:absolute; bottom:0; left:0; right:0; height:26px;
                     background:linear-gradient(90deg,rgba(0,212,255,0.04),rgba(0,212,255,0.02));
                     border-top:1px solid rgba(0,212,255,0.08);
                     overflow:hidden; display:flex; align-items:center; pointer-events:none; z-index:11; }
        .nh-ticker-inner { display:flex; gap:3rem; animation:nh-scroll 35s linear infinite;
                           white-space:nowrap; font-family:'JetBrains Mono',monospace;
                           font-size:0.58rem; letter-spacing:1px; color:rgba(0,212,255,0.22); }
        @keyframes nh-scroll { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }

        /* Scanline */
        .nh-scanline { position:absolute; left:0; right:0; height:1px;
                       background:linear-gradient(90deg,transparent,rgba(0,212,255,0.2),transparent);
                       animation:nh-scan 5s linear infinite; pointer-events:none; z-index:3; }
        @keyframes nh-scan { 0%{top:0} 100%{top:100%} }
    </style>

    <div id="nerai-hero-wrap">
        <canvas id="nh-canvas"></canvas>
        <div class="nh-scanline"></div>

        <!-- Corner brackets -->
        <div class="nh-corner tl"></div><div class="nh-corner tr"></div>
        <div class="nh-corner bl"></div><div class="nh-corner br"></div>

        <!-- HUD indicators -->
        <div class="nh-hud nh-hud-tl">
            <div class="nh-hud-label">THREATS DETECTED</div>
            <div class="nh-hud-val" id="nh-threats">17</div>
        </div>
        <div class="nh-hud nh-hud-tr">
            <div class="nh-hud-label">AI CONFIDENCE</div>
            <div class="nh-hud-val" id="nh-conf">94.2%</div>
        </div>
        <div class="nh-hud nh-hud-bl">
            <div class="nh-hud-label">DATA STREAMS</div>
            <div class="nh-hud-val" id="nh-streams">2,847</div>
        </div>
        <div class="nh-hud nh-hud-br">
            <div class="nh-hud-label">COVERAGE</div>
            <div class="nh-hud-val">195 NATIONS</div>
        </div>

        <!-- Brand overlay — compact bottom-left -->
        <div class="nh-brand">
            <svg width="28" height="28" viewBox="0 0 48 48">
                <circle cx="6" cy="6" r="3.2" fill="#0a0e17"/><circle cx="16" cy="6" r="3.2" fill="#00d4ff"/>
                <circle cx="26" cy="6" r="3.2" fill="#0a0e17"/><circle cx="36" cy="6" r="3.2" fill="#00d4ff"/>
                <circle cx="6" cy="16" r="3.2" fill="#00d4ff"/><circle cx="16" cy="16" r="3.2" fill="#0a0e17"/>
                <circle cx="26" cy="16" r="3.2" fill="#00d4ff"/><circle cx="36" cy="16" r="3.2" fill="#0a0e17"/>
                <circle cx="6" cy="26" r="3.2" fill="#0a0e17"/><circle cx="16" cy="26" r="3.2" fill="#00d4ff"/>
                <circle cx="26" cy="26" r="3.2" fill="#0a0e17"/><circle cx="36" cy="26" r="3.2" fill="#00d4ff"/>
                <circle cx="6" cy="36" r="3.2" fill="#00d4ff"/><circle cx="16" cy="36" r="3.2" fill="#0a0e17"/>
                <circle cx="26" cy="36" r="3.2" fill="#00d4ff"/><circle cx="36" cy="36" r="3.2" fill="#0a0e17"/>
            </svg>
            <div class="nh-brand-text">
                <h1>NER<span>AI</span></h1>
                <div class="nh-sub">STRATEGIC INSIGHTS HUB</div>
            </div>
        </div>

        <!-- Ticker -->
        <div class="nh-ticker">
            <div class="nh-ticker-inner">
                <span>ACTIVE MONITORS: 2,847</span><span>DATA STREAMS: 156</span>
                <span>RISK ALERTS: 23</span><span>COVERAGE: 195 COUNTRIES</span>
                <span>AI MODELS: 12 ACTIVE</span><span>LATENCY: 340ms</span>
                <span>UPTIME: 99.97%</span><span>SOURCES: GDELT · NEWS · COMMODITIES</span>
                <span>ACTIVE MONITORS: 2,847</span><span>DATA STREAMS: 156</span>
                <span>RISK ALERTS: 23</span><span>COVERAGE: 195 COUNTRIES</span>
                <span>AI MODELS: 12 ACTIVE</span><span>LATENCY: 340ms</span>
            </div>
        </div>
    </div>

    <script>
    // ─── NERAI Enhanced Hero: AI Core + Geopolitical Network ───
    (function(){
        var canvas = document.getElementById('nh-canvas');
        if(!canvas) return;
        var ctx = canvas.getContext('2d');
        var W, H, cx, cy, t=0;
        var mouse = {x:-9999, y:-9999};

        // ── City nodes (world-map positions) ──
        var cities = [
            {n:'Washington',rx:0.22,ry:0.38,risk:0},{n:'London',rx:0.44,ry:0.26,risk:0},
            {n:'Moscow',rx:0.58,ry:0.22,risk:0},{n:'Beijing',rx:0.74,ry:0.33,risk:0},
            {n:'Delhi',rx:0.66,ry:0.47,risk:0},{n:'Tokyo',rx:0.84,ry:0.33,risk:0},
            {n:'São Paulo',rx:0.30,ry:0.68,risk:0},{n:'Lagos',rx:0.46,ry:0.57,risk:0},
            {n:'Dubai',rx:0.58,ry:0.44,risk:0},{n:'Sydney',rx:0.84,ry:0.73,risk:0},
            {n:'Cairo',rx:0.52,ry:0.42,risk:0},{n:'Berlin',rx:0.48,ry:0.25,risk:0},
            {n:'Istanbul',rx:0.53,ry:0.33,risk:0},{n:'Singapore',rx:0.74,ry:0.58,risk:0},
            {n:'Ankara',rx:0.55,ry:0.35,risk:0},{n:'Nairobi',rx:0.54,ry:0.60,risk:0}
        ];

        // ── Floating particles ──
        var pts = [];
        function initPts(){
            pts=[];
            for(var i=0;i<70;i++){
                pts.push({x:Math.random()*W, y:Math.random()*H,
                          vx:(Math.random()-0.5)*0.25, vy:(Math.random()-0.5)*0.25,
                          r:Math.random()*1.2+0.4, a:Math.random()*0.4+0.15});
            }
        }

        // ── Data packets (travel between cities) ──
        var packets = [];
        function spawnPacket(){
            if(packets.length >= 12) return;
            var a = Math.floor(Math.random()*cities.length);
            var b = Math.floor(Math.random()*cities.length);
            if(a===b) b = (b+1)%cities.length;
            packets.push({from:a, to:b, prog:0, speed:0.004+Math.random()*0.006,
                          color: Math.random()>0.7 ? 'rgba(255,179,71,0.9)' : 'rgba(0,212,255,0.9)'});
        }

        // ── Resize ──
        function resize(){
            var r = canvas.parentElement.getBoundingClientRect();
            W = canvas.width = r.width;
            H = canvas.height = r.height;
            cx = W/2; cy = H/2;
            // Update city screen positions
            cities.forEach(function(c){ c.x=c.rx*W; c.y=c.ry*H; c.pulse=Math.random()*6.28; });
            if(pts.length===0) initPts();
        }
        resize();
        window.addEventListener('resize', resize);

        // Mouse interaction
        canvas.addEventListener('mousemove', function(e){
            var r=canvas.getBoundingClientRect();
            mouse.x=e.clientX-r.left; mouse.y=e.clientY-r.top;
        });
        canvas.addEventListener('mouseleave', function(){ mouse.x=-9999; mouse.y=-9999; });

        // ── Assign random risk levels periodically ──
        function updateRisks(){
            cities.forEach(function(c){
                c.risk = Math.random();  // 0=safe, >0.6=amber, >0.8=red
            });
        }
        updateRisks();
        setInterval(updateRisks, 8000);

        // ── HUD counter animation ──
        function updateHUD(){
            var el1 = document.getElementById('nh-threats');
            var el2 = document.getElementById('nh-conf');
            var el3 = document.getElementById('nh-streams');
            if(el1) el1.textContent = Math.floor(Math.random()*20+8);
            if(el2) el2.textContent = (Math.random()*6+92).toFixed(1)+'%';
            if(el3) el3.textContent = (Math.floor(Math.random()*500+2500)).toLocaleString();
        }
        setInterval(updateHUD, 4000);

        // ═══ DRAW ═══
        function draw(){
            t += 0.016;
            ctx.fillStyle = 'rgba(10,14,23,0.92)';
            ctx.fillRect(0,0,W,H);

            // ── 1. Background dot grid (pulsing from center) ──
            var gridSp = 45;
            var pulseWave = Math.sin(t*0.8)*0.3+0.5;
            for(var gx=0; gx<W; gx+=gridSp){
                for(var gy=0; gy<H; gy+=gridSp){
                    var dx=gx-cx, dy=gy-cy;
                    var dist=Math.sqrt(dx*dx+dy*dy);
                    var maxD = Math.max(W,H)*0.55;
                    if(dist<maxD){
                        var op = (1-dist/maxD)*pulseWave*0.12;
                        ctx.fillStyle = 'rgba(0,212,255,'+op+')';
                        ctx.beginPath();
                        ctx.arc(gx, gy, 1, 0, 6.28);
                        ctx.fill();
                    }
                }
            }

            // ── 2. AI Core: concentric rotating arcs ──
            for(var ring=1; ring<=3; ring++){
                var radius = 35 + ring*22;
                var rot = t * (ring%2===0 ? 0.5 : -0.4) * (0.8+ring*0.1);
                ctx.strokeStyle = 'rgba(0,212,255,'+(0.25-ring*0.06)+')';
                ctx.lineWidth = 1.5;
                ctx.setLineDash([10,14]);
                ctx.beginPath();
                ctx.arc(cx, cy, radius, rot, rot + 3.6);
                ctx.stroke();
                ctx.setLineDash([]);
            }
            // Core glow
            var coreR = 18 + Math.sin(t*1.2)*4;
            var grad = ctx.createRadialGradient(cx,cy,0, cx,cy, coreR+30);
            grad.addColorStop(0, 'rgba(0,212,255,0.12)');
            grad.addColorStop(1, 'rgba(0,212,255,0)');
            ctx.fillStyle = grad;
            ctx.beginPath(); ctx.arc(cx,cy,coreR+30,0,6.28); ctx.fill();
            // Core dot
            ctx.fillStyle = 'rgba(0,212,255,0.5)';
            ctx.beginPath(); ctx.arc(cx,cy,coreR,0,6.28); ctx.fill();
            ctx.fillStyle = 'rgba(255,255,255,0.7)';
            ctx.beginPath(); ctx.arc(cx,cy,3,0,6.28); ctx.fill();

            // Neural rays from core to edges
            for(var ray=0; ray<8; ray++){
                var angle = (ray/8)*6.28 + t*0.15;
                var len = 70 + Math.sin(t*0.7+ray*1.3)*25;
                var rx = cx + Math.cos(angle)*len;
                var ry = cy + Math.sin(angle)*len;
                ctx.strokeStyle = 'rgba(0,212,255,0.08)';
                ctx.lineWidth = 0.8;
                ctx.beginPath(); ctx.moveTo(cx,cy); ctx.lineTo(rx,ry); ctx.stroke();
                ctx.fillStyle = 'rgba(0,212,255,0.25)';
                ctx.beginPath(); ctx.arc(rx,ry,1.5,0,6.28); ctx.fill();
            }

            // ── 3. Orbit ellipses ──
            ctx.save();
            ctx.strokeStyle = 'rgba(0,212,255,0.06)';
            ctx.lineWidth = 0.8;
            ctx.setLineDash([3,8]);
            ctx.beginPath(); ctx.ellipse(cx,cy, 140,90, 0.15, 0, 6.28); ctx.stroke();
            ctx.beginPath(); ctx.ellipse(cx,cy, 200,110, -0.2, 0, 6.28); ctx.stroke();
            ctx.setLineDash([]);
            // Orbiting dots
            var oa1 = t*0.6;
            var ox1 = cx+Math.cos(oa1)*140*Math.cos(0.15)-Math.sin(oa1)*90*Math.sin(0.15);
            var oy1 = cy+Math.sin(oa1)*140*Math.cos(0.15)+Math.cos(oa1)*90*Math.sin(0.15);
            ctx.fillStyle = 'rgba(0,212,255,0.7)';
            ctx.beginPath(); ctx.arc(ox1,oy1,2.5,0,6.28); ctx.fill();
            var oa2 = t*0.35+3.14;
            var ox2 = cx+Math.cos(oa2)*200*Math.cos(-0.2)-Math.sin(oa2)*110*Math.sin(-0.2);
            var oy2 = cy+Math.sin(oa2)*200*Math.cos(-0.2)+Math.cos(oa2)*110*Math.sin(-0.2);
            ctx.fillStyle = 'rgba(0,212,255,0.5)';
            ctx.beginPath(); ctx.arc(ox2,oy2,2,0,6.28); ctx.fill();
            ctx.restore();

            // ── 4. City bezier connections ──
            var conns = [[0,1],[1,2],[2,3],[3,5],[4,8],[1,11],[11,2],[7,10],[6,0],[9,5],
                         [8,10],[10,7],[12,14],[13,3],[15,7],[4,13],[6,7],[0,6],[1,12],[8,14]];
            conns.forEach(function(c){
                var a=cities[c[0]], b=cities[c[1]];
                var mx=(a.x+b.x)/2, my=(a.y+b.y)/2;
                // Curved arc (control point offset perpendicular)
                var dx=b.x-a.x, dy=b.y-a.y;
                var cpx = mx - dy*0.15;
                var cpy = my + dx*0.15;
                ctx.strokeStyle = 'rgba(0,212,255,0.07)';
                ctx.lineWidth = 0.7;
                ctx.beginPath();
                ctx.moveTo(a.x, a.y);
                ctx.quadraticCurveTo(cpx, cpy, b.x, b.y);
                ctx.stroke();
            });

            // ── 5. City nodes with risk coloring ──
            cities.forEach(function(c){
                c.pulse += 0.025;
                var pr = 3 + Math.sin(c.pulse)*1.2;
                var col, gcol;
                if(c.risk > 0.8){ col='rgba(255,71,87,'; gcol='rgba(255,71,87,'; }
                else if(c.risk > 0.55){ col='rgba(255,179,71,'; gcol='rgba(255,179,71,'; }
                else { col='rgba(0,212,255,'; gcol='rgba(0,212,255,'; }
                // Glow
                ctx.fillStyle = gcol+(0.04+Math.sin(c.pulse)*0.02)+')';
                ctx.beginPath(); ctx.arc(c.x,c.y,pr+8,0,6.28); ctx.fill();
                // Node
                ctx.fillStyle = col+(0.55+Math.sin(c.pulse)*0.25)+')';
                ctx.beginPath(); ctx.arc(c.x,c.y,pr,0,6.28); ctx.fill();
                // Center
                ctx.fillStyle = '#fff';
                ctx.beginPath(); ctx.arc(c.x,c.y,1.2,0,6.28); ctx.fill();
                // Label
                ctx.font = '500 8.5px Inter,sans-serif';
                ctx.fillStyle = 'rgba(138,155,181,'+(0.4+Math.sin(c.pulse)*0.15)+')';
                ctx.fillText(c.n, c.x+9, c.y+3);
            });

            // ── 6. Data packets traveling on arcs ──
            if(Math.random()<0.04) spawnPacket();
            var alive = [];
            packets.forEach(function(p){
                p.prog += p.speed;
                if(p.prog >= 1) return; // drop finished
                alive.push(p);
                var a=cities[p.from], b=cities[p.to];
                var mx=(a.x+b.x)/2, my=(a.y+b.y)/2;
                var dx=b.x-a.x, dy=b.y-a.y;
                var cpx=mx-dy*0.15, cpy=my+dx*0.15;
                // Quadratic bezier position at t
                var u=p.prog, u1=1-u;
                var px = u1*u1*a.x + 2*u1*u*cpx + u*u*b.x;
                var py = u1*u1*a.y + 2*u1*u*cpy + u*u*b.y;
                ctx.fillStyle = p.color;
                ctx.beginPath(); ctx.arc(px,py,2,0,6.28); ctx.fill();
                // Glow trail
                ctx.fillStyle = p.color.replace('0.9','0.15');
                ctx.beginPath(); ctx.arc(px,py,5,0,6.28); ctx.fill();
            });
            packets = alive;

            // ── 7. Floating particles + connections ──
            pts.forEach(function(p){
                p.x+=p.vx; p.y+=p.vy;
                if(p.x<0||p.x>W) p.vx*=-1;
                if(p.y<0||p.y>H) p.vy*=-1;
                // Mouse repel
                var mdx=p.x-mouse.x, mdy=p.y-mouse.y;
                var md=Math.sqrt(mdx*mdx+mdy*mdy);
                if(md<100){p.vx+=mdx/md*0.06;p.vy+=mdy/md*0.06;}
                p.vx*=0.997; p.vy*=0.997;
                ctx.fillStyle='rgba(0,212,255,'+p.a*0.35+')';
                ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,6.28); ctx.fill();
            });
            // Particle-to-particle connections
            var maxC=100;
            for(var i=0;i<pts.length;i++){
                for(var j=i+1;j<pts.length;j++){
                    var ddx=pts[i].x-pts[j].x, ddy=pts[i].y-pts[j].y;
                    var dd=Math.sqrt(ddx*ddx+ddy*ddy);
                    if(dd<maxC){
                        ctx.strokeStyle='rgba(0,212,255,'+(1-dd/maxC)*0.06+')';
                        ctx.lineWidth=0.4;
                        ctx.beginPath();ctx.moveTo(pts[i].x,pts[i].y);ctx.lineTo(pts[j].x,pts[j].y);ctx.stroke();
                    }
                }
            }

            requestAnimationFrame(draw);
        }
        draw();
    })();
    </script>
    """, height=540, scrolling=False)


def inject_kpi_row(metrics):
    """
    Premium KPI row.
    metrics = [{"value": "195+", "label": "COUNTRIES MONITORED"}, ...]
    """
    cols_html = ""
    for m in metrics:
        cols_html += f"""
        <div class="nerai-kpi" style="flex:1;min-width:160px;">
            <div class="kpi-value">{m['value']}</div>
            <div class="kpi-label">{m['label']}</div>
        </div>
        """

    st.markdown(f"""
    <div style="display:flex;gap:1rem;flex-wrap:wrap;margin:1.5rem 0;">
        {cols_html}
    </div>
    """, unsafe_allow_html=True)


def inject_module_cards(modules):
    """
    Home page module navigation cards.
    modules = [{"icon": "📊", "title": "Indices", "desc": "...", "page_key": "indices"}, ...]
    """
    cards_html = ""
    for m in modules:
        cards_html += f"""
        <div class="nerai-module-card" style="flex:1;min-width:220px;">
            <div style="font-size:1.5rem;margin-bottom:0.75rem;">{m['icon']}</div>
            <h4>{m['title']}</h4>
            <p>{m['desc']}</p>
            <div style="margin-top:1rem;font-size:0.75rem;color:#00d4ff;font-weight:600;letter-spacing:1px;">
                → OPEN
            </div>
        </div>
        """

    st.markdown(f"""
    <div style="display:flex;gap:1rem;flex-wrap:wrap;margin:1.5rem 0;">
        {cards_html}
    </div>
    """, unsafe_allow_html=True)


def inject_freshness_bar(gdelt_ago="2h", commodities_ago="4h", news_ago="1h", status="online"):
    """Data freshness indicator bar."""
    dot_class = "live" if status == "online" else ("ok" if status == "ok" else "stale")
    st.markdown(f"""
    <div class="nerai-freshness">
        <span><span class="dot {dot_class}"></span>GDELT: {gdelt_ago} ago</span>
        <span>|</span>
        <span>Commodities: {commodities_ago} ago</span>
        <span>|</span>
        <span>News: {news_ago} ago</span>
        <span>|</span>
        <span style="color:#00e676;">● ONLINE</span>
    </div>
    """, unsafe_allow_html=True)


def inject_section_header(text):
    """Branded section divider."""
    st.markdown(f"""
    <div class="nerai-section-header">{text}</div>
    """, unsafe_allow_html=True)


def inject_sidebar_fix():
    """
    Critical fix: Override any 'button[kind=header] display:none' rules
    that break sidebar collapse/expand. Must load AFTER main CSS.
    Correct Streamlit data-testid attributes (verified via DOM inspection):
      - stSidebarCollapseButton  (collapse button container)
      - stBaseButton-headerNoPadding (the actual button)
      - collapsedControl / stSidebarCollapsedControl (expand when collapsed)
    """
    st.markdown("""
    <style>
    /* ══ SIDEBAR ARROW FIX — LAST CSS LOADED, HIGHEST PRIORITY ══ */

    /* 1. Force sidebar collapse button visible when sidebar is OPEN */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebarCollapseButton"] button[data-testid="stBaseButton-headerNoPadding"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 999999 !important;
        color: #00d4ff !important;
        cursor: pointer !important;
    }

    /* 2. Force sidebar expand button visible when sidebar is COLLAPSED */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 999999 !important;
    }
    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapsedControl"] button {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        color: #00d4ff !important;
        background: #111827 !important;
        border: 1px solid rgba(0,212,255,0.15) !important;
        border-radius: 8px !important;
        cursor: pointer !important;
    }
    [data-testid="collapsedControl"] button:hover,
    [data-testid="stSidebarCollapsedControl"] button:hover {
        background: rgba(0,212,255,0.08) !important;
        border-color: #00d4ff !important;
    }

    /* 3. CRITICAL: Force Material Symbols font on ALL icon spans */
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="stSidebarCollapseButton"] span span,
    [data-testid="stBaseButton-headerNoPadding"] span,
    [data-testid="collapsedControl"] span,
    [data-testid="stSidebarCollapsedControl"] span,
    [data-testid="stSidebar"] [data-testid="stBaseButton-headerNoPadding"] span,
    span.st-emotion-cache-12bp31y,
    span[class*="ed4y4ls0"],
    .material-symbols-rounded {
        font-family: 'Material Symbols Rounded' !important;
        font-size: 24px !important;
        -webkit-font-smoothing: antialiased;
        font-style: normal;
        font-weight: normal;
        line-height: 1;
        letter-spacing: normal;
        text-transform: none;
        white-space: nowrap;
        word-wrap: normal;
        direction: ltr;
        -webkit-font-feature-settings: 'liga';
        font-feature-settings: 'liga';
    }

    /* 4. Ensure the collapse button in sidebar header is not hidden */
    [data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"] {
        display: flex !important;
        visibility: visible !important;
        color: #00d4ff !important;
    }

    /* 5. Custom expand button style (injected by JS below) */
    #nerai-sidebar-expand {
        position: fixed !important;
        top: 8px !important;
        left: 8px !important;
        z-index: 999999 !important;
        width: 32px !important;
        height: 32px !important;
        background: #111827 !important;
        border: 1px solid rgba(0,212,255,0.2) !important;
        border-radius: 8px !important;
        color: #00d4ff !important;
        font-size: 18px !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.2s ease !important;
        font-family: sans-serif !important;
    }
    #nerai-sidebar-expand:hover {
        background: rgba(0,212,255,0.1) !important;
        border-color: #00d4ff !important;
        box-shadow: 0 0 12px rgba(0,212,255,0.15) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- JavaScript: Watch for sidebar collapse and inject expand button ---
    # st.markdown strips <script> tags, so we use components.html
    # which runs in an iframe but can access parent via window.parent
    _stc.html("""
    <script>
    (function() {
        const doc = window.parent.document;
        const SIDEBAR_SEL = '[data-testid="stSidebar"]';
        const EXPAND_ID = 'nerai-sidebar-expand';

        function isSidebarCollapsed() {
            const sb = doc.querySelector(SIDEBAR_SEL);
            if (!sb) return true;
            const rect = sb.getBoundingClientRect();
            return rect.left < -50 || rect.width < 10;
        }

        function expandSidebar() {
            // Try native Streamlit expand controls first
            const native = doc.querySelector('[data-testid="collapsedControl"] button') ||
                           doc.querySelector('[data-testid="stSidebarCollapsedControl"] button');
            if (native) { native.click(); removeBtn(); return; }

            // Fallback: force sidebar visible, keep styles until user collapses
            var sb = doc.querySelector(SIDEBAR_SEL);
            if (sb) {
                // 1. Force sidebar visible (keep styles until user collapses)
                sb.style.transition = 'transform 0.3s ease';
                sb.style.transform = 'none';
                sb.style.width = '300px';
                sb.style.minWidth = '300px';
                sb.style.left = '0px';
                removeBtn();

                // 2. Update Streamlit localStorage state
                try {
                    var keys = Object.keys(localStorage);
                    for (var i = 0; i < keys.length; i++) {
                        if (keys[i].indexOf('stSidebarCollapsed') !== -1) {
                            localStorage.setItem(keys[i], 'false');
                        }
                    }
                } catch(e) {}

                // 3. Hook collapse button to clear forced styles on click
                function hookCollapseBtn() {
                    var cb = doc.querySelector('[data-testid="stSidebarCollapseButton"] button');
                    if (!cb) return;
                    if (cb._neraiClearStyles) {
                        cb.removeEventListener('click', cb._neraiClearStyles, true);
                    }
                    cb._neraiClearStyles = function() {
                        sb.style.transform = '';
                        sb.style.width = '';
                        sb.style.minWidth = '';
                        sb.style.left = '';
                        sb.style.transition = '';
                        cb.removeEventListener('click', cb._neraiClearStyles, true);
                        cb._neraiClearStyles = null;
                    };
                    cb.addEventListener('click', cb._neraiClearStyles, {capture: true});
                }
                hookCollapseBtn();
                setTimeout(hookCollapseBtn, 300);
                setTimeout(hookCollapseBtn, 800);
            }
        }

        function removeBtn() {
            const btn = doc.getElementById(EXPAND_ID);
            if (btn) btn.remove();
        }

        function addBtn() {
            if (doc.getElementById(EXPAND_ID)) return;
            const btn = doc.createElement('button');
            btn.id = EXPAND_ID;
            btn.innerHTML = '&#9776;';
            btn.title = 'Open Navigation';
            btn.addEventListener('click', expandSidebar);
            doc.body.appendChild(btn);
        }

        function check() {
            if (isSidebarCollapsed()) {
                addBtn();
            } else {
                removeBtn();
            }
        }

        // MutationObserver + interval for reliability
        try {
            const obs = new MutationObserver(check);
            obs.observe(doc.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['style','class'] });
        } catch(e) {}

        check();
        setInterval(check, 500);
    })();
    </script>
    """, height=0)


def inject_all():
    """Inject all global styles + freshness bar + sidebar fix. Call once at app start."""
    inject_global_css()
    inject_freshness_bar()
    inject_sidebar_fix()


# ─── Plotly Template ───
def get_plotly_template():
    """
    Returns a Plotly layout dict for consistent chart styling.
    Usage: fig.update_layout(**get_plotly_template())
    """
    return dict(
        paper_bgcolor="#0a0e17",
        plot_bgcolor="#0a0e17",
        font=dict(family="Inter, sans-serif", color="#8a9bb5", size=12),
        title_font=dict(family="Inter, sans-serif", color="#e8edf4", size=16, weight=700),
        xaxis=dict(
            gridcolor="rgba(0,212,255,0.05)",
            zerolinecolor="rgba(0,212,255,0.08)",
            tickfont=dict(color="#4a5d75", size=10),
        ),
        yaxis=dict(
            gridcolor="rgba(0,212,255,0.05)",
            zerolinecolor="rgba(0,212,255,0.08)",
            tickfont=dict(color="#4a5d75", size=10),
        ),
        colorway=["#00d4ff", "#ff4757", "#00e676", "#ffb347", "#b388ff",
                   "#0099cc", "#ff6b81", "#69db7c", "#ffd93d", "#da77f2"],
        hoverlabel=dict(
            bgcolor="#1a2338",
            font_size=12,
            font_family="Inter, sans-serif",
            font_color="#e8edf4",
            bordercolor="rgba(0,212,255,0.2)",
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8a9bb5", size=11),
        ),
        margin=dict(l=40, r=20, t=50, b=40),
    )
