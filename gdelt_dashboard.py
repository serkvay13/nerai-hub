"""
NERAI INTELLIGENCE HUB — Dashboard v2.0
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import os

st.set_page_config(
    page_title="NERAI Intelligence Hub",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');

.stApp {
    background: #020b18;
    background-image:
        radial-gradient(ellipse at 15% 40%, rgba(0,150,255,0.05) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 15%, rgba(100,0,255,0.06) 0%, transparent 55%),
        radial-gradient(ellipse at 50% 90%, rgba(0,80,180,0.04) 0%, transparent 55%);
}
html, body, [class*="css"] { font-family:'Exo 2',sans-serif; color:#c8d8e8; }

[data-testid="stSidebar"] {
    background: rgba(2,8,20,0.97);
    border-right: 1px solid rgba(0,150,255,0.12);
}
[data-testid="stSidebar"] label {
    color:#00b4ff !important; font-size:0.7rem !important;
    letter-spacing:0.15em; text-transform:uppercase;
}

/* KPI KARTI */
.kpi-card {
    background: linear-gradient(135deg,rgba(0,18,40,0.95),rgba(0,8,22,0.95));
    border:1px solid rgba(0,150,255,0.2);
    border-radius:10px; padding:16px 18px;
    position:relative; overflow:hidden;
    box-shadow:0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04);
    transition: border-color 0.3s;
}
.kpi-card:hover { border-color:rgba(0,180,255,0.45); }
.kpi-card::before {
    content:''; position:absolute; top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,transparent,var(--accent,#00b4ff),transparent);
}
.kpi-label { font-size:0.65rem; letter-spacing:0.2em; text-transform:uppercase;
             color:rgba(0,180,255,0.6); font-family:'Share Tech Mono',monospace; margin-bottom:4px; }
.kpi-value { font-size:2.1rem; font-weight:700; line-height:1; color:#fff;
             text-shadow:0 0 24px rgba(0,180,255,0.4); }
.kpi-sub   { font-size:0.68rem; margin-top:5px; font-family:'Share Tech Mono',monospace; }
.kpi-up    { color:#00ff9d; } .kpi-down { color:#ff4b6e; } .kpi-neu { color:#556; }
.badge-low  { color:#00ff9d; font-size:0.6rem; background:rgba(0,255,157,0.08);
              border:1px solid rgba(0,255,157,0.25); border-radius:3px; padding:1px 6px; }
.badge-med  { color:#ffd700; font-size:0.6rem; background:rgba(255,215,0,0.08);
              border:1px solid rgba(255,215,0,0.25); border-radius:3px; padding:1px 6px; }
.badge-high { color:#ff6b35; font-size:0.6rem; background:rgba(255,107,53,0.1);
              border:1px solid rgba(255,107,53,0.3); border-radius:3px; padding:1px 6px; }
.badge-crit { color:#ff4b6e; font-size:0.6rem; background:rgba(255,75,110,0.1);
              border:1px solid rgba(255,75,110,0.35); border-radius:3px; padding:1px 6px; }

/* HERO */
.hero-title {
    font-size:2.2rem; font-weight:700; letter-spacing:0.07em;
    background:linear-gradient(90deg,#00b4ff 0%,#7b2fff 45%,#00e5ff 100%);
    background-size:200% auto; -webkit-background-clip:text;
    -webkit-text-fill-color:transparent; animation:shine 5s linear infinite;
}
@keyframes shine { to { background-position:200% center; } }
.hero-sub { font-size:0.72rem; letter-spacing:0.22em; text-transform:uppercase;
            color:rgba(0,180,255,0.45); font-family:'Share Tech Mono',monospace; }
.live-dot { display:inline-block; width:7px; height:7px; border-radius:50%;
            background:#00ff9d; box-shadow:0 0 8px #00ff9d;
            animation:pulse 2s infinite; margin-right:5px; vertical-align:middle; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.8)} }

/* SECTION HEADER */
.sec-hdr { font-size:0.65rem; letter-spacing:0.25em; text-transform:uppercase;
           color:rgba(0,150,255,0.55); font-family:'Share Tech Mono',monospace;
           padding:8px 0 6px; border-bottom:1px solid rgba(0,150,255,0.1); margin-bottom:12px; }

/* SIGNAL CARD */
.signal-card {
    background:rgba(0,15,35,0.7); border:1px solid rgba(0,150,255,0.12);
    border-radius:8px; padding:10px 14px; margin-bottom:8px;
    display:flex; align-items:center; justify-content:space-between;
}
.signal-name { font-size:0.75rem; color:#a0c0d8; font-weight:600; }
.signal-topic { font-size:0.62rem; color:rgba(0,150,255,0.5); font-family:'Share Tech Mono',monospace; }
.signal-val { font-size:1rem; font-weight:700; color:#fff; text-align:right; }

/* NORM BADGE */
.norm-raw   { color:#8ba3bc; }
.norm-score { color:#00b4ff; }
.norm-z     { color:#7b2fff; }

/* DIVIDER */
.h-div { height:1px; background:linear-gradient(90deg,transparent,rgba(0,150,255,0.15),transparent); margin:12px 0; }

#MainMenu,footer,.stDeployButton { visibility:hidden; display:none; }
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-thumb { background:rgba(0,150,255,0.25); border-radius:2px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SABİTLER
# ─────────────────────────────────────────────────────────────
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

def hex_to_rgba(h, a=0.06):
    r,g,b = int(h[1:3],16),int(h[3:5],16),int(h[5:7],16)
    return f'rgba({r},{g},{b},{a})'

BASE_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,8,22,0.7)',
    font=dict(family='Exo 2,sans-serif', color='#7a9ab8', size=11),
    margin=dict(l=45,r=15,t=38,b=40),
    xaxis=dict(gridcolor='rgba(0,100,180,0.1)', linecolor='rgba(0,100,180,0.15)',
               tickfont=dict(size=10,color='#4a6a8a')),
    yaxis=dict(gridcolor='rgba(0,100,180,0.1)', linecolor='rgba(0,100,180,0.15)',
               tickfont=dict(size=10,color='#4a6a8a')),
)

# ─────────────────────────────────────────────────────────────
# VERİ
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data(filepath='./indices.csv'):
    if os.path.exists(filepath):
        df = pd.read_csv(filepath, sep=',', header=0, index_col=[0,1])
        df.columns = pd.to_datetime(df.columns, format='%Y%m%d')
        return df, False
    return _demo_data(), True

def _demo_data():
    np.random.seed(42)
    topics = list(TOPIC_LABELS.keys())
    countries = list(COUNTRY_NAMES.keys())
    dates = pd.date_range(end=datetime.date.today(), periods=180, freq='D')
    idx = pd.MultiIndex.from_product([topics,countries], names=['topic','country'])
    return pd.DataFrame(
        np.random.exponential(0.0008, size=(len(idx), len(dates))),
        index=idx, columns=dates
    )

def apply_norm(df_topic, method):
    """df_topic: country × dates (single level index)."""
    if method == 'Raw':
        return df_topic
    out = df_topic.copy().astype(float)
    for c in out.index:
        row = out.loc[c]
        if method == 'Score (0–100)':
            mn, mx = row.min(), row.max()
            out.loc[c] = (row - mn) / (mx - mn) * 100 if mx > mn else row * 0
        elif method == 'Z-Score':
            mu, sd = row.mean(), row.std()
            out.loc[c] = (row - mu) / sd if sd > 0 else row * 0
    return out

def fmt(val, method):
    if method == 'Raw':    return f'{val:.5f}'
    if method == 'Score (0–100)': return f'{val:.1f}'
    return f'{val:+.2f}σ'

def risk_badge(val, method):
    if method == 'Score (0–100)':
        if val >= 75: return '<span class="badge-crit">CRITICAL</span>'
        if val >= 50: return '<span class="badge-high">HIGH</span>'
        if val >= 25: return '<span class="badge-med">MEDIUM</span>'
        return '<span class="badge-low">LOW</span>'
    if method == 'Z-Score':
        if val >= 2:  return '<span class="badge-crit">SPIKE</span>'
        if val >= 1:  return '<span class="badge-high">ELEVATED</span>'
        if val <= -1: return '<span class="badge-low">SUPPRESSED</span>'
        return '<span class="badge-neu" style="color:#556">NORMAL</span>'
    return ''

# ─────────────────────────────────────────────────────────────
# CHART FONKSİYONLARI
# ─────────────────────────────────────────────────────────────
def chart_timeseries(df_n, countries, title, method):
    fig = go.Figure()
    y_label = {'Raw':'Raw Index','Score (0–100)':'Risk Score (0–100)','Z-Score':'Z-Score (σ)'}[method]
    for i, c in enumerate(countries):
        if c not in df_n.index: continue
        s = df_n.loc[c]
        col = GLOW_COLORS[i % len(GLOW_COLORS)]
        fig.add_trace(go.Scatter(
            x=s.index, y=s.values, name=COUNTRY_NAMES.get(c,c), mode='lines',
            line=dict(width=2, color=col),
            fill='tozeroy', fillcolor=hex_to_rgba(col, 0.05),
            hovertemplate=f'<b>{COUNTRY_NAMES.get(c,c)}</b><br>%{{x|%d %b %Y}}<br>{y_label}: %{{y:.4f}}<extra></extra>'
        ))
    if method == 'Z-Score':
        fig.add_hline(y=2, line_dash='dot', line_color='rgba(255,75,110,0.4)',
                      annotation_text='Alert (+2σ)', annotation_font_size=9)
        fig.add_hline(y=-2, line_dash='dot', line_color='rgba(0,255,157,0.3)',
                      annotation_text='-2σ', annotation_font_size=9)
    t = {**BASE_THEME}
    t['yaxis'] = {**t['yaxis'], 'title': y_label, 'title_font': dict(size=10)}
    fig.update_layout(**t, height=330,
        title=dict(text=title, font=dict(size=12,color='#6a9ab8'), x=0.01),
        legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='rgba(0,100,180,0.2)',
                    borderwidth=1, font=dict(size=10)),
        hovermode='x unified')
    return fig

def chart_heatmap(df_n, top_n, method):
    means = df_n.mean(axis=1).nlargest(top_n)
    sel = means.index.tolist()
    matrix = []
    for c in sel:
        try: matrix.append(df_n.loc[c].values)
        except: matrix.append([0]*len(df_n.columns))
    matrix = np.array(matrix)
    dates_str = [d.strftime('%d %b') for d in df_n.columns]
    step = max(1, len(dates_str)//18)
    xlabels = [d if i%step==0 else '' for i,d in enumerate(dates_str)]
    ylabels = [COUNTRY_NAMES.get(c,c) for c in sel]
    colorscale = (
        [[0,'rgba(0,10,30,1)'],[0.25,'rgba(0,60,120,1)'],
         [0.5,'rgba(0,130,200,1)'],[0.75,'rgba(100,0,200,1)'],[1,'rgba(255,50,100,1)']]
        if method != 'Z-Score' else
        [[0,'rgba(0,80,160,1)'],[0.35,'rgba(0,20,50,1)'],
         [0.5,'rgba(10,10,30,1)'],[0.65,'rgba(80,0,120,1)'],[1,'rgba(255,50,100,1)']]
    )
    fig = go.Figure(go.Heatmap(
        z=matrix, x=xlabels, y=ylabels, colorscale=colorscale,
        hovertemplate='<b>%{y}</b><br>%{x}<br>Value: %{z:.3f}<extra></extra>',
        showscale=True, colorbar=dict(thickness=7,len=0.85,
            tickfont=dict(size=8,color='#4a6a8a'), outlinewidth=0)
    ))
    t = {**BASE_THEME}
    t['xaxis'] = dict(showticklabels=True, tickangle=-45,
                      tickfont=dict(size=8,color='#4a6a8a'), gridcolor='rgba(0,0,0,0)')
    t['yaxis'] = dict(tickfont=dict(size=9,color='#8ab0c8'), gridcolor='rgba(0,0,0,0)')
    fig.update_layout(**t, height=420,
        title=dict(text=f'Top {top_n} Countries — Heatmap',
                   font=dict(size=12,color='#6a9ab8'), x=0.01))
    return fig

def chart_world(df_n, date_col):
    try:
        row = df_n[[date_col]].reset_index()
        row.columns = ['country','value']
        row['iso3'] = row['country'].map(FIPS_TO_ISO3)
        row['name'] = row['country'].map(COUNTRY_NAMES)
        row = row.dropna(subset=['iso3'])
    except: return go.Figure()
    fig = go.Figure(go.Choropleth(
        locations=row['iso3'], z=row['value'], text=row['name'],
        colorscale=[[0,'rgba(0,15,40,1)'],[0.3,'rgba(0,80,160,1)'],
                    [0.6,'rgba(80,0,180,1)'],[0.85,'rgba(200,0,100,1)'],
                    [1,'rgba(255,50,50,1)']],
        autocolorscale=False, marker_line_color='rgba(0,100,180,0.3)',
        marker_line_width=0.5,
        colorbar=dict(title=dict(text='Score',font=dict(size=9,color='#4a6a8a')),
                      thickness=7,len=0.55,tickfont=dict(size=8,color='#4a6a8a'),
                      outlinewidth=0,bgcolor='rgba(0,0,0,0)'),
        hovertemplate='<b>%{text}</b><br>Value: %{z:.3f}<extra></extra>'
    ))
    t = {**BASE_THEME}
    fig.update_layout(**t, height=330,
        title=dict(text=f'Global Risk Map — {pd.Timestamp(date_col).strftime("%d %b %Y")}',
                   font=dict(size=12,color='#6a9ab8'), x=0.01),
        geo=dict(bgcolor='rgba(0,0,0,0)', showframe=False, showcoastlines=True,
                 coastlinecolor='rgba(0,100,180,0.25)', showland=True,
                 landcolor='rgba(4,18,42,1)', showocean=True,
                 oceancolor='rgba(0,6,18,1)', showlakes=False,
                 projection_type='natural earth'))
    return fig

def chart_ranking(df_n, date_col, n=12):
    try:
        row = df_n[[date_col]].reset_index()
        row.columns = ['country','value']
        row['name'] = row['country'].map(COUNTRY_NAMES)
        row = row.nlargest(n,'value').sort_values('value')
    except: return go.Figure()
    n_rows = len(row)
    colors = [f'rgba({int(0+200*i/max(n_rows-1,1))},{int(120+80*i/max(n_rows-1,1))},{int(220-20*i/max(n_rows-1,1))},0.85)' for i in range(n_rows)]
    fig = go.Figure(go.Bar(
        x=row['value'], y=row['name'], orientation='h',
        marker=dict(color=colors, line=dict(color='rgba(0,180,255,0.2)',width=0.5)),
        hovertemplate='<b>%{y}</b><br>Value: %{x:.4f}<extra></extra>'
    ))
    t = {**BASE_THEME}
    t['xaxis'] = dict(gridcolor='rgba(0,100,180,0.1)', tickfont=dict(size=10,color='#4a6a8a'))
    t['yaxis'] = dict(tickfont=dict(size=10,color='#8ab0c8'), gridcolor='rgba(0,0,0,0)')
    fig.update_layout(**t, height=330,
        title=dict(text='Country Ranking', font=dict(size=12,color='#6a9ab8'), x=0.01))
    return fig

def chart_sparkline(series, color='#00b4ff'):
    fig = go.Figure(go.Scatter(
        x=series.index, y=series.values, mode='lines',
        line=dict(width=1.5, color=color),
        fill='tozeroy', fillcolor=hex_to_rgba(color, 0.12)
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=45, margin=dict(l=0,r=0,t=0,b=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False
    )
    return fig

# ─────────────────────────────────────────────────────────────
# VERİ YÜKLE
# ─────────────────────────────────────────────────────────────
df, is_demo = load_data()
date_cols = df.columns
all_topics = sorted(df.index.get_level_values('topic').unique().tolist())
all_countries = sorted(df.index.get_level_values('country').unique().tolist())

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:10px 0 18px;border-bottom:1px solid rgba(0,150,255,0.12);margin-bottom:16px;'>
      <div style='font-size:1.15rem;font-weight:700;color:#00b4ff;letter-spacing:0.08em;'>⬡ NERAI</div>
      <div style='font-size:0.6rem;color:rgba(0,180,255,0.35);letter-spacing:0.22em;font-family:monospace;'>
        INTELLIGENCE HUB
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec-hdr">Normalization</div>', unsafe_allow_html=True)
    norm_method = st.radio(
        "norm", ['Score (0–100)', 'Z-Score', 'Raw'],
        index=0, label_visibility='collapsed',
        help="Score 0–100: tarihin en yüksek değeri=100 | Z-Score: ortalamadan sapma | Raw: ham veri"
    )

    st.markdown('<div class="sec-hdr" style="margin-top:14px">Topic</div>', unsafe_allow_html=True)
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
    n_days = st.slider("days", 14, min(180, len(date_cols)), 60, label_visibility='collapsed')

    st.markdown('<div class="sec-hdr" style="margin-top:14px">Map Date</div>', unsafe_allow_html=True)
    map_opts = [d.strftime('%Y-%m-%d') for d in date_cols[-30:]]
    map_date_str = st.selectbox("map", map_opts, index=len(map_opts)-1, label_visibility='collapsed')
    map_date = pd.Timestamp(map_date_str)

    heatmap_n = st.slider("Heatmap top N countries", 8, 30, 15)

    st.markdown(f"""
    <div style='margin-top:20px;padding:10px;background:rgba(0,150,255,0.05);
         border:1px solid rgba(0,150,255,0.1);border-radius:6px;
         font-size:0.62rem;color:rgba(0,180,255,0.4);font-family:monospace;line-height:2;'>
      <span class='live-dot'></span>LIVE DATA<br>
      📅 {len(date_cols)} days<br>
      📊 {len(all_topics)} topics · {len(all_countries)} countries<br>
      🔢 {len(df):,} data points<br>
      {'⚠ DEMO MODE' if is_demo else '✓ GDELT Project'}
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# VERİ HAZIRLAMA
# ─────────────────────────────────────────────────────────────
if sel_topic in df.index.get_level_values('topic'):
    df_topic_raw = df.xs(sel_topic, level='topic')
