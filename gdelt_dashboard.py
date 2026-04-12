"""
NERAI INTELLIGENCE HUB — Dashboard v3.0
Multi-page: Home | Indices | Country Profile | News
"""
import streamlit as st
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
}

# Time-limited access codes  {code: expiry_date}
from datetime import datetime as _dt
_TIMED_CODES = {
    'NERAI-SOLO-26': _dt(2026, 4, 14),   # expires 14 April 2026
    'NERAI-PRO-DEMO': _dt(2026, 4, 19),   # 1-week Pro trial, expires 19 April 2026
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
        if val>=