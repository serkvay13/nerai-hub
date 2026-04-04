"""
NERAI INTELLIGENCE HUB — Dashboard v3.0
Multi-page: Home | Indices | Country Profile | News
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime, os, json
import re
import streamlit.components.v1 as _stc

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


# ===============================================================
# ACCESS GATE - Solo / Pro tier authentication
# ===============================================================
_VALID_CODES = {
    'NERAI-SOLO-26': 'solo',
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
#MainMenu, footer, .stDeployButton { display:none !important; }

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
        # Interpolate gap periods: values below 5% of row median are treated as missing GDELT data
        date_cols = [c for c in df.columns if c not in ['topic', 'country']]
        if date_cols:
            for idx in df.index:
                row = df.loc[idx, date_cols]
                nonzero = row[row > 0]
                if len(nonzero) > 0:
                    thr = nonzero.median() * 0.05
                    df.loc[idx, date_cols] = row.where(row > thr, np.nan)
                else:
                    df.loc[idx, date_cols] = row.replace(0, np.nan)
            df[date_cols] = df[date_cols].interpolate(axis=1, method='linear', limit_direction='both')
            df[date_cols] = df[date_cols].ffill(axis=1).bfill(axis=1)
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
        fig.add_hline(y=-2,line_dash='dot',line_color='rgba(0,212,170,0.4)',
                      annotation_text='-2σ',annotation_font_size=9)
    t = {**BASE_THEME}
    t['yaxis'] = {**t['yaxis'],'title':y_label,'title_font':dict(size=10)}
    fig.update_layout(**t, height=340,
        title=dict(text=title,font=dict(size=12,color='#0077a8'),x=0.01),
        legend=dict(bgcolor='rgba(255,255,255,0.85)',bordercolor='rgba(0,119,168,0.25)',
                    borderwidth=1,font=dict(size=10,color='#0d1f3c')),
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
        [[0,'#0d3464'],[0.25,'#00b4d8'],
         [0.5,'#0077a8'],[0.75,'#f59e0b'],[1,'#e05060']]
        if method!='Z-Score' else
        [[0,'#00d4aa'],[0.35,'#0d3464'],
         [0.5,'#f4f7fb'],[0.65,'#f59e0b'],[1,'#e05060']]
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
    t['yaxis'] = dict(tickfont=dict(size=9,color='#0d1f3c'),gridcolor='rgba(0,0,0,0)')
    fig.update_layout(**t,height=420,
        title=dict(text=f'Top {top_n} Countries — Heatmap',
                   font=dict(size=12,color='#0077a8'),x=0.01))
    return fig

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
    fig.update_layout(**t,height=330,
        title=dict(text=f'Global Risk Map — {pd.Timestamp(date_col).strftime("%d %b %Y")}',
                   font=dict(size=12,color='#0077a8'),x=0.01),
        geo=dict(bgcolor='rgba(0,0,0,0)',showframe=False,showcoastlines=True,
                 coastlinecolor='rgba(0,119,168,0.3)',showland=True,
                 landcolor='#0d3464',showocean=True,
                 oceancolor='#f4f7fb',showlakes=False,
                 projection_type='natural earth'))
    return fig

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
    t['yaxis'] = dict(tickfont=dict(size=10,color='#0d1f3c'),gridcolor='rgba(0,0,0,0)')
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
                {'range':[0,25],'color':'rgba(0,212,170,0.10)'},
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
    else:               st_,col_,ico = 'COOPERATIVE','#00d4aa','🤝'
    if   trend_7d> 5: tr_txt,tr_col = '▲ DETERIORATING','#e06030'
    elif trend_7d> 1: tr_txt,tr_col = '↗ WORSENING',    '#f59e0b'
    elif trend_7d<-5: tr_txt,tr_col = '▼ IMPROVING',    '#00d4aa'
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
all_topics  = sorted(df.index.get_level_values('topic').unique().tolist())
all_countries = sorted(df.index.get_level_values('country').unique().tolist())

tension_norm, coop_norm = compute_bilateral_base(df)
deteri_norm, incr_norm  = _get_bilateral_specific_norm(df)

# ── Load pre-computed predictions (if available) ─────────────
@st.cache_data(ttl=3600)
def load_predictions():
    pred_file   = './predictions.csv'
    trend_file  = './forecast_trends.csv'
    preds, trends = None, None
    if os.path.exists(pred_file):
        try:
            preds = pd.read_csv(pred_file, parse_dates=['ds'])
            # --- Normalize raw event counts to 0-100 per topic+country ---
            if preds is not None and 'yhat' in preds.columns and len(preds) > 0:
                for tc_cols in [['topic', 'country']]:
                    if all(c in preds.columns for c in tc_cols):
                        grp_min = preds.groupby(tc_cols)['yhat'].transform('min')
                        grp_max = preds.groupby(tc_cols)['yhat'].transform('max')
                        grp_range = grp_max - grp_min
                        for col in ['yhat', 'yhat_lower', 'yhat_upper']:
                            if col in preds.columns:
                                preds[col] = np.where(grp_range > 0, (preds[col] - grp_min) / grp_range * 100, 50).clip(0, 120)
                        break
        except Exception:
            preds = None
    if os.path.exists(trend_file):
        try:
            trends = pd.read_csv(trend_file)
            # Validate: drop rows with NaN topic or country (bad data from old script runs)
            if trends is not None and 'topic' in trends.columns and 'country' in trends.columns:
                trends = trends.dropna(subset=['topic', 'country'])
                trends['topic']   = trends['topic'].astype(str).str.strip()
                trends['country'] = trends['country'].astype(str).str.strip()
                # Filter out rows where topic/country look invalid (single chars or empty)
                trends = trends[trends['topic'].str.len() > 2]
                trends = trends[trends['country'].str.len() >= 2]
                if len(trends) == 0:
                    trends = None
        except Exception:
            trends = None
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
        <text x='50' y='36' font-family='Inter,sans-serif' font-weight='800' font-size='30' fill='#e0e8f0' letter-spacing='-1'>NER</text>
        <!-- AI text (cyan) -->
        <text x='118' y='36' font-family='Inter,sans-serif' font-weight='800' font-size='30' fill='#00d4ff' letter-spacing='-1'>AI</text>
      </svg>
      <div style='color:#5a6b82;font-size:10px;letter-spacing:2px;margin-top:4px;text-transform:uppercase;'>Intelligence Hub</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Navigation ──────────────────────────────────────────
    st.markdown('<div class="sec-hdr">Navigation</div>', unsafe_allow_html=True)

    nav_pages = [
        ('home',        '🏠  HOME'),
        ('indices',     '📊  INDICES'),
        ('profile',     '🎯  COUNTRY PROFILE'),
        ('news',        '📰  NEWS'),
        ('predictions', '🔮  PREDICTIONS'),
        ('causality',   '🕸  CAUSAL NETWORK'),
        ('scenarios',   '⚡  WHAT-IF SCENARIOS'),
        ('insights',    '🔍  INSIGHTS'),
    ]
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
                st.warning('⚠️ 0 anlamlı ilişki bulundu — eşik değerleri çok katı olabilir. Tekrar dene veya Max Series artır.')
            else:
                st.success('✅ Causal network ready!')
            with st.expander('📋 Script çıktısı', expanded=False):
                st.code(out[-1200:] or '(çıktı yok)')
            st.cache_data.clear(); st.rerun()
        else:
            st.error('Script hatası:\n' + (r.stderr[-800:] or r.stdout[-400:] or 'Bilinmeyen hata'))

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
            help="Score 0–100: tarihin en yüksek değeri=100 | Z-Score: ortalamadan sapma | Raw: ham veri")

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
                    '⚠️ Solo: 3 ay görüntülüyor. '
                    'Pro ile 60 aya kadar geçmişe gidin.</div>',
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
    if st.session_state.page not in ('predictions',):
        sel_pred_topic   = all_topics[0] if all_topics else ''
        sel_pred_country = 'US'
        pred_hist_months = 24

# ═══════════════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════════════
def render_home():
    # ── Animated Hero ────────────────────────────────────────

    # === 3D GLOBE ===
    _globe_html = (
        '<div style="background:#0a0e1a;border-radius:12px;padding:0;margin-bottom:1rem;">'
        '<canvas id="nglobe" width="700" height="500" style="display:block;margin:auto;"></canvas>'
        '<script>'
        '(function(){'
        'var cv=document.getElementById("nglobe");if(!cv)return;'
        'var c=cv.getContext("2d"),W=cv.width,H=cv.height,cx=W/2,cy=H/2,R=180;'
        'var t=0,stars=[];for(var i=0;i<200;i++)stars.push([Math.random()*W,Math.random()*H,Math.random()*1.5+0.5]);'
        'var cities=[[51.5,-0.1,"London"],[40.7,-74,"NYC"],[35.7,139.7,"Tokyo"],[39.9,116.4,"Beijing"],[-33.9,151.2,"Sydney"],[55.8,37.6,"Moscow"],[28.6,77.2,"Delhi"]];'
        'var arcs=[[0,1],[1,3],[3,4],[2,5],[5,6],[6,0],[2,4]];'
        'function proj(lat,lon){var la=lat*Math.PI/180,lo=lon*Math.PI/180+t*0.003;var x=Math.cos(la)*Math.sin(lo),y=Math.sin(la),z=Math.cos(la)*Math.cos(lo);return z>-0.1?[cx+x*R,cy-y*R,z]:null;}'
        'function draw(){c.fillStyle="#0a0e1a";c.fillRect(0,0,W,H);'
        'for(var i=0;i<stars.length;i++){var s=stars[i];var b=0.5+0.5*Math.sin(t*0.02+i);c.fillStyle="rgba(255,255,255,"+b+")";c.beginPath();c.arc(s[0],s[1],s[2],0,6.28);c.fill();}'
        'c.strokeStyle="rgba(0,255,255,0.08)";c.lineWidth=0.5;'
        'for(var la=-80;la<=80;la+=20){c.beginPath();for(var lo=0;lo<=360;lo+=5){var p=proj(la,lo);if(p){if(lo==0)c.moveTo(p[0],p[1]);else c.lineTo(p[0],p[1]);}}c.stroke();}'
        'for(var lo=0;lo<360;lo+=30){c.beginPath();for(var la=-90;la<=90;la+=5){var p=proj(la,lo);if(p){if(la==-90)c.moveTo(p[0],p[1]);else c.lineTo(p[0],p[1]);}}c.stroke();}'
        'var sw=t*0.5%360;c.fillStyle="rgba(0,255,200,0.04)";c.beginPath();c.moveTo(cx,cy);'
        'for(var a=sw;a<sw+40;a+=2){var p=proj(0,a);if(p)c.lineTo(p[0],p[1]);}c.closePath();c.fill();'
        'for(var i=0;i<arcs.length;i++){var a=arcs[i],c1=cities[a[0]],c2=cities[a[1]];var p1=proj(c1[0],c1[1]),p2=proj(c2[0],c2[1]);'
        'if(p1&&p2){var phase=(t*0.02+i)%1;c.strokeStyle="rgba(0,200,255,"+(0.3+0.3*Math.sin(t*0.05+i))+")";c.lineWidth=1.5;c.beginPath();'
        'var mx=(p1[0]+p2[0])/2,my=(p1[1]+p2[1])/2-30;c.moveTo(p1[0],p1[1]);c.quadraticCurveTo(mx,my,p2[0],p2[1]);c.stroke();}}'
        'for(var i=0;i<cities.length;i++){var ci=cities[i],p=proj(ci[0],ci[1]);'
        'if(p){c.fillStyle="rgba(0,255,200,"+(0.6+0.4*Math.sin(t*0.03+i))+")";c.beginPath();c.arc(p[0],p[1],3+Math.sin(t*0.05+i),0,6.28);c.fill();'
        'c.fillStyle="rgba(200,255,255,0.7)";c.font="9px monospace";c.fillText(ci[2],p[0]+6,p[1]-4);}}'
        'c.fillStyle="rgba(0,255,200,0.06)";c.beginPath();c.arc(cx,cy,R,0,6.28);c.fill();'
        'c.strokeStyle="rgba(0,255,255,0.15)";c.lineWidth=1;c.beginPath();c.arc(cx,cy,R,0,6.28);c.stroke();'
        'c.strokeStyle="rgba(0,255,200,0.08)";c.lineWidth=0.5;c.beginPath();c.arc(cx,cy,R+20+5*Math.sin(t*0.02),0,6.28);c.stroke();'
        'c.fillStyle="rgba(0,255,200,0.5)";c.font="bold 11px monospace";c.fillText("NERAI GLOBAL INTELLIGENCE",cx-100,30);'
        'c.font="9px monospace";c.fillStyle="rgba(0,200,255,0.4)";c.fillText("NODES: "+cities.length+" | LINKS: "+arcs.length+" | STATUS: ACTIVE",cx-120,H-15);'
        't++;requestAnimationFrame(draw);}'
        'draw();'
        '})();'
        '</script></div>'
    )
    _stc.html(_globe_html, height=510, scrolling=False)
    st.markdown(f"""
    <div class="home-hero">
      <!-- Corner HUD brackets -->
      <div class="home-corner home-corner-tl"></div>
      <div class="home-corner home-corner-tr"></div>
      <div class="home-corner home-corner-bl"></div>
      <div class="home-corner home-corner-br"></div>
      <!-- Glowing orbs -->
      <div class="home-orb" style="width:320px;height:320px;top:-100px;left:-80px;background:rgba(0,70,200,0.13);"></div>
      <div class="home-orb" style="width:260px;height:260px;top:-60px;right:-60px;background:rgba(80,0,180,0.10);"></div>
      <div class="home-orb" style="width:220px;height:220px;bottom:-70px;left:50%;transform:translateX(-50%);background:rgba(0,120,230,0.09);"></div>
      <!-- Floating hexagons -->
      <div class="hex-deco" style="width:70px;height:80px;top:12%;left:4%;animation-delay:0s;"></div>
      <div class="hex-deco" style="width:55px;height:63px;top:18%;right:6%;animation-delay:3s;"></div>
      <div class="hex-deco" style="width:45px;height:52px;bottom:18%;left:10%;animation-delay:6s;opacity:0.6;"></div>
      <div class="hex-deco" style="width:40px;height:46px;bottom:22%;right:9%;animation-delay:1.5s;opacity:0.5;"></div>
      <!-- Main content -->
      <div style="position:relative;z-index:2;padding:12px 0;">
        <!-- CSS Text Logo -->
        <div class="nerai-logo-wrap">
          <div class="nerai-logo-ring"></div>
          <div class="nerai-logo-ring nerai-logo-ring-2"></div>
          <div class="nerai-logo-brand">
            <span class="nerai-logo-hex">◈</span>
            <span class="nerai-logo-ner">NER</span><span class="nerai-logo-ai">AI</span>
          </div>
        </div>
        <!-- Sub-brand line -->
        <div style="font-size:0.65rem;letter-spacing:0.35em;text-transform:uppercase;
             color:rgba(0,200,255,0.4);font-family:'Share Tech Mono',monospace;
             margin-bottom:6px;">Intelligence Hub</div>
        <div class="hero-tagline">Geopolitical Risk Intelligence Platform</div>
        <!-- Separator -->
        <div style="height:1px;background:linear-gradient(90deg,transparent,rgba(0,200,255,0.4),rgba(123,47,255,0.3),transparent);
             width:60%;margin:0 auto 30px;"></div>
        <!-- Stats row -->
        <div class="home-stat-row">
          <div class="home-stat">
            <div class="home-stat-val">{len(all_countries)}</div>
            <div class="home-stat-lbl">Countries</div>
          </div>
          <div style="width:1px;background:rgba(0,150,255,0.15);align-self:stretch;"></div>
          <div class="home-stat">
            <div class="home-stat-val">{len(all_topics)}</div>
            <div class="home-stat-lbl">Risk Topics</div>
          </div>
          <div style="width:1px;background:rgba(0,150,255,0.15);align-self:stretch;"></div>
          <div class="home-stat">
            <div class="home-stat-val">{len(date_cols)}</div>
            <div class="home-stat-lbl">Days of Data</div>
          </div>
          <div style="width:1px;background:rgba(0,150,255,0.15);align-self:stretch;"></div>
          <div class="home-stat">
            <div class="home-stat-val">{len(df):,}</div>
            <div class="home-stat-lbl">Data Points</div>
          </div>
        </div>
        <!-- Live status bar -->
        <div style="display:inline-flex;align-items:center;gap:12px;
             background:rgba(0,20,50,0.6);border:1px solid rgba(0,150,255,0.2);
             border-radius:20px;padding:5px 18px;
             font-size:0.68rem;color:rgba(0,200,255,0.6);
             font-family:'Share Tech Mono',monospace;letter-spacing:0.1em;">
          <span class="live-dot"></span>
          <span>LIVE</span>
          <span style="color:rgba(0,150,255,0.3);">|</span>
          <span>GDELT PROJECT</span>
          <span style="color:rgba(0,150,255,0.3);">|</span>
          <span>LAST UPDATE: {date_cols[-1].strftime('%d %b %Y') if len(date_cols) else 'N/A'}</span>
          <span style="color:rgba(0,150,255,0.3);">|</span>
          <span style="color:{'#ffaa00' if is_demo else '#00d4aa'};">{'⚠ DEMO' if is_demo else '✓ ONLINE'}</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Module Tiles ─────────────────────────────────────────
    st.markdown("""
    <div style="font-size:0.62rem;letter-spacing:0.35em;text-transform:uppercase;
         color:rgba(0,180,255,0.45);font-family:'Share Tech Mono',monospace;
         margin-bottom:20px;text-align:center;
         display:flex;align-items:center;justify-content:center;gap:14px;">
      <span style="flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(0,150,255,0.2));"></span>
      SELECT A MODULE TO BEGIN
      <span style="flex:1;height:1px;background:linear-gradient(90deg,rgba(0,150,255,0.2),transparent);"></span>
    </div>""", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown("""
        <div class="home-module" style="--mc:#0077a8">
          <div class="home-module-icon">📊</div>
          <div class="home-module-title">Indices</div>
          <div class="home-module-desc">
            Topic-based geopolitical risk indices across {n_c} countries.<br>
            Time series, heatmaps, world maps, signals &amp; alarms.
          </div>
        </div>""".format(n_c=len(all_countries)), unsafe_allow_html=True)
        if st.button("→ Open Indices", key='home_to_indices', use_container_width=True):
            st.session_state.page = 'indices'
            st.rerun()

    with m2:
        st.markdown("""
        <div class="home-module" style="--mc:#f59e0b">
          <div class="home-module-icon">🎯</div>
          <div class="home-module-title">Country Profile</div>
          <div class="home-module-desc">
            Deep-dive into any country: top risk scores, active alarms,
            bilateral relations worst &amp; best partners.
          </div>
        </div>""", unsafe_allow_html=True)
        if st.button("→ Open Profile", key='home_to_profile', use_container_width=True):
            st.session_state.page = 'profile'
            st.rerun()

    with m3:
        st.markdown("""
        <div class="home-module" style="--mc:#00d4aa">
          <div class="home-module-icon">📰</div>
          <div class="home-module-title">News</div>
          <div class="home-module-desc">
            Live GDELT headlines across 28 topic categories.<br>
            Real-time global news intelligence feed.
          </div>
        </div>""", unsafe_allow_html=True)
        if st.button("→ Open News", key='home_to_news', use_container_width=True):
            st.session_state.page = 'news'
            st.rerun()

    with m4:
        pred_status = '✓ READY' if has_predictions else '⏳ PENDING'
        pred_color  = '#0077a8' if has_predictions else '#e06030'
        st.markdown(f"""
        <div class="home-module" style="--mc:{pred_color}">
          <div class="home-module-icon">🔮</div>
          <div class="home-module-title">Predictions</div>
          <div class="home-module-desc">
            N-HiTS deep learning 12-month forecasts<br>
            for 2,400 topic × country risk series.<br>
            <span style='color:{pred_color};font-family:monospace;font-size:0.6rem;'>
              {pred_status}
            </span>
          </div>
        </div>""", unsafe_allow_html=True)
        if st.button("→ Open Predictions", key='home_to_pred', use_container_width=True):
            st.session_state.page = 'predictions'
            st.rerun()

    st.markdown('<div class="h-div" style="margin:28px 0 20px;"></div>', unsafe_allow_html=True)

    # ── Live Tension Overview ────────────────────────────────
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
                     border-radius:10px;padding:14px 12px;text-align:center;
                     border-top:3px solid {clr};">
                  <div style="font-size:0.72rem;color:#1a3a5c;font-weight:600;margin-bottom:4px;">
                    {n1}
                  </div>
                  <div style="font-size:0.55rem;color:rgba(123,47,255,0.6);
                       font-family:monospace;margin-bottom:4px;">↔ VS ↔</div>
                  <div style="font-size:0.72rem;color:#1a3a5c;font-weight:600;margin-bottom:8px;">
                    {n2}
                  </div>
                  <div style="font-size:1.4rem;font-weight:700;color:{clr};
                       text-shadow:0 0 14px {clr}55;">{net:.0f}</div>
                  <div style="font-size:0.58rem;color:{clr};font-family:monospace;">
                    {'CRITICAL' if net>=65 else 'HIGH' if net>=45 else 'ELEVATED' if net>=25 else 'MODERATE'}
                  </div>
                </div>""", unsafe_allow_html=True)

    # ── Quick stats row ──────────────────────────────────────
    st.markdown('<div class="h-div" style="margin:24px 0 16px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-hdr">📈  Top Risk Countries — All Topics</div>', unsafe_allow_html=True)

    avg_all = tension_norm.mean(axis=1).nlargest(8)
    cols_r  = st.columns(8)
    for col_el, (country, val) in zip(cols_r, avg_all.items()):
        with col_el:
            clr = '#e05060' if val>=50 else ('#f59e0b' if val>=25 else '#00b4d8')
            st.markdown(f"""
            <div style="background:rgba(0,10,28,0.7);border:1px solid {clr}20;
                 border-radius:8px;padding:10px 8px;text-align:center;">
              <div style="font-size:0.65rem;color:#1a4070;margin-bottom:4px;">
                {COUNTRY_NAMES.get(country,country)}
              </div>
              <div style="font-size:1.2rem;font-weight:700;color:{clr};
                   text-shadow:0 0 10px {clr}50;">{val:.0f}</div>
            </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE: INDICES
# ═══════════════════════════════════════════════════════════════
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
    for _idx in df_norm.index:
        _r = df_norm.loc[_idx]
        _nz = _r[_r > 0]
        if len(_nz) > 2:
            _t = _nz.median() * 0.05
            df_norm.loc[_idx] = _r.where(_r > _t, np.nan).interpolate(method='linear', limit_direction='both').ffill().bfill().fillna(0)
    df_recent     = apply_norm(df_recent_raw, norm_method)
    for _idx in df_recent.index:
        _r = df_recent.loc[_idx]
        _nz = _r[_r > 0]
        if len(_nz) > 2:
            _t = _nz.median() * 0.05
            df_recent.loc[_idx] = _r.where(_r > _t, np.nan).interpolate(method='linear', limit_direction='both').ffill().bfill().fillna(0)
    norm_suffix   = {'Raw':'','Score (0–100)':' · Score 0–100','Z-Score':' · Z-Score'}[norm_method]
    sel_label     = TOPIC_LABELS.get(sel_topic, sel_topic.replace('_',' ').title())

    # Header
    c1h, c2h = st.columns([3,1])
    with c1h:
        st.markdown(f"""
        <div style='padding:6px 0 2px;'>
          <div class='hero-title'>NERAI Intelligence Hub</div>
          <div class='hero-sub'><span class='live-dot'></span>
            Geopolitical Risk Intelligence &nbsp;·&nbsp; Data: GDELT Project
          </div>
        </div>""", unsafe_allow_html=True)
    with c2h:
        nm_color = {'Raw':'#2a5080','Score (0–100)':'#00b4d8','Z-Score':'#0077a8'}[norm_method]
        st.markdown(f"""
        <div style='text-align:right;padding-top:12px;font-family:monospace;
             font-size:0.68rem;color:rgba(0,180,255,0.4);'>
          LAST UPDATE<br>
          <span style='color:#0077a8;font-size:0.9rem;'>{date_cols[-1].strftime('%d %b %Y')}</span><br>
          <span style='color:{nm_color};font-size:0.7rem;'>▣ {norm_method}</span>
        </div>""", unsafe_allow_html=True)
    st.markdown('<div class="h-div"></div>', unsafe_allow_html=True)

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

    # Top Signals
    with st.expander("⚡  Top Signals — Biggest Movers (Last 7 Days)", expanded=True):
        st.markdown('<div class="sec-hdr">Anomaly Detection</div>', unsafe_allow_html=True)
        if len(df_norm.columns)>7:
            last    = df_norm.iloc[:,-1]
            prev    = df_norm.iloc[:,-8]
            changes = ((last-prev)/(prev.abs().clip(lower=1.0))*100).clip(-200,200).dropna()
            top_up  = changes.nlargest(5)
            top_dn  = changes.nsmallest(3)
            sig_c1, sig_c2 = st.columns(2)
            with sig_c1:
                st.markdown('<div style="font-size:0.65rem;color:#ff6b35;letter-spacing:0.15em;margin-bottom:8px;">▲ RISING RISK</div>', unsafe_allow_html=True)
                for c,pct in top_up.items():
                    val = last[c]
                    st.markdown(f"""
                    <div class='signal-card' style='border-color:rgba(255,107,53,0.2);'>
                      <div><div class='signal-name'>{COUNTRY_NAMES.get(c,c)}</div>
                      <div class='signal-topic'>{sel_label}</div></div>
                      <div><div class='signal-val' style='color:#ff6b35;'>{fmt(val,norm_method)}</div>
                      <div style='font-size:0.65rem;color:#ff9d6b;text-align:right;'>▲ {pct:+.1f}%</div></div>
                    </div>""", unsafe_allow_html=True)
            with sig_c2:
                st.markdown('<div style="font-size:0.65rem;color:#00d4aa;letter-spacing:0.15em;margin-bottom:8px;">▼ DECLINING RISK</div>', unsafe_allow_html=True)
                for c,pct in top_dn.items():
                    val = last[c]
                    st.markdown(f"""
                    <div class='signal-card' style='border-color:rgba(0,255,157,0.15);'>
                      <div><div class='signal-name'>{COUNTRY_NAMES.get(c,c)}</div>
                      <div class='signal-topic'>{sel_label}</div></div>
                      <div><div class='signal-val' style='color:#00d4aa;'>{fmt(val,norm_method)}</div>
                      <div style='font-size:0.65rem;color:#00cc7a;text-align:right;'>{pct:+.1f}%</div></div>
                    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="h-div"></div>', unsafe_allow_html=True)

    # Time Series with Peak Detection
    col_ts, col_map = st.columns([3,2])
    with col_ts:
        st.markdown('<div class="sec-hdr">Time Series Analysis</div>', unsafe_allow_html=True)
        if sel_countries:
            fig_ts, peak_info = chart_timeseries_with_peaks(
                df_recent, sel_countries,
                f'{sel_label}{norm_suffix} · Last {n_days} Days',
                norm_method, show_peaks=True
            )
            st.plotly_chart(fig_ts, use_container_width=True, config={'displayModeBar':False})

            # Peak News Section
            if peak_info and sel_countries:
                with st.expander("📰  Peak Analysis — What Happened at Spike Points?", expanded=False):
                    st.markdown('<div class="sec-hdr">GDELT Headlines Around Peak Dates</div>', unsafe_allow_html=True)
                    for c, peaks in peak_info.items():
                        cname = COUNTRY_NAMES.get(c, c)
                        for pk_date in peaks[:1]:  # top 1 peak per country
                            pk_str = pk_date.strftime('%Y-%m-%d')
                            st.markdown(f"""
                            <div class="peak-date-badge">⚡ {cname} — Peak: {pk_date.strftime('%d %b %Y')}</div>
                            """, unsafe_allow_html=True)
                            with st.spinner(f'Fetching news for {cname}...'):
                                articles = fetch_peak_news(c, sel_topic, pk_str)
                            if articles:
                                for art in articles:
                                    title  = art.get('title','No title')
                                    source = art.get('domain','')
                                    url    = art.get('url','#')
                                    seendate = art.get('seendate','')
                                    date_disp = seendate[:8] if len(seendate)>=8 else ''
                                    if date_disp:
                                        try: date_disp = pd.Timestamp(date_disp).strftime('%d %b %Y')
                                        except: pass
                                    st.markdown(f"""
                                    <div class="peak-news-item">
                                      <div class="peak-news-headline">
                                        <a href="{url}" target="_blank" style="color:#1a3a70;text-decoration:none;">
                                          {title[:120]}{'...' if len(title)>120 else ''}
                                        </a>
                                      </div>
                                      <div class="peak-news-src">{source} · {date_disp}</div>
                                    </div>""", unsafe_allow_html=True)
                            else:
                                st.markdown('<div style="color:rgba(100,150,180,0.4);font-size:0.72rem;padding:8px 0;">No news found for this peak period.</div>', unsafe_allow_html=True)
        else:
            st.info("Sidebar'dan en az bir ülke seçin.")

    with col_map:
        st.markdown('<div class="sec-hdr">Global Risk Map</div>', unsafe_allow_html=True)
        if map_date in df_norm.columns:
            st.plotly_chart(chart_world(df_norm, map_date),
                use_container_width=True, config={'displayModeBar':False})

    st.markdown('<div class="h-div"></div>', unsafe_allow_html=True)

    # Heatmap + Ranking
    col_h, col_r = st.columns([3,2])
    with col_h:
        st.markdown('<div class="sec-hdr">Country Heatmap</div>', unsafe_allow_html=True)
        st.plotly_chart(chart_heatmap(df_recent, heatmap_n, norm_method),
            use_container_width=True, config={'displayModeBar':False})
    with col_r:
        st.markdown('<div class="sec-hdr">Country Ranking</div>', unsafe_allow_html=True)
        if map_date in df_norm.columns:
            st.plotly_chart(chart_ranking(df_norm, map_date),
                use_container_width=True, config={'displayModeBar':False})

    # Top Bilateral Alerts
    st.markdown('<div class="h-div"></div>', unsafe_allow_html=True)
    with st.expander("🚨  Top 5 Bilateral Tension Alerts — Auto-Detected", expanded=True):
        st.markdown('<div class="sec-hdr">Highest Risk Country Pairs · Last 7 Days</div>', unsafe_allow_html=True)
        top_pairs = compute_top_tensions(tension_norm, coop_norm, deteri_norm)
        for rank, pair in enumerate(top_pairs, 1):
            n1  = COUNTRY_NAMES.get(pair['c1'],pair['c1'])
            n2  = COUNTRY_NAMES.get(pair['c2'],pair['c2'])
            net = pair['net']; trnd = pair['trend']
            if   net>=65: badge_cls,badge_txt,bar_col = 'badge-crit','CRITICAL','#e05060'
            elif net>=45: badge_cls,badge_txt,bar_col = 'badge-high','HIGH','#e06030'
            elif net>=25: badge_cls,badge_txt,bar_col = 'badge-med','ELEVATED','#f59e0b'
            else:         badge_cls,badge_txt,bar_col = 'badge-low','MODERATE','#00b4d8'
            t_sym = '▲' if trnd>0.5 else ('▼' if trnd<-0.5 else '→')
            t_col = '#e06030' if trnd>0.5 else ('#00d4aa' if trnd<-0.5 else '#7a9ab8')
            st.markdown(f"""
            <div class="pair-card" style="border-color:rgba(255,255,255,0.06);">
              <div style="font-size:1rem;font-weight:700;color:rgba(0,150,255,0.35);
                   font-family:monospace;width:22px;flex-shrink:0;">#{rank}</div>
              <div style="flex:1;min-width:0;">
                <div style="font-size:0.85rem;font-weight:600;color:#2a4060;margin-bottom:5px;">
                  {n1}<span style="color:rgba(123,47,255,0.6);padding:0 6px;">↔</span>{n2}
                </div>
                <div style="background:rgba(0,0,0,0.35);border-radius:3px;height:3px;width:100%;">
                  <div style="background:{bar_col};width:{min(net,100):.0f}%;height:3px;
                       border-radius:3px;box-shadow:0 0 8px {bar_col}70;"></div>
                </div>
              </div>
              <div style="text-align:right;flex-shrink:0;margin-left:14px;">
                <div style="font-size:1rem;font-weight:700;color:{bar_col};">{net:.1f}</div>
                <div style="font-size:0.62rem;color:{t_col};font-family:monospace;">{t_sym} {abs(trnd):.1f}</div>
              </div>
              <div style="flex-shrink:0;margin-left:10px;">
                <span class="{badge_cls}">{badge_txt}</span>
              </div>
            </div>""", unsafe_allow_html=True)

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

    _render_footer()

# ═══════════════════════════════════════════════════════════════
# PAGE: COUNTRY PROFILE
# ═══════════════════════════════════════════════════════════════
def render_profile():
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
                elif z<=-1.5: alm_col,alm_lbl = '#00d4aa','SUPPRESSED'
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

        st.markdown("""<div style="font-size:0.6rem;color:#00d4aa;letter-spacing:0.15em;
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
        c_col_g = '#00d4aa' if cur_c>40 else ('#00b4d8' if cur_c>15 else '#4a6a8a')
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
        mode='lines',line=dict(width=2,color='#00d4aa'),
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
                    borderwidth=1,font=dict(size=10,color='#0d1f3c')),hovermode='x unified')
    st.plotly_chart(fig_bi, use_container_width=True, config={'displayModeBar':False})
    _render_footer()