else:
    df_topic_raw = df.groupby(level='country').mean()

df_topic_raw = df_topic_raw.reindex(columns=sorted(df_topic_raw.columns))
df_recent_raw = df_topic_raw[date_cols[-n_days:]]
df_norm    = apply_norm(df_topic_raw, norm_method)
df_recent  = apply_norm(df_recent_raw, norm_method)

norm_suffix = {'Raw':'','Score (0–100)':' · Score 0–100','Z-Score':' · Z-Score'}[norm_method]

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
c1, c2 = st.columns([3,1])
with c1:
    st.markdown(f"""
    <div style='padding:6px 0 2px;'>
      <div class='hero-title'>NERAI Intelligence Hub</div>
      <div class='hero-sub'><span class='live-dot'></span>
        Geopolitical Risk Intelligence &nbsp;·&nbsp; Data: GDELT Project
      </div>
    </div>""", unsafe_allow_html=True)
with c2:
    nm_color = {'Raw':'#8ba3bc','Score (0–100)':'#00b4ff','Z-Score':'#7b2fff'}[norm_method]
    st.markdown(f"""
    <div style='text-align:right;padding-top:12px;font-family:monospace;font-size:0.68rem;color:rgba(0,180,255,0.4);'>
      LAST UPDATE<br>
      <span style='color:#00b4ff;font-size:0.9rem;'>{date_cols[-1].strftime('%d %b %Y')}</span><br>
      <span style='color:{nm_color};font-size:0.7rem;'>▣ {norm_method}</span>
    </div>""", unsafe_allow_html=True)

