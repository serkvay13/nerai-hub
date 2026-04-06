"""
NERAI INTELLIGENCE HUB — Dashboard v3.0
Multi-page: Home | Indices | Country Profile | News
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
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
import nerai_premium_css

def _safe_pct(val, maxabs=150):
    """Cap percentage to +/-maxabs to prevent display of astronomical values."""
    if val is None or (isinstance(val, float) and (val != val)): return 0.0
    return max(-maxabs, min(maxabs, float(val)))

import urllib.request, urllib.parse

st.set_page_config(
    page_title="NERAI Intelligence Hub",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -- NERAI Premium CSS --
nerai_premium_css.inject_all()


# ===============================================================
# ACCESS GATE - Solo / Pro tier authentication
# ===============================================================
_VALID_CODES = {
    'NERAI-TRIAL-26': 'solo',
    'NERAI-PRO-26':  'pro',
    'NERAI-2026':    'pro',
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
all_topics  = sorted(df.index.get_level_values('topic').unique().tolist())
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
    ]
    # Solo tier: restrict to basic pages only
    _SOLO_PAGES = {'home', 'indices', 'profile', 'news', 'scenarios', 'threat_radar'}
    if _IS_SOLO:
        nav_pages = [(k, l) for k, l in nav_pages if k in _SOLO_PAGES]
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

    if st.button('🔄 Refresh Indices', use_container_width=True,
                 help='Run gdelt_indices.py to fetch latest GDELT data'):
        with st.spinner('Fetching GDELT data…'):
            r = subprocess.run([_sys.executable, './gdelt_indices.py'],
                               capture_output=True, text=True, cwd='.')
        if r.returncode == 0:
            st.success('✅ Indices updated!')
            st.cache_data.clear(); st.rerun()
        else:
            st.error(r.stderr[-600:] or 'Failed')

    _max_s = st.slider('Max Series (causality)', 50, 500, 200, 50,
                        help='Fewer = faster. 200 ≈ 5-8 min. 500 ≈ 30+ min.')
    if st.button('🕸 Run Causal Analysis', use_container_width=True,
                 help='Run gdelt_causality.py — top-variance series only'):
        with st.spinner(f'Computing causality for top {_max_s} series… (~5-8 min)'):
            r = subprocess.run(
                [_sys.executable, './gdelt_causality.py', '--max-series', str(_max_s)],
                capture_output=True, text=True, cwd='.')
        if r.returncode == 0:
            out = (r.stdout or '').strip()
            # Check if any edges were actually found
            if 'edges found' in out.lower() and '0 edges' in out.lower():
                st.warning('⚠️ 0 significant relationships found — threshold values may be too strict. Try again or increase Max Series.')
            else:
                st.success('✅ Causal network ready!')
            with st.expander('📋 Script output', expanded=False):
                st.code(out[-1200:] or '(no output)')
            st.cache_data.clear(); st.rerun()
        else:
            st.error('Script error:\n' + (r.stderr[-800:] or r.stdout[-400:] or 'Unknown error'))

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
    if st.session_state.page == 'indices':
        st.markdown('<div class="sec-hdr">Topic</div>', unsafe_allow_html=True)
        topic_display = {t: TOPIC_LABELS.get(t, t.replace('_',' ').title()) for t in all_topics}
        sel_label = st.selectbox("topic", list(topic_display.values()),
            index=list(topic_display.values()).index('Political Instability')
                  if 'Political Instability' in topic_display.values() else 0,
            label_visibility='collapsed')
        sel_topic = [k for k,v in topic_display.items() if v==sel_label][0]

        st.markdown('<div class="sec-hdr" style="margin-top:14px">Countries</div>', unsafe_allow_html=True)
        c_opts = [f"{COUNTRY_NAMES.get(c,c)} ({c})" for c in all_countries]
        defaults = ['United States (US)','Russia (RS)','China (CH)','Turkey (TU)','Iran (IR)','Ukraine (UP)']
        defaults = [d for d in defaults if d in c_opts][:4]
        sel_c_labels = st.multiselect("countries", c_opts, default=defaults, label_visibility='collapsed')
        sel_countries = [x.split('(')[-1].strip(')') for x in sel_c_labels]

        st.markdown('<div class="sec-hdr" style="margin-top:14px">Date Range</div>', unsafe_allow_html=True)
        n_days = st.slider("days", 14, min(180,len(date_cols)), 60, label_visibility='collapsed')

        st.markdown('<div class="sec-hdr" style="margin-top:14px">Map Date</div>', unsafe_allow_html=True)
        map_opts = [d.strftime('%Y-%m-%d') for d in date_cols[-30:]]
        map_date_str = st.selectbox("map", map_opts, index=len(map_opts)-1, label_visibility='collapsed')
        map_date = pd.Timestamp(map_date_str)

        heatmap_n = st.slider("Heatmap top N", 8, 30, 15)

        st.markdown(f"""
        <div style='margin-top:14px;padding:10px;background:rgba(0,150,255,0.05);
             border:1px solid rgba(0,150,255,0.1);border-radius:6px;
             font-size:0.62rem;color:rgba(0,180,255,0.4);font-family:monospace;line-height:2;'>
          <span class='live-dot'></span>LIVE DATA<br>
          📅 {len(date_cols)} days · 📊 {len(all_topics)} topics · {len(all_countries)} countries<br>
          {'⚠ DEMO MODE' if is_demo else '✓ GDELT Project'}
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sec-hdr" style="margin-top:18px">Normalization</div>', unsafe_allow_html=True)
        norm_method = st.radio("norm", ['Score (0–100)','Z-Score','Raw'],
            index=0, label_visibility='collapsed',
                help="Score 0–100: highest value in history=100 | Z-Score: deviation from mean | Raw: raw data")

    elif st.session_state.page == 'profile':
        st.markdown('<div class="sec-hdr">Country</div>', unsafe_allow_html=True)
        profile_c_opts = [f"{COUNTRY_NAMES.get(c,c)} ({c})" for c in sorted(all_countries)]
        profile_default = 'United States (US)' if 'United States (US)' in profile_c_opts else profile_c_opts[0]
        sel_profile_label = st.selectbox("profile_country", profile_c_opts,
            index=profile_c_opts.index(profile_default), label_visibility='collapsed')
        profile_country = sel_profile_label.split('(')[-1].strip(')')

        st.markdown('<div class="sec-hdr" style="margin-top:14px">Bilateral Analyzer</div>', unsafe_allow_html=True)
        c_opts_bi = [f"{COUNTRY_NAMES.get(c,c)} ({c})" for c in sorted(all_countries)]
        default_a = 'United States (US)' if 'United States (US)' in c_opts_bi else c_opts_bi[0]
        default_b = 'Russia (RS)'        if 'Russia (RS)'        in c_opts_bi else c_opts_bi[1]
        sel_bi_a = st.selectbox("Country A", c_opts_bi, index=c_opts_bi.index(default_a))
        bi_a = sel_bi_a.split('(')[-1].strip(')')
        sel_bi_b = st.selectbox("Country B", c_opts_bi, index=c_opts_bi.index(default_b))
        bi_b = sel_bi_b.split('(')[-1].strip(')')

        bi_days = st.slider("History (days)", 14, 90, 60)

    elif st.session_state.page == 'news':
        st.markdown('<div class="sec-hdr">Live News Feed</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style='padding:8px;background:rgba(0,150,255,0.05);
             border:1px solid rgba(0,150,255,0.1);border-radius:6px;
             font-size:0.62rem;color:rgba(0,180,255,0.4);font-family:monospace;'>
          <span class='live-dot'></span>GDELT Project<br>
          Real-time global news<br>
          28 topic categories
        </div>""", unsafe_allow_html=True)

    elif st.session_state.page == 'predictions':
        st.markdown('<div class="sec-hdr">Forecast Filters</div>', unsafe_allow_html=True)
        if has_predictions:
            topic_display_p = {t: TOPIC_LABELS.get(t, t.replace('_',' ').title())
                               for t in sorted(pred_df['topic'].dropna().unique()) if t}
            if topic_display_p:
                pred_label = st.selectbox(
                    "pred_topic", list(topic_display_p.values()),
                    index=list(topic_display_p.values()).index('Political Instability')
                          if 'Political Instability' in topic_display_p.values() else 0,
                    label_visibility='collapsed')
                sel_pred_topic = next((k for k,v in topic_display_p.items() if v==pred_label), list(topic_display_p.keys())[0])
            else:
                st.warning("No valid topic data in predictions yet.")
                sel_pred_topic = None
            
            st.markdown('<div class="sec-hdr" style="margin-top:14px">Country</div>',
                        unsafe_allow_html=True)
            pred_c_opts = [f"{COUNTRY_NAMES.get(c,c)} ({c})"
                           for c in sorted(pred_df['country'].unique())]
            pred_default = 'United States (US)' if 'United States (US)' in pred_c_opts \
                           else pred_c_opts[0]
            sel_pred_country_label = st.selectbox(
                "pred_country", pred_c_opts,
                index=pred_c_opts.index(pred_default),
                label_visibility='collapsed')
            sel_pred_country = sel_pred_country_label.split('(')[-1].strip(')')

            st.markdown('<div class="sec-hdr" style="margin-top:14px">History window</div>',
                        unsafe_allow_html=True)
            if _IS_PRO:
                pred_hist_months = st.slider("hist_months", 3, 60, 24,
                                             label_visibility='collapsed')
            else:
                pred_hist_months = 3
                st.markdown(
                    '<div style="font-size:11px;color:#e07b20;padding:4px 0;">'
                    '⚠️ Solo: Showing 3 months. '
                    'Upgrade to Pro for up to 60 months of history.</div>',
                    unsafe_allow_html=True)
        else:
            sel_pred_topic   = all_topics[0] if all_topics else ''
            sel_pred_country = 'US'
            pred_hist_months = 24

    # defaults for pages that don't set them
    if st.session_state.page not in ('indices',):
        sel_topic = all_topics[0] if all_topics else 'political_instability'
        sel_countries = ['US','RS','CH','TU']
        n_days = 60
        map_date = date_cols[-1] if len(date_cols) else pd.Timestamp.now()
        heatmap_n = 15
        norm_method = 'Score (0–100)'
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

# ═══════════════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════════════
def render_home():
    """Home page — Premium world-class hero + KPIs + module navigation."""

    # ── 1. HERO: AI + Geopolitical Network Visualization ──
    # (from nerai_premium_css.py — replaces old Three.js globe)
    nerai_premium_css.inject_home_hero()

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
                Live GDELT headlines across 28 topic categories.<br>
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
    # Data prep
    if sel_topic in df.index.get_level_values('topic'):
        df_topic_raw = df.xs(sel_topic, level='topic')
    else:
        df_topic_raw = df.groupby(level='country').mean()

    df_topic_raw  = df_topic_raw.reindex(columns=sorted(df_topic_raw.columns))
    df_recent_raw = df_topic_raw[date_cols[-n_days:]]
    df_norm       = apply_norm(df_topic_raw, norm_method)
    # Fill remaining zero-gaps after normalization
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
    norm_suffix   = {'Raw':'','Score (0–100)':' · Score 0–100','Z-Score':' · Z-Score'}[norm_method]
    sel_label     = TOPIC_LABELS.get(sel_topic, sel_topic.replace('_',' ').title())

    # Header — Premium
    nerai_premium_css.inject_page_header(
        title="Risk Matrix",
        subtitle="Topic-based geopolitical risk indices across 60 countries",
        badge="LIVE",
        icon="\U0001f4ca"
    )


    # KPI Cards
    kpi_countries = (sel_countries + all_countries)[:4]
    kpi_cols = st.columns(4)
    for col_el, c in zip(kpi_cols, kpi_countries):
        with col_el:
            if c in df_norm.index and len(df_norm.columns)>1:
                series = df_norm.loc[c]
                val    = series.iloc[-1]
                prev7  = series.iloc[-8] if len(series)>7 else series.iloc[0]
                delta  = val - prev7
                d_cls  = 'kpi-up' if delta>0 else ('kpi-down' if delta<0 else 'kpi-neu')
                d_sym  = '▲' if delta>0 else ('▼' if delta<0 else '●')
                badge  = risk_badge(val, norm_method)
                spark_color = '#e05060' if (norm_method=='Score (0–100)' and val>=60) else \
                              '#f59e0b' if (norm_method=='Score (0–100)' and val>=35) else '#00b4d8'
                st.markdown(f"""
                <div class='kpi-card' style='--accent:{spark_color};'>
                  <div class='kpi-label'>{COUNTRY_NAMES.get(c,c)}</div>
                  <div class='kpi-value'>{fmt(val,norm_method)}</div>
                  <div class='kpi-sub'>
                    <span class='{d_cls}'>{d_sym} {fmt(abs(delta),norm_method)} vs 7d</span>
                    &nbsp; {badge}
                  </div>
                </div>""", unsafe_allow_html=True)
                st.plotly_chart(chart_sparkline(series.iloc[-30:],spark_color),
                    use_container_width=True, config={'displayModeBar':False,'staticPlot':True})
            else:
                st.markdown(f"""
                <div class='kpi-card'><div class='kpi-label'>{COUNTRY_NAMES.get(c,c)}</div>
                <div class='kpi-value'>—</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="h-div" style="margin:4px 0 14px"></div>', unsafe_allow_html=True)


    # Data Table
    with st.expander("📊  Data Table — Selected Countries", expanded=False):
        if sel_countries:
            rows = []
            for c in sel_countries:
                if c in df_recent.index:
                    s = df_recent.loc[c]
                    rows.append({'Country':COUNTRY_NAMES.get(c,c),
                                 **{d.strftime('%d %b'):fmt(v,norm_method) for d,v in s.items()}})
            if rows:
                st.dataframe(pd.DataFrame(rows).set_index('Country'), use_container_width=True)
                # ── CSV Export — Pro only ──────────────────────────────
                if _IS_PRO:
                    _csv_bytes = pd.DataFrame(rows).to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label='⬇️  Download as CSV (Pro)',
                        data=_csv_bytes,
                        file_name=f'nerai_{sel_topic}_indices.csv',
                        mime='text/csv',
                        use_container_width=True,
                    )
                else:
                    st.markdown(
                        '<div style="font-size:11px;color:#e07b20;padding:5px 0;">'
                        'U0001f512 CSV download — <b>Pro</b> plan only.</div>',
                        unsafe_allow_html=True)


    # ── Heatmap ──────────────────────────────────────────────
    try:
        nerai_premium_css.inject_section_header("Risk Heatmap \u2014 Top Countries", icon="\U0001f5fa\ufe0f")
        _fig_hm = chart_heatmap(df_norm, heatmap_n, norm_method)
        if _fig_hm is not None:
            st.plotly_chart(_fig_hm, use_container_width=True)
    except Exception:
        pass

    # ── Global Risk Map ────────────────────────────────────────
    try:
        nerai_premium_css.inject_section_header("Global Risk Map", icon="\U0001f30d")
        _fig_wm = chart_world(df_norm, map_date)
        if _fig_wm is not None:
            st.plotly_chart(_fig_wm, use_container_width=True)
    except Exception:
        pass

    _render_footer()

