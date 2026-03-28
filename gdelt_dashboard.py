"""
NERAI INTELLIGENCE HUB — Dashboard v3.0
Multi-page: Home | Indices | Country Profile | News
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime, os, json
import urllib.request, urllib.parse

st.set_page_config(
    page_title="NERAI Intelligence Hub",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

/* ROOT PALETTE */
:root {
    --navy:#0d1f3c; --teal:#0077a8; --sky:#e8f0f8; --silver:#5a6b82;
    --border:rgba(0,119,168,0.14); --hot:#e05060; --warm:#f59e0b;
    --cool:#00d4aa; --mild:#00b4d8; --white:#ffffff;
}

/* BASE */
.stApp { background:#f4f7fb; }
html,body,[class*="css"]{font-family:'Inter',sans-serif;color:#0d1f3c;}

/* SIDEBAR */
[data-testid="stSidebar"]{background:#ffffff;border-right:1px solid rgba(0,119,168,0.14);}
[data-testid="stSidebar"] label{color:#0077a8 !important;font-size:0.7rem !important;
    letter-spacing:0.1em;text-transform:uppercase;}
[data-testid="stSidebar"] .stButton>button{
    background:#e8f0f8 !important;border:1px solid rgba(0,119,168,0.2) !important;
    color:#0d1f3c !important;font-family:'Inter',sans-serif !important;
    font-size:0.78rem !important;letter-spacing:0.04em !important;
    border-radius:8px !important;width:100% !important;
    text-align:left !important;padding:9px 14px !important;
    transition:all 0.2s !important;margin-bottom:3px !important;}
[data-testid="stSidebar"] .stButton>button:hover{
    border-color:#0077a8 !important;color:#0077a8 !important;
    background:#d5e5f0 !important;}

/* KPI */
.kpi-card{background:#ffffff;border:1px solid rgba(0,119,168,0.14);
    border-radius:12px;padding:16px 18px;position:relative;overflow:hidden;
    box-shadow:0 2px 12px rgba(13,31,60,0.07);transition:box-shadow 0.2s;}
.kpi-card:hover{box-shadow:0 4px 20px rgba(0,119,168,0.14);}
.kpi-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,#0077a8,#00d4aa);}
.kpi-label{font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;
    color:#0077a8;font-weight:600;margin-bottom:4px;}
.kpi-value{font-size:2.1rem;font-weight:700;line-height:1;color:#0d1f3c;}
.kpi-sub{font-size:0.68rem;margin-top:5px;color:#5a6b82;}
.kpi-up{color:#00d4aa;}.kpi-down{color:#e05060;}.kpi-neu{color:#5a6b82;}
.badge-low{color:#00d4aa;font-size:0.6rem;background:rgba(0,212,170,0.1);
    border:1px solid rgba(0,212,170,0.3);border-radius:4px;padding:2px 7px;}
.badge-med{color:#f59e0b;font-size:0.6rem;background:rgba(245,158,11,0.1);
    border:1px solid rgba(245,158,11,0.3);border-radius:4px;padding:2px 7px;}
.badge-high{color:#e06030;font-size:0.6rem;background:rgba(224,96,48,0.1);
    border:1px solid rgba(224,96,48,0.3);border-radius:4px;padding:2px 7px;}
.badge-crit{color:#e05060;font-size:0.6rem;background:rgba(224,80,96,0.1);
    border:1px solid rgba(224,80,96,0.3);border-radius:4px;padding:2px 7px;}

/* HERO */
.hero-title{font-size:2rem;font-weight:700;letter-spacing:0.03em;
    color:#0d1f3c;font-family:'DM Serif Display',serif;}
.hero-sub{font-size:0.72rem;letter-spacing:0.18em;text-transform:uppercase;color:#0077a8;}
.live-dot{display:inline-block;width:7px;height:7px;border-radius:50%;
    background:#00d4aa;animation:pulse 2s infinite;margin-right:5px;vertical-align:middle;}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(.8)}}

/* SECTION HEADER */
.sec-hdr{font-size:0.65rem;letter-spacing:0.2em;text-transform:uppercase;
    color:#0077a8;font-weight:600;
    padding:8px 0 6px;border-bottom:2px solid rgba(0,119,168,0.18);margin-bottom:12px;}

/* SIGNAL CARD */
.signal-card{background:#ffffff;border:1px solid rgba(0,119,168,0.14);
    border-radius:10px;padding:10px 14px;margin-bottom:8px;
    display:flex;align-items:center;justify-content:space-between;
    transition:box-shadow 0.2s;}
.signal-card:hover{box-shadow:0 2px 12px rgba(0,119,168,0.12);}
.signal-name{font-size:0.75rem;color:#0d1f3c;font-weight:600;}
.signal-topic{font-size:0.62rem;color:#0077a8;}
.signal-val{font-size:1rem;font-weight:700;color:#0d1f3c;text-align:right;}

/* NORM BADGE */
.norm-raw{color:#5a6b82;}.norm-score{color:#0077a8;}.norm-z{color:#00d4aa;}

/* DIVIDER */
.h-div{height:1px;background:linear-gradient(90deg,transparent,rgba(0,119,168,0.2),transparent);margin:12px 0;}

#MainMenu,footer,.stDeployButton{visibility:hidden;display:none;}
::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-thumb{background:rgba(0,119,168,0.2);border-radius:2px;}

/* BILATERAL */
.vs-badge{display:inline-block;background:rgba(0,119,168,0.1);
    border:1px solid rgba(0,119,168,0.3);border-radius:50%;
    width:38px;height:38px;line-height:38px;text-align:center;
    font-size:0.72rem;font-weight:700;color:#0077a8;}
.relation-status{border-radius:10px;padding:18px 12px;text-align:center;
    background:#e8f0f8;margin:4px 0;}
.metric-mini{background:#ffffff;border:1px solid rgba(0,119,168,0.14);
    border-radius:8px;padding:12px 10px;text-align:center;}
.metric-mini-label{font-size:0.58rem;letter-spacing:0.12em;text-transform:uppercase;
    color:#0077a8;font-weight:600;margin-bottom:4px;}
.metric-mini-val{font-size:1.5rem;font-weight:700;line-height:1.1;color:#0d1f3c;}
.pair-card{background:#ffffff;border:1px solid rgba(0,119,168,0.14);
    border-radius:8px;padding:11px 15px;margin-bottom:7px;
    display:flex;align-items:center;gap:12px;}

/* COUNTRY PROFILE */
.prof-header{background:linear-gradient(135deg,#e8f0f8,#f4f7fb);
    border:1px solid rgba(0,119,168,0.18);border-radius:12px;
    padding:14px 20px;margin-bottom:14px;
    display:flex;align-items:center;justify-content:space-between;
    box-shadow:0 2px 12px rgba(13,31,60,0.06);}
.prof-country{font-size:1.25rem;font-weight:700;color:#0d1f3c;}
.prof-sub{font-size:0.6rem;color:#0077a8;
    letter-spacing:0.12em;margin-top:3px;text-transform:uppercase;}
.prof-section-title{font-size:0.58rem;letter-spacing:0.18em;text-transform:uppercase;
    color:#0077a8;font-weight:600;
    padding-bottom:5px;border-bottom:1px solid rgba(0,119,168,0.15);margin-bottom:9px;}
.idx-row{display:flex;align-items:center;justify-content:space-between;
    padding:6px 0;border-bottom:1px solid rgba(0,119,168,0.08);}
.idx-label{font-size:0.72rem;color:#5a6b82;}
.idx-val{font-size:0.82rem;font-weight:700;color:#0d1f3c;}
.idx-bar-bg{background:#e8f0f8;border-radius:3px;height:3px;margin-top:3px;}
.alarm-row{background:#ffffff;border:1px solid rgba(0,119,168,0.14);
    border-radius:8px;padding:8px 11px;margin-bottom:6px;
    display:flex;align-items:center;justify-content:space-between;}
.alarm-label{font-size:0.72rem;color:#0d1f3c;font-weight:600;}
.alarm-meta{font-size:0.58rem;color:#0077a8;margin-top:2px;}
.rel-compact{background:#f4f7fb;border-radius:7px;padding:8px 12px;
    margin-bottom:5px;display:flex;align-items:center;justify-content:space-between;
    border-left:3px solid transparent;}

/* NEWS CARD */
.news-card{background:#ffffff;border:1px solid rgba(0,119,168,0.14);
    border-radius:12px;padding:14px 16px;margin-bottom:10px;transition:box-shadow 0.2s;}
.news-card:hover{box-shadow:0 4px 16px rgba(0,119,168,0.12);}
.news-title{font-size:0.82rem;color:#0d1f3c;font-weight:600;line-height:1.45;}
.news-source{font-size:0.62rem;color:#0077a8;margin-top:4px;}
.news-date{font-size:0.6rem;color:#5a6b82;}
.news-url{font-size:0.6rem;color:#0077a8;}

/* CAT BUTTON */
.cat-item{background:#e8f0f8;border:1px solid rgba(0,119,168,0.15);
    border-radius:8px;padding:7px 12px;margin-bottom:4px;cursor:pointer;
    font-size:0.68rem;color:#0d1f3c;letter-spacing:0.05em;
    transition:all 0.2s;display:block;}
.cat-item:hover,.cat-item.active{border-color:#0077a8;color:#0077a8;background:#d5e5f0;}

/* HOME PAGE HERO */
.home-hero{
    background:linear-gradient(135deg,#0d1f3c 0%,#0a2d4a 60%,#0d1f3c 100%);
    border-radius:16px;padding:50px 40px;margin-bottom:32px;
    position:relative;overflow:hidden;text-align:center;
    box-shadow:0 8px 40px rgba(13,31,60,0.18);}
.home-hero::before{content:'';position:absolute;inset:0;
    background-image:
        linear-gradient(rgba(0,119,168,0.07) 1px,transparent 1px),
        linear-gradient(90deg,rgba(0,119,168,0.07) 1px,transparent 1px);
    background-size:50px 50px;pointer-events:none;}
.home-corner{position:absolute;width:22px;height:22px;}
.home-corner-tl{top:14px;left:14px;border-top:2px solid rgba(0,180,216,0.5);border-left:2px solid rgba(0,180,216,0.5);}
.home-corner-tr{top:14px;right:14px;border-top:2px solid rgba(0,180,216,0.5);border-right:2px solid rgba(0,180,216,0.5);}
.home-corner-bl{bottom:14px;left:14px;border-bottom:2px solid rgba(0,180,216,0.5);border-left:2px solid rgba(0,180,216,0.5);}
.home-corner-br{bottom:14px;right:14px;border-bottom:2px solid rgba(0,180,216,0.5);border-right:2px solid rgba(0,180,216,0.5);}
.home-orb{position:absolute;border-radius:50%;filter:blur(70px);pointer-events:none;}

/* LOGO */
.nerai-logo-wrap{position:relative;z-index:2;margin-bottom:14px;display:inline-block;}
.nerai-logo-brand{display:inline-flex;align-items:center;gap:6px;line-height:1;}
.nerai-logo-hex{font-size:3rem;color:#00d4aa;}
.nerai-logo-ner{font-size:4.4rem;font-weight:900;letter-spacing:0.04em;
    font-family:'Inter',sans-serif;color:#ffffff;}
.nerai-logo-ai{font-size:4.4rem;font-weight:900;letter-spacing:0.04em;
    font-family:'Inter',sans-serif;
    background:linear-gradient(135deg,#00d4aa 0%,#0077a8 100%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.nerai-logo-ring,.nerai-logo-ring-2{display:none;}
@keyframes logo-hex-pulse{0%,100%{opacity:0.9;}50%{opacity:1;}}
@keyframes logo-text-glow{0%,100%{opacity:0.95;}50%{opacity:1;}}

/* TAGLINE */
.hero-tagline{font-size:0.8rem;letter-spacing:0.3em;text-transform:uppercase;
    color:rgba(0,212,170,0.8);font-family:'Inter',sans-serif;margin:8px 0 28px;}
.hex-deco{display:none;}

/* HOME STATS */
.home-stat-row{display:flex;justify-content:center;gap:50px;margin-bottom:30px;position:relative;z-index:2;}
.home-stat{text-align:center;}
.home-stat-val{font-size:2rem;font-weight:700;color:#00d4aa;font-family:'Inter',sans-serif;}
.home-stat-lbl{font-size:0.6rem;letter-spacing:0.18em;color:rgba(0,212,170,0.7);text-transform:uppercase;}

/* HOME MODULES */
.home-module{background:#ffffff;border:1px solid rgba(0,119,168,0.16);
    border-radius:14px;padding:30px 22px 24px;text-align:center;
    position:relative;overflow:hidden;min-height:190px;
    display:flex;flex-direction:column;align-items:center;justify-content:center;
    transition:box-shadow 0.25s,transform 0.25s;
    box-shadow:0 2px 12px rgba(13,31,60,0.07);}
.home-module:hover{box-shadow:0 8px 32px rgba(0,119,168,0.16);transform:translateY(-4px);}
.home-module::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,#0077a8,#00d4aa);}
.home-module-icon{font-size:2.8rem;margin-bottom:12px;line-height:1;}
.home-module-title{font-size:0.9rem;font-weight:700;color:#0d1f3c;
    letter-spacing:0.06em;text-transform:uppercase;margin-bottom:8px;}
.home-module-desc{font-size:0.67rem;color:#5a6b82;line-height:1.6;}
.home-module-btn{
    margin-top:16px;padding:7px 20px;
    background:#e8f0f8;border:1px solid rgba(0,119,168,0.25);
    border-radius:6px;color:#0077a8;font-size:0.68rem;font-family:'Inter',sans-serif;
    cursor:pointer;transition:all 0.2s;display:inline-block;}
.home-module-btn:hover{background:#0077a8;color:#ffffff;border-color:#0077a8;}

/* PEAK NEWS */
.peak-news-box{background:#ffffff;border:1px solid rgba(0,119,168,0.2);
    border-radius:10px;padding:14px 16px;margin-top:10px;}
.peak-date-badge{background:rgba(0,119,168,0.1);border:1px solid rgba(0,119,168,0.25);
    border-radius:4px;padding:2px 8px;font-size:0.6rem;color:#0077a8;
    display:inline-block;margin-bottom:8px;}
.peak-news-item{padding:7px 0;border-bottom:1px solid rgba(0,119,168,0.08);}
.peak-news-item:last-child{border-bottom:none;}
.peak-news-headline{font-size:0.75rem;color:#0d1f3c;line-height:1.4;}
.peak-news-src{font-size:0.58rem;color:#0077a8;margin-top:2px;}
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
GLOW_COLORS = ['#0077a8','#00d4aa','#f59e0b','#e05060','#00b4d8',
               '#5a6b82','#0099cc','#f0c75e','#c97a8a','#7ec8b8']

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
    paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(244,247,251,0.8)',
    font=dict(family='Inter,sans-serif',color='#5a6b82',size=11),
    margin=dict(l=45,r=15,t=38,b=40),
    xaxis=dict(gridcolor='rgba(0,119,168,0.1)',linecolor='rgba(0,119,168,0.15)',
               tickfont=dict(size=10,color='#5a6b82')),
    yaxis=dict(gridcolor='rgba(0,119,168,0.1)',linecolor='rgba(0,119,168,0.15)',
               tickfont=dict(size=10,color='#5a6b82')),
)

# ═══════════════════════════════════════════════════════════════
# DATA LOAD
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def load_data(filepath='./indices.csv'):
    if os.path.exists(filepath):
        df = pd.read_csv(filepath,sep=',',header=0,index_col=[0,1])
        df.columns = pd.to_datetime(df.columns,format='%Y%m%d')
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
        if method=='Score (0–100)':
            mn,mx = row.min(),row.max()
            out.loc[c] = (row-mn)/(mx-mn)*100 if mx>mn else row*0
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
                                line=dict(color='white',width=1.5)),
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
        legend=dict(bgcolor='rgba(0,0,0,0)',bordercolor='rgba(0,100,180,0.2)',
                    borderwidth=1,font=dict(size=10)),
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
        [[0,'#e8f0f8'],[0.25,'#00b4d8'],
         [0.5,'#0077a8'],[0.75,'#f59e0b'],[1,'#e05060']]
        if method!='Z-Score' else
        [[0,'#00d4aa'],[0.35,'#e8f0f8'],
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
        colorscale=[[0,'#e8f0f8'],[0.3,'#00b4d8'],
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
                 landcolor='#e8f0f8',showocean=True,
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
    RANK_PALETTE = ['#00b4d8','#0077a8','#00d4aa','#f59e0b','#e05060','#5a6b82','#c97a8a','#7ec8b8','#f0c75e','#0099cc','#e06030','#00c4a0']
    colors = [RANK_PALETTE[i % len(RANK_PALETTE)] for i in range(n_rows)]
    fig = go.Figure(go.Bar(
        x=row['value'],y=row['name'],orientation='h',
        marker=dict(color=colors,line=dict(color='rgba(0,119,168,0.15)',width=0.5)),
        hovertemplate='<b>%{y}</b><br>Value: %{x:.4f}<extra></extra>'
    ))
    t = {**BASE_THEME}
    t['xaxis'] = dict(gridcolor='rgba(0,119,168,0.1)',tickfont=dict(size=10,color='#5a6b82'))
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
                      font=dict(family='Inter,sans-serif',color='#5a6b82'),
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
            pct    = (recent-prev7)/(abs(prev7)+1e-10)*100
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
    """Google News RSS (primary) + GDELT fallback ile haber çeker. Son 2 gün filtresi."""
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
    """Belirli bir peak tarihi için ülke+topic haberleri (Google News + GDELT fallback)."""
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
    <div style='padding:10px 0 18px;border-bottom:1px solid rgba(0,150,255,0.15);margin-bottom:16px;'>
      <div style='font-size:1.35rem;font-weight:900;letter-spacing:0.1em;
           font-family:"Exo 2",sans-serif;line-height:1.1;'>
        <span style='color:rgba(0,230,255,0.95);
             text-shadow:0 0 14px rgba(0,210,255,0.9),0 0 30px rgba(0,160,255,0.45);'>◈</span>
        <span style='color:#ffffff;
             text-shadow:0 0 18px rgba(0,210,255,0.35),0 0 35px rgba(0,140,255,0.15);'> NER</span><span style='background:linear-gradient(135deg,#00e5ff,#0099ff,#8b3fff);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;
             background-clip:text;'>AI</span>
      </div>
      <div style='font-size:0.58rem;color:rgba(0,210,255,0.55);letter-spacing:0.28em;
           font-family:"Share Tech Mono",monospace;margin-top:3px;'>
        INTELLIGENCE HUB
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Navigation ──────────────────────────────────────────
    st.markdown('<div class="sec-hdr">Navigation</div>', unsafe_allow_html=True)

    nav_pages = [
        ('home',        '🏠  HOME'),
        ('indices',     '📊  INDICES'),
        ('profile',     '🎯  COUNTRY PROFILE'),
        ('news',        '📰  NEWS'),
        ('predictions', '🔮  PREDICTIONS'),
        ('insights',    '🔍  INSIGHTS'),
    ]
    for page_key, page_label in nav_pages:
        active_style = 'border-color:rgba(0,180,255,0.5) !important;color:#00e5ff !important;background:rgba(0,50,110,0.4) !important;' if st.session_state.page == page_key else ''
        if st.button(page_label, key=f'nav_{page_key}'):
            st.session_state.page = page_key
            st.rerun()

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
                               for t in sorted(pred_df['topic'].unique())}
            pred_label = st.selectbox(
                "pred_topic", list(topic_display_p.values()),
                index=list(topic_display_p.values()).index('Political Instability')
                      if 'Political Instability' in topic_display_p.values() else 0,
                label_visibility='collapsed')
            sel_pred_topic = [k for k,v in topic_display_p.items() if v==pred_label][0]

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
            pred_hist_months = st.slider("hist_months", 12, 60, 24,
                                         label_visibility='collapsed')
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
                  <div style="font-size:0.72rem;color:#a0c0d8;font-weight:600;margin-bottom:4px;">
                    {n1}
                  </div>
                  <div style="font-size:0.55rem;color:rgba(123,47,255,0.6);
                       font-family:monospace;margin-bottom:4px;">↔ VS ↔</div>
                  <div style="font-size:0.72rem;color:#a0c0d8;font-weight:600;margin-bottom:8px;">
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
              <div style="font-size:0.65rem;color:#8ab0cc;margin-bottom:4px;">
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
    df_recent     = apply_norm(df_recent_raw, norm_method)
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
        nm_color = {'Raw':'#8ba3bc','Score (0–100)':'#00b4d8','Z-Score':'#0077a8'}[norm_method]
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
            changes = ((last-prev)/(prev.abs()+1e-10)*100).dropna()
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
                                        <a href="{url}" target="_blank" style="color:#b8d0e8;text-decoration:none;">
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
                <div style="font-size:0.85rem;font-weight:600;color:#c8d8e8;margin-bottom:5px;">
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
                      <div style="background:{col};width:{s:.0f}%;height:3px;
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
                    <div style="font-size:0.75rem;font-weight:600;color:#c8d8e8;">
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
                    <div style="font-size:0.75rem;font-weight:600;color:#c8d8e8;">
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
                <div style="background:{color};width:{avg_v:.0f}%;height:3px;border-radius:3px;box-shadow:0 0 6px {color}70;"></div>
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
        legend=dict(bgcolor='rgba(0,0,0,0)',bordercolor='rgba(0,100,180,0.2)',
                    borderwidth=1,font=dict(size=10)),hovermode='x unified')
    st.plotly_chart(fig_bi, use_container_width=True, config={'displayModeBar':False})
    _render_footer()


# ═══════════════════════════════════════════════════════════════
# PAGE: NEWS
# ═══════════════════════════════════════════════════════════════
def render_news():
    st.markdown(f"""
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
          <div style="font-size:1.1rem;font-weight:700;color:#00e5ff;letter-spacing:0.08em;">
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
                       style="color:#c8d8e8;text-decoration:none;">
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
          <div style='font-size:1.1rem;font-weight:700;color:#00e5ff;
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
        if topic in df.index.get_level_values('topic') and \
           country in df.index.get_level_values('country'):
            try:
                hist_max = float(df.xs(topic, level='topic').loc[country].max())
            except Exception:
                hist_max = None
            if hist_max and hist_max > 0:
                return yhat_vals / hist_max * 100
        return yhat_vals * 1000   # fallback: scale small raw values

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

        # Historical line
        if hist_series is not None and len(hist_series) > 0:
            fig_fc.add_trace(go.Scatter(
                x=hist_series.index, y=hist_series.values,
                name='Historical (monthly avg)',
                mode='lines',
                line=dict(color='#00b4d8', width=2),
                hovertemplate='%{x|%b %Y}: %{y:.1f}<extra>Historical</extra>'
            ))

        if len(fc) > 0:
            # Normalise forecast to same scale
            if hist_series is not None and hist_series.max() > 0:
                raw_hist_max = float(df.xs(sel_pred_topic, level='topic')
                                       .loc[sel_pred_country].max()) \
                               if (sel_pred_topic in df.index.get_level_values('topic') and
                                   sel_pred_country in df.index.get_level_values('country')) \
                               else 1.0
                scale = 100 / raw_hist_max if raw_hist_max > 0 else 1.0
            else:
                scale = 1.0

            yhat   = fc['yhat']       * scale
            y_lo   = fc['yhat_lower'] * scale
            y_hi   = fc['yhat_upper'] * scale

            # Confidence band
            fig_fc.add_trace(go.Scatter(
                x=pd.concat([fc['ds'], fc['ds'].iloc[::-1]]),
                y=pd.concat([y_hi, y_lo.iloc[::-1]]),
                fill='toself',
                fillcolor='rgba(123,47,255,0.10)',
                line=dict(color='rgba(0,0,0,0)'),
                name='90% Confidence',
                hoverinfo='skip',
                showlegend=True,
            ))
            # Forecast line
            fig_fc.add_trace(go.Scatter(
                x=fc['ds'], y=yhat,
                name='12-Month Forecast',
                mode='lines+markers',
                line=dict(color='#0077a8', width=2.5, dash='dot'),
                marker=dict(size=5, color='#0077a8'),
                hovertemplate='%{x|%b %Y}: %{y:.1f}<extra>Forecast</extra>'
            ))

            # Today marker
            today = pd.Timestamp.now().normalize()
            fig_fc.add_vline(x=today, line_width=1,
                             line_dash='dash', line_color='rgba(0,200,255,0.3)')
            fig_fc.add_annotation(
                x=today, y=1, yref='paper',
                text='TODAY', showarrow=False,
                font=dict(size=9, color='rgba(0,200,255,0.45)'),
                xanchor='left', yanchor='bottom'
            )

        t_fc = {**BASE_THEME}
        t_fc['yaxis'] = {**t_fc.get('yaxis', {}),
                         'title': 'Risk Score (0–100)', 'title_font': dict(size=10)}
        fig_fc.update_layout(
            **t_fc, height=500,
            legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='rgba(0,100,180,0.2)',
                        borderwidth=1, font=dict(size=10)),
            hovermode='x unified'
        )
        st.plotly_chart(fig_fc, use_container_width=True, config={'displayModeBar': False})

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
                    <div style='font-size:0.68rem;color:#a8c0d8;white-space:nowrap;
                         overflow:hidden;text-overflow:ellipsis;'>{row["label"]}</div>
                    <div style='background:rgba(0,0,0,0.3);border-radius:2px;
                         height:2px;width:100%;margin-top:3px;'>
                      <div style='background:{col_d};width:{bar_w:.0f}%;height:2px;
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
                    <div style='font-size:0.73rem;color:#c8d8e8;'>{lbl}</div>
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
                    <div style='font-size:0.73rem;color:#c8d8e8;'>{lbl}</div>
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
                change_pcts[country] = (r_mean - p_mean) / (p_mean + 1e-15) * 100 if p_mean > 1e-15 else 0.0
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
                     f"<span style='color:#a8c0d8;font-size:0.63rem;white-space:nowrap;"
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
      <div style='font-size:0.98rem;font-weight:700;color:#e8f4ff;
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
                color = "#ff6b6b" if pct > 15 else "#ffa94d" if pct > 5 else "#74c0fc" if pct < -5 else "#a9e34b"
                arrow = "▲" if pct > 0 else "▼"
                trend_items.append((abs(pct), pct,
                    f"<span style='color:{color};'><b>{arrow} {lbl}</b> {direction} <b>{pct:+.1f}%</b></span>"))
        except Exception:
            pass

        trend_items.sort(key=lambda x: -x[0])

        if trend_items:
            phrases = [s for _, _, s in trend_items[:5]]
            section1_html = (
                f"<p style='color:#c8ddf0;font-size:0.73rem;line-height:1.75;margin:0 0 4px;'>"
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
                    col = "#74c0fc"
                    sentence = (f"<b>{lbl}</b> is projected to "
                                f"<span style='color:{col};'>ease <b>{pct_12m:+.1f}%</b></span> "
                                f"by {ds_str} (3-month: {pct_3m:+.1f}%)")
                pred_items.append((abs(pct_12m), pct_12m, sentence))

            pred_items.sort(key=lambda x: -x[0])

        if pred_items:
            pred_phrases = [s for _, _, s in pred_items[:5]]
            section2_html = (
                f"<p style='color:#c8ddf0;font-size:0.73rem;line-height:1.75;margin:0 0 4px;'>"
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
            assess_color = "#74c0fc"
            assess_text  = (
                f"<b>{cname}</b> demonstrates an <span style='color:#74c0fc;'><b>improving risk outlook</b></span>. "
                f"Recent indices are easing, and the 12-month model confirms continued de-escalation on most fronts."
            )
        elif net_trend < -5:
            assess_color = "#a9e34b"
            assess_text  = (
                f"<b>{cname}</b> is experiencing <span style='color:#a9e34b;'><b>short-term de-escalation</b></span>, "
                f"though longer-term projections remain uncertain. The situation should continue to be monitored."
            )
        elif net_pred < -5:
            assess_color = "#74c0fc"
            assess_text  = (
                f"<b>{cname}</b> shows a <span style='color:#74c0fc;'><b>positive medium-term outlook</b></span> "
                f"according to model projections, despite limited movement in recent indices."
            )
        else:
            assess_color = "#94a3b8"
            assess_text  = (
                f"<b>{cname}</b> presents a <span style='color:#94a3b8;'><b>stable-to-uncertain</b></span> picture. "
                f"No strong directional signal is present in either the current data window or forward projections."
            )

        country_blocks.append(f"""
<div style='background:rgba(5,15,40,0.6);border:1px solid rgba(0,120,200,0.18);
     border-radius:8px;padding:14px 16px;margin-bottom:12px;'>
  <div style='font-size:0.82rem;font-weight:700;color:#ddeeff;letter-spacing:0.04em;
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
  <p style='color:#e2e8f0;font-size:0.73rem;line-height:1.75;margin:0;'>{assess_text}</p>
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


def render_insights():
    # ── Page header ─────────────────────────────────────────────
    st.markdown("""
<div style='padding:10px 0 6px;'>
  <div style='font-size:1.55rem;font-weight:800;color:#e8f4ff;letter-spacing:0.04em;'>
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
  <div style='font-size:0.95rem;font-weight:700;color:#b8d8ff;margin-bottom:4px;'>
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

    if qa_question and qa_question.strip():
        with st.spinner("Analysing data…"):
            answer_html = _answer_question(
                qa_question, df, trend_df, pred_df, insights_df)
        st.markdown(answer_html, unsafe_allow_html=True)
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
                st.markdown(f"<div style='display:flex;justify-content:space-between;padding:4px 8px;margin-bottom:3px;background:rgba(255,75,110,0.05);border:1px solid rgba(255,75,110,0.12);border-radius:5px;'><div><div style='font-size:0.72rem;color:#c8d8e8;'>{lbl}</div><div style='font-size:0.58rem;color:rgba(0,150,255,0.5);font-family:monospace;'>{cnt}</div></div><div style='font-size:0.82rem;font-weight:700;color:#e05060;font-family:monospace;'>+{r['trend_pct']:.1f}%</div></div>", unsafe_allow_html=True)
        with cf2:
            st.markdown("<div style='font-size:0.62rem;color:rgba(0,255,157,0.7);font-family:monospace;margin-bottom:8px;'>▼ HIGHEST FALLING</div>", unsafe_allow_html=True)
            for _, r in trend_df.nsmallest(15, 'trend_pct').iterrows():
                lbl = TOPIC_LABELS.get(r['topic'], str(r['topic']).replace('_',' ').title())
                cnt = COUNTRY_NAMES.get(r['country'], r['country'])
                st.markdown(f"<div style='display:flex;justify-content:space-between;padding:4px 8px;margin-bottom:3px;background:rgba(0,255,157,0.04);border:1px solid rgba(0,255,157,0.10);border-radius:5px;'><div><div style='font-size:0.72rem;color:#c8d8e8;'>{lbl}</div><div style='font-size:0.58rem;color:rgba(0,150,255,0.5);font-family:monospace;'>{cnt}</div></div><div style='font-size:0.82rem;font-weight:700;color:#00d4aa;font-family:monospace;'>{r['trend_pct']:.1f}%</div></div>", unsafe_allow_html=True)

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
# ROUTING
# ═══════════════════════════════════════════════════════════════
page = st.session_state.get('page', 'home')
if   page == 'home':        render_home()
elif page == 'indices':     render_indices()
elif page == 'profile':     render_profile()
elif page == 'news':        render_news()
elif page == 'predictions': render_predictions()
elif page == 'insights':    render_insights()
else:
    st.session_state.page = 'home'
    st.rerun()