st.markdown('<div class="h-div"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# KPI KARTLARI (sparkline ile)
# ─────────────────────────────────────────────────────────────
kpi_countries = (sel_countries + all_countries)[:4]
kpi_cols = st.columns(4)

for col, c in zip(kpi_cols, kpi_countries):
    with col:
        if c in df_norm.index and len(df_norm.columns) > 1:
            series = df_norm.loc[c]
            val    = series.iloc[-1]
            prev7  = series.iloc[-8] if len(series) > 7 else series.iloc[0]
            delta  = val - prev7
            d_cls  = 'kpi-up' if delta>0 else ('kpi-down' if delta<0 else 'kpi-neu')
            d_sym  = '▲' if delta>0 else ('▼' if delta<0 else '●')
            badge  = risk_badge(val, norm_method)
            spark_color = '#ff4b6e' if (norm_method=='Score (0–100)' and val>=60) else \
                          '#ffd700' if (norm_method=='Score (0–100)' and val>=35) else '#00b4ff'

            st.markdown(f"""
            <div class='kpi-card' style='--accent:{spark_color};'>
              <div class='kpi-label'>{COUNTRY_NAMES.get(c,c)}</div>
              <div class='kpi-value'>{fmt(val, norm_method)}</div>
              <div class='kpi-sub'>
                <span class='{d_cls}'>{d_sym} {fmt(abs(delta),norm_method)} vs 7d</span>
                &nbsp; {badge}
              </div>
            </div>""", unsafe_allow_html=True)
            # Sparkline
            spark_data = series.iloc[-30:]
            fig_sp = chart_sparkline(spark_data, spark_color)
            st.plotly_chart(fig_sp, use_container_width=True,
                            config={'displayModeBar':False, 'staticPlot':True})
        else:
            st.markdown(f"""
            <div class='kpi-card'><div class='kpi-label'>{COUNTRY_NAMES.get(c,c)}</div>
            <div class='kpi-value'>—</div></div>""", unsafe_allow_html=True)

st.markdown('<div class="h-div" style="margin:4px 0 14px"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TOP SIGNALS (En yüksek son değerler)
# ─────────────────────────────────────────────────────────────
with st.expander("⚡  Top Signals — Biggest Movers (Last 7 Days)", expanded=True):
    st.markdown('<div class="sec-hdr">Anomaly Detection</div>', unsafe_allow_html=True)
    if len(df_norm.columns) > 7:
        last = df_norm.iloc[:, -1]
        prev = df_norm.iloc[:, -8]
        changes = ((last - prev) / (prev.abs() + 1e-10) * 100).dropna()
        top_up   = changes.nlargest(5)
        top_down = changes.nsmallest(3)
        sig_col1, sig_col2 = st.columns(2)
        with sig_col1:
            st.markdown('<div style="font-size:0.65rem;color:#ff6b35;letter-spacing:0.15em;margin-bottom:8px;">▲ RISING RISK</div>', unsafe_allow_html=True)
            for c, pct in top_up.items():
                val = last[c]
                st.markdown(f"""
                <div class='signal-card' style='border-color:rgba(255,107,53,0.2);'>
                  <div>
                    <div class='signal-name'>{COUNTRY_NAMES.get(c,c)}</div>
                    <div class='signal-topic'>{sel_label}</div>
                  </div>
                  <div>
                    <div class='signal-val' style='color:#ff6b35;'>{fmt(val,norm_method)}</div>
                    <div style='font-size:0.65rem;color:#ff9d6b;text-align:right;'>▲ {pct:+.1f}%</div>
                  </div>
                </div>""", unsafe_allow_html=True)
        with sig_col2:
            st.markdown('<div style="font-size:0.65rem;color:#00ff9d;letter-spacing:0.15em;margin-bottom:8px;">▼ DECLINING RISK</div>', unsafe_allow_html=True)
            for c, pct in top_down.items():
                val = last[c]
                st.markdown(f"""
                <div class='signal-card' style='border-color:rgba(0,255,157,0.15);'>
                  <div>
                    <div class='signal-name'>{COUNTRY_NAMES.get(c,c)}</div>
                    <div class='signal-topic'>{sel_label}</div>
                  </div>
                  <div>
                    <div class='signal-val' style='color:#00ff9d;'>{fmt(val,norm_method)}</div>
                    <div style='font-size:0.65rem;color:#00cc7a;text-align:right;'>{pct:+.1f}%</div>
                  </div>
                </div>""", unsafe_allow_html=True)

st.markdown('<div class="h-div"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TIME SERIES + WORLD MAP
# ─────────────────────────────────────────────────────────────
col_ts, col_map = st.columns([3,2])
with col_ts:
    st.markdown('<div class="sec-hdr">Time Series Analysis</div>', unsafe_allow_html=True)
    if sel_countries:
        fig = chart_timeseries(df_recent, sel_countries,
              f'{sel_label}{norm_suffix} · Last {n_days} Days', norm_method)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})
    else:
        st.info("Sidebar'dan en az bir ülke seçin.")

with col_map:
    st.markdown('<div class="sec-hdr">Global Risk Map</div>', unsafe_allow_html=True)
    if map_date in df_norm.columns:
        st.plotly_chart(chart_world(df_norm, map_date),
                        use_container_width=True, config={'displayModeBar':False})

st.markdown('<div class="h-div"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HEATMAP + RANKING
# ─────────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────────
# RAW DATA TABLE
# ─────────────────────────────────────────────────────────────
with st.expander("📊  Data Table — Selected Countries", expanded=False):
    if sel_countries:
        rows = []
        for c in sel_countries:
            if c in df_recent.index:
                s = df_recent.loc[c]
                rows.append({'Country': COUNTRY_NAMES.get(c,c),
                             **{d.strftime('%d %b'): fmt(v,norm_method) for d,v in s.items()}})
        if rows:
            st.dataframe(pd.DataFrame(rows).set_index('Country'), use_container_width=True)

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-top:20px;padding:12px 0;border-top:1px solid rgba(0,150,255,0.07);
     text-align:center;font-size:0.6rem;color:rgba(0,150,255,0.18);font-family:monospace;
     letter-spacing:0.12em;'>
  NERAI INTELLIGENCE HUB &nbsp;·&nbsp; DATA SOURCE: GDELT PROJECT (gdeltproject.org)
  &nbsp;·&nbsp; FOR RESEARCH &amp; INFORMATIONAL PURPOSES ONLY
</div>""", unsafe_allow_html=True)