# ═══════════════════════════════════════════════════════════════
# PAGE: NEWS
# ═══════════════════════════════════════════════════════════════
def render_news():
    st.markdown(f"""

    # === NEWS DYNAMIC BACKGROUND ===
    _topic_colors = {"conflict": "rgba(255,60,60,0.05)", "diplomacy": "rgba(0,200,255,0.05)", "economy": "rgba(0,255,150,0.05)", "politics": "rgba(180,100,255,0.05)", "environment": "rgba(100,255,100,0.05)", "health": "rgba(255,200,0,0.05)", "technology": "rgba(0,150,255,0.05)"}
    _cur_topic = st.session_state.get("news_topic", "").lower()
    _bg_col = _topic_colors.get(_cur_topic, "rgba(0,255,200,0.03)")
    st.markdown(f"<style>.main .block-container{{background:linear-gradient(180deg,{_bg_col},transparent)!important;}}</style>", unsafe_allow_html=True)
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

        # Globe Map showing topic hotspots
        st.markdown('<div class="h-div" style="margin:20px 0;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-hdr">📡  Topic Activity Map — Country Coverage</div>', unsafe_allow_html=True)

        # Find the closest matching topic from our indices
        cat_lower = sel_cat.lower().replace(' ','_')
        topic_match = None
        for t in all_topics:
            if any(word in t for word in cat_lower.split('_')[:2]):
                topic_match = t
                break
        if topic_match is None and all_topics:
            topic_match = 'political_instability'

        if topic_match and topic_match in df.index.get_level_values('topic'):
            df_cat_raw  = df.xs(topic_match, level='topic')
            df_cat_norm = apply_norm(df_cat_raw, 'Score (0–100)')
            last_date   = df_cat_norm.columns[-1]
            st.plotly_chart(
                chart_world(df_cat_norm, last_date),
                use_container_width=True, config={'displayModeBar':False}
            )

    _render_footer()


# ═══════════════════════════════════════════════════════════════
# PAGE: PREDICTIONS
# ═══════════════════════════════════════════════════════════════
def render_predictions():
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
        # Predictions already normalized to 0-100 at load time
        return yhat_vals

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
            if hist_series is not None and hist_series.max() > 0:
                raw_hist_max = float(df.xs(sel_pred_topic, level='topic')
                                       .loc[sel_pred_country].max()) \
                               if (sel_pred_topic in df.index.get_level_values('topic') and
                                   sel_pred_country in df.index.get_level_values('country')) \
                               else 1.0
                scale = 1.0  # Predictions already normalized at load time
            else:
                scale = 1.0  # Already normalized at load time

            yhat = fc['yhat']       * scale
            y_lo = fc['yhat_lower'] * scale
            y_hi = fc['yhat_upper'] * scale
            fc_end_val = round(float(yhat.iloc[-1]), 1)

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
            font=dict(family='Inter,sans-serif', color='#0d1f3c', size=11),
            height=420, hovermode='x unified',
            margin=dict(l=50, r=20, t=55, b=40),
            xaxis=dict(gridcolor='rgba(0,119,168,0.06)', tickfont=dict(size=10, color='#5a6b82'), showgrid=False),
            yaxis=dict(title='Risk Score (0–100)', title_font=dict(size=10, color='#5a6b82'),
                       gridcolor='rgba(0,212,255,0.06)', tickfont=dict(size=10, color='#5a6b82'), zeroline=False),
            legend=dict(
                bgcolor='rgba(255,255,255,0.92)', bordercolor='rgba(0,119,168,0.2)',
                borderwidth=1, font=dict(size=10, color='#0d1f3c'),
                orientation='h', yanchor='bottom', y=1.01, xanchor='left', x=0
            ),
        )
        st.plotly_chart(fig_fc, use_container_width=True, config={'displayModeBar': False})

        # KPI strip
        if current_val is not None and fc_end_val is not None:
            delta = max(-100, min(100, fc_end_val - current_val))
            d_col = '#e05060' if delta > 0 else '#00d4aa'
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
                         else '#00d4aa' if dirn == 'falling' else '#7a9ab8')
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

    # ── Top Movers (global) ───────────────────────────────────
    if trend_df is not None:
        st.markdown('<div class="sec-hdr">🌍  Global Top Movers — Next 12 Months</div>',
                    unsafe_allow_html=True)
        col_rise, col_fall = st.columns(2)

        with col_rise:
            st.markdown("""
            <div style='font-size:0.62rem;color:rgba(255,75,110,0.6);
                 font-family:monospace;letter-spacing:0.18em;
                 margin-bottom:8px;'>▲  HIGHEST RISING RISKS</div>""",
                        unsafe_allow_html=True)
            top_rise = trend_df.nlargest(10, 'trend_pct')
            for _, r in top_rise.iterrows():
                _t = r['topic'] if pd.notna(r['topic']) else ''
                lbl = TOPIC_LABELS.get(_t, str(_t).replace('_', ' ').title() if _t else 'Unknown')
                cnt = COUNTRY_NAMES.get(r['country'], r['country'])
                st.markdown(f"""
                <div style='display:flex;justify-content:space-between;align-items:center;
                     padding:5px 8px;margin-bottom:3px;
                     background:rgba(255,75,110,0.05);
                     border:1px solid rgba(255,75,110,0.12);border-radius:5px;'>
                  <div>
                    <div style='font-size:0.73rem;color:#2a4060;'>{lbl}</div>
                    <div style='font-size:0.6rem;color:rgba(0,150,255,0.5);
                         font-family:monospace;'>{cnt}</div>
                  </div>
                  <div style='font-size:0.85rem;font-weight:700;
                       color:#e05060;font-family:monospace;'>
                    +{r['trend_pct']:.1f}%
                  </div>
                </div>""", unsafe_allow_html=True)

        with col_fall:
            st.markdown("""
            <div style='font-size:0.62rem;color:rgba(0,255,157,0.6);
                 font-family:monospace;letter-spacing:0.18em;
                 margin-bottom:8px;'>▼  HIGHEST FALLING RISKS</div>""",
                        unsafe_allow_html=True)
            top_fall = trend_df.nsmallest(10, 'trend_pct')
            for _, r in top_fall.iterrows():
                _t = r['topic'] if pd.notna(r['topic']) else ''
                lbl = TOPIC_LABELS.get(_t, str(_t).replace('_', ' ').title() if _t else 'Unknown')
                cnt = COUNTRY_NAMES.get(r['country'], r['country'])
                st.markdown(f"""
                <div style='display:flex;justify-content:space-between;align-items:center;
                     padding:5px 8px;margin-bottom:3px;
                     background:rgba(0,255,157,0.04);
                     border:1px solid rgba(0,255,157,0.10);border-radius:5px;'>
                  <div>
                    <div style='font-size:0.73rem;color:#2a4060;'>{lbl}</div>
                    <div style='font-size:0.6rem;color:rgba(0,150,255,0.5);
                         font-family:monospace;'>{cnt}</div>
                  </div>
                  <div style='font-size:0.85rem;font-weight:700;
                       color:#00d4aa;font-family:monospace;'>
                    {r['trend_pct']:.1f}%
                  </div>
                </div>""", unsafe_allow_html=True)

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
    chg_col   = '#e05060' if change > 10 else '#00d4aa' if change < -10 else '#7a9ab8'
    chg_arrow = '▲' if change > 10 else '▼' if change < -10 else '→'
    risk_col  = '#e05060' if risk > 65 else '#f59e0b' if risk > 35 else '#00d4aa'
    fc_col    = '#e05060' if fc_dir == 'rising' else '#00d4aa' if fc_dir == 'falling' else '#7a9ab8'
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
      {topic_rows(tf, '#00d4aa')}
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
            "Aşağıda GDELT (Global Database of Events, Language and Tone) platformundan "
            "alınan gerçek zamanlı veriler yer almaktadır:\n\n"
            + context +
            "\n\nUSER QUESTION: " + question + "\n\n"
            "Lütfen bu soruyu 3-4 paragrafla, şu çerçevede analiz et:\n"
            "1) Mevcut durum — GDELT verilerine göre risk endeksleri ve son trendler\n"
            "2) Önemli gelişmeler — Endekslerdeki değişimlere yol açan olaylar ve haberler\n"
            "3) Öngörüler — Model tahminlerine göre önümüzdeki dönemde beklenen seyir\n"
            "4) Stratejik değerlendirme — Genel jeopolitik tabloya yansıması\n\n"
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
            '⚠️ AI analiz hatası: ' + str(_e)[:300] + '</div>'
        )


