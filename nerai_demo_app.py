# ============================================================
# NERAI Strategic Insights Hub — Snowflake Demo App
# Streamlit in Snowflake
# ============================================================

import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, timedelta

session = get_active_session()

# ─────────────────────────────────────────────────────────────
# SAYFA AYARLARI
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="NERAI — Geopolitical Risk Intelligence", layout="wide")

# ─────────────────────────────────────────────────────────────
# DEMO BANNER — her zaman üstte görünür
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(90deg,#1a1a2e,#16213e);padding:14px 24px;border-radius:8px;
            border-left:4px solid #e94560;margin-bottom:20px;display:flex;align-items:center;gap:16px">
  <span style="background:#e94560;color:white;font-size:11px;font-weight:700;
               padding:3px 10px;border-radius:4px;letter-spacing:1px">DEMO</span>
  <span style="color:#ccc;font-size:14px">
    Bu ekran <strong style="color:white">NERAI Strategic Insights Hub</strong>'ın sınırlı bir önizlemesidir.
    Gerçek platform; özel senaryo analizleri, erken uyarı sistemi, portföy risk taraması,
    API erişimi ve özelleştirilebilir raporlama içerir.
    &nbsp;→&nbsp;<a href="https://nerai.co" target="_blank" style="color:#e94560;text-decoration:none;font-weight:600">nerai.co</a>
    &nbsp;|&nbsp;<a href="mailto:kagan@neraicorp.com" style="color:#e94560;text-decoration:none;font-weight:600">7-day trial talep et</a>
  </span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# BAŞLIK
# ─────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 9])
with col_logo:
    st.markdown("<div style='font-size:40px;padding-top:6px'>🌐</div>", unsafe_allow_html=True)
with col_title:
    st.markdown("## NERAI — Geopolitical Risk Intelligence")
    st.caption("Powered by GDELT · ACLED · World Bank · IMF · Satellite feeds")

st.divider()

# ─────────────────────────────────────────────────────────────
# FİLTRELER
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_filter_options():
    topics = session.sql(
        "SELECT DISTINCT topic FROM NERAI_DATA.RISK_INTELLIGENCE.NERAI_INDICES ORDER BY topic"
    ).to_pandas()["TOPIC"].tolist()
    countries = session.sql(
        "SELECT DISTINCT country FROM NERAI_DATA.RISK_INTELLIGENCE.NERAI_INDICES ORDER BY country"
    ).to_pandas()["COUNTRY"].tolist()
    return topics, countries

topics, countries = get_filter_options()

col1, col2, col3 = st.columns([3, 3, 2])
with col1:
    selected_topic = st.selectbox("Risk Kategorisi", topics, index=topics.index("Political Stability") if "Political Stability" in topics else 0)
with col2:
    selected_country = st.selectbox("Ülke", countries, index=countries.index("Turkey") if "Turkey" in countries else 0)
with col3:
    lookback = st.selectbox("Dönem", ["Son 30 gün", "Son 60 gün", "Son 90 gün"], index=2)
    days_back = {"Son 30 gün": 30, "Son 60 gün": 60, "Son 90 gün": 90}[lookback]

# ─────────────────────────────────────────────────────────────
# VERİ ÇEK
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=1800)
def get_risk_data(topic, country, days):
    df = session.sql(f"""
        SELECT score_date, index_value
        FROM NERAI_DATA.RISK_INTELLIGENCE.NERAI_INDICES
        WHERE topic = '{topic}'
          AND country = '{country}'
          AND score_date >= DATEADD(day, -{days}, CURRENT_DATE())
        ORDER BY score_date
    """).to_pandas()
    df["SCORE_DATE"] = pd.to_datetime(df["SCORE_DATE"])
    return df