# ═══════════════════════════════════════════════════════════════
# PAGE: COUNTRY PROFILE
# ═══════════════════════════════════════════════════════════════
def render_profile():
    nerai_premium_css.inject_page_header(
        title="Country Intel",
        subtitle="Deep-dive risk analysis, bilateral relations & alarm monitoring",
        badge="INTEL",
        icon="🌏"
    )

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

    # Page header
    st.markdown(f"""
    <div style='padding:6px 0 2px;'>
      <div class='hero-title'>Country Intelligence Profile</div>
      <div class='hero-sub'><span class='live-dot'></span>
        Deep-dive analysis &nbsp;·&nbsp; GDELT Data
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="h-div"></div>', unsafe_allow_html=True)

    # ── Profile Header ────────────────────────────────────────
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


    # === NEWS DYNAMIC BACKGROUND ===
    _topic_colors = {"conflict": "rgba(255,60,60,0.05)", "diplomacy": "rgba(0,200,255,0.05)", "economy": "rgba(0,255,150,0.05)", "politics": "rgba(180,100,255,0.05)", "environment": "rgba(100,255,100,0.05)", "health": "rgba(255,200,0,0.05)", "technology": "rgba(0,150,255,0.05)"}
    _cur_topic = st.session_state.get("news_topic", "").lower()
    _bg_col = _topic_colors.get(_cur_topic, "rgba(0,255,200,0.03)")
    st.markdown(f"<style>.main .block-container{{background:linear-gradient(180deg,{_bg_col},transparent)!important;}}</style>", unsafe_allow_html=True)
    st.markdown("""
    <div style='padding:6px 0 10px;'>
      <div class='hero-title'>Global News Intelligence</div>
      <div class='hero-sub'><span class='live-dot'></span>
        Live GDELT Headlines &nbsp;·&nbsp; 28 Topic Categories
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="h-div"></div>', unsafe_allow_html=True)

    cat_names  = [c[0] for c in NEWS_CATEGORIES]
    cat_queries = {c[0]: c[1] for c in NEWS_CATEGORIES}

    # Category selector + news
    left_col, right_col = st.columns([2, 5])

    with left_col:
        st.markdown('<div class="sec-hdr">Topics</div>', unsafe_allow_html=True)
        sel_cat = st.radio(
            "Category", cat_names,
            index=0, label_visibility='collapsed',
            key='news_cat'
        )

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

        with st.spinner(f'Fetching latest {sel_cat} news...'):
            articles = fetch_gdelt_news(cat_q, max_records=10)

        if articles:
            for art in articles:
                title    = art.get('title', 'No title')
                source   = art.get('domain', '')
                url      = art.get('url', '#')
                seendate = art.get('seendate', '')
                language = art.get('language', '')
                date_disp = seendate[:8] if len(seendate)>=8 else ''
                if date_disp:
                    try: date_disp = pd.Timestamp(date_disp).strftime('%d %b %Y')
                    except: pass

                st.markdown(f"""
                <div class="news-card">
                  <div class="news-title">
                    <a href="{url}" target="_blank"
                       style="color:#2a4060;text-decoration:none;">
                      {title[:180]}{'...' if len(title)>180 else ''}
                    </a>
                  </div>
                  <div style="display:flex;gap:14px;margin-top:6px;align-items:center;">
                    <div class="news-source">🌐 {source}</div>
                    <div class="news-date">📅 {date_disp}</div>
                    {'<div style="font-size:0.58rem;color:rgba(100,180,255,0.3);font-family:monospace;">LANG: '+language.upper()+'</div>' if language else ''}
                  </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align:center;padding:40px;
                 color:rgba(100,150,200,0.4);font-family:monospace;font-size:0.8rem;">
              <div style="font-size:2rem;margin-bottom:12px;">📡</div>
              No articles found for "{sel_cat}".<br>
              <span style="font-size:0.65rem;">GDELT API may be temporarily unavailable.</span>
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
        if trend_df is not None:
            country_trends = trend_df[trend_df['country'] == sel_pred_country].copy()
            country_trends['label'] = country_trends['topic'].apply(
                lambda t: TOPIC_LABELS.get(t, str(t).replace('_', ' ').title()) if pd.notna(t) else 'Unknown')
            country_trends = country_trends.sort_values('trend_pct', ascending=False)

            for _, row in country_trends.iterrows():
                pct   = row['trend_pct']
                dirn  = row['direction']
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
    """Comprehensive multi-paragraph Claude analysis for Insights Q&A."""
    import anthropic, os, datetime
    try:
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            return (
                '<div style="background:#1a0d0d;border:1px solid #8a3a3a;border-radius:8px;'
                'padding:14px;margin-top:14px;color:#ff9999;font-size:13px;">'
                '⚠️ <b>ANTHROPIC_API_KEY</b> Streamlit Cloud Secrets bölümünde tanımlı değil. '
                'Settings → Secrets kısmına ekleyin.</div>'
            )

        _pq = _parse_question(question)
        if isinstance(_pq, dict):
            country = _pq.get('country', '') or ''
            topic   = _pq.get('topic', '')   or ''
        elif isinstance(_pq, (list, tuple)) and len(_pq) >= 2:
            country = str(_pq[0]) if _pq[0] else ''
            topic   = str(_pq[1]) if _pq[1] else ''
        else:
            country = ''
            topic   = ''
        today_str = datetime.datetime.now().strftime('%d %B %Y')

        sections = []

        # ── 1. GDELT Risk Index Trends ──────────────────────────────
        if df_raw is not None and not df_raw.empty and country:
            try:
                ckey = 'country' if 'country' in df_raw.columns else None
                cdf  = df_raw[df_raw[ckey].str.lower() == country.lower()] if ckey else df_raw
                if not cdf.empty and 'y' in cdf.columns and 'ds' in cdf.columns:
                    cdf = cdf.sort_values('ds')
                    latest  = cdf['ds'].max()
                    wk_ago  = latest - __import__('pandas').Timedelta(days=7)
                    recent  = cdf[cdf['ds'] >= wk_ago]
                    older   = cdf[cdf['ds'] <  wk_ago]
                    if not recent.empty:
                        # Top rising topics
                        r_avg = recent.groupby('topic')['y'].mean() if 'topic' in recent.columns else recent[['y']].mean()
                        o_avg = older.groupby('topic')['y'].mean()  if 'topic' in older.columns  else older[['y']].mean()
                        changes = {}
                        for t in r_avg.index:
                            if t in o_avg.index and o_avg[t] > 0:
                                changes[t] = round((r_avg[t] - o_avg[t]) / o_avg[t] * 100, 1)
                        if changes:
                            s_asc  = sorted(changes.items(), key=lambda x: x[1])
                            rising = [(t,v) for t,v in s_asc if v > 0][-5:][::-1]
                            fall   = [(t,v) for t,v in s_asc if v < 0][:3]
                            lines  = [f"  ↑ {t}: +{v}%" for t,v in rising]
                            if fall: lines += [f"  ↓ {t}: {v}%" for t,v in fall]
                            sections.append("GDELT Risk Endeksi Değişimleri - " + country + " (7 gün):\n" + "\n".join(lines))
            except Exception:
                pass

        # ── 2. Forward Forecasts ────────────────────────────────────
        if pred_df is not None and not pred_df.empty and country:
            try:
                import pandas as _pd
                ckey = 'country' if 'country' in pred_df.columns else None
                pdf  = pred_df[pred_df[ckey].str.lower() == country.lower()] if ckey else pred_df
                if not pdf.empty and 'yhat' in pdf.columns and 'ds' in pdf.columns:
                    future = pdf[pdf['ds'] > _pd.Timestamp.now()].head(60)
                    if not future.empty:
                        if 'topic' in future.columns:
                            fc_avg = future.groupby('topic')['yhat'].mean().sort_values(ascending=False).head(5)
                            lines  = [f"  {t}: {v:.1f}" for t,v in fc_avg.items()]
                        else:
                            lines = [f"  Ortalama tahmin: {future['yhat'].mean():.1f}"]
                        sections.append("30 Günlük Tahminler - " + country + ":\n" + "\n".join(lines))
            except Exception:
                pass

        # ── 3. News driving index changes ───────────────────────────
        if insights_df is not None and not insights_df.empty:
            try:
                news_cols = [c for c in ['title','headline','text','event'] if c in insights_df.columns]
                date_col  = next((c for c in ['date','published','ds'] if c in insights_df.columns), None)
                topic_col = next((c for c in ['topic','category'] if c in insights_df.columns), None)
                ctry_col  = next((c for c in ['country','geo'] if c in insights_df.columns), None)
                if news_cols:
                    nc = news_cols[0]
                    df2 = insights_df
                    if country and ctry_col:
                        mask = df2[ctry_col].str.lower().str.contains(country.lower(), na=False)
                        df2  = df2[mask] if mask.any() else insights_df
                    if topic and topic_col:
                        mask2 = df2[topic_col].str.lower().str.contains(topic.lower(), na=False)
                        if mask2.any(): df2 = df2[mask2]
                    top = df2.head(6)
                    items = []
                    for _, row in top.iterrows():
                        s = str(row[nc])[:120]
                        if date_col and row.get(date_col): s = '[' + str(row[date_col])[:10] + '] ' + s
                        if topic_col and row.get(topic_col): s += ' (' + str(row[topic_col]) + ')'
                        items.append('  • ' + s)
                    if items:
                        sections.append("Related News:\n" + "\n".join(items))
            except Exception:
                pass

        if not sections:
            sections.append("Note: Insufficient structured data for this query; a general analysis will be provided.")

        context = "\n\n".join(sections)

        prompt = (
            "You are a senior geopolitical risk analyst for the NERAI Intelligence Platform. "
            "Today's date: " + today_str + ".\n\n"
                "Below is real-time data from the GDELT (Global Database of Events, Language and Tone) platform:\n\n"

            + context +
            "\n\nUSER QUESTION: " + question + "\n\n"
                "Please analyze this question in 3-4 paragraphs within the following framework:\n"
                "1) Current situation \u2014 Risk indices and recent trends based on GDELT data\n"
                "2) Key developments \u2014 Events and news driving changes in the indices\n"
                "3) Forecasts \u2014 Expected trajectory based on model predictions\n"
                "4) Strategic assessment \u2014 Implications for the overall geopolitical landscape\n\n"
            "Base your analysis strictly on the provided GDELT data. Do not use Markdown, write plain paragraphs. "
            "Respond in English."
        )

        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=900,
            messages=[{'role': 'user', 'content': prompt}]
        )
        narrative = msg.content[0].text.strip()

        return (
            '<div style="background:linear-gradient(135deg,#0d1e38,#0a1628);'
            'border:1px solid #2a5080;border-radius:12px;padding:20px;margin-top:16px;">'
            '<div style="color:#5ba3f5;font-size:11px;font-weight:700;letter-spacing:2px;'
            'margin-bottom:14px;">🤖 AI ANALYSIS — GDELT-BASED ASSESSMENT</div>'
            '<div style="color:#c8d8f0;font-size:14px;line-height:1.85;white-space:pre-wrap;">'
            + narrative +
            '</div>'
            '<div style="color:#3a5a7a;font-size:10px;margin-top:14px;border-top:1px solid #1a3a5a;'
            'padding-top:8px;">GDELT realtime · claude-haiku-4-5 · ' + today_str + '</div>'
            '</div>'
        )
    except Exception as _e:
        return (
            '<div style="background:#1a0808;border:1px solid #8a2a2a;border-radius:8px;'
            'padding:12px;margin-top:12px;color:#ff9999;font-size:12px;">'
            '⚠️ AI analysis error: ' + str(_e)[:300] + '</div>'
        )


def render_insights():
    nerai_premium_css.inject_page_header(
        title="AI Insights",
        subtitle="Machine-generated intelligence briefings & natural language Q&A",
        badge="AI",
        icon="🧠"
    )

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
        _render_footer()
        return

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
        .force("link", d3.forceLink(edges).id(d=>d.id).distance(160))
        .force("charge", d3.forceManyBody().strength(-400))
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
        st.dataframe(
            display_df[['source_label', 'target_label', 'max_f_stat', 'min_p_value', 'best_lag']].rename(
                columns={'source_label': 'Source', 'target_label': 'Target',
                         'max_f_stat': 'F-Stat', 'min_p_value': 'p-value', 'best_lag': 'Lag (m)'}),
            use_container_width=True
        )


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


def _generate_weekly_pdf():
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


def _generate_risk_pdf():
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
def render_briefing_room():
    nerai_premium_css.inject_page_header(
        title="Briefing Room",
        subtitle="Automated intelligence reports & downloadable risk assessments",
        badge="REPORTS",
        icon="📋"
    )

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
            "<div style='font-size:0.75rem;color:#8aa8c8;'>Week 14 | March 28 - April 4, 2026</div></div>"
            "</div>"
            "<div style='display:inline-block;background:#ffd700;color:#000;padding:3px 10px;"
            "border-radius:3px;font-weight:700;font-size:0.7rem;letter-spacing:0.05em;'>UNCLASSIFIED</div>"
            "</div>", unsafe_allow_html=True)

        with st.expander("Read Full Bulletin", expanded=False):
            st.markdown(_weekly_bulletin_html(), unsafe_allow_html=True)

        st.download_button(
            label="\u2B07 Download PDF",
            data=_generate_weekly_pdf(),
            file_name="NERAI_Weekly_Bulletin_W14.pdf",
            mime="application/pdf",
            use_container_width=True)

    with col2:
        st.markdown(
            "<div style='background:rgba(10,20,40,0.6);border:1px solid rgba(255,75,110,0.3);"
            "border-radius:10px;padding:20px;margin-bottom:14px;'>"
            "<div style='display:flex;align-items:center;gap:10px;margin-bottom:12px;'>"
            "<div style='font-size:1.8rem;'>&#9888;</div>"
            "<div><div style='font-size:1.05rem;font-weight:700;color:#ff4b6e;'>NERAI Risk Alert</div>"
            "<div style='font-size:0.75rem;color:#8aa8c8;'>Critical Threat Assessment | April 2026</div></div>"
            "</div>"
            "<div style='display:inline-block;background:#ff4b6e;color:#fff;padding:3px 10px;"
            "border-radius:3px;font-weight:700;font-size:0.7rem;letter-spacing:0.05em;'>SEVERITY: CRITICAL</div>"
            "</div>", unsafe_allow_html=True)

        with st.expander("Read Full Alert", expanded=False):
            st.markdown(_risk_alert_html(), unsafe_allow_html=True)

        st.download_button(
            label="\u2B07 Download PDF",
            data=_generate_risk_pdf(),
            file_name="NERAI_Risk_Alert_Apr2026.pdf",
            mime="application/pdf",
            use_container_width=True)

    st.markdown(
        "<div style='margin-top:30px;padding:14px 20px;background:rgba(10,20,40,0.4);"
        "border:1px solid rgba(0,180,255,0.15);border-radius:8px;text-align:center;"
        "color:#8aa8c8;font-size:0.8rem;line-height:1.6;'>"
        "All analyses produced by NERAI Intelligence using proprietary indices, predictive models "
        "and causal network analysis. Reports updated weekly."
        "</div>", unsafe_allow_html=True)


def _weekly_bulletin_html():
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


def _risk_alert_html():
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
    """Return (p1_html, p2_html) plain-English analysis of a scenario result."""
    val_cols = [c for c in result_df.columns if c not in ('scenario', 'series_id', 'topic', 'country')]
    if not val_cols or result_df.empty:
        return None, None

    val_col = val_cols[0]
    sid_col = 'series_id' if 'series_id' in result_df.columns else result_df.index.name or 'index'
    if sid_col == 'index':
        impacts = result_df[val_col]
        ids     = result_df.index.astype(str)
    else:
        impacts = result_df.set_index(sid_col)[val_col]
        ids     = impacts.index

    max_impact  = float(impacts.abs().max())
    avg_impact  = float(impacts.abs().mean())
    top_hit     = impacts.abs().idxmax() if not impacts.empty else None
    direction   = "upward" if float(impacts.mean()) >= 0 else "downward"
    n_elevated  = int((impacts.abs() > avg_impact).sum())
    n_total     = len(impacts)
    breadth     = "concentrated in a small cluster of series" if n_elevated < n_total / 2 else "broad across the monitored universe"

    sel_result_str = str(sel_result) if sel_result is not None else ''
    scenario_label = SCENARIO_TEMPLATES.get(sel_result_str, {}).get('label', sel_result_str.replace('_', ' ').title())

    p1 = (
        f"Under the <b>{scenario_label}</b> simulation, the model projects a "
        f"<b>{'widespread' if n_elevated >= n_total/2 else 'localised'} {direction} pressure</b> "
        f"across the affected risk series, with an average absolute deviation of "
        f"<b>{avg_impact:.4f} index points</b> from baseline forecasts. "
    )
    if top_hit is not None:
        lbl, cc = _node_label(str(top_hit))
        p1 += (
            f"The most severely impacted series is <b>{lbl}</b> "
            f"({COUNTRY_NAMES.get(cc, cc)}), which registers a peak deviation of "
            f"<b>{max_impact:.4f}</b> — roughly "
            f"{'moderate' if max_impact < 0.1 else 'substantial' if max_impact < 0.3 else 'severe'}. "
            f"In total, <b>{n_elevated} of {n_total}</b> monitored series show above-average exposure to this shock, "
            f"meaning the impact is {breadth}."
        )

    p2 = (
        f"From a risk-intelligence perspective, this pattern suggests that the shock "
        f"{'concentrates risk within a limited geographic or thematic cluster, limiting direct contagion but potentially creating a pressure-cooker effect in those areas' if n_elevated < n_total/2 else 'spreads risk broadly, increasing the probability of multi-front instability and cross-domain contagion'}. "
        f"Elevated readings in geopolitical indices of this magnitude are historically associated with "
        f"increased media attention, diplomatic activity, and in severe cases, market repricing of "
        f"sovereign risk in the affected region. "
        f"These projections are generated by ARIMA re-forecasting on GDELT-derived event indices — "
        f"they represent statistically plausible directional shifts, not deterministic point forecasts. "
        f"For a fuller picture of downstream exposure, visit the <b>Causal Network</b> tab: "
        f"series that are statistically caused by the shocked origin will appear as direct descendants "
        f"in the network graph and are the most likely vectors of second-order propagation."
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

    import subprocess, sys as _sys
    st.markdown('<div class="h-div" style="margin:24px 0;"></div>', unsafe_allow_html=True)

    # ── Run Pre-Built Scenario ──────────────────────────────────
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
                impact_df = impact_df.nlargest(40, 'abs').sort_values('val', ascending=False)
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
                    title=dict(text=f'Top 40 Most Impacted Series — {scen_lbl}',
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
                  Only the 40 most impacted series are shown, sorted by impact magnitude.
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

            # Raw data table (collapsible)
            with st.expander("🔢 Raw Results Table", expanded=False):
                st.dataframe(result_df, use_container_width=True)


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

    _render_footer()


page = st.session_state.get('page', 'home')

# Solo tier: block access to pro-only pages
if _IS_SOLO and page not in ('home', 'indices', 'profile', 'news', 'scenarios', 'threat_radar'):
    st.session_state.page = 'home'
    page = 'home'
    st.warning('\u26a0\ufe0f This feature is available on the Pro plan. Upgrade at neraicorp.com/pricing')
if   page == 'home':        render_home()
elif page == 'indices':     render_indices()
elif page == 'profile':     render_profile()
elif page == 'news':        render_news()
elif page == 'predictions': render_predictions()
elif page == 'causality':   render_causality()
elif page == 'scenarios':   render_scenarios()
elif page == 'threat_radar': render_threat_radar()
elif page == 'insights':    render_insights()
elif page == 'briefing':    render_briefing_room()
elif page == 'api':         render_api()
else:
    st.session_state.page = 'home'
    st.rerun()
