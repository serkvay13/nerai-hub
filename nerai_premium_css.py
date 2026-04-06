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
    button[kind="header"],
    .css-1rs6os.edgvbvh3,
    [data-testid="stSidebar"] button[aria-label="Close"],
    [data-testid="stSidebar"] [data-testid="stSidebarNavCollapseIcon"],
    section[data-testid="stSidebar"] > div > button {{
        color: {TOKENS['cyan']} !important;
        background: {TOKENS['bg_card']} !important;
        border: 1px solid {TOKENS['cyan_border']} !important;
        border-radius: 8px !important;
        opacity: 1 !important;
        visibility: visible !important;
        z-index: 999999 !important;
    }}
    [data-testid="collapsedControl"]:hover,
    [data-testid="stSidebarCollapsedControl"]:hover {{
        background: {TOKENS['cyan_glow']} !important;
        border-color: {TOKENS['cyan']} !important;
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

    /* Paragraphs & default text */
    .stApp p, .stApp span, .stApp label {{
        font-family: 'Inter', sans-serif !important;
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

    /* Hide hamburger */
    button[kind="header"] {{ display: none !important; }}

    </style>
    """, unsafe_allow_html=True)


def inject_home_hero():
    """
    Home page hero — Interactive particle network globe.
    Mevcut spinning globe yerine kullanılacak.
    Daha hafif, daha futuristic, tam ekran uyumlu.
    """
    st.markdown("""
    <div id="nerai-hero-container" style="
        position: relative;
        width: 100%;
        height: 520px;
        overflow: hidden;
        border-radius: 20px;
        background: radial-gradient(ellipse at 50% 50%, rgba(0,212,255,0.04) 0%, #0a0e17 70%);
        margin-bottom: 2rem;
    ">
        <canvas id="nerai-globe-canvas" style="
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
        "></canvas>

        <!-- Grid overlay -->
        <div style="
            position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background:
                linear-gradient(rgba(0,212,255,0.015) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,212,255,0.015) 1px, transparent 1px);
            background-size: 50px 50px;
            pointer-events: none;
        "></div>

        <!-- Scan line -->
        <div id="nerai-scanline" style="
            position: absolute; left: 0; right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(0,212,255,0.3), transparent);
            animation: scanline 4s linear infinite;
            pointer-events: none;
        "></div>

        <!-- Corner brackets -->
        <div style="position:absolute;top:16px;left:16px;width:30px;height:30px;border-top:2px solid rgba(0,212,255,0.3);border-left:2px solid rgba(0,212,255,0.3);pointer-events:none;"></div>
        <div style="position:absolute;top:16px;right:16px;width:30px;height:30px;border-top:2px solid rgba(0,212,255,0.3);border-right:2px solid rgba(0,212,255,0.3);pointer-events:none;"></div>
        <div style="position:absolute;bottom:16px;left:16px;width:30px;height:30px;border-bottom:2px solid rgba(0,212,255,0.3);border-left:2px solid rgba(0,212,255,0.3);pointer-events:none;"></div>
        <div style="position:absolute;bottom:16px;right:16px;width:30px;height:30px;border-bottom:2px solid rgba(0,212,255,0.3);border-right:2px solid rgba(0,212,255,0.3);pointer-events:none;"></div>

        <!-- Content overlay -->
        <div style="
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            z-index: 10;
            pointer-events: none;
        ">
            <!-- NERAI Dot Grid Logo (SVG) -->
            <svg width="48" height="48" viewBox="0 0 48 48" style="margin-bottom:16px;filter:drop-shadow(0 0 12px rgba(0,212,255,0.4));">
                <circle cx="6" cy="6" r="3.5" fill="#0a0e17"/><circle cx="16" cy="6" r="3.5" fill="#00d4ff"/>
                <circle cx="26" cy="6" r="3.5" fill="#0a0e17"/><circle cx="36" cy="6" r="3.5" fill="#00d4ff"/>
                <circle cx="6" cy="16" r="3.5" fill="#00d4ff"/><circle cx="16" cy="16" r="3.5" fill="#0a0e17"/>
                <circle cx="26" cy="16" r="3.5" fill="#00d4ff"/><circle cx="36" cy="16" r="3.5" fill="#0a0e17"/>
                <circle cx="6" cy="26" r="3.5" fill="#0a0e17"/><circle cx="16" cy="26" r="3.5" fill="#00d4ff"/>
                <circle cx="26" cy="26" r="3.5" fill="#0a0e17"/><circle cx="36" cy="26" r="3.5" fill="#00d4ff"/>
                <circle cx="6" cy="36" r="3.5" fill="#00d4ff"/><circle cx="16" cy="36" r="3.5" fill="#0a0e17"/>
                <circle cx="26" cy="36" r="3.5" fill="#00d4ff"/><circle cx="36" cy="36" r="3.5" fill="#0a0e17"/>
            </svg>

            <div style="
                font-family: 'Inter', sans-serif;
                font-size: 2.2rem;
                font-weight: 900;
                letter-spacing: -1px;
                color: #e8edf4;
                text-shadow: 0 0 40px rgba(0,212,255,0.15);
                margin-bottom: 4px;
            ">
                NER<span style="color:#00d4ff">AI</span>
            </div>
            <div style="
                font-size: 0.62rem;
                font-weight: 600;
                letter-spacing: 4px;
                text-transform: uppercase;
                color: rgba(0,212,255,0.6);
                margin-bottom: 20px;
            ">STRATEGIC INSIGHTS HUB</div>

            <div style="
                font-size: 0.88rem;
                color: #8a9bb5;
                max-width: 380px;
                line-height: 1.6;
                margin: 0 auto;
            ">Geopolitical Risk Intelligence Platform</div>
        </div>

        <!-- Scrolling data ticker -->
        <div style="
            position: absolute;
            bottom: 14px; left: 0; right: 0;
            overflow: hidden;
            height: 22px;
            pointer-events: none;
        ">
            <div style="
                display: flex;
                gap: 3rem;
                animation: ticker 30s linear infinite;
                white-space: nowrap;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.6rem;
                letter-spacing: 1px;
                color: rgba(0,212,255,0.25);
            ">
                <span>MONITORS: 2,847</span>
                <span>DATA STREAMS: 156</span>
                <span>RISK ALERTS: 23</span>
                <span>COVERAGE: 195 COUNTRIES</span>
                <span>ACTIVE MONITORS: 2,847</span>
                <span>DATA STREAMS: 156</span>
                <span>RISK ALERTS: 23</span>
                <span>COVERAGE: 195 COUNTRIES</span>
                <span>MONITORS: 2,847</span>
                <span>DATA STREAMS: 156</span>
                <span>RISK ALERTS: 23</span>
                <span>COVERAGE: 195 COUNTRIES</span>
            </div>
        </div>
    </div>

    <style>
        @keyframes scanline {
            0% { top: 0; }
            100% { top: 100%; }
        }
        @keyframes ticker {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }
    </style>

    <script>
    // ─── NERAI Particle Network Globe ───
    (function() {
        const canvas = document.getElementById('nerai-globe-canvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        let w, h, particles = [], connections = [], mouse = {x: -1000, y: -1000};

        function resize() {
            const rect = canvas.parentElement.getBoundingClientRect();
            w = canvas.width = rect.width;
            h = canvas.height = rect.height;
        }
        resize();
        window.addEventListener('resize', resize);

        // City nodes (relative positions)
        const cities = [
            {name:'Washington',rx:0.22,ry:0.38},{name:'London',rx:0.44,ry:0.28},
            {name:'Moscow',rx:0.58,ry:0.24},{name:'Beijing',rx:0.74,ry:0.35},
            {name:'Delhi',rx:0.66,ry:0.48},{name:'Tokyo',rx:0.82,ry:0.35},
            {name:'São Paulo',rx:0.30,ry:0.65},{name:'Lagos',rx:0.46,ry:0.55},
            {name:'Dubai',rx:0.58,ry:0.45},{name:'Sydney',rx:0.82,ry:0.72},
            {name:'Cairo',rx:0.52,ry:0.42},{name:'Berlin',rx:0.49,ry:0.28},
            {name:'Istanbul',rx:0.53,ry:0.34},{name:'Singapore',rx:0.73,ry:0.58},
            {name:'Ankara',rx:0.54,ry:0.36},{name:'Nairobi',rx:0.54,ry:0.58},
        ];

        // Create particles
        const numParticles = 80;
        for (let i = 0; i < numParticles; i++) {
            particles.push({
                x: Math.random() * w,
                y: Math.random() * h,
                vx: (Math.random() - 0.5) * 0.3,
                vy: (Math.random() - 0.5) * 0.3,
                r: Math.random() * 1.5 + 0.5,
                isCity: false,
                alpha: Math.random() * 0.5 + 0.2,
            });
        }

        // Add city nodes
        cities.forEach(c => {
            particles.push({
                x: c.rx * w, y: c.ry * h,
                vx: 0, vy: 0, r: 3,
                isCity: true, name: c.name,
                alpha: 1, rx: c.rx, ry: c.ry,
                pulse: Math.random() * Math.PI * 2,
            });
        });

        canvas.addEventListener('mousemove', e => {
            const rect = canvas.getBoundingClientRect();
            mouse.x = e.clientX - rect.left;
            mouse.y = e.clientY - rect.top;
        });
        canvas.addEventListener('mouseleave', () => { mouse.x = -1000; mouse.y = -1000; });

        function draw() {
            ctx.clearRect(0, 0, w, h);

            const time = Date.now() * 0.001;

            // Update city positions on resize
            particles.forEach(p => {
                if (p.isCity) {
                    p.x = p.rx * w;
                    p.y = p.ry * h;
                    p.pulse += 0.02;
                }
            });

            // Move floating particles
            particles.forEach(p => {
                if (!p.isCity) {
                    p.x += p.vx;
                    p.y += p.vy;
                    if (p.x < 0 || p.x > w) p.vx *= -1;
                    if (p.y < 0 || p.y > h) p.vy *= -1;

                    // Mouse repel
                    const dx = p.x - mouse.x;
                    const dy = p.y - mouse.y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    if (dist < 100) {
                        p.vx += dx / dist * 0.08;
                        p.vy += dy / dist * 0.08;
                    }
                    // Damping
                    p.vx *= 0.995;
                    p.vy *= 0.995;
                }
            });

            // Draw connections
            const maxDist = 120;
            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    const threshold = (particles[i].isCity || particles[j].isCity) ? maxDist * 1.5 : maxDist;
                    if (dist < threshold) {
                        const alpha = (1 - dist / threshold) * 0.15;
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.strokeStyle = `rgba(0,212,255,${alpha})`;
                        ctx.lineWidth = 0.5;
                        ctx.stroke();
                    }
                }
            }

            // Draw particles
            particles.forEach(p => {
                if (p.isCity) {
                    // Pulsing city node
                    const pulseR = 3 + Math.sin(p.pulse) * 1.5;
                    // Outer glow
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, pulseR + 6, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(0,212,255,${0.03 + Math.sin(p.pulse) * 0.02})`;
                    ctx.fill();
                    // Core
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, pulseR, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(0,212,255,${0.6 + Math.sin(p.pulse) * 0.3})`;
                    ctx.fill();
                    // Center bright dot
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, 1.5, 0, Math.PI * 2);
                    ctx.fillStyle = '#fff';
                    ctx.fill();
                    // Label
                    ctx.font = '500 9px Inter, sans-serif';
                    ctx.fillStyle = `rgba(138,155,181,${0.5 + Math.sin(p.pulse) * 0.2})`;
                    ctx.fillText(p.name, p.x + 8, p.y + 3);
                } else {
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(0,212,255,${p.alpha * 0.4})`;
                    ctx.fill();
                }
            });

            // Random data transmission effect
            if (Math.random() < 0.02) {
                const cityNodes = particles.filter(p => p.isCity);
                if (cityNodes.length >= 2) {
                    const a = cityNodes[Math.floor(Math.random() * cityNodes.length)];
                    const b = cityNodes[Math.floor(Math.random() * cityNodes.length)];
                    if (a !== b) {
                        ctx.beginPath();
                        ctx.moveTo(a.x, a.y);
                        ctx.lineTo(b.x, b.y);
                        ctx.strokeStyle = 'rgba(0,212,255,0.25)';
                        ctx.lineWidth = 1.5;
                        ctx.stroke();
                    }
                }
            }

            requestAnimationFrame(draw);
        }
        draw();
    })();
    </script>
    """, unsafe_allow_html=True)


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


def inject_all():
    """Inject all global styles + freshness bar. Call once at app start."""
    inject_global_css()
    inject_freshness_bar()


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