def render_insights():
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
                st.markdown(f"<div style='display:flex;justify-content:space-between;padding:4px 8px;margin-bottom:3px;background:rgba(0,255,157,0.04);border:1px solid rgba(0,255,157,0.10);border-radius:5px;'><div><div style='font-size:0.72rem;color:#2a4060;'>{lbl}</div><div style='font-size:0.58rem;color:rgba(0,150,255,0.5);font-family:monospace;'>{cnt}</div></div><div style='font-size:0.82rem;font-weight:700;color:#00d4aa;font-family:monospace;'>{_safe_pct(r['trend_pct']):.1f}%</div></div>", unsafe_allow_html=True)

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


def build_network_figure(filtered, highlight_nodes=None):
    """Build an interactive Plotly network diagram from a filtered edge DataFrame."""
    import math
    if highlight_nodes is None:
        highlight_nodes = set()

    nodes = list(set(filtered['source'].tolist() + filtered['target'].tolist()))
    n = len(nodes)
    if n == 0:
        return None

    # Layout: networkx spring if available, else circular fallback
    try:
        import networkx as nx
        G = nx.DiGraph()
        for _, row in filtered.iterrows():
            G.add_edge(row['source'], row['target'], weight=float(row['max_f_stat']))
        pos = nx.spring_layout(G, k=2.5, seed=42, iterations=60)
    except ImportError:
        pos = {}
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / n
            pos[node] = (math.cos(angle), math.sin(angle))

    out_deg = filtered.groupby('source')['max_f_stat'].sum().to_dict()
    in_deg  = filtered.groupby('target')['max_f_stat'].sum().to_dict()

    # Edge traces (one per edge for individual hover)
    edge_traces = []
    for _, row in filtered.iterrows():
        x0, y0 = pos[row['source']]
        x1, y1 = pos[row['target']]
        f = float(row['max_f_stat'])
        is_hl = (row['source'] in highlight_nodes or row['target'] in highlight_nodes)
        color = 'rgba(224,112,32,0.85)' if is_hl else f'rgba(0,140,255,{min(0.75, 0.15 + f/25):.2f})'
        width = 3.5 if is_hl else max(0.8, min(4.0, f / 7))
        s_lbl, s_cc = _node_label(row['source'])
        t_lbl, t_cc = _node_label(row['target'])
        edge_traces.append(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            mode='lines',
            line=dict(width=width, color=color),
            hoverinfo='text',
            hovertext=f"{s_lbl} ({COUNTRY_NAMES.get(s_cc,s_cc)}) → {t_lbl} ({COUNTRY_NAMES.get(t_cc,t_cc)})<br>F={f:.1f}  p={float(row['min_p_value']):.3f}  lag={int(row['best_lag'])}m",
            showlegend=False
        ))

    # Node trace
    nx_list, ny_list, ntxt, nhov, ncol, nsz = [], [], [], [], [], []
    for node in nodes:
        x, y = pos[node]
        lbl, cc = _node_label(node)
        nx_list.append(x); ny_list.append(y)
        ntxt.append(f"{lbl}<br><b>{COUNTRY_NAMES.get(cc,cc)}</b>")
        out_f = out_deg.get(node, 0)
        in_f  = in_deg.get(node, 0)
        nhov.append(f"<b>{lbl}</b><br><b>{COUNTRY_NAMES.get(cc,cc)}</b><br>"
                    f"Out-influence: {out_f:.1f}<br>In-influence: {in_f:.1f}<br>"
                    f"Connections out: {int(filtered[filtered['source']==node].shape[0])}")
        is_hl = node in highlight_nodes
        ncol.append('#e07020' if is_hl else ('#0055a8' if out_f > 8 else '#0099cc'))
        nsz.append(22 if is_hl else max(10, min(34, 10 + out_f / 2.5)))

    node_trace = go.Scatter(
        x=nx_list, y=ny_list,
        mode='markers+text',
        text=ntxt,
        textposition='top center',
        textfont=dict(size=7, color='#1a2a3a'),
        hovertext=nhov,
        hoverinfo='text',
        marker=dict(size=nsz, color=ncol,
                    line=dict(width=1.5, color='rgba(255,255,255,0.6)')),
        showlegend=False
    )

    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        height=540,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(232,240,250,0.45)',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showline=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showline=False),
        margin=dict(l=10, r=10, t=10, b=10),
        hovermode='closest',
    )
    return fig


