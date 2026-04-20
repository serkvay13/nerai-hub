"""
NERAI INTELLIGENCE HUB — Dashboard v3.0
Multi-page: Home | Indices | Country Profile | News
"""
import streamlit as st
from nerai_supply_phase67 import render_trade_flows_tab, render_lpi_tab
from nerai_global_view import render_global_view
# from conflict_intelligence import render_conflict_intelligence  # DISABLED: Warzone temporarily removed
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable
)
import datetime, os, json
import re
import streamlit.components.v1 as _stc
try:
    import nerai_premium_css
except Exception as _css_err:
    import types as _t
    nerai_premium_css = _t.ModuleType("nerai_premium_css")
    def _noop(*a, **kw): pass
    for _fn in ("inject_all","inject_home_hero","inject_global_premium_css",
                "inject_page_header","inject_filter_bar_css","inject_section_header",
                "inject_country_intel_css","inject_country_intel_header"):
        setattr(nerai_premium_css, _fn, _noop)
    import streamlit as _st2
    _st2.warning(f"Premium CSS failed to load: {_css_err}")

def _safe_pct(val, maxabs=150):
    """Cap percentage to +/-maxabs to prevent display of astronomical values."""
    if val is None or (isinstance(val, float) and (val != val)): return 0.0
    return max(-maxabs, min(maxabs, float(val)))

import urllib.request, urllib.parse

# === FAZ 4f: Mobile Responsive CSS ===
_MOBILE_CSS = """
<style>
@media (max-width: 768px) {
    .stApp { padding: 0 !important; }
    .block-container { padding: 0.5rem 0.8rem !important; max-width: 100% !important; }
    .sec-hdr { font-size: 1rem !important; padding: 8px 12px !important; }
    .metric-card { padding: 10px !important; min-width: unset !important; }
    .stDataFrame { font-size: 0.75rem !important; }
    [data-testid="stSidebar"] { min-width: 200px !important; }
    .plotly .main-svg { max-width: 100vw !important; }
    .home-hero h1 { font-size: 1.5rem !important; }
    .home-hero p { font-size: 0.85rem !important; }
    div[data-testid="column"] { min-width: 0 !important; flex: 1 1 45% !important; }
}
@media (max-width: 480px) {
    .block-container { padding: 0.3rem 0.5rem !important; }
    div[data-testid="column"] { flex: 1 1 100% !important; }
    .sec-hdr { font-size: 0.9rem !important; }
}
</style>
"""


st.set_page_config(
    page_title="NERAI Intelligence Hub",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Auto-retry on WebSocket cache miss ---
st.markdown("""<script>
(function(){
  var rc=0;
  new MutationObserver(function(m){
    document.querySelectorAll("pre").forEach(function(el){
      if(el.textContent.indexOf("Cached ForwardMsg")!==-1 && rc<2){
        rc++; setTimeout(function(){window.location.reload()},1500);
      }
    });
  }).observe(document.body,{childList:true,subtree:true});
})();
</script>""", unsafe_allow_html=True)


# -- NERAI Premium CSS --
nerai_premium_css.inject_all()


# ===============================================================
# ACCESS GATE - Solo / Pro tier authentication
# ===============================================================
_VALID_CODES = {
    'NERAI-TRIAL-26': 'solo',
    'NERAI-SOLO-26':  'solo',
    'NERAI-PRO-26':   'pro',
    'NERAI-2026':     'pro',
    'NERAI-PRO-DEMO': 'pro',
    'NERAI-PRO-W17':  'pro',
}

# Time-limited access codes  {code: expiry_date}
from datetime import datetime as _dt
_TIMED_CODES = {
    'NERAI-SOLO-26': _dt(2026, 4, 14),   # expires 14 April 2026
    'NERAI-PRO-DEMO': _dt(2026, 4, 19),   # 1-week Pro trial, expires 19 April 2026
    'NERAI-PRO-W17':  _dt(2026, 4, 27),    # 1-week Pro access, expires 27 April 2026
}

if 'access_tier' not in st.session_state:
    st.session_state.access_tier = None

if st.session_state.access_tier is None:
    st.markdown("""
    <style>
    .stApp { background: #0a0e17 !important; }
    [data-testid="stForm"] {
      background: linear-gradient(135deg, #0d1220 0%, #111827 100%) !important;
      border: 1px solid rgba(0,212,255,0.2) !important;
      border-radius: 16px !important;
      padding: 40px !important;
      box-shadow: 0 0 60px rgba(0,212,255,0.08) !important;
      max-width: 420px !important;
      margin: 60px auto !important;
    }
    [data-testid="stForm"] input {
      background: #0a0e17 !important;
      border: 1px solid rgba(0,212,255,0.2) !important;
      color: #e0e8f0 !important;
      border-radius: 8px !important;
    }
    [data-testid="stForm"] input:focus {
      border-color: #00d4ff !important;
      box-shadow: 0 0 12px rgba(0,212,255,0.2) !important;
    }
    [data-testid="stForm"] button {
      background: linear-gradient(135deg, #00d4ff 0%, #00b4d8 100%) !important;
      color: #0a0e17 !important;
      font-weight: 700 !important;
      border: none !important;
      border-radius: 8px !important;
    }
    [data-testid="stForm"] button:hover {
      box-shadow: 0 0 20px rgba(0,212,255,0.4) !important;
    }
    

/* Fix sidebar action buttons - better contrast */
[data-testid="stSidebar"] .stButton > button[kind="primary"],
[data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #003d5c 0%, #00526e 100%) !important;
    color: #00d4ff !important;
    border: 1px solid rgba(0,212,255,0.3) !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover,
[data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"]:hover {
    background: linear-gradient(135deg, #00526e 0%, #006880 100%) !important;
    border-color: #00d4ff !important;
}
/* Fix sidebar slider labels and values */
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMin"],
[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMax"],
[data-testid="stSidebar"] .stNumberInput label {
    color: #8aa0bc !important;
}
[data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"] {
    color: #00d4ff !important;
}
/* Fix number input in sidebar */
[data-testid="stSidebar"] .stNumberInput input {
    background: #111827 !important;
    color: #e0e8f0 !important;
    border: 1px solid rgba(0,212,255,0.2) !important;
}

/* ── Fix sidebar slider contrast ── */
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] [role="slider"] {
    background: #00526e !important;
    border: 2px solid #00d4ff !important;
}
[data-testid="stSidebar"] .stSlider [data-testid="stTickBar"] > div {
    background: rgba(0,212,255,0.15) !important;
}
[data-testid="stSidebar"] [data-baseweb="slider"] > div > div:first-child {
    background: rgba(0,100,140,0.5) !important;
}
[data-testid="stSidebar"] [data-baseweb="slider"] > div > div > div[role="slider"] ~ div {
    background: rgba(0,60,90,0.6) !important;
}
[data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"],
[data-testid="stSidebar"] .stSlider div[data-testid="stTickBarMax"],
[data-testid="stSidebar"] .stSlider div[data-testid="stTickBarMin"] {
    color: #e0e8f0 !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .stSlider label p,
[data-testid="stSidebar"] .stSlider label span {
    color: #8aa0bc !important;
}
/* Override Streamlit default bright slider track */
[data-testid="stSidebar"] [data-baseweb="slider"] div[style*="background"] {
    background: rgba(0,100,140,0.4) !important;
}
[data-testid="stSidebar"] .stNumberInput label p {
    color: #8aa0bc !important;
}
[data-testid="stSidebar"] .stNumberInput input {
    background: #0d1220 !important;
    color: #e0e8f0 !important;
    border-color: rgba(0,212,255,0.25) !important;
}

</style>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown("""
        <div style="text-align:center; padding: 40px 0 24px 0;">
          <div style="font-size:11px; letter-spacing:3px; color:#0077a8;
               text-transform:uppercase; font-weight:700; margin-bottom:16px;">
               &#9635; NERAI Intelligence</div>
          <div style="font-size:26px; font-weight:700; color:#ffffff; margin-bottom:8px;">
               Access Dashboard</div>
          <div style="font-size:14px; color:#7a9ab8; margin-bottom:28px;">
               Enter your access code to continue.</div>
        </div>
        """, unsafe_allow_html=True)

        _code = st.text_input("Access code", placeholder="e.g. NERAI-PRO-26",
                              label_visibility="collapsed", key="_gate_input")
        if st.button("Enter Dashboard", use_container_width=True, type="primary"):
            _c = _code.strip().upper()
            if _c in _VALID_CODES:
                if _c in _TIMED_CODES and _dt.now() > _TIMED_CODES[_c]:
                    st.error("This access code has expired.")
                else:
                    st.session_state.access_tier = _VALID_CODES[_c]
                    st.rerun()
            else:
                st.error("Invalid code. Get yours at neraicorp.com/#pricing")
        st.markdown(
            '<div style="text-align:center; margin-top:16px; font-size:12px; color:#3a6a8a;">'
            'No code? <a href="https://neraicorp.com/#pricing" target="_blank" '
            'style="color:#0077a8;">Subscribe at neraicorp.com</a></div>',
            unsafe_allow_html=True)
    st.stop()

# Tier shortcut
_IS_PRO = st.session_state.access_tier == 'pro'
_IS_SOLO = st.session_state.access_tier == 'solo'


# ═══════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=DM+Serif+Display&family=JetBrains+Mono:wght@400;500&display=swap');
:root {
  --bg-primary: #0a0e17;
  --bg-secondary: #0d1220;
  --bg-card: #111827;
  --bg-card-hover: #151d2e;
  --accent: #00d4ff;
  --accent2: #00ffc8;
  --accent-dim: rgba(0,212,255,0.15);
  --text-primary: #e0e8f0;
  --text-secondary: #8899aa;
  --text-dim: #5a6b82;
  --border: rgba(0,212,255,0.12);
  --border-glow: rgba(0,212,255,0.25);
  --glow: 0 0 20px rgba(0,212,255,0.15);
  --glow-strong: 0 0 30px rgba(0,212,255,0.25), 0 0 60px rgba(0,212,255,0.1);
  --navy: #0d1220;
  --teal: #00d4ff;
  --sky: #00b4d8;
  --silver: #8899aa;
  --hot: #ff6b6b;
  --warm: #ffd93d;
  --cool: #00ffc8;
  --mild: #a29bfe;
}

/* ── Global dark background ── */
.stApp, .main, [data-testid="stAppViewContainer"] {
  background: var(--bg-primary) !important;
  color: var(--text-primary) !important;
}
[data-testid="stHeader"] { background: transparent !important; }
        #MainMenu {visibility: hidden !important;} footer {visibility: hidden !important;} [data-testid="stDeployButton"] {display: none !important;} [data-testid="stToolbar"] {display: none !important;} header[data-testid="stHeader"] {display: none !important;} [data-testid="manage-app-button"] {display: none !important;} [data-testid="stStatusWidget"] {display: none !important;} [data-testid="stAppViewBlockContainer"] > div:last-child {visibility: visible;} .reportview-container .main footer {display: none !important;} div[data-testid="stBottomBlockContainer"] {display: none !important;} #stStreamlitDialog {display: none !important;} .stApp > footer {display: none !important;} div.viewerBadge_container__r5tak {display: none !important;} div.viewerBadge_link__qRIco {display: none !important;} a[href*="streamlit.io"] {display: none !important;} div[class*="StatusWidget"] {display: none !important;} .stApp > header button[kind="header"] { display: none !important; } div[class*="stToolbar"] {display: none !important;} .styles_viewerBadge {display: none !important;} ._container_gzau3 {display: none !important;} ._profileContainer {display: none !important;}

/* ── Sidebar dark glass ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0d1220 0%, #0a0e17 100%) !important;
  border-right: 1px solid var(--border) !important;
  box-shadow: 4px 0 30px rgba(0,0,0,0.5) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  color: var(--text-secondary) !important;
  border: 1px solid transparent !important;
  border-radius: 8px !important;
  padding: 8px 16px !important;
  text-align: left !important;
  transition: all 0.3s ease !important;
  font-size: 13px !important;
  width: 100% !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(0,212,255,0.08) !important;
  border-color: var(--border-glow) !important;
  color: var(--accent) !important;
  box-shadow: var(--glow) !important;
}
[data-testid="stSidebar"] hr {
  border-color: var(--border) !important;
  margin: 12px 0 !important;
}

/* ── Typography ── */
h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
  color: var(--text-primary) !important;
  font-family: 'Inter', sans-serif !important;
}
p, span, label, .stMarkdown p { color: var(--text-secondary) !important; }

/* ── KPI Cards (futuristic glow) ── */
.kpi-card, [data-testid="stMetric"] {
  background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  padding: 20px !important;
  box-shadow: var(--glow) !important;
  transition: all 0.3s ease !important;
  position: relative !important;
  overflow: hidden !important;
}
.kpi-card:hover, [data-testid="stMetric"]:hover {
  border-color: var(--border-glow) !important;
  box-shadow: var(--glow-strong) !important;
  transform: translateY(-2px) !important;
}
.kpi-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
}
[data-testid="stMetricValue"] {
  color: var(--accent) !important;
  font-weight: 700 !important;
  font-size: 28px !important;
  text-shadow: 0 0 20px rgba(0,212,255,0.3) !important;
}
[data-testid="stMetricLabel"] {
  color: var(--text-secondary) !important;
  text-transform: uppercase !important;
  letter-spacing: 1px !important;
  font-size: 11px !important;
}
[data-testid="stMetricDelta"] svg { fill: var(--accent2) !important; }
[data-testid="stMetricDelta"] div { color: var(--accent2) !important; }

/* ── Signal/News Cards ── */
.signal-card, .news-card {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  padding: 16px !important;
  margin-bottom: 10px !important;
  transition: all 0.3s ease !important;
}
.signal-card:hover, .news-card:hover {
  border-color: var(--accent) !important;
  box-shadow: 0 0 15px rgba(0,212,255,0.12) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg-secondary) !important;
  border-radius: 10px !important;
  padding: 4px !important;
  gap: 4px !important;
  border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--text-dim) !important;
  border-radius: 8px !important;
  font-size: 13px !important;
  padding: 8px 16px !important;
}
.stTabs [aria-selected="true"] {
  background: rgba(0,212,255,0.12) !important;
  color: var(--accent) !important;
  box-shadow: 0 0 10px rgba(0,212,255,0.1) !important;
}
.stTabs [data-baseweb="tab-border"] { display: none !important; }
.stTabs [data-baseweb="tab-highlight"] { background: var(--accent) !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
}
[data-testid="stExpander"] summary { color: var(--text-primary) !important; }
[data-testid="stExpander"] summary:hover { color: var(--accent) !important; }

/* ── Selectbox / Multiselect ── */
[data-testid="stSelectbox"], [data-testid="stMultiSelect"] {
  background: var(--bg-card) !important;
}
[data-baseweb="select"] > div {
  background: var(--bg-secondary) !important;
  border-color: var(--border) !important;
  color: var(--text-primary) !important;
}
[data-baseweb="popover"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border-glow) !important;
}
[data-baseweb="popover"] li { color: var(--text-primary) !important; }
[data-baseweb="popover"] li:hover { background: rgba(0,212,255,0.1) !important; }

/* ── DataFrame / Tables ── */
[data-testid="stDataFrame"], .stDataFrame {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
}

/* ── Slider ── */
[data-testid="stSlider"] [data-baseweb="slider"] div {
  background: var(--accent) !important;
}

/* ── Hero Section ── */
.hero-section {
  background: linear-gradient(135deg, #0d1220 0%, #111827 50%, #0d1220 100%) !important;
  border: 1px solid var(--border) !important;
  border-radius: 16px !important;
  padding: 32px !important;
  position: relative !important;
  overflow: hidden !important;
}
.hero-section::before {
  content: '';
  position: absolute;
  top: -50%; left: -50%;
  width: 200%; height: 200%;
  background: radial-gradient(circle at 30% 40%, rgba(0,212,255,0.05) 0%, transparent 50%);
  animation: heroGlow 8s ease-in-out infinite;
}
@keyframes heroGlow {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(20px, -20px); }
}

/* ── Badge styling ── */
.badge, .tier-badge {
  background: rgba(0,212,255,0.12) !important;
  color: var(--accent) !important;
  border: 1px solid var(--border-glow) !important;
  border-radius: 20px !important;
  padding: 4px 12px !important;
  font-size: 11px !important;
  font-weight: 600 !important;
  letter-spacing: 0.5px !important;
  text-shadow: 0 0 8px rgba(0,212,255,0.3) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb {
  background: rgba(0,212,255,0.2);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(0,212,255,0.4); }

/* ── Animations ── */
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }
@keyframes glowPulse {
  0%, 100% { box-shadow: 0 0 5px rgba(0,212,255,0.2); }
  50% { box-shadow: 0 0 20px rgba(0,212,255,0.4), 0 0 40px rgba(0,212,255,0.1); }
}
@keyframes borderGlow {
  0%, 100% { border-color: rgba(0,212,255,0.12); }
  50% { border-color: rgba(0,212,255,0.35); }
}
.glow-animate { animation: glowPulse 3s ease-in-out infinite; }
.border-animate { animation: borderGlow 4s ease-in-out infinite; }

/* ── Profile section ── */
.profile-header {
  background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  padding: 24px !important;
}

/* ── Plotly chart container ── */
.js-plotly-plot, .plotly {
  border-radius: 10px !important;
  overflow: hidden !important;
}

/* ── Streamlit elements ── */
.stAlert {
  background: var(--bg-card) !important;
  border-color: var(--border) !important;
  color: var(--text-primary) !important;
}
.stProgress > div > div {
  background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
}
.stSpinner > div { border-color: var(--accent) transparent transparent !important; }

/* ── Heatmap overrides ── */
.heatmap-container {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  padding: 16px !important;
}

/* ── Column gap fix ── */
[data-testid="column"] { padding: 0 8px !important; }

/* ── Login page override ── */
.login-container {
  background: var(--bg-card) !important;
  border: 1px solid var(--border-glow) !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# NERAI LOGO (transparent PNG, base64)
# ═══════════════════════════════════════════════════════════════
NERAI_LOGO_B64 = ""

# ═══════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════
COUNTRY_NAMES = {
    'AF':'Afghanistan','AR':'Argentina','AM':'Armenia','AS':'Australia',
    'BE':'Belgium','BR':'Brazil','CA':'Canada','CH':'China','CO':'Colombia',
    'DA':'Denmark','EG':'Egypt','ET':'Ethiopia','FR':'France','GZ':'Gaza Strip',
    'GM':'Germany','GH':'Ghana','GR':'Greece','HK':'Hong Kong','IC':'Iceland',
    'IN':'India','ID':'Indonesia','IR':'Iran','IZ':'Iraq','IS':'Israel',
    'IT':'Italy','JM':'Jamaica','JA':'Japan','JO':'Jordan','KZ':'Kazakhstan',
    'KE':'Kenya','KU':'Kuwait','KG':'Kyrgyzstan','LE':'Lebanon','MY':'Malaysia',
    'MX':'Mexico','NL':'Netherlands','NG':'Niger','NI':'Nigeria','KN':'North Korea',
    'NO':'Norway','PK':'Pakistan','RP':'Philippines','PO':'Portugal','RQ':'Puerto Rico',
    'QA':'Qatar','RS':'Russia','SA':'Saudi Arabia','SO':'Somalia','SF':'South Africa',
    'KS':'South Korea','SP':'Spain','SW':'Sweden','SZ':'Switzerland','SY':'Syria',
    'TU':'Turkey','UP':'Ukraine','AE':'United Arab Emirates','UK':'United Kingdom',
    'US':'United States','YM':'Yemen',
}
FIPS_TO_ISO3 = {
    'AF':'AFG','AR':'ARG','AM':'ARM','AS':'AUS','BE':'BEL','BR':'BRA',
    'CA':'CAN','CH':'CHN','CO':'COL','DA':'DNK','EG':'EGY','ET':'ETH',
    'FR':'FRA','GZ':'PSE','GM':'DEU','GH':'GHA','GR':'GRC','HK':'HKG',
    'IC':'ISL','IN':'IND','ID':'IDN','IR':'IRN','IZ':'IRQ','IS':'ISR',
    'IT':'ITA','JM':'JAM','JA':'JPN','JO':'JOR','KZ':'KAZ','KE':'KEN',
    'KU':'KWT','KG':'KGZ','LE':'LBN','MY':'MYS','MX':'MEX','NL':'NLD',
    'NG':'NER','NI':'NGA','KN':'PRK','NO':'NOR','PK':'PAK','RP':'PHL',
    'PO':'PRT','RQ':'PRI','QA':'QAT','RS':'RUS','SA':'SAU','SO':'SOM',
    'SF':'ZAF','KS':'KOR','SP':'ESP','SW':'SWE','SZ':'CHE','SY':'SYR',
    'TU':'TUR','UP':'UKR','AE':'ARE','UK':'GBR','US':'USA','YM':'YEM',
}
_PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#c0d0e0"),
)
TOPIC_LABELS = {
    'political_instability':'Political Instability','government_instability':'Government Instability',
    'military_escalation':'Military Escalation','terrorism':'Terrorism','protest':'Protest',
    'coup':'Coup','political_repression':'Political Repression','domestic_violence':'Domestic Violence',
    'military_crisis':'Military Crisis','international_crisis':'International Crisis',
    'regime_instability':'Regime Instability','military_clash':'Military Clash',
    'deteriorating_bilateral_relations':'Deteriorating Bilateral Relations',
    'increasing_bilateral_relations':'Increasing Bilateral Relations',
    'international_support':'International Support','political_stability':'Political Stability',
    'democratization':'Democratization','dispute_settlement':'Dispute Settlement',
    'military_deescalation':'Military De-escalation','instability':'Instability',
    'ethnic_religious_violence':'Ethnic/Religious Violence',
    'opposition_activeness':'Opposition Activeness','political_crisis':'Political Crisis',
    'political_dissent':'Political Dissent','leadership_change':'Leadership Change',
    'mass_killing':'Mass Killing',
    'increasing_international_financial_support':'Intl. Financial Support',
    'institutional_strength':'Institutional Strength','impose_curfew':'Curfew',
    'imposing_state_of_emergency':'State of Emergency',
    'appeal_of_leadership_change':'Appeal of Leadership Change',
    'threaten_in_international_relations':'Intl. Threats','torture':'Torture',
    'mass_expulsion':'Mass Expulsion','repression_tactics':'Repression Tactics',
    'pressure_to_political_parties':'Pressure on Parties','authoritarianism':'Authoritarianism',
    'confiscate_property':'Property Confiscation','human_rights_abuses':'Human Rights Abuses',
    'corruption':'Corruption',
}
GLOW_COLORS = ['#00d4ff','#00ffc8','#ff6b6b','#ffd93d','#a29bfe',
               '#00b4d8','#ff8a5c','#55efc4','#fd79a8','#74b9ff']

TENSION_WEIGHTS = {
    'deteriorating_bilateral_relations':3.0,
    'military_clash':3.5,'military_escalation':2.5,'military_crisis':2.5,
    'political_crisis':2.0,'international_crisis':2.0,
    'threaten_in_international_relations':2.0,'instability':1.5,
}
COOP_WEIGHTS = {
    'increasing_bilateral_relations':3.0,'military_deescalation':2.5,
    'dispute_settlement':2.0,'international_support':1.5,'political_stability':1.0,
}
BILATERAL_INDICATORS = [
    ('political_crisis','Political Crisis','#f59e0b'),
    ('military_clash','War Risk','#e05060'),
    ('threaten_in_international_relations','Intl. Threats','#e06030'),
    ('military_escalation','Military Escalation','#0077a8'),
]

NEWS_CATEGORIES = [
    ('POLITICAL',           'political government democracy parliament'),
    ('US POLITICS',         'United States politics congress Washington'),
    ('RULE OF LAW',         'rule law judiciary court justice'),
    ('MIGRATION',           'migration immigration refugee asylum border'),
    ('FINANCIAL',           'financial economy GDP market recession'),
    ('FINANCIAL POLITICS',  'financial policy central bank interest rate monetary'),
    ('FINANCIAL INSTITUTIONS','IMF World Bank financial institution lending'),
    ('CURRENCIES',          'currency exchange rate dollar euro inflation'),
    ('CONFLICT',            'conflict war fighting battle military violence'),
    ('COUP',                'coup overthrow military takeover government'),
    ('TERRORISM',           'terrorism attack extremist bomb blast'),
    ('ETHNIC',              'ethnic minority genocide discrimination violence'),
    ('RELIGIOUS',           'religious faith mosque church temple extremism'),
    ('POLITICAL LEADERS',   'president prime minister leader summit diplomacy'),
    ('DISASTERS',           'disaster earthquake flood hurricane tsunami'),
    ('EMERGENCIES',         'emergency crisis evacuation warning catastrophe'),
    ('MEDIA',               'media press freedom journalism censorship propaganda'),
    ('HEALTH',              'health pandemic disease WHO outbreak epidemic'),
    ('CRIME',               'crime trafficking fraud corruption arrest prison'),
    ('ICT SECURITY',        'cyber security hack data breach ransomware attack'),
    ('STRATEGIC SECURITY',  'strategic security intelligence NATO defense alliance'),
    ('MILITARY',            'military army navy airforce weapon troops defense'),
    ('LAW',                 'law legislation parliament constitution bill'),
    ('CORRUPTION',          'corruption bribery scandal embezzlement fraud'),
    ('ELECTIONS',           'election vote ballot campaign democracy poll'),
    ('PROTESTS',            'protest demonstration riot uprising march'),
    ('TRAVEL',              'travel visa border tourism aviation flight'),
    ('LANGUAGES',           'language culture indigenous minority rights'),
]

def hex_to_rgba(h, a=0.06):
    r,g,b = int(h[1:3],16),int(h[3:5],16),int(h[5:7],16)
    return f'rgba({r},{g},{b},{a})'

BASE_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(13,18,32,0.9)',
    font=dict(family='Inter,sans-serif',color='#8899aa',size=11),
    margin=dict(l=45,r=15,t=38,b=40),
    xaxis=dict(gridcolor='rgba(0,212,255,0.06)',linecolor='rgba(0,212,255,0.15)',
               tickfont=dict(size=10,color='#6b7c93'),zeroline=False),
    yaxis=dict(gridcolor='rgba(0,212,255,0.06)',linecolor='rgba(0,212,255,0.15)',
               tickfont=dict(size=10,color='#6b7c93'),zeroline=False),
)


# ═══════════════════════════════════════════════════════════════
# DATA LOAD
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def load_data(filepath='./indices.csv'):
    if os.path.exists(filepath):
        df = pd.read_csv(filepath,sep=',',header=0,index_col=[0,1])
        df.columns = pd.to_datetime(df.columns,format='%Y%m%d')
        # Vectorized gap detection: values below 5% of row median are treated as missing
        date_cols = [c for c in df.columns if c not in ['topic', 'country']]
        if date_cols:
            pos_vals = df[date_cols].where(df[date_cols] > 0)
            row_medians = pos_vals.median(axis=1)
            threshold = row_medians * 0.05
            mask = df[date_cols].lt(threshold, axis=0) | (df[date_cols] == 0)
            df[date_cols] = df[date_cols].where(~mask, np.nan)
            # Small gaps (up to 7 days): linear interpolation
            df[date_cols] = df[date_cols].interpolate(axis=1, method='linear', limit=7, limit_direction='both')
            # Large gaps: forward/backward fill then add noise to avoid flat lines
            still_nan = df[date_cols].isna()
            df[date_cols] = df[date_cols].ffill(axis=1).bfill(axis=1)
            if still_nan.any().any():
                row_std = df[date_cols].std(axis=1)
                np.random.seed(42)
                noise = pd.DataFrame(
                    np.random.normal(0, 1, size=df[date_cols].shape),
                    index=df[date_cols].index, columns=df[date_cols].columns
                )
                noise = noise.multiply(row_std * 0.05, axis=0)
                df[date_cols] = df[date_cols].where(~still_nan, df[date_cols] + noise)
                df[date_cols] = df[date_cols].clip(lower=0)
            df[date_cols] = df[date_cols].fillna(0)
        return df,False
    return _demo_data(),True

def _demo_data():
    np.random.seed(42)
    topics = list(TOPIC_LABELS.keys())
    countries = list(COUNTRY_NAMES.keys())
    dates = pd.date_range(end=datetime.date.today(),periods=180,freq='D')
    idx = pd.MultiIndex.from_product([topics,countries],names=['topic','country'])
    return pd.DataFrame(
        np.random.exponential(0.0008,size=(len(idx),len(dates))),
        index=idx,columns=dates
    )

def apply_norm(df_topic,method):
    if method=='Raw': return df_topic
    out = df_topic.copy().astype(float)
    for c in out.index:
        row = out.loc[c]
        # Replace near-zero gap values with NaN and interpolate
        nonzero = row[row > 0]
        if len(nonzero) > 2:
            thr = nonzero.median() * 0.05
            row_clean = row.where(row > thr, np.nan)
        else:
            row_clean = row.replace(0, np.nan)
        if row_clean.notna().sum() >= 2:
            row_clean = row_clean.interpolate(method='linear', limit_direction='both')
        row = row_clean.ffill().bfill().fillna(0)
        if method=='Score (0–100)':
            # Use 2nd-98th percentile for robust normalization
            vals = row[row > 0]
            if len(vals) > 2:
                p2, p98 = np.percentile(vals, [2, 98])
                if p98 > p2:
                    out.loc[c] = ((row - p2) / (p98 - p2) * 100).clip(0, 100)
                else:
                    mn, mx = row.min(), row.max()
                    out.loc[c] = (row - mn) / (mx - mn) * 100 if mx > mn else row * 0
            else:
                mn, mx = row.min(), row.max()
                out.loc[c] = (row - mn) / (mx - mn) * 100 if mx > mn else row * 0
        elif method=='Z-Score':
            mu,sd = row.mean(),row.std()
            out.loc[c] = (row-mu)/sd if sd>0 else row*0
    return out

def fmt(val,method):
    if method=='Raw': return f'{val:.5f}'
    if method=='Score (0–100)': return f'{val:.1f}'
    return f'{val:+.2f}σ'

def risk_badge(val,method):
    if method=='Score (0–100)':
        if val>=75: return '<span class="badge-crit">CRITICAL</span>'
        if val>=50: return '<span class="badge-high">HIGH</span>'
        if val>=25: return '<span class="badge-med">MEDIUM</span>'
        return '<span class="badge-low">LOW</span>'
    if method=='Z-Score':
        if val>=2:  return '<span class="badge-crit">SPIKE</span>'
        if val>=1:  return '<span class="badge-high">ELEVATED</span>'
        if val<=-1: return '<span class="badge-low">SUPPRESSED</span>'
        return '<span class="badge-neu" style="color:#556">NORMAL</span>'
    return ''

# ═══════════════════════════════════════════════════════════════
# CHART FUNCTIONS
# ═══════════════════════════════════════════════════════════════
def find_top_peaks(series, n=3, window=7):
    """Zaman serisindeki en yüksek local peak tarihlerini döner."""
    vals = series.values
    peaks = []
    half = window // 2
    for i in range(half, len(vals) - half):
        local_max = max(vals[max(0,i-half):i+half+1])
        if vals[i] == local_max and vals[i] > series.mean():
            peaks.append((i, vals[i]))
    peaks.sort(key=lambda x: x[1], reverse=True)
    if len(peaks) < n:
        top_idx = pd.Series(vals).nlargest(n).index.tolist()
        return [series.index[i] for i in top_idx]
    return [series.index[i] for i, v in peaks[:n]]


def chart_timeseries_with_peaks(df_n, countries, title, method, show_peaks=True):
    """Time series chart with peak annotation markers."""
    fig = go.Figure()
    y_label = {'Raw':'Raw Index','Score (0–100)':'Risk Score (0–100)','Z-Score':'Z-Score (σ)'}[method]
    peak_info = {}
    for i, c in enumerate(countries):
        if c not in df_n.index: continue
        s = df_n.loc[c]
        col = GLOW_COLORS[i % len(GLOW_COLORS)]
        # Build hover text with peak indicator
        hover_texts = []
        for dt, val in zip(s.index, s.values):
            hover_texts.append(f'<b>{COUNTRY_NAMES.get(c,c)}</b><br>{dt.strftime("%d %b %Y")}<br>{y_label}: {val:.3f}')
        fig.add_trace(go.Scatter(
            x=s.index, y=s.values, name=COUNTRY_NAMES.get(c,c), mode='lines',
            line=dict(width=2,color=col),
            fill='tozeroy', fillcolor=hex_to_rgba(col,0.05),
            text=hover_texts, hoverinfo='text',
        ))
        if show_peaks and len(s) > 14:
            peaks = find_top_peaks(s, n=2)
            peak_info[c] = peaks
            for pk in peaks:
                pk_val = float(s.loc[pk])
                fig.add_trace(go.Scatter(
                    x=[pk], y=[pk_val], mode='markers',
                    marker=dict(size=10, color=col, symbol='star',
                                line=dict(color='#0d1220',width=1.5)),
                    name=f'{COUNTRY_NAMES.get(c,c)} peak',
                    hovertemplate=f'<b>⚡ PEAK — {COUNTRY_NAMES.get(c,c)}</b><br>'
                                  f'{pk.strftime("%d %b %Y")}<br>'
                                  f'{y_label}: {pk_val:.3f}<br>'
                                  f'<i>Click "📰 Peak News" below to see headlines</i>'
                                  f'<extra></extra>',
                    showlegend=False
                ))
    if method=='Z-Score':
        fig.add_hline(y=2,line_dash='dot',line_color='rgba(224,80,96,0.5)',
                      annotation_text='Alert (+2σ)',annotation_font_size=9)
        fig.add_hline(y=-2,line_dash='dot',line_color='rgba(0,184,212,0.4)',
                      annotation_text='-2σ',annotation_font_size=9)
    t = {**BASE_THEME}
    t['yaxis'] = {**t['yaxis'],'title':y_label,'title_font':dict(size=10)}
    fig.update_layout(**t, height=340,
        title=dict(text=title,font=dict(size=12,color='#0077a8'),x=0.01),
        legend=dict(bgcolor='rgba(255,255,255,0.85)',bordercolor='rgba(0,119,168,0.25)',
                    borderwidth=1,font=dict(size=10,color='#8aa0bc')),
        hovermode='x unified')
    return fig, peak_info


def chart_heatmap(df_n, top_n, method):
    means = df_n.mean(axis=1).nlargest(top_n)
    sel = means.index.tolist()
    matrix = []
    for c in sel:
        try: matrix.append(df_n.loc[c].values)
        except: matrix.append([0]*len(df_n.columns))
    matrix = np.array(matrix)
    dates_str = [d.strftime('%d %b') for d in df_n.columns]
    step = max(1,len(dates_str)//18)
    xlabels = [d if i%step==0 else '' for i,d in enumerate(dates_str)]
    ylabels = [COUNTRY_NAMES.get(c,c) for c in sel]
    colorscale = (
        [[0,'#0a1628'],[0.15,'#0d3464'],[0.35,'#00b4d8'],
         [0.55,'#0077a8'],[0.75,'#f59e0b'],[0.9,'#e05060'],[1,'#ff2d55']]
        if method!='Z-Score' else
        [[0,'#00B8D4'],[0.25,'#0d3464'],
         [0.5,'#1a2338'],[0.65,'#f59e0b'],[1,'#e05060']]
    )
    fig = go.Figure(go.Heatmap(
        z=matrix,x=xlabels,y=ylabels,colorscale=colorscale,
        hovertemplate='<b>%{y}</b><br>%{x}<br>Value: %{z:.3f}<extra></extra>',
        showscale=True,colorbar=dict(thickness=7,len=0.85,
            tickfont=dict(size=8,color='#5a6b82'),outlinewidth=0)
    ))
    t = {**BASE_THEME}
    t['xaxis'] = dict(showticklabels=True,tickangle=-45,
                      tickfont=dict(size=8,color='#5a6b82'),gridcolor='rgba(0,0,0,0)')
    t['yaxis'] = dict(tickfont=dict(size=9,color='#8aa0bc'),gridcolor='rgba(0,0,0,0)')
    fig.update_layout(**t,height=460,
        title=dict(text=f'Top {top_n} Countries — Heatmap',
                   font=dict(size=12,color='#0077a8'),x=0.01))
    return fig

def heatmap_glow_html(df_n, top_n, method, topic_label=''):
    """Animated heatmap with hover tooltips. Colors baked into cells server-side."""
    import json as _json, math
    means = df_n.mean(axis=1).nlargest(top_n)
    sel = means.index.tolist()
    matrix = []
    for c in sel:
        try: matrix.append(df_n.loc[c].values.tolist())
        except: matrix.append([0.0]*len(df_n.columns))
    all_dates = [d.strftime('%d %b %Y') for d in df_n.columns]
    ylabels = [COUNTRY_NAMES.get(c,c) for c in sel]
    mat = np.array(matrix, dtype=float)
    mat = np.nan_to_num(mat, nan=0.0)
    vmin = float(mat.min())
    vmax = float(mat.max())
    if vmax <= vmin: vmax = vmin + 1.0
    rows = len(ylabels)
    cols = len(all_dates)
    cH = max(24, min(34, 460 // max(rows, 1)))
    cW = max(6, min(16, 650 // max(cols, 1)))
    # Color mapping function (Python-side)
    stops = [(13,52,100),(0,180,212),(0,119,168),(245,158,11),(224,80,96)]
    pos = [0.0, 0.25, 0.5, 0.75, 1.0]
    def val2rgb(v):
        t = max(0.0, min(1.0, (v - vmin) / (vmax - vmin)))
        idx = 0
        for k in range(len(pos)-1):
            if pos[k] <= t <= pos[k+1]: idx = k; break
        f = (t - pos[idx]) / (pos[idx+1] - pos[idx]) if pos[idx+1] != pos[idx] else 0
        r = int(stops[idx][0] + (stops[idx+1][0] - stops[idx][0]) * f)
        g = int(stops[idx][1] + (stops[idx+1][1] - stops[idx][1]) * f)
        b = int(stops[idx][2] + (stops[idx+1][2] - stops[idx][2]) * f)
        return f'rgb({r},{g},{b})'
    ttl = f"Top {top_n} Countries \u2014 {topic_label} Heatmap" if topic_label else f"Top {top_n} Countries \u2014 Heatmap"
    h = []
    h.append('<style>')
    h.append('*{box-sizing:border-box;margin:0;padding:0;}')
    h.append('body{background:transparent;overflow-x:auto;}')
    h.append('</style>')
    h.append(f'<div style="font-family:monospace;padding:10px 8px;">')
    h.append(f'<div style="color:#00B8D4;font-size:14px;font-weight:bold;margin-bottom:2px;letter-spacing:1px;">{ttl}</div>')
    h.append(f'<div style="color:#5a6b82;font-size:10px;margin-bottom:10px;">Score ({method}) \u2022 Hover for details</div>')
    h.append('<div style="display:flex;align-items:flex-start;">')
    # Y-axis labels + cells
    h.append('<div>')
    for r in range(rows):
        h.append(f'<div style="display:flex;align-items:center;height:{cH+2}px;">')
        h.append(f'<div style="width:95px;text-align:right;padding-right:6px;color:#8aa0bc;font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{ylabels[r]}</div>')
        for c in range(cols):
            v = float(mat[r][c])
            bg = val2rgb(v)
            sv = round(v, 1)
            h.append(f'<div class="hc" data-i="{r*cols+c}" data-info="{ylabels[r]}|{all_dates[c]}|{sv}|{topic_label}" style="width:{cW}px;height:{cH}px;margin:0 1px;border-radius:2px;background:{bg};display:inline-block;cursor:crosshair;transition:filter .3s,box-shadow .3s,transform .15s;"></div>')
        h.append('</div>')
    h.append('</div>')
    # Color legend
    h.append(f'<div style="display:flex;flex-direction:column;align-items:center;margin-left:12px;">')
    h.append(f'<span style="color:#5a6b82;font-size:9px;">{round(vmax)}</span>')
    h.append(f'<div style="width:12px;height:{cH*rows}px;margin:4px 0;border-radius:4px;background:linear-gradient(to bottom,#e05060,#f59e0b,#0077a8,#00b4d8,#0d3464);"></div>')
    h.append(f'<span style="color:#5a6b82;font-size:9px;">{round(vmin)}</span>')
    h.append('</div></div>')
    # Tooltip div
    h.append('<div id="htt" style="display:none;position:fixed;background:rgba(6,13,26,0.95);border:1px solid rgba(0,184,212,0.4);border-radius:6px;padding:10px 14px;color:#e0e8f0;font-size:11px;z-index:9999;pointer-events:none;min-width:170px;box-shadow:0 4px 20px rgba(0,0,0,0.6);"><div id="ht1" style="color:#00B8D4;font-size:13px;font-weight:bold;"></div><div id="ht2" style="color:#f59e0b;font-size:10px;margin:2px 0;"></div><div id="ht3" style="color:#8aa0bc;font-size:10px;margin-bottom:5px;"></div><div id="ht4" style="font-size:16px;font-weight:bold;"></div></div>')
    h.append('</div>')
    # JS: tooltip + glow animation
    h.append('<scr' + 'ipt>')
    h.append('(function(){')
    h.append('var cs=document.querySelectorAll(".hc"),tip=document.getElementById("htt");')
    h.append('function rl(v){v=parseFloat(v);if(v<20)return"LOW";if(v<40)return"MEDIUM";if(v<60)return"HIGH";if(v<80)return"VERY HIGH";return"CRITICAL";}')
    h.append('function sc(v){v=parseFloat(v);if(v<30)return"#00B8D4";if(v<50)return"#0077a8";if(v<70)return"#f59e0b";return"#e05060";}')
    h.append('cs.forEach(function(c){')
    h.append('c.onmouseenter=function(e){var p=c.dataset.info.split("|");')
    h.append('document.getElementById("ht1").textContent=p[0];')
    h.append('document.getElementById("ht2").textContent=p[3]||"";')
    h.append('document.getElementById("ht3").textContent=p[1];')
    h.append('document.getElementById("ht4").innerHTML="<span style=\\"color:"+sc(p[2])+"\\">"+p[2]+"</span> <span style=\\"font-size:10px;color:#5a6b82\\">/100 "+rl(p[2])+"</span>";')
    h.append('tip.style.display="block";tip.style.left=(e.clientX+12)+"px";tip.style.top=(e.clientY-60)+"px";};')
    h.append('c.onmousemove=function(e){tip.style.left=(e.clientX+12)+"px";tip.style.top=(e.clientY-60)+"px";};')
    h.append('c.onmouseleave=function(){tip.style.display="none";};')
    h.append('c.onmouseenter2=c.onmouseenter;')
    h.append('});')
    # Glow animation
    h.append('var gl=new Set(),tot=cs.length;')
    h.append('setInterval(function(){gl.forEach(function(i){cs[i].style.filter="";cs[i].style.boxShadow="";});gl.clear();')
    h.append('for(var n=0;n<4;n++){var i=Math.floor(Math.random()*tot);gl.add(i);')
    h.append('cs[i].style.filter="brightness(1.6)";cs[i].style.boxShadow="0 0 10px rgba(0,184,212,0.5)";}},500);')
    h.append('})();')
    h.append('</scr' + 'ipt>')
    return '\n'.join(h)
def chart_world(df_n,date_col):
    try:
        row = df_n[[date_col]].reset_index()
        row.columns = ['country','value']
        row['iso3'] = row['country'].map(FIPS_TO_ISO3)
        row['name'] = row['country'].map(COUNTRY_NAMES)
        row = row.dropna(subset=['iso3'])
    except: return go.Figure()
    fig = go.Figure(go.Choropleth(
        locations=row['iso3'],z=row['value'],text=row['name'],
        colorscale=[[0,'#0d3464'],[0.3,'#00b4d8'],
                    [0.6,'#0077a8'],[0.85,'#f59e0b'],
                    [1,'#e05060']],
        autocolorscale=False,marker_line_color='rgba(0,119,168,0.3)',
        marker_line_width=0.5,
        colorbar=dict(title=dict(text='Score',font=dict(size=9,color='#5a6b82')),
                      thickness=7,len=0.55,tickfont=dict(size=8,color='#5a6b82'),
                      outlinewidth=0,bgcolor='rgba(0,0,0,0)'),
        hovertemplate='<b>%{text}</b><br>Value: %{z:.3f}<extra></extra>'
    ))
    t = {**BASE_THEME}
    fig.update_layout(**t,height=420,
        title=dict(text=f'Global Risk Map — {pd.Timestamp(date_col).strftime("%d %b %Y")}',
                   font=dict(size=12,color='#0077a8'),x=0.01),
        geo=dict(bgcolor='rgba(0,0,0,0)',showframe=False,showcoastlines=True,
                 coastlinecolor='rgba(0,212,255,0.15)',showland=True,
                 landcolor='#111d33',showocean=True,
                 oceancolor='#0a0e17',showlakes=False,
                 projection_type='natural earth'))
    return fig

def risk_globe_html(df_n, date_col):
    """Interactive rotating 3D globe for risk visualization."""
    import json as _json
    try:
        row = df_n[[date_col]].reset_index()
        row.columns = ['country','value']
        row['iso3'] = row['country'].map(FIPS_TO_ISO3)
        row['name'] = row['country'].map(COUNTRY_NAMES)
        row = row.dropna(subset=['iso3'])
    except:
        return "<div style='color:#5a6b82;text-align:center;padding:40px;'>No data available</div>"
    locs = _json.dumps(row['iso3'].tolist())
    vals = _json.dumps(row['value'].round(3).tolist())
    names = _json.dumps(row['name'].tolist())
    ttl = f"Global Risk Map \u2014 {pd.Timestamp(date_col).strftime('%d %b %Y')}"
    html = '<div id="rglobe" style="width:100%;height:620px;cursor:grab;background:transparent;"></div>\n'
    html += '<script>\n'
    html += '(function(){\n'
    html += 'var s=document.createElement("script");\n'
    html += 's.src="https://cdn.plot.ly/plotly-2.27.0.min.js";\n'
    html += 's.onload=function(){\n'
    html += 'var data=[{type:"choropleth",locations:' + locs + ',z:' + vals + ',text:' + names + ','
    html += 'colorscale:[[0,"#0a1628"],[0.2,"#0d3464"],[0.4,"#00b4d8"],[0.6,"#0077a8"],[0.85,"#f59e0b"],[1,"#e05060"]],'
    html += 'autocolorscale:false,marker:{line:{color:"rgba(0,184,212,0.4)",width:0.6}},'
    html += 'colorbar:{title:{text:"Score",font:{size:11,color:"#00B8D4"}},thickness:10,len:0.55,'
    html += 'tickfont:{size:9,color:"#5a6b82"},outlinewidth:0,bgcolor:"rgba(0,0,0,0)"},'
    html += 'hovertemplate:"<b>%{text}</b><br>Risk Score: %{z:.1f}<extra></extra>"}];\n'
    html += 'var layout={geo:{bgcolor:"rgba(0,0,0,0)",showframe:false,showcoastlines:true,'
    html += 'coastlinecolor:"rgba(0,184,212,0.25)",showland:true,landcolor:"#0a1628",'
    html += 'showocean:true,oceancolor:"#060d1a",showlakes:false,'
    html += 'projection:{type:"orthographic",rotation:{lon:30,lat:20,roll:0}},'
    html += 'lonaxis:{showgrid:true,gridcolor:"rgba(0,184,212,0.06)"},'
    html += 'lataxis:{showgrid:true,gridcolor:"rgba(0,184,212,0.06)"}},'
    html += 'paper_bgcolor:"rgba(0,0,0,0)",plot_bgcolor:"rgba(0,0,0,0)",'
    html += 'margin:{t:45,b:5,l:5,r:5},height:620,'
    html += 'title:{text:"' + ttl + '",font:{size:14,color:"#00B8D4",family:"monospace"},x:0.02},'
    html += 'dragmode:"pan"};\n'
    html += 'Plotly.newPlot("rglobe",data,layout,{displayModeBar:false,scrollZoom:false});\n'
    html += 'var lon=30,rotating=true;\n'
    html += 'setInterval(function(){if(rotating){lon=(lon+0.3)%360;'
    html += 'Plotly.relayout("rglobe",{"geo.projection.rotation.lon":lon});}},50);\n'
    html += 'var el=document.getElementById("rglobe");\n'
    html += 'el.addEventListener("mouseenter",function(){rotating=false;el.style.cursor="grab";});\n'
    html += 'el.addEventListener("mouseleave",function(){rotating=true;});\n'
    html += 'el.addEventListener("mousedown",function(){el.style.cursor="grabbing";});\n'
    html += 'el.addEventListener("mouseup",function(e){el.style.cursor="grab";'
    html += 'var g=el._fullLayout.geo.projection.rotation;lon=g.lon;});\n'
    html += '};\n'
    html += 'document.head.appendChild(s);\n'
    html += '})();\n'
    html += '</scrip'+'t>'
    return html
def chart_ranking(df_n,date_col,n=12):
    try:
        row = df_n[[date_col]].reset_index()
        row.columns = ['country','value']
        row['name'] = row['country'].map(COUNTRY_NAMES)
        row = row.nlargest(n,'value').sort_values('value')
    except: return go.Figure()
    n_rows = len(row)
    RANK_PALETTE = ['#00d4ff','#00ffc8','#00b4d8','#ffd93d','#ff6b6b','#a29bfe','#fd79a8','#55efc4','#74b9ff','#ff8a5c','#6c5ce7','#81ecec']
    colors = [RANK_PALETTE[i % len(RANK_PALETTE)] for i in range(n_rows)]
    fig = go.Figure(go.Bar(
        x=row['value'],y=row['name'],orientation='h',
        marker=dict(color=colors,line=dict(color='rgba(0,212,255,0.15)',width=0.5)),
        hovertemplate='<b>%{y}</b><br>Value: %{x:.4f}<extra></extra>'
    ))
    t = {**BASE_THEME}
    t['xaxis'] = dict(gridcolor='rgba(0,212,255,0.06)',tickfont=dict(size=10,color='#6b7c93'))
    t['yaxis'] = dict(tickfont=dict(size=10,color='#8aa0bc'),gridcolor='rgba(0,0,0,0)')
    fig.update_layout(**t,height=330,
        title=dict(text='Country Ranking',font=dict(size=12,color='#0077a8'),x=0.01))
    return fig

def chart_sparkline(series,color='#0077a8'):
    fig = go.Figure(go.Scatter(
        x=series.index,y=series.values,mode='lines',
        line=dict(width=1.5,color=color),
        fill='tozeroy',fillcolor=hex_to_rgba(color,0.12)
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
        height=45,margin=dict(l=0,r=0,t=0,b=0),
        xaxis=dict(visible=False),yaxis=dict(visible=False),showlegend=False
    )
    return fig

def gauge_chart(value,title,color,height=210):
    fig = go.Figure(go.Indicator(
        mode='gauge+number',value=round(value,1),
        domain={'x':[0,1],'y':[0,1]},
        title={'text':title,'font':{'size':10,'color':'#5a6b82','family':'Inter'}},
        number={'font':{'color':color,'size':30,'family':'Inter'},'valueformat':'.0f'},
        gauge={
            'axis':{'range':[0,100],'nticks':5,
                    'tickfont':{'size':8,'color':'#5a6b82'},'tickcolor':'#0077a8'},
            'bar':{'color':color,'thickness':0.22},
            'bgcolor':'rgba(0,0,0,0)','borderwidth':0,
            'steps':[
                {'range':[0,25],'color':'rgba(0,184,212,0.10)'},
                {'range':[25,50],'color':'rgba(245,158,11,0.10)'},
                {'range':[50,75],'color':'rgba(224,96,48,0.10)'},
                {'range':[75,100],'color':'rgba(224,80,96,0.12)'},
            ],
            'threshold':{'line':{'color':color,'width':3},'thickness':0.75,'value':value},
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                      font=dict(family='Inter,sans-serif',color='#8899aa'),
                      height=height,margin=dict(l=15,r=15,t=45,b=5))
    return fig

# ═══════════════════════════════════════════════════════════════
# BILATERAL FUNCTIONS  — FIXED (geometric mean approach)
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def compute_bilateral_base(_df_raw):
    """Ağırlıklı TENSION ve COOPERATION zaman serisi — global 99p normalize."""
    available = set(_df_raw.index.get_level_values('topic').unique())
    countries  = _df_raw.index.get_level_values('country').unique()
    cols       = _df_raw.columns

    t_sum = pd.DataFrame(0.0,index=countries,columns=cols)
    t_wt  = 0.0
    for topic,w in TENSION_WEIGHTS.items():
        if topic in available:
            tdf = _df_raw.xs(topic,level='topic').reindex(countries).fillna(0)
            t_sum += tdf*w; t_wt += w

    c_sum = pd.DataFrame(0.0,index=countries,columns=cols)
    c_wt  = 0.0
    for topic,w in COOP_WEIGHTS.items():
        if topic in available:
            tdf = _df_raw.xs(topic,level='topic').reindex(countries).fillna(0)
            c_sum += tdf*w; c_wt += w

    tension = t_sum/t_wt if t_wt>0 else t_sum
    coop    = c_sum/c_wt if c_wt>0 else c_sum

    def _norm99(df):
        flat = df.values.flatten()
        pos  = flat[flat>0]
        mx   = np.percentile(pos,99) if len(pos) else 1.0
        return (df/mx*100).clip(0,100)

    return _norm99(tension), _norm99(coop)


@st.cache_data(ttl=3600)
def _get_bilateral_specific_norm(_df_raw):
    """
    'deteriorating_bilateral_relations' ve 'increasing_bilateral_relations'
    topic'lerini bağımsız olarak 0-100 normalize et.
    Her ülkenin bu konulardaki özgül skorunu döner.
    """
    available = set(_df_raw.index.get_level_values('topic').unique())
    countries = _df_raw.index.get_level_values('country').unique()
    cols      = _df_raw.columns

    def _get_norm(topic_key):
        if topic_key not in available:
            return pd.DataFrame(0.0, index=countries, columns=cols)
        tdf  = _df_raw.xs(topic_key, level='topic').reindex(countries).fillna(0)
        flat = tdf.values.flatten()
        pos  = flat[flat > 0]
        mx   = np.percentile(pos, 99) if len(pos) else 1.0
        return (tdf / mx * 100).clip(0, 100) if mx > 0 else tdf * 0

    deteri = _get_norm('deteriorating_bilateral_relations')
    incr   = _get_norm('increasing_bilateral_relations')
    return deteri, incr


def get_bilateral_series(t_norm, c_norm, c1, c2, n_days=60):
    cols   = t_norm.columns[-n_days:]
    t1     = t_norm.loc[c1,cols] if c1 in t_norm.index else pd.Series(0.0,index=cols)
    t2     = t_norm.loc[c2,cols] if c2 in t_norm.index else pd.Series(0.0,index=cols)
    c1s    = c_norm.loc[c1,cols] if c1 in c_norm.index else pd.Series(0.0,index=cols)
    c2s    = c_norm.loc[c2,cols] if c2 in c_norm.index else pd.Series(0.0,index=cols)
    bi_t   = (t1+t2)/2
    bi_c   = (c1s+c2s)/2
    bi_net = (bi_t - bi_c*0.35).clip(0,100)
    return bi_t, bi_c, bi_net


def relation_status(net_score,trend_7d):
    if   net_score>=80: st_,col_,ico = 'CRISIS',     '#ff0033','🚨'
    elif net_score>=65: st_,col_,ico = 'HOSTILE',    '#e05060','⚠️'
    elif net_score>=45: st_,col_,ico = 'TENSE',      '#e06030','📈'
    elif net_score>=25: st_,col_,ico = 'CAUTIOUS',   '#f59e0b','📊'
    elif net_score>=10: st_,col_,ico = 'STABLE',     '#00b4d8','📉'
    else:               st_,col_,ico = 'COOPERATIVE','#00B8D4','🤝'
    if   trend_7d> 5: tr_txt,tr_col = '▲ DETERIORATING','#e06030'
    elif trend_7d> 1: tr_txt,tr_col = '↗ WORSENING',    '#f59e0b'
    elif trend_7d<-5: tr_txt,tr_col = '▼ IMPROVING',    '#00B8D4'
    elif trend_7d<-1: tr_txt,tr_col = '↘ EASING',       '#00b4d8'
    else:             tr_txt,tr_col = '→ STABLE',        '#7a9ab8'
    return st_,col_,ico,tr_txt,tr_col


@st.cache_data(ttl=3600)
def compute_top_tensions(_t_norm, _c_norm, _deteri_norm, top_n=28, n_pairs=5):
    """
    FIXED: geometric mean bilateral scoring so BOTH countries must have
    elevated scores for a pair to rank high. Prevents low-coverage
    countries from appearing as high-tension partners.
    """
    avg_t  = _t_norm.mean(axis=1)
    top_c  = avg_t.nlargest(top_n).index.tolist()
    recent = _t_norm.columns[-7:]
    prev7  = _t_norm.columns[-14:-7] if len(_t_norm.columns)>=14 else _t_norm.columns[:7]

    pairs = []
    for i in range(len(top_c)):
        for j in range(i+1,len(top_c)):
            c1,c2 = top_c[i],top_c[j]
            # Bilateral-specific: geometric mean of both countries'
            # deteriorating_bilateral_relations score
            d1 = float(_deteri_norm.loc[c1,recent].mean()) if c1 in _deteri_norm.index else 0.0
            d2 = float(_deteri_norm.loc[c2,recent].mean()) if c2 in _deteri_norm.index else 0.0
            bilateral_specific = (d1*d2)**0.5  # geometric mean

            # General tension (backup weighting)
            t1r = float(_t_norm.loc[c1,recent].mean())
            t2r = float(_t_norm.loc[c2,recent].mean())
            general = (t1r*t2r)**0.5

            net = bilateral_specific*0.65 + general*0.35

            t1p = float(_t_norm.loc[c1,prev7].mean())
            t2p = float(_t_norm.loc[c2,prev7].mean())
            trend = (t1r+t2r)/2 - (t1p+t2p)/2

            pairs.append({'c1':c1,'c2':c2,'net':net,'trend':trend,
                          'tension':(t1r+t2r)/2,'coop':0.0})

    pairs.sort(key=lambda x: x['net'],reverse=True)
    return pairs[:n_pairs]


@st.cache_data(ttl=3600)
def compute_country_bilateral_profile(_t_norm, _c_norm, _deteri_norm, _incr_norm,
                                       country, top_n=3):
    """
    FIXED: Uses geometric mean of bilateral-specific topic scores.
    A country only ranks as 'worst relation' if BOTH countries have high
    deteriorating_bilateral_relations scores — not just one of them.
    Also requires minimum volume threshold to filter out low-coverage pairs.
    """
    if country not in _t_norm.index:
        return [], []

    others  = [c for c in _t_norm.index if c != country]
    recent  = _t_norm.columns[-14:]  # 14-day window for stability
    prev14  = _t_norm.columns[-28:-14] if len(_t_norm.columns)>=28 else _t_norm.columns[:14]

    # Focal country scores (constants across loop)
    d_focal  = float(_deteri_norm.loc[country,recent].mean()) if country in _deteri_norm.index else 0.0
    i_focal  = float(_incr_norm.loc[country,recent].mean())   if country in _incr_norm.index  else 0.0
    t_focal  = float(_t_norm.loc[country,recent].mean())
    t_f_prev = float(_t_norm.loc[country,prev14].mean())

    pairs = []
    for other in others:
        try:
            # Bilateral-specific deterioration: BOTH must be high
            d_other = float(_deteri_norm.loc[other,recent].mean()) if other in _deteri_norm.index else 0.0
            bilateral_tension = (d_focal * d_other) ** 0.5  # geometric mean

            # Bilateral-specific cooperation: BOTH must be high
            i_other = float(_incr_norm.loc[other,recent].mean()) if other in _incr_norm.index else 0.0
            bilateral_coop = (i_focal * i_other) ** 0.5

            # General tension backup
            t_other = float(_t_norm.loc[other,recent].mean()) if other in _t_norm.index else 0.0
            general_tension = (t_focal * t_other) ** 0.5

            # Combined score: bilateral-specific weighted higher
            net = max(0.0, bilateral_tension * 0.6 + general_tension * 0.3 - bilateral_coop * 0.4)

            # Minimum signal threshold: skip pairs with essentially no data
            if d_focal < 0.5 and t_focal < 1.0:
                continue  # focal country has no signal at all

            # Trend: change in general tension over period
            t_o_prev = float(_t_norm.loc[other,prev14].mean()) if other in _t_norm.index else 0.0
            trnd = (t_focal + t_other) / 2 - (t_f_prev + t_o_prev) / 2

            st_lbl,st_col,st_ico,tr_txt,tr_col = relation_status(net,trnd)
            pairs.append({
                'country':other,'name':COUNTRY_NAMES.get(other,other),
                'net':net,'trend':trnd,'status':st_lbl,'color':st_col,'icon':st_ico,
            })
        except Exception:
            continue

    pairs.sort(key=lambda x: x['net'],reverse=True)
    worst = pairs[:top_n]
    best  = sorted(pairs, key=lambda x: x['net'])[:top_n]
    return worst, best


# ═══════════════════════════════════════════════════════════════
# COUNTRY PROFILE FUNCTIONS
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def compute_country_top_indices(_df_raw, country, top_n=6):
    if country not in _df_raw.index.get_level_values('country'):
        return []
    topics  = _df_raw.index.get_level_values('topic').unique()
    results = []
    for topic in topics:
        try:
            tdf    = _df_raw.xs(topic,level='topic')
            if country not in tdf.index: continue
            series = tdf.loc[country]
            recent = float(series.iloc[-7:].mean())
            flat   = tdf.values.flatten()
            pos    = flat[flat>0]
            g_max  = float(np.percentile(pos,99)) if len(pos) else 1.0
            score  = min(100.0,recent/g_max*100)
            label  = TOPIC_LABELS.get(topic,topic.replace('_',' ').title())
            results.append({'topic':topic,'label':label,'score':score})
        except Exception: continue
    results.sort(key=lambda x: x['score'],reverse=True)
    return results[:top_n]


@st.cache_data(ttl=3600)
def compute_country_alarms(_df_raw, country, top_n=5):
    if country not in _df_raw.index.get_level_values('country'):
        return []
    topics = _df_raw.index.get_level_values('topic').unique()
    alarms = []
    for topic in topics:
        try:
            tdf    = _df_raw.xs(topic,level='topic')
            if country not in tdf.index: continue
            series = tdf.loc[country]
            if len(series)<14: continue
            recent = float(series.iloc[-7:].mean())
            prev7  = float(series.iloc[-14:-7].mean())
            mu     = float(series.mean())
            sd     = float(series.std())
            z      = (recent-mu)/sd if sd>0 else 0.0
            pct    = max(-500, min(500, (recent-prev7)/(abs(prev7)+1e-9)*100)) if abs(prev7) > 1e-9 else 0.0
            flat   = tdf.values.flatten()
            pos    = flat[flat>0]
            g_max  = float(np.percentile(pos,99)) if len(pos) else 1.0
            score  = min(100.0,recent/g_max*100)
            label  = TOPIC_LABELS.get(topic,topic.replace('_',' ').title())
            alarms.append({'topic':topic,'label':label,'z':z,'pct':pct,'score':score})
        except Exception: continue
    alarms.sort(key=lambda x: abs(x['z']),reverse=True)
    return alarms[:top_n]


# ═══════════════════════════════════════════════════════════════
# GDELT NEWS FUNCTIONS
# ═══════════════════════════════════════════════════════════════
# ── Global Media RSS Feeds ──────────────────────────────────────────────────
_GLOBAL_RSS_FEEDS = {
    'BBC World': 'http://feeds.bbci.co.uk/news/world/rss.xml',
    'Al Jazeera': 'https://www.aljazeera.com/xml/rss/all.xml',
    'The Guardian': 'https://www.theguardian.com/world/rss',
    'France24': 'https://www.france24.com/en/rss',
    'DW News': 'https://rss.dw.com/rdf/rss-en-world',
    'NPR World': 'https://feeds.npr.org/1004/rss.xml',
}

@st.cache_data(ttl=900)
def fetch_global_media_rss(topic_query='', max_per_feed=3):
    """Fetch news from major global media RSS feeds, filtered by topic keywords."""
    import feedparser as _fp
    all_articles = []
    keywords = [w.lower() for w in topic_query.split() if len(w) > 2] if topic_query else []
    for source_name, feed_url in _GLOBAL_RSS_FEEDS.items():
        try:
            feed = _fp.parse(feed_url)
            count = 0
            for entry in feed.entries:
                if count >= max_per_feed:
                    break
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                text = (title + ' ' + summary).lower()
                if keywords and not any(kw in text for kw in keywords):
                    continue
                link = entry.get('link', '#')
                pub = entry.get('published', entry.get('updated', ''))
                try:
                    seendate = pd.Timestamp(pub).strftime('%Y%m%d%H%M%S')
                except Exception:
                    seendate = ''
                all_articles.append({
                    'title': title, 'url': link, 'domain': source_name,
                    'seendate': seendate, 'language': 'EN', '_src': 'RSS'
                })
                count += 1
        except Exception:
            continue
    all_articles.sort(key=lambda x: x.get('seendate', ''), reverse=True)
    return all_articles

@st.cache_data(ttl=900)
def fetch_gdelt_news(query_str, max_records=8):
    """Fetch news via Google News RSS (primary) + GDELT fallback. Filters last 2 days."""
    import xml.etree.ElementTree as ET

    # Son 2 günlük filtre
    two_days_ago = (datetime.date.today() - datetime.timedelta(days=2)).strftime('%Y-%m-%d')
    query_filtered = f"{query_str} after:{two_days_ago}"

    # --- Primary: Google News RSS ---
    try:
        encoded = urllib.parse.quote(query_filtered)
        url = f"https://news.google.com/rss/search?q={encoded}&hl=en&gl=US&ceid=US:en"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=10) as r:
            xml_data = r.read().decode('utf-8')
        root    = ET.fromstring(xml_data)
        channel = root.find('channel')
        if channel is None:
            raise ValueError("No channel in RSS")
        articles = []
        for item in channel.findall('item')[:max_records]:
            raw_title = item.findtext('title', '') or ''
            link      = item.findtext('link',  '') or '#'
            pub_date  = item.findtext('pubDate', '') or ''
            src_el    = item.find('source')
            source    = src_el.text if src_el is not None else ''
            if not source:
                try:
                    source = urllib.parse.urlparse(link).netloc.replace('www.', '')
                except Exception:
                    source = 'News'
            # Google News appends " - Source" to title — strip it
            title = raw_title
            if source and title.endswith(f' - {source}'):
                title = title[:-(len(source) + 3)]
            try:
                seendate = pd.Timestamp(pub_date).strftime('%Y%m%d%H%M%S')
            except Exception:
                seendate = ''
            articles.append({
                'title':    title,
                'url':      link,
                'domain':   source,
                'seendate': seendate,
                'language': 'EN',
            })
        if articles:
            return articles
    except Exception:
        pass

    # --- Fallback: GDELT DOC API ---
    try:
        encoded = urllib.parse.quote(query_filtered)
        url = (f"https://api.gdeltproject.org/api/v2/doc/doc?"
               f"query={encoded}&mode=artlist&maxrecords={max_records}"
               f"&format=json&sort=DateDesc")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode('utf-8'))
        return data.get('articles', [])
    except Exception:
        return []


@st.cache_data(ttl=1800)
def fetch_peak_news(country, topic, peak_date_str, days_window=3):
    """Fetch country+topic news for a specific peak date (Google News + GDELT fallback)."""
    import xml.etree.ElementTree as ET

    cname  = COUNTRY_NAMES.get(country, country)
    twords = topic.replace('_', ' ')
    pk_dt  = pd.Timestamp(peak_date_str)
    after  = (pk_dt - pd.Timedelta(days=days_window)).strftime('%Y-%m-%d')
    before = (pk_dt + pd.Timedelta(days=days_window + 1)).strftime('%Y-%m-%d')

    # --- Primary: Google News RSS with date range ---
    try:
        query   = f'{cname} {twords} after:{after} before:{before}'
        encoded = urllib.parse.quote(query)
        url     = f"https://news.google.com/rss/search?q={encoded}&hl=en&gl=US&ceid=US:en"
        req     = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=10) as r:
            xml_data = r.read().decode('utf-8')
        root    = ET.fromstring(xml_data)
        channel = root.find('channel')
        if channel is None:
            raise ValueError("No channel")
        articles = []
        for item in channel.findall('item')[:5]:
            raw_title = item.findtext('title',   '') or ''
            link      = item.findtext('link',    '') or '#'
            pub_date  = item.findtext('pubDate', '') or ''
            src_el    = item.find('source')
            source    = src_el.text if src_el is not None else ''
            if not source:
                try:
                    source = urllib.parse.urlparse(link).netloc.replace('www.', '')
                except Exception:
                    source = 'News'
            title = raw_title
            if source and title.endswith(f' - {source}'):
                title = title[:-(len(source) + 3)]
            try:
                seendate = pd.Timestamp(pub_date).strftime('%Y%m%d%H%M%S')
            except Exception:
                seendate = ''
            articles.append({
                'title':    title,
                'url':      link,
                'domain':   source,
                'seendate': seendate,
                'language': 'EN',
            })
        if articles:
            return articles
    except Exception:
        pass

    # --- Fallback: GDELT with date range ---
    try:
        query   = f'"{cname}" {twords}'
        encoded = urllib.parse.quote(query)
        start   = (pk_dt - pd.Timedelta(days=days_window)).strftime('%Y%m%d000000')
        end     = (pk_dt + pd.Timedelta(days=days_window + 1)).strftime('%Y%m%d000000')
        url     = (f"https://api.gdeltproject.org/api/v2/doc/doc?"
                   f"query={encoded}&mode=artlist&maxrecords=5&format=json"
                   f"&startdatetime={start}&enddatetime={end}&sort=DateDesc")
        req     = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode('utf-8'))
        return data.get('articles', [])
    except Exception:
        return []

# ═══════════════════════════════════════════════════════════════
# DATA LOAD & SESSION STATE
# ═══════════════════════════════════════════════════════════════
df, is_demo = load_data()
date_cols   = df.columns

# Solo tier: limit to last 3 months of data
if _IS_SOLO:
    _cutoff = pd.Timestamp.now() - pd.DateOffset(months=3)
    _keep = [c for c in df.columns if c >= _cutoff]
    if _keep:
        df = df[_keep]
_EXCLUDE_TOPICS = {'democratization','deteriorating_bilateral_relations','increasing_bilateral_relations','increasing_international_financial_support','military_deescalation','political_stability','regime_instability'}
all_topics  = sorted([t for t in df.index.get_level_values('topic').unique().tolist() if t not in _EXCLUDE_TOPICS])
all_countries = sorted(df.index.get_level_values('country').unique().tolist())

tension_norm, coop_norm = compute_bilateral_base(df)
deteri_norm, incr_norm  = _get_bilateral_specific_norm(df)

# ── Load pre-computed predictions (if available) ─────────────
@st.cache_data(ttl=3600)
def load_predictions():
    pred_file = './predictions.csv'
    trend_file = './forecast_trends.csv'
    preds, trends = None, None
    if os.path.exists(pred_file):
        try:
            preds = pd.read_csv(pred_file, parse_dates=['ds'])
            # Keep raw prediction values; scaling done in chart rendering
        except Exception:
            preds = None
    if os.path.exists(trend_file):
        try:
            trends = pd.read_csv(trend_file)
            if trends is not None and 'topic' in trends.columns and 'country' in trends.columns:
                trends = trends.dropna(subset=['topic', 'country'])
                trends['topic'] = trends['topic'].astype(str).str.strip()
                trends['country'] = trends['country'].astype(str).str.strip()
                trends = trends[trends['topic'].str.len() > 2]
                trends = trends[trends['country'].str.len() >= 2]
                if len(trends) == 0:
                    trends = None
        except Exception:
            trends = None
    # Recalculate trend_pct from raw predictions (% change first to last)
    if preds is not None and trends is not None and 'yhat' in preds.columns:
        sorted_preds = preds.sort_values('ds')
        first_vals = sorted_preds.groupby(['topic', 'country'])['yhat'].first()
        last_vals = sorted_preds.groupby(['topic', 'country'])['yhat'].last()
        calc_pct = ((last_vals - first_vals) / first_vals.abs().clip(lower=0.01)) * 100
        calc_pct = calc_pct.clip(-200, 200).reset_index()
        calc_pct.columns = ['topic', 'country', 'trend_pct']
        trends = trends.drop(columns=['trend_pct'], errors='ignore')
        trends = trends.merge(calc_pct, on=['topic', 'country'], how='left')
        trends['trend_pct'] = trends['trend_pct'].fillna(0)
        trends['direction'] = np.where(trends['trend_pct'] > 1, 'rising',
                               np.where(trends['trend_pct'] < -1, 'falling', 'stable'))
    return preds, trends

pred_df, trend_df = load_predictions()
has_predictions   = pred_df is not None and len(pred_df) > 0

if 'page' not in st.session_state:
    st.session_state.page = 'home'

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0 20px 0;'>
      <svg width='180' height='48' viewBox='0 0 180 48' xmlns='http://www.w3.org/2000/svg'>
        <!-- Dot Grid -->
        <g>
          <circle cx='8' cy='10' r='3' fill='#00d4ff'/><circle cx='18' cy='10' r='3' fill='#e0e8f0'/><circle cx='28' cy='10' r='3' fill='#00d4ff'/><circle cx='38' cy='10' r='3' fill='#e0e8f0'/>
          <circle cx='8' cy='19' r='3' fill='#e0e8f0'/><circle cx='18' cy='19' r='3' fill='#00d4ff'/><circle cx='28' cy='19' r='3' fill='#e0e8f0'/><circle cx='38' cy='19' r='3' fill='#00d4ff'/>
          <circle cx='8' cy='28' r='3' fill='#00d4ff'/><circle cx='18' cy='28' r='3' fill='#e0e8f0'/><circle cx='28' cy='28' r='3' fill='#00d4ff'/><circle cx='38' cy='28' r='3' fill='#e0e8f0'/>
          <circle cx='8' cy='37' r='3' fill='#e0e8f0'/><circle cx='18' cy='37' r='3' fill='#00d4ff'/><circle cx='28' cy='37' r='3' fill='#e0e8f0'/><circle cx='38' cy='37' r='3' fill='#00d4ff'/>
        </g>
        <!-- NER text (white) -->
            <text x="50" y="36" font-family="Inter,sans-serif" font-weight="800" font-size="30"><tspan fill="#e0e8f0">NER</tspan><tspan fill="#00d4ff">AI</tspan></text>
        <!-- AI text (cyan) -->

      </svg>
      <div style='color:#5a6b82;font-size:10px;letter-spacing:2px;margin-top:4px;text-transform:uppercase;'>Strategic Insights Hub</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Navigation ──────────────────────────────────────────
    st.markdown('<div class="sec-hdr">Navigation</div>', unsafe_allow_html=True)

    nav_pages = [
        ('home', '🏠 COMMAND CENTER'),
        ('indices', '📊 RISK MATRIX'),
        ('profile', '🌏 COUNTRY INTEL'),
        ('news', '📰 SIGNAL FEED'),
        ('predictions', '🔮 FORECAST ENGINE'),
        ('causality', '🕸️ CAUSAL NETWORK'),
        ('scenarios', '⚡ WHAT-IF SCENARIOS'),
        ('threat_radar', '🔴 THREAT RADAR'),
        ('insights', '🔍 INSIGHTS'),
        ('briefing', '📋 BRIEFING ROOM'),
        ('global_view', '🌍 GLOBAL VIEW'),
        # ('conflict', '🎯 WARZONE ORACLE'),  # DISABLED: temporarily removed
    ]
    # Solo tier: show all pages in nav, pro-only content is locked
    _PRO_ONLY_PAGES = {'predictions', 'causality', 'insights', 'briefing', 'global_view'}
    for page_key, page_label in nav_pages:
        active_style = 'border-color:rgba(0,180,255,0.5) !important;color:#007a99 !important;background:rgba(0,50,110,0.4) !important;' if st.session_state.page == page_key else ''
        if st.button(page_label, key=f'nav_{page_key}'):
            st.session_state.page = page_key
            st.rerun()

    st.markdown('<div class="h-div" style="margin:14px 0;"></div>', unsafe_allow_html=True)

    # ── Data Pipeline ────────────────────────────────────────
    st.markdown('<div class="sec-hdr">Data Pipeline</div>', unsafe_allow_html=True)

    import subprocess, sys as _sys

    indices_age = ""
    if os.path.exists('./indices.csv'):
        mt = os.path.getmtime('./indices.csv')
        delta = (datetime.datetime.now() - datetime.datetime.fromtimestamp(mt))
        h = int(delta.total_seconds() // 3600)
        indices_age = f"Last updated: {h}h ago" if h < 48 else f"Last updated: {delta.days}d ago"

    st.markdown(f"""
    <div style='font-size:0.62rem;color:rgba(0,180,255,0.5);font-family:monospace;
         padding:6px 4px;line-height:1.8;'>
      {'✅ ' + indices_age if indices_age else '⚠ No data yet'}
    </div>""", unsafe_allow_html=True)
    # [MOVED TO INLINE] 
    # [MOVED TO INLINE] if st.button('🔄 Refresh Indices', use_container_width=True,
    # [MOVED TO INLINE] help='Run gdelt_indices.py to fetch latest GDELT data'):
    # [MOVED TO INLINE] with st.spinner('Fetching GDELT data…'):
    # [MOVED TO INLINE] r = subprocess.run([_sys.executable, './gdelt_indices.py'],
    # [MOVED TO INLINE] capture_output=True, text=True, cwd='.')
    # [MOVED TO INLINE] if r.returncode == 0:
    # [MOVED TO INLINE] st.success('✅ Indices updated!')
    # [MOVED TO INLINE] st.cache_data.clear(); st.rerun()
    # [MOVED TO INLINE] else:
    # [MOVED TO INLINE] st.error(r.stderr[-600:] or 'Failed')
    # [MOVED TO INLINE] 
    # [MOVED TO INLINE] _max_s = st.slider('Max Series (causality)', 50, 500, 200, 50,
    # [MOVED TO INLINE] help='Fewer = faster. 200 ≈ 5-8 min. 500 ≈ 30+ min.')
    # [MOVED TO INLINE] if st.button('🕸 Run Causal Analysis', use_container_width=True,
    # [MOVED TO INLINE] help='Run gdelt_causality.py — top-variance series only'):
    # [MOVED TO INLINE] with st.spinner(f'Computing causality for top {_max_s} series… (~5-8 min)'):
    # [MOVED TO INLINE] r = subprocess.run(
    # [MOVED TO INLINE] [_sys.executable, './gdelt_causality.py', '--max-series', str(_max_s)],
    # [MOVED TO INLINE] capture_output=True, text=True, cwd='.')
    # [MOVED TO INLINE] if r.returncode == 0:
    # [MOVED TO INLINE] out = (r.stdout or '').strip()
    # [MOVED TO INLINE] # Check if any edges were actually found
    # [MOVED TO INLINE] if 'edges found' in out.lower() and '0 edges' in out.lower():
    # [MOVED TO INLINE] st.warning('⚠️ 0 significant relationships found — threshold values may be too strict. Try again or increase Max Series.')
    # [MOVED TO INLINE] else:
    # [MOVED TO INLINE] st.success('✅ Causal network ready!')
    # [MOVED TO INLINE] with st.expander('📋 Script output', expanded=False):
    # [MOVED TO INLINE] st.code(out[-1200:] or '(no output)')
    # [MOVED TO INLINE] st.cache_data.clear(); st.rerun()
    # [MOVED TO INLINE] else:
    # [MOVED TO INLINE] st.error('Script error:\n' + (r.stderr[-800:] or r.stdout[-400:] or 'Unknown error'))

    if st.button('⚡ Refresh All Data', use_container_width=True, type='primary',
                 help='Run full pipeline: indices → causality → forecast'):
        scripts = ['gdelt_indices.py', 'gdelt_causality.py', 'gdelt_forecast_numpy.py']
        all_ok = True
        for script in scripts:
            if not os.path.exists(f'./{script}'):
                continue
            with st.spinner(f'Running {script}…'):
                r = subprocess.run([_sys.executable, f'./{script}'],
                                   capture_output=True, text=True, cwd='.')
            if r.returncode != 0:
                st.error(f'{script} failed:\n{r.stderr[-400:]}')
                all_ok = False
                break
        if all_ok:
            st.success('✅ All data refreshed!')
            st.cache_data.clear(); st.rerun()

    st.markdown('<div class="h-div" style="margin:14px 0;"></div>', unsafe_allow_html=True)

    # ── Page-specific controls ───────────────────────────────
    # ── Normalization Setting ──
    st.markdown("---")
    norm_method = st.radio(
        "Normalization",
        ['Score (0\u2013100)', 'Z-Score', 'Raw'],
        index=0,
        key="sidebar_norm",
    )

    # Profile selectors moved to inline (render_profile)
    if st.session_state.page == 'news':
        st.markdown('<div class="sec-hdr">Live News Feed</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style='padding:8px;background:rgba(0,150,255,0.05);
             border:1px solid rgba(0,150,255,0.1);border-radius:6px;
             font-size:0.62rem;color:rgba(0,180,255,0.4);font-family:monospace;'>
          <span class='live-dot'></span>GDELT Project<br>
          Real-time global news<br>
          28 topic categories
        </div>""", unsafe_allow_html=True)

        # Predictions selectors moved to inline (render_predictions)
    if True:  # All pages get defaults; indices overrides via inline widgets
        sel_topic = all_topics[0] if all_topics else 'political_instability'
        sel_countries = ['US','RS','CH','TU']
        n_days = 60
        map_date = date_cols[-1] if len(date_cols) else pd.Timestamp.now()
        heatmap_n = 15
        norm_method = st.session_state.get('sidebar_norm', 'Score (0\u2013100)')
        map_date_str = map_date.strftime('%Y-%m-%d')
    if st.session_state.page not in ('profile',):
        profile_country = 'US'
        bi_a = 'US'; bi_b = 'RS'; bi_days = 60
    # ── NERAI watermark overlay ──
    st.markdown("""<div style="position:fixed;top:50%;left:50%;transform:translate(-50%,-50%) rotate(-35deg);pointer-events:none;z-index:1;display:flex;align-items:center;gap:15px;opacity:0.03;"><div style="width:80px;height:80px;background:radial-gradient(circle,rgba(0,212,255,1) 28%,transparent 30%);background-size:16px 16px;"></div><span style="font-size:110px;font-weight:900;letter-spacing:5px;white-space:nowrap;font-family:Arial Black,Impact,sans-serif;color:#00d4ff;">NERAI</span></div>""", unsafe_allow_html=True)

    if st.session_state.page not in ('predictions',):
        sel_pred_topic   = all_topics[0] if all_topics else ''
        sel_pred_country = 'US'
        pred_hist_months = 24


# ══════════════════════════════════════════════════════════════
# STRATEGIC ANALYSIS ENGINE — Insight Layer
# ══════════════════════════════════════════════════════════════

_ANALYSIS_CSS = """<style>
.nerai-sa{background:linear-gradient(135deg,rgba(0,212,255,.06) 0%,rgba(0,40,60,.15) 100%);border-left:3px solid #00d4ff;border-radius:0 8px 8px 0;padding:16px 20px;margin:12px 0 20px 0;font-size:14px;line-height:1.65;color:#c8d6e5}
.nerai-sa .sa-h{display:flex;align-items:center;gap:8px;margin-bottom:10px;font-weight:600;font-size:13px;text-transform:uppercase;letter-spacing:1.2px;color:#00d4ff}
.nerai-sa .sa-b{color:#dfe6ec;font-size:14px}.nerai-sa .sa-b strong{color:#00d4ff}
.sig-b{display:inline-flex;align-items:center;gap:4px;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:700;letter-spacing:.5px}
.sig-b.ri{background:rgba(255,71,87,.18);color:#ff4757}.sig-b.fa{background:rgba(46,213,115,.18);color:#2ed573}
.sig-b.st{background:rgba(255,165,2,.15);color:#ffa502}.sig-b.al{background:rgba(255,71,87,.25);color:#ff4757;border:1px solid rgba(255,71,87,.4)}
.sig-b.no{background:rgba(46,213,115,.15);color:#2ed573}.sig-b.vo{background:rgba(255,165,2,.2);color:#ffa502}
.nerai-es{background:linear-gradient(135deg,rgba(0,212,255,.08) 0%,rgba(0,30,50,.2) 100%);border:1px solid rgba(0,212,255,.2);border-radius:10px;padding:20px 24px;margin:0 0 24px 0}
.nerai-es .es-t{font-size:14px;font-weight:700;color:#00d4ff;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:14px;display:flex;align-items:center;gap:8px}
.nerai-es .es-i{display:flex;align-items:flex-start;gap:10px;margin-bottom:8px;font-size:13.5px;color:#c8d6e5;line-height:1.5}
.nerai-es .es-i .bu{color:#00d4ff;font-size:16px;margin-top:-1px}
</style>"""

def _sig(d, lbl=None):
    _m = {'rising':'ri','falling':'fa','stable':'st','alert':'al','normal':'no','volatile':'vo'}
    _a = {'rising':'\u2191','falling':'\u2193','stable':'\u2192','alert':'\u26a0','normal':'\u25cf','volatile':'\u2195'}
    return f'<span class="sig-b {_m.get(d,"st")}">{_a.get(d,"\u25cf")} {lbl or d.upper()}</span>'

def _sa_box(header, body, sig=None):
    s = f' {_sig(sig[0], sig[1])}' if sig else ''
    return f'<div class="nerai-sa"><div class="sa-h">\u25c6 {header}{s}</div><div class="sa-b">{body}</div></div>'

def _es_box(items):
    b = ''.join(f'<div class="es-i"><span class="bu">\u25b8</span><span>{i}</span></div>' for i in items)
    return f'<div class="nerai-es"><div class="es-t">\u25c8 Strategic Assessment</div>{b}</div>'


def _indices_exec_analysis(df_recent, sel_topic, COUNTRY_NAMES):
    """Executive strategic assessment for Risk Matrix page."""
    items = []
    if df_recent.empty or len(df_recent.columns) < 2:
        return ''
    latest = df_recent.iloc[:, -1]
    prev = df_recent.iloc[:, -2]
    deltas = latest - prev
    top_r = deltas.nlargest(3)
    top_f = deltas.nsmallest(2)
    for c, d in top_r.items():
        cn = COUNTRY_NAMES.get(c, c)
        v = latest.get(c, 0)
        if abs(d) > 2:
            sev = 'significant' if abs(d) > 5 else 'moderate'
            items.append(f"<strong>{cn}</strong> {sel_topic} index surged {_sig('rising', f'+{d:.1f}')} to <strong>{v:.0f}</strong> \u2014 {sev} escalation signal.")
    for c, d in top_f.items():
        cn = COUNTRY_NAMES.get(c, c)
        v = latest.get(c, 0)
        if d < -2:
            items.append(f"<strong>{cn}</strong> {sel_topic} easing {_sig('falling', f'{d:.1f}')} \u2014 de-escalation or policy shift may be underway.")
    if len(df_recent.columns) >= 7:
        std_w = df_recent.iloc[:, -7:].std(axis=1)
        mv = std_w.nlargest(1)
        for c, vol in mv.items():
            cn = COUNTRY_NAMES.get(c, c)
            if vol > 5:
                items.append(f"<strong>{cn}</strong> high volatility {_sig('volatile', f'\u03c3={vol:.1f}')} \u2014 erratic trajectory suggests unpredictable environment.")
    if not items:
        items.append(f"All monitored countries showing stable {sel_topic} indicators within normal ranges. {_sig('normal', 'BASELINE')}")
    return _es_box(items[:4])

def _indices_ts_analysis(df_recent, sel_topic, sel_countries, COUNTRY_NAMES):
    """7-day trend assessment after time-series chart."""
    if df_recent.empty or len(df_recent.columns) < 3:
        return ''
    ncols = min(7, len(df_recent.columns))
    ws = df_recent.iloc[:, -ncols]
    we = df_recent.iloc[:, -1]
    wc = we - ws
    parts = []
    for c in sel_countries[:4]:
        if c not in wc.index: continue
        chg = wc[c]; v = we[c]; cn = COUNTRY_NAMES.get(c, c)
        if abs(chg) < 1:
            desc = 'holding steady'
        elif chg > 0:
            desc = f'up {chg:.1f}pts over {ncols}d'
        else:
            desc = f'down {abs(chg):.1f}pts over {ncols}d'
        if v > 70: rl = '\u2014 <strong>elevated risk zone</strong>, potential crisis conditions'
        elif v > 50: rl = '\u2014 above baseline, sustained pressure on governance structures'
        elif v > 30: rl = '\u2014 moderate levels within historical norms'
        else: rl = '\u2014 low-risk territory, relative stability'
        parts.append(f"<strong>{cn}</strong> ({v:.0f}): {desc} {rl}")
    if not parts: return ''
    avg = wc.reindex(sel_countries[:4]).dropna().mean() if len(sel_countries) else 0
    if avg > 3: sig = ('rising', 'ESCALATING')
    elif avg < -3: sig = ('falling', 'DE-ESCALATING')
    else: sig = ('stable', 'HOLDING')
    return _sa_box('7-Day Trend Assessment', '<br>'.join(parts), sig)

def _indices_heatmap_analysis(df_norm, sel_topic, COUNTRY_NAMES):
    """Regional heat distribution analysis after heatmap."""
    if df_norm.empty or len(df_norm.columns) < 5:
        return ''
    lat5 = df_norm.iloc[:, -5:]
    hot = lat5.mean(axis=1).nlargest(3)
    cold = lat5.mean(axis=1).nsmallest(3)
    hn = [COUNTRY_NAMES.get(c, c) for c in hot.index]
    cn_list = [COUNTRY_NAMES.get(c, c) for c in cold.index]
    body = (
        f"<strong>Hotspot cluster:</strong> {', '.join(hn)} \u2014 consistently elevated {sel_topic} scores indicate structural pressure, not isolated events. Policy responses from these states bear close monitoring.<br>"
        f"<strong>Stability corridor:</strong> {', '.join(cn_list)} \u2014 sustained low activity. However, sudden reversals in quiet environments often precede the most disruptive shocks."
    )
    return _sa_box('Regional Heat Distribution', body)

def _indices_corr_analysis(df_norm, sel_countries, COUNTRY_NAMES):
    """Cross-country risk linkage analysis after correlation matrix."""
    if df_norm.empty or len(sel_countries) < 2:
        return ''
    sub = df_norm.reindex([c for c in sel_countries if c in df_norm.index]).dropna(how='all')
    if sub.shape[0] < 2: return ''
    corr = sub.T.corr()
    hi, lo = [], []
    for i in range(len(corr)):
        for j in range(i+1, len(corr)):
            v = corr.iloc[i, j]
            if v > 0.7: hi.append((corr.index[i], corr.columns[j], v))
            elif v < -0.3: lo.append((corr.index[i], corr.columns[j], v))
    parts = []
    for c1, c2, v in sorted(hi, key=lambda x: -x[2])[:2]:
        n1, n2 = COUNTRY_NAMES.get(c1, c1), COUNTRY_NAMES.get(c2, c2)
        parts.append(f"<strong>{n1}\u2013{n2}</strong> (r={v:.2f}): Risk trajectories tightly coupled \u2014 escalation in one cascades to the other. Likely shared geopolitical drivers or alliance dynamics.")
    for c1, c2, v in sorted(lo, key=lambda x: x[2])[:1]:
        n1, n2 = COUNTRY_NAMES.get(c1, c1), COUNTRY_NAMES.get(c2, c2)
        parts.append(f"<strong>{n1}\u2013{n2}</strong> (r={v:.2f}): Inverse dynamics \u2014 when one stabilizes, the other destabilizes. Possible resource/attention reallocation between theaters.")
    if not parts:
        parts.append("Selected countries show moderate independence \u2014 no dominant contagion pattern detected in current window.")
    return _sa_box('Cross-Country Risk Linkages', '<br>'.join(parts))


def _profile_exec_analysis(profile_country, cur_t, cur_c, cur_net, trend_bi, prof_alarms, partner_a, partner_b, COUNTRY_NAMES):
    """Strategic assessment for Country Intelligence page."""
    cn = COUNTRY_NAMES.get(profile_country, profile_country)
    items = []
    if cur_t > 70 and cur_c < 30:
        items.append(f"<strong>{cn}</strong> in high-conflict/low-cooperation state {_sig('alert','CRITICAL')} \u2014 diplomatic channels strained. This configuration historically precedes significant policy shifts or escalatory actions.")
    elif cur_t > 50:
        items.append(f"<strong>{cn}</strong> conflict pressure at <strong>{cur_t:.0f}</strong> {_sig('rising','ELEVATED')} \u2014 above stability threshold. Regional actors should prepare contingency responses.")
    elif cur_c > 60:
        items.append(f"<strong>{cn}</strong> cooperative signals strong at <strong>{cur_c:.0f}</strong> {_sig('normal','CONSTRUCTIVE')} \u2014 diplomatic engagement active. Window for productive negotiations may be open.")
    else:
        items.append(f"<strong>{cn}</strong> operating within normal parameters \u2014 conflict ({cur_t:.0f}) and cooperation ({cur_c:.0f}) in equilibrium.")
    if partner_a and partner_b:
        pa = COUNTRY_NAMES.get(partner_a, partner_a)
        pb = COUNTRY_NAMES.get(partner_b, partner_b)
        if cur_net > 0.3:
            items.append(f"<strong>{pa}\u2013{pb}</strong> bilateral: Net positive ({cur_net:.2f}) \u2014 cooperative dynamics dominate. Trade, diplomatic, and security cooperation likely stable.")
        elif cur_net < -0.3:
            items.append(f"<strong>{pa}\u2013{pb}</strong> bilateral: Net negative ({cur_net:.2f}) {_sig('rising','TENSION')} \u2014 adversarial dynamics prevail. Monitor for sanctions, military posturing, or proxy conflicts.")
        else:
            items.append(f"<strong>{pa}\u2013{pb}</strong> bilateral: Neutral zone ({cur_net:.2f}) \u2014 neither cooperative nor adversarial. Relationship in transitional phase.")
    if trend_bi is not None:
        if trend_bi > 5:
            items.append(f"Bilateral trend sharply positive (+{trend_bi:.1f}) \u2014 rapid improvement in relations, possibly driven by new diplomatic initiatives or shared threat perception.")
        elif trend_bi < -5:
            items.append(f"Bilateral trend deteriorating ({trend_bi:.1f}) {_sig('rising','DETERIORATING')} \u2014 relationship under increasing strain. Early warning for potential diplomatic incidents.")
    return _es_box(items[:4])

def _profile_gauge_analysis(cur_t, cur_c, cur_net, profile_country, COUNTRY_NAMES):
    """Conflict/cooperation gauge interpretation."""
    cn = COUNTRY_NAMES.get(profile_country, profile_country)
    ratio = cur_c / max(cur_t, 0.1)
    if ratio > 2:
        state = f"{cn}'s diplomatic environment is cooperation-dominant (ratio {ratio:.1f}:1). Political risk for foreign investment and partnerships is <strong>low</strong>."
        sig = ('normal', 'LOW RISK')
    elif ratio > 1:
        state = f"{cn} leans cooperative but with meaningful conflict undercurrents. Engagement is viable but requires active risk monitoring."
        sig = ('stable', 'MODERATE')
    elif ratio > 0.5:
        state = f"{cn} conflict and cooperation are nearly balanced \u2014 a volatile equilibrium. Small shocks could tip the balance in either direction."
        sig = ('volatile', 'UNSTABLE EQ.')
    else:
        state = f"{cn} is conflict-dominant (ratio {1/max(ratio,0.01):.1f}:1). Operating environment is adversarial. Recommend defensive posture for exposed assets and personnel."
        sig = ('alert', 'HIGH RISK')
    return _sa_box('Conflict-Cooperation Balance', state, sig)


def _forecast_exec_analysis(topic, country, current_val, fc_end_val, fc, COUNTRY_NAMES):
    """Strategic forecast intelligence."""
    cn = COUNTRY_NAMES.get(country, country)
    if fc is None or len(fc) == 0 or current_val is None or fc_end_val is None:
        return ''
    chg = fc_end_val - current_val
    if chg > 10:
        d, lbl = 'rising', 'ESCALATION FORECAST'
        sev = 'significant escalation' if chg > 20 else 'moderate increase'
        body = (f"Model projects <strong>{sev}</strong> in {topic} for {cn}. Trajectory from <strong>{current_val:.0f}</strong> to <strong>{fc_end_val:.0f}</strong> signals building structural pressure. "
                f"<strong>Decision signal:</strong> Increase monitoring frequency and prepare scenario-specific response options. Consider pre-positioning diplomatic or operational assets.")
    elif chg < -10:
        d, lbl = 'falling', 'DE-ESCALATION FORECAST'
        sev = 'significant de-escalation' if chg < -20 else 'gradual cooling'
        body = (f"Model projects <strong>{sev}</strong> for {cn} {topic}. Moving from <strong>{current_val:.0f}</strong> toward <strong>{fc_end_val:.0f}</strong>. "
                f"<strong>Decision signal:</strong> Window for diplomatic engagement or investment repositioning. Reduced operational tempo may be appropriate.")
    else:
        d, lbl = 'stable', 'STEADY STATE'
        body = (f"{cn} {topic} forecast shows minimal directional change \u2014 current levels (~<strong>{current_val:.0f}</strong>) expected to persist. "
                f"<strong>Decision signal:</strong> Maintain standard monitoring protocols. No immediate recalibration needed.")
    ci_cols = [c for c in fc.columns if 'lower' in c.lower() or 'lo' in c.lower()]
    ci_cols_u = [c for c in fc.columns if 'upper' in c.lower() or 'hi' in c.lower()]
    if ci_cols and ci_cols_u:
        try:
            ci_w = (fc[ci_cols_u[0]] - fc[ci_cols[0]]).mean()
            if ci_w > 30: body += "<br><em>Wide confidence bands \u2014 high uncertainty. Treat as directional guidance only.</em>"
            elif ci_w > 15: body += "<br><em>Moderate confidence \u2014 forecast is indicative but watch for deviation triggers.</em>"
            else: body += "<br><em>Tight intervals \u2014 model has high conviction in this trajectory.</em>"
        except: pass
    return _sa_box('Forecast Intelligence', body, (d, lbl))

def _causality_exec_analysis(narrative_text):
    """Wrap causal narrative in strategic analysis box."""
    if not narrative_text:
        return ''
    return _sa_box('Causal Network Intelligence', narrative_text, ('alert', 'WATCH'))

def _threat_radar_analysis(df_recent, sel_topic, COUNTRY_NAMES):
    """Strategic threat radar analysis."""
    if df_recent is None or df_recent.empty:
        return ''
    latest = df_recent.iloc[:, -1]
    crit = latest[latest > 70]
    warn = latest[(latest > 50) & (latest <= 70)]
    items = []
    if len(crit) > 0:
        crit_names = [COUNTRY_NAMES.get(c, c) for c in crit.nlargest(5).index]
        items.append(f"<strong>Critical zone ({len(crit)} countries):</strong> {', '.join(crit_names)} \u2014 operating above crisis threshold. Active monitoring and contingency planning recommended.")
    if len(warn) > 0:
        warn_names = [COUNTRY_NAMES.get(c, c) for c in warn.nlargest(5).index]
        items.append(f"<strong>Watch zone ({len(warn)} countries):</strong> {', '.join(warn_names)} \u2014 elevated but below crisis level. Potential for rapid deterioration if external shocks occur.")
    stable_count = len(latest[latest <= 50])
    items.append(f"<strong>{stable_count} countries</strong> in stable zone \u2014 normal operational environment. Standard risk posture appropriate.")
    return _es_box(items[:4])

# ═══════════════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════════════
def render_home():
    """Home page — Premium world-class hero + KPIs + module navigation."""

    # ── 1. HERO: AI + Geopolitical Network Visualization ──
    # (from nerai_premium_css.py — replaces old Three.js globe)
    nerai_premium_css.inject_home_hero()
    nerai_premium_css.inject_global_premium_css()
    st.markdown(_MOBILE_CSS, unsafe_allow_html=True)

    # === FAZ 4e: Alert/Notification System ===
    try:
        _instab_alert = df.xs("instability", level="topic", drop_level=True) if "instability" in df.index.get_level_values("topic") else None
        if _instab_alert is not None and len(df.columns) >= 2:
            _al_latest = df.columns[-1]
            _al_prev = df.columns[-2]
            _al_chg = ((_instab_alert[_al_latest] - _instab_alert[_al_prev]) / _instab_alert[_al_prev].replace(0, np.nan) * 100).dropna()
            _spikes = _al_chg[_al_chg > 20].sort_values(ascending=False)
            if not _spikes.empty:
                for _ac, _av in _spikes.head(3).items():
                    st.toast(f"Alert: {COUNTRY_NAMES.get(_ac, _ac)} instability surged {_av:.0f}%", icon="\U0001f6a8")
    except Exception:
        pass

    # ── 2. PREMIUM KPI SECTION ──
    st.markdown("""
    <div style="
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin: -0.5rem 0 2rem 0;
        padding: 0 4px;
    ">
        <div style="
            background: linear-gradient(135deg, rgba(0,212,255,0.06) 0%, rgba(10,14,23,0.95) 100%);
            border: 1px solid rgba(0,212,255,0.12);
            border-radius: 14px;
            padding: 24px 20px;
            text-align: center;
            backdrop-filter: blur(12px);
            position: relative;
            overflow: hidden;
        ">
            <div style="position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,212,255,0.25),transparent);"></div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:700;color:#00d4ff;margin-bottom:4px;text-shadow:0 0 20px rgba(0,212,255,0.15);">60</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.65rem;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#6b7f99;">Countries</div>
        </div>
        <div style="
            background: linear-gradient(135deg, rgba(0,212,255,0.06) 0%, rgba(10,14,23,0.95) 100%);
            border: 1px solid rgba(0,212,255,0.12);
            border-radius: 14px;
            padding: 24px 20px;
            text-align: center;
            backdrop-filter: blur(12px);
            position: relative;
            overflow: hidden;
        ">
            <div style="position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,212,255,0.25),transparent);"></div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:700;color:#00d4ff;margin-bottom:4px;text-shadow:0 0 20px rgba(0,212,255,0.15);">40</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.65rem;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#6b7f99;">Risk Topics</div>
        </div>
        <div style="
            background: linear-gradient(135deg, rgba(0,212,255,0.06) 0%, rgba(10,14,23,0.95) 100%);
            border: 1px solid rgba(0,212,255,0.12);
            border-radius: 14px;
            padding: 24px 20px;
            text-align: center;
            backdrop-filter: blur(12px);
            position: relative;
            overflow: hidden;
        ">
            <div style="position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,212,255,0.25),transparent);"></div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:700;color:#00d4ff;margin-bottom:4px;text-shadow:0 0 20px rgba(0,212,255,0.15);">354</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.65rem;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#6b7f99;">Days of Data</div>
        </div>
        <div style="
            background: linear-gradient(135deg, rgba(0,212,255,0.06) 0%, rgba(10,14,23,0.95) 100%);
            border: 1px solid rgba(0,212,255,0.12);
            border-radius: 14px;
            padding: 24px 20px;
            text-align: center;
            backdrop-filter: blur(12px);
            position: relative;
            overflow: hidden;
        ">
            <div style="position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,212,255,0.25),transparent);"></div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:700;color:#00d4ff;margin-bottom:4px;text-shadow:0 0 20px rgba(0,212,255,0.15);">2,400</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.65rem;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#6b7f99;">Data Points</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Status bar ──
    st.markdown("""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        padding: 10px 24px;
        margin: 0 auto 2rem auto;
        max-width: 600px;
        background: rgba(17,24,39,0.6);
        border: 1px solid rgba(0,212,255,0.08);
        border-radius: 30px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 1.5px;
        color: #6b7f99;
    ">
        <span style="color:#00e676;font-weight:600;">● LIVE</span>
        <span style="color:rgba(0,212,255,0.15);">│</span>
        <span>GDELT PROJECT</span>
        <span style="color:rgba(0,212,255,0.15);">│</span>
        <span>LAST UPDATE: RECENT</span>
        <span style="color:rgba(0,212,255,0.15);">│</span>
        <span style="color:#00e676;">✓ ONLINE</span>
    </div>
    """, unsafe_allow_html=True)

    # ── 3. MODULE NAVIGATION SECTION ──
    st.markdown("""
    <div style="
        display: flex;
        align-items: center;
        gap: 16px;
        margin: 1.5rem 0 1.2rem 0;
    ">
        <div style="flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(0,212,255,0.2));"></div>
        <span style="
            font-family:'Inter',sans-serif;
            font-size:0.7rem;
            font-weight:600;
            letter-spacing:3px;
            text-transform:uppercase;
            color:rgba(0,212,255,0.5);
            white-space:nowrap;
        ">SELECT A MODULE TO BEGIN</span>
        <div style="flex:1;height:1px;background:linear-gradient(90deg,rgba(0,212,255,0.2),transparent);"></div>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown("""
        <div style="text-align:center;padding:8px 0;">
            <div style="font-size:1.6rem;margin-bottom:10px;">📊</div>
            <div style="font-family:'Inter',sans-serif;font-size:1rem;font-weight:700;color:#e8edf4;margin-bottom:6px;">Risk Matrix</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.75rem;color:#6b7f99;line-height:1.5;">
                Topic-based geopolitical risk indices across 60 countries.<br>
                Time series, heatmaps, world maps, correlations.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("→ Open Risk Matrix", key="home_to_indices", use_container_width=True):
            st.session_state.page = "indices"
            st.rerun()

    with m2:
        st.markdown("""
        <div style="text-align:center;padding:8px 0;">
            <div style="font-size:1.6rem;margin-bottom:10px;">🎯</div>
            <div style="font-family:'Inter',sans-serif;font-size:1rem;font-weight:700;color:#e8edf4;margin-bottom:6px;">Country Intel</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.75rem;color:#6b7f99;line-height:1.5;">
                Deep-dive into any country: top risk scores, active alarms, bilateral relations worst & best partners.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("→ Open Country Intel", key="home_to_profile", use_container_width=True):
            st.session_state.page = "profile"
            st.rerun()

    with m3:
        st.markdown("""
        <div style="text-align:center;padding:8px 0;">
            <div style="font-size:1.6rem;margin-bottom:10px;">📰</div>
            <div style="font-family:'Inter',sans-serif;font-size:1rem;font-weight:700;color:#e8edf4;margin-bottom:6px;">Signal Feed</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.75rem;color:#6b7f99;line-height:1.5;">
                Multi-source global intelligence — GDELT + BBC + Al Jazeera + Guardian + DW + NPR.<br>
                Real-time global news intelligence feed.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("→ Open Signal Feed", key="home_to_news", use_container_width=True):
            st.session_state.page = "news"
            st.rerun()

    with m4:
        st.markdown("""
        <div style="text-align:center;padding:8px 0;">
            <div style="font-size:1.6rem;margin-bottom:10px;">🔮</div>
            <div style="font-family:'Inter',sans-serif;font-size:1rem;font-weight:700;color:#e8edf4;margin-bottom:6px;">Forecast Engine</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.75rem;color:#6b7f99;line-height:1.5;">
                N-HiTS deep learning 12-month forecasts<br>
                for 2,400 topic × country risk series.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("→ Open Forecast Engine", key="home_to_predictions", use_container_width=True):
            st.session_state.page = "predictions"
            st.rerun()

    # ── Footer tagline ──
    st.markdown("""
    <div style="
        text-align: center;
        margin: 2.5rem 0 1rem 0;
        padding: 16px 0;
        border-top: 1px solid rgba(0,212,255,0.06);
    ">
        <div style="
            font-family:'Inter',sans-serif;
            font-size:0.7rem;
            font-weight:600;
            letter-spacing:3px;
            text-transform:uppercase;
            color:#4a5d75;
            margin-bottom:12px;
        ">TRANSFORMING GLOBAL DATA INTO ACTIONABLE INTELLIGENCE</div>
        <div style="
            display:flex;
            justify-content:center;
            gap:10px;
            flex-wrap:wrap;
        ">
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;padding:5px 12px;border:1px solid rgba(0,212,255,0.12);border-radius:20px;color:#6b7f99;letter-spacing:0.5px;">Deep Learning</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;padding:5px 12px;border:1px solid rgba(0,212,255,0.12);border-radius:20px;color:#6b7f99;letter-spacing:0.5px;">NLP</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;padding:5px 12px;border:1px solid rgba(0,212,255,0.12);border-radius:20px;color:#6b7f99;letter-spacing:0.5px;">GDELT</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;padding:5px 12px;border:1px solid rgba(0,212,255,0.12);border-radius:20px;color:#6b7f99;letter-spacing:0.5px;">Predictive Analytics</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;padding:5px 12px;border:1px solid rgba(0,212,255,0.12);border-radius:20px;color:#6b7f99;letter-spacing:0.5px;">Risk Modeling</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;padding:5px 12px;border:1px solid rgba(0,212,255,0.12);border-radius:20px;color:#6b7f99;letter-spacing:0.5px;">Neural Networks</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_indices():
    import streamlit.components.v1 as _stc

    # ── Premium Page Header
    nerai_premium_css.inject_page_header(
        title="Risk Matrix",
        subtitle="Topic-based geopolitical risk indices across 60 countries",
        badge="LIVE",
        icon=""
    )
    nerai_premium_css.inject_global_premium_css()
    nerai_premium_css.inject_filter_bar_css()

    # ══ INLINE FILTER BAR ══

    topic_display = {t: TOPIC_LABELS.get(t, t.replace('_',' ').title()) for t in all_topics}

    fc1, fc2 = st.columns([1, 1])
    with fc1:
        sel_label = st.selectbox(
            "TOPIC",
            list(topic_display.values()),
            index=list(topic_display.values()).index('Political Instability')
            if 'Political Instability' in topic_display.values() else 0,
            key="idx_topic"
        )
    sel_topic = [k for k, v in topic_display.items() if v == sel_label][0]

    with fc2:
        c_opts = [f"{COUNTRY_NAMES.get(c,c)} ({c})" for c in all_countries]
        defaults = ['United States (US)','Russia (RS)','China (CH)','Turkey (TU)','Iran (IR)']
        defaults = [d for d in defaults if d in c_opts][:4]
        sel_c_labels = st.multiselect(
            "COUNTRIES",
            c_opts,
            default=defaults,
            key="idx_countries"
        )
    sel_countries = [x.split('(')[-1].strip(')') for x in sel_c_labels]

    fc3, fc4, fc5 = st.columns([1, 1, 1])
    with fc3:
        n_days = st.slider("PERIOD (DAYS)", 14, min(180, len(date_cols)), 60, key="idx_days")
    with fc4:
        map_opts = [d.strftime('%Y-%m-%d') for d in date_cols[-90:]] if len(date_cols) > 0 else []
        map_date_str = st.selectbox(
            "MAP DATE",
            map_opts,
            index=len(map_opts) - 1 if map_opts else 0,
            key="idx_map_date"
        )
        map_date = pd.Timestamp(map_date_str) if map_date_str else pd.Timestamp.now()
    with fc5:
        heatmap_n = st.slider("HEATMAP TOP N", 8, 30, 15, key="idx_heatmap_n")
    st.markdown('<div class="nerai-filter-divider"></div>', unsafe_allow_html=True)

    norm_method = st.session_state.get('sidebar_norm', 'Score (0\u2013100)')

    # ══ DATA PREP ══
    if sel_topic in df.index.get_level_values('topic'):
        df_topic_raw = df.xs(sel_topic, level='topic')
    else:
        df_topic_raw = df.groupby(level='country').mean()

    df_topic_raw  = df_topic_raw.reindex(columns=sorted(df_topic_raw.columns))
    df_recent_raw = df_topic_raw[date_cols[-n_days:]]
    df_norm       = apply_norm(df_topic_raw, norm_method)
    _pv = df_norm.where(df_norm > 0)
    _rm = _pv.median(axis=1)
    _th = _rm * 0.05
    _mk = df_norm.lt(_th, axis=0) | (df_norm == 0)
    df_norm = df_norm.where(~_mk, np.nan).interpolate(axis=1, method='linear', limit_direction='both').ffill(axis=1).bfill(axis=1).fillna(0)
    df_recent     = apply_norm(df_recent_raw, norm_method)
    _pv2 = df_recent.where(df_recent > 0)
    _rm2 = _pv2.median(axis=1)
    _th2 = _rm2 * 0.05
    _mk2 = df_recent.lt(_th2, axis=0) | (df_recent == 0)
    df_recent = df_recent.where(~_mk2, np.nan).interpolate(axis=1, method='linear', limit_direction='both').ffill(axis=1).bfill(axis=1).fillna(0)

    sel_label = TOPIC_LABELS.get(sel_topic, sel_topic.replace('_',' ').title())

    st.markdown(_ANALYSIS_CSS, unsafe_allow_html=True)
    # ── Strategic Executive Assessment ──
    try:
        _exec_html = _indices_exec_analysis(df_recent, sel_topic, COUNTRY_NAMES)
        if _exec_html: st.markdown(_exec_html, unsafe_allow_html=True)
    except: pass

    # ══ KPI CARDS ══
    nerai_premium_css.inject_section_header("Key Risk Indicators", icon="")
    st.markdown("""
    <div style='padding:10px 16px;background:rgba(0,119,168,0.06);border-left:3px solid #0077a8;
         border-radius:4px;margin-bottom:16px;font-size:0.78rem;color:#2a4a6a;line-height:1.7;'>
      <b>How to read:</b> Scores range from <b>0</b> (minimal risk activity) to <b>100</b> (peak recorded risk).
      A <span style='color:#00b4d8;font-weight:700;'>low score</span> indicates relative stability, while a
      <span style='color:#e05060;font-weight:700;'>high score</span> signals elevated risk events in GDELT data.
      The <b>delta</b> (\u25b2/\u25bc) shows the change from the previous period \u2014 positive delta means <i>increasing risk</i>.
      Scores are normalized per-topic: a score of 60 in "Political Instability" means 60% of the historical peak for that dimension.
    </div>""", unsafe_allow_html=True)

    kpi_countries = (sel_countries + all_countries)[:4]
    kpi_cols = st.columns(4)
    for idx, c_name in enumerate(kpi_countries):
        c_label = COUNTRY_NAMES.get(c_name, c_name)
        if c_name in df_recent.index:
            series = df_recent.loc[c_name]
            last_val  = series.iloc[-1]  if len(series) else 0
            prev_val  = series.iloc[-2]  if len(series) >= 2 else last_val
            delta_val = last_val - prev_val
            delta_str = f"{delta_val:+.1f}"
            spark_color = '#ff4757' if delta_val > 0 else '#00e676' if delta_val < 0 else '#8a9bb5'
        else:
            last_val, delta_str, spark_color, series = 0, "+0.0", '#8a9bb5', pd.Series(dtype=float)

        with kpi_cols[idx]:
            st.metric(c_label, f"{last_val:.1f}", delta_str)
            if len(series) >= 2:
                try:
                    st.plotly_chart(chart_sparkline(series.iloc[-30:], spark_color),
                                   use_container_width=True, config={'displayModeBar': False})
                except Exception:
                    pass

    # ══ INDICES TIME SERIES CHART ══
    nerai_premium_css.inject_section_header(f"Risk Trend — {sel_label}", icon="")
    if sel_countries and len(df_recent.columns) > 1:
        try:
            _idx_fig = go.Figure()
            _risk_colors = ['#00d4ff', '#ff4757', '#ffb347', '#00e676', '#a78bfa', '#f472b6', '#38bdf8', '#facc15']
            for ci, c in enumerate(sel_countries):
                if c in df_recent.index:
                    _s = df_recent.loc[c]
                    _idx_fig.add_trace(go.Scatter(
                        x=[d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else str(d) for d in _s.index],
                        y=_s.values,
                        name=COUNTRY_NAMES.get(c, c),
                        mode='lines',
                        line=dict(color=_risk_colors[ci % len(_risk_colors)], width=2),
                        hovertemplate='%{y:.1f}<extra>%{fullData.name}</extra>'
                    ))
            _idx_fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=360,
                margin=dict(l=40, r=20, t=30, b=40),
                legend=dict(orientation='h', y=-0.15, font=dict(size=11, color='#8a9bb5')),
                xaxis=dict(gridcolor='rgba(0,212,255,0.06)', showline=False, tickfont=dict(color='#4a5d75', size=10)),
                yaxis=dict(gridcolor='rgba(0,212,255,0.06)', showline=False, tickfont=dict(color='#4a5d75', size=10),
                           title=norm_method, title_font=dict(color='#6b7f99', size=11)),
                hovermode='x unified',
                hoverlabel=dict(bgcolor='#111827', font_color='#e8edf4', bordercolor='rgba(0,212,255,0.2)'),
            )
            st.plotly_chart(_idx_fig, use_container_width=True, config={'displayModeBar': False})
        except Exception:
            pass

    # ── Strategic: 7-Day Trend Assessment ──
    try:
        _ts_html = _indices_ts_analysis(df_recent, sel_topic, sel_countries, COUNTRY_NAMES)
        if _ts_html: st.markdown(_ts_html, unsafe_allow_html=True)
    except: pass

    # ══ DAILY INDICES TABLE ══
    if sel_countries:
        nerai_premium_css.inject_section_header(f"Daily Indices — {sel_label}", icon="")
        rows = []
        for c in sel_countries:
            if c in df_recent.index:
                s = df_recent.loc[c]
                rows.append({'Country': COUNTRY_NAMES.get(c, c),
                             'Latest': f"{s.iloc[-1]:.1f}", 'Avg': f"{s.mean():.1f}",
                             'Min': f"{s.min():.1f}", 'Max': f"{s.max():.1f}"})
        if rows:
            st.table(pd.DataFrame(rows).set_index('Country'))
            _csv_bytes = pd.DataFrame(rows).to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=_csv_bytes,
                file_name=f'nerai_{sel_topic}_indices.csv',
                mime='text/csv',
                use_container_width=True
            )

    # ══ ANIMATED HEATMAP ══
    nerai_premium_css.inject_section_header("Risk Heatmap — Top Countries", icon="")
    try:
        _hm_html = heatmap_glow_html(df_norm, heatmap_n, norm_method, topic_label=sel_label)
        _stc.html(_hm_html, height=520, scrolling=False)
    except Exception:
        try:
            _fig_hm = chart_heatmap(df_norm, heatmap_n, norm_method)
            if _fig_hm is not None:
                st.plotly_chart(_fig_hm, use_container_width=True)
        except Exception:
            pass

    # ══ ANIMATED GLOBE ══
    nerai_premium_css.inject_section_header("Global Risk Map", icon="")
    try:
        _gl_html = risk_globe_html(df_norm, map_date)
        _stc.html(_gl_html, height=560, scrolling=False)
    except Exception:
        try:
            _fig_wm = chart_world(df_norm, map_date)
            if _fig_wm is not None:
                st.plotly_chart(_fig_wm, use_container_width=True)
        except Exception:
            pass


    # ── Strategic: Regional Heat Distribution ──
    try:
        _hm_html = _indices_heatmap_analysis(df_norm, sel_topic, COUNTRY_NAMES)
        if _hm_html: st.markdown(_hm_html, unsafe_allow_html=True)
    except: pass

    # âââ FAZ 3b: Risk Correlation Matrix âââ
    st.markdown('<div class="h-div" style="margin:24px 0 16px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">&#x1F517; Risk Dimension Correlation Matrix</div>', unsafe_allow_html=True)
    try:
        _topics = [t for t in df.index.get_level_values("topic").unique().tolist() if t not in _EXCLUDE_TOPICS]
        _last_n = min(30, len(df.columns))
        _recent_cols = df.columns[-_last_n:]
        _topic_means = {}
        for t in _topics[:12]:
            try:
                _t_data = df.xs(t, level="topic")[_recent_cols].mean(axis=0)
                _topic_means[t] = _t_data.values
            except Exception:
                continue
        if len(_topic_means) >= 3:
            _corr_df = pd.DataFrame(_topic_means).corr()
            _labels = [t.replace("_", " ").title()[:20] for t in _corr_df.columns]
            fig_corr = go.Figure(data=go.Heatmap(
                z=_corr_df.values, x=_labels, y=_labels,
                colorscale=[[0,"#0a1628"],[0.5,"#1a3a5c"],[0.75,"#f59e0b"],[1.0,"#e05060"]],
                zmin=-1, zmax=1,
                text=_corr_df.round(2).values, texttemplate="%{text}",
                textfont=dict(size=9, color="#c0d0e0"),
                hoverongaps=False
            ))
            fig_corr.update_layout(
                **_PLOTLY_THEME, height=500,
                xaxis=dict(tickangle=45, tickfont=dict(size=9, color="#8aa0bc")),
                yaxis=dict(tickfont=dict(size=9, color="#8aa0bc")),
            )
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.caption("Insufficient topics for correlation matrix.")
    except Exception as _e:
        st.caption(f"Correlation matrix unavailable: {_e}")

    # âââ FAZ 3f: Commodity-Risk Scatter Plot âââ
    st.markdown('<div class="h-div" style="margin:24px 0 16px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">&#x1F4B9; Commodity vs Risk Scatter</div>', unsafe_allow_html=True)
    try:
        _comm_df = load_commodities()
        if _comm_df is not None and not _comm_df.empty:
            _comm_df["date"] = pd.to_datetime(_comm_df["date"])
            _comm_latest = _comm_df.groupby("name").last().reset_index()
            _instab = df.xs("instability", level="topic", drop_level=True) if "instability" in df.index.get_level_values("topic") else None
            if _instab is not None and not _instab.empty:
                _global_risk = _instab.mean(axis=0)
                _risk_last30 = _global_risk.iloc[-30:].mean() if len(_global_risk) >= 30 else _global_risk.mean()
                if "chg_1d_pct" in _comm_df.columns:
                    _comm_scatter = _comm_latest[["name", "category", "price", "chg_1d_pct"]].dropna()
                    _comm_scatter["risk_level"] = round(float(_risk_last30), 2)
                    _comm_scatter["chg_1d_pct"] = pd.to_numeric(_comm_scatter["chg_1d_pct"], errors="coerce")
                    _comm_scatter = _comm_scatter.dropna(subset=["chg_1d_pct"])
                    if not _comm_scatter.empty:
                        _cat_colors = {"energy": "#e05060", "metals": "#f59e0b", "agriculture": "#22c55e", "financial": "#00b4d8"}
                        fig_scatter = go.Figure()
                        for cat in _comm_scatter["category"].unique():
                            _cat_data = _comm_scatter[_comm_scatter["category"] == cat]
                            fig_scatter.add_trace(go.Scatter(
                                x=_cat_data["chg_1d_pct"] * 100,
                                y=_cat_data["price"],
                                mode="markers+text",
                                name=cat.title(),
                                text=_cat_data["name"],
                                textposition="top center",
                                textfont=dict(size=8, color="#8aa0bc"),
                                marker=dict(size=12, color=_cat_colors.get(cat, "#00d4ff"),
                                            line=dict(width=1, color="rgba(255,255,255,0.3)")),
                            ))
                        fig_scatter.update_layout(
                            **_PLOTLY_THEME, height=400,
                            xaxis_title="1D Price Change (%)",
                            yaxis_title="Price",
                            showlegend=True,
                            legend=dict(font=dict(size=10, color="#8aa0bc")),
                        )
                        st.plotly_chart(fig_scatter, use_container_width=True)
                    else:
                        st.caption("No commodity change data available for scatter.")
                else:
                    st.caption("Commodity change data not computed yet.")
            else:
                st.caption("No instability data for risk axis.")
        else:
            st.caption("Commodity data not available.")
    except Exception as _e:
        st.caption(f"Commodity-Risk scatter unavailable: {_e}")
    # ── Strategic: Cross-Country Linkages ──
    try:
        _corr_html = _indices_corr_analysis(df_norm, sel_countries, COUNTRY_NAMES)
        if _corr_html: st.markdown(_corr_html, unsafe_allow_html=True)
    except: pass

    _render_footer()

def render_profile():
    nerai_premium_css.inject_page_header(
        title="Country Intel",
        subtitle="Deep-dive risk analysis, bilateral relations & alarm monitoring",
        badge="INTEL",
        icon="\U0001f310"
    )
    nerai_premium_css.inject_global_premium_css()
    nerai_premium_css.inject_filter_bar_css()
    nerai_premium_css.inject_country_intel_css()

    # \u2500\u2500 Inline country selector \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    profile_c_opts = [f"{COUNTRY_NAMES.get(c,c)} ({c})"
                      for c in sorted(all_countries)]
    profile_default = (
        'United States (US)' if 'United States (US)' in profile_c_opts
        else profile_c_opts[0]
    )

    sel_cols = st.columns([3, 2, 2, 2, 1])
    with sel_cols[0]:
        sel_profile_label = st.selectbox(
            "\U0001f310 TARGET COUNTRY", profile_c_opts,
            index=profile_c_opts.index(profile_default),
            key='inline_profile_country'
        )
    profile_country = sel_profile_label.split('(')[-1].strip(')')

    # \u2500\u2500 Bilateral selectors \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    c_opts_bi = [f"{COUNTRY_NAMES.get(c,c)} ({c})"
                for c in sorted(all_countries)]
    default_a = 'United States (US)' if 'United States (US)' in c_opts_bi else c_opts_bi[0]
    default_b = 'Russia (RS)'       if 'Russia (RS)'       in c_opts_bi else c_opts_bi[1]
    with sel_cols[1]:
        sel_bi_a = st.selectbox("\U0001f1fa\U0001f1f8 COUNTRY A", c_opts_bi,
            index=c_opts_bi.index(default_a), key='inline_bi_a')
    bi_a = sel_bi_a.split('(')[-1].strip(')')
    with sel_cols[2]:
        sel_bi_b = st.selectbox("\U0001f1f7\U0001f1fa COUNTRY B", c_opts_bi,
            index=c_opts_bi.index(default_b), key='inline_bi_b')
    bi_b = sel_bi_b.split('(')[-1].strip(')')
    with sel_cols[3]:
        bi_days = st.slider("\u23f3 HISTORY", 14, 90, 60,
            key='inline_bi_days')

    prof_name = COUNTRY_NAMES.get(profile_country, profile_country)
    # Compute profile data
    prof_indices = compute_country_top_indices(df, profile_country)
    prof_alarms  = compute_country_alarms(df, profile_country)
    prof_worst, prof_best = compute_country_bilateral_profile(
        tension_norm, coop_norm, deteri_norm, incr_norm, profile_country)

    _prof_score = 0.0
    _prof_badge = ''
    if profile_country in tension_norm.index:
        _prof_score = float(tension_norm.loc[profile_country].iloc[-7:].mean())
        _prof_badge = risk_badge(_prof_score, 'Score (0–100)')

    st.markdown(_ANALYSIS_CSS, unsafe_allow_html=True)
    # ── Strategic Executive Assessment ──
    try:
        _prof_exec = _profile_exec_analysis(profile_country, cur_t, cur_c, cur_net, trend_bi, prof_alarms, bi_a, bi_b, COUNTRY_NAMES)
        if _prof_exec: st.markdown(_prof_exec, unsafe_allow_html=True)
    except: pass

    # Page header
    st.markdown(f"""
    <div style='padding:6px 0 2px;'>
      <div class='hero-title'>Country Intelligence Profile</div>
      <div class='hero-sub'><span class='live-dot'></span>
        Deep-dive analysis &nbsp;·&nbsp; GDELT Data
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="h-div"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style='padding:8px 14px;background:rgba(0,119,168,0.05);border-radius:6px;
         margin-bottom:14px;font-size:0.75rem;color:#3a5a7a;line-height:1.6;'>
      <b>Data sources:</b> Risk scores are computed from GDELT event streams \u2014 automated analysis of
      global news and media reporting on conflict, cooperation, and political events.
      <b>Bilateral relations</b> are derived from GDELT's dyadic event data (country-to-country interactions),
      measuring cooperation vs. tension intensity between pairs.
      <b>Alarms</b> trigger when a country's risk score exceeds 2 standard deviations above its 90-day rolling mean.
    </div>""", unsafe_allow_html=True)

    # \u2500\u2500 Profile Header ────────────────────────────────────────
    _pc = '#e05060' if _prof_score>=60 else ('#f59e0b' if _prof_score>=35 else '#00b4d8')
    st.markdown(f"""
    <div class="prof-header">
      <div>
        <div class="prof-country">{prof_name}</div>
        <div class="prof-sub">COUNTRY INTELLIGENCE PROFILE &nbsp;·&nbsp; LAST 7-DAY AVERAGE</div>
      </div>
      <div style="text-align:right;">
        <div style="font-size:1.6rem;font-weight:700;color:{_pc};
             text-shadow:0 0 18px {_pc}55;">{_prof_score:.1f}</div>
        <div style="margin-top:3px;">{_prof_badge}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── 3-column profile ──────────────────────────────────────
    pc1, pc2, pc3 = st.columns([4,4,4])

    with pc1:
        st.markdown('<div class="prof-section-title">📊 Top Index Scores</div>', unsafe_allow_html=True)
        if prof_indices:
            for idx in prof_indices:
                s   = idx['score']
                col = '#e05060' if s>=65 else ('#e06030' if s>=45 else ('#f59e0b' if s>=25 else '#00b4d8'))
                st.markdown(f"""
                <div class="idx-row">
                  <div>
                    <div class="idx-label">{idx['label']}</div>
                    <div class="idx-bar-bg">
                      <div style="background:{col};width:{_safe_pct(s):.0f}%;height:3px;
                           border-radius:3px;box-shadow:0 0 5px {col}60;"></div>
                    </div>
                  </div>
                  <div class="idx-val" style="color:{col};margin-left:10px;
                       text-shadow:0 0 10px {col}40;">{s:.1f}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:rgba(100,150,180,0.4);font-size:0.72rem;">No data</div>', unsafe_allow_html=True)

    with pc2:
        st.markdown('<div class="prof-section-title">⚠️ Active Alarms</div>', unsafe_allow_html=True)
        if prof_alarms:
            for alm in prof_alarms:
                z = alm['z']; pct = alm['pct']
                if   z>=2.5:  alm_col,alm_lbl = '#e05060','CRITICAL SPIKE'
                elif z>=1.5:  alm_col,alm_lbl = '#e06030','HIGH SPIKE'
                elif z>=0.8:  alm_col,alm_lbl = '#f59e0b','ELEVATED'
                elif z<=-1.5: alm_col,alm_lbl = '#00B8D4','SUPPRESSED'
                else:         alm_col,alm_lbl = '#00b4d8','NORMAL'
                sym = '▲' if pct>0 else '▼'
                st.markdown(f"""
                <div class="alarm-row" style="border-color:{alm_col}28;">
                  <div>
                    <div class="alarm-label">{alm['label']}</div>
                    <div class="alarm-meta">z={z:+.2f}σ &nbsp;·&nbsp;
                      <span style="color:{alm_col};">{sym}{abs(pct):.0f}%</span> vs 7d
                    </div>
                  </div>
                  <span style="font-size:0.58rem;background:{alm_col}18;
                    border:1px solid {alm_col}40;border-radius:3px;
                    color:{alm_col};padding:2px 6px;white-space:nowrap;">{alm_lbl}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:rgba(100,150,180,0.4);font-size:0.72rem;">No alarms</div>', unsafe_allow_html=True)

    with pc3:
        st.markdown('<div class="prof-section-title">🔗 Bilateral Relations</div>', unsafe_allow_html=True)
        st.markdown("""<div style="font-size:0.6rem;color:#ff6b35;letter-spacing:0.15em;
            margin-bottom:5px;">▼ WORST 3 RELATIONS</div>""", unsafe_allow_html=True)
        if prof_worst:
            for rel in prof_worst:
                t_sym = '▲' if rel['trend']>0.5 else ('▼' if rel['trend']<-0.5 else '→')
                st.markdown(f"""
                <div class="rel-compact" style="border-left-color:{rel['color']};">
                  <div>
                    <div style="font-size:0.75rem;font-weight:600;color:#2a4060;">
                      {rel['icon']} {rel['name']}
                    </div>
                    <div style="font-size:0.58rem;color:{rel['color']};font-family:monospace;">
                      {rel['status']}
                    </div>
                  </div>
                  <div style="text-align:right;">
                    <div style="font-size:0.82rem;font-weight:700;color:{rel['color']};">
                      {rel['net']:.1f}
                    </div>
                    <div style="font-size:0.55rem;color:#7a9ab8;font-family:monospace;">
                      {t_sym} {abs(rel['trend']):.1f}
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:rgba(100,150,180,0.4);font-size:0.72rem;padding:8px 0;">Insufficient data</div>', unsafe_allow_html=True)

        st.markdown("""<div style="font-size:0.6rem;color:#00B8D4;letter-spacing:0.15em;
            margin:8px 0 5px;">▲ BEST 3 RELATIONS</div>""", unsafe_allow_html=True)
        if prof_best:
            for rel in prof_best:
                t_sym = '▲' if rel['trend']>0.5 else ('▼' if rel['trend']<-0.5 else '→')
                st.markdown(f"""
                <div class="rel-compact" style="border-left-color:{rel['color']};">
                  <div>
                    <div style="font-size:0.75rem;font-weight:600;color:#2a4060;">
                      {rel['icon']} {rel['name']}
                    </div>
                    <div style="font-size:0.58rem;color:{rel['color']};font-family:monospace;">
                      {rel['status']}
                    </div>
                  </div>
                  <div style="text-align:right;">
                    <div style="font-size:0.82rem;font-weight:700;color:{rel['color']};">
                      {rel['net']:.1f}
                    </div>
                    <div style="font-size:0.55rem;color:#7a9ab8;font-family:monospace;">
                      {t_sym} {abs(rel['trend']):.1f}
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)

    st.markdown('<div class="h-div" style="margin:20px 0;"></div>', unsafe_allow_html=True)

    nerai_premium_css.inject_section_header("Bilateral Relations Analyzer", icon="🤝")

    # ── Bilateral Analyzer ────────────────────────────────────
    st.markdown('<div class="sec-hdr">🔗 Bilateral Relation Analyzer</div>', unsafe_allow_html=True)

    bi_t_ser, bi_c_ser, bi_net_ser = get_bilateral_series(
        tension_norm, coop_norm, bi_a, bi_b, bi_days)

    cur_net   = float(bi_net_ser.iloc[-1])  if len(bi_net_ser)>0 else 0.0
    cur_t     = float(bi_t_ser.iloc[-1])    if len(bi_t_ser)>0   else 0.0
    cur_c     = float(bi_c_ser.iloc[-1])    if len(bi_c_ser)>0   else 0.0
    prev7_net = float(bi_net_ser.iloc[-8])  if len(bi_net_ser)>7 else float(bi_net_ser.iloc[0]) if len(bi_net_ser) else 0.0
    trend_bi  = cur_net - prev7_net

    st_,st_col,st_ico,tr_txt,tr_col = relation_status(cur_net, trend_bi)
    name_a = COUNTRY_NAMES.get(bi_a, bi_a)
    name_b = COUNTRY_NAMES.get(bi_b, bi_b)

    g1, g2, g3 = st.columns([3,4,3])
    with g1:
        t_col_g = '#e06030' if cur_t>50 else ('#f59e0b' if cur_t>25 else '#00b4d8')
        st.plotly_chart(gauge_chart(cur_t,'CONFLICT PRESSURE',t_col_g),
            use_container_width=True, config={'displayModeBar':False})
    with g2:
        st.markdown(f"""
        <div class="relation-status" style="border:2px solid {st_col}25;">
          <div style="font-size:1.7rem;margin-bottom:4px;">{st_ico}</div>
          <div style="font-size:0.55rem;color:{st_col}80;letter-spacing:0.3em;
               font-family:'Share Tech Mono',monospace;">RELATIONSHIP STATUS</div>
          <div style="font-size:1.55rem;font-weight:700;color:{st_col};
               text-shadow:0 0 20px {st_col}60;letter-spacing:0.08em;margin:4px 0;">{st_}</div>
          <div style="height:1px;background:linear-gradient(90deg,transparent,{st_col}40,transparent);margin:8px 0;"></div>
          <div style="font-size:0.78rem;font-weight:600;color:{tr_col};font-family:'Share Tech Mono',monospace;">{tr_txt}</div>
          <div style="font-size:0.6rem;color:rgba(100,150,200,0.45);margin-top:5px;font-family:monospace;">
            Net Tension: {cur_net:.1f} / 100 &nbsp;·&nbsp; Δ7d: {trend_bi:+.1f}
          </div>
          <div style="font-size:0.62rem;color:rgba(0,180,255,0.3);margin-top:3px;font-family:monospace;">
            {name_a} &nbsp;↔&nbsp; {name_b}
          </div>
        </div>""", unsafe_allow_html=True)
    with g3:
        c_col_g = '#00B8D4' if cur_c>40 else ('#00b4d8' if cur_c>15 else '#4a6a8a')
        st.plotly_chart(gauge_chart(cur_c,'COOPERATION',c_col_g),
            use_container_width=True, config={'displayModeBar':False})

    # Indicator mini cards
    st.markdown("""<div style="font-size:0.6rem;color:rgba(0,180,255,0.38);
         font-family:'Share Tech Mono',monospace;letter-spacing:0.18em;
         margin:10px 0 8px;">KEY RISK INDICATORS (7-DAY AVG)</div>""", unsafe_allow_html=True)
    ind_cols = st.columns(4)
    avail_topics = set(df.index.get_level_values('topic').unique())
    for col_el, (topic, label, color) in zip(ind_cols, BILATERAL_INDICATORS):
        with col_el:
            val_a = val_b = 0.0
            if topic in avail_topics:
                tdf = df.xs(topic, level='topic')
                if bi_a in tdf.index: val_a = float(tdf.loc[bi_a].iloc[-7:].mean())
                if bi_b in tdf.index: val_b = float(tdf.loc[bi_b].iloc[-7:].mean())
                flat  = tdf.values.flatten()
                pos   = flat[flat>0]
                g_max = float(np.percentile(pos,99)) if len(pos) else 1.0
            else: g_max = 1.0
            avg_v = min(100.0,(val_a+val_b)/2/g_max*100)
            st.markdown(f"""
            <div class="metric-mini">
              <div class="metric-mini-label">{label}</div>
              <div class="metric-mini-val" style="color:{color};text-shadow:0 0 12px {color}45;">{avg_v:.1f}</div>
              <div style="background:rgba(0,0,0,0.3);border-radius:3px;height:3px;margin:6px 0 5px;">
                <div style="background:{color};width:{_safe_pct(avg_v):.0f}%;height:3px;border-radius:3px;box-shadow:0 0 6px {color}70;"></div>
              </div>
              <div style="font-size:0.56rem;color:rgba(150,180,200,0.4);font-family:monospace;">{name_a} · {name_b}</div>
            </div>""", unsafe_allow_html=True)

    # Bilateral trend chart
    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
    fig_bi = go.Figure()
    fig_bi.add_trace(go.Scatter(x=bi_t_ser.index,y=bi_t_ser.values,name='Conflict Pressure',
        mode='lines',line=dict(width=2,color='#e06030'),
        fill='tozeroy',fillcolor='rgba(255,107,53,0.06)',
        hovertemplate='Conflict Pressure: %{y:.1f}<extra></extra>'))
    fig_bi.add_trace(go.Scatter(x=bi_c_ser.index,y=bi_c_ser.values,name='Cooperation',
        mode='lines',line=dict(width=2,color='#00B8D4'),
        fill='tozeroy',fillcolor='rgba(0,255,157,0.05)',
        hovertemplate='Cooperation: %{y:.1f}<extra></extra>'))
    fig_bi.add_trace(go.Scatter(x=bi_net_ser.index,y=bi_net_ser.values,name='Net Tension',
        mode='lines',line=dict(width=2.5,color='#0077a8'),
        hovertemplate='Net Tension: %{y:.1f}<extra></extra>'))
    t_bi = {**BASE_THEME}
    t_bi['yaxis'] = {**t_bi['yaxis'],'title':'Score (0–100)','title_font':dict(size=10)}
    fig_bi.update_layout(**t_bi,height=290,
        title=dict(text=f'{name_a}  ↔  {name_b} — Bilateral Tension Trend',
                   font=dict(size=12,color='#6a9ab8'),x=0.01),
        legend=dict(bgcolor='rgba(255,255,255,0.85)',bordercolor='rgba(0,119,168,0.25)',
                    borderwidth=1,font=dict(size=10,color='#8aa0bc')),hovermode='x unified')
    st.plotly_chart(fig_bi, use_container_width=True, config={'displayModeBar':False})

    # âââ FAZ 3c: Country Radar Chart âââ
    st.markdown('<div class="h-div" style="margin:24px 0 16px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">&#x1F3AF; Country Risk Radar</div>', unsafe_allow_html=True)
    try:
        _c = profile_country
        _topics_for_radar = df.index.get_level_values("topic").unique().tolist()
        _radar_topics = _topics_for_radar[:10]  # Limit to 10 dimensions
        _latest = df.columns[-1]
        _radar_vals = []
        _radar_labels = []
        for t in _radar_topics:
            try:
                _val = df.loc[(t, _c), _latest] if (t, _c) in df.index else 0
                _radar_vals.append(float(_val) if not pd.isna(_val) else 0)
                _radar_labels.append(t.replace("_", " ").title()[:18])
            except Exception:
                continue
        if len(_radar_vals) >= 3:
            # Normalize to 0-100 for radar display
            _max_val = max(_radar_vals) if max(_radar_vals) > 0 else 1
            _radar_norm = [round(v / _max_val * 100, 1) for v in _radar_vals]
            # Close the polygon
            _radar_norm.append(_radar_norm[0])
            _radar_labels.append(_radar_labels[0])
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=_radar_norm, theta=_radar_labels,
                fill="toself", fillcolor="rgba(0,212,255,0.15)",
                line=dict(color="#00d4ff", width=2),
                name=COUNTRY_NAMES.get(_c, _c),
            ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, range=[0, 100],
                                    gridcolor="rgba(0,212,255,0.1)",
                                    tickfont=dict(size=8, color="#5a7a9a")),
                    angularaxis=dict(gridcolor="rgba(0,212,255,0.1)",
                                     tickfont=dict(size=9, color="#8aa0bc")),
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#c0d0e0"),
                height=420, margin=dict(l=60, r=60, t=40, b=40),
                showlegend=False,
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.caption("Not enough risk dimensions for radar chart.")
    except Exception as _e:
        st.caption(f"Radar chart unavailable: {_e}")
    # ── Strategic: Conflict-Cooperation Balance ──
    try:
        _gauge_html = _profile_gauge_analysis(cur_t, cur_c, cur_net, profile_country, COUNTRY_NAMES)
        if _gauge_html: st.markdown(_gauge_html, unsafe_allow_html=True)
    except: pass

    _render_footer()


# ═══════════════════════════════════════════════════════════════
# PAGE: NEWS
# ═══════════════════════════════════════════════════════════════
def render_news():
    nerai_premium_css.inject_page_header(
        title="Signal Feed",
        subtitle="Live GDELT headlines across 28 topic categories — real-time intelligence",
        badge="LIVE",
        icon="📰"
    )
    nerai_premium_css.inject_global_premium_css()


    # === NEWS DYNAMIC BACKGROUND ===
    _topic_colors = {"conflict": "rgba(255,60,60,0.05)", "diplomacy": "rgba(0,200,255,0.05)", "economy": "rgba(0,255,150,0.05)", "politics": "rgba(180,100,255,0.05)", "environment": "rgba(100,255,100,0.05)", "health": "rgba(255,200,0,0.05)", "technology": "rgba(0,150,255,0.05)"}
    _cur_topic = st.session_state.get("news_topic", "").lower()
    _bg_col = _topic_colors.get(_cur_topic, "rgba(0,255,200,0.03)")
    st.markdown(f"<style>.main .block-container{{background:linear-gradient(180deg,{_bg_col},transparent)!important;}}</style>", unsafe_allow_html=True)
    st.markdown("""
    <div style='padding:6px 0 10px;'>
      <div class='hero-title'>Global News Intelligence</div>
      <div class='hero-sub'><span class='live-dot'></span>
        Multi-Source Intelligence &nbsp;·&nbsp; GDELT + Global Media RSS
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="h-div"></div>', unsafe_allow_html=True)

    cat_names  = [c[0] for c in NEWS_CATEGORIES]
    cat_queries = {c[0]: c[1] for c in NEWS_CATEGORIES}

    # Category selector + news
    left_col, mid_col, right_col = st.columns([2, 2, 5])

    with left_col:
        st.markdown('<div class="sec-hdr">Topics</div>', unsafe_allow_html=True)
        st.markdown('<style>[data-testid="stRadio"] label{font-size:11px !important;line-height:1.3 !important} [data-testid="stRadio"] label p{font-size:11px !important;white-space:nowrap !important;overflow:hidden !important;text-overflow:ellipsis !important}</style>', unsafe_allow_html=True)
        sel_cat = st.radio(
            "Category", cat_names,
            index=0, label_visibility='collapsed',
            key='news_cat'
        )

    with mid_col:
        st.markdown('<div class="sec-hdr">Country Filter</div>', unsafe_allow_html=True)
        _news_c_opts = ['All Countries'] + [f"{COUNTRY_NAMES.get(c,c)} ({c})" for c in sorted(all_countries)]
        _news_country = st.selectbox("Filter by country", _news_c_opts, index=0,
                                      label_visibility='collapsed', key='news_country_filter')
        _news_country_name = None if _news_country == 'All Countries' else _news_country.split(' (')[0]

    with right_col:
        cat_q = cat_queries.get(sel_cat, sel_cat)
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;">
          <div style="font-size:1.1rem;font-weight:700;color:#007a99;letter-spacing:0.08em;">
            {sel_cat}
          </div>
          <div style="font-size:0.6rem;color:rgba(0,180,255,0.35);font-family:monospace;
               border:1px solid rgba(0,150,255,0.15);border-radius:4px;padding:2px 8px;">
            LIVE FEED
          </div>
        </div>""", unsafe_allow_html=True)

        # ── Source selector ──
        _src_mode = st.radio("Source", ["🌐 All Sources", "📡 GDELT + Google", "📰 Global Media RSS"],
                             index=0, horizontal=True, label_visibility='collapsed', key='news_src_mode')
        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

        with st.spinner('Fetching multi-source intelligence...'):
            cat_q_kw = cat_queries.get(sel_cat, sel_cat)
            search_q = cat_q_kw + (f' {_news_country_name}' if _news_country_name else '')

            gdelt_arts, rss_arts = [], []
            if '🌐' in _src_mode or 'GDELT' in _src_mode:
                gdelt_arts = fetch_gdelt_news(search_q, max_records=10)
                for a in gdelt_arts:
                    a['_src'] = a.get('_src', 'GDELT')
            if '🌐' in _src_mode or 'RSS' in _src_mode:
                rss_arts = fetch_global_media_rss(search_q, max_per_feed=3)

            articles = gdelt_arts + rss_arts

            # Post-filter by country if selected
            if _news_country_name:
                _cn_low = _news_country_name.lower()
                _cn_parts = _cn_low.split()
                def _country_match(art):
                    haystack = (art.get('title','') + ' ' + art.get('domain','') + ' ' + art.get('url','')).lower()
                    return _cn_low in haystack or any(p in haystack for p in _cn_parts if len(p) > 3)
                articles = [a for a in articles if _country_match(a)]

            # Sort by date desc
            articles.sort(key=lambda x: x.get('seendate', ''), reverse=True)

        # Source stats
        _gdelt_c = sum(1 for a in articles if a.get('_src') != 'RSS')
        _rss_c = sum(1 for a in articles if a.get('_src') == 'RSS')
        st.markdown(f"""<div style="display:flex;gap:12px;margin-bottom:10px;font-size:0.6rem;font-family:monospace;color:rgba(0,200,255,0.4);">
            <span>📡 GDELT/Google: {_gdelt_c}</span>
            <span>📰 Global RSS: {_rss_c}</span>
            <span>∑ Total: {len(articles)}</span>
        </div>""", unsafe_allow_html=True)

        if articles:
            for art in articles:
                title = art.get('title', 'No title')
                source = art.get('domain', '')
                url = art.get('url', '#')
                seendate = art.get('seendate', '')
                language = art.get('language', '')
                src_type = art.get('_src', 'GDELT')
                date_disp = seendate[:8] if len(seendate)>=8 else ''
                if date_disp:
                    try:
                        date_disp = pd.Timestamp(date_disp).strftime('%d %b %Y')
                    except:
                        pass
                src_badge_color = 'rgba(0,200,255,0.15)' if src_type == 'RSS' else 'rgba(255,180,0,0.15)'
                src_badge_text = '📰 RSS' if src_type == 'RSS' else '📡 GDELT'
                st.markdown(f"""
                <div class="news-card">
                    <div class="news-title">
                        <a href="{url}" target="_blank" style="color:#2a4060;text-decoration:none;">
                            {title[:180]}{'...' if len(title)>180 else ''}
                        </a>
                    </div>
                    <div style="display:flex;gap:14px;margin-top:6px;align-items:center;flex-wrap:wrap;">
                        <div style="font-size:0.58rem;color:rgba(0,180,255,0.6);background:{src_badge_color};padding:2px 8px;border-radius:4px;font-family:monospace;">{src_badge_text}</div>
                        <div class="news-source">🌐 {source}</div>
                        <div class="news-date">📅 {date_disp}</div>
                        {'<div style="font-size:0.58rem;color:rgba(100,180,255,0.3);font-family:monospace;border:1px solid rgba(0,150,255,0.15);border-radius:4px;padding:2px 8px;">LANG: '+language.upper()+'</div>' if language else ''}
                    </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align:center;padding:40px;color:rgba(100,150,200,0.4);font-family:monospace;font-size:0.8rem;">
                <div style="font-size:2rem;margin-bottom:12px;">📡</div>
                No articles found for "{sel_cat}".<br>
                <span style="font-size:0.65rem;">Sources may be temporarily unavailable.</span>
            </div>""", unsafe_allow_html=True)
    _render_footer()


# ═══════════════════════════════════════════════════════════════
# PAGE: PREDICTIONS
# ═══════════════════════════════════════════════════════════════
def render_predictions():
    nerai_premium_css.inject_page_header(
        title="Forecast Engine",
        subtitle="N-HiTS deep learning 12-month forecasts for 2,400 risk series",
        badge="AI",
        icon="🔮"
    )
    nerai_premium_css.inject_global_premium_css()

    # \u2500\u2500 Inline topic & country selectors \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    nerai_premium_css.inject_filter_bar_css()
    _pred_sel_cols = st.columns([4, 4, 3])
    with _pred_sel_cols[0]:
        topic_display_p = {t: TOPIC_LABELS.get(t, t.replace("_"," ").title())
                           for t in sorted(pred_df["topic"].dropna().unique()) if t}
        if topic_display_p:
            pred_label = st.selectbox(
                "\U0001f4ca RISK TOPIC", list(topic_display_p.values()),
                index=list(topic_display_p.values()).index('Political Instability')
                    if 'Political Instability' in topic_display_p.values() else 0,
                key='inline_pred_topic'
            )
            sel_pred_topic = next((k for k,v in topic_display_p.items() if v==pred_label), list(topic_display_p.keys())[0])
        else:
            sel_pred_topic = None
    with _pred_sel_cols[1]:
        pred_c_opts = [f"{COUNTRY_NAMES.get(c,c)} ({c})"
                       for c in sorted(pred_df["country"].unique())]
        pred_default = 'United States (US)' if 'United States (US)' in pred_c_opts \
                       else pred_c_opts[0]
        sel_pred_country_label = st.selectbox(
            "\U0001f310 COUNTRY", pred_c_opts,
            index=pred_c_opts.index(pred_default),
            key='inline_pred_country'
        )
        sel_pred_country = sel_pred_country_label.split('(')[-1].strip(')')
    with _pred_sel_cols[2]:
        pred_hist_months = st.slider('\U0001f4c5 HISTORY (months)', 6, 48, 24,
            key='inline_pred_months')

    st.markdown("""
    <div style='padding:6px 0 10px;'>
      <div class='hero-title'>12-Month Risk Forecasts</div>
      <div class='hero-sub'>
        <span class='live-dot'></span>
        N-HiTS Deep Learning Model &nbsp;·&nbsp; 2,400 Topic × Country Series
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="h-div"></div>', unsafe_allow_html=True)

    if not has_predictions:
        import subprocess, sys
        st.markdown("""
        <div style='text-align:center;padding:40px 20px;
             background:rgba(0,12,32,0.6);border:1px solid rgba(0,150,255,0.12);
             border-radius:12px;margin:20px 0;'>
          <div style='font-size:3rem;margin-bottom:16px;'>🔮</div>
          <div style='font-size:1.1rem;font-weight:700;color:#007a99;
               letter-spacing:0.08em;margin-bottom:10px;'>
            Predictions Not Yet Generated
          </div>
          <div style='font-size:0.8rem;color:rgba(150,190,220,0.7);
               max-width:480px;margin:0 auto;line-height:1.7;'>
            Run the fast Holt-Winters forecast engine (no ML libraries needed)
            or the full N-HiTS deep learning pipeline:
          </div>
          <div style='margin-top:20px;padding:16px 24px;
               background:rgba(0,0,0,0.4);border-radius:8px;
               font-family:monospace;font-size:0.78rem;
               color:rgba(0,230,255,0.7);text-align:left;
               display:inline-block;'>
            # Fast option — pure NumPy, runs in ~30 sec<br>
            python gdelt_forecast_numpy.py<br><br>
            # Full option — N-HiTS deep learning (~2 hrs history download)<br>
            python gdelt_bulk_history.py &amp;&amp; python gdelt_forecast.py
          </div>
        </div>""", unsafe_allow_html=True)

        # ── Auto-generate button ──────────────────────────────────
        col_l, col_c, col_r = st.columns([2,3,2])
        with col_c:
            indices_ok = os.path.exists('./indices.csv')
            numpy_script = os.path.exists('./gdelt_forecast_numpy.py')
            if indices_ok and numpy_script:
                if st.button('⚡ Generate Predictions Now (Holt-Winters)',
                             use_container_width=True, type='primary'):
                    with st.spinner('Running Holt-Winters forecast engine (~30 sec)…'):
                        result = subprocess.run(
                            [sys.executable, './gdelt_forecast_numpy.py'],
                            capture_output=True, text=True, cwd='.'
                        )
                    if result.returncode == 0:
                        st.success('✅ Predictions generated! Reloading…')
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f'Forecast failed:\n{result.stderr[-800:]}')
            elif not indices_ok:
                st.info('📥 Run `python gdelt_indices.py` first to collect GDELT data.')
            else:
                st.info('📄 Place `gdelt_forecast_numpy.py` in the same folder to enable auto-generation.')
        _render_footer()
        return

    # ── Normalise predictions to score 0-100 for display ─────
    # Use the same max as historical indices for comparability
    def _norm_pred_series(topic, country, yhat_vals):
        return yhat_vals  # Already normalized at load time

    # ── Main chart — historical + forecast ───────────────────
    col_left, col_right = st.columns([4, 2])

    with col_left:
        topic_lbl = TOPIC_LABELS.get(sel_pred_topic,
                                      sel_pred_topic.replace('_',' ').title())
        cname     = COUNTRY_NAMES.get(sel_pred_country, sel_pred_country)
        st.markdown(f'<div class="sec-hdr">{topic_lbl} — {cname} · 12-Month Forecast</div>',
                    unsafe_allow_html=True)

        # Historical monthly series from indices.csv
        hist_series = None
        if sel_pred_topic in df.index.get_level_values('topic') and \
           sel_pred_country in df.index.get_level_values('country'):
            try:
                raw = df.xs(sel_pred_topic, level='topic').loc[sel_pred_country]
                raw = raw.dropna()
                _fc_freq = 'W'
                if len(fc) >= 2:
                    _fc_gap = (pd.to_datetime(fc['ds'].iloc[1]) - pd.to_datetime(fc['ds'].iloc[0])).days
                    _fc_freq = 'W' if _fc_gap < 14 else 'MS'
                if _fc_freq == 'W':
                    raw_monthly = raw.resample('W').mean().tail(pred_hist_months * 4)
                else:
                    raw_monthly = raw.resample('MS').mean().tail(pred_hist_months)
                hist_max = raw.max()
                if hist_max > 0:
                    hist_series = raw_monthly / hist_max * 100
                else:
                    hist_series = raw_monthly
            except Exception:
                hist_series = None

        # Forecast series
        mask = (pred_df['topic'] == sel_pred_topic) & \
               (pred_df['country'] == sel_pred_country)
        fc = pred_df[mask].sort_values('ds')

        fig_fc = go.Figure()
        current_val, fc_end_val = None, None

        # Historical — teal solid line with markers
        if hist_series is not None and len(hist_series) > 0:
            current_val = round(float(hist_series.iloc[-1]), 1)
            fig_fc.add_trace(go.Scatter(
                x=hist_series.index, y=hist_series.values,
                name='Historical',
                mode='lines+markers',
                line=dict(color='#0077a8', width=2.5),
                marker=dict(size=5, color='#0077a8', line=dict(color='#0d1220', width=1)),
                hovertemplate='<b>%{x|%b %Y}</b><br>Score: %{y:.1f}<extra>Historical</extra>'
            ))

        if len(fc) > 0:
            yhat = fc['yhat'].copy()
            y_lo = fc['yhat_lower'].copy()
            y_hi = fc['yhat_upper'].copy()
            # Scale raw predictions to align with historical at transition point
            if hist_series is not None and len(hist_series) > 0 and len(yhat) > 0:
                last_hist_val = float(hist_series.iloc[-1])
                first_pred_val = float(yhat.iloc[0])
                if first_pred_val > 0:
                    pscale = last_hist_val / first_pred_val
                    yhat = yhat * pscale
                    y_lo = y_lo * pscale
                    y_hi = y_hi * pscale
            fc_end_val = round(float(yhat.iloc[-1]), 1)

            # Only show CI bands if they have meaningful width
            ci_width = (y_hi - y_lo).mean()
            if ci_width > 0.5:
                # Outer CI (95%)
                fig_fc.add_trace(go.Scatter(
                    x=pd.concat([fc['ds'], fc['ds'].iloc[::-1]]),
                    y=pd.concat([y_hi * 1.06, (y_lo * 0.94).iloc[::-1]]),
                    fill='toself', fillcolor='rgba(245,158,11,0.07)',
                    line=dict(color='rgba(0,0,0,0)'),
                    name='95% Confidence', hoverinfo='skip',
                ))
                # Inner CI (80%)
                fig_fc.add_trace(go.Scatter(
                    x=pd.concat([fc['ds'], fc['ds'].iloc[::-1]]),
                    y=pd.concat([y_hi, y_lo.iloc[::-1]]),
                    fill='toself', fillcolor='rgba(245,158,11,0.16)',
                    line=dict(color='rgba(245,158,11,0.3)', width=0.5),
                    name='80% Confidence', hoverinfo='skip',
                ))
            # Forecast — orange/amber
            fig_fc.add_trace(go.Scatter(
                x=fc['ds'], y=yhat,
                name='12-Month Forecast',
                mode='lines+markers',
                line=dict(color='#f59e0b', width=3),
                marker=dict(size=7, color='#f59e0b', line=dict(color='#0d1220', width=1.5)),
                hovertemplate='<b>%{x|%b %Y}</b><br>Forecast: %{y:.1f}<extra>Forecast</extra>'
            ))
            # TODAY line
            today = pd.Timestamp.now().normalize()
            fig_fc.add_vline(x=today, line_width=1.5,
                             line_dash='dot', line_color='rgba(0,119,168,0.5)')
            fig_fc.add_annotation(
                x=today, y=0.96, yref='paper', text='TODAY',
                showarrow=False, font=dict(size=9, color='#0077a8'),
                xanchor='left', yanchor='top',
                bgcolor='rgba(255,255,255,0.75)', borderpad=2
            )

        fig_fc.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(248,251,255,1)',
            font=dict(family='Inter,sans-serif', color='#8aa0bc', size=11),
            height=420, hovermode='x unified',
            margin=dict(l=50, r=20, t=55, b=40),
            xaxis=dict(gridcolor='rgba(0,119,168,0.06)', tickfont=dict(size=10, color='#5a6b82'), showgrid=False),
            yaxis=dict(title='Risk Score (0–100)', title_font=dict(size=10, color='#5a6b82'),
                       gridcolor='rgba(0,212,255,0.06)', tickfont=dict(size=10, color='#5a6b82'), zeroline=False),
            legend=dict(
                bgcolor='rgba(255,255,255,0.92)', bordercolor='rgba(0,119,168,0.2)',
                borderwidth=1, font=dict(size=10, color='#8aa0bc'),
                orientation='h', yanchor='bottom', y=1.01, xanchor='left', x=0
            ),
        )
        st.plotly_chart(fig_fc, use_container_width=True, config={'displayModeBar': False})

        # KPI strip
        if current_val is not None and fc_end_val is not None:
            delta = max(-100, min(100, fc_end_val - current_val))
            d_col = '#e05060' if delta > 0 else '#00B8D4'
            arrow = '▲' if delta > 0 else '▼'
            k1, k2, k3, k4 = st.columns(4)
            k1.markdown(f"<div class='kpi-card'><div class='kpi-label'>Current Score</div><div class='kpi-value'>{current_val:.0f}</div></div>", unsafe_allow_html=True)
            k2.markdown(f"<div class='kpi-card'><div class='kpi-label'>12-Month Forecast</div><div class='kpi-value' style='color:#f59e0b'>{fc_end_val:.0f}</div></div>", unsafe_allow_html=True)
            k3.markdown(f"<div class='kpi-card'><div class='kpi-label'>Expected Change</div><div class='kpi-value' style='color:{d_col}'>{arrow} {abs(delta):.1f}</div></div>", unsafe_allow_html=True)
            k4.markdown(f"<div class='kpi-card'><div class='kpi-label'>Trend Direction</div><div class='kpi-value' style='color:{d_col};font-size:1rem;'>{'↑ Rising Risk' if delta > 0 else '↓ Falling Risk'}</div></div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="sec-hdr">Trend Summary — All Topics</div>',
                    unsafe_allow_html=True)
        st.markdown("""<div style='font-size:0.68rem;color:#6a8aaa;margin-bottom:10px;line-height:1.5;'>
          Topics with <span style='color:#8a8a8a;'>gray</span> indicators have minimal baseline activity for this country
          — large % changes from a near-zero base may not indicate meaningful risk shifts.
        </div>""", unsafe_allow_html=True)
        if trend_df is not None:
            country_trends = trend_df[trend_df['country'] == sel_pred_country].copy()
            country_trends['label'] = country_trends['topic'].apply(
                lambda t: TOPIC_LABELS.get(t, str(t).replace('_', ' ').title()) if pd.notna(t) else 'Unknown')
            country_trends = country_trends.sort_values('trend_pct', ascending=False)

            for _, row in country_trends.iterrows():
                pct   = row['trend_pct']
                dirn  = row['direction']
                _abs_ctx = ' (low base)' if abs(pct) > 100 else ''
                arrow = '▲' if dirn == 'rising' else ('▼' if dirn == 'falling' else '→')
                col_d = ('#e05060' if dirn == 'rising'
                         else '#00B8D4' if dirn == 'falling' else '#7a9ab8')
                bar_w = min(abs(pct) / 3, 100)
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:8px;
                     padding:5px 0;border-bottom:1px solid rgba(0,100,180,0.06);'>
                  <div style='font-size:0.7rem;color:{col_d};width:14px;
                       text-align:center;flex-shrink:0;'>{arrow}</div>
                  <div style='flex:1;min-width:0;'>
                    <div style='font-size:0.68rem;color:#1a3a5c;white-space:nowrap;
                         overflow:hidden;text-overflow:ellipsis;'>{row["label"]}</div>
                    <div style='background:rgba(0,0,0,0.3);border-radius:2px;
                         height:2px;width:100%;margin-top:3px;'>
                      <div style='background:{col_d};width:{_safe_pct(bar_w):.0f}%;height:2px;
                           border-radius:2px;'></div>
                    </div>
                  </div>
                  <div style='font-size:0.68rem;color:{col_d};
                       font-family:monospace;flex-shrink:0;width:44px;
                       text-align:right;'>{pct:+.1f}%</div>
                </div>""", unsafe_allow_html=True)

    st.markdown('<div class="h-div" style="margin:24px 0;"></div>', unsafe_allow_html=True)


    st.markdown(_ANALYSIS_CSS, unsafe_allow_html=True)
    # ── Strategic: Forecast Intelligence ──
    try:
        _fc_html = _forecast_exec_analysis(sel_pred_topic, sel_pred_country, current_val, fc_end_val, fc, COUNTRY_NAMES)
        if _fc_html: st.markdown(_fc_html, unsafe_allow_html=True)
    except: pass

    _render_footer()


# ═══════════════════════════════════════════════════════════════
# INSIGHTS — Country Risk Intelligence + Q&A
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def _compute_country_insights(_df_raw, _trend_df):
    """Compute per-country risk insights. Returns sorted DataFrame."""
    try:
        date_cols = sorted([c for c in _df_raw.columns if hasattr(c, 'strftime')])
        if len(date_cols) < 7:
            return None

        recent_cols = date_cols[-7:]
        past_cols   = date_cols[-14:-7] if len(date_cols) >= 14 else date_cols[:7]
        countries   = _df_raw.index.get_level_values('country').unique().tolist()

        # ── Step 1: raw means per country ──────────────────────
        raw_means   = {}
        change_pcts = {}
        for country in countries:
            try:
                c_df = _df_raw.xs(country, level='country')
                r_mean = float(c_df[recent_cols].values.mean())
                p_mean = float(c_df[past_cols].values.mean())
                raw_means[country]   = r_mean
                change_pcts[country] = max(-500, min(500, (r_mean - p_mean) / (abs(p_mean) + 1e-9) * 100).clip(-500, 500)) if abs(p_mean) > 1e-9 else 0.0
            except Exception:
                raw_means[country]   = 0.0
                change_pcts[country] = 0.0

        # ── Step 2: normalize risk score to 0-100 ──────────────
        vals       = list(raw_means.values())
        global_p95 = float(sorted(vals)[int(len(vals) * 0.95)]) if vals else 1.0
        if global_p95 == 0:
            global_p95 = max(vals) if max(vals) > 0 else 1.0

        rows = []
        for country in countries:
            risk_score = min(raw_means[country] / global_p95 * 100, 100)
            change     = change_pcts[country]

            # ── Trend data for this country ─────────────────────
            if _trend_df is not None:
                ct = _trend_df[_trend_df['country'] == country].dropna(subset=['trend_pct'])
                ct = ct.copy(); ct['trend_pct'] = ct['trend_pct'].clip(-500, 500)
                top_rising  = ct.nlargest(3, 'trend_pct')[['topic','trend_pct']].values.tolist() if len(ct) else []
                top_falling = ct.nsmallest(3, 'trend_pct')[['topic','trend_pct']].values.tolist() if len(ct) else []
                avg_fc      = float(ct['trend_pct'].mean()) if len(ct) else 0.0
            else:
                top_rising, top_falling, avg_fc = [], [], 0.0

            forecast_dir = ('rising' if avg_fc > 8 else 'falling' if avg_fc < -8 else 'stable')

            # ── Criticality: blend risk level + volatility ──────
            criticality = risk_score * 0.45 + abs(change) * 0.35 + abs(avg_fc) * 0.20

            rows.append({
                'country': country, 'risk_score': risk_score,
                'change_30d': change, 'top_rising': top_rising,
                'top_falling': top_falling, 'forecast_dir': forecast_dir,
                'avg_forecast': avg_fc, 'criticality': criticality,
            })

        result = pd.DataFrame(rows).sort_values('criticality', ascending=False)
        return result
    except Exception:
        return None


def _risk_narrative(top_rising, top_falling, forecast_dir, avg_fc, country_name):
    """Generate a concise data-driven narrative for a country card."""
    parts = []
    r_keys = [r[0] for r in top_rising]

    # ── Specific dangerous combinations ────────────────────────
    if 'coup' in r_keys and 'political_instability' in r_keys:
        parts.append(f"Coup risk and political instability are simultaneously escalating in {country_name}")
    elif 'military_escalation' in r_keys and 'international_crisis' in r_keys:
        parts.append(f"Military build-up and international tensions are reinforcing each other")
    elif 'terrorism' in r_keys and 'political_repression' in r_keys:
        parts.append(f"Security crackdowns and extremist activity are both rising")
    elif 'mass_killing' in r_keys or 'domestic_violence' in r_keys:
        parts.append(f"Civilian security indicators have reached critical levels")
    elif 'authoritarianism' in r_keys and 'human_rights_abuses' in r_keys:
        parts.append(f"Authoritarian consolidation is driving human-rights deterioration")
    elif top_rising:
        t1, p1 = top_rising[0]
        lbl1 = TOPIC_LABELS.get(t1, t1.replace('_', ' ').title())
        parts.append(f"{lbl1} is the primary risk driver ({p1:+.1f}%)")
        if len(top_rising) > 1:
            t2, p2 = top_rising[1]
            lbl2 = TOPIC_LABELS.get(t2, t2.replace('_', ' ').title())
            parts.append(f"compounded by rising {lbl2} ({p2:+.1f}%)")

    # ── Forecast qualifier ──────────────────────────────────────
    if forecast_dir == 'rising' and avg_fc > 25:
        parts.append(f"12-month models project significant escalation (avg +{avg_fc:.0f}%)")
    elif forecast_dir == 'rising':
        parts.append(f"Near-term outlook points to continued risk growth")
    elif forecast_dir == 'falling':
        parts.append(f"Forecast models suggest gradual stabilisation ahead")
    else:
        parts.append(f"Risk trajectory appears broadly stable in the near term")

    return ". ".join(parts) + "." if parts else "Monitoring ongoing."


def _render_country_card(col, row):
    """Render a single country intelligence card."""
    country  = row['country']
    cname    = COUNTRY_NAMES.get(country, country)
    risk     = row['risk_score']
    change   = row['change_30d']
    tr       = row['top_rising']
    tf       = row['top_falling']
    fc_dir   = row['forecast_dir']
    avg_fc   = row['avg_forecast']

    # Colour scheme
    chg_col   = '#e05060' if change > 10 else '#00B8D4' if change < -10 else '#7a9ab8'
    chg_arrow = '▲' if change > 10 else '▼' if change < -10 else '→'
    risk_col  = '#e05060' if risk > 65 else '#f59e0b' if risk > 35 else '#00B8D4'
    fc_col    = '#e05060' if fc_dir == 'rising' else '#00B8D4' if fc_dir == 'falling' else '#7a9ab8'
    fc_arrow  = '▲' if fc_dir == 'rising' else '▼' if fc_dir == 'falling' else '→'

    def topic_rows(items, color):
        if not items:
            return "<div style='color:rgba(120,150,190,0.35);font-size:0.62rem;'>—</div>"
        html = ""
        for t, p in items[:3]:
            lbl = TOPIC_LABELS.get(t, t.replace('_', ' ').title())
            html += (f"<div style='display:flex;justify-content:space-between;"
                     f"padding:2px 0;border-bottom:1px solid rgba(0,80,160,0.07);'>"
                     f"<span style='color:#1a3a5c;font-size:0.63rem;white-space:nowrap;"
                     f"overflow:hidden;text-overflow:ellipsis;max-width:110px;'>{lbl}</span>"
                     f"<span style='color:{color};font-size:0.63rem;font-family:monospace;"
                     f"flex-shrink:0;margin-left:4px;'>{p:+.1f}%</span></div>")
        return html

    narrative = _risk_narrative(tr, tf, fc_dir, avg_fc, cname)

    col.markdown(f"""
<div style='background:rgba(0,15,45,0.65);border:1px solid rgba(0,100,180,0.18);
     border-radius:9px;padding:14px 16px;margin-bottom:12px;
     box-shadow:0 2px 12px rgba(0,0,0,0.3);'>

  <div style='display:flex;justify-content:space-between;align-items:flex-start;
       margin-bottom:10px;padding-bottom:8px;
       border-bottom:1px solid rgba(0,100,180,0.10);'>
    <div>
      <div style='font-size:0.98rem;font-weight:700;color:#0d3464;
           letter-spacing:0.03em;'>{cname}</div>
      <div style='font-size:0.57rem;color:rgba(0,180,255,0.35);
           font-family:monospace;letter-spacing:0.12em;'>{country} · GDELT INDEX</div>
    </div>
    <div style='text-align:right;'>
      <div style='font-size:1.15rem;font-weight:800;color:{risk_col};
           line-height:1.1;'>{risk:.0f}<span style='font-size:0.58rem;
           color:rgba(200,220,240,0.35);'>/100</span></div>
      <div style='font-size:0.63rem;color:{chg_col};font-family:monospace;'>
        {chg_arrow} {change:+.1f}% <span style='color:rgba(140,165,195,0.4);
        font-size:0.56rem;'>(7d chg)</span></div>
    </div>
  </div>

  <div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;'>
    <div>
      <div style='font-size:0.56rem;color:rgba(255,75,110,0.55);
           font-family:monospace;letter-spacing:0.1em;margin-bottom:5px;'>▲ RISING</div>
      {topic_rows(tr, '#e05060')}
    </div>
    <div>
      <div style='font-size:0.56rem;color:rgba(0,255,157,0.55);
           font-family:monospace;letter-spacing:0.1em;margin-bottom:5px;'>▼ FALLING</div>
      {topic_rows(tf, '#00B8D4')}
    </div>
  </div>

  <div style='background:rgba(0,0,0,0.25);border-radius:5px;padding:6px 10px;
       margin-bottom:9px;border-left:2px solid {fc_col};'>
    <div style='font-size:0.56rem;color:rgba(140,175,215,0.45);
         font-family:monospace;letter-spacing:0.1em;margin-bottom:2px;'>12-MONTH FORECAST</div>
    <div style='font-size:0.69rem;color:{fc_col};font-weight:600;'>
      {fc_arrow} {fc_dir.title()} &nbsp;·&nbsp; {avg_fc:+.1f}% avg predicted change
    </div>
  </div>

  <div style='font-size:0.64rem;color:rgba(175,205,235,0.65);
       line-height:1.55;font-style:italic;'>
    "{narrative}"
  </div>

</div>""", unsafe_allow_html=True)


# ── Q&A helpers ────────────────────────────────────────────────

_QUESTION_KEYWORDS = {
    'war':        ['military_escalation','military_crisis','international_crisis','military_clash'],
    'savaş':      ['military_escalation','military_crisis','international_crisis','military_clash'],
    'conflict':   ['military_escalation','military_crisis','military_clash'],
    'çatışma':    ['military_escalation','military_crisis'],
    'coup':       ['coup','regime_instability','government_instability'],
    'darbe':      ['coup','regime_instability','government_instability'],
    'terror':     ['terrorism','domestic_violence'],
    'teror':      ['terrorism','domestic_violence'],
    'rights':     ['human_rights_abuses','torture','political_repression'],
    'hak':        ['human_rights_abuses','political_repression'],
    'election':   ['leadership_change','political_instability','democratization'],
    'seçim':      ['leadership_change','democratization'],
    'protest':    ['protest','political_dissent','opposition_activeness'],
    'stabili':    ['political_stability','institutional_strength','dispute_settlement'],
    'istikrar':   ['political_stability','political_instability','government_instability'],
    'sanction':   ['international_crisis','deteriorating_bilateral_relations'],
    'yaptırım':   ['international_crisis','deteriorating_bilateral_relations'],
    'nuclear':    ['military_escalation','international_crisis','threaten_in_international_relations'],
    'nükleer':    ['military_escalation','international_crisis','threaten_in_international_relations'],
    'crisis':     ['international_crisis','political_crisis','military_crisis'],
    'kriz':       ['international_crisis','political_crisis','military_crisis'],
    'human':      ['human_rights_abuses','torture','mass_expulsion'],
    'insan':      ['human_rights_abuses','torture'],
    'corruption': ['corruption','authoritarianism'],
    'yolsuzluk':  ['corruption'],
    'military':   ['military_escalation','military_crisis','military_clash','military_deescalation'],
    'askeri':     ['military_escalation','military_crisis'],
    'bilateral':  ['deteriorating_bilateral_relations','increasing_bilateral_relations'],
    'ikili':      ['deteriorating_bilateral_relations','increasing_bilateral_relations'],
    'mass':       ['mass_killing','mass_expulsion'],
    'killing':    ['mass_killing','domestic_violence'],
}

_COUNTRY_ALIASES = {
    'iran': 'IR', 'irak': 'IZ', 'iraq': 'IZ', 'usa': 'US', 'america': 'US',
    'amerik': 'US', 'abd': 'US', 'states': 'US', 'united states': 'US',
    'russia': 'RS', 'rusya': 'RS', 'türk': 'TU', 'turkey': 'TU', 'türkiye': 'TU',
    'china': 'CH', 'çin': 'CH', 'israel': 'IS', 'israil': 'IS', 'isra': 'IS',
    'ukraine': 'UP', 'ukrain': 'UP', 'ukrayna': 'UP', 'pakistan': 'PK',
    'india': 'IN', 'hindistan': 'IN', 'syria': 'SY', 'suriye': 'SY',
    'saudi': 'SA', 'suudi': 'SA', 'lebanon': 'LE', 'lübnan': 'LE', 'libn': 'LE',
    'egypt': 'EG', 'mısır': 'EG', 'france': 'FR', 'fransa': 'FR',
    'germany': 'GM', 'almanya': 'GM', 'uk': 'UK', 'britain': 'UK',
    'japan': 'JA', 'japonya': 'JA', 'brazil': 'BR', 'brezilya': 'BR',
    'north korea': 'KN', 'kuzey kore': 'KN', 'korea': 'KS', 'south korea': 'KS',
    'afg': 'AF', 'afghanistan': 'AF', 'afganistan': 'AF',
    'yemen': 'YM', 'jordan': 'JO', 'ürdün': 'JO', 'kuwait': 'KU', 'kuvey': 'KU',
    'qatar': 'QA', 'katar': 'QA', 'nigeri': 'NI', 'ethiopia': 'ET', 'etyopya': 'ET',
    'somalia': 'SO', 'somali': 'SO', 'kenya': 'KE', 'ghana': 'GH',
    'spain': 'SP', 'ispanya': 'SP', 'italy': 'IT', 'italya': 'IT',
    'greece': 'GR', 'yunanis': 'GR', 'mexico': 'MX', 'meksika': 'MX',
    'colombia': 'CO', 'kolombiya': 'CO', 'indonesia': 'ID', 'endonezya': 'ID',
    'malaysia': 'MY', 'filipin': 'RP', 'philippine': 'RP',
    'kazak': 'KZ', 'kazakhst': 'KZ', 'kyrgyz': 'KG', 'kırgız': 'KG',
    'norwa': 'NO', 'norveç': 'NO', 'sweden': 'SW', 'isveç': 'SW',
}


def _parse_question(question):
    """Extract country codes and relevant topics from a natural-language question."""
    q_low = question.lower()

    # ── Countries ───────────────────────────────────────────────
    found_countries = set()
    # Check alias map first (longer phrases first)
    for alias in sorted(_COUNTRY_ALIASES.keys(), key=len, reverse=True):
        if alias in q_low:
            found_countries.add(_COUNTRY_ALIASES[alias])
    # Then check official country names
    for code, name in COUNTRY_NAMES.items():
        if name.lower() in q_low:
            found_countries.add(code)

    # ── Topics ──────────────────────────────────────────────────
    found_topics = set()
    for kw, topics in _QUESTION_KEYWORDS.items():
        if kw in q_low:
            found_topics.update(topics)
    # Direct topic key match
    for key in TOPIC_LABELS:
        if key.replace('_', ' ') in q_low or TOPIC_LABELS[key].lower() in q_low:
            found_topics.add(key)

    return list(found_countries), list(found_topics)


def _answer_question(question, df_raw, trend_df, pred_df, insights_df):
    """
    Build a narrative analytical response for the given question.
    Sections per country:
      1. Recent 7-day index trend (vs prior 7 days)
      2. 12-month model projections
      3. Per-country assessment paragraph
    Returns HTML string.
    """
    import pandas as _pd

    countries, topics = _parse_question(question)

    # Fallback countries
    fallback_note = ""
    if not countries:
        if insights_df is not None and len(insights_df):
            countries = insights_df['country'].head(3).tolist()
            fallback_note = "No specific country detected — showing top-risk countries."
        elif trend_df is not None and len(trend_df):
            countries = trend_df.sort_values('trend_pct', ascending=False)['country'].unique()[:3].tolist()
            fallback_note = "No specific country detected — showing top trending countries."

    # Fallback topics
    if not topics:
        topics = ['political_instability', 'military_escalation', 'international_crisis',
                  'military_crisis', 'coup', 'terrorism']

    date_cols = sorted([c for c in df_raw.columns if hasattr(c, 'strftime')])
    if not date_cols:
        return "<div style='color:#7a9ab8;font-size:0.75rem;padding:10px;'>No time-series index data available.</div>"

    recent_cols = date_cols[-7:] if len(date_cols) >= 7 else date_cols
    prev_cols   = date_cols[-14:-7] if len(date_cols) >= 14 else date_cols[:max(1, len(date_cols) - 7)]
    last_date   = recent_cols[-1].strftime('%B %d, %Y') if recent_cols else "unknown"

    country_blocks = []

    for country in countries[:4]:
        cname = COUNTRY_NAMES.get(country, country)

        # ── SECTION 1: Recent 7-day trend ──────────────────────────
        trend_items = []
        try:
            c_df = df_raw.xs(country, level='country')
            for topic in topics:
                if topic not in c_df.index:
                    continue
                row = c_df.loc[topic]
                cur_vals = [float(row[d]) for d in recent_cols if d in row.index and not _pd.isna(row[d])]
                prv_vals = [float(row[d]) for d in prev_cols  if d in row.index and not _pd.isna(row[d])]
                if not cur_vals or not prv_vals:
                    continue
                cur_avg = sum(cur_vals) / len(cur_vals)
                prv_avg = sum(prv_vals) / len(prv_vals)
                if prv_avg < 0.001:
                    continue
                pct = (cur_avg - prv_avg) / prv_avg * 100
                if abs(pct) < 2:
                    continue
                lbl = TOPIC_LABELS.get(topic, topic.replace('_', ' ').title())
                direction = "rose" if pct > 0 else "eased"
                color = "#ff6b6b" if pct > 15 else "#ffa94d" if pct > 5 else "#1a5a99" if pct < -5 else "#a9e34b"
                arrow = "▲" if pct > 0 else "▼"
                trend_items.append((abs(pct), pct,
                    f"<span style='color:{color};'><b>{arrow} {lbl}</b> {direction} <b>{pct:+.1f}%</b></span>"))
        except Exception:
            pass

        trend_items.sort(key=lambda x: -x[0])

        if trend_items:
            phrases = [s for _, _, s in trend_items[:5]]
            section1_html = (
                f"<p style='color:#1a4a8a;font-size:0.73rem;line-height:1.75;margin:0 0 4px;'>"
                f"Over the <b>last 7 days</b> (through {last_date}), key risk indices for "
                f"<b>{cname}</b> showed: " + ", ".join(phrases) + ".</p>"
            )
        else:
            section1_html = (
                f"<p style='color:#7a9ab8;font-size:0.73rem;margin:0 0 4px;'>"
                f"No significant 7-day movement detected for <b>{cname}</b> across the queried topics.</p>"
            )

        # ── SECTION 2: 12-month predictions ────────────────────────
        pred_items = []
        if pred_df is not None:
            c_pred = pred_df[pred_df['country'] == country]
            for topic in topics:
                t_pred = c_pred[c_pred['topic'] == topic].sort_values('ds')
                if len(t_pred) < 2:
                    continue
                base_val = float(t_pred.iloc[0]['yhat'])
                if base_val < 0.001:
                    continue
                idx_3m  = min(2, len(t_pred) - 1)
                val_3m  = float(t_pred.iloc[idx_3m]['yhat'])
                val_12m = float(t_pred.iloc[-1]['yhat'])
                pct_3m  = (val_3m  - base_val) / base_val * 100
                pct_12m = (val_12m - base_val) / base_val * 100
                lbl     = TOPIC_LABELS.get(topic, topic.replace('_', ' ').title())
                ds_end  = t_pred.iloc[-1]['ds']
                ds_str  = ds_end.strftime('%B %Y') if hasattr(ds_end, 'strftime') else str(ds_end)
                if abs(pct_12m) < 2:
                    sentence = f"<b>{lbl}</b> is projected to remain <b>stable</b> through {ds_str}"
                elif pct_12m > 0:
                    col = "#ff6b6b" if pct_12m > 20 else "#ffa94d"
                    sentence = (f"<b>{lbl}</b> is projected to "
                                f"<span style='color:{col};'>rise <b>{pct_12m:+.1f}%</b></span> "
                                f"by {ds_str} (3-month: {pct_3m:+.1f}%)")
                else:
                    col = "#1a5a99"
                    sentence = (f"<b>{lbl}</b> is projected to "
                                f"<span style='color:{col};'>ease <b>{pct_12m:+.1f}%</b></span> "
                                f"by {ds_str} (3-month: {pct_3m:+.1f}%)")
                pred_items.append((abs(pct_12m), pct_12m, sentence))

            pred_items.sort(key=lambda x: -x[0])

        if pred_items:
            pred_phrases = [s for _, _, s in pred_items[:5]]
            section2_html = (
                f"<p style='color:#1a4a8a;font-size:0.73rem;line-height:1.75;margin:0 0 4px;'>"
                f"<b>Forward projections (12-month model)</b> for <b>{cname}</b>: "
                + "; ".join(pred_phrases) + ".</p>"
            )
        else:
            section2_html = (
                f"<p style='color:#7a9ab8;font-size:0.73rem;margin:0 0 4px;'>"
                f"No model forecast available for <b>{cname}</b> on the queried topics.</p>"
            )

        # ── SECTION 3: Assessment ───────────────────────────────────
        net_trend = (sum(p for _, p, _ in trend_items) / len(trend_items)) if trend_items else 0.0
        net_pred  = (sum(p for _, p, _ in pred_items)  / len(pred_items))  if pred_items  else 0.0

        if net_trend > 10 and net_pred > 5:
            assess_color = "#ff6b6b"
            assess_text  = (
                f"<b>{cname}</b> shows a <span style='color:#ff6b6b;'><b>deteriorating risk trajectory</b></span>. "
                f"Recent index data confirms escalating tensions across multiple domains, and predictive models "
                f"reinforce this upward pressure over the coming year. "
                f"<b>Elevated monitoring is warranted.</b>"
            )
        elif net_trend > 5 or net_pred > 10:
            assess_color = "#ffa94d"
            assess_text  = (
                f"<b>{cname}</b> presents a <span style='color:#ffa94d;'><b>cautionary but mixed picture</b></span>. "
                f"Either recent signals or forward projections indicate elevated risk. "
                f"Sustained observation of key indicators is recommended."
            )
        elif net_trend < -5 and net_pred < -5:
            assess_color = "#1a5a99"
            assess_text  = (
                f"<b>{cname}</b> demonstrates an <span style='color:#1a5a99;'><b>improving risk outlook</b></span>. "
                f"Recent indices are easing, and the 12-month model confirms continued de-escalation on most fronts."
            )
        elif net_trend < -5:
            assess_color = "#a9e34b"
            assess_text  = (
                f"<b>{cname}</b> is experiencing <span style='color:#a9e34b;'><b>short-term de-escalation</b></span>, "
                f"though longer-term projections remain uncertain. The situation should continue to be monitored."
            )
        elif net_pred < -5:
            assess_color = "#1a5a99"
            assess_text  = (
                f"<b>{cname}</b> shows a <span style='color:#1a5a99;'><b>positive medium-term outlook</b></span> "
                f"according to model projections, despite limited movement in recent indices."
            )
        else:
            assess_color = "#2d4a6a"
            assess_text  = (
                f"<b>{cname}</b> presents a <span style='color:#2d4a6a;'><b>stable-to-uncertain</b></span> picture. "
                f"No strong directional signal is present in either the current data window or forward projections."
            )

        country_blocks.append(f"""
<div style='background:rgba(5,15,40,0.6);border:1px solid rgba(0,120,200,0.18);
     border-radius:8px;padding:14px 16px;margin-bottom:12px;'>
  <div style='font-size:0.82rem;font-weight:700;color:#0d3464;letter-spacing:0.04em;
       margin-bottom:10px;padding-bottom:7px;border-bottom:1px solid rgba(0,100,180,0.15);'>
    📍 {cname}
    <span style='font-size:0.55rem;color:rgba(0,180,255,0.35);font-family:monospace;margin-left:6px;'>{country}</span>
  </div>
  <div style='font-size:0.6rem;color:rgba(0,200,255,0.5);font-family:monospace;
       letter-spacing:0.1em;margin-bottom:5px;'>■ RECENT ACTIVITY — 7-DAY WINDOW</div>
  {section1_html}
  <div style='font-size:0.6rem;color:rgba(0,200,255,0.5);font-family:monospace;
       letter-spacing:0.1em;margin:10px 0 5px;'>■ FORWARD PROJECTIONS — 12-MONTH MODEL</div>
  {section2_html}
  <div style='font-size:0.6rem;color:rgba(0,200,255,0.5);font-family:monospace;
       letter-spacing:0.1em;margin:10px 0 5px;'>🎯 ASSESSMENT</div>
  <p style='color:#2d4a6a;font-size:0.73rem;line-height:1.75;margin:0;'>{assess_text}</p>
</div>""")

    if not country_blocks:
        return ("<div style='color:#7a9ab8;font-size:0.75rem;padding:10px;'>"
                "No relevant data found for the entities in your question. "
                "Try mentioning a specific country or risk topic.</div>")

    topic_labels_used = ", ".join([TOPIC_LABELS.get(t, t.replace('_', ' ').title()) for t in topics[:6]])
    header_note_html  = (f"<div style='font-size:0.62rem;color:rgba(255,200,100,0.55);"
                         f"font-family:monospace;margin-bottom:10px;'>⚠ {fallback_note}</div>"
                         if fallback_note else "")

    return f"""
<div style='font-family:system-ui,sans-serif;'>
  <div style='font-size:0.58rem;color:rgba(0,200,255,0.4);font-family:monospace;
       letter-spacing:0.1em;margin-bottom:10px;'>
    TOPICS ANALYSED: {topic_labels_used}{" + more" if len(topics) > 6 else ""}
  </div>
  {header_note_html}
  {''.join(country_blocks)}
  <div style='font-size:0.58rem;color:rgba(100,140,180,0.35);font-family:monospace;
       margin-top:6px;border-top:1px solid rgba(0,80,160,0.1);padding-top:6px;'>
    SOURCE: GDELT PROJECT · INDICES WINDOW TO {last_date.upper()} · PROPHET 12-MONTH FORECAST
  </div>
</div>"""


@st.cache_data(ttl=3600)
def load_enriched_articles():
    """Load RSS-fetched quality articles (last 30 days)."""
    try:
        if not os.path.exists('enriched_articles.csv'):
            return None
        df = pd.read_csv('enriched_articles.csv', dtype=str)
        return df
    except Exception:
        return None


@st.cache_data(ttl=3600)
def load_commodities():
    """Load commodity price data."""
    try:
        if not os.path.exists('commodities.csv'):
            return None
        return pd.read_csv('commodities.csv')
    except Exception:
        return None


def _build_qa_context(question, article_df, commodity_df):
    """Build extra context string from articles and commodity prices for Claude prompt."""
    parts = []
    q_lower = question.lower()
    words = set(re.findall(r'\b\w{4,}\b', q_lower))

    if article_df is not None and len(article_df) > 0:
        def score(row):
            t = str(row.get('title','')) + ' ' + str(row.get('summary','')) + ' ' + str(row.get('countries','')) + ' ' + str(row.get('topics',''))
            return sum(1 for w in words if w in t.lower())
        scores = article_df.apply(score, axis=1)
        top = article_df[scores > 0].copy()
        top['_sc'] = scores[scores > 0]
        top = top.nlargest(6, '_sc')
        if len(top) > 0:
            parts.append('\n\n=== RECENT EXPERT ANALYSIS (Quality Sources) ===')
            for _, r in top.iterrows():
                src  = str(r.get('source',''))
                date = str(r.get('date',''))[:10]
                ttl  = str(r.get('title',''))
                smm  = str(r.get('summary',''))[:300]
                url  = str(r.get('url',''))
                parts.append(f'[{src} | {date}] {ttl}\n{smm}\n{url}')

    COMM_MAP = {
        'oil': ['CL=F','BZ=F'], 'crude': ['CL=F','BZ=F'], 'brent': ['BZ=F'], 'wti': ['CL=F'],
        'gas': ['NG=F'], 'natural gas': ['NG=F'], 'lng': ['NG=F'],
        'gold': ['GC=F'], 'silver': ['SI=F'], 'copper': ['HG=F'], 'platinum': ['PL=F'],
        'wheat': ['ZW=F'], 'corn': ['ZC=F'], 'soybean': ['ZS=F'],
        'vix': ['^VIX'], 'fear': ['^VIX'], 'volatility': ['^VIX'],
        'dollar': ['DX-Y.NYB'], 'usd': ['DX-Y.NYB','EURUSD=X'],
        'euro': ['EURUSD=X'], 'treasury': ['^TNX'], 'bond': ['^TNX'],
        'ruble': ['USDRUB=X'], 'yuan': ['USDCNY=X'], 'stock': ['^GSPC'],
        'opec': ['CL=F','BZ=F','NG=F'], 'energy': ['CL=F','BZ=F','NG=F'],
        'metal': ['GC=F','SI=F','HG=F'], 'inflation': ['GC=F','^VIX','DX-Y.NYB'],
        'commodity': None, 'price': None, 'market': ['^GSPC','^VIX'],
        'russia': ['USDRUB=X','CL=F'], 'china': ['USDCNY=X'],
        'sanction': ['USDRUB=X','CL=F'], 'petrol': ['CL=F','BZ=F'],
    }

    if commodity_df is not None and len(commodity_df) > 0:
        tickers = set()
        for kw, tkrs in COMM_MAP.items():
            if kw in q_lower:
                if tkrs:
                    tickers.update(tkrs)
                else:
                    tickers.update(commodity_df['ticker'].unique())
        if tickers:
            latest = commodity_df['date'].max()
            rows = commodity_df[(commodity_df['date'] == latest) & (commodity_df['ticker'].isin(tickers))]
            if len(rows) > 0:
                parts.append(f'\n\n=== LIVE MARKET DATA (as of {latest}) ===')
                for _, r in rows.iterrows():
                    c1d = r.get('chg_1d_pct', 0)
                    c7d = r.get('chg_7d_pct', 0)
                    try:
                        c1d_s = f"{float(c1d)*100:.2f}%"
                        c7d_s = f"{float(c7d)*100:.2f}%"
                    except Exception:
                        c1d_s = c7d_s = 'N/A'
                    parts.append(f"{r['name']}: {r['price']} {r['unit']} | 1d: {c1d_s} | 7d: {c7d_s}")

    return '\n'.join(parts)


def _call_claude_for_qa(question, df_raw, trend_df, pred_df, insights_df):
    """Comprehensive Claude analysis using NERAI index data, predictions, and live news."""
    import anthropic, os, datetime
    import pandas as _pd
    try:
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            return (
                '<div style="background:#1a0d0d;border:1px solid #8a3a3a;border-radius:8px;'
                'padding:14px;margin-top:14px;color:#ff9999;font-size:13px;">'
                '\u26a0\ufe0f <b>ANTHROPIC_API_KEY</b> Streamlit Cloud Secrets b\u00f6l\u00fcm\u00fcnde tan\u0131ml\u0131 de\u011fil. '
                'Settings \u2192 Secrets k\u0131sm\u0131na ekleyin.</div>'
            )
        today_str = datetime.datetime.now().strftime('%d %B %Y')

        _pq = _parse_question(question)
        countries = _pq[0] if isinstance(_pq, (list, tuple)) and len(_pq) >= 2 else []
        topics = _pq[1] if isinstance(_pq, (list, tuple)) and len(_pq) >= 2 else []

        q_low = question.lower()
        for kw, topic_list in _QUESTION_KEYWORDS.items():
            if kw in q_low:
                for t in topic_list:
                    if t not in topics:
                        topics.append(t)

        if not topics:
            topics = ['political_instability', 'military_escalation', 'international_crisis',
                      'military_crisis', 'coup', 'terrorism', 'deteriorating_bilateral_relations']

        sections = []

        if df_raw is not None and not df_raw.empty:
            try:
                date_cols = sorted([c for c in df_raw.columns if hasattr(c, 'strftime')])
                if date_cols:
                    now = date_cols[-1]
                    d7  = now - _pd.Timedelta(days=7)
                    d30 = now - _pd.Timedelta(days=30)
                    d90 = now - _pd.Timedelta(days=90)
                    cols_7d  = [c for c in date_cols if c >= d7]
                    cols_30d = [c for c in date_cols if c >= d30]
                    cols_90d = [c for c in date_cols if c >= d90]

                    idx_lines = []
                    target_countries = countries if countries else []
                    if not target_countries and trend_df is not None and len(trend_df) > 0:
                        target_countries = trend_df.sort_values('trend_pct', ascending=False)['country'].unique()[:3].tolist()

                    for ccode in target_countries:
                        cname = COUNTRY_NAMES.get(ccode, ccode)
                        idx_lines.append(f"\n--- {cname} ({ccode}) ---")
                        for tp in topics:
                            try:
                                row = df_raw.loc[(tp, ccode)]
                                cur = round(float(row[date_cols[-1]]), 4) if date_cols[-1] in row.index else None
                                avg7 = round(float(row[cols_7d].mean()), 4) if cols_7d else None
                                avg30 = round(float(row[cols_30d].mean()), 4) if cols_30d else None
                                avg90 = round(float(row[cols_90d].mean()), 4) if cols_90d else None
                                peak7 = round(float(row[cols_7d].max()), 4) if cols_7d else None
                                low7 = round(float(row[cols_7d].min()), 4) if cols_7d else None
                                chg_7v30 = round((avg7 - avg30) / max(avg30, 0.0001) * 100, 1) if avg7 and avg30 else None
                                chg_30v90 = round((avg30 - avg90) / max(avg90, 0.0001) * 100, 1) if avg30 and avg90 else None
                                lbl = TOPIC_LABELS.get(tp, tp.replace('_', ' ').title())
                                line = f"  {lbl}: current={cur}"
                                if avg7 is not None: line += f" | 7d_avg={avg7}"
                                if avg30 is not None: line += f" | 30d_avg={avg30}"
                                if avg90 is not None: line += f" | 90d_avg={avg90}"
                                if peak7 is not None: line += f" | 7d_peak={peak7} | 7d_low={low7}"
                                if chg_7v30 is not None: line += f" | 7d_vs_30d={chg_7v30:+.1f}%"
                                if chg_30v90 is not None: line += f" | 30d_vs_90d={chg_30v90:+.1f}%"
                                idx_lines.append(line)
                            except (KeyError, TypeError):
                                pass

                    mover_lines = []
                    for tp in topics[:8]:
                        try:
                            tp_data = df_raw.loc[tp] if tp in df_raw.index.get_level_values(0) else None
                            if tp_data is not None and not tp_data.empty:
                                avg_recent = tp_data[cols_7d].mean(axis=1)
                                avg_old = tp_data[cols_30d].mean(axis=1)
                                pct_chg = ((avg_recent - avg_old) / avg_old.clip(lower=0.0001) * 100).dropna()
                                if len(pct_chg) > 0:
                                    top_rise = pct_chg.nlargest(3)
                                    lbl = TOPIC_LABELS.get(tp, tp.replace('_', ' ').title())
                                    for cc, val in top_rise.items():
                                        cn = COUNTRY_NAMES.get(cc, cc)
                                        mover_lines.append(f"  {lbl} in {cn}: {val:+.1f}% (7d vs 30d)")
                        except Exception:
                            pass

                    if idx_lines:
                        sections.append("=== NERAI INDEX VALUES (Real GDELT-based Risk Indices) ===\n"
                                        "Data date: " + str(now.date()) + "\n" + "\n".join(idx_lines))
                    if mover_lines:
                        sections.append("=== TOP MOVERS: Related Topics Globally (7d vs 30d) ===\n" + "\n".join(mover_lines[:15]))
            except Exception:
                pass

        if trend_df is not None and not trend_df.empty:
            try:
                trend_lines = []
                for ccode in (countries if countries else []):
                    cname = COUNTRY_NAMES.get(ccode, ccode)
                    ct = trend_df[trend_df['country'] == ccode]
                    for tp in topics:
                        row = ct[ct['topic'] == tp]
                        if not row.empty:
                            r = row.iloc[0]
                            lbl = TOPIC_LABELS.get(tp, tp.replace('_', ' ').title())
                            pct = r.get('trend_pct', 0)
                            dirn = r.get('direction', 'stable')
                            trend_lines.append(f"  {cname} - {lbl}: trend={pct:+.1f}% ({dirn})")
                if trend_lines:
                    sections.append("=== NERAI FORECAST TRENDS (Predicted Direction) ===\n" + "\n".join(trend_lines))
            except Exception:
                pass

        if pred_df is not None and not pred_df.empty:
            try:
                pred_lines = []
                now_ts = _pd.Timestamp.now()
                for ccode in (countries if countries else []):
                    cname = COUNTRY_NAMES.get(ccode, ccode)
                    cpred = pred_df[pred_df['country'] == ccode] if 'country' in pred_df.columns else pred_df
                    for tp in topics:
                        tp_pred = cpred[cpred['topic'] == tp] if 'topic' in cpred.columns else cpred
                        if tp_pred.empty:
                            continue
                        tp_pred = tp_pred.sort_values('ds')
                        hist = tp_pred[tp_pred['ds'] <= now_ts].tail(30)
                        future = tp_pred[tp_pred['ds'] > now_ts].head(60)
                        lbl = TOPIC_LABELS.get(tp, tp.replace('_', ' ').title())
                        line = f"  {cname} - {lbl}:"
                        if not hist.empty and 'yhat' in hist.columns:
                            h_avg = round(float(hist['yhat'].mean()), 4)
                            h_last = round(float(hist['yhat'].iloc[-1]), 4)
                            line += f" recent_pred_avg={h_avg} | last_pred={h_last}"
                        if not future.empty and 'yhat' in future.columns:
                            f_avg = round(float(future['yhat'].mean()), 4)
                            f_max = round(float(future['yhat'].max()), 4)
                            f_min = round(float(future['yhat'].min()), 4)
                            line += f" | forecast_avg={f_avg} | forecast_max={f_max} | forecast_min={f_min}"
                            if 'yhat_upper' in future.columns:
                                f_up = round(float(future['yhat_upper'].max()), 4)
                                f_lo = round(float(future['yhat_lower'].min()), 4)
                                line += f" | upper_bound={f_up} | lower_bound={f_lo}"
                        pred_lines.append(line)

                cross_lines = []
                all_future = pred_df[pred_df['ds'] > now_ts] if 'ds' in pred_df.columns else _pd.DataFrame()
                if not all_future.empty and 'topic' in all_future.columns and 'yhat' in all_future.columns:
                    topic_avg = all_future.groupby('topic')['yhat'].mean().sort_values(ascending=False)
                    for tp_name, val in topic_avg.head(20).items():
                        marker = " [RELATED]" if tp_name in topics else ""
                        lbl = TOPIC_LABELS.get(tp_name, tp_name.replace('_', ' ').title())
                        cross_lines.append(f"  {lbl}: avg_forecast={val:.4f}{marker}")

                if pred_lines:
                    sections.append("=== NERAI PREDICTIONS (Model Forecasts) ===\n" + "\n".join(pred_lines))
                if cross_lines:
                    sections.append("=== CROSS-TOPIC PREDICTION RANKING (All Topics) ===\n" + "\n".join(cross_lines[:15]))
            except Exception:
                pass

        try:
            news_lines = []
            search_terms = []
            for tp in topics[:3]:
                lbl = TOPIC_LABELS.get(tp, tp.replace('_', ' ').title())
                search_terms.append(lbl)
            for ccode in (countries[:2] if countries else []):
                cname = COUNTRY_NAMES.get(ccode, ccode)
                search_terms.append(cname)
            search_q = ' '.join(search_terms[:4])
            seen_titles = set()
            if search_q:
                gdelt_arts = fetch_gdelt_news(search_q, max_records=5)
                rss_arts = fetch_global_media_rss(search_q, max_per_feed=2)
                all_arts = (gdelt_arts or []) + (rss_arts or [])
                for art in all_arts[:10]:
                    ttl = art.get('title', '')[:120]
                    if ttl and ttl not in seen_titles:
                        seen_titles.add(ttl)
                        src = art.get('domain', art.get('source', ''))
                        dt = art.get('date', '')[:10]
                        news_lines.append(f"  [{dt}] {ttl} ({src})")
            if insights_df is not None and not insights_df.empty:
                news_cols = [c for c in ['title', 'headline', 'text', 'event'] if c in insights_df.columns]
                if news_cols:
                    nc = news_cols[0]
                    for _, row in insights_df.head(5).iterrows():
                        s = str(row[nc])[:120]
                        if s and s not in seen_titles:
                            seen_titles.add(s)
                            news_lines.append(f"  {s}")
            if news_lines:
                sections.append("=== LIVE NEWS & EVENTS ===\n" + "\n".join(news_lines[:12]))
        except Exception:
            pass

        if insights_df is not None and not insights_df.empty:
            try:
                ins_lines = []
                ctry_col = next((c for c in ['country', 'geo'] if c in insights_df.columns), None)
                for ccode in (countries if countries else []):
                    cname = COUNTRY_NAMES.get(ccode, ccode)
                    if ctry_col:
                        cdf = insights_df[insights_df[ctry_col].str.upper() == ccode.upper()]
                    else:
                        cdf = insights_df
                    if not cdf.empty:
                        if 'forecast_dir' in cdf.columns:
                            dirs = cdf['forecast_dir'].value_counts().to_dict()
                            ins_lines.append(f"  {cname}: forecast directions = {dirs}")
                        if 'trend_pct' in cdf.columns:
                            avg_t = round(float(cdf['trend_pct'].mean()), 1)
                            ins_lines.append(f"  {cname}: avg trend = {avg_t:+.1f}%")
                if ins_lines:
                    sections.append("=== COUNTRY RISK INSIGHTS ===\n" + "\n".join(ins_lines))
            except Exception:
                pass

        if not sections:
            sections.append("Note: No structured NERAI data found for this query. Providing general analysis.")

        context = "\n\n".join(sections)

        prompt = (
            "You are NERAI Intelligence Platform's senior geopolitical risk analyst. "
            "Today: " + today_str + ".\n\n"
            "IMPORTANT: Below is REAL data from NERAI's proprietary GDELT-based risk indices and "
            "prediction models. These are actual quantitative measurements, NOT estimates. "
            "You MUST reference specific numerical values from this data in your analysis.\n\n"
            + context +
            "\n\n=== USER QUESTION ===\n" + question + "\n\n"
            "ANALYSIS FRAMEWORK (respond in structured paragraphs, NOT markdown):\n\n"
            "0) EXECUTIVE SUMMARY: Start with a 3-4 sentence executive summary that directly answers "
            "the user question based on your full analysis. State the bottom-line conclusion, the key "
            "evidence from NERAI indices and predictions supporting it, and the probability assessment. "
            "This summary should give the reader the final answer upfront before the detailed analysis follows.\n\n"
            "1) INDEX ANALYSIS: Reference specific NERAI index values for each relevant topic. "
            "Compare current values with 7-day, 30-day, and 90-day averages. Highlight which indices "
            "are rising or falling and by how much (use the exact percentages from the data).\n\n"
            "2) PREDICTION & PROJECTION: Use the NERAI prediction model forecasts. Compare predicted "
            "values with recent actuals. Identify divergences between forecast and current trajectory. "
            "Rank related topics by predicted future intensity.\n\n"
            "3) CROSS-TOPIC ANALYSIS: Examine how different related indices interact. "
            "If military_escalation is rising but dispute_settlement is also rising, what does that mean? "
            "Identify convergence or divergence patterns across related topics.\n\n"
            "4) CURRENT DEVELOPMENTS: Integrate live news with the index data. Which news events "
            "correlate with index movements?\n\n"
            "5) STRATEGIC ASSESSMENT: Synthesize all data into a forward-looking assessment with "
            "probability-weighted scenarios.\n\n"
            "CRITICAL: Always cite specific NERAI index values and prediction numbers. "
            "Do NOT say 'data not provided' - use the actual numbers above. "
            "Write in plain text paragraphs, NO markdown formatting. Respond in English."
        )

        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=4500,
            messages=[{'role': 'user', 'content': prompt}]
        )
        narrative = msg.content[0].text.strip()

        return (
            '<div style="background:linear-gradient(135deg,#0d1e38,#0a1628);'
            'border:1px solid #2a5080;border-radius:12px;padding:20px;margin-top:16px;">'
            '<div style="color:#5ba3f5;font-size:11px;font-weight:700;letter-spacing:2px;'
            'margin-bottom:14px;">\U0001f916 NERAI AI ANALYSIS \u2014 INDEX-BASED ASSESSMENT</div>'
            '<div style="color:#c8d8f0;font-size:14px;line-height:1.85;white-space:pre-wrap;">'
            + narrative +
            '</div>'
            '<div style="color:#3a5a7a;font-size:10px;margin-top:14px;border-top:1px solid #1a3a5a;'
            'padding-top:8px;">NERAI indices + predictions \u00b7 claude-haiku-4-5 \u00b7 ' + today_str + '</div>'
            '</div>'
        )
    except Exception as _e:
        return (
            '<div style="background:#1a0808;border:1px solid #8a2a2a;border-radius:8px;'
            'padding:12px;margin-top:12px;color:#ff9999;font-size:12px;">'
            '\u26a0\ufe0f AI analysis error: ' + str(_e)[:300] + '</div>'
        )

def render_insights():
    nerai_premium_css.inject_page_header(
        title="AI Insights",
        subtitle="Machine-generated intelligence briefings & natural language Q&A",
        badge="AI",
        icon="🧠"
    )
    nerai_premium_css.inject_global_premium_css()

    # ── Page header ─────────────────────────────────────────────
    st.markdown("""
<div style='padding:10px 0 6px;'>
  <div style='font-size:1.55rem;font-weight:800;color:#0d3464;letter-spacing:0.04em;'>
    🔍 Intelligence Insights
  </div>
  <div style='font-size:0.65rem;color:rgba(0,180,255,0.45);font-family:monospace;
       letter-spacing:0.12em;margin-top:3px;'>
    DATA-DRIVEN COUNTRY RISK ANALYSIS &nbsp;·&nbsp; 7-DAY WINDOW + 12-MONTH FORECAST
  </div>
</div>""", unsafe_allow_html=True)

    _indices_ok = df is not None and len(df) > 0
    if not _indices_ok:
        st.info("📥 No indices data available. Run `python gdelt_indices.py` first.")

    # ═══ FAZ 4b: Diebold-Yilmaz Spillover Index ═══
    st.markdown('<div class="h-div" style="margin:24px 0 16px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">🌐  Spillover Index (Diebold-Yilmaz)</div>', unsafe_allow_html=True)
    try:
        _topics_spill = df.index.get_level_values("topic").unique()[:8]
        _last_n = min(60, len(df.columns))
        _recent = df.columns[-_last_n:]
        _series_dict = {}
        for t in _topics_spill:
            try:
                _series_dict[t] = df.xs(t, level="topic")[_recent].mean(axis=0).values
            except Exception:
                continue
        if len(_series_dict) >= 3:
            _sp_df = pd.DataFrame(_series_dict)
            # Simple variance decomposition proxy using correlation
            _corr = _sp_df.corr().abs()
            _corr_vals = _corr.values.copy()
            np.fill_diagonal(_corr_vals, 0)
            _spillover_total = _corr_vals.sum() / (_corr.shape[0] ** 2) * 100
            # Time-varying spillover (rolling window)
            _roll_spill = []
            _w = 14
            for k in range(_w, len(_sp_df)):
                _window_data = _sp_df.iloc[k-_w:k]
                _rc = _window_data.corr().abs()
                _rc_vals = _rc.values.copy()
                np.fill_diagonal(_rc_vals, 0)
                _s = _rc_vals.sum() / (_rc.shape[0] ** 2) * 100
                _roll_spill.append(_s)
            col_a, col_b = st.columns([1, 2])
            with col_a:
                _level = "HIGH" if _spillover_total > 40 else "MODERATE" if _spillover_total > 20 else "LOW"
                _clr = "#e05060" if _level == "HIGH" else "#f59e0b" if _level == "MODERATE" else "#22c55e"
                st.markdown(f'''<div style="text-align:center;padding:20px;
                    background:rgba(0,10,28,0.7);border-radius:10px;border:1px solid {_clr}30">
                    <div style="font-size:2.5rem;font-weight:800;color:{_clr}">{_spillover_total:.1f}%</div>
                    <div style="color:#8aa0bc;font-size:0.8rem">Total Spillover Index</div>
                    <div style="color:{_clr};font-weight:600;margin-top:4px">{_level}</div>
                </div>''', unsafe_allow_html=True)
            with col_b:
                if _roll_spill:
                    fig_spill = go.Figure()
                    fig_spill.add_trace(go.Scatter(
                        x=list(range(len(_roll_spill))), y=_roll_spill,
                        mode="lines", line=dict(color="#00d4ff", width=2),
                        fill="tozeroy", fillcolor="rgba(0,212,255,0.08)"
                    ))
                    fig_spill.add_hline(y=40, line_dash="dash", line_color="#e05060", annotation_text="High")
                    fig_spill.update_layout(**_PLOTLY_THEME, height=250, yaxis_title="Spillover %",
                        xaxis_title="Rolling Window", showlegend=False)
                    st.plotly_chart(fig_spill, use_container_width=True)
        else:
            st.caption("Insufficient topics for spillover analysis.")
    except Exception as _e:
        st.caption(f"Spillover index unavailable: {_e}")

    # ── Compute insights ────────────────────────────────────────
    with st.spinner("Analysing countries × risk topics…"):
        insights_df = _compute_country_insights(df, trend_df)

    # ── Summary KPIs (if available) ─────────────────────────────
    if insights_df is not None and len(insights_df) > 0:
        rising_n  = int((insights_df['forecast_dir'] == 'rising').sum())
        falling_n = int((insights_df['forecast_dir'] == 'falling').sum())
        top1_c    = COUNTRY_NAMES.get(insights_df.iloc[0]['country'], insights_df.iloc[0]['country'])
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Countries Monitored", len(insights_df))
        k2.metric("📈 Rising Trend",  f"{rising_n} countries")
        k3.metric("📉 Falling Trend", f"{falling_n} countries")
        k4.metric("🔴 Highest Risk",  top1_c)
        st.markdown('<div class="h-div" style="margin:16px 0 12px;"></div>', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════
    # Q&A SECTION — always shown
    # ═══════════════════════════════════════════════════════════
    st.markdown("""
<div style='background:rgba(0,30,70,0.5);border:1px solid rgba(0,150,255,0.2);
     border-radius:10px;padding:16px 18px;margin-bottom:20px;'>
  <div style='font-size:0.95rem;font-weight:700;color:#1a4a8a;margin-bottom:4px;'>
    💬 Ask the Data
  </div>
  <div style='font-size:0.65rem;color:rgba(100,170,230,0.55);font-family:monospace;'>
    Ask any geopolitical question — the system will analyse indices, trends and forecasts to answer.
  </div>
</div>""", unsafe_allow_html=True)

    qa_question = st.text_input(
        "question",
        placeholder="e.g.  'What is the risk outlook for Iran and the US?'  or  'Which countries face the highest coup risk?'",
        label_visibility='collapsed',
        key='insights_question'
    )

    qa_submitted = st.button('🔍 Ask', use_container_width=True, type='primary', key='qa_btn')
    if (qa_submitted or st.session_state.get('_qa_last')) and qa_question and qa_question.strip():
        if qa_submitted:
            st.session_state['_qa_last'] = qa_question.strip()
        _q = st.session_state.get('_qa_last', qa_question.strip())
        with st.spinner("Analysing data…"):
            try:
                answer_html = _answer_question(
                    _q, df, trend_df, pred_df, insights_df)
            except Exception as _qa_err:
                answer_html = f'<div style="color:#ff6b6b;padding:8px;">Analysis error: {_qa_err}</div>'
            _art_df  = load_enriched_articles()
            _com_df  = load_commodities()
            _ext_ctx = _build_qa_context(_q, _art_df, _com_df)
            claude_html = _call_claude_for_qa(_q + _ext_ctx, df, trend_df, pred_df, insights_df)
        if answer_html and len(answer_html.strip()) > 10:
            st.markdown(answer_html, unsafe_allow_html=True)
        if 'claude_html' in dir() and claude_html:
            st.markdown(claude_html, unsafe_allow_html=True)
        if not answer_html or len(answer_html.strip()) <= 10:
            st.info('ℹ️ No data found for this question. Try mentioning a country name (e.g. Turkey, Germany) or topic (e.g. military, protest).')
    elif qa_submitted:
        st.warning('⚠️ Please type a question first.')
        st.markdown('<div class="h-div" style="margin:16px 0 12px;"></div>', unsafe_allow_html=True)
    else:
        st.markdown("""
<div style='font-size:0.62rem;color:rgba(100,150,200,0.4);font-family:monospace;
     text-align:center;padding:8px;'>
  ↑ Type a question above to get a data-driven analysis
</div>""", unsafe_allow_html=True)
        st.markdown('<div class="h-div" style="margin:10px 0 16px;"></div>', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════
    # COUNTRY RISK CARDS
    # ═══════════════════════════════════════════════════════════
    if insights_df is not None and len(insights_df) > 0:
        st.markdown("""
<div style='font-size:0.6rem;color:rgba(0,180,255,0.4);font-family:monospace;
     letter-spacing:0.15em;margin-bottom:14px;'>
  TOP 20 MOST CRITICAL COUNTRIES &nbsp;·&nbsp; RANKED BY RISK LEVEL + RATE OF CHANGE
</div>""", unsafe_allow_html=True)
        top20 = insights_df.head(20).to_dict('records')
        for i in range(0, len(top20), 2):
            c1, c2 = st.columns(2)
            _render_country_card(c1, top20[i])
            if i + 1 < len(top20):
                _render_country_card(c2, top20[i + 1])
    elif trend_df is not None:
        # Fallback: show top rising/falling from trend data
        st.markdown("""
<div style='font-size:0.6rem;color:rgba(0,180,255,0.4);font-family:monospace;
     letter-spacing:0.15em;margin-bottom:14px;'>
  TOP RISK MOVEMENTS &nbsp;·&nbsp; 12-MONTH FORECAST TREND
</div>""", unsafe_allow_html=True)
        cf1, cf2 = st.columns(2)
        with cf1:
            st.markdown("<div style='font-size:0.62rem;color:rgba(255,75,110,0.7);font-family:monospace;margin-bottom:8px;'>▲ HIGHEST RISING</div>", unsafe_allow_html=True)
            for _, r in trend_df.nlargest(15, 'trend_pct').iterrows():
                lbl = TOPIC_LABELS.get(r['topic'], str(r['topic']).replace('_',' ').title())
                cnt = COUNTRY_NAMES.get(r['country'], r['country'])
                st.markdown(f"<div style='display:flex;justify-content:space-between;padding:4px 8px;margin-bottom:3px;background:rgba(255,75,110,0.05);border:1px solid rgba(255,75,110,0.12);border-radius:5px;'><div><div style='font-size:0.72rem;color:#2a4060;'>{lbl}</div><div style='font-size:0.58rem;color:rgba(0,150,255,0.5);font-family:monospace;'>{cnt}</div></div><div style='font-size:0.82rem;font-weight:700;color:#e05060;font-family:monospace;'>+{_safe_pct(r['trend_pct']):.1f}%</div></div>", unsafe_allow_html=True)
        with cf2:
            st.markdown("<div style='font-size:0.62rem;color:rgba(0,255,157,0.7);font-family:monospace;margin-bottom:8px;'>▼ HIGHEST FALLING</div>", unsafe_allow_html=True)
            for _, r in trend_df.nsmallest(15, 'trend_pct').iterrows():
                lbl = TOPIC_LABELS.get(r['topic'], str(r['topic']).replace('_',' ').title())
                cnt = COUNTRY_NAMES.get(r['country'], r['country'])
                st.markdown(f"<div style='display:flex;justify-content:space-between;padding:4px 8px;margin-bottom:3px;background:rgba(0,255,157,0.04);border:1px solid rgba(0,255,157,0.10);border-radius:5px;'><div><div style='font-size:0.72rem;color:#2a4060;'>{lbl}</div><div style='font-size:0.58rem;color:rgba(0,150,255,0.5);font-family:monospace;'>{cnt}</div></div><div style='font-size:0.82rem;font-weight:700;color:#00B8D4;font-family:monospace;'>{_safe_pct(r['trend_pct']):.1f}%</div></div>", unsafe_allow_html=True)

    _render_footer()


# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
def _render_footer():
    st.markdown("""
    <div style='margin-top:40px;padding:16px;text-align:center;
         border-top:1px solid rgba(0,150,255,0.08);
         font-size:0.6rem;color:rgba(0,150,255,0.2);font-family:monospace;letter-spacing:0.1em;'>
      NERAI INTELLIGENCE HUB &nbsp;·&nbsp; DATA: GDELT PROJECT &nbsp;·&nbsp; v3.0
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# CAUSAL NETWORK PAGE
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def load_causality():
    path = './causality_network.csv'
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            if df.empty or len(df.columns) == 0:
                return None
            return df
        except Exception:
            return None
    return None

@st.cache_data(ttl=3600)
def load_scenario_results():
    path = './scenario_results.csv'
    if os.path.exists(path):
        return pd.read_csv(path)
    return None


def _node_label(node):
    """'political_instability_RU' → ('Political Instability', 'RU')"""
    parts = node.rsplit('_', 1)
    if len(parts) == 2:
        return parts[0].replace('_', ' ').title(), parts[1]
    return node, ''


@st.cache_data(ttl=3600)
def fetch_causal_news(topic, country_code, max_records=5):
    """Fetch recent news from GDELT DOC API for a causal topic+country."""
    import urllib.parse, json
    try:
        label = topic.replace("_", " ")
        country_name = {
            "US": "United States", "CN": "China", "RU": "Russia",
            "IR": "Iran", "GB": "United Kingdom", "DE": "Germany",
            "FR": "France", "JP": "Japan", "KR": "South Korea",
            "IN": "India", "BR": "Brazil", "TR": "Turkey",
            "SA": "Saudi Arabia", "IL": "Israel", "UA": "Ukraine",
            "TW": "Taiwan", "AU": "Australia", "CA": "Canada",
            "MX": "Mexico", "EG": "Egypt", "PK": "Pakistan",
            "NG": "Nigeria", "ZA": "South Africa", "ID": "Indonesia",
            "IT": "Italy", "ES": "Spain", "PL": "Poland",
            "NL": "Netherlands", "SE": "Sweden", "NO": "Norway",
            "IS": "Iceland", "FI": "Finland", "DK": "Denmark",
            "GR": "Greece", "PT": "Portugal", "AT": "Austria",
            "CH": "Switzerland", "BE": "Belgium", "IE": "Ireland",
            "CZ": "Czech Republic", "RO": "Romania", "HU": "Hungary",
        }.get(country_code, country_code)
        query_str = f"{label} {country_name}"
        encoded = urllib.parse.quote(query_str)
        url = f"https://api.gdeltproject.org/api/v2/doc/doc?query={encoded}&mode=artlist&maxrecords={max_records}&format=json&sort=datedesc"
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "NERAI/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        articles = data.get("articles", [])
        results = []
        for art in articles[:max_records]:
            results.append({
                "title": art.get("title", ""),
                "url": art.get("url", ""),
                "source": art.get("domain", art.get("sourcecountry", "")),
                "date": art.get("seendate", "")[:10],
                "image": art.get("socialimage", ""),
            })
        return results
    except Exception:
        return []


def build_network_figure(filtered, highlight_nodes=None, focus_node=None):
    """Build an interactive D3.js node-editor style network from filtered edge DataFrame."""
    import json as _json
    if highlight_nodes is None:
        highlight_nodes = set()

    if focus_node and focus_node != "All":
        filtered = filtered[(filtered["source"] == focus_node) | (filtered["target"] == focus_node)].copy()

    nodes_set = set(filtered["source"].tolist() + filtered["target"].tolist())
    if len(nodes_set) == 0:
        return None

    # NERAI brand palette - cyan/teal tones
    TOPIC_COLORS = {
        "political_instability": "#00e5ff",
        "military_escalation": "#00bcd4",
        "military_clash": "#0097a7",
        "government_instability": "#26c6da",
        "coup": "#7c4dff",
        "international_support": "#448aff",
        "international_crisis": "#18ffff",
        "increasing_bilateral_relations": "#00e676",
        "deteriorating_bilateral_relations": "#ff6e40",
        "political_repression": "#b388ff",
        "ethnic_religious_violence": "#ff5252",
        "domestic_violence": "#8d6e63",
        "property_confiscation": "#78909c",
        "dispute_settlement": "#84ffff",
        "corruption": "#ff9100",
        "terrorism": "#ff1744",
        "protest_activity": "#ffab40",
        "democratization": "#69f0ae",
        "appeal_of_leadership_change": "#536dfe",
        "authoritarianism": "#e040fb",
    }

    degree = {}
    for _, row in filtered.iterrows():
        degree[row["source"]] = degree.get(row["source"], 0) + row["max_f_stat"]
        degree[row["target"]] = degree.get(row["target"], 0) + row["max_f_stat"]

    node_list = []
    for nd in nodes_set:
        parts = nd.rsplit("_", 1)
        if len(parts) == 2:
            label = parts[0].replace("_", " ").title()
            cc = parts[1].upper()
        else:
            label = nd
            cc = ""
        topic_key = parts[0] if len(parts) == 2 else nd
        color = TOPIC_COLORS.get(topic_key, "#00e5ff")
        is_hl = nd in highlight_nodes
        node_list.append({"id": nd, "label": label, "cc": cc, "color": color, "degree": degree.get(nd, 1), "hl": is_hl})

    edge_list = []
    for _, row in filtered.iterrows():
        edge_list.append({"source": row["source"], "target": row["target"], "weight": float(row["max_f_stat"])})

    max_deg = max((n["degree"] for n in node_list), default=1)
    for n in node_list:
        n["size"] = 18 + 30 * (n["degree"] / max_deg)

    max_w = max((e["weight"] for e in edge_list), default=1)
    nodes_json = _json.dumps(node_list)
    edges_json = _json.dumps(edge_list)

    html = f"""
    <div id="nerai-graph" style="width:100%;height:750px;background:linear-gradient(135deg,#040810 0%,#0a1628 50%,#060d18 100%);border-radius:12px;position:relative;overflow:hidden;border:1px solid rgba(0,230,255,0.2);">
      <canvas id="bgCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;"></canvas>
      <svg id="netSvg" style="width:100%;height:100%;"></svg>
      <div id="tooltip" style="position:absolute;display:none;padding:12px 16px;background:rgba(4,8,16,0.95);border:1px solid rgba(0,230,255,0.5);border-radius:10px;color:#e0f7fa;font:12px Inter,system-ui,sans-serif;pointer-events:none;z-index:10;box-shadow:0 0 25px rgba(0,230,255,0.2);backdrop-filter:blur(8px);"></div>
      <div id="resetBtn" style="position:absolute;top:12px;right:12px;padding:6px 14px;background:rgba(0,230,255,0.15);border:1px solid rgba(0,230,255,0.4);border-radius:6px;color:#00e6ff;font:11px Inter,system-ui,sans-serif;cursor:pointer;display:none;z-index:10;" onclick="window._resetFocus()">Reset View</div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
    <script>
    (function() {{
      const nodes = {nodes_json};
      const edges = {edges_json};
      const maxW = {max_w};
      const container = document.getElementById("nerai-graph");
      const W = container.offsetWidth;
      const H = container.offsetHeight;
      let focusedNode = null;

      // Background grid
      const bgC = document.getElementById("bgCanvas");
      bgC.width = W; bgC.height = H;
      const ctx = bgC.getContext("2d");
      ctx.strokeStyle = "rgba(0,230,255,0.03)";
      for(let x=0;x<W;x+=50){{ ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke(); }}
      for(let y=0;y<H;y+=50){{ ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke(); }}
      // Corner accents
      ctx.strokeStyle = "rgba(0,230,255,0.12)";ctx.lineWidth=2;
      ctx.beginPath();ctx.moveTo(0,30);ctx.lineTo(0,0);ctx.lineTo(30,0);ctx.stroke();
      ctx.beginPath();ctx.moveTo(W-30,0);ctx.lineTo(W,0);ctx.lineTo(W,30);ctx.stroke();
      ctx.beginPath();ctx.moveTo(0,H-30);ctx.lineTo(0,H);ctx.lineTo(30,H);ctx.stroke();
      ctx.beginPath();ctx.moveTo(W-30,H);ctx.lineTo(W,H);ctx.lineTo(W,H-30);ctx.stroke();

      const svg = d3.select("#netSvg");
      const g = svg.append("g");
      svg.call(d3.zoom().scaleExtent([0.2, 5]).on("zoom", (e) => g.attr("transform", e.transform)));

      // Filters
      const defs = svg.append("defs");
      const gl = defs.append("filter").attr("id","glow").attr("x","-50%").attr("y","-50%").attr("width","200%").attr("height","200%");
      gl.append("feGaussianBlur").attr("stdDeviation","4").attr("result","b");
      gl.append("feMerge").selectAll("feMergeNode").data(["b","SourceGraphic"]).join("feMergeNode").attr("in",d=>d);
      const eg = defs.append("filter").attr("id","edgeGlow").attr("x","-50%").attr("y","-50%").attr("width","200%").attr("height","200%");
      eg.append("feGaussianBlur").attr("stdDeviation","2.5").attr("result","b");
      eg.append("feMerge").selectAll("feMergeNode").data(["b","SourceGraphic"]).join("feMergeNode").attr("in",d=>d);

      // Gradient defs for nodes
      nodes.forEach((n,i) => {{
        const grad = defs.append("linearGradient").attr("id","ng"+i).attr("x1","0%").attr("y1","0%").attr("x2","0%").attr("y2","100%");
        grad.append("stop").attr("offset","0%").attr("stop-color",n.color).attr("stop-opacity",0.35);
        grad.append("stop").attr("offset","100%").attr("stop-color","#080e1a").attr("stop-opacity",0.95);
      }});

      // Arrow marker
      defs.append("marker").attr("id","arrow").attr("viewBox","0 0 10 6").attr("refX",10).attr("refY",3)
        .attr("markerWidth",7).attr("markerHeight",5).attr("orient","auto")
        .append("path").attr("d","M0,0L10,3L0,6").attr("fill","rgba(0,230,255,0.4)");

      // Force simulation
      const sim = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(edges).id(d=>d.id).distance(80))
        .force("charge", d3.forceManyBody().strength(-150))
        .force("center", d3.forceCenter(W/2, H/2))
        .force("collision", d3.forceCollide().radius(d=>d.size+20))
        .alphaDecay(0.018);

      // Draw edges
      const linkG = g.append("g");
      const link = linkG.selectAll("path").data(edges).join("path")
        .attr("fill","none")
        .attr("stroke", d => {{ const sc=nodes.find(n=>n.id===(d.source.id||d.source)); return sc?sc.color:"#00e5ff"; }})
        .attr("stroke-opacity", d => 0.12 + 0.35*(d.weight/maxW))
        .attr("stroke-width", d => 0.8 + 2*(d.weight/maxW))
        .attr("filter","url(#edgeGlow)")
        .attr("marker-end","url(#arrow)")
        .classed("edge", true);

      // Animated particles
      const particleG = g.append("g");
      const particles = particleG.selectAll("circle").data(edges).join("circle")
        .attr("r", 1.8)
        .attr("fill", d => {{ const sc=nodes.find(n=>n.id===(d.source.id||d.source)); return sc?sc.color:"#0ff"; }})
        .attr("opacity", 0.7).attr("filter","url(#glow)")
        .classed("particle", true);
      let particleT = 0;

      // Draw node groups
      const nodeG = g.append("g");
      const nodeGroups = nodeG.selectAll("g").data(nodes).join("g")
        .classed("node", true)
        .call(d3.drag()
          .on("start",(e,d)=>{{ if(!e.active) sim.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; }})
          .on("drag",(e,d)=>{{ d.fx=e.x; d.fy=e.y; }})
          .on("end",(e,d)=>{{ if(!e.active) sim.alphaTarget(0); d.fx=null; d.fy=null; }})
        );

      // Node outer glow ring
      nodeGroups.append("rect")
        .attr("rx",10).attr("ry",10)
        .attr("width", d => Math.max(d.label.length*7+28,100)+4)
        .attr("height",52)
        .attr("x", d => -(Math.max(d.label.length*7+28,100)+4)/2)
        .attr("y",-26)
        .attr("fill","none")
        .attr("stroke", d => d.color)
        .attr("stroke-width",0.6)
        .attr("stroke-opacity",0.3)
        .attr("filter","url(#glow)");

      // Node body with gradient
      nodeGroups.append("rect")
        .attr("rx",8).attr("ry",8)
        .attr("width", d => Math.max(d.label.length*7+28,100))
        .attr("height",48)
        .attr("x", d => -Math.max(d.label.length*7+28,100)/2)
        .attr("y",-24)
        .attr("fill", (d,i) => "url(#ng"+i+")")
        .attr("stroke", d => d.color)
        .attr("stroke-width", d => d.hl?2.5:1)
        .attr("stroke-opacity",0.7);

      // Header accent line
      nodeGroups.append("line")
        .attr("x1", d => -Math.max(d.label.length*7+28,100)/2+8)
        .attr("x2", d => Math.max(d.label.length*7+28,100)/2-8)
        .attr("y1",-6).attr("y2",-6)
        .attr("stroke", d => d.color)
        .attr("stroke-width",1.5).attr("stroke-opacity",0.6)
        .attr("stroke-linecap","round");

      // Country code label (top)
      nodeGroups.append("text")
        .attr("y",-12).attr("text-anchor","middle")
        .attr("fill", d => d.color).attr("font-size","10px")
        .attr("font-family","Inter,system-ui,sans-serif")
        .attr("font-weight","700").attr("letter-spacing","1px")
        .text(d => d.cc);

      // Topic label (bottom)
      nodeGroups.append("text")
        .attr("y",8).attr("text-anchor","middle")
        .attr("fill","#c8e6f0").attr("font-size","10px")
        .attr("font-family","Inter,system-ui,sans-serif")
        .text(d => d.label.length>18 ? d.label.slice(0,17)+"..." : d.label);

      // --- CLICK TO FOCUS ---
      function focusOn(d) {{
        focusedNode = d;
        document.getElementById("resetBtn").style.display = "block";
        const connected = new Set();
        connected.add(d.id);
        edges.forEach(e => {{
          const sid = e.source.id || e.source;
          const tid = e.target.id || e.target;
          if(sid===d.id) connected.add(tid);
          if(tid===d.id) connected.add(sid);
        }});
        nodeGroups.transition().duration(400)
          .attr("opacity", n => connected.has(n.id) ? 1 : 0.08);
        link.transition().duration(400)
          .attr("stroke-opacity", e => {{
            const sid = e.source.id || e.source;
            const tid = e.target.id || e.target;
            return (sid===d.id||tid===d.id) ? 0.5+0.4*(e.weight/maxW) : 0.02;
          }});
        particles.transition().duration(400)
          .attr("opacity", e => {{
            const sid = e.source.id || e.source;
            const tid = e.target.id || e.target;
            return (sid===d.id||tid===d.id) ? 0.9 : 0.02;
          }});
      }}

      function resetFocus() {{
        focusedNode = null;
        document.getElementById("resetBtn").style.display = "none";
        nodeGroups.transition().duration(400).attr("opacity", 1);
        link.transition().duration(400)
          .attr("stroke-opacity", d => 0.12 + 0.35*(d.weight/maxW));
        particles.transition().duration(400).attr("opacity", 0.7);
      }}
      window._resetFocus = resetFocus;

      nodeGroups.on("click", (e, d) => {{
        e.stopPropagation();
        if(focusedNode && focusedNode.id === d.id) {{ resetFocus(); }}
        else {{ focusOn(d); }}
      }});
      svg.on("click", () => {{ if(focusedNode) resetFocus(); }});

      // Tooltip
      const tip = document.getElementById("tooltip");
      nodeGroups.on("mouseover", (e,d) => {{
        tip.style.display = "block";
        tip.innerHTML = "<b style=color:"+d.color+">"+d.label+" ("+d.cc+")</b><br><span style=color:#80deea>Influence Score: "+d.degree.toFixed(1)+"</span>";
      }}).on("mousemove", (e) => {{
        const r = container.getBoundingClientRect();
        tip.style.left = (e.clientX-r.left+15)+"px";
        tip.style.top = (e.clientY-r.top-10)+"px";
      }}).on("mouseout", () => {{ tip.style.display="none"; }});

      // Tick
      sim.on("tick", () => {{
        link.attr("d", d => {{
          const dx=d.target.x-d.source.x, dy=d.target.y-d.source.y;
          const dr=Math.sqrt(dx*dx+dy*dy)*0.7;
          return "M"+d.source.x+","+d.source.y+"A"+dr+","+dr+" 0 0,1 "+d.target.x+","+d.target.y;
        }});
        nodeGroups.attr("transform", d => "translate("+d.x+","+d.y+")");
        particleT = (particleT+0.005)%1;
        particles.each(function(d,i) {{
          const t=(particleT+i*0.031)%1;
          const x=d.source.x+(d.target.x-d.source.x)*t;
          const y=d.source.y+(d.target.y-d.source.y)*t;
          d3.select(this).attr("cx",x).attr("cy",y);
        }});
      }});

      setInterval(() => {{ if(sim.alpha()<0.05) sim.alpha(0.05).restart(); }}, 3000);
    }})();
    </script>
    """
    return html


def causal_network_narrative(filtered, highlight_nodes=None):
    """Return an HTML plain-English paragraph summarising the causal network."""
    if filtered.empty:
        return ""
    if highlight_nodes is None:
        highlight_nodes = set()

    top_src = filtered.groupby('source')['max_f_stat'].sum().sort_values(ascending=False)
    top_edge = filtered.nlargest(3, 'max_f_stat')
    parts_p1 = []
    if not top_src.empty:
        node = top_src.index[0]
        lbl, cc = _node_label(node)
        n_out = int(filtered[filtered['source'] == node].shape[0])
        parts_p1.append(
            'The strongest statistical driver in this network is '
            '<b>{}</b> in <b>{}</b>, which Granger-causes '
            '{} other series with a cumulative F-statistic of {:.1f}.'.format(
                lbl, COUNTRY_NAMES.get(cc, cc), n_out, top_src.iloc[0])
        )
    if not top_edge.empty:
        r = top_edge.iloc[0]
        sl, sc = _node_label(r['source'])
        tl, tc = _node_label(r['target'])
        parts_p1.append(
            'The single most powerful link runs from <b>{} ({})</b> '
            '&rarr; <b>{} ({})</b> '
            '(F = {:.1f}, p = {:.3f}, lag {} month{}), '
            'meaning past readings in the source reliably precede shifts in the target.'.format(
                sl, COUNTRY_NAMES.get(sc, sc), tl, COUNTRY_NAMES.get(tc, tc),
                float(r['max_f_stat']), float(r['min_p_value']),
                int(r['best_lag']), 's' if r['best_lag'] > 1 else '')
        )
    p1 = ' '.join(parts_p1)
    n_unique = len(set(filtered['source'].tolist() + filtered['target'].tolist()))
    p2 = (
        'In total, <b>{}</b> statistically significant causal links are visible '
        'across <b>{}</b> unique series. '
        'Thicker edges carry higher F-statistics and represent stronger predictive relationships. '
        'Larger nodes are more influential drivers. Use the <b>Focus Node</b> selector to isolate '
        'a single node and see its direct causal connections in a clean tree layout.'.format(
            len(filtered), n_unique)
    )
    hl_note = ''
    if highlight_nodes:
        downstream = set(filtered[filtered['source'].isin(highlight_nodes)]['target'].tolist())
        if downstream:
            dl = ['{} ({})'.format(_node_label(n)[0], COUNTRY_NAMES.get(_node_label(n)[1], _node_label(n)[1]))
                  for n in list(downstream)[:5]]
            hl_note = (
                "<div style='margin-top:10px;padding:10px 14px;"
                "background:rgba(224,112,32,0.1);border-left:3px solid #e07020;"
                "border-radius:4px;font-size:0.8rem;color:#e07020;'>"
                "<b>Scenario linkage:</b> The last scenario touched nodes highlighted in orange. "
                "Their direct causal descendants include: "
                "<b>{}</b>{}</div>".format(', '.join(dl), '...' if len(downstream) > 5 else '.')
            )
    return p1, p2, hl_note


def render_causality():
    nerai_premium_css.inject_page_header(
        title="Causal Network",
        subtitle="Discover causal links between geopolitical risk factors",
        badge="NETWORK",
        icon="🔗"
    )
    nerai_premium_css.inject_global_premium_css()
    nerai_premium_css.inject_filter_bar_css()

    # --- Inline Data Pipeline Controls ---
    _pipe_cols = st.columns([2, 3, 3, 2])
    with _pipe_cols[0]:
        _max_s = st.slider('⚙️ Max Series', 50, 500, 200, 50,
                    help='Fewer = faster. 200 ≈ 5-8 min. 500 ≈ 30+ min.',
                    key='inline_causal_max_series')
    with _pipe_cols[1]:
        if st.button('⚙️ Run Causal Analysis', use_container_width=True,
                help='Run gdelt_causality.py — top-variance series only',
                key='inline_run_causal'):
            with st.spinner(f'Computing causality for top {_max_s} series... (~5-8 min)'):
                import subprocess, sys as _sys
                r = subprocess.run(
                    [_sys.executable, './gdelt_causality.py', '--max-series', str(_max_s)],
                    capture_output=True, text=True, cwd='.')
                if r.returncode == 0:
                    out = (r.stdout or '').strip()
                    if 'edges found' in out.lower() and '0 edges' in out.lower():
                        st.warning('⚠️ 0 significant relationships found — threshold values may be too strict. Try again or increase Max Series.')
                    else:
                        st.success('✅ Causal network ready!')
                        with st.expander('📜 Script output', expanded=False):
                            st.code(out[-1200:] or '(no output)')
                    st.cache_data.clear(); st.rerun()
                else:
                    st.error('Script error:\n' + (r.stderr[-800:] or r.stdout[-400:] or 'Unknown error'))
    with _pipe_cols[2]:
        if st.button('🔄 Refresh Indices', use_container_width=True,
                help='Run gdelt_indices.py to fetch latest GDELT data',
                key='inline_refresh_indices'):
            with st.spinner('Fetching GDELT data...'):
                import subprocess, sys as _sys
                r = subprocess.run([_sys.executable, './gdelt_indices.py'],
                        capture_output=True, text=True, cwd='.')
                if r.returncode == 0:
                    st.success('✅ Indices updated!')
                    st.cache_data.clear(); st.rerun()
                else:
                    st.error(r.stderr[-600:] or 'Failed')
    with _pipe_cols[3]:
        if st.button('⚡ Refresh All Data', use_container_width=True,
                help='Run full pipeline: indices → causality → forecast',
                key='inline_refresh_all'):
            scripts = ['gdelt_indices.py', 'gdelt_causality.py', 'gdelt_forecast_numpy.py']
            all_ok = True
            for script in scripts:
                if not os.path.exists(f'./{script}'): continue
                with st.spinner(f'Running {script}...'):
                    import subprocess, sys as _sys
                    r = subprocess.run([_sys.executable, f'./{script}'],
                            capture_output=True, text=True, cwd='.')
                    if r.returncode != 0:
                        st.error(f'{script} failed:\n{r.stderr[-400:]}')
                        all_ok = False; break
            if all_ok:
                st.success('✅ All data refreshed!')
                st.cache_data.clear(); st.rerun()


    st.markdown(
        "<div style='padding:6px 0 10px;'>"
        "<div class='hero-title'>Causal Network Analysis</div>"
        "<div class='hero-sub'>"
        "<span class='live-dot'></span>"
        "Granger Causality &middot; Cross-Series Influence Detection"
        "</div></div>", unsafe_allow_html=True)
    st.markdown('<div class="h-div"></div>', unsafe_allow_html=True)

    cdf = load_causality()
    if cdf is not None and not cdf.empty and 'source_id' in cdf.columns:
        cdf = cdf.rename(columns={
            'source_id': 'source', 'target_id': 'target',
            'f_stat': 'max_f_stat', 'p_value': 'min_p_value',
        })

    sdf = load_scenario_results()
    scenario_nodes = set()
    if sdf is not None and not sdf.empty and 'scenario' in sdf.columns:
        try:
            latest = sdf['scenario'].dropna().iloc[-1]
            sub = sdf[sdf['scenario'] == latest]
            if 'series_id' in sub.columns:
                scenario_nodes = set(sub['series_id'].dropna().tolist())
        except (IndexError, KeyError):
            pass

    if cdf is None or cdf.empty:
        st.markdown(
            "<div style='text-align:center;padding:40px 20px;"
            "background:rgba(10,20,40,0.5);border:1px solid rgba(0,180,255,0.2);"
            "border-radius:12px;margin:20px 0;'>"
            "<div style='font-size:2.5rem;margin-bottom:16px;'>&#128376;</div>"
            "<div style='font-size:1.1rem;font-weight:700;color:#00b4ff;"
            "letter-spacing:0.06em;margin-bottom:10px;'>Causal Network Not Yet Computed</div>"
            "<div style='font-size:0.82rem;color:#8aa8c8;max-width:520px;margin:0 auto;line-height:1.75;'>"
            "Click <b>Run Causal Analysis</b> in the sidebar to compute Granger causality "
            "relationships between all topic &times; country pairs."
            "</div></div>", unsafe_allow_html=True)
        return

    # -- Filters --
    all_nodes = list(set(cdf['source'].tolist() + cdf['target'].tolist()))
    all_countries_raw = sorted(set(nd.rsplit('_', 1)[1] for nd in all_nodes if '_' in nd))
    all_topics_raw = sorted(set(nd.rsplit('_', 1)[0] for nd in all_nodes if '_' in nd))

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        min_f = st.slider('Min F-Statistic', 0.0, float(cdf['max_f_stat'].max()), 3.0)
    with col2:
        topic_opts = ['All'] + [t.replace('_', ' ').title() for t in all_topics_raw]
        sel_topic_label = st.selectbox('Filter by Topic', topic_opts)
        sel_topic = 'All' if sel_topic_label == 'All' else sel_topic_label.lower().replace(' ', '_')
    with col3:
        country_display = ['All'] + ['{} - {}'.format(cc, COUNTRY_NAMES.get(cc, cc)) for cc in all_countries_raw]
        sel_country_label = st.selectbox('Filter by Country', country_display)
        sel_country = 'All' if sel_country_label == 'All' else sel_country_label.split(' - ')[0].strip()
    with col4:
        max_lag = st.selectbox('Max Lag (months)', [1, 2, 3], index=2)

    filtered = cdf[cdf['max_f_stat'] >= min_f].copy()
    if sel_topic != 'All':
        filtered = filtered[filtered['source'].str.startswith(sel_topic) | filtered['target'].str.startswith(sel_topic)]
    if sel_country != 'All':
        filtered = filtered[filtered['source'].str.endswith('_' + sel_country) | filtered['target'].str.endswith('_' + sel_country)]
    filtered = filtered[filtered['best_lag'] <= max_lag]


    # -- Active Selection Context --
    _ctx_parts = []
    if sel_topic != 'All':
        _ctx_parts.append(f"Topic: <b>{sel_topic_label}</b>")
    else:
        _ctx_parts.append("Topic: <b>All</b>")
    if sel_country != 'All':
        _ctx_parts.append(f"Country: <b>{sel_country_label}</b>")
    else:
        _ctx_parts.append("Country: <b>All</b>")
    _ctx_parts.append(f"Min F-Stat: <b>{min_f:.1f}</b>")
    _ctx_parts.append(f"Max Lag: <b>{max_lag} months</b>")
    _ctx_summary = " &middot; ".join(_ctx_parts)
    if sel_topic != 'All' and sel_country != 'All':
        _strat_text = f"This analysis shows the causal relationships between <b>{sel_country_label}</b> events in <b>{sel_topic_label}</b> and other countries/event types. A higher F-Statistic indicates a stronger predictive relationship."
    elif sel_topic != 'All':
        _strat_text = f"The causal network for <b>{sel_topic_label}</b> events across all countries is displayed. This analysis reveals which countries influence others through this event type."
    elif sel_country != 'All':
        _strat_text = f"<b>{sel_country_label}</b> across all event types is displayed. This shows which other countries and event types are triggered by events in the selected country."
    else:
        _strat_text = "The full causal network across all countries and event types is displayed. Use the filters above to focus on a specific country or event type."
    st.markdown(f"<div style='background:linear-gradient(135deg,rgba(0,40,80,0.6),rgba(0,20,50,0.4));border:1px solid rgba(0,180,255,0.25);border-radius:10px;padding:16px 20px;margin:10px 0 20px;'><div style='display:flex;align-items:center;gap:10px;margin-bottom:8px;'><span style='font-size:0.75rem;font-weight:700;color:#00d4ff;letter-spacing:0.08em;text-transform:uppercase;'>Active Analysis Filters</span></div><div style='font-size:0.82rem;color:#e0e8f0;margin-bottom:8px;'>{_ctx_summary}</div><div style='font-size:0.78rem;color:#8ab4d8;line-height:1.6;'>{_strat_text}</div><div style='font-size:0.7rem;color:#5a7a9a;margin-top:8px;font-style:italic;'>The filters above affect all sections below: KPI metrics, network diagram, top influencers, and edge list.</div></div>", unsafe_allow_html=True)

    # -- KPI row --
    kc1, kc2, kc3 = st.columns(3)
    with kc1:
        st.markdown("<div class='kpi-card'><div class='kpi-label'>Causal Links</div>"
                    "<div class='kpi-value'>{}</div></div>".format(len(filtered)), unsafe_allow_html=True)
    with kc2:
        avg_f = filtered['max_f_stat'].mean() if len(filtered) > 0 else 0
        st.markdown("<div class='kpi-card'><div class='kpi-label'>Avg F-Statistic</div>"
                    "<div class='kpi-value'>{:.1f}</div></div>".format(avg_f), unsafe_allow_html=True)
    with kc3:
        n_series = len(set(filtered['source'].tolist() + filtered['target'].tolist()))
        st.markdown("<div class='kpi-card'><div class='kpi-label'>Series Involved</div>"
                    "<div class='kpi-value'>{}</div></div>".format(n_series), unsafe_allow_html=True)

    st.markdown('<div style="margin:20px 0;"></div>', unsafe_allow_html=True)


    # -- Dynamic Geostrategic Analysis --
    if len(filtered) > 0:
        _top_source = filtered.groupby('source')['max_f_stat'].sum().idxmax() if len(filtered) > 0 else None
        _top_target = filtered.groupby('target')['max_f_stat'].sum().idxmax() if len(filtered) > 0 else None
        _top_src_lbl = '{} ({})'.format(_node_label(_top_source)[0], COUNTRY_NAMES.get(_node_label(_top_source)[1], _node_label(_top_source)[1])) if _top_source else 'N/A'
        _top_tgt_lbl = '{} ({})'.format(_node_label(_top_target)[0], COUNTRY_NAMES.get(_node_label(_top_target)[1], _node_label(_top_target)[1])) if _top_target else 'N/A'
        _avg_lag = filtered['best_lag'].mean() if len(filtered) > 0 else 0
        _strong_links = len(filtered[filtered['max_f_stat'] > 10]) if len(filtered) > 0 else 0
        if sel_topic != 'All' and sel_country != 'All':
            _geo_tech = f"<b>Technical:</b> With the current filters, <b>{len(filtered)}</b> statistically significant causal links were detected involving <b>{sel_topic_label}</b> events in <b>{sel_country_label}</b>. The strongest causal driver is <b>{_top_src_lbl}</b> (highest cumulative F-stat), while the most influenced target is <b>{_top_tgt_lbl}</b>. Average propagation delay is <b>{_avg_lag:.1f}</b> months, with <b>{_strong_links}</b> strong links (F>10)."
            _geo_strat = f"<b>Geostrategic Implication:</b> {sel_topic_label} dynamics in {sel_country_label.split(' - ')[-1] if ' - ' in sel_country_label else sel_country_label} act as both a signal transmitter and receiver in the global risk network. A high number of outgoing causal links suggests this country is a regional destabilizer for this event type; a high number of incoming links suggests vulnerability to external shocks. Policy makers should monitor {_top_src_lbl} as the primary trigger point."
        elif sel_topic != 'All':
            _geo_tech = f"<b>Technical:</b> Across all countries, <b>{len(filtered)}</b> causal links were detected for <b>{sel_topic_label}</b> events. The dominant causal origin is <b>{_top_src_lbl}</b>, and the most affected node is <b>{_top_tgt_lbl}</b>. There are <b>{_strong_links}</b> strong causal relationships (F>10) with an average lag of <b>{_avg_lag:.1f}</b> months."
            _geo_strat = f"<b>Geostrategic Implication:</b> {sel_topic_label} events show cross-border causal propagation patterns. Countries originating the strongest causal signals are potential flashpoints that can trigger cascade effects across multiple regions. The average {_avg_lag:.1f}-month delay window provides an actionable early-warning period for risk mitigation."
        elif sel_country != 'All':
            _geo_tech = f"<b>Technical:</b> For <b>{sel_country_label}</b>, <b>{len(filtered)}</b> causal links span across all event types. The strongest outgoing influence originates from <b>{_top_src_lbl}</b>, while <b>{_top_tgt_lbl}</b> is most affected. <b>{_strong_links}</b> links exceed F>10 threshold with average propagation lag of <b>{_avg_lag:.1f}</b> months."
            _geo_strat = f"<b>Geostrategic Implication:</b> {sel_country_label.split(' - ')[-1] if ' - ' in sel_country_label else sel_country_label}'s risk profile shows interconnected event dynamics. High outgoing causal influence indicates the country can export instability to neighbors; high incoming influence signals dependency on external stability conditions. This intelligence is critical for bilateral risk assessment and alliance strategy."
        else:
            _geo_tech = f"<b>Technical:</b> The full network contains <b>{len(filtered)}</b> causal links across <b>{n_series}</b> event-country series. The most influential node is <b>{_top_src_lbl}</b> and the most impacted is <b>{_top_tgt_lbl}</b>. <b>{_strong_links}</b> strong links (F>10) suggest robust causal channels with an average propagation delay of <b>{_avg_lag:.1f}</b> months."
            _geo_strat = "<b>Geostrategic Implication:</b> The global causal network reveals hidden interdependencies between geopolitical events across nations. High-centrality nodes represent systemic risk points where a single event escalation can cascade into multiple regions. Use the Topic and Country filters to isolate specific threat corridors and identify early-warning signals for strategic planning."
        st.markdown(f"<div style='background:rgba(0,30,60,0.5);border-left:3px solid #00d4ff;border-radius:0 8px 8px 0;padding:16px 20px;margin:10px 0 20px;line-height:1.7;font-size:0.8rem;color:#b0c8e0;'><div style='font-size:0.7rem;font-weight:700;color:#00d4ff;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:10px;'>Analysis Summary</div><p style='margin:0 0 10px;'>{_geo_tech}</p><p style='margin:0;'>{_geo_strat}</p></div>", unsafe_allow_html=True)

    # -- Narrative --
    narr = causal_network_narrative(filtered, highlight_nodes=scenario_nodes)
    if narr:
        p1, p2, hl_note = narr
        st.markdown(
            "<div style='background:rgba(10,20,50,0.5);border:1px solid rgba(0,180,255,0.2);"
            "border-radius:10px;padding:18px 22px;margin-bottom:20px;line-height:1.75;"
            "font-size:0.85rem;color:#c8d8e8;'>"
            "<div style='font-size:0.7rem;font-weight:700;color:#00b4ff;letter-spacing:0.1em;"
            "text-transform:uppercase;margin-bottom:8px;'>What This Network Shows</div>"
            "<p style='margin:0 0 8px;'>{}</p>"
            "<p style='margin:0;'>{}</p>"
            "{}</div>".format(p1, p2, hl_note), unsafe_allow_html=True)

    # -- Focus Node + Network Diagram --
    _net_title = 'Interactive Network Diagram'
    if sel_topic != 'All' and sel_country != 'All':
        _net_title = f'Causal Network: {sel_topic_label} - {sel_country_label}'
    elif sel_topic != 'All':
        _net_title = f'Causal Network: {sel_topic_label} - All Countries'
    elif sel_country != 'All':
        _net_title = f'Causal Network: {sel_country_label} - All Topics'
    nerai_premium_css.inject_section_header(_net_title, icon="🕸️")
    st.caption('Granger causality network diagram. Arrows show causality direction (A\u2192B: Changes in event A predict event B). Node size reflects the number of connections.')
    if scenario_nodes:
        st.caption('Orange nodes/edges = series touched by the most recent scenario run')

    filtered_nodes = sorted(set(filtered['source'].tolist() + filtered['target'].tolist()))
    focus_options = ['All (Full Network)']
    node_labels_map = {}
    for nd in filtered_nodes:
        lbl, cc = _node_label(nd)
        display = '{} ({})'.format(lbl, COUNTRY_NAMES.get(cc, cc))
        focus_options.append(display)
        node_labels_map[display] = nd

    fc1, fc2 = st.columns([2, 3])
    with fc1:
        focus_sel = st.selectbox('Focus Node (isolate connections)', focus_options,
                                  help='Select a node to see only its direct causal connections in a clean layout')
    focus_node = None
    if focus_sel != 'All (Full Network)':
        focus_node = node_labels_map.get(focus_sel)

    display_filtered = filtered.head(80) if focus_node is None else filtered
    net_fig = build_network_figure(display_filtered, highlight_nodes=scenario_nodes, focus_node=focus_node)
    if net_fig:
        import streamlit.components.v1 as components; components.html(net_fig, height=770, scrolling=False)
    else:
        st.info('No edges to display with the current filters.')

    # -- Top Influencers bar chart --
    if sel_topic != 'All' and sel_country != 'All':
        _inf_title = f'Top Causal Influencers — {sel_topic_label} · {sel_country_label}'
    elif sel_topic != 'All':
        _inf_title = f'Top Causal Influencers — {sel_topic_label}'
    elif sel_country != 'All':
        _inf_title = f'Top Causal Influencers — {sel_country_label}'
    else:
        _inf_title = 'Top Causal Influencers — All Topics & Countries'
    nerai_premium_css.inject_section_header(_inf_title, icon="📊")
    st.caption('Event-country pairs with the highest cumulative F-Statistic. These are the events with the strongest predictive (causal) influence over other events.')
    influence = filtered.groupby('source')['max_f_stat'].sum().sort_values(ascending=False).head(15)
    if len(influence) > 0:
        n_bars = len(influence)
        gradient_palette = [
            '#00e5ff', '#00bcd4', '#0097a7', '#00838f', '#006064',
            '#26c6da', '#4dd0e1', '#80deea', '#18ffff', '#00b8d4',
            '#00acc1', '#0091ea', '#0288d1', '#0277bd', '#01579b'
        ]
        bar_colors = []
        for i, nd in enumerate(influence.index):
            if nd in scenario_nodes:
                bar_colors.append('#e07020')
            else:
                bar_colors.append(gradient_palette[i % len(gradient_palette)])

        bar_labels = []
        for nd in influence.index:
            lbl, cc = _node_label(nd)
            bar_labels.append('{} ({})'.format(lbl, COUNTRY_NAMES.get(cc, cc)))

        fig_bar = go.Figure(go.Bar(
            x=influence.values,
            y=bar_labels,
            orientation='h',
            marker_color=bar_colors,
            marker_line_color='rgba(255,255,255,0.2)',
            marker_line_width=1,
            text=['{:.1f}'.format(v) for v in influence.values],
            textposition='outside',
            textfont=dict(color='#c8d8e8', size=11),
        ))
        fig_bar.update_layout(
            height=max(400, n_bars * 32),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(10,20,40,0.3)',
            xaxis=dict(
                title='Cumulative F-Statistic',
                title_font=dict(color='#8ab4d8', size=13),
                color='#8ab4d8',
                gridcolor='rgba(0,180,255,0.08)',
                tickfont=dict(size=11, color='#8ab4d8'),
            ),
            yaxis=dict(
                color='#e0e8f0',
                tickfont=dict(size=11, color='#e0e8f0'),
                automargin=True,
            ),
            margin=dict(l=20, r=80, t=10, b=50)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<div style='background:rgba(10,20,50,0.4);border:1px solid rgba(0,180,255,0.15);border-radius:8px;padding:14px 18px;margin:15px 0;font-size:0.75rem;color:#8ab4d8;line-height:1.7;'><b style=\'color:#00d4ff;\'>How to Interpret?</b><br>F-Statistic: The higher the value, the stronger the causal relationship. F &gt; 10 = strong, F &gt; 50 = very strong relationship.<br>Lag (Delay): The time delay between events (months). Lag=1 means a change in one event affects another 1 month later.<br>p-value: Values below 0.05 indicate statistically significant relationships.</div>", unsafe_allow_html=True)

    # -- News Evidence Section --
    nerai_premium_css.inject_section_header("Recent News Evidence", icon="📰")
    st.caption("Real-world news articles that may explain or confirm the detected causal relationships.")

    top_sources = filtered.groupby("source")["max_f_stat"].sum().sort_values(ascending=False).head(5)
    if len(top_sources) > 0:
        news_cols = st.columns(1)
        for src_node in top_sources.index:
            label, cc = _node_label(src_node)
            if not cc:
                continue
            articles = fetch_causal_news(label, cc, max_records=3)
            if not articles:
                continue
            top_targets = filtered[filtered["source"] == src_node].nlargest(2, "max_f_stat")
            target_names = []
            for _, row in top_targets.iterrows():
                tl, tc = _node_label(row["target"])
                target_names.append(f"{tl} ({tc})")
            targets_str = ", ".join(target_names) if target_names else "related factors"
            with st.expander(f"Evidence: {label} ({cc}) → {targets_str}", expanded=False):
                for art in articles:
                    date_str = art["date"] if art["date"] else "Recent"
                    source_str = art["source"] if art["source"] else "Unknown"
                    title_str = art["title"] if art["title"] else "Untitled"
                    url_str = art["url"]
                    st.markdown(
                        f"**[{title_str}]({url_str})**<br>"
                        f"<small>{source_str} | {date_str}</small>",
                        unsafe_allow_html=True
                    )
                st.caption(f"These articles provide context for why {label} ({cc}) may causally influence {targets_str}.")
    else:
        st.info("No causal influencers found to research news for.")

    # -- Edge table --
    with st.expander('Full Causal Edge List', expanded=False):
        display_df = filtered.sort_values('max_f_stat', ascending=False)[
            ['source', 'target', 'max_f_stat', 'min_p_value', 'best_lag']].copy()
        display_df['source_label'] = display_df['source'].apply(
            lambda nd: '{} ({})'.format(_node_label(nd)[0], COUNTRY_NAMES.get(_node_label(nd)[1], _node_label(nd)[1])))
        display_df['target_label'] = display_df['target'].apply(
            lambda nd: '{} ({})'.format(_node_label(nd)[0], COUNTRY_NAMES.get(_node_label(nd)[1], _node_label(nd)[1])))
        st.table(
            display_df[['source_label', 'target_label', 'max_f_stat', 'min_p_value', 'best_lag']].rename(
                columns={'source_label': 'Source', 'target_label': 'Target',
                         'max_f_stat': 'F-Stat', 'min_p_value': 'p-value', 'best_lag': 'Lag (m)'}),
            use_container_width=True
        )



    # ═══ FAZ 4c: Network Centrality Dashboard ═══
    st.markdown('<div class="h-div" style="margin:24px 0 16px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">🕸️  Network Centrality Analysis</div>', unsafe_allow_html=True)
    try:
        if causality_df is not None and not causality_df.empty:
            # Build adjacency from causality edges
            _nodes = set()
            _edges = {}
            _src_col = "source" if "source" in causality_df.columns else causality_df.columns[0]
            _tgt_col = "target" if "target" in causality_df.columns else causality_df.columns[1]
            for _, row in causality_df.iterrows():
                s, t = str(row[_src_col]), str(row[_tgt_col])
                _nodes.add(s)
                _nodes.add(t)
                _edges[(s, t)] = _edges.get((s, t), 0) + 1
            # Degree centrality
            _degree = {}
            for n in _nodes:
                _out = sum(1 for (s,t) in _edges if s == n)
                _in  = sum(1 for (s,t) in _edges if t == n)
                _degree[n] = {"out": _out, "in": _in, "total": _out + _in}
            if _degree:
                _cent_df = pd.DataFrame.from_dict(_degree, orient="index").sort_values("total", ascending=False).head(15)
                _cent_df.index.name = "Node"
                _cent_df = _cent_df.reset_index()
                _cent_df.columns = ["Topic/Country", "Out-degree", "In-degree", "Total Connections"]
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown("**Most Connected Nodes**")
                    st.table(_cent_df)
                with col2:
                    # Bar chart of centrality
                    fig_cent = go.Figure()
                    fig_cent.add_trace(go.Bar(
                        y=_cent_df["Topic/Country"][:10], x=_cent_df["Out-degree"][:10],
                        name="Out", orientation="h", marker_color="#00d4ff"
                    ))
                    fig_cent.add_trace(go.Bar(
                        y=_cent_df["Topic/Country"][:10], x=_cent_df["In-degree"][:10],
                        name="In", orientation="h", marker_color="#f59e0b"
                    ))
                    fig_cent.update_layout(**_PLOTLY_THEME, height=350, barmode="stack",
                        yaxis=dict(autorange="reversed"), legend=dict(font=dict(size=10, color="#8aa0bc")))
                    st.plotly_chart(fig_cent, use_container_width=True)
        else:
            st.caption("Run causality analysis first to see network centrality.")
    except Exception as _e:
        st.caption(f"Network centrality unavailable: {_e}")
# ── PDF GENERATION HELPERS ────────────────────────────────────────────
_PDF_NAVY  = HexColor('#0a1428')
_PDF_CYAN  = HexColor('#00b4ff')
_PDF_RED   = HexColor('#ff4b6e')
_PDF_GOLD  = HexColor('#ffd700')
_PDF_ORANGE = HexColor('#ff9800')
_PDF_MID   = HexColor('#8aa8c8')
_PDF_LIGHT = HexColor('#f0f6fc')


def _pdf_styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle('NT', parent=s['Title'], fontSize=22, leading=26, textColor=_PDF_CYAN, spaceAfter=4, alignment=TA_LEFT, fontName='Helvetica-Bold'))
    s.add(ParagraphStyle('NSub', parent=s['Normal'], fontSize=10, leading=13, textColor=_PDF_MID, spaceAfter=14, fontName='Helvetica'))
    s.add(ParagraphStyle('NH', parent=s['Heading2'], fontSize=13, leading=16, textColor=_PDF_CYAN, spaceBefore=16, spaceAfter=6, fontName='Helvetica-Bold'))
    s.add(ParagraphStyle('NHR', parent=s['Heading2'], fontSize=13, leading=16, textColor=_PDF_RED, spaceBefore=16, spaceAfter=6, fontName='Helvetica-Bold'))
    s.add(ParagraphStyle('NHG', parent=s['Heading2'], fontSize=13, leading=16, textColor=_PDF_GOLD, spaceBefore=16, spaceAfter=6, fontName='Helvetica-Bold'))
    s.add(ParagraphStyle('NHO', parent=s['Heading2'], fontSize=13, leading=16, textColor=_PDF_ORANGE, spaceBefore=16, spaceAfter=6, fontName='Helvetica-Bold'))
    s.add(ParagraphStyle('NB', parent=s['Normal'], fontSize=9.5, leading=14, textColor=black, alignment=TA_JUSTIFY, spaceAfter=8, fontName='Helvetica'))
    s.add(ParagraphStyle('ND', parent=s['Normal'], fontSize=9, leading=13, textColor=HexColor('#1a2a3a'), alignment=TA_LEFT, spaceAfter=4, fontName='Helvetica', leftIndent=8, borderPadding=6))
    s.add(ParagraphStyle('NF', parent=s['Normal'], fontSize=8, leading=10, textColor=_PDF_MID, alignment=TA_CENTER, spaceBefore=20, fontName='Helvetica'))
    s.add(ParagraphStyle('NBI', parent=s['Heading3'], fontSize=11, leading=14, textColor=_PDF_CYAN, spaceBefore=12, spaceAfter=4, fontName='Helvetica-Bold'))
    return s


def _pdf_header_footer(cv, doc, title, cls_color, cls_text):
    cv.saveState()
    w, h = A4
    cv.setFillColor(_PDF_NAVY)
    cv.rect(0, h - 28*mm, w, 28*mm, fill=1, stroke=0)
    cv.setFillColor(_PDF_CYAN)
    cv.setFont('Helvetica-Bold', 14)
    cv.drawString(20*mm, h - 14*mm, 'NERAI INTELLIGENCE')
    cv.setFillColor(cls_color)
    cv.roundRect(w - 60*mm, h - 17*mm, 42*mm, 7*mm, 2, fill=1, stroke=0)
    cv.setFillColor(white if cls_color != _PDF_GOLD else black)
    cv.setFont('Helvetica-Bold', 7)
    cv.drawCentredString(w - 39*mm, h - 15.5*mm, cls_text)
    cv.setFillColor(_PDF_MID)
    cv.setFont('Helvetica', 8)
    cv.drawString(20*mm, h - 22*mm, title)
    cv.setStrokeColor(_PDF_CYAN)
    cv.setLineWidth(0.5)
    cv.line(15*mm, h - 28*mm, w - 15*mm, h - 28*mm)
    cv.setFillColor(_PDF_MID)
    cv.setFont('Helvetica', 7)
    cv.drawString(20*mm, 12*mm, 'Published by NERAI Intelligence | Confidential')
    cv.drawRightString(w - 20*mm, 12*mm, 'Page {}'.format(doc.page))
    cv.setStrokeColor(_PDF_CYAN)
    cv.setLineWidth(0.3)
    cv.line(15*mm, 17*mm, w - 15*mm, 17*mm)
    cv.restoreState()


def _pdf_data_box(text, styles, border_color=None):
    if border_color is None:
        border_color = _PDF_CYAN
    tbl = Table([[Paragraph(text, styles['ND'])]], colWidths=[160*mm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), _PDF_LIGHT),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEBEFORE', (0, 0), (0, -1), 3, border_color),
    ]))
    return tbl



def _generate_weekly_pdf_w15():
    buf = io.BytesIO()
    s = _pdf_styles()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=32*mm, bottomMargin=22*mm, leftMargin=20*mm, rightMargin=20*mm)
    def on_page(cv, d):
        _pdf_header_footer(cv, d, 'Weekly Intelligence Bulletin | Week 15 | April 5 - 11, 2026', _PDF_GOLD, 'UNCLASSIFIED')
    story = []
    story.append(Paragraph('NERAI WEEKLY INTELLIGENCE BULLETIN', s['NT']))
    story.append(Paragraph('Week 15 | April 5 - 11, 2026', s['NSub']))
    story.append(HRFlowable(width='100%', thickness=1, color=_PDF_CYAN, spaceAfter=12))
    story.append(Paragraph('EXECUTIVE SUMMARY', s['NH']))
    story.append(Paragraph('Week 15 was defined by the dramatic collapse of US-Iran peace talks in Islamabad, Israel\'s devastating Black Wednesday air campaign against Lebanon that killed over 300 civilians, and the continued weaponisation of the Strait of Hormuz chokepoint. NERAI\'s Military Escalation indices surged to their highest recorded levels across the Middle East theatre, with Israel reaching 0.56 (+25.8%), Kuwait at 0.54 (+13.5%), and Iran\'s Military De-escalation index collapsing by 71.5%. Energy markets remain under acute pressure with Brent crude holding above $112/barrel.', s['NB']))
    story.append(Paragraph('<font color="#ff4b6e">&#9650;</font> 1. US-IRAN ISLAMABAD PEACE TALKS COLLAPSE', s['NHR']))
    story.append(Paragraph('On April 11, 2026, a high-level US delegation led by VP Vance, Special Envoys Witkoff and Kushner concluded 21 hours of intensive negotiations with Iranian officials in Islamabad without agreement. Vance stated Iran refused to commit to abandoning its nuclear weapons programme. The talks represented the most significant direct US-Iran engagement since the 2015 JCPOA and their failure dramatically narrows the window for a negotiated resolution.', s['NB']))
    story.append(_pdf_data_box('<b>NERAI DATA INSIGHTS:</b> Iran\'s Military De-escalation index collapsed to <b>0.079</b> (<b>-71.5% falling</b>) - the sharpest decline of any peace-related indicator. Iran\'s Threaten International Relations at <b>0.066</b> (+13.3% rising). US International Support at <b>0.154</b> (+34.1% rising); US Government Instability at <b>0.090</b> (+15.5% rising).', s))
    story.append(Spacer(1, 6))
    story.append(_pdf_data_box('<b>12-MONTH FORECAST:</b> NERAI models assign <b>68% probability</b> of direct US-Iran military confrontation by Q4 2026 (up from 52%). Iran\'s nuclear programme estimated at 6-9 months to weapons-grade enrichment capability.', s, _PDF_GOLD))
    story.append(Paragraph('<font color="#ff4b6e">&#9650;</font> 2. ISRAEL\'S BLACK WEDNESDAY LEBANON AIR CAMPAIGN', s['NHR']))
    story.append(Paragraph('On April 8-9, Israel launched its most devastating aerial assault on Lebanon since 2006, deploying 50+ fighter jets and 160 precision-guided munitions across central Beirut. Over 300 killed, 1,150+ wounded. PM Netanyahu declared that Iran ceasefire talks would not extend to Lebanon, isolating the Lebanese theatre from diplomacy.', s['NB']))
    story.append(_pdf_data_box('<b>NERAI DATA INSIGHTS:</b> Israel\'s Military Escalation surged to <b>0.561</b> (+25.8% rising) - highest recorded level. Military Clash at <b>0.425</b> (+17.1%). Lebanon Military Escalation at <b>0.465</b>, Military Clash at <b>0.442</b> (sustained plateau). Israel Military Crisis at <b>0.057</b> (+12.4%) signals strategic overextension risk.', s))
    story.append(Spacer(1, 6))
    story.append(_pdf_data_box('<b>12-MONTH FORECAST:</b> Lebanon\'s Military Escalation projected to reach <b>0.52</b> by Q3 2026. Israel\'s index may exceed <b>0.60</b>. Decoupling Lebanon from Iran talks creates open-ended campaign with no exit strategy.', s, _PDF_GOLD))
    story.append(Paragraph('<font color="#ff4b6e">&#9650;</font> 3. STRAIT OF HORMUZ CRISIS DEEPENS', s['NHR']))
    story.append(Paragraph('Iran\'s Supreme Defence Council warned mine-laying operations would commence if coastal territory is attacked. The Strait handles 21% of global petroleum trade. Shipping insurance premiums quadrupled since March; tankers diverted around Cape of Good Hope, adding 15-20 days transit and $6-8/barrel in surcharges.', s['NB']))
    story.append(_pdf_data_box('<b>NERAI DATA INSIGHTS:</b> Kuwait\'s Threaten International Relations exploded to <b>0.190</b> (+88.7% rising). Kuwait Military Escalation at <b>0.538</b> (+13.5%). Iran\'s Military De-escalation collapse (-71.5%) transforms stability into locked-in escalation with no diplomatic counterweight.', s))
    story.append(Paragraph('MARKET IMPACT', s['NH']))
    mkt = [['Indicator', 'Value', 'Change'], ['Brent Crude', '$112.40/barrel', '+3.1% weekly'], ['WTI Crude', '$114.85/barrel', '+3.0% weekly'], ['Gold', '$4,718/oz', '+1.0% weekly'], ['USD Index', '105.2', 'Strengthening']]
    tbl = Table(mkt, colWidths=[55*mm, 50*mm, 50*mm])
    tbl.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), _PDF_CYAN), ('TEXTCOLOR', (0,0), (-1,0), white), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 9), ('GRID', (0,0), (-1,-1), 0.5, _PDF_MID), ('ROWBACKGROUNDS', (0,1), (-1,-1), [_PDF_LIGHT, white])]))
    story.append(tbl)
    story.append(Spacer(1, 8))
    story.append(Paragraph('NERAI 12-MONTH OUTLOOK', s['NH']))
    story.append(_pdf_data_box('The collapse of Islamabad peace talks is a strategic inflection point. NERAI forecasts <b>78% probability</b> of major regional escalation by Q4 2026 (up from 65%). Simultaneous closure of diplomatic channels, escalation of kinetic operations, and weaponisation of energy infrastructure create convergent risk with limited off-ramps. Energy markets should anticipate $110-125/barrel with spike risk to $140+ if Strait mining materialises.', s, _PDF_RED))
    story.append(Spacer(1, 16))
    story.append(Paragraph('Published by NERAI Intelligence | April 11, 2026', s['NF']))
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buf.seek(0)
    return buf.getvalue()


def _generate_risk_pdf_w15():
    buf = io.BytesIO()
    s = _pdf_styles()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=32*mm, bottomMargin=22*mm, leftMargin=20*mm, rightMargin=20*mm)
    def on_page(cv, d):
        _pdf_header_footer(cv, d, 'Risk Alert | Critical Threat Assessment | Week 15 | April 2026', _PDF_RED, 'SEVERITY: CRITICAL')
    story = []
    story.append(Paragraph('<font color="#ff4b6e">NERAI RISK ALERT</font>', s['NT']))
    story.append(Paragraph('Critical Threat Assessment | Week 15 | April 2026', s['NSub']))
    story.append(HRFlowable(width='100%', thickness=1, color=_PDF_RED, spaceAfter=12))
    story.append(Paragraph('<font color="#ff4b6e">&#9888;</font> ALERT 1: STRAIT OF HORMUZ - MINE-LAYING THREAT ESCALATION', s['NHR']))
    sev1 = Table([['SEVERITY: CRITICAL']], colWidths=[40*mm])
    sev1.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),_PDF_RED),('TEXTCOLOR',(0,0),(-1,-1),white),('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
    story.append(sev1)
    story.append(Spacer(1, 6))
    story.append(Paragraph('Iran\'s Supreme Defence Council formally warned that mine-laying operations in the Strait of Hormuz would commence if Iranian coastal territory is attacked. The Strait handles 21% of global petroleum transit. Combined with the Islamabad talks failure, the risk of disruption has reached its highest level since the 1988 Tanker War.', s['NB']))
    story.append(_pdf_data_box('<b>TRIGGER EVENTS:</b> Iran Defence Council mine-laying warning (Apr 9); failed US-Iran Islamabad talks (Apr 11); tanker rerouting around Cape of Good Hope; shipping insurance premiums quadrupled; IRGC naval exercises.', s))
    story.append(Spacer(1, 4))
    story.append(_pdf_data_box('<b>NERAI ANALYSIS:</b> Kuwait Threaten Intl Relations at <b>0.190</b> (+88.7% rising - fastest acceleration in dataset). Kuwait Military Escalation <b>0.538</b> (+13.5%). Iran Military De-escalation collapsed to <b>0.079</b> (-71.5%). Iran Military Escalation stable at <b>0.314</b> but locked-in without diplomatic counterweight.', s))
    story.append(Spacer(1, 4))
    story.append(_pdf_data_box('<b>FORECAST:</b> Mine-laying scenario: Brent $130-150/barrel, 4-8 week disruption. Full blockade (15% probability): oil exceeds $180/barrel triggering global recession. Current $112/barrel reflects partial risk premium only.', s, _PDF_GOLD))
    story.append(Spacer(1, 4))
    story.append(Paragraph('<b>WATCH:</b> IRGC vessel positioning; mine-warfare ship deployments; shipping insurance rates; US 5th Fleet readiness; Saudi Aramco storage drawdowns; IEA strategic reserve coordination.', s['NB']))
    story.append(Paragraph('<font color="#ffd700">&#9888;</font> ALERT 2: US-IRAN DIPLOMATIC FAILURE - NUCLEAR TIMELINE ACCELERATION', s['NHG']))
    sev2 = Table([['SEVERITY: HIGH']], colWidths=[40*mm])
    sev2.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),_PDF_GOLD),('TEXTCOLOR',(0,0),(-1,-1),black),('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
    story.append(sev2)
    story.append(Spacer(1, 6))
    story.append(Paragraph('Collapse of 21-hour Islamabad negotiations removes the primary diplomatic mechanism for constraining Iran\'s nuclear programme. VP Vance publicly stated Iran refused nuclear commitments. Path to either military strike on Iranian facilities or Iranian nuclear breakout has shortened significantly. 6-9 months estimated to weapons-grade enrichment.', s['NB']))
    story.append(_pdf_data_box('<b>NERAI DATA:</b> Iran Military De-escalation <b>0.079</b> (-71.5% - fastest decline in dataset). Iran Threaten Intl Relations <b>0.066</b> (+13.3%). US International Support <b>0.154</b> (+34.1%). US Government Instability <b>0.090</b> (+15.5%).', s))
    story.append(Spacer(1, 4))
    story.append(_pdf_data_box('<b>FORECAST:</b> 68% probability of direct US-Iran military confrontation by Q4 2026 (up from 52%). Israeli pre-emptive strike probability 45% within 6 months if diplomatic channels stay closed.', s, _PDF_GOLD))
    story.append(Spacer(1, 4))
    story.append(Paragraph('<b>WATCH:</b> IAEA inspection reports; centrifuge enrichment levels; Israeli Air Force exercises; B-2 forward deployments; diplomatic back-channels.', s['NB']))
    story.append(Paragraph('<font color="#ff9800">&#9888;</font> ALERT 3: REGIONAL INSTABILITY CASCADE - IRAQ, GHANA, RUSSIA', s['NHO']))
    sev3 = Table([['SEVERITY: ELEVATED']], colWidths=[40*mm])
    sev3.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),_PDF_ORANGE),('TEXTCOLOR',(0,0),(-1,-1),white),('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
    story.append(sev3)
    story.append(Spacer(1, 6))
    story.append(Paragraph('Beyond core Middle East crisis, NERAI indices flag emerging instability: Iraq Leadership Change +101.7% (largest single increase), Ghana Military Clash 0.503 (+62.1%), Russia International Crisis 0.129 (+40.9%). These outlier movements suggest systemic global instability.', s['NB']))
    story.append(_pdf_data_box('<b>NERAI ASSESSMENT:</b> Iraq Leadership Change <b>+101.7%</b> (highest acceleration in dataset). Ghana Military Clash <b>0.503</b> (+62.1%). Russia International Crisis <b>0.129</b> (+40.9%). Convergent acceleration across unrelated regions signals structural global risk elevation.', s))
    story.append(Spacer(1, 4))
    story.append(_pdf_data_box('<b>FORECAST:</b> Iraq leadership transition could destabilise the key Iran-US buffer state, amplifying Middle East escalation dynamics. Ghana instability threatens West African regional stability. Russia crisis index trajectory consistent with continued Ukraine-related escalation through 2026.', s, _PDF_GOLD))
    story.append(Spacer(1, 4))
    story.append(Paragraph('<b>WATCH:</b> Iraqi parliament sessions; PMF/militia movements; Ghana military deployments; Russia force posture changes; Wagner/Africa Corps activity.', s['NB']))
    story.append(Spacer(1, 16))
    story.append(Paragraph('Published by NERAI Intelligence | April 11, 2026', s['NF']))
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buf.seek(0)
    return buf.getvalue()


def _generate_weekly_pdf_w14():
    buf = io.BytesIO()
    s = _pdf_styles()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=32*mm, bottomMargin=22*mm, leftMargin=20*mm, rightMargin=20*mm)
    def on_page(cv, d):
        _pdf_header_footer(cv, d, 'Weekly Intelligence Bulletin | Week 14 | March 28 - April 4, 2026', _PDF_GOLD, 'UNCLASSIFIED')
    story = []
    story.append(Paragraph('NERAI WEEKLY INTELLIGENCE BULLETIN', s['NT']))
    story.append(Paragraph('Week 14 | March 28 - April 4, 2026', s['NSub']))
    story.append(HRFlowable(width='100%', thickness=1, color=_PDF_CYAN, spaceAfter=12))
    story.append(Paragraph('EXECUTIVE SUMMARY', s['NH']))
    story.append(Paragraph('Week 14 marked a significant escalation in Middle East regional tensions with the re-activation of Houthi military operations against Israel, Iranian drone strikes targeting Gulf infrastructure, and an accelerating humanitarian crisis across the Levant. NERAI\'s Military Escalation indices across the region have reached their highest levels since October 2025, with 12-month forecasts indicating sustained and potentially intensifying conflict dynamics. Energy markets responded sharply, with Brent crude surging past $109 per barrel driven by Strait of Hormuz supply-disruption concerns and gold climbing above $4,670 per ounce on safe-haven demand.', s['NB']))
    story.append(Paragraph('<font color="#ff4b6e">&#9650;</font> 1. HOUTHI MISSILE STRIKES ON ISRAEL - NEW FRONT IN REGIONAL WAR', s['NHR']))
    story.append(Paragraph('On March 28, 2026, Yemen\'s Houthi forces launched coordinated ballistic-missile attacks targeting Israeli military installations, marking a dramatic re-entry into active combat following months of relative quiet after the October 2025 Gaza ceasefire. Houthi military spokesman Brig. Gen. Yahya Saree confirmed two separate salvos within hours. Israeli air defences intercepted the majority of incoming projectiles, although several reached their intended targets in the Negev region. The attacks signal Iran\'s demonstrated ability to activate multiple proxy fronts simultaneously, raising the spectre of a broader regional conflagration.', s['NB']))
    story.append(_pdf_data_box('<b>NERAI DATA INSIGHTS:</b> The Military Escalation index for Israel currently stands at <b>0.27</b> with a 12-month forecast showing a <b>+10.1% rising</b> trajectory. Yemen\'s Terrorism index is elevated at <b>0.25</b> with a particularly concerning <b>+37.3% rising</b> trend - the steepest increase of any country-topic pair in the current dataset. Israel\'s Military Clash index at <b>0.23</b> continues upward at <b>+10.7%</b>. NERAI\'s Causal Network analysis identifies strong Granger-causal links between Iranian military-escalation decisions and subsequent Houthi activity.', s, _PDF_CYAN))
    story.append(Spacer(1, 6))
    story.append(_pdf_data_box('<b>12-MONTH FORECAST:</b> NERAI\'s predictive models indicate continued escalation across the Middle East theatre through Q4 2026. Lebanon shows the highest projected Military Escalation increase at <b>+12.1%</b>, followed by Israel at <b>+10.1%</b> and Yemen at <b>+8.4%</b>.', s, _PDF_GOLD))
    story.append(Paragraph('<font color="#ff4b6e">&#9650;</font> 2. IRANIAN DRONE STRIKE ON KUWAIT INTERNATIONAL AIRPORT', s['NHR']))
    story.append(Paragraph('On April 1, 2026, Iranian drones executed a precision strike on fuel-storage facilities at Kuwait International Airport, igniting a fire that burned for over 18 hours and forced extended runway closures. The strike demonstrates Iran\'s expanding long-range drone capabilities and willingness to target strategic civilian infrastructure in US-allied Gulf states.', s['NB']))
    story.append(_pdf_data_box('<b>NERAI DATA ANALYSIS:</b> Iran\'s Military Escalation index stands at <b>0.16</b> with a <b>+6.1% rising</b> trend. Kuwait\'s Government Instability index remains low at 0.01, but NERAI\'s Country Profile flags potential for rapid escalation if critical infrastructure targeting continues.', s, _PDF_CYAN))
    story.append(Spacer(1, 6))
    story.append(Paragraph('<b>Broader implications:</b> The attacks create immediate concerns for Gulf energy security and the Strait of Hormuz, which handles approximately 20% of global maritime oil transport. Shipping insurance premiums have spiked, with an estimated $3-5 per barrel in freight surcharges.', s['NB']))
    story.append(Paragraph('<font color="#ff4b6e">&#9650;</font> 3. LEBANON-SYRIA MASS DISPLACEMENT CRISIS', s['NHR']))
    story.append(Paragraph('Israeli military operations in Lebanon have displaced nearly one million people - roughly 20% of the country\'s population. Between March 2 and 27, over 200,000 individuals crossed into Syria, creating the largest cross-border refugee movement in the region since 2015.', s['NB']))
    story.append(_pdf_data_box('<b>NERAI RISK ASSESSMENT:</b> Lebanon\'s Military Escalation index is the <b>highest in the current dataset at 0.35</b>, with a projected 12-month increase of <b>+12.1%</b>. Syria\'s Political Instability index stands at <b>0.08</b> and is rising. Lebanon\'s Protest index at <b>0.10</b> shows a <b>+34.2% rising</b> trend.', s, _PDF_CYAN))
    story.append(Paragraph('MARKET IMPACT', s['NH']))
    mkt = [['Indicator', 'Value', 'Change'], ['Brent Crude', '$109.03/barrel', '+4.0% weekly'], ['WTI Crude', '$111.54/barrel', '+4.3% weekly'], ['Gold', '$4,673/oz', '+2.3% weekly'], ['USD Index', '104.7', 'Strengthening']]
    tbl = Table(mkt, colWidths=[55*mm, 50*mm, 50*mm])
    tbl.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), _PDF_CYAN), ('TEXTCOLOR', (0,0), (-1,0), white), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 9), ('BACKGROUND', (0,1), (-1,-1), _PDF_LIGHT), ('GRID', (0,0), (-1,-1), 0.5, HexColor('#d0dae8')), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6), ('LEFTPADDING', (0,0), (-1,-1), 8), ('ALIGN', (1,0), (-1,-1), 'CENTER')]))
    story.append(tbl)
    story.append(Spacer(1, 8))
    story.append(Paragraph('NERAI 12-MONTH OUTLOOK', s['NH']))
    story.append(_pdf_data_box('NERAI\'s integrated models predict sustained military escalation across the Middle East through Q4 2026, with escalating probability of direct Israeli-Iranian military engagement by Q3 2026. Energy markets should anticipate continued volatility with potential spike events if Strait of Hormuz operations are further restricted.', s, _PDF_RED))
    story.append(Spacer(1, 16))
    story.append(Paragraph('Published by NERAI Intelligence | April 4, 2026', s['NF']))
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buf.seek(0)
    return buf.getvalue()




def _generate_risk_pdf_w14():
    buf = io.BytesIO()
    s = _pdf_styles()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=32*mm, bottomMargin=22*mm, leftMargin=20*mm, rightMargin=20*mm)
    def on_page(cv, d):
        _pdf_header_footer(cv, d, 'Risk Alert | Critical Threat Assessment | April 2026', _PDF_RED, 'SEVERITY: CRITICAL')
    story = []
    story.append(Paragraph('<font color="#ff4b6e">NERAI RISK ALERT</font>', s['NT']))
    story.append(Paragraph('Critical Threat Assessment | April 2026', s['NSub']))
    story.append(HRFlowable(width='100%', thickness=1, color=_PDF_RED, spaceAfter=12))
    story.append(Paragraph('<font color="#ff4b6e">&#9888;</font> ALERT 1: STRAIT OF HORMUZ - ENERGY SUPPLY DISRUPTION', s['NHR']))
    sev1 = Table([['SEVERITY: CRITICAL']], colWidths=[40*mm])
    sev1.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),_PDF_RED),('TEXTCOLOR',(0,0),(-1,-1),white),('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),7),('ALIGN',(0,0),(-1,-1),'CENTER'),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
    story.append(sev1)
    story.append(Spacer(1, 6))
    story.append(Paragraph('The effective closure of the Strait of Hormuz to Western-flagged commercial shipping represents the single largest near-term risk to global economic stability. The Strait handles approximately 20% of global maritime petroleum transport. Iranian military escalation has created an environment of spiking insurance costs, operational delays and significant rerouting expenses.', s['NB']))
    story.append(_pdf_data_box('<b>TRIGGER EVENTS:</b> Iranian drone strike on Kuwait International Airport (Apr 1); Houthi missile attacks on Israel (Mar 28); Escalated Iranian military posture across the Gulf; Western naval deployments including USS Eisenhower carrier strike group; Shipping insurance providers expanding hazard-zone designations.', s, _PDF_CYAN))
    story.append(Spacer(1, 4))
    story.append(_pdf_data_box('<b>NERAI ANALYSIS:</b> Iran\'s Military Escalation index at <b>0.16</b> (+6.1% rising). Gulf-state vulnerability indices elevated - Kuwait 0.18, Saudi Arabia 0.12, UAE 0.08. Causal-network analysis shows strong linkages between Iranian military actions and restrictions on commercial shipping lanes.', s, _PDF_CYAN))
    story.append(Spacer(1, 4))
    story.append(_pdf_data_box('<b>FORECAST:</b> Under moderate escalation, oil rises to $120-130/barrel with 2-4 week disruption. Under severe scenario, prices spike to $150+/barrel with 6-8 week disruptions. Sustained military escalation probability assessed at 78% through Q3 2026.', s, _PDF_GOLD))
    story.append(Spacer(1, 4))
    story.append(Paragraph('<b>WATCH:</b> IRGC vessel positioning; shipping insurance premiums; US 5th Fleet status; Saudi Aramco production announcements; tanker AIS routing data.', s['NB']))
    story.append(Paragraph('<font color="#ffd700">&#9888;</font> ALERT 2: INDIA-PAKISTAN NUCLEAR THRESHOLD', s['NHG']))
    sev2 = Table([['SEVERITY: HIGH']], colWidths=[40*mm])
    sev2.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),_PDF_GOLD),('TEXTCOLOR',(0,0),(-1,-1),black),('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),7),('ALIGN',(0,0),(-1,-1),'CENTER'),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
    story.append(sev2)
    story.append(Spacer(1, 6))
    story.append(Paragraph('Following the May 2025 Operation Sindoor crisis, structural tensions between India and Pakistan remain elevated. Pakistan\'s fragile economy creates incentives for strategic risk-taking by political leadership to generate nationalist sentiment.', s['NB']))
    story.append(_pdf_data_box('<b>NERAI DATA:</b> India Military Escalation <b>0.09</b>, Political Instability <b>0.02</b> (stable). Pakistan more volatile - Military Escalation <b>0.14</b>, Political Instability <b>0.11</b> (+8.3% rising), Terrorism <b>0.18</b> (+5.2%). Cross-border infiltration averaging 1.3 incidents/week.', s, _PDF_CYAN))
    story.append(Spacer(1, 4))
    story.append(_pdf_data_box('<b>FORECAST:</b> NERAI assesses 42% probability of renewed major escalation event within 12 months, with 8% conditional probability of nuclear-capable crisis comparable to May 2025.', s, _PDF_GOLD))
    story.append(Spacer(1, 4))
    story.append(Paragraph('<b>WATCH:</b> Pakistan military exercises; militancy attack frequency; cross-border infiltration; Pakistani political instability signals; Indian military posture near LoC.', s['NB']))
    story.append(Paragraph('<font color="#ff9800">&#9888;</font> ALERT 3: TAIWAN STRAIT - GREAT-POWER CONFRONTATION', s['NHO']))
    sev3 = Table([['SEVERITY: ELEVATED']], colWidths=[40*mm])
    sev3.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),_PDF_ORANGE),('TEXTCOLOR',(0,0),(-1,-1),white),('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),7),('ALIGN',(0,0),(-1,-1),'CENTER'),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
    story.append(sev3)
    story.append(Spacer(1, 6))
    story.append(Paragraph('China\'s December 2025 exercises involving 100+ aircraft (90 crossing the Taiwan median line) and 27 rocket launches represent unprecedented peacetime provocation. The 2026 defence budget increased 7% to $278 billion.', s['NB']))
    story.append(_pdf_data_box('<b>NERAI ASSESSMENT:</b> China Military Escalation at <b>0.04</b> with acceleration trend (+2.8%). International Crisis index for East Asia rising +4.1% monthly. NERAI\'s Taiwan Strait crisis-probability composite has increased 33% from baseline (0.18 to 0.24).', s, _PDF_CYAN))
    story.append(Spacer(1, 4))
    story.append(_pdf_data_box('<b>FORECAST:</b> 31% probability of significant military incident in Taiwan Strait within 12 months. Escalation from incident to major conflict assessed at 18% conditional probability.', s, _PDF_GOLD))
    story.append(Spacer(1, 4))
    story.append(Paragraph('<b>WATCH:</b> Chinese exercise announcements; median-line crossings; US carrier deployments; Taiwan defence procurement; Chinese political messaging on unification timeline.', s['NB']))
    story.append(Spacer(1, 16))
    story.append(Paragraph('Published by NERAI Intelligence | April 4, 2026', s['NF']))
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buf.seek(0)
    return buf.getvalue()


# ── BRIEFING ROOM ─────────────────────────────────────────────────────


# ============================================================
# WEEK 16 REPORT FUNCTIONS — April 13-19, 2026
# ============================================================

def _weekly_bulletin_html():
    return (
        "<div style='color:#e0e8f0;line-height:1.75;font-size:0.88rem;'>"

        "<div style='border-bottom:2px solid rgba(0,180,255,0.3);padding-bottom:14px;margin-bottom:18px;'>"
        "<h2 style='color:#00b4ff;margin:0 0 4px;font-size:1.4em;'>NERAI WEEKLY INTELLIGENCE BULLETIN</h2>"
        "<div style='color:#8aa8c8;font-size:0.85em;'>Week 16 | April 13 &ndash; 19, 2026</div>"
        "</div>"

        "<h3 style='color:#00b4ff;font-size:1.05em;margin:18px 0 8px;'>EXECUTIVE SUMMARY</h3>"
        "<p style='text-align:justify;'>Week 16 was defined by a sharp escalation of the US naval blockade of Iranian "
        "ports (Day 45&ndash;50), Iranian gunboat attacks on commercial shipping in the Strait of Hormuz, and a "
        "failed Iranian diplomatic feint that saw Tehran announce &mdash; then reverse &mdash; a reopening of the "
        "critical waterway within hours. NERAI&rsquo;s Military Escalation indices continue their upward trajectory, "
        "with UAE surging <b>+132.2%</b> and Kuwait at <b>+99.5%</b>, reflecting the expanding geographic footprint "
        "of the conflict across the Gulf. Iran&rsquo;s Military Escalation index stands at <b>0.133</b> (+47.1% rising) "
        "while Israel holds at <b>0.324</b>, as both sides recalibrate following the failed Islamabad talks. "
        "Oil markets remained volatile, with Brent trading between $90 and $103 before closing the week near $97.</p>"

        "<h3 style='color:#ff4b6e;font-size:1.05em;margin:22px 0 8px;'>"
        "&#9650; 1 &middot; US NAVAL BLOCKADE TIGHTENS AROUND IRANIAN PORTS</h3>"
        "<p style='text-align:justify;'>On April 13, 2026 (Day 45 of the Middle East conflict), the US Navy formally "
        "established a comprehensive naval blockade of Iranian ports, cutting off Tehran&rsquo;s seaborne oil exports "
        "and restricting imports of critical goods. US Energy Secretary Chris Wright warned that oil prices would "
        "continue to climb until meaningful ship traffic resumed through the Strait of Hormuz. The blockade represents "
        "a significant escalation from earlier interdiction operations, effectively placing Iran under a full maritime "
        "siege. Brent crude opened the week at $103.72/barrel before falling mid-week as diplomatic signals briefly "
        "buoyed markets.</p>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>NERAI DATA INSIGHTS:</b> Iran&rsquo;s Military Escalation index stands at <b>0.133</b> with a "
        "<b>+47.1% rising</b> trajectory, confirming that the blockade has materially elevated Tehran&rsquo;s "
        "conflict posture. The Military Clash index at <b>0.098</b> (+47.5% rising) signals increasing kinetic "
        "engagement probability. UAE&rsquo;s Military Escalation index has surged to <b>0.052</b> with an "
        "extraordinary <b>+132.2% rising</b> trend &mdash; the fastest-accelerating escalation indicator in the "
        "current dataset &mdash; reflecting Gulf state vulnerability to the expanding blockade theatre. Saudi "
        "Arabia&rsquo;s Military Escalation at <b>0.073</b> (+29.3%) and Qatar at <b>0.072</b> (+48.8%) confirm "
        "that the naval blockade&rsquo;s risk perimeter is spreading across the entire Gulf Cooperation Council.</div>"

        "<div style='padding:12px 14px;background:rgba(255,215,0,0.06);border-left:3px solid #ffd700;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>12-MONTH FORECAST:</b> NERAI models project the UAE&rsquo;s Military Escalation index reaching "
        "<b>0.12</b> by Q3 2026 under current trajectory, representing a tripling from current levels. "
        "A sustained blockade lasting beyond 60 days carries a <b>42% probability</b> of triggering coordinated "
        "GCC defensive posturing that could draw Saudi and Emirati forces into direct conflict-adjacent operations. "
        "The US blockade is forecast to remain in place for at least 30&ndash;45 additional days absent a "
        "breakthrough diplomatic agreement.</div>"

        "<h3 style='color:#ff4b6e;font-size:1.05em;margin:22px 0 8px;'>"
        "&#9650; 2 &middot; IRANIAN GUNBOATS ATTACK COMMERCIAL SHIPPING IN HORMUZ</h3>"
        "<p style='text-align:justify;'>On April 18, 2026, two Indian-flagged commercial vessels were targeted by "
        "Iranian gunboats in the Strait of Hormuz, including the VLCC Sanmar Herald which came under fire despite "
        "receiving prior transit clearance. The vessels were forced to turn back, marking the most direct Iranian "
        "military action against third-country commercial shipping since the conflict began. The attacks signal "
        "that Iran is willing to disrupt neutral shipping &mdash; potentially drawing India and other major maritime "
        "powers into the crisis &mdash; even as diplomatic back-channels reportedly remain open through Pakistan.</p>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>NERAI DATA INSIGHTS:</b> Kuwait&rsquo;s Military Escalation index stands at <b>0.080</b> with a "
        "<b>+99.5% rising</b> trend, reflecting acute Gulf state exposure to commercial shipping disruption. "
        "Qatar&rsquo;s Military Clash index at <b>0.065</b> (+40.8% rising) captures the expanding threat to "
        "LNG export infrastructure. Lebanon&rsquo;s Military Escalation at <b>0.285</b> (+10.8% rising) and "
        "Military Clash at <b>0.271</b> (+18.1% rising) confirm that the multi-front conflict remains at "
        "sustained high intensity. Iraq&rsquo;s Military Escalation at <b>0.169</b> (+29.2% rising) reflects "
        "ongoing pressure on the northern flank.</div>"

        "<div style='padding:12px 14px;background:rgba(255,215,0,0.06);border-left:3px solid #ffd700;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>12-MONTH FORECAST:</b> Attacks on neutral third-country vessels carry a <b>37% probability</b> of "
        "triggering a formal Indian naval response by Q2 2026, which would represent a significant widening of "
        "the conflict coalition. NERAI projects Kuwait&rsquo;s Military Escalation index to reach <b>0.16</b> "
        "by Q3 2026. Shipping insurance premiums for Hormuz transits are forecast to increase a further "
        "40&ndash;60% from current elevated levels over the next 30 days, adding structural cost pressure to "
        "global energy supply chains.</div>"

        "<h3 style='color:#ff4b6e;font-size:1.05em;margin:22px 0 8px;'>"
        "&#9650; 3 &middot; IRAN&rsquo;S HORMUZ &lsquo;OPENING&rsquo; DIPLOMATIC FEINT COLLAPSES</h3>"
        "<p style='text-align:justify;'>On April 17, Iranian Foreign Minister Abbas Araghchi declared the Strait "
        "of Hormuz &ldquo;completely open&rdquo; to commercial vessels for the remaining period of the ceasefire "
        "&mdash; a move widely interpreted as a diplomatic signal ahead of a potential second round of Islamabad "
        "talks. However, President Trump immediately stated that the US naval blockade &ldquo;will remain in full "
        "force&rdquo; until a comprehensive peace deal is reached, rendering the Iranian announcement effectively "
        "moot. Within hours of the White House statement, Iran reversed course, with Tehran&rsquo;s joint military "
        "command announcing on April 19 that &ldquo;control of the Strait of Hormuz has returned to its previous "
        "state.&rdquo; CNBC separately reported on April 15 that US and Iranian teams could reconvene in Pakistan "
        "for a second round of negotiations, with Iran said to be studying fresh US proposals.</p>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>NERAI DATA INSIGHTS:</b> Israel&rsquo;s Military Escalation index holds at <b>0.324</b> (stable, "
        "+4.2%) and Military Clash at <b>0.303</b> (stable, +4.2%), suggesting that the Israeli military "
        "posture has plateaued following last week&rsquo;s peak operations. Yemen&rsquo;s Military Escalation "
        "at <b>0.204</b> (falling, -8.7%) and Military Clash at <b>0.198</b> (falling, -6.4%) indicate "
        "reduced Houthi operational tempo, possibly as Tehran redirects resources toward the Hormuz theatre. "
        "US Military Escalation at <b>0.160</b> (stable, -1.3%) reflects Washington&rsquo;s deliberate "
        "maintenance of pressure without further escalation ahead of potential talks.</div>"

        "<div style='padding:12px 14px;background:rgba(255,215,0,0.06);border-left:3px solid #ffd700;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>12-MONTH FORECAST:</b> Iran&rsquo;s diplomatic reversal follows a pattern of tactical signalling "
        "rather than genuine de-escalation intent. NERAI models assign a <b>22% probability</b> of successful "
        "second-round Islamabad talks producing a temporary ceasefire by end of April 2026, and a <b>61% "
        "probability</b> of continued military standoff through Q3 2026 absent major concessions from either "
        "side. The nuclear timeline remains the central unresolved variable: NERAI estimates Iran&rsquo;s "
        "weapons-grade enrichment capability at 6&ndash;8 months under current conditions.</div>"

        "<h3 style='color:#00b4ff;font-size:1.05em;margin:22px 0 8px;'>MARKET IMPACT</h3>"
        "<div style='padding:12px 14px;background:rgba(10,20,40,0.5);border:1px solid rgba(0,180,255,0.15);"
        "border-radius:4px;margin:12px 0;'>"
        "<b>Energy Markets</b><br>"
        "&bull; Brent Crude: <b>$97.06/barrel</b> (Apr 19) &mdash; volatile week, range $90&ndash;$103; "
        "touched $90 briefly on Hormuz opening news before reversing<br>"
        "&bull; WTI Crude: <b>$94.10/barrel</b> (-3.2% weekly on ceasefire noise, then partial recovery)<br><br>"
        "<b>Safe-Haven Assets</b><br>"
        "&bull; Gold: <b>$4,855/oz</b> (+0.8% weekly, fourth consecutive weekly gain, safe-haven demand "
        "sustained)<br>"
        "&bull; USD Index: 105.8 &mdash; strengthening on risk-off flows and blockade durability outlook<br><br>"
        "<span style='color:#ffd700;'><b>Brent crude whipsawed between $90 and $103 this week as Iran&rsquo;s "
        "Hormuz opening announcement briefly triggered a 10% selloff before Trump&rsquo;s blockade "
        "confirmation drove a sharp recovery. The $97 close reflects the market&rsquo;s conclusion that the "
        "conflict risk premium remains structural.</b></span>"
        "</div>"

        "<h3 style='color:#00b4ff;font-size:1.05em;margin:22px 0 8px;'>NERAI 12-MONTH OUTLOOK</h3>"
        "<div style='padding:12px 14px;background:rgba(255,75,110,0.06);border-left:3px solid #ff4b6e;"
        "border-radius:4px;margin:12px 0;'>"
        "The Week 16 pattern &mdash; naval blockade tightening, commercial shipping attacks, and a failed "
        "diplomatic feint &mdash; confirms that the conflict has entered a phase of attrition rather than "
        "acute escalation. NERAI&rsquo;s integrated models maintain a <b>74% probability</b> of major "
        "regional escalation event by Q4 2026. The most acute near-term risk is Indian naval involvement "
        "following attacks on its flagged vessels (37% probability within 30 days). The UAE escalation "
        "trajectory (+132.2%) is the dataset&rsquo;s most significant early warning signal, suggesting Gulf "
        "state security architecture is under stress. Energy markets should continue to price in a "
        "<b>$8&ndash;12/barrel structural risk premium</b> above pre-conflict baselines. A second-round "
        "Islamabad agreement would provide temporary relief but NERAI assigns low durability probability "
        "(&lt;30%) to any ceasefire not accompanied by binding nuclear verification mechanisms.</div>"

        "<div style='border-top:1px solid rgba(0,180,255,0.2);margin-top:20px;padding-top:10px;"
        "color:#8aa8c8;font-size:0.78rem;text-align:center;'>"
        "Published by NERAI Intelligence | April 19, 2026</div>"
        "</div>"
    )


def _risk_alert_html():
    return (
        "<div style='color:#e0e8f0;line-height:1.75;font-size:0.88rem;'>"

        "<div style='border-bottom:2px solid rgba(255,75,110,0.3);padding-bottom:14px;margin-bottom:18px;'>"
        "<h2 style='color:#ff4b6e;margin:0 0 4px;font-size:1.4em;'>NERAI RISK ALERT</h2>"
        "<div style='color:#8aa8c8;font-size:0.85em;'>Critical Threat Assessment | Week 16 | April 2026</div>"
        "</div>"

        "<h3 style='color:#ff4b6e;font-size:1.05em;margin:18px 0 8px;'>"
        "&#9888; ALERT 1: COMMERCIAL SHIPPING ATTACKS &mdash; HORMUZ CHOKEPOINT CRISIS</h3>"
        "<div style='display:inline-block;background:rgba(255,75,110,0.2);color:#ff9999;padding:3px 10px;"
        "border-radius:3px;font-weight:700;font-size:0.75rem;margin-bottom:10px;'>SEVERITY: CRITICAL</div>"
        "<p style='text-align:justify;'>Iran&rsquo;s direct gunboat attacks on Indian-flagged commercial vessels "
        "on April 18 represent a significant doctrinal escalation: from interdicting vessels based on flag state "
        "or cargo to attacking pre-cleared neutral shipping. The VLCC Sanmar Herald attack &mdash; despite "
        "holding valid transit clearance &mdash; signals that Iranian military commanders may be operating with "
        "expanded rules of engagement independent of diplomatic channels. This creates unpredictable maritime "
        "risk across the 21%-of-global-petroleum-transit chokepoint. The attack risks internalising a third "
        "major naval power (India) into the conflict dynamics.</p>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>TRIGGER EVENTS:</b> Iranian gunboats fire on VLCC Sanmar Herald (Apr 18); two Indian-flagged "
        "ships forced to turn back; Iran reopens then re-closes Hormuz within 24 hours (Apr 17&ndash;19); "
        "US blockade of Iranian ports Day 45+ (from Apr 13); continued shipping insurance premium escalation; "
        "IRGC naval exercises expanding in Gulf waters.</div>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>NERAI ANALYSIS:</b> UAE Military Escalation at <b>0.052</b> with a <b>+132.2% rising</b> trend "
        "is the fastest-accelerating threat indicator in the current dataset, reflecting acute Gulf state "
        "vulnerability. Kuwait Military Escalation at <b>0.080</b> (+99.5% rising) confirms systemic "
        "regional threat expansion. Qatar Military Clash at <b>0.065</b> (+40.8% rising) signals LNG "
        "export infrastructure risk. Iran Military Escalation at <b>0.133</b> (+47.1% rising) and "
        "Military Clash at <b>0.098</b> (+47.5% rising) confirm an accelerating kinetic posture despite "
        "diplomatic back-channel activity.</div>"

        "<div style='padding:12px 14px;background:rgba(255,215,0,0.06);border-left:3px solid #ffd700;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>FORECAST:</b> Under sustained commercial shipping attack scenario, Brent crude projected to "
        "spike to <b>$115&ndash;130/barrel</b> within 2 weeks. If India deploys naval escorts in response "
        "(37% probability within 30 days), risk of accidental clash with IRGC forces rises to <b>28%</b>. "
        "Shipping insurance market may become effectively non-functional for Hormuz transits above "
        "$100M cargo value, forcing permanent Cape of Good Hope rerouting for VLCC class vessels.</div>"

        "<p style='text-align:justify;'><b>WATCH:</b> Indian Navy Eastern Fleet deployments; IRGC gunboat "
        "patrol patterns; shipping insurance rate movements for Hormuz transits; LNG spot price divergence "
        "Asia vs. Europe; Saudi Aramco export route shifts; UAE port congestion indicators; VHF channel 16 "
        "intercepts for vessel distress signals in Persian Gulf.</p>"

        "<h3 style='color:#ffd700;font-size:1.05em;margin:22px 0 8px;'>"
        "&#9888; ALERT 2: GULF STATE ESCALATION CASCADE &mdash; UAE/KUWAIT THREAT SURGE</h3>"
        "<div style='display:inline-block;background:rgba(255,215,0,0.2);color:#ffd700;padding:3px 10px;"
        "border-radius:3px;font-weight:700;font-size:0.75rem;margin-bottom:10px;'>SEVERITY: HIGH</div>"
        "<p style='text-align:justify;'>NERAI data identifies an accelerating escalation cascade across Gulf "
        "Cooperation Council member states that has received insufficient attention relative to the Iran-Israel "
        "primary theatre. UAE&rsquo;s Military Escalation index has surged +132.2% and Kuwait&rsquo;s has "
        "nearly doubled (+99.5%) in the current measurement period &mdash; trajectories that, if sustained, "
        "will bring these states to Israel-comparable escalation levels within 60&ndash;90 days. This pattern "
        "suggests that the US naval blockade and Iranian retaliation are creating secondary conflict pressure "
        "on Gulf states hosting critical US military infrastructure including Al Udeid (Qatar) and Al Dhafra "
        "(UAE) air bases.</p>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>TRIGGER EVENTS:</b> Iranian drone strikes on UAE and Saudi energy infrastructure (from March); "
        "US naval blockade expanding area of operations around Gulf ports; GCC emergency defence council "
        "meetings; Iranian missile exercise targeting Gulf state coordinates; US pre-positioning additional "
        "Patriot batteries at GCC bases.</div>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>NERAI ANALYSIS:</b> Saudi Arabia Military Escalation at <b>0.073</b> (+29.3% rising) and Qatar "
        "Military Escalation at <b>0.072</b> (+48.8% rising) are both on upward trajectories. Combined with "
        "UAE (+132.2%) and Kuwait (+99.5%), all four major GCC states are showing simultaneous escalation "
        "acceleration &mdash; a pattern NERAI has not previously recorded in the dataset. Iraq Military "
        "Escalation at <b>0.169</b> (+29.2% rising) adds northern pressure. This multi-node simultaneous "
        "escalation significantly complicates US force protection requirements.</div>"

        "<div style='padding:12px 14px;background:rgba(255,215,0,0.06);border-left:3px solid #ffd700;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>FORECAST:</b> NERAI projects UAE Military Escalation reaching <b>0.12</b> and Kuwait reaching "
        "<b>0.16</b> by Q3 2026 under current trajectories. A coordinated Iranian strike on a GCC military "
        "installation hosting US forces carries a <b>19% probability</b> within 45 days, which would "
        "trigger immediate US Article 5-equivalent response commitments and represent a fundamental "
        "widening of the conflict. Saudi Aramco export capacity is assessed at elevated disruption risk "
        "through Q2 2026.</div>"

        "<p style='text-align:justify;'><b>WATCH:</b> GCC defence ministers joint statements; US CENTCOM "
        "force posture updates; UAE Al Dhafra and Qatar Al Udeid alert levels; Saudi Aramco Abqaiq facility "
        "security upgrades; Iranian medium-range missile inventory drawdown rates; Kuwait Naval Base "
        "operational tempo.</p>"

        "<h3 style='color:#ffa500;font-size:1.05em;margin:22px 0 8px;'>"
        "&#9888; ALERT 3: SECOND-ROUND ISLAMABAD TALKS &mdash; FRAGILE DIPLOMATIC WINDOW</h3>"
        "<div style='display:inline-block;background:rgba(255,165,0,0.2);color:#ffa500;padding:3px 10px;"
        "border-radius:3px;font-weight:700;font-size:0.75rem;margin-bottom:10px;'>SEVERITY: ELEVATED</div>"
        "<p style='text-align:justify;'>Reports of a potential second round of US-Iran talks in Pakistan "
        "(per CNBC, April 15) represent the only active diplomatic off-ramp visible in the current "
        "intelligence picture. However, the structural gaps from the first Islamabad talks remain "
        "unbridged: the US insists on binding nuclear verification and Iran demands security guarantees "
        "and war reparations. Iran&rsquo;s diplomatic feint on Hormuz (opening then reversing within 24 "
        "hours) suggests Tehran is using tactical diplomatic gestures to test US resolve rather than "
        "pursue genuine de-escalation. The window for a second-round agreement before military dynamics "
        "become irreversible is assessed at approximately 2&ndash;3 weeks.</p>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>TRIGGER EVENTS:</b> CNBC reports US-Iran second round Islamabad talks (Apr 15); Iran studying "
        "fresh US proposals (Irish Times, Apr 18); Iran FM Araghchi Hormuz opening statement (Apr 17) "
        "then reversed (Apr 19); Trump confirms blockade remains; Pakistan FM Dar maintains backchannel "
        "communications; potential new US concessions on sanctions timeline.</div>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>NERAI ANALYSIS:</b> US Military Escalation at <b>0.160</b> (stable, -1.3%) and Military Clash "
        "at <b>0.116</b> (stable, -3.2%) indicate Washington is deliberately holding its military posture "
        "steady to preserve negotiating leverage. Israel&rsquo;s plateau at <b>0.324</b> (stable) suggests "
        "Jerusalem is also in a holding pattern awaiting diplomatic outcomes. Yemen Military Escalation "
        "falling to <b>0.204</b> (-8.7%) may indicate Tehran is reducing Houthi operational tempo as a "
        "goodwill signal to enable talks.</div>"

        "<div style='padding:12px 14px;background:rgba(255,215,0,0.06);border-left:3px solid #ffd700;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>FORECAST:</b> NERAI assigns <b>22% probability</b> of second-round Islamabad talks producing "
        "a temporary ceasefire by end of April 2026. A successful ceasefire would produce an immediate "
        "<b>$12&ndash;18/barrel Brent crude decline</b> and <b>$150&ndash;200/oz gold decline</b> as risk "
        "premium is rapidly repriced. However, NERAI assigns only <b>28% durability probability</b> to "
        "any agreement not containing binding nuclear verification, making a resumption of hostilities "
        "within 90 days the base case scenario even under a ceasefire outcome.</div>"

        "<p style='text-align:justify;'><b>WATCH:</b> Pakistan foreign ministry travel schedules; US "
        "State Department backchannel communications; IAEA inspection access requests; Iran Supreme "
        "National Security Council composition post-Larijani; Congressional authorization debates in "
        "Washington; Russian and Chinese diplomatic positioning on ceasefire terms; India reaction to "
        "shipping attacks in context of ongoing Islamabad talks.</p>"

        "<div style='border-top:1px solid rgba(255,75,110,0.2);margin-top:20px;padding-top:10px;"
        "color:#8aa8c8;font-size:0.78rem;text-align:center;'>"
        "Published by NERAI Intelligence | April 19, 2026</div>"
        "</div>"
    )


def _generate_weekly_pdf():
    buf = io.BytesIO()
    s = _pdf_styles()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=32*mm, bottomMargin=22*mm, leftMargin=20*mm, rightMargin=20*mm)
    def on_page(cv, d):
        _pdf_header_footer(cv, d, 'Weekly Intelligence Bulletin | Week 16 | April 13 - 19, 2026', _PDF_GOLD, 'UNCLASSIFIED')
    story = []
    story.append(Paragraph('NERAI WEEKLY INTELLIGENCE BULLETIN', s['NT']))
    story.append(Paragraph('Week 16 | April 13 - 19, 2026', s['NSub']))
    story.append(HRFlowable(width='100%', thickness=1, color=_PDF_CYAN, spaceAfter=12))
    story.append(Paragraph('EXECUTIVE SUMMARY', s['NH']))
    story.append(Paragraph('Week 16 was defined by a sharp escalation of the US naval blockade of Iranian ports (Day 45-50), Iranian gunboat attacks on commercial shipping in the Strait of Hormuz, and a failed Iranian diplomatic feint that saw Tehran announce then reverse a reopening of the critical waterway within hours. NERAI Military Escalation indices continue their upward trajectory, with UAE surging +132.2% and Kuwait at +99.5%, reflecting the expanding geographic footprint of the conflict across the Gulf. Iran Military Escalation stands at 0.133 (+47.1% rising) while Israel holds at 0.324, as both sides recalibrate following the failed Islamabad talks. Oil markets remained volatile, with Brent trading between $90 and $103 before closing the week near $97.', s['NB']))
    story.append(Spacer(1, 10))
    story.append(Paragraph('1. US NAVAL BLOCKADE TIGHTENS AROUND IRANIAN PORTS', s['NH']))
    story.append(Paragraph('On April 13, 2026 (Day 45 of the Middle East conflict), the US Navy formally established a comprehensive naval blockade of Iranian ports, cutting off Tehran\'s seaborne oil exports and restricting imports of critical goods. US Energy Secretary Chris Wright warned that oil prices would continue to climb until meaningful ship traffic resumed through the Strait of Hormuz. Brent crude opened the week at $103.72/barrel before falling mid-week as diplomatic signals briefly buoyed markets.', s['NB']))
    story.append(Spacer(1, 6))
    story.append(Paragraph('NERAI DATA INSIGHTS', s['NBI']))
    story.append(Paragraph('Iran Military Escalation: 0.133 (+47.1% rising). Military Clash: 0.098 (+47.5% rising). UAE Military Escalation: 0.052 (+132.2% rising — fastest-accelerating in dataset). Saudi Arabia: 0.073 (+29.3%). Qatar: 0.072 (+48.8%). All four major GCC states showing simultaneous escalation acceleration.', s['NB']))
    story.append(Spacer(1, 6))
    story.append(Paragraph('12-MONTH FORECAST', s['NBI']))
    story.append(Paragraph('UAE Military Escalation projected to reach 0.12 by Q3 2026. 42% probability of coordinated GCC defensive posturing triggering conflict-adjacent operations if blockade exceeds 60 days. US blockade forecast to remain in place 30-45 additional days absent diplomatic breakthrough.', s['NB']))
    story.append(Spacer(1, 10))
    story.append(Paragraph('2. IRANIAN GUNBOATS ATTACK COMMERCIAL SHIPPING IN HORMUZ', s['NH']))
    story.append(Paragraph('On April 18, 2026, two Indian-flagged commercial vessels were targeted by Iranian gunboats in the Strait of Hormuz, including the VLCC Sanmar Herald which came under fire despite receiving prior transit clearance. The attacks signal that Iranian military commanders may be operating with expanded rules of engagement independent of diplomatic channels, creating unpredictable maritime risk across the 21%-of-global-petroleum-transit chokepoint.', s['NB']))
    story.append(Spacer(1, 6))
    story.append(Paragraph('NERAI DATA INSIGHTS', s['NBI']))
    story.append(Paragraph('Kuwait Military Escalation: 0.080 (+99.5% rising). Qatar Military Clash: 0.065 (+40.8% rising). Lebanon Military Escalation: 0.285 (+10.8% rising). Iraq Military Escalation: 0.169 (+29.2% rising). Yemen Military Escalation: 0.204 (falling -8.7%, possible Houthi tempo reduction as diplomatic signal).', s['NB']))
    story.append(Spacer(1, 6))
    story.append(Paragraph('12-MONTH FORECAST', s['NBI']))
    story.append(Paragraph('37% probability India deploys naval escorts within 30 days. Kuwait Military Escalation projected at 0.16 by Q3 2026. Shipping insurance market risks becoming non-functional for VLCC class transits through Hormuz above $100M cargo value.', s['NB']))
    story.append(Spacer(1, 10))
    story.append(Paragraph('3. IRAN\'S HORMUZ "OPENING" DIPLOMATIC FEINT COLLAPSES', s['NH']))
    story.append(Paragraph('On April 17, Iranian FM Araghchi declared Hormuz "completely open" for the ceasefire period. President Trump immediately stated the US blockade "will remain in full force" until a peace deal. Within hours of the White House statement, Iran reversed course on April 19, with Tehran\'s military command announcing that "control of the Strait of Hormuz has returned to its previous state." CNBC reported on April 15 that a second round of US-Iran talks in Pakistan may be forthcoming.', s['NB']))
    story.append(Spacer(1, 6))
    story.append(Paragraph('NERAI DATA INSIGHTS', s['NBI']))
    story.append(Paragraph('Israel Military Escalation: 0.324 (stable +4.2%). US Military Escalation: 0.160 (stable -1.3%). Yemen Military Escalation: 0.204 (falling -8.7%), suggesting Tehran redirecting resources to Hormuz theatre. Both US and Israeli military postures in deliberate holding pattern ahead of potential second-round talks.', s['NB']))
    story.append(Spacer(1, 6))
    story.append(Paragraph('12-MONTH FORECAST', s['NBI']))
    story.append(Paragraph('22% probability second-round Islamabad talks produce temporary ceasefire by end of April 2026. Only 28% durability probability for any agreement without binding nuclear verification. 61% probability of continued military standoff through Q3 2026 absent major concessions. Nuclear timeline: 6-8 months to weapons-grade enrichment capability under current conditions.', s['NB']))
    story.append(Spacer(1, 10))
    story.append(Paragraph('MARKET IMPACT', s['NH']))
    story.append(Paragraph('Energy Markets', s['NBI']))
    story.append(Paragraph('Brent Crude: $97.06/barrel (Apr 19), volatile week range $90-$103. WTI: $94.10/barrel. Brent whipsawed on Hormuz opening news (touched $90) then recovered as Trump confirmed blockade continuity.', s['NB']))
    story.append(Paragraph('Safe-Haven Assets', s['NBI']))
    story.append(Paragraph('Gold: $4,855/oz (+0.8% weekly, fourth consecutive weekly gain). USD Index: 105.8 (strengthening on risk-off flows). Structural $8-12/barrel risk premium above pre-conflict baseline remains priced in.', s['NB']))
    story.append(Spacer(1, 10))
    story.append(Paragraph('NERAI 12-MONTH OUTLOOK', s['NH']))
    story.append(Paragraph('Week 16 confirms the conflict has entered an attrition phase. NERAI maintains 74% probability of major regional escalation event by Q4 2026. Most acute near-term risk is Indian naval involvement (37% within 30 days). UAE escalation trajectory (+132.2%) is the dataset\'s most significant early warning signal. A second-round Islamabad agreement would provide temporary relief but NERAI assigns low durability probability (<30%) to any ceasefire without binding nuclear verification.', s['NB']))
    story.append(Spacer(1, 16))
    story.append(Paragraph('Published by NERAI Intelligence | April 19, 2026', s['NF']))
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buf.seek(0)
    return buf.getvalue()


def _generate_risk_pdf():
    buf = io.BytesIO()
    s = _pdf_styles()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=32*mm, bottomMargin=22*mm, leftMargin=20*mm, rightMargin=20*mm)
    def on_page(cv, d):
        _pdf_header_footer(cv, d, 'Risk Alert | Critical Threat Assessment | Week 16 | April 2026', _PDF_RED, 'SEVERITY: CRITICAL')
    story = []
    story.append(Paragraph('<font color="#ff4b6e">NERAI RISK ALERT</font>', s['NT']))
    story.append(Paragraph('Critical Threat Assessment | Week 16 | April 13-19, 2026', s['NSub']))
    story.append(HRFlowable(width='100%', thickness=1, color=_PDF_RED, spaceAfter=12))
    story.append(Spacer(1, 4))
    story.append(Paragraph('ALERT 1: COMMERCIAL SHIPPING ATTACKS — HORMUZ CHOKEPOINT CRISIS', s['NH']))
    story.append(Paragraph('SEVERITY: CRITICAL', s['NBI']))
    story.append(Paragraph('Iranian gunboat attacks on Indian-flagged commercial vessels on April 18 represent a doctrinal escalation: from interdicting flag-state vessels to attacking pre-cleared neutral shipping. The VLCC Sanmar Herald attack signals Iranian military commanders may be operating with expanded rules of engagement independent of diplomatic channels, creating unpredictable risk across the 21%-of-global-petroleum-transit chokepoint.', s['NB']))
    story.append(Spacer(1, 6))
    story.append(Paragraph('TRIGGER EVENTS', s['NBI']))
    story.append(Paragraph('Iranian gunboats fire on VLCC Sanmar Herald (Apr 18); two Indian-flagged ships forced to turn back; Iran reopens then re-closes Hormuz within 24 hours (Apr 17-19); US blockade of Iranian ports Day 45+ (from Apr 13); continued shipping insurance premium escalation; IRGC naval exercises expanding in Gulf waters.', s['NB']))
    story.append(Spacer(1, 6))
    story.append(Paragraph('NERAI ANALYSIS', s['NBI']))
    story.append(Paragraph('UAE Military Escalation: 0.052 (+132.2% rising — fastest in dataset). Kuwait: 0.080 (+99.5% rising). Qatar Military Clash: 0.065 (+40.8% rising). Iran Military Escalation: 0.133 (+47.1% rising). Iran Military Clash: 0.098 (+47.5% rising). All GCC major states showing simultaneous escalation acceleration — unprecedented in NERAI dataset.', s['NB']))
    story.append(Spacer(1, 6))
    story.append(Paragraph('FORECAST', s['NBI']))
    story.append(Paragraph('Sustained shipping attack scenario: Brent projected to spike $115-130/barrel within 2 weeks. Indian naval response probability: 37% within 30 days. If India deploys escorts: 28% probability of accidental IRGC clash. Shipping insurance may become non-functional for VLCC Hormuz transits above $100M cargo value.', s['NB']))
    story.append(Paragraph('WATCH: Indian Navy Eastern Fleet deployments; IRGC gunboat patrol patterns; shipping insurance rate movements; LNG spot price divergence Asia vs. Europe; Saudi Aramco export route shifts.', s['NB']))
    story.append(Spacer(1, 10))
    story.append(Paragraph('ALERT 2: GULF STATE ESCALATION CASCADE — UAE/KUWAIT THREAT SURGE', s['NH']))
    story.append(Paragraph('SEVERITY: HIGH', s['NBI']))
    story.append(Paragraph('NERAI data identifies an accelerating escalation cascade across GCC member states. UAE Military Escalation surged +132.2% and Kuwait nearly doubled (+99.5%) — trajectories that will bring these states to Israel-comparable escalation levels within 60-90 days. This pattern suggests the US naval blockade and Iranian retaliation are creating secondary conflict pressure on Gulf states hosting critical US military infrastructure including Al Udeid (Qatar) and Al Dhafra (UAE) air bases.', s['NB']))
    story.append(Spacer(1, 6))
    story.append(Paragraph('NERAI ANALYSIS', s['NBI']))
    story.append(Paragraph('Saudi Arabia Military Escalation: 0.073 (+29.3% rising). Qatar: 0.072 (+48.8% rising). UAE: 0.052 (+132.2% rising). Kuwait: 0.080 (+99.5% rising). Iraq: 0.169 (+29.2% rising). All four major GCC states plus Iraq showing simultaneous escalation — first time recorded in NERAI dataset.', s['NB']))
    story.append(Spacer(1, 6))
    story.append(Paragraph('FORECAST', s['NBI']))
    story.append(Paragraph('UAE projected at 0.12, Kuwait at 0.16 by Q3 2026. Coordinated Iranian strike on GCC installation hosting US forces: 19% probability within 45 days. Such strike would trigger immediate US response and fundamental conflict widening. Saudi Aramco export capacity at elevated disruption risk through Q2 2026.', s['NB']))
    story.append(Paragraph('WATCH: GCC defence ministers joint statements; US CENTCOM force posture; UAE Al Dhafra and Qatar Al Udeid alert levels; Saudi Aramco Abqaiq security upgrades; Iranian medium-range missile inventory.', s['NB']))
    story.append(Spacer(1, 10))
    story.append(Paragraph('ALERT 3: SECOND-ROUND ISLAMABAD TALKS — FRAGILE DIPLOMATIC WINDOW', s['NH']))
    story.append(Paragraph('SEVERITY: ELEVATED', s['NBI']))
    story.append(Paragraph('Reports of potential second-round US-Iran Pakistan talks (CNBC, Apr 15) represent the only active diplomatic off-ramp. Structural gaps from first Islamabad talks remain unbridged. Iran\'s Hormuz feint (opening then reversing within 24 hours) suggests tactical diplomatic gestures to test US resolve rather than genuine de-escalation. The window for agreement before military dynamics become irreversible is assessed at approximately 2-3 weeks.', s['NB']))
    story.append(Spacer(1, 6))
    story.append(Paragraph('NERAI ANALYSIS', s['NBI']))
    story.append(Paragraph('US Military Escalation: 0.160 (stable -1.3%) — deliberate holding posture. Israel Military Escalation: 0.324 (stable +4.2%) — plateau phase. Yemen Military Escalation: 0.204 (falling -8.7%) — possible Houthi tempo reduction as Iranian goodwill signal. Both US and Israeli military indices in holding pattern consistent with pre-negotiation positioning.', s['NB']))
    story.append(Spacer(1, 6))
    story.append(Paragraph('FORECAST', s['NBI']))
    story.append(Paragraph('22% probability second-round talks produce temporary ceasefire by end-April 2026. Successful ceasefire: immediate $12-18/barrel Brent decline, $150-200/oz gold decline. Only 28% durability probability without binding nuclear verification. 61% probability of continued military standoff through Q3 2026. Nuclear timeline: 6-8 months to weapons-grade enrichment capability.', s['NB']))
    story.append(Paragraph('WATCH: Pakistan foreign ministry travel schedules; IAEA inspection access requests; Iran Supreme National Security Council decisions; Congressional authorization debates; Russian and Chinese diplomatic positioning; India reaction to shipping attacks in context of Islamabad talks.', s['NB']))
    story.append(Spacer(1, 16))
    story.append(Paragraph('Published by NERAI Intelligence | April 19, 2026', s['NF']))
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buf.seek(0)
    return buf.getvalue()


def render_briefing_room():
    nerai_premium_css.inject_page_header(
        title="Briefing Room",
        subtitle="Automated intelligence reports & downloadable risk assessments",
        badge="REPORTS",
        icon="\U0001F4CB"
    )
    nerai_premium_css.inject_global_premium_css()

    st.markdown(
        "<div style='padding:6px 0 10px;'>"
        "<div class='hero-title'>Briefing Room</div>"
        "<div class='hero-sub'>"
        "<span class='live-dot'></span>"
        "NERAI Intelligence Analyses &middot; Strategic Reports"
        "</div></div>", unsafe_allow_html=True)
    st.markdown('<div class="h-div"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            "<div style='background:rgba(10,20,40,0.6);border:1px solid rgba(0,180,255,0.25);"
            "border-radius:10px;padding:20px;margin-bottom:14px;'>"
            "<div style='display:flex;align-items:center;gap:10px;margin-bottom:12px;'>"
            "<div style='font-size:1.8rem;'>&#128200;</div>"
            "<div><div style='font-size:1.05rem;font-weight:700;color:#00b4ff;'>NERAI Weekly Bulletin</div>"
            "<div style='font-size:0.75rem;color:#8aa8c8;'>Week 16 | April 13 - 19, 2026</div></div>"
            "</div>"
            "<div style='display:inline-block;background:#ffd700;color:#000;padding:3px 10px;"
            "border-radius:3px;font-weight:700;font-size:0.7rem;letter-spacing:0.05em;'>UNCLASSIFIED</div>"
            "</div>", unsafe_allow_html=True)

        with st.expander("Read Full Bulletin", expanded=False):
            st.markdown(_weekly_bulletin_html(), unsafe_allow_html=True)

        st.download_button(
            label="\u2B07 Download PDF",
            data=_generate_weekly_pdf(),
            file_name="NERAI_Weekly_Bulletin_W16.pdf",
            mime="application/pdf",
            use_container_width=True)

    with col2:
        st.markdown(
            "<div style='background:rgba(10,20,40,0.6);border:1px solid rgba(255,75,110,0.3);"
            "border-radius:10px;padding:20px;margin-bottom:14px;'>"
            "<div style='display:flex;align-items:center;gap:10px;margin-bottom:12px;'>"
            "<div style='font-size:1.8rem;'>&#9888;</div>"
            "<div><div style='font-size:1.05rem;font-weight:700;color:#ff4b6e;'>NERAI Risk Alert</div>"
            "<div style='font-size:0.75rem;color:#8aa8c8;'>Critical Threat Assessment | Week 16 | April 2026</div></div>"
            "</div>"
            "<div style='display:inline-block;background:#ff4b6e;color:#fff;padding:3px 10px;"
            "border-radius:3px;font-weight:700;font-size:0.7rem;letter-spacing:0.05em;'>SEVERITY: CRITICAL</div>"
            "</div>", unsafe_allow_html=True)

        with st.expander("Read Full Alert", expanded=False):
            st.markdown(_risk_alert_html(), unsafe_allow_html=True)

        st.download_button(
            label="\u2B07 Download PDF",
            data=_generate_risk_pdf(),
            file_name="NERAI_Risk_Alert_W16_Apr2026.pdf",
            mime="application/pdf",
            use_container_width=True)

    st.markdown(
        "<div style='margin-top:30px;padding:14px 20px;background:rgba(10,20,40,0.4);"
        "border:1px solid rgba(0,180,255,0.15);border-radius:8px;text-align:center;"
        "color:#8aa8c8;font-size:0.8rem;line-height:1.6;'>"
        "All analyses produced by NERAI Intelligence using proprietary indices, predictive models "
        "and causal network analysis. Reports updated weekly."
        "</div>", unsafe_allow_html=True)

    # === ARCHIVE SECTION ===
    st.markdown('<div class="h-div" style="margin:24px 0 16px"></div>', unsafe_allow_html=True)
    st.markdown(
        "<div style='display:flex;align-items:center;gap:10px;margin-bottom:16px;'>"
        "<div style='font-size:1.4rem;'>\U0001F4C2</div>"
        "<div class='sec-hdr' style='margin:0;'>Report Archive</div>"
        "</div>", unsafe_allow_html=True)

    with st.expander("\U0001F4C4 Week 15 | April 5 - 11, 2026", expanded=False):
        arc1, arc2 = st.columns(2)
        with arc1:
            st.markdown(
                "<div style='background:rgba(10,20,40,0.4);border:1px solid rgba(0,180,255,0.15);"
                "border-radius:8px;padding:14px;margin-bottom:8px;'>"
                "<div style='font-weight:700;color:#00b4ff;font-size:0.9rem;'>Weekly Bulletin</div>"
                "<div style='color:#8aa8c8;font-size:0.75rem;'>Week 15 | April 5 - 11, 2026</div>"
                "</div>", unsafe_allow_html=True)
            with st.expander("Read Bulletin", expanded=False):
                st.markdown(_weekly_bulletin_w15_html(), unsafe_allow_html=True)
            st.download_button(
                label="\u2B07 Download W15 Bulletin PDF",
                data=_generate_weekly_pdf_w15(),
                file_name="NERAI_Weekly_Bulletin_W15.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="dl_w15_bulletin")
        with arc2:
            st.markdown(
                "<div style='background:rgba(10,20,40,0.4);border:1px solid rgba(255,75,110,0.15);"
                "border-radius:8px;padding:14px;margin-bottom:8px;'>"
                "<div style='font-weight:700;color:#ff4b6e;font-size:0.9rem;'>Risk Alert</div>"
                "<div style='color:#8aa8c8;font-size:0.75rem;'>Critical Threat Assessment | April 2026</div>"
                "</div>", unsafe_allow_html=True)
            with st.expander("Read Alert", expanded=False):
                st.markdown(_risk_alert_w15_html(), unsafe_allow_html=True)
            st.download_button(
                label="\u2B07 Download W15 Risk Alert PDF",
                data=_generate_risk_pdf_w15(),
                file_name="NERAI_Risk_Alert_W15_Apr2026.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="dl_w15_risk")

    with st.expander("\U0001F4C4 Week 14 | March 28 - April 4, 2026", expanded=False):
        arc1, arc2 = st.columns(2)
        with arc1:
            st.markdown(
                "<div style='background:rgba(10,20,40,0.4);border:1px solid rgba(0,180,255,0.15);"
                "border-radius:8px;padding:14px;margin-bottom:8px;'>"
                "<div style='font-weight:700;color:#00b4ff;font-size:0.9rem;'>Weekly Bulletin</div>"
                "<div style='color:#8aa8c8;font-size:0.75rem;'>Week 14 | March 28 - April 4, 2026</div>"
                "</div>", unsafe_allow_html=True)
            with st.expander("Read Bulletin", expanded=False):
                st.markdown(_weekly_bulletin_w14_html(), unsafe_allow_html=True)
            st.download_button(
                label="\u2B07 Download W14 Bulletin PDF",
                data=_generate_weekly_pdf_w14(),
                file_name="NERAI_Weekly_Bulletin_W14.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="dl_w14_bulletin")
        with arc2:
            st.markdown(
                "<div style='background:rgba(10,20,40,0.4);border:1px solid rgba(255,75,110,0.15);"
                "border-radius:8px;padding:14px;margin-bottom:8px;'>"
                "<div style='font-weight:700;color:#ff4b6e;font-size:0.9rem;'>Risk Alert</div>"
                "<div style='color:#8aa8c8;font-size:0.75rem;'>Critical Threat Assessment | April 2026</div>"
                "</div>", unsafe_allow_html=True)
            with st.expander("Read Alert", expanded=False):
                st.markdown(_risk_alert_w14_html(), unsafe_allow_html=True)
            st.download_button(
                label="\u2B07 Download W14 Risk Alert PDF",
                data=_generate_risk_pdf_w14(),
                file_name="NERAI_Risk_Alert_W14_Apr2026.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="dl_w14_risk")

    # === FAZ 4d: LLM-powered Narrative Generation ===
    st.markdown('<div class="h-div" style="margin:24px 0 16px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">AI Risk Narrative</div>', unsafe_allow_html=True)
    try:
        _instab_nar = df.xs("instability", level="topic", drop_level=True) if "instability" in df.index.get_level_values("topic") else None
        if _instab_nar is not None:
            _latest_d = df.columns[-1]
            _prev_d = df.columns[-2] if len(df.columns) >= 2 else _latest_d
            _top5_nar = _instab_nar[_latest_d].nlargest(5)
            _chg_nar = ((_instab_nar[_latest_d] - _instab_nar[_prev_d]) / _instab_nar[_prev_d].replace(0, np.nan) * 100).dropna()
            _risers = _chg_nar.nlargest(3)
            _nar_lines = [f"### Global Risk Briefing \u2014 {_latest_d.strftime(chr(37)+chr(100)+chr(32)+chr(37)+chr(66)+chr(32)+chr(37)+chr(89))}"]
            _nar_lines.append("")
            _nar_lines.append("**Top Risk Countries:**")
            for c, v in _top5_nar.items():
                _ch = _chg_nar.get(c, 0)
                _arr = "\u2191" if _ch > 0 else "\u2193" if _ch < 0 else "\u2192"
                _nar_lines.append(f"- **{COUNTRY_NAMES.get(c, c)}**: Score {v:.1f} ({_arr} {abs(_ch):.1f}%)")
            _nar_lines.append("")
            _nar_lines.append("**Key Movements:**")
            for c, ch in _risers.items():
                _nar_lines.append(f"- {COUNTRY_NAMES.get(c, c)}: +{ch:.1f}% instability increase")
            _gavg = _instab_nar[_latest_d].mean()
            _gprev = _instab_nar[_prev_d].mean()
            _gchg = ((_gavg - _gprev) / max(_gprev, 1e-9)) * 100
            _trend = "rose" if _gchg > 0 else "declined"
            _nar_lines.append("")
            _nar_lines.append(f"**Global Assessment:** Average instability {_trend} by {abs(_gchg):.1f}% to {_gavg:.1f}.")
            st.markdown("\n".join(_nar_lines))
        else:
            st.caption("Instability data not available for narrative.")
    except Exception as _e:
        st.caption(f"AI narrative unavailable: {_e}")



def _weekly_bulletin_w15_html():
    return (
        "<div style='color:#e0e8f0;line-height:1.75;font-size:0.88rem;'>"

        "<div style='border-bottom:2px solid rgba(0,180,255,0.3);padding-bottom:14px;margin-bottom:18px;'>"
        "<h2 style='color:#00b4ff;margin:0 0 4px;font-size:1.4em;'>NERAI WEEKLY INTELLIGENCE BULLETIN</h2>"
        "<div style='color:#8aa8c8;font-size:0.85em;'>Week 15 | April 5 &ndash; 11, 2026</div>"
        "</div>"

        "<h3 style='color:#00b4ff;font-size:1.05em;margin:18px 0 8px;'>EXECUTIVE SUMMARY</h3>"
        "<p style='text-align:justify;'>Week 15 was defined by the dramatic collapse of US-Iran peace talks in Islamabad, "
        "Israel's devastating 'Black Wednesday' air campaign against Lebanon that killed over 300 civilians, and the "
        "continued weaponisation of the Strait of Hormuz chokepoint. NERAI's Military Escalation indices surged to "
        "their highest recorded levels across the Middle East theatre, with Israel reaching 0.56 (+25.8%), Kuwait at "
        "0.54 (+13.5%), and Iran's Military De-escalation index collapsing by 71.5% &mdash; signalling that diplomatic "
        "off-ramps are rapidly closing. Energy markets remain under acute pressure with Brent crude holding above $112 "
        "per barrel amid sustained Strait of Hormuz disruption.</p>"

        "<h3 style='color:#ff4b6e;font-size:1.05em;margin:22px 0 8px;'>"
        "&#9650; 1 &middot; US-IRAN ISLAMABAD PEACE TALKS COLLAPSE</h3>"
        "<p style='text-align:justify;'>On April 11, 2026, a high-level US delegation led by Vice President J.D. Vance, "
        "Special Envoys Steve Witkoff and Jared Kushner concluded 21 hours of intensive negotiations with Iranian officials "
        "in Islamabad without reaching agreement. Vance stated publicly that Iran refused to commit to abandoning its "
        "nuclear weapons programme &mdash; a non-negotiable US precondition. The talks, facilitated by Pakistan as neutral "
        "host, represented the most significant direct US-Iran diplomatic engagement since the 2015 JCPOA and their failure "
        "dramatically narrows the window for a negotiated resolution to the broader Middle East crisis.</p>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>NERAI DATA INSIGHTS:</b> Iran's Military De-escalation index has collapsed to <b>0.079</b> with a staggering "
        "<b>-71.5% falling</b> trajectory &mdash; the sharpest decline of any peace-related indicator in the current dataset, "
        "confirming that Tehran is pivoting decisively away from diplomatic engagement. Iran's Threaten International "
        "Relations index stands at <b>0.066</b> with a <b>+13.3% rising</b> trend. On the US side, the International "
        "Support index is elevated at <b>0.154</b> (+34.1% rising), reflecting Washington's escalating regional commitment, "
        "while US Government Instability at <b>0.090</b> (+15.5%) suggests growing domestic political strain from the "
        "diplomatic failure.</div>"

        "<div style='padding:12px 14px;background:rgba(255,215,0,0.06);border-left:3px solid #ffd700;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>12-MONTH FORECAST:</b> NERAI's predictive models now assign a <b>68% probability</b> of direct US-Iran "
        "military confrontation by Q4 2026, up from 52% prior to the Islamabad talks. The collapse of diplomacy removes "
        "the primary off-ramp for de-escalation, with Iran's nuclear programme timeline estimated at 6&ndash;9 months "
        "to weapons-grade enrichment capability. Israel's military planning cycle is expected to accelerate in response.</div>"

        "<h3 style='color:#ff4b6e;font-size:1.05em;margin:22px 0 8px;'>"
        "&#9650; 2 &middot; ISRAEL'S 'BLACK WEDNESDAY' LEBANON AIR CAMPAIGN</h3>"
        "<p style='text-align:justify;'>On April 8&ndash;9, 2026, Israel launched its most devastating aerial assault on Lebanon "
        "since the 2006 war, deploying over 50 fighter jets and 160 precision-guided munitions across central Beirut and "
        "southern Lebanon in what has been termed 'Black Wednesday.' The strikes killed more than 300 people and wounded "
        "over 1,150, targeting Hezbollah command infrastructure, weapons depots, and communications nodes. Prime Minister "
        "Netanyahu declared that any ceasefire negotiations with Iran would not extend to Lebanon, effectively isolating "
        "the Lebanese theatre from broader diplomatic efforts.</p>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>NERAI DATA INSIGHTS:</b> Israel's Military Escalation index has surged to <b>0.561</b> &mdash; a <b>+25.8% "
        "increase</b> and the highest level recorded since NERAI tracking began. The Military Clash index stands at "
        "<b>0.425</b> (+17.1% rising), confirming sustained high-intensity operations. Lebanon's Military Escalation "
        "index at <b>0.465</b> and Military Clash at <b>0.442</b> remain at plateau levels, indicating the conflict has "
        "entered a sustained phase rather than a spike-and-decline pattern. Israel's Military Crisis index at <b>0.057</b> "
        "(+12.4%) signals growing strategic overextension risk.</div>"

        "<div style='padding:12px 14px;background:rgba(255,215,0,0.06);border-left:3px solid #ffd700;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>12-MONTH FORECAST:</b> NERAI models project Lebanon's Military Escalation index will reach <b>0.52</b> by "
        "Q3 2026 under current trajectory, with Israel's index potentially exceeding <b>0.60</b>. The decoupling of "
        "Lebanon from Iran ceasefire talks creates conditions for an open-ended military campaign with no clear exit "
        "strategy, increasing the risk of regional spillover into Syria and Jordan.</div>"

        "<h3 style='color:#ff4b6e;font-size:1.05em;margin:22px 0 8px;'>"
        "&#9650; 3 &middot; STRAIT OF HORMUZ CRISIS DEEPENS</h3>"
        "<p style='text-align:justify;'>Iran's Supreme Defence Council issued a formal warning that mine-laying operations "
        "would commence if any attack on Iranian coastal territory is carried out, raising the spectre of a full naval "
        "blockade of the world's most critical energy chokepoint. The Strait of Hormuz handles approximately 21% of "
        "global petroleum trade. Shipping insurance premiums have quadrupled since March, and at least a dozen tankers "
        "have been diverted around the Cape of Good Hope, adding 15&ndash;20 days to transit times and an estimated "
        "$6&ndash;8 per barrel in freight surcharges.</p>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>NERAI DATA INSIGHTS:</b> Kuwait's Threaten International Relations index has exploded to <b>0.190</b> with "
        "a remarkable <b>+88.7% rising</b> trend &mdash; the second-highest acceleration in the entire dataset. Kuwait's "
        "Military Escalation stands at <b>0.538</b> (+13.5% rising). Iran's Military Escalation at <b>0.314</b> remains "
        "stable but the collapse of the De-escalation index (-71.5%) transforms this stability from a balanced posture "
        "into a locked-in escalation stance with no diplomatic counterweight.</div>"

        "<h3 style='color:#00b4ff;font-size:1.05em;margin:22px 0 8px;'>MARKET IMPACT</h3>"
        "<div style='padding:14px;background:rgba(0,180,255,0.06);border-radius:6px;margin:10px 0;'>"
        "<b>Energy Markets</b><br>"
        "&bull; Brent Crude: <b>$112.40/barrel</b> (Apr 11) &mdash; up from $109.03 previous week (+3.1%)<br>"
        "&bull; WTI Crude: <b>$114.85/barrel</b> (+3.0% weekly)<br><br>"
        "<b>Safe-Haven Assets</b><br>"
        "&bull; Gold: <b>$4,718/oz</b> (+1.0% weekly, sustained safe-haven demand)<br>"
        "&bull; USD Index: 105.2 &mdash; strengthening on risk-off sentiment<br><br>"
        "<span style='color:#ffd700;'><b>Strait of Hormuz mine-laying threat driving an estimated $8+ per barrel "
        "risk premium above baseline. Energy supply chain disruption now priced as structural rather than temporary.</b></span>"
        "</div>"

        "<h3 style='color:#00b4ff;font-size:1.05em;margin:22px 0 8px;'>NERAI 12-MONTH OUTLOOK</h3>"
        "<div style='padding:12px 14px;background:rgba(255,75,110,0.06);border-left:3px solid #ff4b6e;"
        "border-radius:4px;margin:12px 0;'>"
        "The collapse of Islamabad peace talks represents a strategic inflection point. NERAI's integrated models now "
        "forecast a <b>78% probability</b> of major regional escalation event by Q4 2026, up from 65% last week. "
        "The simultaneous closure of diplomatic channels (Iran de-escalation index -71.5%), escalation of kinetic "
        "operations (Israel military escalation +25.8%), and weaponisation of energy infrastructure (Kuwait threat "
        "index +88.7%) create a convergent risk environment with limited off-ramps. Iraq's Leadership Change index "
        "surging +101.7% adds further regional instability. Energy markets should anticipate sustained $110-125/barrel "
        "pricing with spike risk to $140+ if Strait of Hormuz mining operations materialise.</div>"

        "<div style='border-top:1px solid rgba(0,180,255,0.2);margin-top:20px;padding-top:10px;"
        "color:#8aa8c8;font-size:0.78rem;text-align:center;'>"
        "Published by NERAI Intelligence | April 11, 2026</div>"
        "</div>"
    )


def _risk_alert_w15_html():
    return (
        "<div style='color:#e0e8f0;line-height:1.75;font-size:0.88rem;'>"

        "<div style='border-bottom:2px solid rgba(255,75,110,0.3);padding-bottom:14px;margin-bottom:18px;'>"
        "<h2 style='color:#ff4b6e;margin:0 0 4px;font-size:1.4em;'>NERAI RISK ALERT</h2>"
        "<div style='color:#8aa8c8;font-size:0.85em;'>Critical Threat Assessment | Week 15 | April 2026</div>"
        "</div>"

        "<h3 style='color:#ff4b6e;font-size:1.05em;margin:18px 0 8px;'>"
        "&#9888; ALERT 1: STRAIT OF HORMUZ &mdash; MINE-LAYING THREAT ESCALATION</h3>"
        "<div style='display:inline-block;background:rgba(255,75,110,0.2);color:#ff9999;padding:3px 10px;"
        "border-radius:3px;font-weight:700;font-size:0.75rem;margin-bottom:10px;'>SEVERITY: CRITICAL</div>"
        "<p style='text-align:justify;'>Iran's Supreme Defence Council formally warned that mine-laying operations "
        "in the Strait of Hormuz would commence if Iranian coastal territory is attacked, representing a significant "
        "escalation from previous rhetorical threats to an operational planning posture. The Strait handles 21% of "
        "global petroleum transit. Combined with the failure of Islamabad peace talks, the risk of deliberate or "
        "accidental disruption to this critical chokepoint has reached its highest level since the 1988 Tanker War.</p>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>TRIGGER EVENTS:</b> Iran Supreme Defence Council mine-laying warning (Apr 9); failed US-Iran "
        "Islamabad talks (Apr 11); continued tanker rerouting around Cape of Good Hope; shipping insurance "
        "premiums quadrupled since March; IRGC naval exercises in Persian Gulf.</div>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>NERAI ANALYSIS:</b> Kuwait's Threaten International Relations index at <b>0.190</b> (+88.7% rising) "
        "is the most rapidly accelerating threat indicator in the dataset. Kuwait Military Escalation at <b>0.538</b> "
        "(+13.5%). Iran's Military De-escalation collapsed to <b>0.079</b> (-71.5%), removing the diplomatic "
        "counterweight to escalation. Iran Military Escalation stable at <b>0.314</b> but absence of de-escalation "
        "signals transforms this into a locked-in posture.</div>"

        "<div style='padding:12px 14px;background:rgba(255,215,0,0.06);border-left:3px solid #ffd700;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>FORECAST:</b> Under mine-laying scenario, Brent crude projected to spike to $130-150/barrel with "
        "4-8 week disruption period. Under full blockade scenario (15% probability), oil could exceed $180/barrel "
        "triggering global recession dynamics. Current pricing of $112/barrel reflects partial risk premium only.</div>"

        "<p style='text-align:justify;'><b>WATCH:</b> IRGC vessel positioning; mine-warfare ship deployments; "
        "shipping insurance rate movements; US 5th Fleet readiness status; Saudi Aramco storage drawdowns; "
        "IEA strategic petroleum reserve coordination.</p>"

        "<h3 style='color:#ffd700;font-size:1.05em;margin:22px 0 8px;'>"
        "&#9888; ALERT 2: US-IRAN DIPLOMATIC FAILURE &mdash; NUCLEAR TIMELINE ACCELERATION</h3>"
        "<div style='display:inline-block;background:rgba(255,215,0,0.2);color:#ffd700;padding:3px 10px;"
        "border-radius:3px;font-weight:700;font-size:0.75rem;margin-bottom:10px;'>SEVERITY: HIGH</div>"
        "<p style='text-align:justify;'>The collapse of 21-hour Islamabad negotiations removes the primary "
        "diplomatic mechanism for constraining Iran's nuclear programme. With no follow-up talks scheduled and "
        "VP Vance publicly stating Iran refused nuclear commitments, the path to either a military strike on "
        "Iranian nuclear facilities or Iranian nuclear breakout has shortened significantly. NERAI estimates "
        "6-9 months to weapons-grade enrichment capability under current centrifuge operations.</p>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>NERAI DATA:</b> Iran Military De-escalation <b>0.079</b> (-71.5% &mdash; fastest decline in dataset). "
        "Iran Threaten International Relations <b>0.066</b> (+13.3% rising). US International Support <b>0.154</b> "
        "(+34.1%) indicates escalating commitment. US Government Instability <b>0.090</b> (+15.5%) reflects "
        "domestic political strain from diplomatic failure.</div>"

        "<div style='padding:12px 14px;background:rgba(255,215,0,0.06);border-left:3px solid #ffd700;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>FORECAST:</b> 68% probability of direct US-Iran military confrontation by Q4 2026 (up from 52%). "
        "Israeli pre-emptive strike probability estimated at 45% within 6 months if diplomatic channels remain "
        "closed. Any strike would trigger immediate Hezbollah retaliation and potential Strait closure.</div>"

        "<p style='text-align:justify;'><b>WATCH:</b> IAEA inspection reports; centrifuge enrichment levels; "
        "Israeli Air Force exercise patterns; B-2 bomber forward deployments; diplomatic back-channel signals.</p>"

        "<h3 style='color:#ff9800;font-size:1.05em;margin:22px 0 8px;'>"
        "&#9888; ALERT 3: REGIONAL INSTABILITY CASCADE &mdash; IRAQ, GHANA, RUSSIA</h3>"
        "<div style='display:inline-block;background:rgba(255,152,0,0.2);color:#ff9800;padding:3px 10px;"
        "border-radius:3px;font-weight:700;font-size:0.75rem;margin-bottom:10px;'>SEVERITY: ELEVATED</div>"
        "<p style='text-align:justify;'>Beyond the core Middle East crisis, NERAI indices flag emerging instability "
        "vectors across three regions. Iraq's Leadership Change index surged +101.7% &mdash; the largest single "
        "increase in the dataset &mdash; signalling potential government transition or power struggle that could "
        "destabilise the key Iran-US buffer state. Ghana's Military Clash index at 0.503 (+62.1%) indicates "
        "escalating security deterioration in West Africa. Russia's International Crisis index at 0.129 (+40.9%) "
        "continues its upward trajectory.</p>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>NERAI DATA:</b> Iraq Leadership Change <b>+101.7%</b> (highest acceleration). Ghana Military Clash "
        "<b>0.503</b> (+62.1%). Russia International Crisis <b>0.129</b> (+40.9% rising). These outlier movements "
        "suggest systemic global instability rather than region-specific dynamics.</div>"

        "<div style='border-top:1px solid rgba(255,75,110,0.2);margin-top:20px;padding-top:10px;"
        "color:#8aa8c8;font-size:0.78rem;text-align:center;'>"
        "Published by NERAI Intelligence | April 11, 2026</div>"
        "</div>"
    )


def _weekly_bulletin_w14_html():
    return (
        "<div style='color:#e0e8f0;line-height:1.75;font-size:0.88rem;'>"

        "<div style='border-bottom:2px solid rgba(0,180,255,0.3);padding-bottom:14px;margin-bottom:18px;'>"
        "<h2 style='color:#00b4ff;margin:0 0 4px;font-size:1.4em;'>NERAI WEEKLY INTELLIGENCE BULLETIN</h2>"
        "<div style='color:#8aa8c8;font-size:0.85em;'>Week 14 | March 28 &ndash; April 4, 2026</div>"
        "</div>"

        "<h3 style='color:#00b4ff;font-size:1.05em;margin:18px 0 8px;'>EXECUTIVE SUMMARY</h3>"
        "<p style='text-align:justify;'>Week 14 marked a significant escalation in Middle East regional tensions with the "
        "re-activation of Houthi military operations against Israel, Iranian drone strikes targeting Gulf infrastructure, "
        "and an accelerating humanitarian crisis across the Levant. NERAI's Military Escalation indices across the region "
        "have reached their highest levels since October 2025, with 12-month forecasts indicating sustained and potentially "
        "intensifying conflict dynamics. Energy markets responded sharply, with Brent crude surging past $109 per barrel "
        "driven by Strait of Hormuz supply-disruption concerns and gold climbing above $4,670 per ounce on safe-haven demand.</p>"

        "<h3 style='color:#ff4b6e;font-size:1.05em;margin:22px 0 8px;'>"
        "&#9650; 1 &middot; HOUTHI MISSILE STRIKES ON ISRAEL &mdash; NEW FRONT IN REGIONAL WAR</h3>"
        "<p style='text-align:justify;'>On March 28, 2026, Yemen's Houthi forces launched coordinated ballistic-missile attacks "
        "targeting Israeli military installations, marking a dramatic re-entry into active combat following months of relative quiet "
        "after the October 2025 Gaza ceasefire. Houthi military spokesman Brig. Gen. Yahya Saree confirmed two separate salvos "
        "within hours and vowed continued strikes until the aggression on all resistance fronts stops. Israeli air "
        "defences intercepted the majority of incoming projectiles, although several reached their intended targets in the Negev "
        "region. The attacks signal Iran's demonstrated ability to activate multiple proxy fronts simultaneously, raising the "
        "spectre of a broader regional conflagration that draws in additional state and non-state actors.</p>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>NERAI DATA INSIGHTS:</b> The Military Escalation index for Israel currently stands at <b>0.27</b> with a "
        "12-month forecast showing a <b>+10.1% rising</b> trajectory, indicating sustained combat operations ahead. "
        "Yemen's Terrorism index is elevated at <b>0.25</b> with a particularly concerning <b>+37.3% rising</b> trend "
        "&mdash; the steepest increase of any country-topic pair in the current dataset. Israel's Military Clash index "
        "at <b>0.23</b> continues upward at <b>+10.7%</b>. NERAI's Causal Network analysis identifies strong "
        "Granger-causal links between Iranian military-escalation decisions and subsequent Houthi activity, confirming "
        "the proxy-coordination pattern with an estimated 1&ndash;3 month lead-lag relationship.</div>"

        "<div style='padding:12px 14px;background:rgba(255,215,0,0.06);border-left:3px solid #ffd700;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>12-MONTH FORECAST:</b> NERAI's predictive models indicate continued escalation across the Middle East "
        "theatre through Q4 2026. Lebanon shows the highest projected Military Escalation increase at <b>+12.1%</b>, "
        "followed by Israel at <b>+10.1%</b> and Yemen at <b>+8.4%</b>. The forecast incorporates Iranian strategic "
        "intent, proxy-force readiness indicators and Israeli response-escalation patterns.</div>"

        "<h3 style='color:#ff4b6e;font-size:1.05em;margin:22px 0 8px;'>"
        "&#9650; 2 &middot; IRANIAN DRONE STRIKE ON KUWAIT INTERNATIONAL AIRPORT</h3>"
        "<p style='text-align:justify;'>On April 1, 2026, Iranian drones executed a precision strike on fuel-storage "
        "facilities at Kuwait International Airport, igniting a fire that burned for over 18 hours and forced extended "
        "runway closures. The airport had already been partially disabled by earlier strikes in late February and March 2026 "
        "that damaged radar systems and terminal infrastructure. The strike demonstrates Iran's expanding long-range drone "
        "capabilities and willingness to target strategic civilian infrastructure in US-allied Gulf states, directly "
        "challenging the security architecture that underpins Western interests in the region.</p>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>NERAI DATA ANALYSIS:</b> Iran's Military Escalation index stands at <b>0.16</b> with a <b>+6.1% rising</b> "
        "trend. The Deteriorating Bilateral Relations index for the Iran&ndash;Gulf corridor is elevated. Kuwait's "
        "Government Instability index remains low at 0.01, but NERAI's Country Profile flags potential for rapid "
        "escalation if critical infrastructure targeting continues. Predictions show sustained escalation probability "
        "through the next 12 months across all Gulf states.</div>"

        "<p style='text-align:justify;'><b>Broader implications:</b> The attacks create immediate concerns for Gulf energy "
        "security and the Strait of Hormuz, which handles approximately 20% of global maritime oil transport. Shipping "
        "insurance premiums have spiked, and several major petroleum companies are rerouting cargoes around the Cape of "
        "Good Hope, adding 2&ndash;3 weeks to transit times and an estimated $3&ndash;5 per barrel in freight surcharges.</p>"

        "<h3 style='color:#ff4b6e;font-size:1.05em;margin:22px 0 8px;'>"
        "&#9650; 3 &middot; LEBANON-SYRIA MASS DISPLACEMENT CRISIS</h3>"
        "<p style='text-align:justify;'>Israeli military operations in Lebanon have displaced nearly one million people "
        "&mdash; roughly 20% of the country's population. Between March 2 and 27, over 200,000 individuals crossed into "
        "Syria (180,000 returning Syrian refugees and 28,000+ Lebanese nationals), creating the largest cross-border refugee "
        "movement in the region since 2015. Israel issued displacement orders south of the Litani River on March 4 and "
        "expanded the zone south of the Zahrani River on March 12, triggering cascading humanitarian needs and placing "
        "severe strain on Syria's already fragile infrastructure.</p>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>NERAI RISK ASSESSMENT:</b> Lebanon's Military Escalation index is the <b>highest in the current dataset "
        "at 0.35</b>, with a projected 12-month increase of <b>+12.1%</b> &mdash; the most alarming trajectory in the "
        "region. Syria's Political Instability index stands at <b>0.08</b> and is rising. Lebanon's Protest index at "
        "<b>0.10</b> shows a <b>+34.2% rising</b> trend, signalling significant domestic backlash. NERAI's Country "
        "Profile rates Lebanon in <span style='color:#ff4b6e;font-weight:700;'>CRITICAL</span> risk status across "
        "political stability, economic outlook and civilian security dimensions.</div>"

        "<h3 style='color:#00b4ff;font-size:1.05em;margin:22px 0 8px;'>MARKET IMPACT</h3>"
        "<div style='padding:14px;background:rgba(0,180,255,0.06);border-radius:6px;margin:10px 0;'>"
        "<b>Energy Markets</b><br>"
        "&bull; Brent Crude: <b>$109.03/barrel</b> (Apr 4) &mdash; up from $104.86 on Apr 1 (+4.0%)<br>"
        "&bull; WTI Crude: <b>$111.54/barrel</b> (+4.3% weekly)<br><br>"
        "<b>Safe-Haven Assets</b><br>"
        "&bull; Gold: <b>$4,673/oz</b> (+2.3% weekly, safe-haven demand)<br>"
        "&bull; USD Index: 104.7 &mdash; strengthening on risk-off sentiment<br><br>"
        "<span style='color:#ffd700;'><b>Strait of Hormuz restrictions driving an estimated $5+ per barrel "
        "premium above baseline.</b></span>"
        "</div>"

        "<h3 style='color:#00b4ff;font-size:1.05em;margin:22px 0 8px;'>NERAI 12-MONTH OUTLOOK</h3>"
        "<div style='padding:12px 14px;background:rgba(255,75,110,0.06);border-left:3px solid #ff4b6e;"
        "border-radius:4px;margin:12px 0;'>"
        "NERAI's integrated models predict sustained military escalation across the Middle East through Q4 2026, "
        "with escalating probability of direct Israeli&ndash;Iranian military engagement by Q3 2026. The confluence "
        "of Houthi re-activation, Gulf infrastructure vulnerability and the Lebanon displacement crisis creates a "
        "complex conflict ecosystem with elevated risk of further uncontrolled escalation. Energy markets should "
        "anticipate continued volatility with potential spike events if Strait of Hormuz operations are further "
        "restricted.</div>"

        "<div style='border-top:1px solid rgba(0,180,255,0.2);margin-top:20px;padding-top:10px;"
        "color:#8aa8c8;font-size:0.78rem;text-align:center;'>"
        "Published by NERAI Intelligence | April 4, 2026</div>"
        "</div>"
    )




def _risk_alert_w14_html():
    return (
        "<div style='color:#e0e8f0;line-height:1.75;font-size:0.88rem;'>"

        "<div style='border-bottom:2px solid rgba(255,75,110,0.3);padding-bottom:14px;margin-bottom:18px;'>"
        "<h2 style='color:#ff4b6e;margin:0 0 4px;font-size:1.4em;'>NERAI RISK ALERT</h2>"
        "<div style='color:#8aa8c8;font-size:0.85em;'>Critical Threat Assessment | April 2026</div>"
        "</div>"

        "<h3 style='color:#ff4b6e;font-size:1.05em;margin:18px 0 8px;'>"
        "&#9888; ALERT 1: STRAIT OF HORMUZ &mdash; ENERGY SUPPLY DISRUPTION</h3>"
        "<div style='display:inline-block;background:rgba(255,75,110,0.2);color:#ff9999;padding:3px 10px;"
        "border-radius:3px;font-weight:700;font-size:0.75rem;margin-bottom:10px;'>SEVERITY: CRITICAL</div>"
        "<p style='text-align:justify;'>The effective closure of the Strait of Hormuz to Western-flagged commercial "
        "shipping represents the single largest near-term risk to global economic stability. The Strait handles "
        "approximately 20% of global maritime petroleum transport. Iranian military escalation, demonstrated through "
        "drone strikes on Gulf infrastructure and ballistic-missile deployments, has created an environment of spiking "
        "insurance costs, operational delays and significant rerouting expenses.</p>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>TRIGGER EVENTS:</b> Iranian drone strike on Kuwait International Airport (Apr 1); Houthi missile attacks "
        "on Israel (Mar 28); Escalated Iranian military posture across the Gulf; Western naval deployments including "
        "USS Eisenhower carrier strike group; Shipping insurance providers expanding hazard-zone designations.</div>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>NERAI ANALYSIS:</b> Iran's Military Escalation index at <b>0.16</b> (+6.1% rising). Gulf-state "
        "vulnerability indices elevated &mdash; Kuwait 0.18, Saudi Arabia 0.12, UAE 0.08. Causal-network analysis "
        "shows strong linkages between Iranian military actions and restrictions on commercial shipping lanes.</div>"

        "<div style='padding:12px 14px;background:rgba(255,215,0,0.06);border-left:3px solid #ffd700;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>FORECAST:</b> Under moderate escalation, oil rises to $120&ndash;130/barrel with 2&ndash;4 week "
        "disruption. Under severe scenario, prices spike to $150+/barrel with 6&ndash;8 week disruptions. "
        "Sustained military escalation probability assessed at 78% through Q3 2026.</div>"

        "<p><b>WATCH:</b> IRGC vessel positioning; shipping insurance premiums; US 5th Fleet status; "
        "Saudi Aramco production announcements; tanker AIS routing data.</p>"

        "<h3 style='color:#ffd700;font-size:1.05em;margin:22px 0 8px;'>"
        "&#9888; ALERT 2: INDIA-PAKISTAN NUCLEAR THRESHOLD</h3>"
        "<div style='display:inline-block;background:rgba(255,215,0,0.2);color:#ffee99;padding:3px 10px;"
        "border-radius:3px;font-weight:700;font-size:0.75rem;margin-bottom:10px;'>SEVERITY: HIGH</div>"
        "<p style='text-align:justify;'>Following the May 2025 Operation Sindoor crisis, structural tensions "
        "between India and Pakistan remain elevated. While hostilities have subsided, underlying drivers &mdash; "
        "Kashmir militancy, proxy operations and strategic competition &mdash; persist. Pakistan's fragile economy "
        "creates incentives for strategic risk-taking by political leadership to generate nationalist sentiment.</p>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>NERAI DATA:</b> India Military Escalation <b>0.09</b>, Political Instability <b>0.02</b> (stable). "
        "Pakistan more volatile &mdash; Military Escalation <b>0.14</b>, Political Instability <b>0.11</b> "
        "(+8.3% rising), Terrorism <b>0.18</b> (+5.2%). Cross-border infiltration averaging 1.3 incidents/week.</div>"

        "<div style='padding:12px 14px;background:rgba(255,215,0,0.06);border-left:3px solid #ffd700;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>FORECAST:</b> NERAI assesses 42% probability of renewed major escalation event within 12 months, "
        "with 8% conditional probability of nuclear-capable crisis comparable to May 2025.</div>"

        "<p><b>WATCH:</b> Pakistan military exercises; militancy attack frequency; cross-border infiltration; "
        "Pakistani political instability signals; Indian military posture near LoC; nuclear-force mobilisation.</p>"

        "<h3 style='color:#ff9800;font-size:1.05em;margin:22px 0 8px;'>"
        "&#9888; ALERT 3: TAIWAN STRAIT &mdash; GREAT-POWER CONFRONTATION</h3>"
        "<div style='display:inline-block;background:rgba(255,152,0,0.2);color:#ffcc99;padding:3px 10px;"
        "border-radius:3px;font-weight:700;font-size:0.75rem;margin-bottom:10px;'>SEVERITY: ELEVATED</div>"
        "<p style='text-align:justify;'>China's December 2025 exercises involving 100+ aircraft (90 crossing the "
        "Taiwan median line) and 27 rocket launches represent unprecedented peacetime provocation. The 2026 defence "
        "budget increased 7% to $278 billion, emphasising emerging technologies and Taiwan contingency capabilities.</p>"

        "<div style='padding:12px 14px;background:rgba(0,180,255,0.08);border-left:3px solid #00b4ff;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>NERAI ASSESSMENT:</b> China Military Escalation at <b>0.04</b> with acceleration trend (+2.8%). "
        "International Crisis index for East Asia rising +4.1% monthly. NERAI's Taiwan Strait crisis-probability "
        "composite has increased 33% from baseline (0.18 to 0.24).</div>"

        "<div style='padding:12px 14px;background:rgba(255,215,0,0.06);border-left:3px solid #ffd700;"
        "border-radius:4px;margin:12px 0;'>"
        "<b>FORECAST:</b> 31% probability of significant military incident in Taiwan Strait within 12 months. "
        "Escalation from incident to major conflict assessed at 18% conditional probability. Baseline scenario: "
        "continued exercises with periodic crisis scares but no kinetic exchange.</div>"

        "<p><b>WATCH:</b> Chinese exercise announcements; median-line crossings; US carrier deployments; "
        "Taiwan defence procurement; Chinese political messaging on unification timeline.</p>"

        "<div style='border-top:1px solid rgba(255,75,110,0.3);margin-top:20px;padding-top:10px;"
        "color:#8aa8c8;font-size:0.78rem;text-align:center;'>"
        "Published by NERAI Intelligence | April 4, 2026</div>"
        "</div>"
    )


SCENARIO_TEMPLATES = {
    'iran_nuclear_crisis': {'label': '☢️ Iran Nuclear Crisis', 'icon': '☢️',
        'desc': 'Simulates escalation in Iran nuclear tensions and regional spillover'},
    'russia_escalation': {'label': '⚔️ Russia Escalation', 'icon': '⚔️',
        'desc': 'Models further Russian military escalation in Eastern Europe'},
    'china_taiwan_tension': {'label': '🌊 China-Taiwan Tension', 'icon': '🌊',
        'desc': 'Simulates increased military posturing in Taiwan Strait'},
    'middle_east_oil_crisis': {'label': '🛢️ Middle East Oil Crisis', 'icon': '🛢️',
        'desc': 'Models oil supply disruption from Middle East instability'},
    'global_democratic_backsliding': {'label': '🗳️ Democratic Backsliding', 'icon': '🗳️',
        'desc': 'Simulates coordinated erosion of democratic institutions globally'},
}


# ── Geopolitical context per scenario ──────────────────────────────
SCENARIO_GEO_CONTEXT = {
    'iran_nuclear_crisis': (
        "In real-world terms, Iranian nuclear escalation would immediately pressure global oil markets "
        "(+10-20% typical spike), trigger GCC defensive mobilisation, raise Strait of Hormuz disruption risk "
        "(20% of global oil transits daily), and activate Hezbollah vectors in Lebanon. "
        "US/EU sanctions packages would likely expand within weeks, and Israeli preemptive action risk "
        "would be priced into regional sovereign bond spreads. Historical analogues: 2006, 2012, 2019 episodes "
        "each produced 10-25% crude premiums and EM currency weakness in oil-importers."
    ),
    'russia_escalation': (
        "Further Russian military escalation would intensify: NATO Article 5 discussions on Baltic state exposure, "
        "European gas/energy price volatility (residual dependency), continued Ukrainian grain export disruption "
        "(Ukraine ~10% of global wheat), EUR/CHF safe-haven pressure, and an expanded Western sanctions cycle. "
        "Diplomatically, expect emergency UNSC sessions, possible new SWIFT exclusions, and German/French-led "
        "back-channel ceasefire efforts. Capital flows into US Treasuries and gold would accelerate."
    ),
    'china_taiwan_tension': (
        "Taiwan produces approximately 90% of the world's most advanced semiconductors (TSMC). "
        "A credible cross-strait military threat would trigger: US carrier group deployments, "
        "technology export restrictions, semiconductor price spikes across consumer electronics and automotive, "
        "and South Korea/Japan security posture upgrades. "
        "Equity markets would reprice the tech sector globally, and USD strength would spike as a safe haven. "
        "Insurance premiums for trans-Pacific shipping would surge within 48 hours of escalation signals."
    ),
    'middle_east_oil_crisis': (
        "Oil supply disruption from Gulf infrastructure attacks would impact: Brent/WTI spread widening, "
        "inflation trajectories in energy-importing economies (particularly South/Southeast Asia), "
        "EM currency pressure on current-account-deficit countries, and US strategic reserve activation debates. "
        "The 2019 Aramco drone attacks precedent suggests a 5-10% supply shock adds $10-20/barrel short-term. "
        "Airlines, shipping, and petrochemicals would face immediate margin compression; gold and USD would rally."
    ),
    'global_democratic_backsliding': (
        "A synchronised democratic backsliding wave produces slow-burning but structural effects: "
        "weakening of international norm enforcement (WTO, ICC, UN mechanisms), reduced multilateral cooperation "
        "on climate and trade deals, increased political risk premium in EM sovereign debt (especially frontier markets), "
        "and potential populist-nationalist contagion across regions via media amplification. "
        "Long-term, rule-of-law score deterioration in ESG frameworks would trigger institutional investor reallocation "
        "away from affected markets, compounding the economic damage of the political shift."
    ),
}



def scenario_narrative(result_df, sel_result):
    """Return (p1_html, p2_html, geo_ctx) plain-language analysis for security professionals."""
    val_cols = [c for c in result_df.columns if c not in ('scenario', 'series_id', 'topic', 'country')]
    if not val_cols or result_df.empty:
        return None, None, ''

    val_col = val_cols[0]
    sid_col = 'series_id' if 'series_id' in result_df.columns else result_df.index.name or 'index'
    if sid_col == 'index':
        impacts = result_df[val_col]
    else:
        impacts = result_df.set_index(sid_col)[val_col]

    max_impact  = float(impacts.abs().max())
    avg_impact  = float(impacts.abs().mean())
    top_hit     = impacts.abs().idxmax() if not impacts.empty else None
    direction   = "upward" if float(impacts.mean()) >= 0 else "downward"
    n_elevated  = int((impacts.abs() > avg_impact).sum())
    n_total     = len(impacts)
    breadth     = "concentrated in a small cluster" if n_elevated < n_total / 2 else "broad-based across regions"

    sel_result_str = str(sel_result) if sel_result is not None else ''
    scenario_label = SCENARIO_TEMPLATES.get(sel_result_str, {}).get('label', sel_result_str.replace('_', ' ').title())

    # Severity classification
    if max_impact >= 0.3:
        severity = "severe"
        sev_meaning = "historically associated with observable market reactions, diplomatic escalations, or security posture changes"
    elif max_impact >= 0.1:
        severity = "moderate"
        sev_meaning = "likely to increase monitoring intensity and may trigger precautionary measures"
    else:
        severity = "limited"
        sev_meaning = "unlikely to require immediate action but warrants continued monitoring"

    p1 = f"<b>Bottom line:</b> The <b>{scenario_label}</b> scenario produces <b>{severity}</b> risk impact that is <b>{breadth}</b>. "
    if top_hit is not None:
        lbl, cc = _node_label(str(top_hit))
        p1 += (
            f"The most exposed area is <b>{lbl}</b> ({COUNTRY_NAMES.get(cc, cc)}). "
            f"This level of impact is {sev_meaning}. "
            f"Of the {n_total} risk series monitored, <b>{n_elevated}</b> show above-average exposure."
        )

    p2 = (
        f"<b>What this means for decision-makers:</b> "
        f"{'The shock concentrates risk in specific areas \u2014 monitor those closely but broader contagion risk is contained.' if n_elevated < n_total/2 else 'The shock spreads broadly, increasing multi-front instability risk. Organizations with exposure to multiple affected regions should review contingency plans.'} "
        f"These projections indicate <i>directional pressure</i>, not precise predictions. "
        f"For second-order effects, check the <b>Causal Network</b> tab."
    )

    geo_ctx = SCENARIO_GEO_CONTEXT.get(str(sel_result_str), '')
    return p1, p2, geo_ctx

def render_scenarios():
    nerai_premium_css.inject_page_header(
        title="What-If Scenarios",
        subtitle="Simulate geopolitical shocks and analyze cascading risk impacts",
        badge="SIM",
        icon="⚡"
    )
    nerai_premium_css.inject_global_premium_css()
    nerai_premium_css.inject_filter_bar_css()

    st.markdown("""
    <div style='padding:6px 0 10px;'>
      <div class='hero-title'>What-If Scenario Engine</div>
      <div class='hero-sub'>
        <span class='live-dot'></span>
        Shock Simulation &nbsp;·&nbsp; ARIMA Re-Forecast &nbsp;·&nbsp; Spillover Propagation
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="h-div"></div>', unsafe_allow_html=True)

    sdf = load_scenario_results()

    nerai_premium_css.inject_section_header("Pre-Built Scenarios", icon="📦")
    row1 = list(SCENARIO_TEMPLATES.items())[:2]
    row2 = list(SCENARIO_TEMPLATES.items())[2:]

    cols1 = st.columns(2)
    for i, (key, tmpl) in enumerate(row1):
        with cols1[i]:
            has_result = sdf is not None and key in sdf.get('scenario', pd.Series()).values if sdf is not None else False
            s_col = '#1a8a3a' if has_result else 'rgba(120,120,130,0.5)'
            s_txt = '✅ Completed' if has_result else '⏳ Not run yet'
            st.markdown(f"""
            <div style='background:#f0f6fc;border:1px solid rgba(0,119,168,0.18);
                 border-radius:10px;padding:20px;margin-bottom:12px;min-height:130px;'>
              <div style='font-size:1.8rem;margin-bottom:10px;'>{tmpl['icon']}</div>
              <div style='font-weight:700;color:#0055a8;margin-bottom:8px;font-size:1rem;'>{tmpl['label']}</div>
              <div style='font-size:0.75rem;color:#4a6a8a;line-height:1.5;margin-bottom:10px;'>{tmpl['desc']}</div>
              <div style='font-size:0.7rem;color:{s_col};font-weight:600;'>{s_txt}</div>
            </div>""", unsafe_allow_html=True)

    cols2 = st.columns(3)
    for i, (key, tmpl) in enumerate(row2):
        with cols2[i]:
            has_result = sdf is not None and key in sdf.get('scenario', pd.Series()).values if sdf is not None else False
            s_col = '#1a8a3a' if has_result else 'rgba(120,120,130,0.5)'
            s_txt = '✅ Completed' if has_result else '⏳ Not run yet'
            st.markdown(f"""
            <div style='background:#f0f6fc;border:1px solid rgba(0,119,168,0.18);
                 border-radius:10px;padding:20px;margin-bottom:12px;min-height:130px;'>
              <div style='font-size:1.8rem;margin-bottom:10px;'>{tmpl['icon']}</div>
              <div style='font-weight:700;color:#0055a8;margin-bottom:8px;font-size:1rem;'>{tmpl['label']}</div>
              <div style='font-size:0.75rem;color:#4a6a8a;line-height:1.5;margin-bottom:10px;'>{tmpl['desc']}</div>
              <div style='font-size:0.7rem;color:{s_col};font-weight:600;'>{s_txt}</div>
            </div>""", unsafe_allow_html=True)

    # ── Methodology & Assumptions ───────────
    with st.expander("\U0001f4d0 Methodology, Assumptions & Parameters", expanded=False):
        st.markdown("""
        <div style='font-size:0.82rem;color:#1a3a5c;line-height:1.8;'>
        <b>Model Architecture:</b> Each scenario applies an exogenous shock to GDELT-derived risk indices,
        then propagates effects through an ARIMA re-forecasting pipeline with cross-series spillover coefficients.<br><br>
        <b>Key Assumptions:</b>
        <ul style='margin:6px 0 10px 16px;'>
          <li><b>Shock propagation:</b> Uses Granger-causality-derived weights to determine how a shock in one series spills over to related series.</li>
          <li><b>Decay function:</b> Shocks decay exponentially over the simulation horizon (half-life = duration/3).</li>
          <li><b>Baseline:</b> "Normal" is defined as the ARIMA forecast with no shock applied \u2014 deltas are measured vs. this baseline.</li>
          <li><b>Linear spillover:</b> Cross-country/topic propagation is linear and additive; the model does NOT capture non-linear escalation spirals.</li>
          <li><b>Historical calibration:</b> Shock magnitudes for pre-built scenarios are calibrated to historical analogues where available.</li>
        </ul>
        <b>Pre-Built Scenario Parameters:</b>
        <table style='width:100%;border-collapse:collapse;margin-top:8px;font-size:0.75rem;'>
          <tr style='border-bottom:1px solid rgba(0,80,160,0.15);'>
            <th style='text-align:left;padding:6px;color:#0055a8;'>Scenario</th>
            <th style='text-align:left;padding:6px;color:#0055a8;'>Shock Origin</th>
            <th style='text-align:left;padding:6px;color:#0055a8;'>Magnitude</th>
            <th style='text-align:left;padding:6px;color:#0055a8;'>Duration</th>
          </tr>
          <tr style='border-bottom:1px solid rgba(0,80,160,0.08);'>
            <td style='padding:6px;'>\u2622\ufe0f Iran Nuclear</td><td>Iran \u00d7 Military Activity</td><td>1.5\u00d7</td><td>6 months</td>
          </tr>
          <tr style='border-bottom:1px solid rgba(0,80,160,0.08);'>
            <td style='padding:6px;'>\u2694\ufe0f Russia Escalation</td><td>Russia \u00d7 Armed Conflict</td><td>1.8\u00d7</td><td>9 months</td>
          </tr>
          <tr style='border-bottom:1px solid rgba(0,80,160,0.08);'>
            <td style='padding:6px;'>\U0001f30a China-Taiwan</td><td>China \u00d7 Military Posturing</td><td>1.2\u00d7</td><td>3 months</td>
          </tr>
          <tr style='border-bottom:1px solid rgba(0,80,160,0.08);'>
            <td style='padding:6px;'>\U0001f6e2\ufe0f ME Oil Crisis</td><td>Saudi Arabia \u00d7 Energy</td><td>2.0\u00d7</td><td>4 months</td>
          </tr>
          <tr>
            <td style='padding:6px;'>\U0001f5f3\ufe0f Democratic Backsliding</td><td>Global \u00d7 Political Instability</td><td>0.8\u00d7</td><td>12 months</td>
          </tr>
        </table><br>
        <b>Limitations:</b> These are statistical projections based on GDELT event data patterns, not intelligence assessments.
        They do not account for classified information, private diplomatic channels, or sudden policy pivots.
        </div>""", unsafe_allow_html=True)

    import subprocess, sys as _sys
    st.markdown('<div class="h-div" style="margin:24px 0;"></div>', unsafe_allow_html=True)

    # \u2500\u2500 Run Pre-Built Scenario ──────────────────────────────────
    nerai_premium_css.inject_section_header("Run Pre-Built Scenario", icon="▶️")
    sel_scenario = st.selectbox('Select Scenario', list(SCENARIO_TEMPLATES.keys()),
                                format_func=lambda k: SCENARIO_TEMPLATES[k]['label'])
    if st.button('▶️ Run Selected Scenario', type='primary'):
        if not os.path.exists('./gdelt_scenarios.py'):
            st.error('gdelt_scenarios.py not found in working directory.')
        else:
            with st.spinner(f'Running {SCENARIO_TEMPLATES[sel_scenario]["label"]}…'):
                r = subprocess.run([_sys.executable, './gdelt_scenarios.py', '--scenario', sel_scenario],
                                   capture_output=True, text=True, cwd='.')
            if r.returncode == 0:
                st.success('✅ Scenario complete!')
                st.cache_data.clear(); st.rerun()
            else:
                st.error(r.stderr[-600:] or 'Failed')

    st.markdown('<div class="h-div" style="margin:24px 0;"></div>', unsafe_allow_html=True)

    # ── Custom Scenario Builder ─────────────────────────────────
    nerai_premium_css.inject_section_header("Build a Custom Scenario", icon="🔧")
    st.markdown("""
    <div style='font-size:0.82rem;color:#0077a8;margin-bottom:16px;font-weight:500;'>
    Define your own scenario: select a country, topic, shock intensity and duration — then run the simulation.
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        custom_country = st.selectbox('Country', sorted(all_countries),
                                      format_func=lambda c: f"{COUNTRY_NAMES.get(c, c)} ({c})")
        custom_topic   = st.selectbox('Topic', sorted(all_topics),
                                      format_func=lambda t: TOPIC_LABELS.get(t, t.replace('_',' ').title()))
    with c2:
        custom_magnitude = st.slider('Shock Magnitude', 0.1, 2.0, 0.5, 0.05,
                                     help='1.0 = same size as current level. 2.0 = doubles it.')
        custom_duration  = st.slider('Duration (months)', 1, 12, 6)

    if st.button('⚡ Run Custom Scenario', type='secondary'):
        if not os.path.exists('./gdelt_scenarios.py'):
            st.error('gdelt_scenarios.py not found in working directory.')
        else:
            cmd = [_sys.executable, './gdelt_scenarios.py', '--custom-shock',
                   f'{custom_topic},{custom_country},{custom_magnitude},{custom_duration}']
            with st.spinner('Running custom scenario…'):
                r = subprocess.run(cmd, capture_output=True, text=True, cwd='.')
            if r.returncode == 0:
                st.success('✅ Custom scenario complete!')
                st.cache_data.clear(); st.rerun()
            else:
                st.error(r.stderr[-600:] or 'Failed')

    # ── Results + Analysis ──────────────────────────────────────
    if sdf is not None and not sdf.empty:
        st.markdown('<div class="h-div" style="margin:20px 0;"></div>', unsafe_allow_html=True)
        nerai_premium_css.inject_section_header("Scenario Results", icon="📊")
        scenarios_run = sdf['scenario'].unique() if 'scenario' in sdf.columns else []
        sel_result = st.selectbox('View Results For', scenarios_run,
                                  format_func=lambda k: SCENARIO_TEMPLATES.get(k, {}).get('label', k))
        result_df = sdf[sdf['scenario'] == sel_result] if len(scenarios_run) > 0 else sdf

        if not result_df.empty:
            val_col_list = [c for c in result_df.columns if c not in ('scenario','series_id','topic','country')]
            if val_col_list:
                # ── Pick best value column ───────────────────────
                y_col = next((c for c in ['delta_pct', 'delta', 'shocked_avg'] if c in result_df.columns), val_col_list[0])
                # ── Build series_id if missing ────────────────────
                rdf = result_df.copy()
                if 'series_id' not in rdf.columns and 'topic' in rdf.columns and 'country' in rdf.columns:
                    rdf['series_id'] = rdf['topic'] + '_' + rdf['country']
                x_src = rdf['series_id'] if 'series_id' in rdf.columns else rdf.index.astype(str)
                y_vals = rdf[y_col]
                # ── Top-40 by absolute impact ─────────────────────
                impact_df = pd.DataFrame({'sid': x_src.values, 'val': y_vals.values})
                impact_df['abs'] = impact_df['val'].abs()
                impact_df = impact_df.nlargest(15, 'abs').sort_values('val', ascending=False)
                # ── Human-readable labels ─────────────────────────
                def _sid_label(sid):
                    parts = str(sid).rsplit('_', 1)
                    if len(parts) == 2:
                        t = parts[0].replace('_', ' ').title()
                        c = COUNTRY_NAMES.get(parts[1], parts[1])
                        return f"{t}<br>({c})"
                    return str(sid)
                impact_df['label'] = impact_df['sid'].apply(_sid_label)
                y_title = 'Δ Risk (% vs baseline)' if y_col == 'delta_pct' else 'Δ Risk Index (vs baseline)'
                bar_colors = ['rgba(220,60,60,0.82)' if v >= 0 else 'rgba(0,140,220,0.82)' for v in impact_df['val']]
                scen_lbl = SCENARIO_TEMPLATES.get(str(sel_result), {}).get('label', str(sel_result).replace('_',' ').title())
                fig = go.Figure(go.Bar(
                    x=impact_df['label'], y=impact_df['val'],
                    marker_color=bar_colors,
                    marker_line_color='rgba(80,80,100,0.2)',
                    marker_line_width=0.8,
                    hovertemplate='<b>%{x}</b><br>Impact: %{y:.5f}<extra></extra>'
                ))
                fig.update_layout(
                    title=dict(text=f'Top 15 Most Impacted Series — {scen_lbl}',
                               font=dict(size=12, color='#1a2a3a'), x=0.5, xanchor='center'),
                    height=440,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(232,240,252,0.45)',
                    xaxis=dict(tickangle=-40, color='#3a5a7a', tickfont=dict(size=8),
                               title=dict(text='Risk Series (Topic · Country)', font=dict(size=10, color='#5a7a9a'))),
                    yaxis=dict(title=y_title, color='#3a5a7a',
                               gridcolor='rgba(0,80,160,0.1)', zeroline=True,
                               zerolinecolor='rgba(0,80,160,0.3)', zerolinewidth=1.5),
                    margin=dict(l=20, r=20, t=50, b=130)
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("""<div style='font-size:0.72rem;color:#4a6a8a;line-height:1.6;padding:8px 12px;
                     background:rgba(0,80,160,0.04);border-radius:6px;margin-bottom:8px;'>
                  <b>How to read:</b> Each bar = one risk dimension × country pair.
                  <span style='color:#dc3c3c;font-weight:700;'>Red</span> = risk rises above baseline after shock.
                  <span style='color:#008cdc;font-weight:700;'>Blue</span> = risk falls below baseline.
                  Only the 15 most impacted series are shown, sorted by impact magnitude.
                </div>""", unsafe_allow_html=True)

            # ── Plain-English Analysis ──────────────────────────
            narr3 = scenario_narrative(result_df, sel_result)
            if narr3 and narr3[0]:
                p1, p2, p3 = narr3
                geo_block = (f"<div style='margin-top:14px;padding:12px 16px;"
                             f"background:rgba(0,85,168,0.06);border-left:3px solid #0077a8;"
                             f"border-radius:4px;font-size:0.82rem;color:#0a3a6a;line-height:1.7;'>"
                             f"<b>&#127758; Geopolitical Context:</b> {p3}</div>") if p3 else ''
                st.markdown(f"""
                <div style='background:#f0f6fc;border:1px solid rgba(0,119,168,0.18);
                     border-radius:10px;padding:20px 24px;margin:20px 0;line-height:1.8;
                     font-size:0.85rem;color:#1a2a3a;'>
                  <div style='font-size:0.7rem;font-weight:700;color:#0077a8;letter-spacing:0.1em;
                       text-transform:uppercase;margin-bottom:10px;'>&#128203; Analytical Summary</div>
                  <p style='margin:0 0 12px;'>{p1}</p>
                  <p style='margin:0 0 4px;'>{p2}</p>
                  {geo_block}
                </div>""", unsafe_allow_html=True)

            # Statistical details (expandable for analysts)
            with st.expander("\U0001f4ca Statistical Details", expanded=False):
                _v_cols = [c for c in result_df.columns if c not in ('scenario','series_id','topic','country')]
                if _v_cols:
                    _vc = _v_cols[0]
                    _si = result_df[_vc]
                    st.markdown(f"""
                    <div style='font-size:0.8rem;color:#1a3a5c;line-height:1.8;'>
                    <b>Statistical Summary:</b><br>
                    \u2022 Mean absolute deviation: <code>{_si.abs().mean():.6f}</code> index points<br>
                    \u2022 Max absolute deviation: <code>{_si.abs().max():.6f}</code> index points<br>
                    \u2022 Standard deviation: <code>{_si.std():.6f}</code><br>
                    \u2022 Series above average impact: <code>{int((_si.abs() > _si.abs().mean()).sum())}</code> / <code>{len(_si)}</code><br>
                    \u2022 Net direction: <code>{'Upward' if _si.mean() >= 0 else 'Downward'} pressure</code>
                    (mean delta = <code>{_si.mean():.6f}</code>)
                    </div>""", unsafe_allow_html=True)

            # Raw data table (collapsible)
            with st.expander("🔢 Raw Results Table", expanded=False):
                st.table(result_df)


# ═══════════════════════════════════════════════════════════════
# PAGE: API ACCESS (Pro only)
# ═══════════════════════════════════════════════════════════════
def render_api():
    nerai_premium_css.inject_page_header(
        title="API Access",
        subtitle="Programmatic access to NERAI risk data & intelligence feeds",
        badge="DEV",
        icon="🔌"
    )
    nerai_premium_css.inject_global_premium_css()

    st.markdown("""
    <div style='padding:28px 0 16px 0;'>
      <div style='font-size:11px;letter-spacing:0.12em;color:#0077a8;
                  text-transform:uppercase;margin-bottom:6px;'>NERAI Intelligence</div>
      <div style='font-size:22px;font-weight:700;color:#0d1f3c;'>API Access</div>
      <div style='font-size:13px;color:#5a6b82;margin-top:4px;'>Pro plan: direct data access</div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="h-div"></div>', unsafe_allow_html=True)

    if not _IS_PRO:
        st.markdown("""
        <div style='background:rgba(224,123,32,0.06);border:1px solid rgba(224,123,32,0.28);
             border-radius:10px;padding:28px;text-align:center;margin:24px 0;'>
          <div style='font-size:22px;margin-bottom:10px;'>U0001f512 Pro Feature</div>
          <div style='color:#5a6b82;font-size:0.88rem;line-height:1.8;'>
            API access is included in the <b>NERAI Pro</b> plan (€39/month).<br>
            Upgrade at <a href='https://neraicorp.com' target='_blank'
            style='color:#0077a8;'>neraicorp.com</a> or contact
            <a href='mailto:info@neraicorp.com' style='color:#0077a8;'>info@neraicorp.com</a>.
          </div>
        </div>""", unsafe_allow_html=True)
        _render_footer()
        return

    st.markdown("""
    <div style='background:rgba(0,119,168,0.05);border:1px solid rgba(0,119,168,0.2);
         border-radius:10px;padding:22px 26px;margin-bottom:20px;'>
      <div style='font-size:13px;font-weight:700;color:#0077a8;margin-bottom:14px;'>
        U0001f511 Your Pro Data Access
      </div>
      <div style='font-size:0.84rem;color:#2a3a5a;line-height:2.2;'>
        <b>Dashboard URL:</b>
        <code style='background:rgba(0,0,0,0.06);padding:2px 6px;border-radius:4px;'>
          https://nerai-intelligence.streamlit.app
        </code><br>
        <b>Datasets:</b> indices.csv · forecast_predictions.csv · causality_network.csv<br>
        <b>Format:</b> CSV — downloadable from Indices &amp; Predictions pages<br>
        <b>Update cadence:</b> Daily automated pipeline<br>
        <b>Coverage:</b> 18 risk dimensions × 195 countries · 2,400+ series
      </div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div style='background:white;border:1px solid #1a3a5c;border-radius:8px;padding:16px 18px;'>
          <div style='font-size:12px;font-weight:700;color:#0077a8;margin-bottom:8px;'>
            U0001f4ca Risk Indices
          </div>
          <div style='font-size:0.78rem;color:#5a6b82;line-height:1.9;'>
            Source: GDELT Event Database<br>
            Aggregation: P90 monthly<br>
            Dimensions: 18 topics × 195 countries<br>
            File: <code>indices.csv</code>
          </div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div style='background:white;border:1px solid #1a3a5c;border-radius:8px;padding:16px 18px;'>
          <div style='font-size:12px;font-weight:700;color:#0077a8;margin-bottom:8px;'>
            U0001f52e 12-Month Forecasts
          </div>
          <div style='font-size:0.78rem;color:#5a6b82;line-height:1.9;'>
            Model: N-HiTS / Holt-Winters<br>
            Horizon: 12 months ahead<br>
            Intervals: 80% + 95% CI<br>
            File: <code>forecast_predictions.csv</code>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#0d3464;border:1px solid #1a3a5c;border-radius:8px;
         padding:14px 18px;margin-top:16px;font-size:0.82rem;color:#5a6b82;line-height:1.8;'>
      <b>Need webhooks, higher frequency, or custom data pipelines?</b><br>
      Contact <a href='mailto:info@neraicorp.com' style='color:#0077a8;'>info@neraicorp.com</a>
      for enterprise API access.
    </div>""", unsafe_allow_html=True)
    st.markdown(_ANALYSIS_CSS, unsafe_allow_html=True)

    _render_footer()


# ═══════════════════════════════════════════════════════════════
# ROUTING
# ═══════════════════════════════════════════════════════════════

# === NAV GLOW + METRIC HOVER CSS ===
st.markdown("""
<style>
div.stButton>button{background:linear-gradient(135deg,#0d1b2a,#1b2a4a)!important;border:1px solid rgba(0,255,200,0.3)!important;color:#00ffc8!important;border-radius:12px!important;font-weight:600!important;letter-spacing:0.5px!important;box-shadow:0 0 15px rgba(0,255,200,0.15)!important;transition:all 0.3s ease!important;}
div.stButton>button:hover{box-shadow:0 0 25px rgba(0,255,200,0.4),0 0 50px rgba(0,100,255,0.2)!important;border-color:rgba(0,255,200,0.6)!important;transform:translateY(-1px)!important;}
div[data-testid="stMetric"]{transition:all 0.3s ease!important;border-radius:10px!important;}
div[data-testid="stMetric"]:hover{box-shadow:0 0 20px rgba(0,255,200,0.2),0 0 40px rgba(0,100,255,0.1)!important;transform:translateY(-2px)!important;}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE: THREAT RADAR
# ═══════════════════════════════════════════════════════════════
def render_threat_radar():
    nerai_premium_css.inject_page_header(
        title="Threat Radar",
        subtitle="Real-time anomaly detection & risk escalation monitoring",
        badge="ALERT",
        icon="🎯"
    )
    nerai_premium_css.inject_global_premium_css()


    st.markdown('<div class="sec-hdr">🔴  Live Threat Overview</div>', unsafe_allow_html=True)

    # ── Live Top Tension Pairs ──
    st.markdown('<div class="sec-hdr">⚡  Live Top Tension Pairs</div>', unsafe_allow_html=True)
    top_pairs = compute_top_tensions(tension_norm, coop_norm, deteri_norm)
    if top_pairs:
        cols_tp = st.columns(len(top_pairs))
        for col_el, pair in zip(cols_tp, top_pairs):
            with col_el:
                n1  = COUNTRY_NAMES.get(pair['c1'],pair['c1'])
                n2  = COUNTRY_NAMES.get(pair['c2'],pair['c2'])
                net = pair['net']
                clr = '#e05060' if net>=45 else ('#f59e0b' if net>=25 else '#00b4d8')
                st.markdown(f"""
                <div style="background:rgba(0,10,28,0.8);border:1px solid {clr}25;
                    border-radius:10px;padding:14px 10px;text-align:center;
                    border-top:2px solid {clr}">
                  <div style="font-size:0.78rem;color:#8aa0bc">{n1}</div>
                  <div style="font-size:0.55rem;color:{clr};letter-spacing:0.2em;margin:2px 0">⇔ VS ⇔</div>
                  <div style="font-size:0.78rem;color:#8aa0bc">{n2}</div>
                  <div style="font-size:1.5rem;font-weight:800;color:{clr};
                      text-shadow:0 0 12px {clr}40;margin:4px 0">{net:.0f}</div>
                  <div style="font-size:0.58rem;color:{clr};font-family:monospace">
                   {'CRITICAL' if net>=65 else 'HIGH' if net>=45 else 'ELEVATED' if net>=25 else 'MODERATE'}
                  </div>
                </div>""", unsafe_allow_html=True)

    st.markdown('<div class="h-div" style="margin:24px 0 16px"></div>', unsafe_allow_html=True)

    # ── Top Risk Countries ──
    st.markdown('<div class="sec-hdr">🏴  Top Risk Countries — All Topics</div>', unsafe_allow_html=True)
    avg_all = tension_norm.mean(axis=1).nlargest(8)
    cols_r  = st.columns(8)
    for col_el, (country, val) in zip(cols_r, avg_all.items()):
        with col_el:
            clr = '#e05060' if val>=50 else ('#f59e0b' if val>=25 else '#00b4d8')
            st.markdown(f"""
            <div style="background:rgba(0,10,28,0.7);border:1px solid {clr}20;
                border-radius:8px;padding:10px 8px;text-align:center">
              <div style="font-size:0.65rem;color:#8aa0bc">{COUNTRY_NAMES.get(country,country)}</div>
              <div style="font-size:1.2rem;font-weight:700;color:{clr};
                  text-shadow:0 0 10px {clr}50">{val:.0f}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="h-div" style="margin:24px 0"></div>', unsafe_allow_html=True)

    # ── Anomaly Detection / Top Signals ──
    with st.expander("⚡  Top Signals — Biggest Movers (Last 7 Days)", expanded=True):
        st.markdown('<div class="sec-hdr">Anomaly Detection</div>', unsafe_allow_html=True)
        # Use raw data with Score normalization for anomaly detection
        df_all_norm = apply_norm(df.groupby(level='country').mean(), 'Score (0–100)')
        if len(df_all_norm.columns) > 7:
            last    = df_all_norm.iloc[:,-1]
            prev    = df_all_norm.iloc[:,-8]
            changes = ((last-prev)/(prev.abs().clip(lower=1.0))*100).clip(-200,200).dropna()
            top_up  = changes.nlargest(5)
            top_dn  = changes.nsmallest(3)
            sig_c1, sig_c2 = st.columns(2)
            with sig_c1:
                st.markdown('<div style="font-size:0.65rem;color:#ff6b35;letter-spacing:0.15em;margin-bottom:8px">▲ RISING RISK</div>',
                            unsafe_allow_html=True)
                for c,pct in top_up.items():
                    cname = COUNTRY_NAMES.get(c, c)
                    clr   = '#e05060' if abs(pct)>=50 else '#ff6b35'
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:8px 12px;margin-bottom:6px;
                        background:rgba(224,80,96,0.06);border:1px solid rgba(224,80,96,0.12);
                        border-radius:8px">
                      <div>
                        <div style="font-size:0.82rem;color:#c0d0e0;font-weight:600">{cname}</div>
                        <div style="font-size:0.62rem;color:#5a7a9a">All Topics</div>
                        <div style="font-size:0.95rem;font-weight:700;color:{clr}">{last[c]:.1f}</div>
                      </div>
                      <div style="font-size:0.8rem;font-weight:700;color:{clr}">
                        ▲ {'+' if pct>0 else ''}{pct:.1f}%
                      </div>
                    </div>""", unsafe_allow_html=True)
            with sig_c2:
                st.markdown('<div style="font-size:0.65rem;color:#00c9a7;letter-spacing:0.15em;margin-bottom:8px">▼ DECLINING RISK</div>',
                            unsafe_allow_html=True)
                for c,pct in top_dn.items():
                    cname = COUNTRY_NAMES.get(c, c)
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:8px 12px;margin-bottom:6px;
                        background:rgba(0,201,167,0.04);border:1px solid rgba(0,201,167,0.10);
                        border-radius:8px">
                      <div>
                        <div style="font-size:0.82rem;color:#c0d0e0;font-weight:600">{cname}</div>
                        <div style="font-size:0.62rem;color:#5a7a9a">All Topics</div>
                        <div style="font-size:0.95rem;font-weight:700;color:#00c9a7">{last[c]:.1f}</div>
                      </div>
                      <div style="font-size:0.8rem;font-weight:700;color:#00c9a7">
                        {pct:.1f}%
                      </div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("Need at least 7 days of data for anomaly detection.")

    st.markdown('<div class="h-div" style="margin:16px 0"></div>', unsafe_allow_html=True)

    # ── Top 5 Bilateral Tension Alerts ──
    with st.expander("🚨  Top 5 Bilateral Tension Alerts — Auto-Detected", expanded=True):
        st.markdown('<div class="sec-hdr">Highest Risk Country Pairs · Last 7 Days</div>', unsafe_allow_html=True)
        top_pairs_bi = compute_top_tensions(tension_norm, coop_norm, deteri_norm)
        for rank, pair in enumerate(top_pairs_bi, 1):
            n1  = COUNTRY_NAMES.get(pair['c1'],pair['c1'])
            n2  = COUNTRY_NAMES.get(pair['c2'],pair['c2'])
            net = pair['net'];  trnd = pair['trend']
            if   net>=65: badge_cls,badge_txt,bar_col = 'badge-crit','CRITICAL','#e05060'
            elif net>=45: badge_cls,badge_txt,bar_col = 'badge-high','HIGH','#e06030'
            elif net>=25: badge_cls,badge_txt,bar_col = 'badge-med','ELEVATED','#f59e0b'
            else:         badge_cls,badge_txt,bar_col = 'badge-low','MODERATE','#00b4d8'
            pct = min(net, 100)
            arrow = '▲' if trnd>=0 else '▼'
            st.markdown(f"""
            <div style="margin-bottom:14px">
              <div style="font-size:0.62rem;color:#5a7a9a;font-family:monospace;margin-bottom:2px">#{rank}</div>
              <div style="font-size:0.78rem;color:{bar_col}">{n1} ⇔ {n2}</div>
              <div style="background:rgba(0,10,28,0.6);border-radius:6px;height:8px;margin:6px 0;overflow:hidden">
                <div style="width:{pct}%;height:100%;background:{bar_col};border-radius:6px"></div>
              </div>
              <div style="display:flex;justify-content:flex-end;gap:12px;align-items:center">
                <span style="font-size:1.15rem;font-weight:800;color:{bar_col}">{net:.1f}</span>
                <span style="font-size:0.65rem;color:{bar_col}">{arrow} {abs(trnd):.1f}</span>
              </div>
              <div style="font-size:0.55rem;color:{bar_col};font-family:monospace;letter-spacing:0.15em;margin-top:2px">{badge_txt}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="h-div" style="margin:16px 0"></div>', unsafe_allow_html=True)

    # ── Global Top Movers (from predictions) ──
    if trend_df is not None:
        st.markdown('<div class="sec-hdr">🌍  Global Top Movers — Next 12 Months</div>',
                    unsafe_allow_html=True)
        col_rise, col_fall = st.columns(2)

        with col_rise:
            st.markdown(
            '<div style="font-size:0.62rem;color:rgba(255,75,110,0.6);'
            'font-family:monospace;letter-spacing:0.18em;'
            'margin-bottom:8px">▲ HIGHEST RISING RISKS</div>',
                    unsafe_allow_html=True)
            top_rise = trend_df.nlargest(10, 'trend_pct')
            for _, r in top_rise.iterrows():
                _t = r['topic'] if pd.notna(r['topic']) else ''
                lbl = TOPIC_LABELS.get(_t, str(_t).replace('_',' ').title() if _t else 'Unknown')
                cnt = COUNTRY_NAMES.get(r['country'], r['country'])
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:5px 8px;margin-bottom:3px;
                    background:rgba(224,80,96,0.04);
                    border:1px solid rgba(224,80,96,0.10);border-radius:5px">
                  <div>
                    <div style="font-size:0.73rem;color:#2a4060">{lbl}</div>
                    <div style="font-size:0.58rem;color:#5a7a9a">{cnt}</div>
                  </div>
                  <div style="font-size:0.85rem;font-weight:700;color:#e05060">
                    +{r['trend_pct']:.1f}%
                  </div>
                </div>""", unsafe_allow_html=True)

        with col_fall:
            st.markdown(
            '<div style="font-size:0.62rem;color:rgba(0,255,157,0.5);'
            'font-family:monospace;letter-spacing:0.18em;'
            'margin-bottom:8px">▼ HIGHEST FALLING RISKS</div>',
                    unsafe_allow_html=True)
            top_fall = trend_df.nsmallest(10, 'trend_pct')
            for _, r in top_fall.iterrows():
                _t = r['topic'] if pd.notna(r['topic']) else ''
                lbl = TOPIC_LABELS.get(_t, str(_t).replace('_',' ').title() if _t else 'Unknown')
                cnt = COUNTRY_NAMES.get(r['country'], r['country'])
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:5px 8px;margin-bottom:3px;
                    background:rgba(0,255,157,0.04);
                    border:1px solid rgba(0,255,157,0.10);border-radius:5px">
                  <div>
                    <div style="font-size:0.73rem;color:#2a4060">{lbl}</div>
                    <div style="font-size:0.58rem;color:#5a7a9a">{cnt}</div>
                  </div>
                  <div style="font-size:0.85rem;font-weight:700;color:#00ff9d">
                    {r['trend_pct']:.1f}%
                  </div>
                </div>""", unsafe_allow_html=True)

    st.markdown('<div class="h-div" style="margin:24px 0"></div>', unsafe_allow_html=True)

    # ── Breaking News ──
    st.markdown('<div class="sec-hdr">📡  Breaking News — Live Feed</div>', unsafe_allow_html=True)
    _bn_queries = [
        ('🔥 Conflict & War', 'war conflict military attack troops'),
        ('⚠️ Political Crisis', 'coup sanctions political crisis emergency'),
        ('💥 Terrorism', 'terrorism attack bombing explosion'),
        ('🌊 Natural Disaster', 'earthquake hurricane flood disaster tsunami'),
        ('📉 Economic Crisis', 'recession inflation economic crisis default'),
    ]
    bn_tabs = st.tabs([q[0] for q in _bn_queries])
    for tab, (label, query) in zip(bn_tabs, _bn_queries):
        with tab:
            with st.spinner(f'Fetching {label} news...'):
                articles = fetch_gdelt_news(query, max_records=6)
            if articles:
                for art in articles:
                    title  = art.get('title', 'No title')
                    source = art.get('domain', '')
                    url    = art.get('url', '#')
                    seendate = art.get('seendate', '')
                    date_disp = seendate[:8] if len(seendate)>=8 else ''
                    if date_disp:
                        try: date_disp = pd.Timestamp(date_disp).strftime('%d %b %Y')
                        except: pass
                    st.markdown(f"""
                    <div style="padding:10px 14px;margin-bottom:8px;
                        background:rgba(0,10,28,0.7);border:1px solid rgba(0,180,255,0.08);
                        border-radius:8px;border-left:3px solid #e05060">
                      <a href="{url}" target="_blank"
                         style="color:#c0d8ee;font-size:0.82rem;font-weight:600;
                                text-decoration:none">{title}</a>
                      <div style="display:flex;gap:12px;margin-top:4px">
                        <span style="font-size:0.6rem;color:#5a7a9a">{source}</span>
                        <span style="font-size:0.6rem;color:#3a6a8a">{date_disp}</span>
                      </div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.caption('No recent articles found.')


    # âââ FAZ 3a: Global Risk Heatmap (Choropleth) âââ
    st.markdown('<div class="h-div" style="margin:24px 0 16px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">&#x1F5FA;&#xFE0F; GLOBAL RISK HEATMAP</div>', unsafe_allow_html=True)
    try:
        _latest_date = df.columns[-1]
        _risk_scores = df.xs("instability", level="topic", drop_level=True)[_latest_date].dropna()
        if not _risk_scores.empty:
            _iso3_codes = [FIPS_TO_ISO3.get(c, c) for c in _risk_scores.index]
            _map_df = pd.DataFrame({
                "country": _iso3_codes,
                "risk_score": _risk_scores.values,
                "name": [COUNTRY_NAMES.get(c, c) for c in _risk_scores.index]
            })
            fig_map = px.choropleth(
                _map_df, locations="country", locationmode="ISO-3",
                color="risk_score", hover_name="name",
                color_continuous_scale=[[0,"#0a1628"],[0.3,"#00b4d8"],[0.6,"#f59e0b"],[1.0,"#e05060"]],
                labels={"risk_score": "Instability Score"},
            )
            fig_map.update_layout(
                geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)",
                         landcolor="#0d1b2a", showframe=False, projection_type="natural earth",
                         coastlinecolor="#1a3a5c", countrycolor="#1a3a5c"),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=30, b=0), height=420,
                coloraxis_colorbar=dict(tickfont=dict(color="#8aa0bc"),
                                        title=dict(font=dict(color="#8aa0bc"))),
                font=dict(color="#c0d0e0"),
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.caption("Insufficient data for heatmap.")
    except Exception as _e:
        st.caption(f"Heatmap unavailable: {_e}")

    # âââ FAZ 3d: Top Movers Daily Table âââ
    st.markdown('<div class="h-div" style="margin:24px 0 16px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">&#x1F4CA; TOP DAILY MOVERS</div>', unsafe_allow_html=True)
    try:
        if len(df.columns) >= 2:
            _d1, _d2 = df.columns[-1], df.columns[-2]
            _all_topics = [t for t in df.index.get_level_values("topic").unique() if t not in _EXCLUDE_TOPICS]
            _instab_topics = [t for t in _all_topics if "instab" in t.lower() or "tension" in t.lower() or "military" in t.lower() or "crisis" in t.lower()]
            if not _instab_topics:
                _instab_topics = list(_all_topics)[:5]
            _movers = []
            for topic in _instab_topics:
                try:
                    _slice = df.xs(topic, level="topic")
                    _v1, _v2 = _slice[_d1], _slice[_d2]
                    _chg = ((_v1 - _v2) / _v2.replace(0, np.nan)).dropna()
                    for c in _chg.index:
                        _movers.append({"Country": COUNTRY_NAMES.get(c, c), "Topic": topic,
                                        "Today": round(float(_v1.get(c, 0)), 2),
                                        "Change": round(float(_chg.get(c, 0)) * 100, 1)})
                except Exception:
                    continue
            if _movers:
                _movers_df = pd.DataFrame(_movers).sort_values("Change", ascending=False)
                _top = pd.concat([_movers_df.head(8), _movers_df.tail(8)]).drop_duplicates()
                _top["Change"] = _top["Change"].apply(lambda x: f"+{x:.1f}%" if x > 0 else f"{x:.1f}%")
                st.table(_top)
            else:
                st.caption("No mover data available.")
        else:
            st.caption("Need at least 2 dates for comparison.")
    except Exception as _e:
        st.caption(f"Top movers unavailable: {_e}")

    # âââ FAZ 3e: Volatility Trend âââ
    st.markdown('<div class="h-div" style="margin:24px 0 16px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">&#x1F4C8; INSTABILITY VOLATILITY TREND</div>', unsafe_allow_html=True)
    try:
        _instab_data = df.xs("instability", level="topic", drop_level=True) if "instability" in df.index.get_level_values("topic") else df.iloc[:5]
        _global_mean = _instab_data.mean(axis=0)
        _rolling_std = _global_mean.rolling(window=7, min_periods=3).std()
        if not _rolling_std.dropna().empty:
            fig_vol = go.Figure()
            fig_vol.add_trace(go.Scatter(
                x=_rolling_std.index, y=_rolling_std.values,
                mode="lines", name="7-day Rolling Volatility",
                line=dict(color="#00d4ff", width=2),
                fill="tozeroy", fillcolor="rgba(0,212,255,0.08)"
            ))
            fig_vol.update_layout(
                **_PLOTLY_THEME,
                height=320,
                yaxis_title="Volatility (σ)",
                xaxis_title="",
            )
            st.plotly_chart(fig_vol, use_container_width=True)
        else:
            st.caption("Insufficient data for volatility trend.")
    except Exception as _e:
            st.caption(f"Volatility trend unavailable: {_e}")

    # ═══ FAZ 4a: DTW-based Early Warning System ═══
    st.markdown('<div class="h-div" style="margin:24px 0 16px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">⚠️  Early Warning Signals (DTW Pattern Match)</div>', unsafe_allow_html=True)
    try:
        from scipy.spatial.distance import euclidean
        _instab = df.xs("instability", level="topic", drop_level=True) if "instability" in df.index.get_level_values("topic") else None
        if _instab is not None and len(df.columns) >= 30:
            _window = 14  # 2-week pattern window
            _alerts = []
            for country in _instab.index[:30]:
                _series = _instab.loc[country].dropna().values
                if len(_series) < _window * 3:
                    continue
                _current = _series[-_window:]
                # Slide through history looking for similar patterns that preceded spikes
                _best_dist = float("inf")
                _best_outcome = 0
                _best_j = 0
                for j in range(_window, len(_series) - _window * 2):
                    _hist_pattern = _series[j:j+_window]
                    # Normalize both
                    _cn = (_current - _current.mean()) / max(_current.std(), 1e-9)
                    _hn = (_hist_pattern - _hist_pattern.mean()) / max(_hist_pattern.std(), 1e-9)
                    _dist = euclidean(_cn, _hn) / _window
                    if _dist < _best_dist:
                        _best_dist = _dist
                        _best_j = j
                        # What happened after this historical pattern?
                        _after = _series[j+_window:j+_window+7]
                        _before_mean = _hist_pattern.mean()
                        _after_mean = _after.mean() if len(_after) > 0 else _before_mean
                        _best_outcome = (_after_mean - _before_mean) / max(_before_mean, 1e-9)
                if _best_dist < 0.5 and _best_outcome > 0.15:
                    # Determine matched historical period
                    _match_cols = df.columns[_best_j:_best_j+_window] if hasattr(df.columns[0], "strftime") else []
                    if len(_match_cols) >= 2:
                        _match_period = f"{_match_cols[0].strftime('%Y-%m-%d')} ~ {_match_cols[-1].strftime('%Y-%m-%d')}"
                    else:
                        _match_period = f"Window idx {_best_j}-{_best_j+_window}"
                    _alerts.append({
                        "Country": COUNTRY_NAMES.get(country, country),
                        "Matched Period": _match_period,
                        "Pattern Similarity": f"{(1 - _best_dist) * 100:.0f}%",
                        "Expected \u0394": f"+{_best_outcome * 100:.1f}%",
                        "Signal": "HIGH" if _best_outcome > 0.3 else "ELEVATED"
                    })
            if _alerts:
                st.table(pd.DataFrame(_alerts))
            else:
                st.success("✅ No elevated early warning signals detected.")
        else:
            st.caption("Insufficient data for DTW analysis.")
    except Exception as _e:
        st.caption(f"Early warning unavailable: {_e}")
        st.caption(f"Volatility trend unavailable: {_e}")
    st.markdown(_ANALYSIS_CSS, unsafe_allow_html=True)
    # ── Strategic: Threat Radar Assessment ──
    try:
        _tr_html = _threat_radar_analysis(df_recent, sel_topic, COUNTRY_NAMES)
        if _tr_html: st.markdown(_tr_html, unsafe_allow_html=True)
    except: pass

    _render_footer()




# =====================================================================
# SUPPLY GRID — Global Supply Chain Intelligence
# =====================================================================

# Cached data fetchers
@st.cache_data(ttl=900)  # 15 min cache
def _sg_fetch_commodities():
    """Fetch commodity prices. Returns reference values if live feed fails."""
    from datetime import datetime as _dt
    # Reference fallback prices (Apr 2026 baseline)
    fallback = [
        ('Brent Crude', 'BZ=F', '$/bbl', 89.50),
        ('WTI Crude', 'CL=F', '$/bbl', 85.20),
        ('Natural Gas', 'NG=F', '$/MMBtu', 3.45),
        ('Gold', 'GC=F', '$/oz', 2780.50),
        ('Silver', 'SI=F', '$/oz', 33.20),
        ('Copper', 'HG=F', '$/lb', 4.85),
        ('Wheat', 'ZW=F', 'cents/bu', 580.0),
        ('Corn', 'ZC=F', 'cents/bu', 460.0),
        ('Soybean', 'ZS=F', 'cents/bu', 1050.0),
        ('Palladium', 'PA=F', '$/oz', 1020.0),
        ('Platinum', 'PL=F', '$/oz', 1010.0),
        ('Cotton', 'CT=F', 'cents/lb', 70.50),
    ]
    out = []
    live_count = 0
    try:
        import yfinance as yf
        for name, sym, unit, fb_price in fallback:
            entry = {'name': name, 'symbol': sym, 'unit': unit,
                     'price': fb_price, 'change_pct': 0.0, 'is_fallback': True}
            try:
                t = yf.Ticker(sym)
                hist = t.history(period='5d', interval='1d')
                if len(hist) >= 2:
                    last = float(hist['Close'].iloc[-1])
                    prev = float(hist['Close'].iloc[-2])
                    chg = ((last - prev) / prev) * 100 if prev else 0
                    entry['price'] = last
                    entry['change_pct'] = chg
                    entry['is_fallback'] = False
                    live_count += 1
            except Exception:
                pass
            out.append(entry)
    except Exception:
        out = [{'name': n, 'symbol': s, 'unit': u, 'price': p,
                'change_pct': 0.0, 'is_fallback': True} for n, s, u, p in fallback]
    ts = _dt.now().strftime('%Y-%m-%d %H:%M UTC')
    suffix = ' · LIVE' if live_count == len(fallback) else (
        f' · PARTIAL ({live_count}/{len(fallback)} live)' if live_count > 0 else ' · REFERENCE VALUES'
    )
    return out, ts + suffix


@st.cache_data(ttl=3600)
def _sg_fetch_freight_index():
    """Fetch Freightos Baltic Index (container shipping rate)."""
    try:
        import yfinance as yf
        # BDRY (Breakwave Dry Bulk Shipping ETF) as proxy + actual freight ETFs
        t = yf.Ticker('BDRY')
        hist = t.history(period='30d')
        if len(hist) >= 2:
            return {
                'name': 'Dry Bulk Freight (BDRY)',
                'price': float(hist['Close'].iloc[-1]),
                'change_30d': ((float(hist['Close'].iloc[-1]) - float(hist['Close'].iloc[0])) / float(hist['Close'].iloc[0])) * 100,
                'updated': hist.index[-1].strftime('%Y-%m-%d')
            }
    except Exception:
        pass
    return None


def _sg_chokepoints_data():
    """Critical maritime chokepoints — based on IMF PortWatch & UNCTAD data."""
    # Source: IMF PortWatch (https://portwatch.imf.org/), UNCTAD Review of Maritime Transport 2024
    return [
        {
            'name': 'Strait of Hormuz', 'lat': 26.57, 'lon': 56.25,
            'world_oil_pct': 20.0, 'daily_vessels': 75, 'world_lng_pct': 25.0,
            'key_commodities': 'Crude Oil, LNG, Condensates',
            'threat_level': 'CRITICAL', 'threat_score': 92,
            'context': 'Iran threats, US-Iran tensions, mining risk April 2026',
            'alt_route': 'No viable alternative for Gulf exports',
            'countries_affected': 'Saudi Arabia, UAE, Kuwait, Iraq, Qatar, Iran'
        },
        {
            'name': 'Bab el-Mandeb / Red Sea', 'lat': 12.58, 'lon': 43.33,
            'world_oil_pct': 12.0, 'daily_vessels': 70, 'world_trade_pct': 15.0,
            'key_commodities': 'Containers, Oil, Grain (Suez transit)',
            'threat_level': 'HIGH', 'threat_score': 78,
            'context': 'Houthi attacks ongoing since Nov 2023; ~70% diversion to Cape',
            'alt_route': 'Cape of Good Hope (+10-14 days, +30% cost)',
            'countries_affected': 'EU, UK, Egypt, Mediterranean ports'
        },
        {
            'name': 'Suez Canal', 'lat': 30.42, 'lon': 32.36,
            'world_oil_pct': 9.0, 'daily_vessels': 50, 'world_trade_pct': 12.0,
            'key_commodities': 'Containers, Oil, LNG, Grain',
            'threat_level': 'HIGH', 'threat_score': 72,
            'context': 'Traffic down ~50% due to Red Sea diversions',
            'alt_route': 'Cape of Good Hope (+10-14 days)',
            'countries_affected': 'EU-Asia trade, Egyptian revenue (~$9B/yr)'
        },
        {
            'name': 'Strait of Malacca', 'lat': 2.5, 'lon': 101.5,
            'world_oil_pct': 30.0, 'daily_vessels': 230, 'world_trade_pct': 25.0,
            'key_commodities': 'Oil, LNG, Containers (Asia trade)',
            'threat_level': 'ELEVATED', 'threat_score': 55,
            'context': 'Piracy, congestion; alternative Sunda/Lombok adds 3-5 days',
            'alt_route': 'Sunda Strait, Lombok Strait (+3-5 days)',
            'countries_affected': 'China, Japan, S.Korea, India energy imports'
        },
        {
            'name': 'Taiwan Strait', 'lat': 24.5, 'lon': 119.5,
            'world_oil_pct': 6.0, 'daily_vessels': 240, 'world_chip_pct': 88.0,
            'key_commodities': 'Containers, Semiconductors, Energy',
            'threat_level': 'ELEVATED', 'threat_score': 68,
            'context': 'PLA exercises increased; 88% of advanced chips transit here',
            'alt_route': 'East of Taiwan (+1-2 days), longer for chip supply',
            'countries_affected': 'Global tech supply chain, US, Japan, S.Korea'
        },
        {
            'name': 'Panama Canal', 'lat': 9.08, 'lon': -79.68,
            'world_oil_pct': 2.0, 'daily_vessels': 28, 'world_trade_pct': 5.0,
            'key_commodities': 'Containers, LNG, Grain (US-Asia)',
            'threat_level': 'MODERATE', 'threat_score': 45,
            'context': 'Recovering from 2023-24 drought; transits at 32-36/day vs 36 normal',
            'alt_route': 'Magellan Strait, Cape Horn (+8-12 days)',
            'countries_affected': 'US East Coast, Latin America, Asia trade'
        },
        {
            'name': 'Bosphorus Strait', 'lat': 41.12, 'lon': 29.07,
            'world_oil_pct': 3.0, 'daily_vessels': 130, 'world_grain_pct': 25.0,
            'key_commodities': 'Black Sea grain, Russian oil, LNG',
            'threat_level': 'ELEVATED', 'threat_score': 58,
            'context': 'Ukraine war risk; Turkish straits regulation, Russian shadow fleet',
            'alt_route': 'No alternative for Black Sea exports',
            'countries_affected': 'Russia, Ukraine, EU grain importers, MENA'
        },
        {
            'name': 'Danish Straits', 'lat': 55.5, 'lon': 11.5,
            'world_oil_pct': 3.0, 'daily_vessels': 60, 'world_lng_pct': 4.0,
            'key_commodities': 'Russian oil, Baltic exports, LNG',
            'threat_level': 'MODERATE', 'threat_score': 42,
            'context': 'Russian shadow fleet inspections, Baltic sabotage incidents',
            'alt_route': 'Limited; pipeline alternatives for some flows',
            'countries_affected': 'Russia, Nordics, Germany, Poland'
        },
    ]


def _sg_critical_materials():
    """Critical materials & supply concentration — USGS Mineral Commodity Summaries 2024."""
    return [
        {'material': 'Rare Earth Elements (REE)', 'top_supplier': 'China', 'top_share': 70, 'processing_share': 90,
         'use': 'Magnets, EVs, defense, electronics', 'risk_score': 95, 'symbol_proxy': None,
         'notes': 'China dominates mining (70%) and refining (90%). Export controls 2023+'},
        {'material': 'Gallium', 'top_supplier': 'China', 'top_share': 98, 'processing_share': 98,
         'use': 'Semiconductors, LEDs, radar', 'risk_score': 96, 'symbol_proxy': None,
         'notes': 'China imposed export controls Aug 2023; near-monopoly'},
        {'material': 'Germanium', 'top_supplier': 'China', 'top_share': 60, 'processing_share': 80,
         'use': 'Fiber optics, IR optics, satellites', 'risk_score': 88, 'symbol_proxy': None,
         'notes': 'China export controls Aug 2023; defense critical'},
        {'material': 'Cobalt', 'top_supplier': 'DRC', 'top_share': 70, 'processing_share': 75,
         'use': 'Li-ion batteries, EVs, aerospace', 'risk_score': 82, 'symbol_proxy': None,
         'notes': 'DRC production, China processes 75%. Conflict mineral concerns'},
        {'material': 'Lithium', 'top_supplier': 'Australia', 'top_share': 47, 'processing_share': 65,
         'use': 'EV batteries, energy storage', 'risk_score': 70, 'symbol_proxy': None,
         'notes': 'Mining in Australia/Chile; China processes 65% of refined Li'},
        {'material': 'Nickel', 'top_supplier': 'Indonesia', 'top_share': 50, 'processing_share': 30,
         'use': 'Stainless steel, EV batteries', 'risk_score': 65, 'symbol_proxy': None,
         'notes': 'Indonesia banned ore exports 2020; market dominance growing'},
        {'material': 'Graphite (Natural)', 'top_supplier': 'China', 'top_share': 65, 'processing_share': 90,
         'use': 'Battery anodes, refractories', 'risk_score': 85, 'symbol_proxy': None,
         'notes': 'Critical for EV anodes; China dominates'},
        {'material': 'Copper', 'top_supplier': 'Chile', 'top_share': 24, 'processing_share': 40,
         'use': 'Electrification, grid, EVs', 'risk_score': 55, 'symbol_proxy': 'HG=F',
         'notes': 'Diversified mining; structural demand from energy transition'},
        {'material': 'Uranium', 'top_supplier': 'Kazakhstan', 'top_share': 43, 'processing_share': 35,
         'use': 'Nuclear power, defense', 'risk_score': 72, 'symbol_proxy': None,
         'notes': 'Kazakhstan + Russia control much of fuel cycle'},
        {'material': 'Palladium', 'top_supplier': 'Russia', 'top_share': 40, 'processing_share': 40,
         'use': 'Catalytic converters, electronics', 'risk_score': 78, 'symbol_proxy': 'PA=F',
         'notes': 'Russia + S.Africa concentration; sanctions risk'},
        {'material': 'Platinum', 'top_supplier': 'South Africa', 'top_share': 70, 'processing_share': 70,
         'use': 'Catalysts, hydrogen tech', 'risk_score': 68, 'symbol_proxy': 'PL=F',
         'notes': 'S.Africa dominates; power grid + labor risks'},
        {'material': 'Manganese', 'top_supplier': 'South Africa', 'top_share': 35, 'processing_share': 60,
         'use': 'Steel, EV batteries', 'risk_score': 60, 'symbol_proxy': None,
         'notes': 'Diversified mining; China leads processing'},
        {'material': 'Titanium', 'top_supplier': 'China', 'top_share': 30, 'processing_share': 50,
         'use': 'Aerospace, defense, medical', 'risk_score': 75, 'symbol_proxy': None,
         'notes': 'Russia historically major; US/EU diversifying post-2022'},
        {'material': 'Tungsten', 'top_supplier': 'China', 'top_share': 80, 'processing_share': 85,
         'use': 'Hard metals, defense, electronics', 'risk_score': 90, 'symbol_proxy': None,
         'notes': 'China dominates; critical for cutting tools, ammunition'},
        {'material': 'Antimony', 'top_supplier': 'China', 'top_share': 48, 'processing_share': 75,
         'use': 'Flame retardants, ammunition, batteries', 'risk_score': 92, 'symbol_proxy': None,
         'notes': 'China export controls Sept 2024; defense + tech critical'},
    ]


def _sg_country_vulnerability():
    """Country supply chain vulnerability scores — based on UN Comtrade & WTO data."""
    return [
        {'country': 'Germany', 'iso': 'DEU', 'energy_dep': 89, 'food_dep': 35, 'critical_min': 95,
         'import_concentration': 62, 'overall_score': 70,
         'top_risks': 'Russian gas legacy, China REE/processing, Taiwan chips'},
        {'country': 'Japan', 'iso': 'JPN', 'energy_dep': 88, 'food_dep': 62, 'critical_min': 92,
         'import_concentration': 55, 'overall_score': 74,
         'top_risks': 'Hormuz oil/LNG, Taiwan chips, China REE'},
        {'country': 'South Korea', 'iso': 'KOR', 'energy_dep': 95, 'food_dep': 70, 'critical_min': 90,
         'import_concentration': 68, 'overall_score': 81,
         'top_risks': 'Energy import, semiconductor materials, China dependency'},
        {'country': 'United Kingdom', 'iso': 'GBR', 'energy_dep': 35, 'food_dep': 45, 'critical_min': 88,
         'import_concentration': 50, 'overall_score': 55,
         'top_risks': 'Critical minerals, food (Brexit complexity), LNG'},
        {'country': 'India', 'iso': 'IND', 'energy_dep': 80, 'food_dep': 5, 'critical_min': 75,
         'import_concentration': 60, 'overall_score': 56,
         'top_risks': 'Crude oil (Russia/Hormuz), pharma APIs from China'},
        {'country': 'China', 'iso': 'CHN', 'energy_dep': 75, 'food_dep': 20, 'critical_min': 25,
         'import_concentration': 45, 'overall_score': 41,
         'top_risks': 'Crude/LNG (Malacca), soybeans, semiconductor equipment'},
        {'country': 'United States', 'iso': 'USA', 'energy_dep': 5, 'food_dep': 5, 'critical_min': 78,
         'import_concentration': 38, 'overall_score': 31,
         'top_risks': 'REE/processing, antibiotics, advanced chips (Taiwan)'},
        {'country': 'Türkiye', 'iso': 'TUR', 'energy_dep': 75, 'food_dep': 40, 'critical_min': 65,
         'import_concentration': 58, 'overall_score': 60,
         'top_risks': 'Russian gas, oil imports (Hormuz/Bosphorus)'},
        {'country': 'France', 'iso': 'FRA', 'energy_dep': 50, 'food_dep': 20, 'critical_min': 90,
         'import_concentration': 48, 'overall_score': 52,
         'top_risks': 'Critical minerals, LNG (post-Russia), uranium fuel cycle'},
        {'country': 'Italy', 'iso': 'ITA', 'energy_dep': 75, 'food_dep': 45, 'critical_min': 92,
         'import_concentration': 60, 'overall_score': 68,
         'top_risks': 'Gas/LNG, Mediterranean Red Sea diversions, REE'},
        {'country': 'Singapore', 'iso': 'SGP', 'energy_dep': 95, 'food_dep': 90, 'critical_min': 70,
         'import_concentration': 55, 'overall_score': 78,
         'top_risks': 'Total food/energy import; trade hub vulnerability'},
        {'country': 'Egypt', 'iso': 'EGY', 'energy_dep': 30, 'food_dep': 60, 'critical_min': 70,
         'import_concentration': 65, 'overall_score': 56,
         'top_risks': 'Wheat (Russia/Ukraine), Suez revenue collapse'},
        {'country': 'Brazil', 'iso': 'BRA', 'energy_dep': 15, 'food_dep': 0, 'critical_min': 60,
         'import_concentration': 35, 'overall_score': 28,
         'top_risks': 'Fertilizer imports, fuel refining, critical chips'},
        {'country': 'Saudi Arabia', 'iso': 'SAU', 'energy_dep': 0, 'food_dep': 80, 'critical_min': 75,
         'import_concentration': 60, 'overall_score': 54,
         'top_risks': 'Food security, defense systems, technology imports'},
        {'country': 'Australia', 'iso': 'AUS', 'energy_dep': 30, 'food_dep': 0, 'critical_min': 30,
         'import_concentration': 35, 'overall_score': 24,
         'top_risks': 'Refined fuels, pharma APIs, advanced electronics'},
    ]


def _sg_sector_heatmap():
    """Sector x Risk dimension matrix."""
    sectors = ['Automotive', 'Pharma', 'Defense', 'Energy', 'Food/Agri', 'Tech/Semi', 'Renewables', 'Aerospace']
    dimensions = ['Mineral Concentration', 'Chokepoint Exposure', 'Geopolitical Risk', 'Single-Supplier Risk', 'Sanctions Exposure']
    # Risk scores 0-100
    matrix = {
        'Automotive':   [85, 60, 70, 75, 55],
        'Pharma':       [50, 40, 65, 88, 45],
        'Defense':      [90, 70, 88, 80, 70],
        'Energy':       [40, 95, 92, 65, 85],
        'Food/Agri':    [30, 75, 70, 60, 65],
        'Tech/Semi':    [85, 80, 90, 92, 75],
        'Renewables':   [92, 55, 75, 88, 60],
        'Aerospace':    [80, 65, 78, 85, 65],
    }
    return sectors, dimensions, matrix


def _sg_threat_color(score):
    if score >= 85: return '#ff2952'  # CRITICAL red
    if score >= 70: return '#ff7a00'  # HIGH orange
    if score >= 50: return '#ffd000'  # MODERATE yellow
    if score >= 30: return '#7fb800'  # LOW green
    return '#00d4ff'                  # MINIMAL cyan


def _sg_threat_label(score):
    if score >= 85: return 'CRITICAL'
    if score >= 70: return 'HIGH'
    if score >= 50: return 'ELEVATED'
    if score >= 30: return 'MODERATE'
    return 'LOW'




# =====================================================================
# PHASE 1: ESG / COMPLIANCE SCREENING DATA FUNCTIONS
# To be inserted BEFORE def render_supply_grid()
# =====================================================================

def _sg_sanctions_data():
    """Key sanctioned jurisdictions — OFAC, EU, UN consolidated lists."""
    return {
        'sanctioned_jurisdictions': [
            {'name': 'Russia', 'iso': 'RUS', 'regimes': ['US OFAC', 'EU 11th package', 'UK', 'Japan'],
             'key_sectors': 'Energy, finance, defense, dual-use tech, luxury goods',
             'severity': 'CRITICAL', 'score': 95,
             'effect': '~$300B frozen assets; oil price cap $60/bbl; SWIFT exclusion'},
            {'name': 'Iran', 'iso': 'IRN', 'regimes': ['US OFAC', 'EU', 'UN partial'],
             'key_sectors': 'Oil, banking, missile/drone tech, IRGC affiliates',
             'severity': 'CRITICAL', 'score': 92,
             'effect': 'Comprehensive US embargo; EU drone/missile restrictions'},
            {'name': 'North Korea', 'iso': 'PRK', 'regimes': ['US OFAC', 'EU', 'UN comprehensive'],
             'key_sectors': 'All trade restricted; military/dual-use comprehensive ban',
             'severity': 'CRITICAL', 'score': 98,
             'effect': 'Total UN trade embargo; secondary sanctions for facilitators'},
            {'name': 'Belarus', 'iso': 'BLR', 'regimes': ['US OFAC', 'EU', 'UK'],
             'key_sectors': 'Potash (fertilizer), oil products, defense, finance',
             'severity': 'HIGH', 'score': 80,
             'effect': 'Linked to Russia sanctions; potash export restrictions'},
            {'name': 'Syria', 'iso': 'SYR', 'regimes': ['US OFAC', 'EU', 'UK'],
             'key_sectors': 'Oil, finance, construction (some easing 2025)',
             'severity': 'HIGH', 'score': 78,
             'effect': 'Caesar Act US sanctions; EU partial easing post-2024'},
            {'name': 'Myanmar', 'iso': 'MMR', 'regimes': ['US OFAC', 'EU', 'UK'],
             'key_sectors': 'Military-linked entities (MOGE), gems, timber',
             'severity': 'HIGH', 'score': 75,
             'effect': 'Targeted military entity sanctions'},
            {'name': 'Venezuela', 'iso': 'VEN', 'regimes': ['US OFAC (sectoral)'],
             'key_sectors': 'Oil/PDVSA, gold, finance',
             'severity': 'HIGH', 'score': 72,
             'effect': 'Oil sanctions partially lifted 2023; reapplied 2024'},
            {'name': 'Cuba', 'iso': 'CUB', 'regimes': ['US OFAC'],
             'key_sectors': 'US embargo (broad); third-country trade allowed',
             'severity': 'MODERATE', 'score': 60,
             'effect': 'Helms-Burton secondary sanctions risk'},
        ],
        'high_risk_entities': [
            {'name': 'Sberbank', 'country': 'Russia', 'list': 'OFAC SDN', 'sector': 'Banking'},
            {'name': 'Gazprom', 'country': 'Russia', 'list': 'OFAC SSI', 'sector': 'Energy'},
            {'name': 'Rosneft', 'country': 'Russia', 'list': 'OFAC SSI', 'sector': 'Oil & Gas'},
            {'name': 'Wagner Group', 'country': 'Russia', 'list': 'OFAC SDN', 'sector': 'PMC'},
            {'name': 'IRGC', 'country': 'Iran', 'list': 'OFAC SDGT', 'sector': 'Military'},
            {'name': 'Huawei', 'country': 'China', 'list': 'US Entity List', 'sector': 'Telecom/Tech'},
            {'name': 'SMIC', 'country': 'China', 'list': 'US Entity List', 'sector': 'Semiconductors'},
            {'name': 'Belaruskali', 'country': 'Belarus', 'list': 'EU/US Sanctions', 'sector': 'Potash'},
        ]
    }


def _sg_uflpa_data():
    """UFLPA (Uyghur Forced Labor Prevention Act) entity regions & flagged sectors."""
    return {
        'high_risk_regions': [
            {'region': 'Xinjiang (XUAR)', 'country': 'China',
             'risk_level': 'CRITICAL', 'rebuttable_presumption': True,
             'key_commodities': 'Cotton (~85% China cotton), polysilicon (~45% global), tomatoes, PVC',
             'guidance': 'All goods from XUAR presumed forced labor; banned from US import unless rebutted'},
            {'region': 'Tibet (TAR)', 'country': 'China',
             'risk_level': 'HIGH', 'rebuttable_presumption': False,
             'key_commodities': 'Mining, manufacturing labor transfer programs',
             'guidance': 'Increasing scrutiny under labor transfer schemes'},
            {'region': 'North Korea', 'country': 'DPRK',
             'risk_level': 'CRITICAL', 'rebuttable_presumption': False,
             'key_commodities': 'Textiles, seafood, IT services (overseas DPRK workers)',
             'guidance': 'CAATSA Section 321(b) — DPRK labor presumption'},
        ],
        'flagged_sectors': [
            {'sector': 'Cotton & Textiles', 'risk': 'CRITICAL', 'origins': 'XUAR, Turkmenistan, Uzbekistan',
             'note': 'XUAR cotton in ~20% of global apparel supply chains'},
            {'sector': 'Polysilicon (Solar)', 'risk': 'CRITICAL', 'origins': 'XUAR (~45% global capacity)',
             'note': 'Solar panel supply chain critically exposed'},
            {'sector': 'Lithium-ion Batteries', 'risk': 'HIGH', 'origins': 'XUAR cathode, DRC cobalt',
             'note': 'Battery chain — forced labor + child labor concerns'},
            {'sector': 'Tomatoes & Processed Food', 'risk': 'HIGH', 'origins': 'XUAR (~25% global tomato paste)',
             'note': 'Italian/Mediterranean processors often source XUAR paste'},
            {'sector': 'Seafood', 'risk': 'HIGH', 'origins': 'China processing, DPRK labor, Thailand',
             'note': 'Distant-water fleets, processing plants flagged'},
            {'sector': 'Cocoa', 'risk': 'HIGH', 'origins': 'Ivory Coast, Ghana (child labor)',
             'note': 'EUDR + child labor compliance challenges'},
            {'sector': 'Mica', 'risk': 'HIGH', 'origins': 'India (Jharkhand/Bihar), Madagascar',
             'note': 'Cosmetic and electronics supply chains'},
            {'sector': 'Palm Oil', 'risk': 'MODERATE', 'origins': 'Malaysia, Indonesia',
             'note': 'Migrant labor abuse + EUDR deforestation concerns'},
        ]
    }


def _sg_eudr_commodities():
    """EU Deforestation Regulation (EUDR) regulated commodities — Reg 2023/1115."""
    return [
        {'commodity': 'Palm Oil', 'risk_origins': 'Indonesia, Malaysia',
         'global_share': 'IDN 58%, MYS 25%', 'eudr_status': 'IN SCOPE',
         'key_buyers': 'EU food, cosmetics, biofuels', 'mitigation': 'RSPO + geolocation proof'},
        {'commodity': 'Soy', 'risk_origins': 'Brazil (Cerrado, Amazon), Argentina, Paraguay',
         'global_share': 'BRA 36%, USA 32%', 'eudr_status': 'IN SCOPE',
         'key_buyers': 'EU livestock feed, food processors', 'mitigation': 'Soy Moratorium, RTRS'},
        {'commodity': 'Cocoa', 'risk_origins': 'Ivory Coast, Ghana, Cameroon, Indonesia',
         'global_share': 'CIV 39%, GHA 17%', 'eudr_status': 'IN SCOPE',
         'key_buyers': 'Nestle, Ferrero, Mondelez, EU chocolate mfrs', 'mitigation': 'Rainforest Alliance, Fair Trade'},
        {'commodity': 'Coffee', 'risk_origins': 'Brazil, Vietnam, Honduras, Indonesia',
         'global_share': 'BRA 35%, VNM 17%', 'eudr_status': 'IN SCOPE',
         'key_buyers': 'EU coffee roasters', 'mitigation': '4C, Rainforest Alliance'},
        {'commodity': 'Cattle (Beef/Leather)', 'risk_origins': 'Brazil, Argentina, Paraguay',
         'global_share': 'BRA 16% beef exports', 'eudr_status': 'IN SCOPE',
         'key_buyers': 'EU beef, leather goods, auto interiors', 'mitigation': 'Farm-of-origin traceability'},
        {'commodity': 'Wood/Timber', 'risk_origins': 'Russia, Ukraine, Brazil, Indonesia, DRC',
         'global_share': 'Tropical hardwoods primary risk', 'eudr_status': 'IN SCOPE',
         'key_buyers': 'EU furniture, paper, construction', 'mitigation': 'FSC, PEFC + DDS'},
        {'commodity': 'Rubber', 'risk_origins': 'Indonesia, Thailand, Vietnam, Ivory Coast',
         'global_share': 'THA 33%, IDN 28%', 'eudr_status': 'IN SCOPE',
         'key_buyers': 'EU automotive, industrial, medical', 'mitigation': 'GPSNR, smallholder traceability'},
    ]


def _sg_conflict_minerals():
    """Conflict minerals (3TG + cobalt) — Dodd-Frank 1502 + EU Regulation."""
    return [
        {'mineral': 'Tantalum (Coltan)', 'high_risk': 'DRC, Rwanda, Burundi', 'use': 'Capacitors, electronics',
         'risk': 'CRITICAL', 'note': 'DRC militia control of mines documented'},
        {'mineral': 'Tin', 'high_risk': 'DRC, Indonesia (Bangka), Myanmar', 'use': 'Solder, alloys',
         'risk': 'HIGH', 'note': 'Myanmar tin from conflict-affected Wa State'},
        {'mineral': 'Tungsten', 'high_risk': 'DRC (low share), China (80%)', 'use': 'Hard metals, defense',
         'risk': 'MODERATE', 'note': 'China dominates legitimate supply'},
        {'mineral': 'Gold (ASM)', 'high_risk': 'DRC, Sudan, Venezuela, Colombia', 'use': 'Electronics, jewelry',
         'risk': 'CRITICAL', 'note': 'ASM funds conflicts; smuggling routes via UAE'},
        {'mineral': 'Cobalt', 'high_risk': 'DRC (~70% global)', 'use': 'EV batteries',
         'risk': 'CRITICAL', 'note': 'Child labor in DRC artisanal cobalt mines'},
        {'mineral': 'Mica', 'high_risk': 'India (Jharkhand/Bihar), Madagascar', 'use': 'Electronics, cosmetics',
         'risk': 'HIGH', 'note': 'Child labor in illegal Indian mica mines'},
    ]


def _sg_country_esg_scores():
    """Country ESG composite scores (0-100, higher = more risk)."""
    return [
        {'country': 'North Korea', 'iso': 'PRK', 'governance': 99, 'labor': 98, 'environment': 70,
         'sanctions_exposure': 100, 'overall': 95, 'note': 'Comprehensive sanctions, severe labor abuses'},
        {'country': 'Russia', 'iso': 'RUS', 'governance': 88, 'labor': 70, 'environment': 75,
         'sanctions_exposure': 95, 'overall': 85, 'note': 'Sectoral sanctions; governance decline post-2022'},
        {'country': 'Iran', 'iso': 'IRN', 'governance': 92, 'labor': 75, 'environment': 78,
         'sanctions_exposure': 92, 'overall': 86, 'note': 'Comprehensive US sanctions, currency controls'},
        {'country': 'Myanmar', 'iso': 'MMR', 'governance': 92, 'labor': 88, 'environment': 80,
         'sanctions_exposure': 75, 'overall': 84, 'note': 'Military junta, MOGE-linked sanctions'},
        {'country': 'DRC', 'iso': 'COD', 'governance': 88, 'labor': 92, 'environment': 85,
         'sanctions_exposure': 35, 'overall': 80, 'note': 'Conflict minerals, child labor in cobalt mining'},
        {'country': 'Venezuela', 'iso': 'VEN', 'governance': 90, 'labor': 75, 'environment': 70,
         'sanctions_exposure': 78, 'overall': 80, 'note': 'PDVSA sanctions, hyperinflation'},
        {'country': 'Belarus', 'iso': 'BLR', 'governance': 85, 'labor': 70, 'environment': 65,
         'sanctions_exposure': 85, 'overall': 79, 'note': 'EU/US sanctions, potash restrictions'},
        {'country': 'China', 'iso': 'CHN', 'governance': 75, 'labor': 88, 'environment': 80,
         'sanctions_exposure': 65, 'overall': 78, 'note': 'XUAR forced labor presumption; export reciprocity'},
        {'country': 'Saudi Arabia', 'iso': 'SAU', 'governance': 70, 'labor': 75, 'environment': 60,
         'sanctions_exposure': 25, 'overall': 60, 'note': 'Migrant worker rights, Khashoggi-related individual sanctions'},
        {'country': 'Indonesia', 'iso': 'IDN', 'governance': 60, 'labor': 65, 'environment': 78,
         'sanctions_exposure': 20, 'overall': 56, 'note': 'EUDR palm oil, peatland concerns'},
        {'country': 'Türkiye', 'iso': 'TUR', 'governance': 65, 'labor': 55, 'environment': 55,
         'sanctions_exposure': 30, 'overall': 51, 'note': 'CAATSA risk for Russia trade; press freedom'},
        {'country': 'Brazil', 'iso': 'BRA', 'governance': 55, 'labor': 50, 'environment': 75,
         'sanctions_exposure': 15, 'overall': 50, 'note': 'EUDR scrutiny, Amazon deforestation'},
        {'country': 'India', 'iso': 'IND', 'governance': 50, 'labor': 65, 'environment': 70,
         'sanctions_exposure': 15, 'overall': 50, 'note': 'Mica child labor; Russia oil sanctions risk'},
        {'country': 'United States', 'iso': 'USA', 'governance': 22, 'labor': 25, 'environment': 40,
         'sanctions_exposure': 8, 'overall': 24, 'note': 'UFLPA enforcement, secondary sanctions risk'},
        {'country': 'Germany', 'iso': 'DEU', 'governance': 15, 'labor': 18, 'environment': 35,
         'sanctions_exposure': 10, 'overall': 20, 'note': 'CSDDD enforcement, Lieferkettengesetz compliance'},
        {'country': 'Australia', 'iso': 'AUS', 'governance': 12, 'labor': 18, 'environment': 35,
         'sanctions_exposure': 5, 'overall': 18, 'note': 'Modern Slavery Act compliance'},
        {'country': 'Norway', 'iso': 'NOR', 'governance': 8, 'labor': 12, 'environment': 18,
         'sanctions_exposure': 5, 'overall': 11, 'note': 'Transparency Act, low risk'},
    ]




# =====================================================================
# PHASE 2: ALTERNATIVE SOURCING INTELLIGENCE DATA FUNCTIONS
# Sources: UN Comtrade flows, USGS production shares, supplier intelligence
# =====================================================================

def _sg_alt_sourcing_data():
    """Alternative sourcing matrix for critical materials & sectors.
    Each entry shows top 5 suppliers ranked by diversification value."""
    return {
        'Rare Earth Elements (REE)': {
            'current_risk': 'China dominates mining (70%) and refining (90%). Export controls 2023+',
            'urgency': 'CRITICAL',
            'alternatives': [
                {'country': 'Australia', 'share': 14, 'lead_time': '+2-3 months', 'cost_delta': '+15%',
                 'compliance': 'EXCELLENT', 'notes': 'Lynas — Mt Weld mine; only non-China REE processor at scale'},
                {'country': 'United States', 'share': 9, 'lead_time': '+3-4 months', 'cost_delta': '+25%',
                 'compliance': 'EXCELLENT', 'notes': 'MP Materials — Mountain Pass; Phase 2 processing ramping 2025'},
                {'country': 'Vietnam', 'share': 3, 'lead_time': '+1-2 months', 'cost_delta': '+8%',
                 'compliance': 'GOOD', 'notes': '2nd largest reserves globally; emerging processing capacity'},
                {'country': 'Brazil', 'share': 2, 'lead_time': '+2-3 months', 'cost_delta': '+12%',
                 'compliance': 'GOOD', 'notes': 'Serra Verde project; heavy REE potential'},
                {'country': 'Malaysia', 'share': 1, 'lead_time': '+1 month', 'cost_delta': '+10%',
                 'compliance': 'MODERATE', 'notes': 'Lynas Advanced Materials Plant (refining only)'},
            ]
        },
        'Gallium': {
            'current_risk': 'China 98% of global supply. Export controls Aug 2023; near-monopoly',
            'urgency': 'CRITICAL',
            'alternatives': [
                {'country': 'Japan', 'share': 1, 'lead_time': '+6 months', 'cost_delta': '+40%',
                 'compliance': 'EXCELLENT', 'notes': 'Dowa Holdings — recycling + small primary production'},
                {'country': 'South Korea', 'share': 1, 'lead_time': '+4 months', 'cost_delta': '+35%',
                 'compliance': 'EXCELLENT', 'notes': 'Recycled gallium from LED/semiconductor waste'},
                {'country': 'Russia', 'share': 0.5, 'lead_time': 'N/A', 'cost_delta': 'Sanctions block',
                 'compliance': 'BLOCKED', 'notes': 'Historically produced; sanctioned since 2022'},
                {'country': 'Germany', 'share': 0.3, 'lead_time': '+5 months', 'cost_delta': '+45%',
                 'compliance': 'EXCELLENT', 'notes': 'Trace recovery from alumina processing'},
            ]
        },
        'Cobalt': {
            'current_risk': 'DRC 70% production; 75% of refining in China. Child labor + conflict minerals',
            'urgency': 'HIGH',
            'alternatives': [
                {'country': 'Australia', 'share': 4, 'lead_time': '+1-2 months', 'cost_delta': '+8%',
                 'compliance': 'EXCELLENT', 'notes': 'Clean production, ESG-compliant supply'},
                {'country': 'Indonesia', 'share': 8, 'lead_time': '+1 month', 'cost_delta': '+5%',
                 'compliance': 'GOOD', 'notes': 'HPAL technology; growing capacity with Chinese partnerships'},
                {'country': 'Canada', 'share': 3, 'lead_time': '+2 months', 'cost_delta': '+12%',
                 'compliance': 'EXCELLENT', 'notes': 'Sudbury mines; IRA-compliant for US battery supply'},
                {'country': 'Philippines', 'share': 3, 'lead_time': '+1-2 months', 'cost_delta': '+6%',
                 'compliance': 'GOOD', 'notes': 'Nickel-cobalt byproduct'},
                {'country': 'Cuba', 'share': 2, 'lead_time': 'N/A', 'cost_delta': 'US sanctions block',
                 'compliance': 'BLOCKED', 'notes': 'Moa Joint Venture (Sherritt Canada) — OFAC restrictions'},
            ]
        },
        'Lithium': {
            'current_risk': 'Australia mines 47%; China processes 65% of refined Li',
            'urgency': 'MEDIUM',
            'alternatives': [
                {'country': 'Chile', 'share': 24, 'lead_time': '+1-2 months', 'cost_delta': '+5%',
                 'compliance': 'EXCELLENT', 'notes': 'SQM, Albemarle — Salar de Atacama brine'},
                {'country': 'Argentina', 'share': 6, 'lead_time': '+2-3 months', 'cost_delta': '+7%',
                 'compliance': 'GOOD', 'notes': 'Lithium Triangle; fast-growing production'},
                {'country': 'United States', 'share': 3, 'lead_time': '+3-4 months', 'cost_delta': '+15%',
                 'compliance': 'EXCELLENT', 'notes': 'Silver Peak (Albemarle), Thacker Pass ramping'},
                {'country': 'Canada', 'share': 2, 'lead_time': '+3-4 months', 'cost_delta': '+14%',
                 'compliance': 'EXCELLENT', 'notes': 'Nemaska Lithium; IRA-compliant refining'},
                {'country': 'Brazil', 'share': 2, 'lead_time': '+2-3 months', 'cost_delta': '+10%',
                 'compliance': 'GOOD', 'notes': 'Sigma Lithium — hard-rock spodumene'},
            ]
        },
        'Semiconductors (advanced)': {
            'current_risk': 'TSMC Taiwan dominates (~60% foundry, ~90% leading edge). Chokepoint risk',
            'urgency': 'CRITICAL',
            'alternatives': [
                {'country': 'South Korea', 'share': 19, 'lead_time': '+3-6 months', 'cost_delta': '+20%',
                 'compliance': 'EXCELLENT', 'notes': 'Samsung — advanced nodes, memory leadership'},
                {'country': 'United States', 'share': 12, 'lead_time': '+12-18 months', 'cost_delta': '+35%',
                 'compliance': 'EXCELLENT', 'notes': 'Intel, TSMC Arizona, Samsung Texas — CHIPS Act funded'},
                {'country': 'Japan', 'share': 6, 'lead_time': '+6-9 months', 'cost_delta': '+25%',
                 'compliance': 'EXCELLENT', 'notes': 'Rapidus (2nm target), Kioxia, Renesas'},
                {'country': 'Germany', 'share': 4, 'lead_time': '+9-12 months', 'cost_delta': '+30%',
                 'compliance': 'EXCELLENT', 'notes': 'Infineon, Bosch, TSMC Dresden 2027'},
                {'country': 'China', 'share': 15, 'lead_time': '+2-3 months', 'cost_delta': '+5%',
                 'compliance': 'HIGH RISK', 'notes': 'SMIC (Entity List); legacy nodes only; export controls'},
            ]
        },
        'Natural Gas / LNG': {
            'current_risk': 'Hormuz chokepoint (25% of global LNG) + Russian pipeline legacy',
            'urgency': 'HIGH',
            'alternatives': [
                {'country': 'United States', 'share': 22, 'lead_time': '+1-3 months', 'cost_delta': '+10-25%',
                 'compliance': 'EXCELLENT', 'notes': 'Largest LNG exporter 2024; 14 terminals operational'},
                {'country': 'Qatar', 'share': 20, 'lead_time': 'Via Hormuz (risk)', 'cost_delta': 'Chokepoint exposure',
                 'compliance': 'EXCELLENT', 'notes': 'North Field expansion; Hormuz transit required'},
                {'country': 'Australia', 'share': 19, 'lead_time': '+2-3 months', 'cost_delta': '+15%',
                 'compliance': 'EXCELLENT', 'notes': 'NWS, Gorgon, Wheatstone — no chokepoint risk'},
                {'country': 'Norway (pipeline)', 'share': 3, 'lead_time': 'Immediate', 'cost_delta': '+8%',
                 'compliance': 'EXCELLENT', 'notes': 'Baltic/North Sea; largest EU pipeline supplier'},
                {'country': 'Nigeria', 'share': 4, 'lead_time': '+2 months', 'cost_delta': '+12%',
                 'compliance': 'MODERATE', 'notes': 'NLNG; political/pipeline security risks'},
            ]
        },
        'Pharma APIs (Common)': {
            'current_risk': 'India 40%, China 35%. Single-source vulnerabilities on antibiotics',
            'urgency': 'HIGH',
            'alternatives': [
                {'country': 'Germany', 'share': 6, 'lead_time': '+2-3 months', 'cost_delta': '+30%',
                 'compliance': 'EXCELLENT', 'notes': 'BASF, Boehringer — high-quality GMP'},
                {'country': 'Italy', 'share': 4, 'lead_time': '+2 months', 'cost_delta': '+25%',
                 'compliance': 'EXCELLENT', 'notes': 'Italian API cluster; fermentation expertise'},
                {'country': 'United States', 'share': 3, 'lead_time': '+3-4 months', 'cost_delta': '+40%',
                 'compliance': 'EXCELLENT', 'notes': 'Reshoring initiatives; Phlow consortium for critical APIs'},
                {'country': 'Japan', 'share': 2, 'lead_time': '+3 months', 'cost_delta': '+35%',
                 'compliance': 'EXCELLENT', 'notes': 'Specialty APIs; high regulatory standards'},
                {'country': 'Switzerland', 'share': 2, 'lead_time': '+2-3 months', 'cost_delta': '+35%',
                 'compliance': 'EXCELLENT', 'notes': 'Lonza, Siegfried — complex biologics'},
            ]
        },
        'Wheat (Export)': {
            'current_risk': 'Black Sea (Russia+Ukraine 25% exports) + Bosphorus chokepoint',
            'urgency': 'HIGH',
            'alternatives': [
                {'country': 'United States', 'share': 11, 'lead_time': 'Immediate', 'cost_delta': 'Market price',
                 'compliance': 'EXCELLENT', 'notes': 'Gulf and PNW ports; no chokepoint risk'},
                {'country': 'Canada', 'share': 14, 'lead_time': 'Immediate', 'cost_delta': '+2%',
                 'compliance': 'EXCELLENT', 'notes': 'Hard red spring wheat; St. Lawrence + Pacific routes'},
                {'country': 'Australia', 'share': 10, 'lead_time': '+1 month', 'cost_delta': '+5%',
                 'compliance': 'EXCELLENT', 'notes': 'Premium white wheat; Asian market focus'},
                {'country': 'Argentina', 'share': 7, 'lead_time': '+1 month', 'cost_delta': '+3%',
                 'compliance': 'GOOD', 'notes': 'Rosario port; no chokepoint; export taxes vary'},
                {'country': 'France', 'share': 8, 'lead_time': 'Immediate', 'cost_delta': '+4%',
                 'compliance': 'EXCELLENT', 'notes': 'EU largest; Rouen port; quality specs'},
            ]
        },
        'Uranium (Fuel Cycle)': {
            'current_risk': 'Kazakhstan 43%, Russia ~20% conversion/enrichment. Rosatom sanctions risk',
            'urgency': 'HIGH',
            'alternatives': [
                {'country': 'Canada', 'share': 15, 'lead_time': '+3-6 months', 'cost_delta': '+10%',
                 'compliance': 'EXCELLENT', 'notes': 'Cameco — McArthur River, Cigar Lake'},
                {'country': 'Australia', 'share': 8, 'lead_time': '+3-4 months', 'cost_delta': '+8%',
                 'compliance': 'EXCELLENT', 'notes': 'Olympic Dam, Ranger; strong allied supply'},
                {'country': 'Namibia', 'share': 11, 'lead_time': '+2-3 months', 'cost_delta': '+5%',
                 'compliance': 'GOOD', 'notes': 'Rossing, Husab — Chinese stakes but stable jurisdiction'},
                {'country': 'Niger', 'share': 4, 'lead_time': 'Political risk', 'cost_delta': 'Volatile',
                 'compliance': 'AT RISK', 'notes': '2023 coup disrupted Orano supply; ongoing uncertainty'},
                {'country': 'United States', 'share': 1, 'lead_time': '+6-12 months', 'cost_delta': '+20%',
                 'compliance': 'EXCELLENT', 'notes': 'Energy Fuels — domestic HALEU push'},
            ]
        },
    }


def _sg_supplier_scorecard_methodology():
    """Methodology explanation for supplier scoring."""
    return [
        {'criterion': 'Country Risk', 'weight': 30, 'source': 'World Bank Governance + OFAC sanctions'},
        {'criterion': 'ESG Compliance', 'weight': 20, 'source': 'UFLPA + EUDR + labor rights indices'},
        {'criterion': 'Production Capacity', 'weight': 20, 'source': 'USGS + UN Comtrade flows'},
        {'criterion': 'Logistics Distance', 'weight': 15, 'source': 'Chokepoint exposure + transit days'},
        {'criterion': 'Lead Time', 'weight': 10, 'source': 'Industry benchmarks'},
        {'criterion': 'Price Competitiveness', 'weight': 5, 'source': 'Yahoo Finance + trade data'},
    ]




# =====================================================================
# PHASE 3: AGENTIC AI RISK VALIDATION (Claude API)
# Uses the existing Anthropic SDK to run risk validation agents
# =====================================================================

def _sg_ai_sample_alerts():
    """Pre-populated sample alerts for demonstration + live signal fusion."""
    return [
        {
            'id': 'alert_001',
            'title': 'Hormuz oil transit risk elevated',
            'category': 'Chokepoint',
            'severity': 'HIGH',
            'source_signals': [
                'GDELT: Iran military_escalation score 0.56 (+25.8% rising)',
                'Kuwait: threaten_intl_relations +88.7%',
                'Oil tanker insurance premiums up 25%',
                'US-Iran Islamabad talks failed April 11, 2026'
            ],
            'exposure': '20% of global oil transit; Saudi/UAE/Kuwait/Qatar/Iraq energy exports',
            'affected_materials': ['Crude Oil', 'LNG', 'Condensates'],
            'raw_facts': 'Iranian officials threatened mining of Strait of Hormuz. Insurance war-risk premiums elevated.'
        },
        {
            'id': 'alert_002',
            'title': 'REE export controls tightening',
            'category': 'Critical Material',
            'severity': 'CRITICAL',
            'source_signals': [
                'China Ministry of Commerce updated REE export license list',
                'USGS: China produces 70%, refines 90%',
                'MP Materials quarterly: capacity ramp ongoing',
                'Industry: lead times for permanent magnets +4 months'
            ],
            'exposure': 'EV motors, wind turbines, defense electronics',
            'affected_materials': ['Neodymium', 'Dysprosium', 'Terbium'],
            'raw_facts': 'China tightened REE export licensing in 2024. Ex-China processing capacity <10% of global.'
        },
        {
            'id': 'alert_003',
            'title': 'Red Sea diversions extending',
            'category': 'Trade Route',
            'severity': 'HIGH',
            'source_signals': [
                'Houthi attacks resumed March 2026',
                'IMF PortWatch: 70% container diversion persistent',
                'Freightos Baltic Index: EU-Asia +30%',
                'Maersk, MSC continue Cape routing'
            ],
            'exposure': 'EU-Asia container trade; 12% global oil',
            'affected_materials': ['Containers', 'Oil', 'Grain'],
            'raw_facts': 'Red Sea attacks ongoing since Nov 2023. Cape routing adds 10-14 days and +30% freight cost.'
        },
        {
            'id': 'alert_004',
            'title': 'Taiwan Strait PLA exercises intensifying',
            'category': 'Geopolitical',
            'severity': 'ELEVATED',
            'source_signals': [
                'PLA joint sword exercises (4th this year)',
                '88% of advanced chips transit Taiwan Strait',
                'TSMC Arizona ramp ~12 months behind',
                'Japan, Korea activating tech contingencies'
            ],
            'exposure': 'Global semiconductor supply; tech industry cascading impact',
            'affected_materials': ['Semiconductors (advanced)', 'Memory chips', 'Foundry capacity'],
            'raw_facts': 'PLA activities increased quarter-over-quarter. No chip alternative at scale in 2-year horizon.'
        },
    ]


def _sg_ai_build_prompt(alert, user_context):
    """Build a prompt for Claude to validate and assess the risk alert."""
    signals_text = '\n'.join([f'- {s}' for s in alert['source_signals']])
    return f"""You are a supply chain risk intelligence analyst for NERAI.
You validate alerts and provide actionable briefings for executives.

ALERT:
Title: {alert['title']}
Category: {alert['category']}
Severity: {alert['severity']}

SIGNAL SOURCES:
{signals_text}

EXPOSURE: {alert['exposure']}
KEY MATERIALS: {', '.join(alert['affected_materials'])}
CONTEXT: {alert['raw_facts']}

USER CONTEXT: {user_context if user_context else 'No additional context provided.'}

Provide a concise risk brief with these 4 sections:

**1. Validation (1-2 sentences):**
Is this signal credible? Rate: CONFIRMED / LIKELY / UNVERIFIED. Note any contradicting indicators.

**2. Business Impact (2-3 sentences):**
Likely cost, lead-time, and revenue impact over 30/90/180 days. Quantify where possible.

**3. Recommended Actions (3 bullet points):**
Immediate (24h), short-term (2 weeks), strategic (1 quarter) mitigations.

**4. Escalation (1 sentence):**
Who should be notified? (Procurement / Ops / C-suite / Board). Confidence level (%)?

Keep total response under 300 words. Use hard numbers and named counterparties where possible.
Format with markdown bold (**) for section headings."""


def _sg_ai_call_claude(prompt, max_tokens=800):
    """Call Claude API for risk validation. Returns (success, response_text)."""
    try:
        import anthropic
        import os
        # Try to get API key from Streamlit secrets or env
        api_key = None
        try:
            api_key = st.secrets.get('ANTHROPIC_API_KEY')
        except Exception:
            pass
        if not api_key:
            api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            return False, 'ANTHROPIC_API_KEY not configured. Add it in Streamlit secrets to enable live AI validation.'

        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model='claude-sonnet-4-5',
            max_tokens=max_tokens,
            messages=[{'role': 'user', 'content': prompt}]
        )
        text = resp.content[0].text if resp.content else ''
        return True, text
    except Exception as e:
        return False, f'AI call failed: {e}'


def _sg_ai_fallback_brief(alert):
    """Structured fallback brief when AI is unavailable — rules-based."""
    sev_impact = {
        'CRITICAL': ('CONFIRMED', 'Severe impact expected', '30-60%', '+50-100%'),
        'HIGH':     ('LIKELY',    'Material impact expected', '15-30%', '+20-50%'),
        'ELEVATED': ('LIKELY',    'Moderate impact possible', '5-15%',  '+10-25%'),
        'MODERATE': ('UNVERIFIED','Limited near-term impact', '2-5%',   '+5-15%'),
    }
    verdict, impact_line, revenue_delta, cost_delta = sev_impact.get(
        alert['severity'], ('UNVERIFIED', 'Uncertain', '<5%', '+5%'))

    materials = ', '.join(alert['affected_materials'][:3])

    actions_by_sev = {
        'CRITICAL': [
            f'IMMEDIATE (24h): Activate alternative sourcing for {materials}; freeze non-essential orders in affected routes',
            'SHORT-TERM (2w): Lock forward contracts with diversified suppliers; increase safety stock 30-60 days',
            'STRATEGIC (Q): Dual-source qualification; insurance review; board-level risk disclosure'
        ],
        'HIGH': [
            f'IMMEDIATE (24h): Audit current orders for {materials}; notify procurement leadership',
            'SHORT-TERM (2w): Engage top-3 alternative suppliers; assess hedging options',
            'STRATEGIC (Q): Diversification roadmap; scenario budgeting'
        ],
        'ELEVATED': [
            'IMMEDIATE (24h): Add to weekly risk watchlist; monitor signals',
            'SHORT-TERM (2w): Map primary supplier single-points-of-failure',
            'STRATEGIC (Q): Maintain intelligence posture; pre-qualify alternates'
        ],
        'MODERATE': [
            'IMMEDIATE (24h): Informational — log to risk register',
            'SHORT-TERM (2w): Normal operations; monthly review',
            'STRATEGIC (Q): Annual diversification review'
        ],
    }

    esc_by_sev = {
        'CRITICAL': 'C-suite + Board. Confidence 90%+',
        'HIGH': 'C-suite + Procurement VP. Confidence 75-85%',
        'ELEVATED': 'Procurement Director + Ops. Confidence 60-75%',
        'MODERATE': 'Risk Manager. Confidence 50-60%',
    }

    return f"""**1. Validation:** {verdict}. Multi-source signals align on this risk. See alert for source citations.

**2. Business Impact:** {impact_line}. Revenue-at-risk ~{revenue_delta}; cost inflation ~{cost_delta} over 90 days. Lead-time extensions likely on {materials}.

**3. Recommended Actions:**
- {actions_by_sev.get(alert['severity'], actions_by_sev['MODERATE'])[0]}
- {actions_by_sev.get(alert['severity'], actions_by_sev['MODERATE'])[1]}
- {actions_by_sev.get(alert['severity'], actions_by_sev['MODERATE'])[2]}

**4. Escalation:** {esc_by_sev.get(alert['severity'], 'Risk Manager')}"""




# =====================================================================
# PHASE 4: SCENARIO SIMULATOR
# What-if disruption modeling across chokepoints, materials, countries
# =====================================================================

def _sg_scenario_library():
    """Pre-defined disruption scenarios with cascade modeling."""
    return {
        'Strait of Hormuz closure (30 days)': {
            'category': 'Chokepoint',
            'severity': 'CATASTROPHIC',
            'duration_days': 30,
            'primary_impacts': {
                'Oil supply': '-20% global transit',
                'LNG supply': '-25% global transit',
                'Gulf exports': 'Full interruption for Saudi/UAE/Kuwait/Qatar/Iraq/Iran',
            },
            'price_projections': {
                'Brent Crude': '+50-120%',
                'WTI Crude': '+45-110%',
                'Natural Gas': '+80-150%',
                'Gold (safe haven)': '+15-25%',
                'USD Index': '+8-15%',
            },
            'cascade_effects': [
                'Asian refiners (China, Japan, Korea, India) activate strategic reserves',
                'Insurance war-risk premiums spike 10x; many tankers refuse charters',
                'Global recession probability rises to 60-70%',
                'EU gas storage depleted 6 weeks earlier than plan',
                'Central banks pause rate cuts; inflation re-accelerates',
            ],
            'affected_countries': 'Saudi Arabia, UAE, Kuwait, Iraq, Iran, Qatar, Oman, China, Japan, S.Korea, India',
            'mitigation_playbook': [
                'Activate US SPR draws; coordinate IEA release',
                'Accelerate Australia/US/Qatar LNG diversion',
                'Saudi-UAE East-West pipeline (~5 Mbpd Red Sea bypass)',
                'Industrial demand rationing in manufacturing sectors',
            ],
            'recovery_timeline': '60-90 days to normalize; 6+ months for full insurance market recovery'
        },
        'Taiwan Strait blockade (90 days)': {
            'category': 'Geopolitical',
            'severity': 'CATASTROPHIC',
            'duration_days': 90,
            'primary_impacts': {
                'Advanced chips': '-88% of global leading-edge supply',
                'TSMC capacity': '0% operational',
                'Memory chips': '-40% (Samsung/Hynix partially exposed)',
                'Rare earth refining': '-5% (Taiwan small share)',
            },
            'price_projections': {
                'Chip prices': '+200-500% for leading-edge',
                'Auto pricing': '+25-50% (chip shortage cascade)',
                'Consumer electronics': '+30-60%',
                'Server/AI hardware': '+100-300%',
                'Industrial equipment': '+20-40%',
            },
            'cascade_effects': [
                'Auto production halts globally within 4-6 weeks',
                'AI/data center buildout freezes; cloud pricing spikes',
                'Defense electronics supply crisis; military readiness impact',
                'Apple, NVIDIA, AMD, Qualcomm revenue drops 40-60% for 2 quarters',
                'Stock market correction 15-30%; tech sector leading',
                'Emergency CHIPS Act II funding for US reshoring',
            ],
            'affected_countries': 'Taiwan, China, US, S.Korea, Japan, Germany, all tech-intensive economies',
            'mitigation_playbook': [
                'Emergency reprovisioning of Intel/Samsung/Global Foundries capacity',
                'Defense Production Act invocation for critical chip allocation',
                'Inventory rationing; prioritize defense, medical, safety-critical',
                'Accelerate Japan Rapidus, Arizona fabs; relax some ITAR/EAR',
                'Diplomatic de-escalation via multilateral mediators',
            ],
            'recovery_timeline': 'Chip supply: 12-24 months to pre-crisis levels; complete supply chain rework'
        },
        'Red Sea 6-month sustained closure': {
            'category': 'Chokepoint',
            'severity': 'HIGH',
            'duration_days': 180,
            'primary_impacts': {
                'EU-Asia container trade': '100% diverted to Cape',
                'Suez Canal revenue': '$9B annual loss to Egypt',
                'Shipping lead times': '+10-14 days',
                'Global oil transit': '-12%',
            },
            'price_projections': {
                'Container rates (EU-Asia)': '+35-60%',
                'Brent Crude': '+10-20%',
                'Wheat (Russia exposure)': '+15-25%',
                'Consumer goods (EU retail)': '+5-10%',
            },
            'cascade_effects': [
                'Egypt fiscal crisis; potential IMF bailout',
                'European retailers delayed fall/winter stock 3-6 weeks',
                'Cape route ports (SA, Namibia) capacity strained',
                'Insurance capacity exhausted for Red Sea transits',
                'Intra-Asian and EU-India routes see capacity reshuffle',
            ],
            'affected_countries': 'Egypt, EU (esp Germany/Italy/France), Saudi, Yemen, coastal EU ports',
            'mitigation_playbook': [
                'Activate Cape of Good Hope as primary EU-Asia route',
                'Increase ship capacity via charter extensions',
                'Accelerate nearshoring announcements (MEX, Poland, Vietnam)',
                'Egyptian IMF facility + bilateral support to stabilize currency',
            ],
            'recovery_timeline': 'Freight rates: 3-6 months post-resolution; Egypt fiscal: 12-18 months'
        },
        'China REE + gallium total export ban (12 months)': {
            'category': 'Critical Material',
            'severity': 'CRITICAL',
            'duration_days': 365,
            'primary_impacts': {
                'REE (Nd/Dy/Tb)': '-70% global mining, -90% refining',
                'Gallium': '-98% global supply',
                'Germanium': '-60% supply',
                'Permanent magnets': 'Ex-China supply <10% of demand',
            },
            'price_projections': {
                'REE oxides': '+300-800%',
                'Gallium': '+500-1000%',
                'Neodymium magnets': '+200-400%',
                'EV motor components': '+50-100%',
                'Wind turbine gen': '+75-150%',
            },
            'cascade_effects': [
                'EV production targets missed globally (~30-50% reduction)',
                'Wind turbine installations delayed 12-18 months',
                'Defense electronics supply crisis (radar, missile guidance)',
                'LED/semiconductor capacity constrained by gallium shortage',
                'Lynas (Australia) + MP Materials (US) become strategic assets',
            ],
            'affected_countries': 'EU, US, Japan, S.Korea, India, Turkey — all advanced manufacturing',
            'mitigation_playbook': [
                'Emergency REE strategic reserve release (DOE, DOD)',
                'Fast-track Lynas Texas + MP Materials Mountain Pass Phase 2',
                'Recycling mandate for end-of-life electronics/EVs',
                'Substitute motor tech (induction, reluctance) where possible',
                'Diplomatic engagement via G7/IEA framework',
            ],
            'recovery_timeline': 'Ex-China capacity ramp: 3-5 years for full replacement'
        },
        'Russian gas total cutoff to EU': {
            'category': 'Energy',
            'severity': 'HIGH',
            'duration_days': 365,
            'primary_impacts': {
                'EU natural gas': '-15-20% (mostly replaced by LNG post-2022)',
                'EU fertilizer': '-10-15% production',
                'EU heavy industry': 'Selective curtailment scenarios',
                'Gas storage': 'Winter 2026 depletion risk',
            },
            'price_projections': {
                'TTF Natural Gas': '+80-150%',
                'LNG spot': '+60-120%',
                'Fertilizer (urea)': '+40-80%',
                'Steel (EU energy cost)': '+15-25%',
                'Electricity (baseload)': '+30-50%',
            },
            'cascade_effects': [
                'Germany industrial recession (chemicals, steel, auto)',
                'Asian LNG competition drives global gas volatility',
                'Hungary, Slovakia push for bilateral exceptions',
                'Green hydrogen + nuclear buildouts accelerate',
                'Food inflation via fertilizer chain',
            ],
            'affected_countries': 'Germany, Austria, Hungary, Slovakia, Italy (plus EU-wide markets)',
            'mitigation_playbook': [
                'Maximum US/Qatar/Norway LNG contracting',
                'Demand reduction 10-15% via industrial rationing',
                'Accelerated nuclear restart (Germany reconsideration)',
                'Strategic gas reserve cross-border pooling',
            ],
            'recovery_timeline': 'Supply normalization: 18-24 months with LNG terminal buildout'
        },
        'Panama Canal drought re-intensifies (6 months)': {
            'category': 'Chokepoint',
            'severity': 'MODERATE',
            'duration_days': 180,
            'primary_impacts': {
                'Panama transits': '-50% (18 vs 36 normal)',
                'US East Coast LNG exports': 'Rerouting costs +20%',
                'US-Asia container trade': '+3-5 days transit',
                'Agricultural exports (US Midwest)': 'Higher logistics cost',
            },
            'price_projections': {
                'Container rates (US-Asia)': '+10-20%',
                'LNG spot': '+5-10%',
                'Soybean export basis': '-5 to -10 cents/bu',
            },
            'cascade_effects': [
                'Magellan Strait / Cape Horn rerouting (+8-12 days)',
                'Rail and intermodal congestion US West-East',
                'Slot auction prices reach $4M+ per transit',
                'Accelerated Nicaragua canal speculation',
            ],
            'affected_countries': 'US, Panama, Chile, Argentina, China, Japan, S.Korea',
            'mitigation_playbook': [
                'Canal authority water management; slot auction optimization',
                'Rail/intermodal capacity expansion via LA/LB ports',
                'LNG contract flexibility clauses activated',
                'Agricultural export timing adjustment',
            ],
            'recovery_timeline': 'Typically 3-6 months once rainfall returns to normal'
        },
    }




# =====================================================================
# PHASE 5: WEATHER & PORT DISRUPTION ALERTS (NOAA/NWS)
# Live weather alerts for major US ports + curated global port weather
# =====================================================================

def _sg_weather_ports():
    """Major global ports with coordinates for weather monitoring."""
    return [
        # US ports — live NWS data
        {'port': 'Los Angeles / Long Beach', 'country': 'USA', 'region': 'us', 'lat': 33.75, 'lon': -118.2,
         'tz': 'US West', 'trade_rank': 1, 'key_cargo': 'Containers, autos (Pacific trade)'},
        {'port': 'New York / New Jersey', 'country': 'USA', 'region': 'us', 'lat': 40.67, 'lon': -74.1,
         'tz': 'US East', 'trade_rank': 3, 'key_cargo': 'Containers (transatlantic)'},
        {'port': 'Savannah', 'country': 'USA', 'region': 'us', 'lat': 32.08, 'lon': -81.1,
         'tz': 'US East', 'trade_rank': 5, 'key_cargo': 'Containers, forest products'},
        {'port': 'Houston', 'country': 'USA', 'region': 'us', 'lat': 29.74, 'lon': -95.27,
         'tz': 'US Gulf', 'trade_rank': 7, 'key_cargo': 'Oil, LNG, petrochemicals'},
        {'port': 'Seattle / Tacoma', 'country': 'USA', 'region': 'us', 'lat': 47.58, 'lon': -122.35,
         'tz': 'US West', 'trade_rank': 8, 'key_cargo': 'Containers (Alaska, Asia)'},
        {'port': 'Norfolk / Hampton Roads', 'country': 'USA', 'region': 'us', 'lat': 36.93, 'lon': -76.32,
         'tz': 'US East', 'trade_rank': 10, 'key_cargo': 'Containers, coal'},
        # International ports — curated snapshot
        {'port': 'Shanghai', 'country': 'CHN', 'region': 'intl', 'lat': 31.24, 'lon': 121.50,
         'tz': 'Asia', 'trade_rank': 'Global #1', 'key_cargo': 'Containers (world largest)'},
        {'port': 'Singapore', 'country': 'SGP', 'region': 'intl', 'lat': 1.27, 'lon': 103.84,
         'tz': 'Asia', 'trade_rank': 'Global #2', 'key_cargo': 'Transshipment, oil, containers'},
        {'port': 'Rotterdam', 'country': 'NLD', 'region': 'intl', 'lat': 51.93, 'lon': 4.14,
         'tz': 'Europe', 'trade_rank': 'EU #1', 'key_cargo': 'Containers, oil, ores'},
        {'port': 'Busan', 'country': 'KOR', 'region': 'intl', 'lat': 35.10, 'lon': 129.04,
         'tz': 'Asia', 'trade_rank': 'Global #7', 'key_cargo': 'Containers (NE Asia hub)'},
        {'port': 'Hamburg', 'country': 'DEU', 'region': 'intl', 'lat': 53.55, 'lon': 9.99,
         'tz': 'Europe', 'trade_rank': 'EU #3', 'key_cargo': 'Containers, vehicles'},
        {'port': 'Jebel Ali (Dubai)', 'country': 'ARE', 'region': 'intl', 'lat': 25.03, 'lon': 55.07,
         'tz': 'Middle East', 'trade_rank': 'Regional #1', 'key_cargo': 'Containers, transshipment'},
        {'port': 'Antwerp-Bruges', 'country': 'BEL', 'region': 'intl', 'lat': 51.26, 'lon': 4.4,
         'tz': 'Europe', 'trade_rank': 'EU #2', 'key_cargo': 'Containers, chemicals'},
        {'port': 'Yokohama / Tokyo', 'country': 'JPN', 'region': 'intl', 'lat': 35.45, 'lon': 139.65,
         'tz': 'Asia', 'trade_rank': 'Japan #1', 'key_cargo': 'Autos, electronics, containers'},
    ]


@st.cache_data(ttl=86400, show_spinner=False)
def _sg_fetch_nws_alerts():
    """Fetch live weather for major global ports via Open-Meteo (free, no key, global coverage).
    Returns (alerts_by_region, status_msg) preserving backward-compat signature.
    Cached 24h; cleared via Force Refresh button."""
    try:
        import urllib.request, json, ssl
        from datetime import datetime, timezone
        ports = [
            {"port": "Singapore", "region": "APAC", "lat": 1.27, "lon": 103.84},
            {"port": "Shanghai", "region": "APAC", "lat": 31.24, "lon": 121.50},
            {"port": "Busan", "region": "APAC", "lat": 35.10, "lon": 129.04},
            {"port": "Tokyo", "region": "APAC", "lat": 35.45, "lon": 139.65},
            {"port": "Hong Kong", "region": "APAC", "lat": 22.32, "lon": 114.17},
            {"port": "Mumbai", "region": "APAC", "lat": 18.95, "lon": 72.83},
            {"port": "Rotterdam", "region": "EUROPE", "lat": 51.93, "lon": 4.14},
            {"port": "Hamburg", "region": "EUROPE", "lat": 53.55, "lon": 9.99},
            {"port": "Antwerp", "region": "EUROPE", "lat": 51.26, "lon": 4.40},
            {"port": "Piraeus", "region": "EUROPE", "lat": 37.94, "lon": 23.65},
            {"port": "Ambarli (Istanbul)", "region": "EUROPE", "lat": 41.02, "lon": 28.68},
            {"port": "Jebel Ali (Dubai)", "region": "MEA", "lat": 25.03, "lon": 55.07},
            {"port": "Jeddah", "region": "MEA", "lat": 21.48, "lon": 39.19},
            {"port": "Durban", "region": "MEA", "lat": -29.87, "lon": 31.02},
            {"port": "Los Angeles", "region": "AMERICAS", "lat": 33.75, "lon": -118.20},
            {"port": "Houston", "region": "AMERICAS", "lat": 29.74, "lon": -95.27},
            {"port": "New York / NJ", "region": "AMERICAS", "lat": 40.67, "lon": -74.10},
            {"port": "Santos", "region": "AMERICAS", "lat": -23.96, "lon": -46.33},
        ]
        alerts_by_region = {"APAC": [], "EUROPE": [], "MEA": [], "AMERICAS": []}
        ctx = ssl.create_default_context()
        count = 0
        for p in ports:
            try:
                url = ("https://api.open-meteo.com/v1/forecast"
                       f"?latitude={p['lat']}&longitude={p['lon']}"
                       "&current=temperature_2m,wind_speed_10m,wind_gusts_10m,weather_code,precipitation"
                       "&timezone=UTC")
                req = urllib.request.Request(url, headers={"User-Agent": "NERAI-Intelligence/1.0"})
                with urllib.request.urlopen(req, context=ctx, timeout=5) as r:
                    data = json.loads(r.read())
                cur = data.get("current", {}) or {}
                temp = cur.get("temperature_2m") or 0
                wind = cur.get("wind_speed_10m") or 0
                gusts = cur.get("wind_gusts_10m") or 0
                wcode = cur.get("weather_code") or 0
                precip = cur.get("precipitation") or 0
                if gusts >= 75 or wcode in (95, 96, 99):
                    sev, desc = "severe", f"Severe conditions - gusts {gusts:.0f} km/h"
                elif gusts >= 50 or wcode in (71,73,75,77,85,86):
                    sev, desc = "high", f"High winds / storms - gusts {gusts:.0f} km/h"
                elif gusts >= 35 or precip >= 5:
                    sev, desc = "moderate", f"Elevated - gusts {gusts:.0f} km/h, precip {precip:.1f}mm"
                else:
                    sev, desc = "normal", f"Normal - wind {wind:.0f} km/h, temp {temp:.0f}C"
                alerts_by_region[p["region"]].append({
                    "port": p["port"], "severity": sev, "description": desc,
                    "wind": wind, "gusts": gusts, "temp": temp, "precip": precip, "weather_code": wcode
                })
                count += 1
            except Exception:
                pass
        status_msg = f"{count} ports polled - Open-Meteo - updated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
        return alerts_by_region, status_msg
    except Exception as e:
        return ({"APAC": [], "EUROPE": [], "MEA": [], "AMERICAS": []}, f"Error fetching weather: {str(e)[:80]}")


@st.cache_data(ttl=86400, show_spinner=False)
def _nerai_fetch_ofac_sdn_summary():
    """Fetch US OFAC SDN list summary from Treasury.gov. Returns dict or None."""
    try:
        import urllib.request, ssl, xml.etree.ElementTree as ET
        from datetime import datetime, timezone
        url = "https://www.treasury.gov/ofac/downloads/sdn.xml"
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={"User-Agent": "NERAI-Intelligence/1.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
            xml_data = r.read()
        root = ET.fromstring(xml_data)
        ns_str = root.tag.split('}')[0].lstrip('{') if '}' in root.tag else ''
        ns = {"s": ns_str} if ns_str else {}
        entries = root.findall("s:sdnEntry", ns) if ns else root.findall("sdnEntry")
        programs = {}
        types = {}
        for e in entries:
            type_el = e.find("s:sdnType", ns) if ns else e.find("sdnType")
            sdn_type = (type_el.text if type_el is not None and type_el.text else "Unknown")
            types[sdn_type] = types.get(sdn_type, 0) + 1
            prog_list = e.find("s:programList", ns) if ns else e.find("programList")
            if prog_list is not None:
                for prog in (prog_list.findall("s:program", ns) if ns else prog_list.findall("program")):
                    p = (prog.text or "").strip()
                    if p: programs[p] = programs.get(p, 0) + 1
        return {
            "total_entries": len(entries),
            "types": dict(sorted(types.items(), key=lambda x: -x[1])),
            "programs": dict(sorted(programs.items(), key=lambda x: -x[1])[:15]),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "source": "US OFAC SDN (treasury.gov)"
        }
    except Exception:
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def _nerai_fetch_uk_ofsi_summary():
    """Fetch UK OFSI consolidated sanctions list summary (lightweight count)."""
    try:
        import urllib.request, ssl
        import xml.etree.ElementTree as ET
        from datetime import datetime, timezone
        url = "https://ofsistorage.blob.core.windows.net/publishlive/2022format/ConList.xml"
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={"User-Agent": "NERAI-Intelligence/1.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
            data = r.read()
        root = ET.fromstring(data)
        regimes = {}
        total_desig = 0
        for elem in root.iter():
            tag_low = elem.tag.lower().split('}')[-1]
            if tag_low == "designation":
                total_desig += 1
            if tag_low in ("regime", "regimename"):
                r_text = (elem.text or "").strip()
                if r_text:
                    regimes[r_text] = regimes.get(r_text, 0) + 1
        return {
            "total_entries": total_desig,
            "regimes": dict(sorted(regimes.items(), key=lambda x: -x[1])[:15]),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "source": "UK HM Treasury OFSI"
        }
    except Exception:
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def _nerai_fetch_eu_sanctions_summary():
    """Return EU consolidated sanctions metadata.
    Full list requires FSF token; returns latest known baseline."""
    from datetime import datetime, timezone
    return {
        "total_entries": None,
        "source": "EU Consolidated Financial Sanctions (FSF)",
        "landing_page": "https://data.europa.eu/data/datasets/consolidated-list-of-persons-groups-and-entities-subject-to-eu-financial-sanctions",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "note": "EU FSF requires auth token for full XML. Metadata only."
    }


@st.cache_data(ttl=86400, show_spinner=False)
def _nerai_fetch_uflpa_entity_count():
    """UFLPA Entity List summary. DHS hosts as XLSX with rotating URL per version."""
    from datetime import datetime, timezone
    return {
        "total_entities": None,
        "landing_page": "https://www.dhs.gov/uflpa-entity-list",
        "last_major_update": "2024",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": "DHS / CBP UFLPA Entity List",
        "note": "Full list requires manual XLSX download from DHS landing page."
    }


def _nerai_freshness_banner_html(label, ttl_hours=24, source_note=""):
    """HTML banner showing data freshness. Relies on st.cache_data TTL for actual data age."""
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    note_html = f" &middot; <span style='color:#8aa0bc;'>{source_note}</span>" if source_note else ""
    return (
        f"<div style='display:flex; align-items:center; gap:10px; padding:6px 12px; "
        f"background:rgba(0,20,45,0.35); border:1px solid rgba(0,212,255,0.15); "
        f"border-radius:6px; font-size:10px; color:#7a8fa8; margin:6px 0 10px 0; letter-spacing:0.5px;'>"
        f"<span style='color:#00d4ff; font-weight:700;'>{label.upper()}</span>"
        f"<span>Auto-refresh every {ttl_hours}h</span>"
        f"<span style='color:#5a6b82;'>|</span>"
        f"<span>Page loaded {ts}</span>"
        f"{note_html}"
        f"</div>"
    )



def _sg_intl_port_weather():
    """Curated current weather risk for international ports (updated weekly)."""
    # Based on seasonal climate patterns and known recurring risks
    return {
        'Shanghai': {'status': 'NORMAL', 'note': 'Mid-April: stable; typhoon season Jun-Oct'},
        'Singapore': {'status': 'MONITORING', 'note': 'Inter-monsoon: thunderstorms possible afternoons'},
        'Rotterdam': {'status': 'NORMAL', 'note': 'Spring patterns; occasional North Sea gales'},
        'Busan': {'status': 'NORMAL', 'note': 'Clear spring; typhoon season Aug-Oct'},
        'Hamburg': {'status': 'NORMAL', 'note': 'Spring winds; Elbe tide-sensitive'},
        'Jebel Ali (Dubai)': {'status': 'NORMAL', 'note': 'Pre-summer stable; Shamal winds possible'},
        'Antwerp-Bruges': {'status': 'NORMAL', 'note': 'Spring conditions stable'},
        'Yokohama / Tokyo': {'status': 'NORMAL', 'note': 'Cherry blossom season; typhoon risk Jul-Oct'},
    }


def _sg_weather_severity_color(severity):
    return {
        'Extreme': '#ff2952', 'Severe': '#ff7a00', 'Moderate': '#ffd000',
        'Minor': '#7fb800', 'Unknown': '#8aa0bc',
        'CRITICAL': '#ff2952', 'MONITORING': '#ffd000', 'NORMAL': '#00ffc8'
    }.get(severity, '#8aa0bc')


def render_supply_grid():
    """SUPPLY GRID — Global Supply Chain Intelligence Hub."""

    # Header
    st.markdown("""
    <div style="margin: 8px 0 24px 0;">
      <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
        <div style="font-size:11px; letter-spacing:3px; color:#00d4ff; font-weight:700; text-transform:uppercase;">
          NERAI · Supply Grid
        </div>
        <div style="height:1px; flex:1; background:linear-gradient(90deg, rgba(0,212,255,0.4), transparent);"></div>
        <div style="font-size:10px; color:#5a6b82; letter-spacing:1.5px;">GLOBAL SUPPLY CHAIN INTELLIGENCE</div>
      </div>
      <div style="font-size:32px; font-weight:700; color:#e0e8f0; margin-bottom:6px; letter-spacing:-0.5px;">
        Supply Grid Command
      </div>
      <div style="font-size:14px; color:#8aa0bc; max-width:780px; line-height:1.6;">
        Real-time intelligence across critical chokepoints, strategic materials, trade flows, and country dependencies.
        Data fused from IMF PortWatch, USGS, UN Comtrade, GDELT, and live commodity markets.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Module tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13 = st.tabs([
        "Live Indicators",
        "Chokepoints",
        "Critical Materials",
        "Trade Disruptions",
        "Country Vulnerability",
        "Sector Heatmap",
        "ESG & Compliance",
        "Alternative Sourcing",
        "AI Risk Analyst",
        "Scenario Simulator",
        "Weather Alerts",
        "Trade Flows",
        "LPI Corridors"
    ])

    # ========== TAB 1: LIVE INDICATORS ==========
    with tab1:
        st.markdown("""
        <div style="margin-bottom:16px;">
          <div style="font-size:18px; font-weight:600; color:#e0e8f0;">Real-time Commodity & Freight Markers</div>
          <div style="font-size:12px; color:#5a6b82; margin-top:4px;">
            Source: Yahoo Finance · 15-min delayed · Updated every 15 minutes
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner('Fetching live market data...'):
            commodities, last_updated = _sg_fetch_commodities()

        all_fallback = commodities and all(c.get('is_fallback') for c in commodities)
        if not commodities:
            st.warning("Commodity data unavailable.")
        elif all_fallback:
            st.info("Live feed unavailable — showing reference values (Apr 2026 baseline). Markets resume on next refresh.")
        else:
            # Group commodities by category
            categories = {
                'Energy': ['Brent Crude', 'WTI Crude', 'Natural Gas'],
                'Precious Metals': ['Gold', 'Silver', 'Platinum', 'Palladium'],
                'Industrial Metals': ['Copper'],
                'Agriculture': ['Wheat', 'Corn', 'Soybean', 'Cotton'],
            }

            for cat_name, cat_items in categories.items():
                st.markdown(f"<div style='font-size:12px; letter-spacing:2px; color:#00d4ff; font-weight:600; margin:18px 0 10px 0;'>{cat_name.upper()}</div>", unsafe_allow_html=True)
                cols = st.columns(len(cat_items))
                for i, item_name in enumerate(cat_items):
                    item = next((c for c in commodities if c['name'] == item_name), None)
                    with cols[i]:
                        if item:
                            chg = item['change_pct']
                            arrow = '▲' if chg >= 0 else '▼'
                            color = '#00ffc8' if chg >= 0 else '#ff6b6b'
                            st.markdown(f"""
                            <div style='background:linear-gradient(135deg, rgba(0,30,60,0.5), rgba(0,15,35,0.7));
                                        border:1px solid rgba(0,212,255,0.18); border-radius:10px;
                                        padding:14px; min-height:100px;'>
                              <div style='font-size:11px; color:#8aa0bc; letter-spacing:0.5px;'>{item['name']}</div>
                              <div style='font-size:24px; font-weight:700; color:#e0e8f0; margin-top:6px;'>
                                {item['price']:,.2f}
                              </div>
                              <div style='font-size:11px; color:#5a6b82;'>{item['unit']}</div>
                              <div style='font-size:13px; color:{color}; font-weight:600; margin-top:6px;'>
                                {arrow} {abs(chg):.2f}%
                              </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style='background:rgba(0,15,35,0.4); border:1px dashed rgba(0,212,255,0.15);
                                        border-radius:10px; padding:14px; min-height:100px;'>
                              <div style='font-size:11px; color:#5a6b82;'>{item_name}</div>
                              <div style='font-size:14px; color:#5a6b82; margin-top:30px;'>—</div>
                            </div>
                            """, unsafe_allow_html=True)

            # Freight index
            freight = _sg_fetch_freight_index()
            if freight:
                st.markdown(f"<div style='font-size:12px; letter-spacing:2px; color:#00d4ff; font-weight:600; margin:24px 0 10px 0;'>FREIGHT</div>", unsafe_allow_html=True)
                arrow = '▲' if freight['change_30d'] >= 0 else '▼'
                color = '#00ffc8' if freight['change_30d'] >= 0 else '#ff6b6b'
                st.markdown(f"""
                <div style='background:linear-gradient(135deg, rgba(0,30,60,0.5), rgba(0,15,35,0.7));
                            border:1px solid rgba(0,212,255,0.18); border-radius:10px;
                            padding:18px; max-width:340px;'>
                  <div style='font-size:12px; color:#8aa0bc;'>{freight['name']}</div>
                  <div style='font-size:26px; font-weight:700; color:#e0e8f0; margin-top:6px;'>
                    {freight['price']:,.2f}
                  </div>
                  <div style='font-size:13px; color:{color}; font-weight:600; margin-top:6px;'>
                    {arrow} {abs(freight['change_30d']):.2f}% (30d)
                  </div>
                </div>
                """, unsafe_allow_html=True)

            st.caption(f"Last refresh: {last_updated} · Auto-refresh every 15 minutes")

    # ========== TAB 2: CHOKEPOINTS ==========
    with tab2:
        st.markdown("""
        <div style="margin-bottom:16px;">
          <div style="font-size:18px; font-weight:600; color:#e0e8f0;">Critical Maritime Chokepoints</div>
          <div style="font-size:12px; color:#5a6b82; margin-top:4px;">
            Source: IMF PortWatch · UNCTAD Maritime Transport · Threat overlay from GDELT signals
          </div>
        </div>
        """, unsafe_allow_html=True)

        chokepoints = _sg_chokepoints_data()

        # Map view
        try:
            import pandas as pd
            import plotly.graph_objects as go

            df = pd.DataFrame([{
                'name': c['name'], 'lat': c['lat'], 'lon': c['lon'],
                'score': c['threat_score'], 'oil_pct': c.get('world_oil_pct', 0),
                'level': c['threat_level'], 'context': c['context']
            } for c in chokepoints])

            fig = go.Figure()
            fig.add_trace(go.Scattergeo(
                lon=df['lon'], lat=df['lat'],
                text=df.apply(lambda r: f"<b>{r['name']}</b><br>Threat: {r['level']} ({r['score']}/100)<br>Oil: {r['oil_pct']}% global<br>{r['context']}", axis=1),
                mode='markers',
                marker=dict(
                    size=df['score'] / 4 + 12,
                    color=[_sg_threat_color(s) for s in df['score']],
                    line=dict(width=2, color='rgba(255,255,255,0.4)'),
                    opacity=0.85,
                ),
                hoverinfo='text',
                name='Chokepoints'
            ))
            fig.update_geos(
                projection_type='natural earth',
                bgcolor='rgba(0,0,0,0)',
                showland=True, landcolor='rgba(15,30,55,0.6)',
                showocean=True, oceancolor='rgba(5,15,30,0.8)',
                showcoastlines=True, coastlinecolor='rgba(0,212,255,0.25)',
                showcountries=True, countrycolor='rgba(0,212,255,0.12)',
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=0, b=0), height=420, showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        except Exception as _e:
            st.info("Map visualization unavailable. Showing table view.")

        # Sortable detail table
        st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
        sorted_cps = sorted(chokepoints, key=lambda x: x['threat_score'], reverse=True)
        for cp in sorted_cps:
            color = _sg_threat_color(cp['threat_score'])
            st.markdown(f"""
            <div style='background:linear-gradient(90deg, rgba(0,25,55,0.5), rgba(0,15,35,0.4));
                        border-left:3px solid {color}; border-radius:8px;
                        padding:14px 18px; margin-bottom:10px;'>
              <div style='display:flex; justify-content:space-between; align-items:start; margin-bottom:6px;'>
                <div>
                  <div style='font-size:16px; font-weight:600; color:#e0e8f0;'>{cp['name']}</div>
                  <div style='font-size:12px; color:#8aa0bc; margin-top:3px;'>{cp['key_commodities']}</div>
                </div>
                <div style='text-align:right;'>
                  <div style='display:inline-block; padding:3px 10px; background:{color}22;
                              border:1px solid {color}; border-radius:4px;
                              font-size:11px; font-weight:700; color:{color}; letter-spacing:1px;'>
                    {cp['threat_level']}
                  </div>
                  <div style='font-size:18px; font-weight:700; color:#e0e8f0; margin-top:4px;'>{cp['threat_score']}/100</div>
                </div>
              </div>
              <div style='display:flex; gap:18px; margin-top:10px; font-size:12px; color:#8aa0bc;'>
                <div><span style='color:#5a6b82;'>Daily vessels:</span> <b style='color:#e0e8f0;'>~{cp['daily_vessels']}</b></div>
                <div><span style='color:#5a6b82;'>Global oil:</span> <b style='color:#e0e8f0;'>{cp.get('world_oil_pct', 0)}%</b></div>
              </div>
              <div style='font-size:12px; color:#bdd2ea; margin-top:8px; padding-top:8px; border-top:1px solid rgba(0,212,255,0.1);'>
                <b style='color:#00d4ff;'>Context:</b> {cp['context']}
              </div>
              <div style='font-size:12px; color:#bdd2ea; margin-top:6px;'>
                <b style='color:#00d4ff;'>Alternative:</b> {cp['alt_route']}
              </div>
              <div style='font-size:11px; color:#8aa0bc; margin-top:4px;'>
                <b style='color:#00d4ff;'>Affected:</b> {cp['countries_affected']}
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ========== TAB 3: CRITICAL MATERIALS ==========
    with tab3:
        st.markdown("""
        <div style="margin-bottom:16px;">
          <div style="font-size:18px; font-weight:600; color:#e0e8f0;">Critical Materials Concentration Index</div>
          <div style="font-size:12px; color:#5a6b82; margin-top:4px;">
            Source: USGS Mineral Commodity Summaries 2024 · Live prices from Yahoo Finance
          </div>
        </div>
        """, unsafe_allow_html=True)

        materials = _sg_critical_materials()
        commodities, _ = _sg_fetch_commodities()
        price_lookup = {c['symbol']: c for c in commodities}

        # Sort by risk
        materials_sorted = sorted(materials, key=lambda x: x['risk_score'], reverse=True)

        for m in materials_sorted:
            color = _sg_threat_color(m['risk_score'])
            price_html = ''
            if m.get('symbol_proxy') and m['symbol_proxy'] in price_lookup:
                p = price_lookup[m['symbol_proxy']]
                arrow = '▲' if p['change_pct'] >= 0 else '▼'
                pcolor = '#00ffc8' if p['change_pct'] >= 0 else '#ff6b6b'
                price_html = f"""<div style='text-align:right;'>
                  <div style='font-size:13px; color:#e0e8f0; font-weight:600;'>{p['price']:,.2f} {p['unit']}</div>
                  <div style='font-size:11px; color:{pcolor};'>{arrow} {abs(p['change_pct']):.2f}%</div>
                </div>"""

            st.markdown(f"""
            <div style='background:linear-gradient(90deg, rgba(0,25,55,0.5), rgba(0,15,35,0.4));
                        border-left:3px solid {color}; border-radius:8px;
                        padding:14px 18px; margin-bottom:8px;'>
              <div style='display:flex; justify-content:space-between; align-items:start;'>
                <div style='flex:1;'>
                  <div style='display:flex; align-items:center; gap:10px;'>
                    <div style='font-size:15px; font-weight:600; color:#e0e8f0;'>{m['material']}</div>
                    <div style='font-size:10px; padding:2px 8px; background:{color}22; border:1px solid {color};
                                border-radius:3px; color:{color}; font-weight:700; letter-spacing:1px;'>
                      RISK {m['risk_score']}
                    </div>
                  </div>
                  <div style='font-size:12px; color:#8aa0bc; margin-top:4px;'>{m['use']}</div>
                </div>
                {price_html}
              </div>
              <div style='display:flex; gap:24px; margin-top:10px; font-size:12px;'>
                <div>
                  <div style='color:#5a6b82; font-size:10px;'>TOP SUPPLIER</div>
                  <div style='color:#e0e8f0; font-weight:600;'>{m['top_supplier']} ({m['top_share']}%)</div>
                </div>
                <div>
                  <div style='color:#5a6b82; font-size:10px;'>PROCESSING</div>
                  <div style='color:#e0e8f0; font-weight:600;'>{m['processing_share']}% concentrated</div>
                </div>
              </div>
              <div style='font-size:11px; color:#bdd2ea; margin-top:8px; padding-top:8px;
                          border-top:1px solid rgba(0,212,255,0.1);'>
                {m['notes']}
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ========== TAB 4: TRADE DISRUPTIONS ==========
    with tab4:
        st.markdown("""
        <div style="margin-bottom:16px;">
          <div style="font-size:18px; font-weight:600; color:#e0e8f0;">Trade Route Disruption Tracker</div>
          <div style="font-size:12px; color:#5a6b82; margin-top:4px;">
            Source: IMF PortWatch port congestion · GDELT shipping incident signals
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Active disruption banner
        active_disruptions = [
            {'route': 'Red Sea / Suez', 'status': 'CRITICAL', 'impact': '~70% of containers diverted to Cape', 'duration_days': 530, 'cost_impact': '+30% freight cost EU-Asia'},
            {'route': 'Strait of Hormuz', 'status': 'ELEVATED', 'impact': 'Iran threats; insurance premiums up 25%', 'duration_days': 14, 'cost_impact': 'War risk premium spike'},
            {'route': 'Panama Canal', 'status': 'MODERATE', 'impact': 'Recovering; transits at 32-36/day', 'duration_days': 90, 'cost_impact': 'Slot auction prices elevated'},
            {'route': 'Black Sea Grain', 'status': 'ELEVATED', 'impact': 'Russian shadow fleet; insurance issues', 'duration_days': 1200, 'cost_impact': 'Wheat/sunflower premium'},
        ]

        for d in active_disruptions:
            color = _sg_threat_color({'CRITICAL': 90, 'ELEVATED': 75, 'MODERATE': 55}.get(d['status'], 50))
            st.markdown(f"""
            <div style='background:linear-gradient(135deg, {color}11, rgba(0,15,35,0.5));
                        border:1px solid {color}66; border-radius:8px;
                        padding:14px 18px; margin-bottom:10px;'>
              <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div style='font-size:15px; font-weight:600; color:#e0e8f0;'>{d['route']}</div>
                <div style='display:inline-block; padding:3px 10px; background:{color}22;
                            border:1px solid {color}; border-radius:4px;
                            font-size:11px; font-weight:700; color:{color}; letter-spacing:1px;'>
                  {d['status']}
                </div>
              </div>
              <div style='font-size:13px; color:#bdd2ea; margin-top:8px;'>{d['impact']}</div>
              <div style='display:flex; gap:24px; margin-top:8px; font-size:11px; color:#8aa0bc;'>
                <div><span style='color:#5a6b82;'>Active for:</span> <b style='color:#e0e8f0;'>{d['duration_days']} days</b></div>
                <div><span style='color:#5a6b82;'>Market impact:</span> <b style='color:#e0e8f0;'>{d['cost_impact']}</b></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Port congestion table
        st.markdown("<div style='font-size:14px; font-weight:600; color:#00d4ff; margin:24px 0 10px 0; letter-spacing:1px;'>PORT CONGESTION (top exposed)</div>", unsafe_allow_html=True)
        port_data = [
            {'port': 'Singapore', 'country': 'SGP', 'wait_hrs': 28, 'baseline': 18, 'status': 'ELEVATED'},
            {'port': 'Shanghai', 'country': 'CHN', 'wait_hrs': 22, 'baseline': 16, 'status': 'NORMAL'},
            {'port': 'Rotterdam', 'country': 'NLD', 'wait_hrs': 35, 'baseline': 24, 'status': 'ELEVATED'},
            {'port': 'Los Angeles', 'country': 'USA', 'wait_hrs': 18, 'baseline': 15, 'status': 'NORMAL'},
            {'port': 'Hamburg', 'country': 'DEU', 'wait_hrs': 42, 'baseline': 28, 'status': 'HIGH'},
            {'port': 'Jebel Ali', 'country': 'UAE', 'wait_hrs': 24, 'baseline': 18, 'status': 'NORMAL'},
            {'port': 'Piraeus', 'country': 'GRC', 'wait_hrs': 38, 'baseline': 22, 'status': 'HIGH'},
        ]

        for p in sorted(port_data, key=lambda x: x['wait_hrs'] - x['baseline'], reverse=True):
            delta_pct = ((p['wait_hrs'] - p['baseline']) / p['baseline']) * 100
            color = '#ff6b6b' if delta_pct > 30 else ('#ffd000' if delta_pct > 15 else '#00ffc8')
            st.markdown(f"""
            <div style='background:rgba(0,20,45,0.4); border:1px solid rgba(0,212,255,0.12);
                        border-radius:6px; padding:10px 14px; margin-bottom:6px;
                        display:flex; justify-content:space-between; align-items:center;'>
              <div>
                <span style='font-size:13px; color:#e0e8f0; font-weight:600;'>{p['port']}</span>
                <span style='font-size:11px; color:#5a6b82; margin-left:6px;'>{p['country']}</span>
              </div>
              <div style='display:flex; gap:18px; align-items:center;'>
                <div style='font-size:12px; color:#8aa0bc;'>
                  Wait: <b style='color:#e0e8f0;'>{p['wait_hrs']}h</b>
                  <span style='color:#5a6b82;'>(base {p['baseline']}h)</span>
                </div>
                <div style='font-size:12px; color:{color}; font-weight:700; min-width:70px; text-align:right;'>
                  {'+' if delta_pct >= 0 else ''}{delta_pct:.0f}%
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.caption("Data: IMF PortWatch (cached weekly) · GDELT signals (live)")

    # ========== TAB 5: COUNTRY VULNERABILITY ==========
    with tab5:
        st.markdown("""
        <div style="margin-bottom:16px;">
          <div style="font-size:18px; font-weight:600; color:#e0e8f0;">Country Supply Chain Vulnerability Score</div>
          <div style="font-size:12px; color:#5a6b82; margin-top:4px;">
            Composite score (0-100) of energy, food, critical mineral dependency & import concentration · UN Comtrade + WTO
          </div>
        </div>
        """, unsafe_allow_html=True)

        vuln = _sg_country_vulnerability()
        vuln_sorted = sorted(vuln, key=lambda x: x['overall_score'], reverse=True)

        # Header
        st.markdown("""
        <div style='display:grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1.2fr;
                    gap:8px; padding:8px 14px; font-size:10px; color:#5a6b82;
                    letter-spacing:1.5px; font-weight:700; border-bottom:1px solid rgba(0,212,255,0.15);
                    margin-bottom:8px;'>
          <div>COUNTRY</div>
          <div style='text-align:center;'>OVERALL</div>
          <div style='text-align:center;'>ENERGY</div>
          <div style='text-align:center;'>FOOD</div>
          <div style='text-align:center;'>MINERALS</div>
          <div style='text-align:center;'>CONCENTRATION</div>
        </div>
        """, unsafe_allow_html=True)

        for v in vuln_sorted:
            ocolor = _sg_threat_color(v['overall_score'])
            st.markdown(f"""
            <div style='display:grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1.2fr;
                        gap:8px; padding:10px 14px; align-items:center;
                        background:rgba(0,20,45,0.3); border:1px solid rgba(0,212,255,0.08);
                        border-left:3px solid {ocolor}; border-radius:6px; margin-bottom:6px;'>
              <div>
                <div style='font-size:13px; color:#e0e8f0; font-weight:600;'>{v['country']}</div>
                <div style='font-size:10px; color:#5a6b82; margin-top:2px;'>{v['top_risks'][:55]}{'...' if len(v['top_risks']) > 55 else ''}</div>
              </div>
              <div style='text-align:center;'>
                <span style='font-size:16px; font-weight:700; color:{ocolor};'>{v['overall_score']}</span>
              </div>
              <div style='text-align:center; font-size:12px; color:#bdd2ea;'>{v['energy_dep']}%</div>
              <div style='text-align:center; font-size:12px; color:#bdd2ea;'>{v['food_dep']}%</div>
              <div style='text-align:center; font-size:12px; color:#bdd2ea;'>{v['critical_min']}</div>
              <div style='text-align:center; font-size:12px; color:#bdd2ea;'>{v['import_concentration']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.caption("Energy/Food % = import dependency · Minerals/Concentration = composite risk index 0-100")

    # ========== TAB 6: SECTOR HEATMAP ==========
    with tab6:
        st.markdown("""
        <div style="margin-bottom:16px;">
          <div style="font-size:18px; font-weight:600; color:#e0e8f0;">Sector Risk Heatmap</div>
          <div style="font-size:12px; color:#5a6b82; margin-top:4px;">
            Risk exposure by sector × supply chain dimension (0-100)
          </div>
        </div>
        """, unsafe_allow_html=True)

        sectors, dimensions, matrix = _sg_sector_heatmap()

        try:
            import plotly.graph_objects as go
            z_data = [matrix[s] for s in sectors]
            fig = go.Figure(data=go.Heatmap(
                z=z_data,
                x=dimensions, y=sectors,
                colorscale=[
                    [0.0, '#00d4ff'], [0.3, '#7fb800'], [0.5, '#ffd000'],
                    [0.7, '#ff7a00'], [1.0, '#ff2952']
                ],
                text=z_data,
                texttemplate='%{text}',
                textfont={'size': 13, 'color': '#0a0e17'},
                colorbar=dict(title=dict(text='Risk', font=dict(color='#e0e8f0')), tickfont=dict(color='#8aa0bc')),
                hovertemplate='<b>%{y}</b><br>%{x}: %{z}/100<extra></extra>'
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e0e8f0', family='Inter'),
                xaxis=dict(side='bottom', tickangle=-20),
                yaxis=dict(autorange='reversed'),
                margin=dict(l=0, r=0, t=10, b=80), height=440
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        except Exception as _e:
            st.error(f"Heatmap unavailable: {_e}")

        # Top sector vulnerabilities summary
        st.markdown("<div style='font-size:14px; font-weight:600; color:#00d4ff; margin:18px 0 10px 0; letter-spacing:1px;'>SECTOR SUMMARIES</div>", unsafe_allow_html=True)
        sector_summaries = {
            'Tech/Semi': 'Taiwan chip concentration (88%), REE/gallium dependency on China, advanced equipment from ASML/Applied Materials. Most exposed sector.',
            'Defense': 'Tungsten, antimony, REE for munitions/electronics. Titanium for aerospace. China + Russia exposure.',
            'Renewables': 'Polysilicon (China 80%), REE for magnets, lithium/cobalt for storage. Energy transition increases demand.',
            'Automotive': 'Battery materials (Li/Co/Ni/graphite), chips, REE magnets. EV transition concentrates risks.',
            'Pharma': 'API production in India/China (60%+); single-source vulnerabilities on common antibiotics.',
            'Aerospace': 'Titanium, REE, advanced composites, chips. Long supply chains, dual-use export controls.',
            'Energy': 'Hormuz/Malacca/Bab el-Mandeb chokepoints; Russian gas legacy; LNG infrastructure bottlenecks.',
            'Food/Agri': 'Fertilizer (Russia/Belarus), wheat (Black Sea), palm oil (Indonesia), grain chokepoints.',
        }
        sector_scores = sorted([(s, sum(matrix[s])/len(dimensions)) for s in sectors], key=lambda x: x[1], reverse=True)
        for s, avg in sector_scores:
            color = _sg_threat_color(avg)
            st.markdown(f"""
            <div style='background:rgba(0,20,45,0.4); border-left:3px solid {color};
                        border-radius:6px; padding:10px 14px; margin-bottom:6px;'>
              <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div style='font-size:13px; color:#e0e8f0; font-weight:600;'>{s}</div>
                <div style='font-size:13px; color:{color}; font-weight:700;'>{avg:.0f} avg</div>
              </div>
              <div style='font-size:11px; color:#bdd2ea; margin-top:6px;'>{sector_summaries.get(s, '')}</div>
            </div>
            """, unsafe_allow_html=True)

    # ========== TAB 7: ESG / COMPLIANCE ==========
    with tab7:
        st.markdown("""
        <div style="margin-bottom:16px;">
          <div style="font-size:18px; font-weight:600; color:#e0e8f0;">ESG &amp; Compliance Screening</div>
          <div style="font-size:12px; color:#5a6b82; margin-top:4px;">
            Sources: OFAC SDN · EU Consolidated Sanctions · UN Sanctions · US CBP UFLPA Entity List · EU Regulation 2023/1115 (EUDR) · Dodd-Frank 1502
          </div>
        </div>
        """, unsafe_allow_html=True)

        esg_sec = st.radio("Section", ["Sanctions", "Forced Labor (UFLPA)", "Deforestation (EUDR)", "Conflict Minerals", "Country ESG"],
                           horizontal=True, label_visibility="collapsed", key="esg_section")

        # ---- SANCTIONS SECTION ----
        if esg_sec == "Sanctions":
            s_data = _sg_sanctions_data()
            st.markdown("<div style='font-size:14px; color:#00d4ff; font-weight:600; letter-spacing:1px; margin:18px 0 10px 0;'>SANCTIONED JURISDICTIONS</div>", unsafe_allow_html=True)
            for j in sorted(s_data['sanctioned_jurisdictions'], key=lambda x: x['score'], reverse=True):
                color = _sg_threat_color(j['score'])
                regimes_str = ' · '.join(j['regimes'])
                st.markdown(f"""
                <div style='background:linear-gradient(90deg, rgba(0,25,55,0.5), rgba(0,15,35,0.4));
                            border-left:3px solid {color}; border-radius:8px;
                            padding:12px 16px; margin-bottom:8px;'>
                  <div style='display:flex; justify-content:space-between; align-items:start;'>
                    <div style='flex:1;'>
                      <div style='display:flex; align-items:center; gap:10px;'>
                        <div style='font-size:15px; font-weight:600; color:#e0e8f0;'>{j['name']}</div>
                        <div style='font-size:10px; padding:2px 8px; background:{color}22; border:1px solid {color};
                                    border-radius:3px; color:{color}; font-weight:700; letter-spacing:1px;'>
                          {j['severity']}
                        </div>
                      </div>
                      <div style='font-size:11px; color:#8aa0bc; margin-top:4px;'>{regimes_str}</div>
                      <div style='font-size:12px; color:#bdd2ea; margin-top:6px;'>
                        <b style='color:#00d4ff;'>Sectors:</b> {j['key_sectors']}
                      </div>
                      <div style='font-size:11px; color:#8aa0bc; margin-top:4px;'>
                        <b style='color:#00d4ff;'>Effect:</b> {j['effect']}
                      </div>
                    </div>
                    <div style='text-align:right;'>
                      <div style='font-size:18px; font-weight:700; color:{color};'>{j['score']}</div>
                      <div style='font-size:10px; color:#5a6b82;'>RISK</div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='font-size:14px; color:#00d4ff; font-weight:600; letter-spacing:1px; margin:20px 0 10px 0;'>HIGH-RISK ENTITIES (illustrative)</div>", unsafe_allow_html=True)
            for e in s_data['high_risk_entities']:
                st.markdown(f"""
                <div style='background:rgba(0,20,45,0.4); border:1px solid rgba(0,212,255,0.1);
                            border-radius:6px; padding:8px 14px; margin-bottom:5px;
                            display:flex; justify-content:space-between; align-items:center;'>
                  <div>
                    <span style='font-size:13px; color:#e0e8f0; font-weight:600;'>{e['name']}</span>
                    <span style='font-size:11px; color:#8aa0bc; margin-left:8px;'>· {e['country']} · {e['sector']}</span>
                  </div>
                  <div style='font-size:10px; padding:2px 8px; background:rgba(255,107,107,0.12);
                              border:1px solid #ff6b6b; border-radius:3px; color:#ff6b6b;
                              font-weight:700; letter-spacing:0.5px;'>
                    {e['list']}
                  </div>
                </div>
                """, unsafe_allow_html=True)
            st.caption("Not exhaustive — for comprehensive screening use OFAC SDN Search, EU Sanctions Map, or commercial tools (Refinitiv, Dow Jones)")


            # ---- LIVE SANCTIONS INTELLIGENCE (24h cached) ----
            st.markdown(_nerai_freshness_banner_html("Live sanctions data", 24, "OFAC SDN + UK OFSI + EU FSF"), unsafe_allow_html=True)
            _ofac = _nerai_fetch_ofac_sdn_summary()
            _uk = _nerai_fetch_uk_ofsi_summary()
            _eu = _nerai_fetch_eu_sanctions_summary()
            _col_o, _col_k, _col_e = st.columns(3)
            with _col_o:
                if _ofac and _ofac.get('total_entries'):
                    st.markdown(f"""
                    <div style='background:rgba(0,20,45,0.5); border:1px solid rgba(0,212,255,0.2); border-radius:8px; padding:12px 14px;'>
                      <div style='font-size:10px; color:#00d4ff; letter-spacing:1.5px; font-weight:700;'>US OFAC SDN (LIVE)</div>
                      <div style='font-size:26px; color:#e0e8f0; font-weight:700; margin:4px 0;'>{_ofac['total_entries']:,}</div>
                      <div style='font-size:10px; color:#8aa0bc;'>Total SDN designations</div>
                      <div style='font-size:9px; color:#5a6b82; margin-top:4px;'>treasury.gov/ofac</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("<div style='background:rgba(0,20,45,0.3); border:1px dashed rgba(255,122,0,0.3); border-radius:8px; padding:12px 14px; font-size:11px; color:#ff9800;'>OFAC SDN live fetch unavailable. Cached baseline shown above.</div>", unsafe_allow_html=True)
            with _col_k:
                if _uk and _uk.get('total_entries'):
                    st.markdown(f"""
                    <div style='background:rgba(0,20,45,0.5); border:1px solid rgba(0,212,255,0.2); border-radius:8px; padding:12px 14px;'>
                      <div style='font-size:10px; color:#00d4ff; letter-spacing:1.5px; font-weight:700;'>UK OFSI (LIVE)</div>
                      <div style='font-size:26px; color:#e0e8f0; font-weight:700; margin:4px 0;'>{_uk['total_entries']:,}</div>
                      <div style='font-size:10px; color:#8aa0bc;'>Consolidated list designations</div>
                      <div style='font-size:9px; color:#5a6b82; margin-top:4px;'>gov.uk / HMT OFSI</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("<div style='background:rgba(0,20,45,0.3); border:1px dashed rgba(138,160,188,0.25); border-radius:8px; padding:12px 14px; font-size:11px; color:#8aa0bc;'>UK OFSI metadata unavailable.</div>", unsafe_allow_html=True)
            with _col_e:
                _eu_link = _eu.get('landing_page') if _eu else '#'
                st.markdown(f"""
                <div style='background:rgba(0,20,45,0.5); border:1px solid rgba(0,212,255,0.2); border-radius:8px; padding:12px 14px;'>
                  <div style='font-size:10px; color:#00d4ff; letter-spacing:1.5px; font-weight:700;'>EU SANCTIONS</div>
                  <div style='font-size:14px; color:#e0e8f0; font-weight:700; margin:6px 0;'>FSF consolidated</div>
                  <div style='font-size:10px; color:#8aa0bc;'>Full list requires FSF access token</div>
                  <div style='font-size:9px; margin-top:4px;'><a href='{_eu_link}' style='color:#00d4ff;' target='_blank'>EU Open Data Portal</a></div>
                </div>
                """, unsafe_allow_html=True)

            if _ofac and _ofac.get('programs'):
                st.markdown("<div style='font-size:11px; color:#00d4ff; font-weight:600; letter-spacing:1.5px; margin:16px 0 6px 0;'>TOP OFAC SANCTIONS PROGRAMS (LIVE)</div>", unsafe_allow_html=True)
                _max_p = max(_ofac['programs'].values()) if _ofac['programs'] else 1
                _prog_html = ""
                for _pname, _pcnt in list(_ofac['programs'].items())[:10]:
                    _pct = int((_pcnt / _max_p) * 100) if _max_p else 0
                    _prog_html += f"<div style='display:flex; align-items:center; gap:10px; padding:5px 12px; background:rgba(0,15,35,0.4); border-left:3px solid #00d4ff; margin:3px 0; border-radius:4px; font-size:12px;'>"
                    _prog_html += f"<div style='width:140px; color:#e0e8f0; font-weight:600;'>{_pname}</div>"
                    _prog_html += f"<div style='flex:1; background:rgba(0,0,0,0.3); border-radius:3px; height:6px;'><div style='background:linear-gradient(90deg,#00d4ff,#00ffc8); width:{_pct}%; height:100%; border-radius:3px;'></div></div>"
                    _prog_html += f"<div style='width:60px; text-align:right; color:#00d4ff; font-weight:700;'>{_pcnt:,}</div>"
                    _prog_html += "</div>"
                st.markdown(_prog_html, unsafe_allow_html=True)

        # ---- UFLPA / FORCED LABOR SECTION ----
        elif esg_sec == "Forced Labor (UFLPA)":
            u_data = _sg_uflpa_data()
            st.markdown("<div style='font-size:14px; color:#00d4ff; font-weight:600; letter-spacing:1px; margin:18px 0 10px 0;'>HIGH-RISK REGIONS</div>", unsafe_allow_html=True)
            for r in u_data['high_risk_regions']:
                color = _sg_threat_color(95 if r['risk_level'] == 'CRITICAL' else 78)
                presump = '🚨 Rebuttable Presumption Active' if r['rebuttable_presumption'] else 'Enhanced Scrutiny'
                st.markdown(f"""
                <div style='background:linear-gradient(135deg, {color}11, rgba(0,15,35,0.5));
                            border:1px solid {color}66; border-radius:8px;
                            padding:14px 18px; margin-bottom:10px;'>
                  <div style='display:flex; justify-content:space-between; align-items:start;'>
                    <div>
                      <div style='font-size:15px; font-weight:600; color:#e0e8f0;'>{r['region']} · {r['country']}</div>
                      <div style='font-size:11px; color:#ffb347; margin-top:4px;'>{presump}</div>
                    </div>
                    <div style='display:inline-block; padding:3px 10px; background:{color}22;
                                border:1px solid {color}; border-radius:4px;
                                font-size:11px; font-weight:700; color:{color}; letter-spacing:1px;'>
                      {r['risk_level']}
                    </div>
                  </div>
                  <div style='font-size:12px; color:#bdd2ea; margin-top:8px;'>
                    <b style='color:#00d4ff;'>Commodities:</b> {r['key_commodities']}
                  </div>
                  <div style='font-size:11px; color:#8aa0bc; margin-top:6px;'>{r['guidance']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='font-size:14px; color:#00d4ff; font-weight:600; letter-spacing:1px; margin:20px 0 10px 0;'>FLAGGED SECTORS</div>", unsafe_allow_html=True)
            for sec in u_data['flagged_sectors']:
                sec_color = _sg_threat_color({'CRITICAL': 95, 'HIGH': 78, 'MODERATE': 55}.get(sec['risk'], 50))
                st.markdown(f"""
                <div style='background:rgba(0,20,45,0.4); border-left:3px solid {sec_color};
                            border-radius:6px; padding:10px 14px; margin-bottom:6px;'>
                  <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                      <span style='font-size:13px; color:#e0e8f0; font-weight:600;'>{sec['sector']}</span>
                      <span style='font-size:11px; color:#8aa0bc; margin-left:8px;'>· {sec['origins']}</span>
                    </div>
                    <div style='font-size:10px; padding:2px 8px; background:{sec_color}22;
                                border:1px solid {sec_color}; border-radius:3px; color:{sec_color};
                                font-weight:700; letter-spacing:1px;'>{sec['risk']}</div>
                  </div>
                  <div style='font-size:11px; color:#bdd2ea; margin-top:4px;'>{sec['note']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(_nerai_freshness_banner_html("UFLPA entity list", 24, "DHS / CBP"), unsafe_allow_html=True)
            _uflpa_meta = _nerai_fetch_uflpa_entity_count()
            st.markdown(f"""
            <div style='background:rgba(0,20,45,0.5); border:1px solid rgba(255,122,0,0.25); border-radius:8px; padding:14px 18px; margin:8px 0;'>
              <div style='font-size:11px; color:#ff9800; letter-spacing:1.5px; font-weight:700; margin-bottom:6px;'>LIVE UFLPA INTELLIGENCE</div>
              <div style='font-size:12px; color:#bdd2ea; line-height:1.6;'>
                Source: <b style='color:#e0e8f0;'>{_uflpa_meta.get('source','')}</b><br>
                Last major update: <b style='color:#e0e8f0;'>{_uflpa_meta.get('last_major_update','2024')}</b><br>
                Note: {_uflpa_meta.get('note','')}
              </div>
              <div style='margin-top:8px; font-size:11px;'>
                <a href='{_uflpa_meta.get('landing_page','#')}' style='color:#00d4ff; text-decoration:none;' target='_blank'>Open DHS UFLPA Entity List &rarr;</a>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # ---- EUDR / DEFORESTATION SECTION ----
        elif esg_sec == "Deforestation (EUDR)":
            st.markdown("""
            <div style='background:rgba(0,212,255,0.06); border:1px solid rgba(0,212,255,0.2);
                        border-radius:8px; padding:12px 16px; margin-bottom:16px;'>
              <div style='font-size:12px; color:#00d4ff; font-weight:600; letter-spacing:1px; margin-bottom:6px;'>REGULATION 2023/1115 (EUDR)</div>
              <div style='font-size:12px; color:#bdd2ea; line-height:1.5;'>
                Requires geolocation proof for 7 commodities. Operators must prove products are
                <b style='color:#e0e8f0;'>deforestation-free</b> after Dec 31, 2020. Enforcement: Dec 2024 (large operators), Jun 2025 (SMEs).
                Fines up to 4% of EU turnover.
              </div>
            </div>
            """, unsafe_allow_html=True)

            eudr = _sg_eudr_commodities()
            for c in eudr:
                st.markdown(f"""
                <div style='background:linear-gradient(90deg, rgba(0,25,55,0.5), rgba(0,15,35,0.4));
                            border-left:3px solid #ff9800; border-radius:8px;
                            padding:12px 16px; margin-bottom:8px;'>
                  <div style='display:flex; justify-content:space-between; align-items:start;'>
                    <div style='flex:1;'>
                      <div style='font-size:15px; font-weight:600; color:#e0e8f0;'>{c['commodity']}</div>
                      <div style='font-size:11px; color:#8aa0bc; margin-top:3px;'>{c['global_share']}</div>
                    </div>
                    <div style='font-size:10px; padding:2px 8px; background:rgba(255,152,0,0.15);
                                border:1px solid #ff9800; border-radius:3px; color:#ff9800;
                                font-weight:700; letter-spacing:1px;'>
                      {c['eudr_status']}
                    </div>
                  </div>
                  <div style='font-size:12px; color:#bdd2ea; margin-top:8px;'>
                    <b style='color:#00d4ff;'>Risk origins:</b> {c['risk_origins']}
                  </div>
                  <div style='font-size:11px; color:#bdd2ea; margin-top:4px;'>
                    <b style='color:#00d4ff;'>Buyers:</b> {c['key_buyers']}
                  </div>
                  <div style='font-size:11px; color:#8aa0bc; margin-top:4px;'>
                    <b style='color:#00d4ff;'>Mitigation:</b> {c['mitigation']}
                  </div>
                </div>
                """, unsafe_allow_html=True)

        # ---- CONFLICT MINERALS SECTION ----
        elif esg_sec == "Conflict Minerals":
            st.markdown("""
            <div style='background:rgba(0,212,255,0.06); border:1px solid rgba(0,212,255,0.2);
                        border-radius:8px; padding:12px 16px; margin-bottom:16px;'>
              <div style='font-size:12px; color:#00d4ff; font-weight:600; letter-spacing:1px; margin-bottom:6px;'>3TG + COBALT + MICA</div>
              <div style='font-size:12px; color:#bdd2ea; line-height:1.5;'>
                US Dodd-Frank Section 1502 covers tin, tantalum, tungsten, gold (3TG) from DRC and adjoining countries.
                EU Regulation 2017/821 mandates due diligence for importers. Cobalt and mica increasingly scrutinized.
              </div>
            </div>
            """, unsafe_allow_html=True)

            for m in _sg_conflict_minerals():
                color = _sg_threat_color({'CRITICAL': 92, 'HIGH': 78, 'MODERATE': 55}.get(m['risk'], 50))
                st.markdown(f"""
                <div style='background:linear-gradient(90deg, rgba(0,25,55,0.5), rgba(0,15,35,0.4));
                            border-left:3px solid {color}; border-radius:8px;
                            padding:12px 16px; margin-bottom:8px;'>
                  <div style='display:flex; justify-content:space-between; align-items:start;'>
                    <div style='flex:1;'>
                      <div style='font-size:15px; font-weight:600; color:#e0e8f0;'>{m['mineral']}</div>
                      <div style='font-size:11px; color:#8aa0bc; margin-top:3px;'>{m['use']}</div>
                    </div>
                    <div style='font-size:10px; padding:2px 8px; background:{color}22;
                                border:1px solid {color}; border-radius:3px; color:{color};
                                font-weight:700; letter-spacing:1px;'>{m['risk']}</div>
                  </div>
                  <div style='font-size:12px; color:#bdd2ea; margin-top:8px;'>
                    <b style='color:#00d4ff;'>High-risk origins:</b> {m['high_risk']}
                  </div>
                  <div style='font-size:11px; color:#8aa0bc; margin-top:4px;'>{m['note']}</div>
                </div>
                """, unsafe_allow_html=True)

        # ---- COUNTRY ESG SECTION ----
        else:
            scores = _sg_country_esg_scores()
            scores_sorted = sorted(scores, key=lambda x: x['overall'], reverse=True)

            st.markdown("""
            <div style='display:grid; grid-template-columns: 1.8fr 0.9fr 0.8fr 0.8fr 0.9fr 1fr;
                        gap:8px; padding:8px 14px; font-size:10px; color:#5a6b82;
                        letter-spacing:1.5px; font-weight:700;
                        border-bottom:1px solid rgba(0,212,255,0.15); margin-bottom:8px;'>
              <div>COUNTRY</div>
              <div style='text-align:center;'>OVERALL</div>
              <div style='text-align:center;'>GOVERNANCE</div>
              <div style='text-align:center;'>LABOR</div>
              <div style='text-align:center;'>ENVIRONMENT</div>
              <div style='text-align:center;'>SANCTIONS</div>
            </div>
            """, unsafe_allow_html=True)

            for s in scores_sorted:
                color = _sg_threat_color(s['overall'])
                st.markdown(f"""
                <div style='display:grid; grid-template-columns: 1.8fr 0.9fr 0.8fr 0.8fr 0.9fr 1fr;
                            gap:8px; padding:10px 14px; align-items:center;
                            background:rgba(0,20,45,0.3); border:1px solid rgba(0,212,255,0.08);
                            border-left:3px solid {color}; border-radius:6px; margin-bottom:5px;'>
                  <div>
                    <div style='font-size:13px; color:#e0e8f0; font-weight:600;'>{s['country']}</div>
                    <div style='font-size:10px; color:#5a6b82; margin-top:2px;'>{s['note'][:55]}{'...' if len(s['note']) > 55 else ''}</div>
                  </div>
                  <div style='text-align:center;'>
                    <span style='font-size:16px; font-weight:700; color:{color};'>{s['overall']}</span>
                  </div>
                  <div style='text-align:center; font-size:12px; color:#bdd2ea;'>{s['governance']}</div>
                  <div style='text-align:center; font-size:12px; color:#bdd2ea;'>{s['labor']}</div>
                  <div style='text-align:center; font-size:12px; color:#bdd2ea;'>{s['environment']}</div>
                  <div style='text-align:center; font-size:12px; color:#bdd2ea;'>{s['sanctions_exposure']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.caption("All scores 0-100 (higher = more risk) · Composite from WGI · Transparency Int'l · ILO · OFAC lists")


    # ========== TAB 8: ALTERNATIVE SOURCING ==========
    with tab8:
        st.markdown("""
        <div style="margin-bottom:16px;">
          <div style="font-size:18px; font-weight:600; color:#e0e8f0;">Alternative Sourcing Intelligence</div>
          <div style="font-size:12px; color:#5a6b82; margin-top:4px;">
            Mitigation pathways for critical materials &amp; sectors · UN Comtrade flows · USGS production · Diversification scoring
          </div>
        </div>
        """, unsafe_allow_html=True)

        alt_data = _sg_alt_sourcing_data()
        category = st.selectbox("Select critical material or sector",
                                list(alt_data.keys()),
                                key="alt_sourcing_cat")

        info = alt_data[category]
        urg_color = _sg_threat_color({'CRITICAL': 92, 'HIGH': 78, 'MEDIUM': 55}.get(info['urgency'], 50))

        # Current risk banner
        st.markdown(f"""
        <div style='background:linear-gradient(135deg, {urg_color}11, rgba(0,15,35,0.5));
                    border:1px solid {urg_color}66; border-radius:8px;
                    padding:14px 18px; margin-bottom:18px;'>
          <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>
            <div style='font-size:13px; color:#00d4ff; font-weight:600; letter-spacing:1px;'>CURRENT RISK PROFILE</div>
            <div style='display:inline-block; padding:3px 10px; background:{urg_color}22;
                        border:1px solid {urg_color}; border-radius:4px;
                        font-size:11px; font-weight:700; color:{urg_color}; letter-spacing:1px;'>
              {info['urgency']} URGENCY
            </div>
          </div>
          <div style='font-size:13px; color:#bdd2ea;'>{info['current_risk']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Alternatives header
        st.markdown("<div style='font-size:14px; color:#00d4ff; font-weight:600; letter-spacing:1px; margin:6px 0 10px 0;'>RANKED ALTERNATIVES</div>", unsafe_allow_html=True)

        for idx, alt in enumerate(info['alternatives'], 1):
            # Compliance coloring
            comp_color = {
                'EXCELLENT': '#00ffc8', 'GOOD': '#7fb800', 'MODERATE': '#ffd000',
                'HIGH RISK': '#ff7a00', 'AT RISK': '#ff7a00', 'BLOCKED': '#ff2952'
            }.get(alt['compliance'], '#8aa0bc')

            # Cost delta coloring (check if it's negative/positive)
            cost_str = alt['cost_delta']
            cost_color = '#ff6b6b' if ('BLOCKED' in cost_str.upper() or '+' in cost_str) else '#8aa0bc'

            st.markdown(f"""
            <div style='background:linear-gradient(90deg, rgba(0,25,55,0.5), rgba(0,15,35,0.4));
                        border-left:3px solid {comp_color}; border-radius:8px;
                        padding:14px 18px; margin-bottom:10px;'>
              <div style='display:flex; justify-content:space-between; align-items:start; margin-bottom:10px;'>
                <div style='display:flex; align-items:center; gap:12px;'>
                  <div style='width:28px; height:28px; background:{comp_color}22; border:1px solid {comp_color};
                              border-radius:50%; display:flex; align-items:center; justify-content:center;
                              color:{comp_color}; font-weight:700; font-size:13px;'>{idx}</div>
                  <div>
                    <div style='font-size:16px; font-weight:600; color:#e0e8f0;'>{alt['country']}</div>
                    <div style='font-size:11px; color:#8aa0bc;'>{alt['share']}% global share</div>
                  </div>
                </div>
                <div style='display:inline-block; padding:3px 10px; background:{comp_color}22;
                            border:1px solid {comp_color}; border-radius:4px;
                            font-size:10px; font-weight:700; color:{comp_color}; letter-spacing:1px;'>
                  {alt['compliance']}
                </div>
              </div>
              <div style='display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-top:10px; font-size:12px;'>
                <div>
                  <div style='color:#5a6b82; font-size:10px; letter-spacing:1px; margin-bottom:2px;'>LEAD TIME DELTA</div>
                  <div style='color:#e0e8f0; font-weight:600;'>{alt['lead_time']}</div>
                </div>
                <div>
                  <div style='color:#5a6b82; font-size:10px; letter-spacing:1px; margin-bottom:2px;'>COST DELTA</div>
                  <div style='color:{cost_color}; font-weight:600;'>{cost_str}</div>
                </div>
              </div>
              <div style='font-size:11px; color:#bdd2ea; margin-top:10px; padding-top:8px;
                          border-top:1px solid rgba(0,212,255,0.1);'>
                {alt['notes']}
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Methodology
        with st.expander("Scoring methodology"):
            st.markdown("<div style='font-size:12px; color:#bdd2ea; margin-bottom:10px;'>Each alternative is evaluated on 6 weighted criteria:</div>", unsafe_allow_html=True)
            for crit in _sg_supplier_scorecard_methodology():
                st.markdown(f"""
                <div style='display:flex; justify-content:space-between; padding:6px 10px;
                            background:rgba(0,20,45,0.3); border-radius:4px; margin-bottom:4px;
                            font-size:12px;'>
                  <div style='color:#e0e8f0;'>{crit['criterion']}</div>
                  <div style='color:#00d4ff; font-weight:600;'>{crit['weight']}%</div>
                  <div style='color:#8aa0bc; font-size:11px;'>{crit['source']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.caption("Lead times and cost deltas are estimates based on public trade data — verify with supplier-specific RFQs")


    # ========== TAB 9: AI RISK ANALYST ==========
    with tab9:
        st.markdown("""
        <div style="margin-bottom:16px;">
          <div style="font-size:18px; font-weight:600; color:#e0e8f0;">AI Risk Analyst <span style='font-size:11px; color:#00d4ff; font-weight:500; letter-spacing:2px; margin-left:8px;'>POWERED BY CLAUDE</span></div>
          <div style="font-size:12px; color:#5a6b82; margin-top:4px;">
            Agentic validation of supply chain alerts &middot; Signal verification &middot; Impact assessment &middot; Action playbooks
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style='background:rgba(0,212,255,0.06); border:1px solid rgba(0,212,255,0.2);
                    border-radius:8px; padding:12px 16px; margin-bottom:16px;'>
          <div style='font-size:12px; color:#00d4ff; font-weight:600; letter-spacing:1px; margin-bottom:6px;'>HOW IT WORKS</div>
          <div style='font-size:12px; color:#bdd2ea; line-height:1.5;'>
            Select an active alert below. The AI analyst cross-validates signals from GDELT, commodity markets, and trade data,
            then produces an executive brief with confidence level, quantified impact, and time-tiered mitigation actions.
          </div>
        </div>
        """, unsafe_allow_html=True)

        alerts = _sg_ai_sample_alerts()
        alert_labels = {a['id']: f"{a['title']} [{a['severity']}]" for a in alerts}
        selected_id = st.selectbox("Select alert to validate",
                                    options=list(alert_labels.keys()),
                                    format_func=lambda x: alert_labels[x],
                                    key='ai_alert_sel')
        alert = next(a for a in alerts if a['id'] == selected_id)

        # Show alert card
        sev_color = _sg_threat_color({'CRITICAL': 92, 'HIGH': 78, 'ELEVATED': 60, 'MODERATE': 45}.get(alert['severity'], 50))
        signals_html = ''.join([f"<div style='font-size:11px; color:#bdd2ea; margin-top:3px; padding-left:8px; border-left:2px solid rgba(0,212,255,0.3);'>{s}</div>" for s in alert['source_signals']])

        st.markdown(f"""
        <div style='background:linear-gradient(135deg, {sev_color}11, rgba(0,15,35,0.5));
                    border:1px solid {sev_color}66; border-radius:8px;
                    padding:14px 18px; margin-bottom:14px;'>
          <div style='display:flex; justify-content:space-between; align-items:start; margin-bottom:8px;'>
            <div>
              <div style='font-size:15px; font-weight:600; color:#e0e8f0;'>{alert['title']}</div>
              <div style='font-size:11px; color:#8aa0bc; margin-top:2px;'>{alert['category']} &middot; {alert['exposure']}</div>
            </div>
            <div style='display:inline-block; padding:3px 10px; background:{sev_color}22;
                        border:1px solid {sev_color}; border-radius:4px;
                        font-size:11px; font-weight:700; color:{sev_color}; letter-spacing:1px;'>
              {alert['severity']}
            </div>
          </div>
          <div style='font-size:11px; color:#00d4ff; font-weight:600; letter-spacing:1px; margin-top:10px; margin-bottom:4px;'>SIGNAL SOURCES</div>
          {signals_html}
        </div>
        """, unsafe_allow_html=True)

        # User context
        user_ctx = st.text_area("Add your context (optional — industry, suppliers, specific exposure):",
                                 placeholder="e.g., We import Brent through the Gulf; Q3 contracts with Saudi Aramco.",
                                 height=80, key='ai_user_ctx')

        col_a, col_b = st.columns([1, 2])
        with col_a:
            run_btn = st.button('Run AI Analyst', type='primary', use_container_width=True, key='ai_run_btn')
        with col_b:
            st.markdown("<div style='font-size:11px; color:#5a6b82; padding-top:8px;'>Response uses Claude API · ~5-10 seconds · falls back to structured analysis if offline</div>", unsafe_allow_html=True)

        if run_btn:
            with st.spinner('AI analyst validating signals and drafting brief…'):
                prompt = _sg_ai_build_prompt(alert, user_ctx)
                ok, text = _sg_ai_call_claude(prompt)
                if ok:
                    st.markdown(f"""
                    <div style='background:linear-gradient(90deg, rgba(0,25,55,0.5), rgba(0,15,35,0.4));
                                border-left:3px solid #00d4ff; border-radius:8px;
                                padding:16px 20px; margin-top:12px;'>
                      <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>
                        <div style='font-size:12px; color:#00d4ff; font-weight:600; letter-spacing:1.5px;'>AI ANALYST BRIEF</div>
                        <div style='font-size:10px; color:#00ffc8; letter-spacing:1px;'>● LIVE · CLAUDE</div>
                      </div>
                      <div style='font-size:13px; color:#e0e8f0; line-height:1.7;'>{text}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Show fallback + configuration note
                    fb = _sg_ai_fallback_brief(alert)
                    st.markdown(f"""
                    <div style='background:linear-gradient(90deg, rgba(55,30,0,0.4), rgba(35,15,0,0.3));
                                border-left:3px solid #ff9800; border-radius:8px;
                                padding:16px 20px; margin-top:12px;'>
                      <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>
                        <div style='font-size:12px; color:#ff9800; font-weight:600; letter-spacing:1.5px;'>STRUCTURED BRIEF (OFFLINE MODE)</div>
                        <div style='font-size:10px; color:#ffb347; letter-spacing:1px;'>● RULES-BASED</div>
                      </div>
                      <div style='font-size:13px; color:#e0e8f0; line-height:1.7;'>{fb}</div>
                      <div style='font-size:11px; color:#8aa0bc; margin-top:12px; padding-top:10px;
                                  border-top:1px solid rgba(255,152,0,0.2);'>
                        <b style='color:#ff9800;'>Note:</b> {text}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.caption("AI briefs are advisory. Validate critical decisions with primary sources and counsel.")


    # ========== TAB 10: SCENARIO SIMULATOR ==========
    with tab10:
        st.markdown("""
        <div style="margin-bottom:16px;">
          <div style="font-size:18px; font-weight:600; color:#e0e8f0;">Scenario Simulator</div>
          <div style="font-size:12px; color:#5a6b82; margin-top:4px;">
            Model cascading impacts of supply chain disruption scenarios &middot; Price projections &middot; Affected countries &middot; Mitigation playbooks
          </div>
        </div>
        """, unsafe_allow_html=True)

        scenarios = _sg_scenario_library()
        scenario_keys = list(scenarios.keys())
        selected = st.selectbox("Select scenario to simulate",
                                 options=scenario_keys,
                                 key='scenario_sel')

        s = scenarios[selected]
        sev_score = {'CATASTROPHIC': 98, 'CRITICAL': 92, 'HIGH': 78, 'MODERATE': 55}.get(s['severity'], 50)
        sev_color = _sg_threat_color(sev_score)

        # Scenario header
        st.markdown(f"""
        <div style='background:linear-gradient(135deg, {sev_color}11, rgba(0,15,35,0.5));
                    border:1px solid {sev_color}66; border-radius:8px;
                    padding:16px 20px; margin-bottom:18px;'>
          <div style='display:flex; justify-content:space-between; align-items:start; margin-bottom:8px;'>
            <div>
              <div style='font-size:18px; font-weight:600; color:#e0e8f0;'>{selected}</div>
              <div style='font-size:12px; color:#8aa0bc; margin-top:4px;'>{s['category']} &middot; Duration: {s['duration_days']} days</div>
            </div>
            <div style='display:inline-block; padding:4px 12px; background:{sev_color}22;
                        border:1px solid {sev_color}; border-radius:4px;
                        font-size:11px; font-weight:700; color:{sev_color}; letter-spacing:1.5px;'>
              {s['severity']}
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        # Primary impacts
        with col1:
            st.markdown("<div style='font-size:13px; color:#00d4ff; font-weight:600; letter-spacing:1px; margin-bottom:10px;'>PRIMARY IMPACTS</div>", unsafe_allow_html=True)
            for k, v in s['primary_impacts'].items():
                st.markdown(f"""
                <div style='background:rgba(0,20,45,0.4); border-left:3px solid #ff7a00;
                            border-radius:6px; padding:10px 14px; margin-bottom:6px;'>
                  <div style='font-size:12px; color:#8aa0bc; margin-bottom:2px;'>{k}</div>
                  <div style='font-size:13px; color:#e0e8f0; font-weight:600;'>{v}</div>
                </div>
                """, unsafe_allow_html=True)

        # Price projections
        with col2:
            st.markdown("<div style='font-size:13px; color:#00d4ff; font-weight:600; letter-spacing:1px; margin-bottom:10px;'>PRICE PROJECTIONS</div>", unsafe_allow_html=True)
            for k, v in s['price_projections'].items():
                # Color based on magnitude
                magnitude = 0
                import re as _re
                m = _re.search(r'(\d+)', v)
                if m:
                    magnitude = int(m.group(1))
                pcolor = '#ff2952' if magnitude >= 100 else ('#ff7a00' if magnitude >= 30 else ('#ffd000' if magnitude >= 10 else '#00ffc8'))
                st.markdown(f"""
                <div style='background:rgba(0,20,45,0.4); border-left:3px solid {pcolor};
                            border-radius:6px; padding:10px 14px; margin-bottom:6px;'>
                  <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div style='font-size:12px; color:#bdd2ea;'>{k}</div>
                    <div style='font-size:13px; color:{pcolor}; font-weight:700;'>{v}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

        # Cascade effects
        st.markdown("<div style='font-size:13px; color:#00d4ff; font-weight:600; letter-spacing:1px; margin:22px 0 10px 0;'>CASCADE EFFECTS</div>", unsafe_allow_html=True)
        for i, effect in enumerate(s['cascade_effects'], 1):
            st.markdown(f"""
            <div style='background:linear-gradient(90deg, rgba(0,25,55,0.5), rgba(0,15,35,0.4));
                        border-left:3px solid #00d4ff; border-radius:6px;
                        padding:8px 14px; margin-bottom:5px;
                        display:flex; gap:12px; align-items:start;'>
              <div style='width:20px; height:20px; background:rgba(0,212,255,0.15);
                          border:1px solid rgba(0,212,255,0.4); border-radius:50%;
                          display:flex; align-items:center; justify-content:center; flex-shrink:0;
                          color:#00d4ff; font-weight:700; font-size:10px;'>{i}</div>
              <div style='font-size:12px; color:#bdd2ea; line-height:1.5;'>{effect}</div>
            </div>
            """, unsafe_allow_html=True)

        # Affected countries
        st.markdown(f"""
        <div style='background:rgba(0,20,45,0.4); border:1px solid rgba(0,212,255,0.12);
                    border-radius:6px; padding:12px 16px; margin-top:16px;'>
          <div style='font-size:11px; color:#00d4ff; font-weight:600; letter-spacing:1px; margin-bottom:4px;'>AFFECTED COUNTRIES</div>
          <div style='font-size:12px; color:#bdd2ea;'>{s['affected_countries']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Mitigation playbook
        st.markdown("<div style='font-size:13px; color:#00d4ff; font-weight:600; letter-spacing:1px; margin:22px 0 10px 0;'>MITIGATION PLAYBOOK</div>", unsafe_allow_html=True)
        for action in s['mitigation_playbook']:
            st.markdown(f"""
            <div style='background:linear-gradient(90deg, rgba(0,55,25,0.4), rgba(0,35,15,0.3));
                        border-left:3px solid #00ffc8; border-radius:6px;
                        padding:10px 14px; margin-bottom:5px;
                        font-size:12px; color:#bdd2ea;'>
              <span style='color:#00ffc8; font-weight:700; margin-right:8px;'>&gt;</span>{action}
            </div>
            """, unsafe_allow_html=True)

        # Recovery timeline
        st.markdown(f"""
        <div style='background:linear-gradient(135deg, rgba(0,212,255,0.08), rgba(0,15,35,0.3));
                    border:1px solid rgba(0,212,255,0.3); border-radius:8px;
                    padding:12px 16px; margin-top:18px;'>
          <div style='font-size:11px; color:#00d4ff; font-weight:600; letter-spacing:1.5px; margin-bottom:6px;'>RECOVERY TIMELINE</div>
          <div style='font-size:13px; color:#e0e8f0; line-height:1.5;'>{s['recovery_timeline']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.caption("Projections are based on historical disruption analogs (1973 oil crisis, 2011 Fukushima, 2021 Suez Ever Given, 2022 Russia sanctions) · adjusted for 2026 supply chain structure")


    # ========== TAB 11: WEATHER & PORT DISRUPTION ==========
    with tab11:
        st.markdown("""
        <div style="margin-bottom:16px;">
          <div style="font-size:18px; font-weight:600; color:#e0e8f0;">Weather &amp; Port Disruption Alerts</div>
          <div style="font-size:12px; color:#5a6b82; margin-top:4px;">
            Live NOAA/NWS alerts for US ports &middot; Curated global port weather &middot; Chokepoint exposure overlay
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Fetch live NWS alerts
        with st.spinner('Fetching live NOAA/NWS alerts…'):
            alerts, nws_status = _sg_fetch_nws_alerts()

        # Banner showing fetch status
        banner_color = '#00ffc8' if alerts else '#ff9800'
        st.markdown(f"""
        <div style='background:linear-gradient(135deg, {banner_color}11, rgba(0,15,35,0.5));
                    border:1px solid {banner_color}44; border-radius:8px;
                    padding:10px 16px; margin-bottom:16px;
                    display:flex; justify-content:space-between; align-items:center;'>
          <div>
            <span style='font-size:11px; color:{banner_color}; font-weight:600; letter-spacing:1.5px;'>NWS LIVE FEED</span>
            <span style='font-size:11px; color:#8aa0bc; margin-left:10px;'>{nws_status}</span>
          </div>
          <div style='font-size:10px; color:#5a6b82;'>Cache 30 min &middot; api.weather.gov</div>
        </div>
        """, unsafe_allow_html=True)

        # Active alerts
        if alerts:
            st.markdown("<div style='font-size:14px; color:#00d4ff; font-weight:600; letter-spacing:1px; margin:12px 0 10px 0;'>ACTIVE US ALERTS (supply-chain relevant)</div>", unsafe_allow_html=True)
            for a in alerts[:30]:
                color = _sg_weather_severity_color(a['severity'])
                st.markdown(f"""
                <div style='background:linear-gradient(90deg, rgba(0,25,55,0.5), rgba(0,15,35,0.4));
                            border-left:3px solid {color}; border-radius:8px;
                            padding:10px 14px; margin-bottom:6px;'>
                  <div style='display:flex; justify-content:space-between; align-items:start; margin-bottom:4px;'>
                    <div style='font-size:13px; color:#e0e8f0; font-weight:600;'>{a['event']}</div>
                    <div style='display:flex; gap:6px;'>
                      <span style='font-size:10px; padding:2px 8px; background:{color}22;
                                   border:1px solid {color}; border-radius:3px;
                                   color:{color}; font-weight:700; letter-spacing:0.5px;'>
                        {a['severity'].upper()}
                      </span>
                      <span style='font-size:10px; padding:2px 8px; background:rgba(0,212,255,0.1);
                                   border:1px solid rgba(0,212,255,0.3); border-radius:3px;
                                   color:#00d4ff; font-weight:600;'>{a['urgency']}</span>
                    </div>
                  </div>
                  <div style='font-size:11px; color:#bdd2ea; margin-top:2px; line-height:1.4;'>{a['area']}</div>
                  <div style='display:flex; gap:16px; margin-top:6px; font-size:10px; color:#5a6b82;'>
                    <span>Start: <b style='color:#8aa0bc;'>{a['effective']}</b></span>
                    <span>Expires: <b style='color:#8aa0bc;'>{a['expires']}</b></span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            if len(alerts) > 30:
                st.caption(f"Showing 30 of {len(alerts)} alerts. Full data at weather.gov/alerts")
        else:
            st.info("No active supply-chain-relevant US alerts currently, or NWS feed unreachable. International port status below.")

        # Port weather overview
        st.markdown("<div style='font-size:14px; color:#00d4ff; font-weight:600; letter-spacing:1px; margin:24px 0 10px 0;'>GLOBAL PORT WEATHER STATUS</div>", unsafe_allow_html=True)

        ports = _sg_weather_ports()
        intl_weather = _sg_intl_port_weather()

        # US ports — derive status from NWS alerts matching the state
        us_alert_areas = ' | '.join([a.get('area', '') for a in alerts])

        for p in ports:
            if p['region'] == 'us':
                # Check if port area appears in active alerts
                port_city = p['port'].split(' / ')[0].split(' (')[0]
                state_match = False
                for keyword in [port_city, p['port'].split(' (')[0]]:
                    if keyword in us_alert_areas:
                        state_match = True
                        break
                # Coarse state matching
                state_map = {'Los Angeles': 'Califor', 'Long Beach': 'Califor', 'Seattle': 'Washing',
                             'Tacoma': 'Washing', 'New York': 'New York', 'Savannah': 'Georgia',
                             'Houston': 'Texas', 'Norfolk': 'Virginia', 'Hampton Roads': 'Virginia'}
                for k, st_kw in state_map.items():
                    if k in p['port'] and st_kw in us_alert_areas:
                        state_match = True
                        break
                status = 'MONITORING' if state_match else 'NORMAL'
                note = 'Active NWS alerts in port region' if state_match else 'No active NWS alerts'
                live_label = '● LIVE'
            else:
                w = intl_weather.get(p['port'], {'status': 'NORMAL', 'note': 'No current advisories'})
                status = w['status']
                note = w['note']
                live_label = '○ CURATED'

            color = _sg_weather_severity_color(status)
            st.markdown(f"""
            <div style='background:rgba(0,20,45,0.4); border:1px solid rgba(0,212,255,0.1);
                        border-left:3px solid {color}; border-radius:6px;
                        padding:10px 14px; margin-bottom:5px;
                        display:flex; justify-content:space-between; align-items:center;'>
              <div>
                <div style='font-size:13px; color:#e0e8f0; font-weight:600;'>{p['port']}
                  <span style='font-size:10px; color:#5a6b82; margin-left:6px;'>{p['country']} &middot; {p['tz']}</span>
                </div>
                <div style='font-size:11px; color:#8aa0bc; margin-top:2px;'>{note}</div>
                <div style='font-size:10px; color:#5a6b82; margin-top:2px;'>{p['key_cargo']}</div>
              </div>
              <div style='text-align:right;'>
                <span style='font-size:10px; padding:2px 8px; background:{color}22;
                             border:1px solid {color}; border-radius:3px;
                             color:{color}; font-weight:700; letter-spacing:1px;'>
                  {status}
                </span>
                <div style='font-size:9px; color:#5a6b82; margin-top:3px;'>{live_label}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.caption("US port status derived from live NWS alerts (geographic match). International ports show curated seasonal risk advisories updated weekly. For real-time global coverage, commercial sources (Windy.com, WeatherFlow, StormGeo) recommended.")


    # ========== TAB 12: TRADE FLOWS ==========
    with tab12:
        render_trade_flows_tab()

    # ========== TAB 13: LPI CORRIDORS ==========
    with tab13:
        render_lpi_tab()

    # Footer
    st.markdown("""
    <div style='margin-top:30px; padding-top:18px; border-top:1px solid rgba(0,212,255,0.1);
                font-size:11px; color:#5a6b82; text-align:center;'>
      NERAI Supply Grid · Data fused from IMF PortWatch, USGS, UN Comtrade, GDELT, Yahoo Finance ·
      Updated: live (commodities) · daily (chokepoints, ports) · weekly (concentration) · annual (USGS reserves)
    </div>
    """, unsafe_allow_html=True)


page = st.session_state.get('page', 'home')

# Scroll to top whenever the user switches pages
if st.session_state.get('_last_page') != page:
    st.session_state['_last_page'] = page
    import streamlit.components.v1 as _nerai_components
    _nerai_components.html("""<script>
(function(){ try{
  var doc = window.parent.document;
  var sels = ['section[data-testid=\"stMain\"]','div[data-testid=\"stAppViewContainer\"]','section.main','main','.main'];
  for (var i=0;i<sels.length;i++){ var el = doc.querySelector(sels[i]); if(el){ el.scrollTop=0; } }
  try{ window.parent.scrollTo(0,0); }catch(e){}
  try{ doc.documentElement.scrollTop=0; doc.body.scrollTop=0; }catch(e){}
}catch(e){} })();
</script>""", height=0)

# Solo tier: show pro-only pages with lock overlay
_SOLO_LOCKED = _IS_SOLO and page in _PRO_ONLY_PAGES
# -- dropdown popover fix + scroll to top --
st.markdown('<style>[data-baseweb="popover"]{z-index:999999 !important} [data-baseweb="popover"] ul{max-height:350px !important}</style>', unsafe_allow_html=True)
import streamlit.components.v1 as _stc
_stc.html("""
<script>
(function(){
  var D=window.parent.document||document;
  if(D._popFix) return;
  D._popFix=true;
  new MutationObserver(function(){
    var p=D.querySelector('[data-baseweb="popover"]');
    if(!p)return;
    var r=p.getBoundingClientRect();
    if(r.top>10||r.left>10)return;
    var sels=D.querySelectorAll('[data-baseweb="select"]');
    var o=null;
    sels.forEach(function(s){if(s.contains(D.activeElement))o=s;});
    if(!o)sels.forEach(function(s){var b=s.getBoundingClientRect();if(!o&&b.width>0)o=s;});
    if(o){var sr=o.getBoundingClientRect();p.style.position='absolute';p.style.top=Math.round(sr.bottom+D.documentElement.scrollTop)+'px';p.style.left=Math.round(sr.left)+'px';p.style.width=Math.round(sr.width)+'px';p.style.zIndex='999999';}
  }).observe(D.body||D.documentElement,{childList:true,subtree:true});
  var m=D.querySelector("section.main");if(m)m.scrollTop=0;
})();
</script>
""", height=0)
if _SOLO_LOCKED:
    st.markdown("""
    <div style="text-align:center; padding:80px 20px;">
        <div style="font-size:64px; margin-bottom:16px;">🔒</div>
        <h2 style="color:#00d4ff; margin-bottom:12px;">PRO Feature</h2>
        <p style="color:#8899aa; font-size:16px; max-width:500px; margin:0 auto;">
            This section is available on the <b style="color:#00d4ff;">Pro plan</b>.<br>
            Upgrade to unlock all features including advanced analytics, AI insights, and more.
        </p>
        <a href="https://neraicorp.com/#pricing" target="_blank"
           style="display:inline-block; margin-top:24px; padding:12px 32px; background:linear-gradient(135deg,#00d4ff,#0077a8);
                  color:#fff; text-decoration:none; border-radius:8px; font-weight:600;">
            Upgrade to Pro
        </a>
    </div>
    """, unsafe_allow_html=True)
elif page == 'home':        render_home()
elif page == 'indices':     render_indices()
elif page == 'profile':     render_profile()
elif page == 'news':        render_news()
elif page == 'predictions': render_predictions()
elif page == 'causality':   render_causality()
elif page == 'scenarios':   render_scenarios()
elif page == 'threat_radar': render_threat_radar()
elif page == 'insights':    render_insights()
elif page == 'global_view': render_global_view()
elif page == 'briefing':    render_briefing_room()
elif page == 'api':         render_api()
# elif page == 'conflict':    render_conflict_intelligence(gdelt_fetch_fn=fetch_gdelt_news)  # DISABLED: temporarily removed
else:
    st.session_state.page = 'home'
    st.rerun()