@st.cache_data(ttl=1800)
def get_forecast_data(topic, country):
    df = session.sql(f"""
        SELECT ds, yhat, yhat_lower, yhat_upper
        FROM NERAI_DATA.RISK_INTELLIGENCE.NERAI_PREDICTIONS
        WHERE topic = '{topic}'
          AND country = '{country}'
          AND ds >= CURRENT_DATE()
          AND ds <= DATEADD(day, 90, CURRENT_DATE())
        ORDER BY ds
    """).to_pandas()
    df["DS"] = pd.to_datetime(df["DS"])
    return df

@st.cache_data(ttl=1800)
def get_trend_data(topic, country):
    df = session.sql(f"""
        SELECT trend_pct, direction
        FROM NERAI_DATA.RISK_INTELLIGENCE.NERAI_FORECAST_TRENDS
        WHERE topic = '{topic}' AND country = '{country}'
    """).to_pandas()
    return df

@st.cache_data(ttl=1800)
def get_top_risks(topic, days):
    df = session.sql(f"""
        SELECT country, AVG(index_value) as avg_risk, MAX(index_value) as peak_risk
        FROM NERAI_DATA.RISK_INTELLIGENCE.NERAI_INDICES
        WHERE topic = '{topic}'
          AND score_date >= DATEADD(day, -{days}, CURRENT_DATE())
        GROUP BY country
        ORDER BY avg_risk DESC
        LIMIT 10
    """).to_pandas()
    return df

df_risk   = get_risk_data(selected_topic, selected_country, days_back)
df_fcast  = get_forecast_data(selected_topic, selected_country)
df_trend  = get_trend_data(selected_topic, selected_country)
df_top10  = get_top_risks(selected_topic, days_back)

# ─────────────────────────────────────────────────────────────
# KPI KARTI
# ─────────────────────────────────────────────────────────────
if not df_risk.empty and not df_trend.empty:
    current_score = df_risk["INDEX_VALUE"].iloc[-1]
    prev_score    = df_risk["INDEX_VALUE"].iloc[0]
    delta         = current_score - prev_score
    direction     = df_trend["DIRECTION"].iloc[0] if not df_trend.empty else "—"
    trend_pct     = df_trend["TREND_PCT"].iloc[0] if not df_trend.empty else 0

    direction_emoji = {"accelerating": "🔴", "reversing": "🟢", "stable": "🟡"}.get(direction.lower(), "⚪")

    risk_level = "HIGH" if current_score > 0.65 else "MEDIUM" if current_score > 0.35 else "LOW"
    risk_color = {"HIGH": "#e94560", "MEDIUM": "#f5a623", "LOW": "#27ae60"}[risk_level]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(label=f"**Risk Skoru** — {selected_country}", value=f"{current_score:.3f}",
              delta=f"{delta:+.3f} ({days_back}g)")
    k2.metric(label="**Trend**", value=f"{direction_emoji} {direction.title()}",
              delta=f"{trend_pct:+.1f}%")
    k3.metric(label="**Risk Seviyesi**",
              value=f"{'🔴' if risk_level=='HIGH' else '🟡' if risk_level=='MEDIUM' else '🟢'} {risk_level}")
    k4.metric(label="**30G Tahmin**",
              value=f"{df_fcast['YHAT'].iloc[0]:.3f}" if not df_fcast.empty else "—",
              delta=f"± {(df_fcast['YHAT_UPPER'].iloc[0] - df_fcast['YHAT_LOWER'].iloc[0])/2:.3f}" if not df_fcast.empty else "")

st.divider()

# ─────────────────────────────────────────────────────────────
# ANA GRAFİK — Risk skoru + Tahmin
# ─────────────────────────────────────────────────────────────
fig = go.Figure()

# Geçmiş risk skoru
if not df_risk.empty:
    fig.add_trace(go.Scatter(
        x=df_risk["SCORE_DATE"], y=df_risk["INDEX_VALUE"],
        name="Risk Skoru (Gerçek)",
        line=dict(color="#4a9eff", width=2.5),
        mode="lines"
    ))