def causal_network_narrative(filtered, highlight_nodes=None):
    """Return an HTML plain-English paragraph summarising the causal network."""
    if filtered.empty:
        return ""
    if highlight_nodes is None:
        highlight_nodes = set()

    top_src  = filtered.groupby('source')['max_f_stat'].sum().sort_values(ascending=False)
    top_edge = filtered.nlargest(3, 'max_f_stat')

    parts_p1 = []
    if not top_src.empty:
        node = top_src.index[0]
        lbl, cc = _node_label(node)
        n_out = int(filtered[filtered['source'] == node].shape[0])
        parts_p1.append(
            f"The strongest statistical driver in this network is "
            f"<b>{lbl}</b> in <b>{COUNTRY_NAMES.get(cc, cc)}</b>, which Granger-causes "
            f"{n_out} other series with a cumulative F-statistic of {top_src.iloc[0]:.1f}."
        )
    if not top_edge.empty:
        r = top_edge.iloc[0]
        sl, sc = _node_label(r['source']); tl, tc = _node_label(r['target'])
        parts_p1.append(
            f"The single most powerful link runs from <b>{sl} ({COUNTRY_NAMES.get(sc,sc)})</b> "
            f"→ <b>{tl} ({COUNTRY_NAMES.get(tc,tc)})</b> "
            f"(F&nbsp;=&nbsp;{float(r['max_f_stat']):.1f}, "
            f"p&nbsp;=&nbsp;{float(r['min_p_value']):.3f}, "
            f"lag&nbsp;{int(r['best_lag'])}&nbsp;month{'s' if r['best_lag']>1 else ''}), "
            f"meaning past readings in the source reliably precede shifts in the target."
        )

    p1 = " ".join(parts_p1)

    p2 = (
        f"In total, <b>{len(filtered)}</b> statistically significant causal links are visible "
        f"across <b>{len(set(filtered['source'].tolist()+filtered['target'].tolist()))}</b> unique series. "
        f"Thicker, darker edges carry higher F-statistics and represent stronger predictive relationships. "
        f"Larger nodes are more influential — they drive more downstream series. "
        f"This network is computed from historical GDELT data using Granger causality tests at lags 1–3 months; "
        f"it does <em>not</em> change when you run a What-If scenario, but you can cross-reference it: "
        f"if a scenario shocks a node that is a strong driver here, the connected nodes are likely to be affected next."
    )

    hl_note = ""
    if highlight_nodes:
        downstream = set(filtered[filtered['source'].isin(highlight_nodes)]['target'].tolist())
        if downstream:
            dl = [f"{_node_label(n)[0]} ({COUNTRY_NAMES.get(_node_label(n)[1],_node_label(n)[1])})"
                  for n in list(downstream)[:5]]
            hl_note = (
                f"<div style='margin-top:10px;padding:10px 14px;"
                f"background:rgba(224,112,32,0.1);border-left:3px solid #e07020;"
                f"border-radius:4px;font-size:0.8rem;color:#7a3a00;'>"
                f"⚠ <b>Scenario linkage:</b> The last scenario touched nodes highlighted in orange. "
                f"Their direct causal descendants — most likely to experience spillover — include: "
                f"<b>{', '.join(dl)}</b>{'…' if len(downstream)>5 else '.'}."
                f"</div>"
            )

    return p1, p2, hl_note


