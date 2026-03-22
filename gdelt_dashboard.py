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
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');

.stApp {
    background:#020b18;
    background-image:
        radial-gradient(ellipse at 15% 40%,rgba(0,150,255,0.05) 0%,transparent 55%),
        radial-gradient(ellipse at 85% 15%,rgba(100,0,255,0.06) 0%,transparent 55%),
        radial-gradient(ellipse at 50% 90%,rgba(0,80,180,0.04) 0%,transparent 55%);
}
html,body,[class*="css"]{font-family:'Exo 2',sans-serif;color:#c8d8e8;}

[data-testid="stSidebar"]{
    background:rgba(2,8,20,0.97);
    border-right:1px solid rgba(0,150,255,0.12);
}
[data-testid="stSidebar"] label{
    color:#00b4ff !important;font-size:0.7rem !important;
    letter-spacing:0.15em;text-transform:uppercase;
}

/* NAV BUTTONS */
[data-testid="stSidebar"] .stButton>button{
    background:rgba(0,20,50,0.6) !important;
    border:1px solid rgba(0,150,255,0.18) !important;
    color:#7ab4d8 !important;
    font-family:'Share Tech Mono',monospace !important;
    font-size:0.72rem !important;letter-spacing:0.12em !important;
    border-radius:6px !important;width:100% !important;
    text-align:left !important;padding:9px 14px !important;
    transition:all 0.25s !important;margin-bottom:3px !important;
}
[data-testid="stSidebar"] .stButton>button:hover{
    border-color:rgba(0,180,255,0.55) !important;
    color:#00e5ff !important;
    background:rgba(0,50,110,0.5) !important;
    box-shadow:0 0 14px rgba(0,150,255,0.2) !important;
}

/* KPI */
.kpi-card{
    background:linear-gradient(135deg,rgba(0,18,40,0.95),rgba(0,8,22,0.95));
    border:1px solid rgba(0,150,255,0.2);border-radius:10px;padding:16px 18px;
    position:relative;overflow:hidden;
    box-shadow:0 4px 24px rgba(0,0,0,0.4),inset 0 1px 0 rgba(255,255,255,0.04);
    transition:border-color 0.3s;
}
.kpi-card:hover{border-color:rgba(0,180,255,0.45);}
.kpi-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,transparent,var(--accent,#00b4ff),transparent);}
.kpi-label{font-size:0.65rem;letter-spacing:0.2em;text-transform:uppercase;
    color:rgba(0,180,255,0.6);font-family:'Share Tech Mono',monospace;margin-bottom:4px;}
.kpi-value{font-size:2.1rem;font-weight:700;line-height:1;color:#fff;
    text-shadow:0 0 24px rgba(0,180,255,0.4);}
.kpi-sub{font-size:0.68rem;margin-top:5px;font-family:'Share Tech Mono',monospace;}
.kpi-up{color:#00ff9d;}.kpi-down{color:#ff4b6e;}.kpi-neu{color:#556;}
.badge-low{color:#00ff9d;font-size:0.6rem;background:rgba(0,255,157,0.08);
    border:1px solid rgba(0,255,157,0.25);border-radius:3px;padding:1px 6px;}
.badge-med{color:#ffd700;font-size:0.6rem;background:rgba(255,215,0,0.08);
    border:1px solid rgba(255,215,0,0.25);border-radius:3px;padding:1px 6px;}
.badge-high{color:#ff6b35;font-size:0.6rem;background:rgba(255,107,53,0.1);
    border:1px solid rgba(255,107,53,0.3);border-radius:3px;padding:1px 6px;}
.badge-crit{color:#ff4b6e;font-size:0.6rem;background:rgba(255,75,110,0.1);
    border:1px solid rgba(255,75,110,0.35);border-radius:3px;padding:1px 6px;}

/* HERO */
.hero-title{font-size:2.2rem;font-weight:700;letter-spacing:0.07em;
    background:linear-gradient(90deg,#00b4ff 0%,#7b2fff 45%,#00e5ff 100%);
    background-size:200% auto;-webkit-background-clip:text;
    -webkit-text-fill-color:transparent;animation:shine 5s linear infinite;}
@keyframes shine{to{background-position:200% center;}}
.hero-sub{font-size:0.72rem;letter-spacing:0.22em;text-transform:uppercase;
    color:rgba(0,180,255,0.45);font-family:'Share Tech Mono',monospace;}
.live-dot{display:inline-block;width:7px;height:7px;border-radius:50%;
    background:#00ff9d;box-shadow:0 0 8px #00ff9d;
    animation:pulse 2s infinite;margin-right:5px;vertical-align:middle;}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(.8)}}

/* SECTION HEADER */
.sec-hdr{font-size:0.65rem;letter-spacing:0.25em;text-transform:uppercase;
    color:rgba(0,150,255,0.55);font-family:'Share Tech Mono',monospace;
    padding:8px 0 6px;border-bottom:1px solid rgba(0,150,255,0.1);margin-bottom:12px;}

/* SIGNAL CARD */
.signal-card{background:rgba(0,15,35,0.7);border:1px solid rgba(0,150,255,0.12);
    border-radius:8px;padding:10px 14px;margin-bottom:8px;
    display:flex;align-items:center;justify-content:space-between;}
.signal-name{font-size:0.75rem;color:#a0c0d8;font-weight:600;}
.signal-topic{font-size:0.62rem;color:rgba(0,150,255,0.5);font-family:'Share Tech Mono',monospace;}
.signal-val{font-size:1rem;font-weight:700;color:#fff;text-align:right;}

/* NORM BADGE */
.norm-raw{color:#8ba3bc;}.norm-score{color:#00b4ff;}.norm-z{color:#7b2fff;}

/* DIVIDER */
.h-div{height:1px;background:linear-gradient(90deg,transparent,rgba(0,150,255,0.15),transparent);margin:12px 0;}

#MainMenu,footer,.stDeployButton{visibility:hidden;display:none;}
::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-thumb{background:rgba(0,150,255,0.25);border-radius:2px;}

/* BILATERAL */
.vs-badge{display:inline-block;background:rgba(123,47,255,0.18);
    border:1px solid rgba(123,47,255,0.45);border-radius:50%;
    width:38px;height:38px;line-height:38px;text-align:center;
    font-size:0.72rem;font-weight:700;color:#7b2fff;font-family:monospace;}
.relation-status{border-radius:10px;padding:18px 12px;text-align:center;
    background:linear-gradient(135deg,rgba(0,15,40,0.95),rgba(15,0,40,0.9));margin:4px 0;}
.metric-mini{background:rgba(0,10,28,0.75);border:1px solid rgba(0,150,255,0.12);
    border-radius:8px;padding:12px 10px;text-align:center;}
.metric-mini-label{font-size:0.58rem;letter-spacing:0.15em;text-transform:uppercase;
    color:rgba(0,180,255,0.45);font-family:'Share Tech Mono',monospace;margin-bottom:4px;}
.metric-mini-val{font-size:1.5rem;font-weight:700;line-height:1.1;}
.pair-card{background:rgba(0,10,28,0.7);border:1px solid rgba(0,150,255,0.1);
    border-radius:8px;padding:11px 15px;margin-bottom:7px;
    display:flex;align-items:center;gap:12px;}

/* COUNTRY PROFILE */
.prof-header{background:linear-gradient(135deg,rgba(0,18,50,0.97),rgba(10,0,45,0.95));
    border:1px solid rgba(0,150,255,0.2);border-radius:10px;
    padding:14px 20px;margin-bottom:14px;
    display:flex;align-items:center;justify-content:space-between;
    box-shadow:0 4px 20px rgba(0,0,0,0.4);}
.prof-country{font-size:1.25rem;font-weight:700;color:#fff;letter-spacing:0.06em;}
.prof-sub{font-size:0.6rem;color:rgba(0,180,255,0.4);
    font-family:'Share Tech Mono',monospace;letter-spacing:0.15em;margin-top:3px;}
.prof-section-title{font-size:0.58rem;letter-spacing:0.22em;text-transform:uppercase;
    color:rgba(0,150,255,0.5);font-family:'Share Tech Mono',monospace;
    padding-bottom:5px;border-bottom:1px solid rgba(0,150,255,0.1);margin-bottom:9px;}
.idx-row{display:flex;align-items:center;justify-content:space-between;
    padding:6px 0;border-bottom:1px solid rgba(0,100,180,0.07);}
.idx-label{font-size:0.72rem;color:#8ab0cc;}
.idx-val{font-size:0.82rem;font-weight:700;}
.idx-bar-bg{background:rgba(0,0,0,0.35);border-radius:3px;height:3px;margin-top:3px;}
.alarm-row{background:rgba(0,12,32,0.75);border:1px solid rgba(0,150,255,0.1);
    border-radius:7px;padding:8px 11px;margin-bottom:6px;
    display:flex;align-items:center;justify-content:space-between;}
.alarm-label{font-size:0.72rem;color:#9ab8cc;font-weight:600;}
.alarm-meta{font-size:0.58rem;color:rgba(0,150,255,0.4);
    font-family:'Share Tech Mono',monospace;margin-top:2px;}
.rel-compact{background:rgba(0,10,28,0.75);border-radius:7px;padding:8px 12px;
    margin-bottom:5px;display:flex;align-items:center;justify-content:space-between;
    border-left:3px solid transparent;}

/* NEWS CARD */
.news-card{background:rgba(0,12,32,0.85);border:1px solid rgba(0,150,255,0.12);
    border-radius:10px;padding:14px 16px;margin-bottom:10px;
    transition:border-color 0.3s;}
.news-card:hover{border-color:rgba(0,180,255,0.3);}
.news-title{font-size:0.82rem;color:#c8d8e8;font-weight:600;line-height:1.45;}
.news-source{font-size:0.62rem;color:rgba(0,150,255,0.5);font-family:monospace;margin-top:4px;}
.news-date{font-size:0.6rem;color:rgba(100,150,200,0.4);font-family:monospace;}
.news-url{font-size:0.6rem;color:rgba(0,180,255,0.35);}

/* CAT BUTTON - news categories */
.cat-item{background:rgba(0,15,40,0.7);border:1px solid rgba(0,150,255,0.1);
    border-radius:6px;padding:7px 12px;margin-bottom:4px;cursor:pointer;
    font-size:0.68rem;color:#7ab4d8;font-family:'Share Tech Mono',monospace;
    letter-spacing:0.1em;transition:all 0.2s;display:block;}
.cat-item:hover,.cat-item.active{border-color:rgba(0,180,255,0.45);
    color:#00e5ff;background:rgba(0,40,90,0.5);}

/* HOME PAGE */
.home-hero{
    background:linear-gradient(135deg,rgba(0,10,30,0.97),rgba(5,0,25,0.95));
    border:1px solid rgba(0,150,255,0.15);border-radius:16px;
    padding:50px 40px;margin-bottom:32px;position:relative;overflow:hidden;
    text-align:center;
}
.home-hero::before{content:'';position:absolute;inset:0;
    background:radial-gradient(ellipse at 50% 0%,rgba(0,100,255,0.08) 0%,transparent 70%);
    pointer-events:none;}
.home-ring{position:absolute;border-radius:50%;border:1px solid rgba(0,150,255,0.07);
    animation:ring-expand 4s ease-out infinite;}
.home-ring:nth-child(2){width:300px;height:300px;top:calc(50% - 150px);left:calc(50% - 150px);animation-delay:0s;}
.home-ring:nth-child(3){width:500px;height:500px;top:calc(50% - 250px);left:calc(50% - 250px);animation-delay:1.3s;}
.home-ring:nth-child(4){width:700px;height:700px;top:calc(50% - 350px);left:calc(50% - 350px);animation-delay:2.6s;}
@keyframes ring-expand{
    0%{opacity:0.5;transform:scale(0.85);}
    100%{opacity:0;transform:scale(1.1);}
}
.home-nerai{font-size:3.5rem;font-weight:700;letter-spacing:0.15em;
    background:linear-gradient(90deg,#00b4ff 0%,#7b2fff 40%,#00e5ff 80%,#00b4ff 100%);
    background-size:300% auto;-webkit-background-clip:text;
    -webkit-text-fill-color:transparent;animation:shine 6s linear infinite;}
.home-sub-title{font-size:0.9rem;letter-spacing:0.4em;text-transform:uppercase;
    color:rgba(0,180,255,0.5);font-family:'Share Tech Mono',monospace;
    margin:10px 0 30px;}
.home-stat-row{display:flex;justify-content:center;gap:50px;margin-bottom:30px;}
.home-stat{text-align:center;}
.home-stat-val{font-size:2rem;font-weight:700;color:#00b4ff;
    text-shadow:0 0 20px rgba(0,180,255,0.4);font-family:'Share Tech Mono',monospace;}
.home-stat-lbl{font-size:0.6rem;letter-spacing:0.2em;color:rgba(0,180,255,0.4);
    text-transform:uppercase;font-family:monospace;}

/* HOME MODULE TILES */
.home-module{
    background:linear-gradient(135deg,rgba(0,18,50,0.92),rgba(0,8,30,0.92));
    border:1px solid rgba(0,150,255,0.15);border-radius:14px;
    padding:30px 22px 24px;text-align:center;position:relative;overflow:hidden;
    min-height:190px;display:flex;flex-direction:column;align-items:center;justify-content:center;
}
.home-module::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,transparent,var(--mc,#00b4ff),transparent);}
.home-module-icon{font-size:2.8rem;margin-bottom:12px;line-height:1;}
.home-module-title{font-size:1rem;font-weight:700;color:#e0f0ff;
    letter-spacing:0.12em;text-transform:uppercase;margin-bottom:8px;}
.home-module-desc{font-size:0.67rem;color:rgba(100,180,220,0.55);line-height:1.6;}
.home-module-btn{
    margin-top:16px;padding:7px 20px;
    background:rgba(0,100,200,0.15);
    border:1px solid rgba(0,150,255,0.3);border-radius:5px;
    color:#00b4ff;font-size:0.68rem;font-family:'Share Tech Mono',monospace;
    letter-spacing:0.1em;cursor:pointer;transition:all 0.2s;display:inline-block;
}

/* PEAK NEWS */
.peak-news-box{background:rgba(0,10,28,0.85);border:1px solid rgba(123,47,255,0.25);
    border-radius:10px;padding:14px 16px;margin-top:10px;}
.peak-date-badge{background:rgba(123,47,255,0.15);border:1px solid rgba(123,47,255,0.3);
    border-radius:4px;padding:2px 8px;font-size:0.6rem;color:#a070ff;
    font-family:monospace;display:inline-block;margin-bottom:8px;}
.peak-news-item{padding:7px 0;border-bottom:1px solid rgba(0,100,180,0.08);}
.peak-news-item:last-child{border-bottom:none;}
.peak-news-headline{font-size:0.75rem;color:#b8d0e8;line-height:1.4;}
.peak-news-src{font-size:0.58rem;color:rgba(0,150,255,0.4);font-family:monospace;margin-top:2px;}
</style>
""", unsafe_allow_html=True)

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
GLOW_COLORS = ['#00b4ff','#7b2fff','#00ff9d','#ff6b35','#ff4b6e',
               '#ffd700','#00e5ff','#e040fb','#69ff47','#ff6e40']

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
    ('political_crisis','Political Crisis','#e040fb'),
    ('military_clash','War Risk','#ff4b6e'),
    ('threaten_in_international_relations','Intl. Threats','#ff6b35'),
    ('military_escalation','Military Escalation','#ffd700'),
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
    paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,8,22,0.7)',
    font=dict(family='Exo 2,sans-serif',color='#7a9ab8',size=11),
    margin=dict(l=45,r=15,t=38,b=40),
    xaxis=dict(gridcolor='rgba(0,100,180,0.1)',linecolor='rgba(0,100,180,0.15)',
               tickfont=dict(size=10,color='#4a6a8a')),
    yaxis=dict(gridcolor='rgba(0,100,180,0.1)',linecolor='rgba(0,100,180,0.15)',
               tickfont=dict(size=10,color='#4a6a8a')),
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
        fig.add_hline(y=2,line_dash='dot',line_color='rgba(255,75,110,0.4)',
                      annotation_text='Alert (+2σ)',annotation_font_size=9)
        fig.add_hline(y=-2,line_dash='dot',line_color='rgba(0,255,157,0.3)',
                      annotation_text='-2σ',annotation_font_size=9)
    t = {**BASE_THEME}
    t['yaxis'] = {**t['yaxis'],'title':y_label,'title_font':dict(size=10)}
    fig.update_layout(**t, height=340,
        title=dict(text=title,font=dict(size=12,color='#6a9ab8'),x=0.01),
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
        [[0,'rgba(0,10,30,1)'],[0.25,'rgba(0,60,120,1)'],
         [0.5,'rgba(0,130,200,1)'],[0.75,'rgba(100,0,200,1)'],[1,'rgba(255,50,100,1)']]
        if method!='Z-Score' else
        [[0,'rgba(0,80,160,1)'],[0.35,'rgba(0,20,50,1)'],
         [0.5,'rgba(10,10,30,1)'],[0.65,'rgba(80,0,120,1)'],[1,'rgba(255,50,100,1)']]
    )
    fig = go.Figure(go.Heatmap(
        z=matrix,x=xlabels,y=ylabels,colorscale=colorscale,
        hovertemplate='<b>%{y}</b><br>%{x}<br>Value: %{z:.3f}<extra></extra>',
        showscale=True,colorbar=dict(thickness=7,len=0.85,
            tickfont=dict(size=8,color='#4a6a8a'),outlinewidth=0)
    ))
    t = {**BASE_THEME}
    t['xaxis'] = dict(showticklabels=True,tickangle=-45,
                      tickfont=dict(size=8,color='#4a6a8a'),gridcolor='rgba(0,0,0,0)')
    t['yaxis'] = dict(tickfont=dict(size=9,color='#8ab0c8'),gridcolor='rgba(0,0,0,0)')
    fig.update_layout(**t,height=420,
        title=dict(text=f'Top {top_n} Countries — Heatmap',
                   font=dict(size=12,color='#6a9ab8'),x=0.01))
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
        colorscale=[[0,'rgba(0,15,40,1)'],[0.3,'rgba(0,80,160,1)'],
                    [0.6,'rgba(80,0,180,1)'],[0.85,'rgba(200,0,100,1)'],
                    [1,'rgba(255,50,50,1)']],
        autocolorscale=False,marker_line_color='rgba(0,100,180,0.3)',
        marker_line_width=0.5,
        colorbar=dict(title=dict(text='Score',font=dict(size=9,color='#4a6a8a')),
                      thickness=7,len=0.55,tickfont=dict(size=8,color='#4a6a8a'),
                      outlinewidth=0,bgcolor='rgba(0,0,0,0)'),
        hovertemplate='<b>%{text}</b><br>Value: %{z:.3f}<extra></extra>'
    ))
    t = {**BASE_THEME}
    fig.update_layout(**t,height=330,
        title=dict(text=f'Global Risk Map — {pd.Timestamp(date_col).strftime("%d %b %Y")}',
                   font=dict(size=12,color='#6a9ab8'),x=0.01),
        geo=dict(bgcolor='rgba(0,0,0,0)',showframe=False,showcoastlines=True,
                 coastlinecolor='rgba(0,100,180,0.25)',showland=True,
                 landcolor='rgba(4,18,42,1)',showocean=True,
                 oceancolor='rgba(0,6,18,1)',showlakes=False,
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
    colors = [f'rgba({int(200*i/max(n_rows-1,1))},{int(120+80*i/max(n_rows-1,1))},{int(220-20*i/max(n_rows-1,1))},0.85)' for i in range(n_rows)]
    fig = go.Figure(go.Bar(
        x=row['value'],y=row['name'],orientation='h',
        marker=dict(color=colors,line=dict(color='rgba(0,180,255,0.2)',width=0.5)),
        hovertemplate='<b>%{y}</b><br>Value: %{x:.4f}<extra></extra>'
    ))
    t = {**BASE_THEME}
    t['xaxis'] = dict(gridcolor='rgba(0,100,180,0.1)',tickfont=dict(size=10,color='#4a6a8a'))
    t['yaxis'] = dict(tickfont=dict(size=10,color='#8ab0c8'),gridcolor='rgba(0,0,0,0)')
    fig.update_layout(**t,height=330,
        title=dict(text='Country Ranking',font=dict(size=12,color='#6a9ab8'),x=0.01))
    return fig

def chart_sparkline(series,color='#00b4ff'):
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
        title={'text':title,'font':{'size':10,'color':'#6a9ab8','family':'Share Tech Mono'}},
        number={'font':{'color':color,'size':30,'family':'Exo 2'},'valueformat':'.0f'},
        gauge={
            'axis':{'range':[0,100],'nticks':5,
                    'tickfont':{'size':8,'color':'#3a5a7a'},'tickcolor':'#2a4a6a'},
            'bar':{'color':color,'thickness':0.22},
            'bgcolor':'rgba(0,0,0,0)','borderwidth':0,
            'steps':[
                {'range':[0,25],'color':'rgba(0,255,157,0.06)'},
                {'range':[25,50],'color':'rgba(255,215,0,0.06)'},
                {'range':[50,75],'color':'rgba(255,107,53,0.08)'},
                {'range':[75,100],'color':'rgba(255,75,110,0.10)'},
            ],
            'threshold':{'line':{'color':color,'width':3},'thickness':0.75,'value':value},
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                      font=dict(family='Exo 2,sans-serif',color='#7a9ab8'),
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
    elif net_score>=65: st_,col_,ico = 'HOSTILE',    '#ff4b6e','⚠️'
    elif net_score>=45: st_,col_,ico = 'TENSE',      '#ff6b35','📈'
    elif net_score>=25: st_,col_,ico = 'CAUTIOUS',   '#ffd700','📊'
    elif net_score>=10: st_,col_,ico = 'STABLE',     '#00b4ff','📉'
    else:               st_,col_,ico = 'COOPERATIVE','#00ff9d','🤝'
    if   trend_7d> 5: tr_txt,tr_col = '▲ DETERIORATING','#ff6b35'
    elif trend_7d> 1: tr_txt,tr_col = '↗ WORSENING',    '#ffd700'
    elif trend_7d<-5: tr_txt,tr_col = '▼ IMPROVING',    '#00ff9d'
    elif trend_7d<-1: tr_txt,tr_col = '↘ EASING',       '#00b4ff'
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
    """GDELT 2.0 API'den en güncel haberleri çeker."""
    try:
        encoded = urllib.parse.quote(query_str)
        url = (f"https://api.gdeltproject.org/api/v2/doc/doc?"
               f"query={encoded}&mode=artlist&maxrecords={max_records}"
               f"&format=json&sort=DateDesc")
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode('utf-8'))
            return data.get('articles', [])
    except Exception:
        return []


@st.cache_data(ttl=1800)
def fetch_peak_news(country, topic, peak_date_str, days_window=3):
    """Belirli bir peak tarihi için ülke+topic kombinasyonu haberleri."""
    try:
        cname  = COUNTRY_NAMES.get(country, country)
        twords = topic.replace('_', ' ')
        pk_dt  = pd.Timestamp(peak_date_str)
        start  = (pk_dt - pd.Timedelta(days=days_window)).strftime('%Y%m%d000000')
        end    = (pk_dt + pd.Timedelta(days=days_window+1)).strftime('%Y%m%d000000')
        query  = f'"{cname}" {twords}'
        encoded = urllib.parse.quote(query)
        url = (f"https://api.gdeltproject.org/api/v2/doc/doc?"
               f"query={encoded}&mode=artlist&maxrecords=5&format=json"
               f"&startdatetime={start}&enddatetime={end}&sort=DateDesc")
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as r:
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

if 'page' not in st.session_state:
    st.session_state.page = 'home'

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='padding:10px 0 18px;border-bottom:1px solid rgba(0,150,255,0.12);margin-bottom:16px;'>
      <div style='font-size:1.15rem;font-weight:700;color:#00b4ff;letter-spacing:0.08em;'>⬡ NERAI</div>
      <div style='font-size:0.6rem;color:rgba(0,180,255,0.35);letter-spacing:0.22em;font-family:monospace;'>
        INTELLIGENCE HUB
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Navigation ──────────────────────────────────────────
    st.markdown('<div class="sec-hdr">Navigation</div>', unsafe_allow_html=True)

    nav_pages = [
        ('home',    '🏠  HOME'),
        ('indices', '📊  INDICES'),
        ('profile', '🎯  COUNTRY PROFILE'),
        ('news',    '📰  NEWS'),
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

# ═══════════════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════════════
def render_home():
    # ── Animated Hero ────────────────────────────────────────
    st.markdown(f"""
    <div class="home-hero">
      <div class="home-ring"></div>
      <div class="home-ring"></div>
      <div class="home-ring"></div>
      <div class="home-nerai">⬡ NERAI</div>
      <div style="font-size:1.6rem;font-weight:300;letter-spacing:0.35em;
           color:rgba(200,220,255,0.6);text-transform:uppercase;margin-top:4px;">
        Intelligence Hub
      </div>
      <div class="home-sub-title">Geopolitical Risk Intelligence Platform</div>
      <div style="height:1px;background:linear-gradient(90deg,transparent,rgba(0,150,255,0.25),transparent);
           width:60%;margin:0 auto 28px;"></div>
      <div class="home-stat-row">
        <div class="home-stat">
          <div class="home-stat-val">{len(all_countries)}</div>
          <div class="home-stat-lbl">Countries</div>
        </div>
        <div class="home-stat">
          <div class="home-stat-val">{len(all_topics)}</div>
          <div class="home-stat-lbl">Risk Topics</div>
        </div>
        <div class="home-stat">
          <div class="home-stat-val">{len(date_cols)}</div>
          <div class="home-stat-lbl">Days of Data</div>
        </div>
        <div class="home-stat">
          <div class="home-stat-val">{len(df):,}</div>
          <div class="home-stat-lbl">Data Points</div>
        </div>
      </div>
      <div style="font-size:0.7rem;color:rgba(0,180,255,0.35);font-family:monospace;letter-spacing:0.1em;">
        <span class="live-dot"></span>
        LIVE · DATA SOURCE: GDELT PROJECT · LAST UPDATE: {date_cols[-1].strftime('%d %b %Y') if len(date_cols) else 'N/A'}
        {'&nbsp;&nbsp;⚠ DEMO MODE' if is_demo else '&nbsp;&nbsp;✓ REAL DATA'}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Module Tiles ─────────────────────────────────────────
    st.markdown("""
    <div style="font-size:0.65rem;letter-spacing:0.3em;text-transform:uppercase;
         color:rgba(0,150,255,0.4);font-family:monospace;margin-bottom:20px;text-align:center;">
      — SELECT A MODULE TO BEGIN —
    </div>""", unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)

    with m1:
        st.markdown("""
        <div class="home-module" style="--mc:#00b4ff">
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
        <div class="home-module" style="--mc:#7b2fff">
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
        <div class="home-module" style="--mc:#00ff9d">
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
                clr = '#ff4b6e' if net>=45 else ('#ffd700' if net>=25 else '#00b4ff')
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
            clr = '#ff4b6e' if val>=50 else ('#ffd700' if val>=25 else '#00b4ff')
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
        nm_color = {'Raw':'#8ba3bc','Score (0–100)':'#00b4ff','Z-Score':'#7b2fff'}[norm_method]
        st.markdown(f"""
        <div style='text-align:right;padding-top:12px;font-family:monospace;
             font-size:0.68rem;color:rgba(0,180,255,0.4);'>
          LAST UPDATE<br>
          <span style='color:#00b4ff;font-size:0.9rem;'>{date_cols[-1].strftime('%d %b %Y')}</span><br>
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
                spark_color = '#ff4b6e' if (norm_method=='Score (0–100)' and val>=60) else \
                              '#ffd700' if (norm_method=='Score (0–100)' and val>=35) else '#00b4ff'
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
                st.markdown('<div style="font-size:0.65rem;color:#00ff9d;letter-spacing:0.15em;margin-bottom:8px;">▼ DECLINING RISK</div>', unsafe_allow_html=True)
                for c,pct in top_dn.items():
                    val = last[c]
                    st.markdown(f"""
                    <div class='signal-card' style='border-color:rgba(0,255,157,0.15);'>
                      <div><div class='signal-name'>{COUNTRY_NAMES.get(c,c)}</div>
                      <div class='signal-topic'>{sel_label}</div></div>
                      <div><div class='signal-val' style='color:#00ff9d;'>{fmt(val,norm_method)}</div>
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
            if   net>=65: badge_cls,badge_txt,bar_col = 'badge-crit','CRITICAL','#ff4b6e'
            elif net>=45: badge_cls,badge_txt,bar_col = 'badge-high','HIGH','#ff6b35'
            elif net>=25: badge_cls,badge_txt,bar_col = 'badge-med','ELEVATED','#ffd700'
            else:         badge_cls,badge_txt,bar_col = 'badge-low','MODERATE','#00b4ff'
            t_sym = '▲' if trnd>0.5 else ('▼' if trnd<-0.5 else '→')
            t_col = '#ff6b35' if trnd>0.5 else ('#00ff9d' if trnd<-0.5 else '#7a9ab8')
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
    _pc = '#ff4b6e' if _prof_score>=60 else ('#ffd700' if _prof_score>=35 else '#00b4ff')
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
                col = '#ff4b6e' if s>=65 else ('#ff6b35' if s>=45 else ('#ffd700' if s>=25 else '#00b4ff'))
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
                if   z>=2.5:  alm_col,alm_lbl = '#ff4b6e','CRITICAL SPIKE'
                elif z>=1.5:  alm_col,alm_lbl = '#ff6b35','HIGH SPIKE'
                elif z>=0.8:  alm_col,alm_lbl = '#ffd700','ELEVATED'
                elif z<=-1.5: alm_col,alm_lbl = '#00ff9d','SUPPRESSED'
                else:         alm_col,alm_lbl = '#00b4ff','NORMAL'
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

        st.markdown("""<div style="font-size:0.6rem;color:#00ff9d;letter-spacing:0.15em;
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
        t_col_g = '#ff6b35' if cur_t>50 else ('#ffd700' if cur_t>25 else '#00b4ff')
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
        c_col_g = '#00ff9d' if cur_c>40 else ('#00b4ff' if cur_c>15 else '#4a6a8a')
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
        mode='lines',line=dict(width=2,color='#ff6b35'),
        fill='tozeroy',fillcolor='rgba(255,107,53,0.06)',
        hovertemplate='Conflict Pressure: %{y:.1f}<extra></extra>'))
    fig_bi.add_trace(go.Scatter(x=bi_c_ser.index,y=bi_c_ser.values,name='Cooperation',
        mode='lines',line=dict(width=2,color='#00ff9d'),
        fill='tozeroy',fillcolor='rgba(0,255,157,0.05)',
        hovertemplate='Cooperation: %{y:.1f}<extra></extra>'))
    fig_bi.add_trace(go.Scatter(x=bi_net_ser.index,y=bi_net_ser.values,name='Net Tension',
        mode='lines',line=dict(width=2.5,color='#7b2fff'),
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
if   page == 'home':    render_home()
elif page == 'indices': render_indices()
elif page == 'profile': render_profile()
elif page == 'news':    render_news()
else:
    st.session_state.page = 'home'
    st.rerun()