# Tahmin bandı
if not df_fcast.empty:
    fig.add_trace(go.Scatter(
        x=pd.concat([df_fcast["DS"], df_fcast["DS"].iloc[::-1]]),
        y=pd.concat([df_fcast["YHAT_UPPER"], df_fcast["YHAT_LOWER"].iloc[::-1]]),
        fill="toself", fillcolor="rgba(229,77,66,0.12)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Tahmin Aralığı", showlegend=True
    ))
    fig.add_trace(go.Scatter(
        x=df_fcast["DS"], y=df_fcast["YHAT"],
        name="90G Tahmin",
        line=dict(color="#e94560", width=2, dash="dash"),
        mode="lines"
    ))

# Bugünü işaretle
today_str = date.today().isoformat()
fig.add_vline(x=today_str, line_dash="dot", line_color="gray",
              annotation_text="Bugün", annotation_position="top right")

fig.update_layout(
    title=f"{selected_topic} Risk Endeksi — {selected_country}",
    xaxis_title="Tarih", yaxis_title="Risk Skoru (0–1)",
    template="plotly_dark",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=400,
    margin=dict(l=0, r=0, t=50, b=0)
)
fig.update_yaxes(range=[0, 1])

st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# ALT BÖLÜM — Top 10 ülke + Veri kaynakları
# ─────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.markdown(f"#### En Riskli 10 Ülke — {selected_topic}")
    if not df_top10.empty:
        df_top10["Seviye"] = df_top10["AVG_RISK"].apply(
            lambda x: "🔴 HIGH" if x > 0.65 else "🟡 MEDIUM" if x > 0.35 else "🟢 LOW"
        )
        df_top10_display = df_top10.rename(columns={
            "COUNTRY": "Ülke", "AVG_RISK": "Ort. Risk", "PEAK_RISK": "Peak"
        })[["Ülke", "Ort. Risk", "Peak", "Seviye"]]
        df_top10_display["Ort. Risk"] = df_top10_display["Ort. Risk"].map("{:.3f}".format)
        df_top10_display["Peak"]      = df_top10_display["Peak"].map("{:.3f}".format)
        st.dataframe(df_top10_display, use_container_width=True, hide_index=True)

with col_right:
    st.markdown("#### Veri Kaynakları")
    st.markdown("""
| Kaynak | Kapsam |
|--------|--------|
| **GDELT** | Küresel haber & olay akışı |
| **ACLED** | Çatışma & güvenlik olayları |
| **World Bank** | Yönetişim göstergeleri |
| **IMF** | Makroekonomik istikrar |
| **Satellite** | İnsani hareketlilik |
    """)

    st.markdown("""
<div style="background:#1a1a2e;border:1px solid #e94560;border-radius:8px;padding:16px;margin-top:16px">
  <p style="color:#e94560;font-weight:700;margin:0 0 8px 0">⚡ Gerçek Platformda Daha Fazlası</p>
  <ul style="color:#ccc;font-size:13px;margin:0;padding-left:18px;line-height:1.8">
    <li>Özel senaryo & stres testi modelleri</li>
    <li>Portföy geneli risk taraması (tek tıkla)</li>
    <li>Erken uyarı sistemi (email/webhook)</li>
    <li>API erişimi — kendi sistemlerinize entegre</li>
    <li>Özelleştirilebilir raporlama & export</li>
    <li>Günlük data refresh + tarihsel arşiv</li>
  </ul>
  <div style="margin-top:12px">
    <a href="https://nerai.co" target="_blank"
       style="background:#e94560;color:white;padding:8px 20px;border-radius:6px;
              text-decoration:none;font-weight:600;font-size:13px">
      7-Day Trial Talep Et →
    </a>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center;color:#555;font-size:12px'>"
    "NERAI Strategic Insights Hub · Demo Preview · "
    "<a href='https://nerai.co' style='color:#e94560'>nerai.co</a> · "
    "<a href='mailto:kagan@neraicorp.com' style='color:#e94560'>kagan@neraicorp.com</a>"
    "</div>",
    unsafe_allow_html=True
)