def render_causality():
    st.markdown("""
    <div style='padding:6px 0 10px;'>
      <div class='hero-title'>Causal Network Analysis</div>
      <div class='hero-sub'>
        <span class='live-dot'></span>
        Granger Causality &nbsp;·&nbsp; Cross-Series Influence Detection
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="h-div"></div>', unsafe_allow_html=True)

    cdf = load_causality()
    # Normalise column names: support both gdelt_causality.py output formats
    if cdf is not None and not cdf.empty and 'source_id' in cdf.columns:
        cdf = cdf.rename(columns={
            'source_id': 'source',
            'target_id': 'target',
            'f_stat':    'max_f_stat',
            'p_value':   'min_p_value',
        })
    sdf = load_scenario_results()

    # Which nodes were in the last scenario run?
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
        st.markdown("""
        <div style='text-align:center;padding:40px 20px;
             background:rgba(232,240,252,0.7);border:1px solid rgba(0,119,168,0.15);
             border-radius:12px;margin:20px 0;'>
          <div style='font-size:3rem;margin-bottom:16px;'>🕸</div>
          <div style='font-size:1.1rem;font-weight:700;color:#0055a8;
               letter-spacing:0.06em;margin-bottom:10px;'>Causal Network Not Yet Computed</div>
          <div style='font-size:0.82rem;color:#3a5a7a;max-width:520px;margin:0 auto;line-height:1.75;'>
            Click <b>Run Causal Analysis</b> in the sidebar to compute Granger causality relationships
            between all topic × country pairs. This reveals which geopolitical signals
            statistically predict future movements in others — and which countries are most
            exposed if a shock occurs upstream.
          </div>
        </div>""", unsafe_allow_html=True)
        st.subheader("Preview: What the edge table looks like")
        demo = pd.DataFrame({
            'source': ['political_instability_RU','military_posture_IR','protest_activity_TR'],
            'target': ['political_instability_UA','oil_market_stability_SA','political_instability_GR'],
            'max_f_stat': [12.4, 8.7, 6.2],
            'min_p_value': [0.002, 0.011, 0.031],
            'best_lag': [1, 2, 1]
        })
        st.dataframe(demo, use_container_width=True)
        return

    # ── Filters ────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        min_f = st.slider('Min F-Statistic', 0.0, float(cdf['max_f_stat'].max()), 3.0)
    with col2:
        topics = ['All'] + sorted(cdf['source'].str.rsplit('_', n=1).str[0].unique().tolist())
        sel_topic = st.selectbox('Filter by Topic', topics)
    with col3:
        max_lag = st.selectbox('Max Lag (months)', [1, 2, 3], index=2)

    filtered = cdf[cdf['max_f_stat'] >= min_f].copy()
    if sel_topic != 'All':
        filtered = filtered[filtered['source'].str.startswith(sel_topic) |
                            filtered['target'].str.startswith(sel_topic)]
    filtered = filtered[filtered['best_lag'] <= max_lag]

    # ── KPI row ────────────────────────────────────────────────
    kc1, kc2, kc3 = st.columns(3)
    with kc1:
        st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Causal Links</div>"
                    f"<div class='kpi-value'>{len(filtered)}</div></div>", unsafe_allow_html=True)
    with kc2:
        st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Avg F-Statistic</div>"
                    f"<div class='kpi-value'>{filtered['max_f_stat'].mean():.1f}</div></div>", unsafe_allow_html=True)
    with kc3:
        n_series = len(set(filtered['source'].tolist() + filtered['target'].tolist()))
        st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Series Involved</div>"
                    f"<div class='kpi-value'>{n_series}</div></div>", unsafe_allow_html=True)

    st.markdown('<div style="margin:20px 0;"></div>', unsafe_allow_html=True)

    # ── Plain-English narrative ────────────────────────────────
    narr = causal_network_narrative(filtered, highlight_nodes=scenario_nodes)
    if narr:
        p1, p2, hl_note = narr
        st.markdown(f"""
        <div style='background:#f0f6fc;border:1px solid rgba(0,119,168,0.18);
             border-radius:10px;padding:18px 22px;margin-bottom:20px;line-height:1.75;
             font-size:0.85rem;color:#1a2a3a;'>
          <div style='font-size:0.7rem;font-weight:700;color:#0077a8;letter-spacing:0.1em;
               text-transform:uppercase;margin-bottom:8px;'>📖 What This Network Shows</div>
          <p style='margin:0 0 8px;'>{p1}</p>
          <p style='margin:0;'>{p2}</p>
          {hl_note}
        </div>""", unsafe_allow_html=True)

    # ── Interactive Network Diagram ────────────────────────────
    st.subheader("🕸 Interactive Network Diagram")
    if scenario_nodes:
        st.caption("🟠 Orange nodes/edges = series touched by the most recent scenario run")

    net_fig = build_network_figure(filtered.head(120), highlight_nodes=scenario_nodes)
    if net_fig:
        st.plotly_chart(net_fig, use_container_width=True)
    else:
        st.info("No edges to display with the current filters.")

    # ── Top Influencers bar ─────────────────────────────────────
    st.subheader("Top Causal Influencers")
    influence = filtered.groupby('source')['max_f_stat'].sum().sort_values(ascending=False).head(15)
    bar_colors = ['rgba(224,112,32,0.8)' if n in scenario_nodes else 'rgba(0,140,220,0.7)'
                  for n in influence.index]
    fig_bar = go.Figure(go.Bar(
        x=influence.values, y=influence.index,
        orientation='h',
        marker_color=bar_colors,
        marker_line_color='rgba(0,80,160,0.3)',
        marker_line_width=1
    ))
    fig_bar.update_layout(
        height=420, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(232,240,252,0.4)',
        xaxis=dict(title='Cumulative F-Statistic', color='#3a5a7a', gridcolor='rgba(0,100,200,0.1)'),
        yaxis=dict(color='#1a2a3a', tickfont=dict(size=10, color='#0d1f3c')),
        margin=dict(l=20, r=20, t=10, b=40)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── Edge table ──────────────────────────────────────────────
    with st.expander("📋 Full Causal Edge List", expanded=False):
        display_df = filtered.sort_values('max_f_stat', ascending=False)[
            ['source', 'target', 'max_f_stat', 'min_p_value', 'best_lag']].copy()
        display_df['source_label'] = display_df['source'].apply(
            lambda n: f"{_node_label(n)[0]} ({COUNTRY_NAMES.get(_node_label(n)[1], _node_label(n)[1])})")
        display_df['target_label'] = display_df['target'].apply(
            lambda n: f"{_node_label(n)[0]} ({COUNTRY_NAMES.get(_node_label(n)[1], _node_label(n)[1])})")
        st.dataframe(
            display_df[['source_label','target_label','max_f_stat','min_p_value','best_lag']].rename(
                columns={'source_label':'Source','target_label':'Target',
                         'max_f_stat':'F-Stat','min_p_value':'p-value','best_lag':'Lag (m)'}),
            use_container_width=True
        )


# ═══════════════════════════════════════════════════════════════
# WHAT-IF SCENARIOS PAGE
# ═══════════════════════════════════════════════════════════════
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

    st.subheader("Pre-Built Scenarios")
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
    st.subheader("▶️ Run Pre-Built Scenario")
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
    st.subheader("🔧 Build a Custom Scenario")
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
        st.subheader("📊 Scenario Results")
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

page = st.session_state.get('page', 'home')
if   page == 'home':        render_home()
elif page == 'indices':     render_indices()
elif page == 'profile':     render_profile()
elif page == 'news':        render_news()
elif page == 'predictions': render_predictions()
elif page == 'causality':   render_causality()
elif page == 'scenarios':   render_scenarios()
elif page == 'insights':    render_insights()
elif page == 'api':         render_api()
else:
    st.session_state.page = 'home'
    st.rerun()
