# =====================================================================
# NERAI Supply Grid - Phase 6+7 Module
# Trade Flow Dashboard + World Bank LPI Corridor View
# Imported by gdelt_dashboard.py
# =====================================================================
import streamlit as st


# -------------------- PHASE 6: TRADE FLOWS --------------------

def _sg_trade_flow_commodities():
    return {
        'Crude Petroleum (HS 2709)': {
            'global_trade_usd': '1.8T',
            'top_exporters': [
                {'country': 'Saudi Arabia', 'share': 16, 'value_b': 290},
                {'country': 'Russia', 'share': 11, 'value_b': 200},
                {'country': 'USA', 'share': 10, 'value_b': 185},
                {'country': 'Canada', 'share': 8, 'value_b': 145},
                {'country': 'UAE', 'share': 6, 'value_b': 110},
                {'country': 'Iraq', 'share': 5, 'value_b': 95},
            ],
            'top_importers': [
                {'country': 'China', 'share': 22, 'value_b': 395},
                {'country': 'India', 'share': 9, 'value_b': 165},
                {'country': 'USA', 'share': 8, 'value_b': 145},
                {'country': 'South Korea', 'share': 7, 'value_b': 125},
                {'country': 'Japan', 'share': 6, 'value_b': 110},
                {'country': 'Germany', 'share': 4, 'value_b': 75},
            ],
            'key_dynamic': 'Russia diverting to India/China; Saudi Aramco Asia-pivot; US exports growing'
        },
        'Natural Gas & LNG (HS 2711)': {
            'global_trade_usd': '700B',
            'top_exporters': [
                {'country': 'USA', 'share': 22, 'value_b': 155},
                {'country': 'Qatar', 'share': 20, 'value_b': 140},
                {'country': 'Australia', 'share': 19, 'value_b': 130},
                {'country': 'Norway', 'share': 11, 'value_b': 75},
                {'country': 'Russia', 'share': 6, 'value_b': 42},
                {'country': 'Malaysia', 'share': 4, 'value_b': 28},
            ],
            'top_importers': [
                {'country': 'China', 'share': 18, 'value_b': 125},
                {'country': 'Japan', 'share': 14, 'value_b': 95},
                {'country': 'Germany', 'share': 9, 'value_b': 65},
                {'country': 'South Korea', 'share': 8, 'value_b': 55},
                {'country': 'Italy', 'share': 5, 'value_b': 35},
                {'country': 'Turkiye', 'share': 4, 'value_b': 28},
            ],
            'key_dynamic': 'EU pivot from Russian pipeline to US/Qatar/Norway LNG (post-2022)'
        },
        'Semiconductors (HS 8542)': {
            'global_trade_usd': '750B',
            'top_exporters': [
                {'country': 'Taiwan', 'share': 24, 'value_b': 180},
                {'country': 'China', 'share': 17, 'value_b': 125},
                {'country': 'South Korea', 'share': 16, 'value_b': 120},
                {'country': 'USA', 'share': 10, 'value_b': 75},
                {'country': 'Singapore', 'share': 9, 'value_b': 65},
                {'country': 'Malaysia', 'share': 7, 'value_b': 52},
            ],
            'top_importers': [
                {'country': 'China', 'share': 32, 'value_b': 240},
                {'country': 'Hong Kong', 'share': 14, 'value_b': 105},
                {'country': 'Taiwan', 'share': 9, 'value_b': 67},
                {'country': 'USA', 'share': 8, 'value_b': 60},
                {'country': 'South Korea', 'share': 7, 'value_b': 52},
                {'country': 'Mexico', 'share': 4, 'value_b': 30},
            ],
            'key_dynamic': 'US export controls on advanced nodes; Taiwan concentration risk; CHIPS Act reshoring'
        },
        'Motor Vehicles (HS 8703)': {
            'global_trade_usd': '870B',
            'top_exporters': [
                {'country': 'Germany', 'share': 17, 'value_b': 148},
                {'country': 'Japan', 'share': 14, 'value_b': 122},
                {'country': 'China', 'share': 12, 'value_b': 104},
                {'country': 'USA', 'share': 7, 'value_b': 60},
                {'country': 'South Korea', 'share': 6, 'value_b': 52},
                {'country': 'Mexico', 'share': 6, 'value_b': 52},
            ],
            'top_importers': [
                {'country': 'USA', 'share': 19, 'value_b': 165},
                {'country': 'Germany', 'share': 7, 'value_b': 61},
                {'country': 'UK', 'share': 5, 'value_b': 44},
                {'country': 'France', 'share': 5, 'value_b': 43},
                {'country': 'Belgium', 'share': 4, 'value_b': 35},
                {'country': 'China', 'share': 4, 'value_b': 35},
            ],
            'key_dynamic': 'China EV exports surging; EU tariff response; US IRA localization pressure'
        },
        'Wheat (HS 1001)': {
            'global_trade_usd': '70B',
            'top_exporters': [
                {'country': 'Russia', 'share': 19, 'value_b': 13.3},
                {'country': 'Canada', 'share': 14, 'value_b': 9.8},
                {'country': 'Australia', 'share': 12, 'value_b': 8.4},
                {'country': 'USA', 'share': 11, 'value_b': 7.7},
                {'country': 'France', 'share': 8, 'value_b': 5.6},
                {'country': 'Argentina', 'share': 7, 'value_b': 4.9},
            ],
            'top_importers': [
                {'country': 'Indonesia', 'share': 7, 'value_b': 4.9},
                {'country': 'Turkiye', 'share': 6, 'value_b': 4.2},
                {'country': 'Egypt', 'share': 6, 'value_b': 4.2},
                {'country': 'Nigeria', 'share': 5, 'value_b': 3.5},
                {'country': 'Algeria', 'share': 4, 'value_b': 2.8},
                {'country': 'Philippines', 'share': 4, 'value_b': 2.8},
            ],
            'key_dynamic': 'Russia dominant post-Ukraine disruption; MENA/Africa food security at risk'
        },
        'Iron Ore (HS 2601)': {
            'global_trade_usd': '180B',
            'top_exporters': [
                {'country': 'Australia', 'share': 54, 'value_b': 97},
                {'country': 'Brazil', 'share': 21, 'value_b': 38},
                {'country': 'South Africa', 'share': 4, 'value_b': 7.2},
                {'country': 'Canada', 'share': 3, 'value_b': 5.4},
                {'country': 'Ukraine', 'share': 2, 'value_b': 3.6},
                {'country': 'Sweden', 'share': 2, 'value_b': 3.6},
            ],
            'top_importers': [
                {'country': 'China', 'share': 71, 'value_b': 128},
                {'country': 'Japan', 'share': 6, 'value_b': 11},
                {'country': 'South Korea', 'share': 4, 'value_b': 7.2},
                {'country': 'Germany', 'share': 2, 'value_b': 3.6},
                {'country': 'Netherlands', 'share': 2, 'value_b': 3.6},
                {'country': 'Malaysia', 'share': 1, 'value_b': 1.8},
            ],
            'key_dynamic': 'Extreme supplier concentration (Australia+Brazil=75%); China=71% demand'
        },
        'Pharmaceuticals (HS 30)': {
            'global_trade_usd': '820B',
            'top_exporters': [
                {'country': 'Germany', 'share': 14, 'value_b': 115},
                {'country': 'Switzerland', 'share': 12, 'value_b': 98},
                {'country': 'USA', 'share': 10, 'value_b': 82},
                {'country': 'Ireland', 'share': 10, 'value_b': 82},
                {'country': 'Belgium', 'share': 8, 'value_b': 66},
                {'country': 'India', 'share': 5, 'value_b': 41},
            ],
            'top_importers': [
                {'country': 'USA', 'share': 22, 'value_b': 180},
                {'country': 'Germany', 'share': 8, 'value_b': 66},
                {'country': 'Switzerland', 'share': 5, 'value_b': 41},
                {'country': 'Belgium', 'share': 5, 'value_b': 41},
                {'country': 'Japan', 'share': 5, 'value_b': 41},
                {'country': 'UK', 'share': 4, 'value_b': 33},
            ],
            'key_dynamic': 'India dominant generics; EU specialty; US reshoring of critical APIs'
        },
        'Soybean (HS 1201)': {
            'global_trade_usd': '70B',
            'top_exporters': [
                {'country': 'Brazil', 'share': 55, 'value_b': 38.5},
                {'country': 'USA', 'share': 36, 'value_b': 25.2},
                {'country': 'Argentina', 'share': 5, 'value_b': 3.5},
                {'country': 'Paraguay', 'share': 2, 'value_b': 1.4},
                {'country': 'Canada', 'share': 1, 'value_b': 0.7},
            ],
            'top_importers': [
                {'country': 'China', 'share': 60, 'value_b': 42},
                {'country': 'EU', 'share': 11, 'value_b': 7.7},
                {'country': 'Mexico', 'share': 4, 'value_b': 2.8},
                {'country': 'Japan', 'share': 3, 'value_b': 2.1},
                {'country': 'Argentina', 'share': 3, 'value_b': 2.1},
            ],
            'key_dynamic': 'China 60% import dependency; Brazil-China pivot post-trade war'
        },
    }


def _sg_trade_dynamics_headlines():
    return [
        {'category': 'Energy', 'headline': 'Russian oil redirected to India (+600% since 2022), China (+40%)', 'trend': 'up', 'magnitude': 'HIGH'},
        {'category': 'Energy', 'headline': 'EU LNG imports from US tripled since 2021 ($40B -> $90B)', 'trend': 'up', 'magnitude': 'HIGH'},
        {'category': 'Tech', 'headline': 'China chip equipment imports up 50% YoY (pre-sanction rush)', 'trend': 'up', 'magnitude': 'MEDIUM'},
        {'category': 'Tech', 'headline': 'Mexico becomes top US goods supplier, overtaking China (since 2023)', 'trend': 'up', 'magnitude': 'HIGH'},
        {'category': 'Auto', 'headline': 'China EV exports +65% YoY; targets LATAM, SE Asia, MENA', 'trend': 'up', 'magnitude': 'HIGH'},
        {'category': 'Food', 'headline': 'Egypt wheat diversifying from Russia/Ukraine (+15% from FR/AU)', 'trend': 'up', 'magnitude': 'MEDIUM'},
        {'category': 'Minerals', 'headline': 'Indonesia nickel exports surge (+35% YoY); HPAL capacity online', 'trend': 'up', 'magnitude': 'MEDIUM'},
        {'category': 'Energy', 'headline': 'Iraq oil exports to Europe rose 22% as Russia gap remains', 'trend': 'up', 'magnitude': 'MEDIUM'},
    ]


def render_trade_flows_tab():
    """Render the Trade Flows tab (Tab 12)."""
    st.markdown("""
    <div style="margin-bottom:16px;">
      <div style="font-size:18px; font-weight:600; color:#e0e8f0;">Global Trade Flow Dashboard</div>
      <div style="font-size:12px; color:#5a6b82; margin-top:4px;">
        Commodity-level trade dynamics &middot; Top exporters/importers &middot; UN Comtrade + WTO data &middot; 2024 values
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:13px; color:#00d4ff; font-weight:600; letter-spacing:1px; margin:6px 0 10px 0;'>RECENT DYNAMICS (last 24 months)</div>", unsafe_allow_html=True)
    for h in _sg_trade_dynamics_headlines()[:6]:
        mag_color = {'HIGH': '#ff7a00', 'MEDIUM': '#ffd000', 'LOW': '#7fb800'}.get(h['magnitude'], '#8aa0bc')
        arrow = '^' if h['trend'] == 'up' else ('v' if h['trend'] == 'down' else '-')
        st.markdown(f"""
        <div style='background:rgba(0,20,45,0.4); border-left:3px solid {mag_color};
                    border-radius:6px; padding:8px 14px; margin-bottom:5px;
                    display:flex; justify-content:space-between; align-items:center;'>
          <div style='display:flex; gap:10px; align-items:center;'>
            <span style='font-size:11px; color:#00d4ff; font-weight:700; letter-spacing:0.5px; width:60px;'>{h['category'].upper()}</span>
            <span style='color:{mag_color}; font-size:12px; font-weight:700;'>{arrow}</span>
            <span style='font-size:12px; color:#bdd2ea;'>{h['headline']}</span>
          </div>
          <span style='font-size:10px; padding:2px 8px; background:{mag_color}22;
                      border:1px solid {mag_color}; border-radius:3px; color:{mag_color};
                      font-weight:600; letter-spacing:0.5px;'>{h['magnitude']}</span>
        </div>
        """, unsafe_allow_html=True)

    commodities = _sg_trade_flow_commodities()
    commodity = st.selectbox("Select commodity group to analyze",
                              options=list(commodities.keys()),
                              key='sg_trade_commodity')
    c = commodities[commodity]

    st.markdown(f"""
    <div style='background:linear-gradient(135deg, rgba(0,212,255,0.08), rgba(0,15,35,0.5));
                border:1px solid rgba(0,212,255,0.3); border-radius:8px;
                padding:14px 18px; margin:14px 0;'>
      <div style='display:flex; justify-content:space-between; align-items:center;'>
        <div>
          <div style='font-size:11px; color:#00d4ff; font-weight:600; letter-spacing:1.5px; margin-bottom:4px;'>GLOBAL ANNUAL TRADE (2024)</div>
          <div style='font-size:22px; font-weight:700; color:#e0e8f0;'>USD {c['global_trade_usd']}</div>
        </div>
        <div style='text-align:right; font-size:11px; color:#8aa0bc; max-width:380px;'>
          {c['key_dynamic']}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_e, col_i = st.columns(2)
    with col_e:
        st.markdown("<div style='font-size:14px; color:#00d4ff; font-weight:600; letter-spacing:1px; margin-bottom:10px;'>TOP EXPORTERS</div>", unsafe_allow_html=True)
        max_exp = max([e['share'] for e in c['top_exporters']], default=1)
        for i, e in enumerate(c['top_exporters'], 1):
            bar_pct = (e['share'] / max_exp) * 100
            st.markdown(f"""
            <div style='background:rgba(0,20,45,0.4); border:1px solid rgba(0,212,255,0.08);
                        border-radius:6px; padding:8px 12px; margin-bottom:5px;'>
              <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>
                <div style='display:flex; gap:8px; align-items:center;'>
                  <span style='color:#5a6b82; font-size:10px; width:16px;'>{i}</span>
                  <span style='font-size:12px; color:#e0e8f0; font-weight:600;'>{e['country']}</span>
                </div>
                <div style='font-size:11px; color:#00d4ff; font-weight:700;'>{e['share']}%
                  <span style='color:#5a6b82; margin-left:4px;'>${e['value_b']}B</span>
                </div>
              </div>
              <div style='background:rgba(0,0,0,0.3); border-radius:3px; height:4px;'>
                <div style='background:linear-gradient(90deg, #00d4ff, #00ffc8);
                            width:{bar_pct}%; height:100%; border-radius:3px;'></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    with col_i:
        st.markdown("<div style='font-size:14px; color:#ff9800; font-weight:600; letter-spacing:1px; margin-bottom:10px;'>TOP IMPORTERS</div>", unsafe_allow_html=True)
        max_imp = max([e['share'] for e in c['top_importers']], default=1)
        for i, e in enumerate(c['top_importers'], 1):
            bar_pct = (e['share'] / max_imp) * 100
            st.markdown(f"""
            <div style='background:rgba(0,20,45,0.4); border:1px solid rgba(255,152,0,0.08);
                        border-radius:6px; padding:8px 12px; margin-bottom:5px;'>
              <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>
                <div style='display:flex; gap:8px; align-items:center;'>
                  <span style='color:#5a6b82; font-size:10px; width:16px;'>{i}</span>
                  <span style='font-size:12px; color:#e0e8f0; font-weight:600;'>{e['country']}</span>
                </div>
                <div style='font-size:11px; color:#ff9800; font-weight:700;'>{e['share']}%
                  <span style='color:#5a6b82; margin-left:4px;'>${e['value_b']}B</span>
                </div>
              </div>
              <div style='background:rgba(0,0,0,0.3); border-radius:3px; height:4px;'>
                <div style='background:linear-gradient(90deg, #ff7a00, #ffd000);
                            width:{bar_pct}%; height:100%; border-radius:3px;'></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    exp_top3 = sum(e['share'] for e in c['top_exporters'][:3])
    imp_top3 = sum(e['share'] for e in c['top_importers'][:3])
    st.markdown(f"""
    <div style='background:rgba(0,20,45,0.4); border:1px solid rgba(0,212,255,0.12);
                border-radius:6px; padding:12px 16px; margin-top:16px;'>
      <div style='font-size:11px; color:#00d4ff; font-weight:600; letter-spacing:1px; margin-bottom:6px;'>CONCENTRATION ANALYSIS</div>
      <div style='display:grid; grid-template-columns:1fr 1fr; gap:12px;'>
        <div>
          <div style='font-size:10px; color:#5a6b82;'>TOP 3 EXPORTERS</div>
          <div style='font-size:15px; color:#e0e8f0; font-weight:700;'>{exp_top3}% of world exports</div>
        </div>
        <div>
          <div style='font-size:10px; color:#5a6b82;'>TOP 3 IMPORTERS</div>
          <div style='font-size:15px; color:#e0e8f0; font-weight:700;'>{imp_top3}% of world imports</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Sources: UN Comtrade (comtradeplus.un.org), WTO Trade Statistics, IEA (energy), USGS (minerals).")


# -------------------- PHASE 7: LPI CORRIDOR VIEW --------------------

def _sg_lpi_data():
    return [
        {'country': 'Singapore', 'iso': 'SGP', 'rank': 1, 'overall': 4.3, 'customs': 4.0, 'infra': 4.6, 'shipments': 4.3, 'competence': 4.4, 'tracking': 4.4, 'timeliness': 4.3, 'region': 'Asia'},
        {'country': 'Finland', 'iso': 'FIN', 'rank': 2, 'overall': 4.2, 'customs': 4.0, 'infra': 4.2, 'shipments': 4.3, 'competence': 4.4, 'tracking': 4.2, 'timeliness': 4.3, 'region': 'Europe'},
        {'country': 'Germany', 'iso': 'DEU', 'rank': 3, 'overall': 4.1, 'customs': 3.9, 'infra': 4.3, 'shipments': 3.7, 'competence': 4.2, 'tracking': 4.2, 'timeliness': 4.1, 'region': 'Europe'},
        {'country': 'Netherlands', 'iso': 'NLD', 'rank': 3, 'overall': 4.1, 'customs': 3.9, 'infra': 4.2, 'shipments': 3.9, 'competence': 4.3, 'tracking': 4.2, 'timeliness': 4.2, 'region': 'Europe'},
        {'country': 'Denmark', 'iso': 'DNK', 'rank': 5, 'overall': 4.1, 'customs': 4.0, 'infra': 4.1, 'shipments': 3.9, 'competence': 4.1, 'tracking': 4.1, 'timeliness': 4.3, 'region': 'Europe'},
        {'country': 'Switzerland', 'iso': 'CHE', 'rank': 7, 'overall': 4.1, 'customs': 4.2, 'infra': 4.3, 'shipments': 3.7, 'competence': 4.2, 'tracking': 4.0, 'timeliness': 4.2, 'region': 'Europe'},
        {'country': 'Austria', 'iso': 'AUT', 'rank': 8, 'overall': 4.0, 'customs': 3.7, 'infra': 4.1, 'shipments': 3.8, 'competence': 4.2, 'tracking': 4.1, 'timeliness': 4.2, 'region': 'Europe'},
        {'country': 'Belgium', 'iso': 'BEL', 'rank': 9, 'overall': 4.0, 'customs': 3.7, 'infra': 4.0, 'shipments': 3.8, 'competence': 4.1, 'tracking': 4.1, 'timeliness': 4.2, 'region': 'Europe'},
        {'country': 'Canada', 'iso': 'CAN', 'rank': 10, 'overall': 4.0, 'customs': 3.8, 'infra': 4.2, 'shipments': 3.7, 'competence': 4.1, 'tracking': 4.1, 'timeliness': 4.1, 'region': 'Americas'},
        {'country': 'Hong Kong', 'iso': 'HKG', 'rank': 11, 'overall': 4.0, 'customs': 3.7, 'infra': 4.2, 'shipments': 3.9, 'competence': 4.1, 'tracking': 4.0, 'timeliness': 4.1, 'region': 'Asia'},
        {'country': 'United States', 'iso': 'USA', 'rank': 17, 'overall': 3.8, 'customs': 3.5, 'infra': 4.1, 'shipments': 3.5, 'competence': 4.0, 'tracking': 4.0, 'timeliness': 4.1, 'region': 'Americas'},
        {'country': 'France', 'iso': 'FRA', 'rank': 13, 'overall': 3.9, 'customs': 3.7, 'infra': 4.0, 'shipments': 3.7, 'competence': 4.0, 'tracking': 4.0, 'timeliness': 4.0, 'region': 'Europe'},
        {'country': 'United Kingdom', 'iso': 'GBR', 'rank': 19, 'overall': 3.8, 'customs': 3.5, 'infra': 4.0, 'shipments': 3.6, 'competence': 3.9, 'tracking': 3.9, 'timeliness': 3.9, 'region': 'Europe'},
        {'country': 'Japan', 'iso': 'JPN', 'rank': 15, 'overall': 3.9, 'customs': 3.7, 'infra': 4.1, 'shipments': 3.6, 'competence': 4.0, 'tracking': 4.0, 'timeliness': 4.0, 'region': 'Asia'},
        {'country': 'China', 'iso': 'CHN', 'rank': 19, 'overall': 3.7, 'customs': 3.3, 'infra': 4.0, 'shipments': 3.7, 'competence': 3.7, 'tracking': 3.7, 'timeliness': 3.8, 'region': 'Asia'},
        {'country': 'UAE', 'iso': 'ARE', 'rank': 7, 'overall': 4.0, 'customs': 3.9, 'infra': 4.4, 'shipments': 3.9, 'competence': 4.1, 'tracking': 4.1, 'timeliness': 4.1, 'region': 'Middle East'},
        {'country': 'South Korea', 'iso': 'KOR', 'rank': 17, 'overall': 3.8, 'customs': 3.6, 'infra': 4.1, 'shipments': 3.6, 'competence': 3.9, 'tracking': 3.8, 'timeliness': 3.9, 'region': 'Asia'},
        {'country': 'Italy', 'iso': 'ITA', 'rank': 19, 'overall': 3.7, 'customs': 3.4, 'infra': 3.8, 'shipments': 3.7, 'competence': 3.8, 'tracking': 3.8, 'timeliness': 3.9, 'region': 'Europe'},
        {'country': 'Spain', 'iso': 'ESP', 'rank': 26, 'overall': 3.7, 'customs': 3.4, 'infra': 3.8, 'shipments': 3.4, 'competence': 3.7, 'tracking': 3.8, 'timeliness': 4.1, 'region': 'Europe'},
        {'country': 'Australia', 'iso': 'AUS', 'rank': 19, 'overall': 3.8, 'customs': 3.7, 'infra': 3.9, 'shipments': 3.4, 'competence': 3.9, 'tracking': 4.0, 'timeliness': 4.0, 'region': 'Oceania'},
        {'country': 'India', 'iso': 'IND', 'rank': 38, 'overall': 3.4, 'customs': 3.0, 'infra': 3.2, 'shipments': 3.5, 'competence': 3.4, 'tracking': 3.4, 'timeliness': 3.6, 'region': 'Asia'},
        {'country': 'Saudi Arabia', 'iso': 'SAU', 'rank': 38, 'overall': 3.3, 'customs': 3.0, 'infra': 3.3, 'shipments': 3.4, 'competence': 3.2, 'tracking': 3.3, 'timeliness': 3.6, 'region': 'Middle East'},
        {'country': 'Turkiye', 'iso': 'TUR', 'rank': 38, 'overall': 3.4, 'customs': 3.1, 'infra': 3.4, 'shipments': 3.4, 'competence': 3.4, 'tracking': 3.5, 'timeliness': 3.6, 'region': 'Middle East'},
        {'country': 'Thailand', 'iso': 'THA', 'rank': 34, 'overall': 3.5, 'customs': 3.2, 'infra': 3.7, 'shipments': 3.5, 'competence': 3.5, 'tracking': 3.6, 'timeliness': 3.7, 'region': 'Asia'},
        {'country': 'Mexico', 'iso': 'MEX', 'rank': 66, 'overall': 2.9, 'customs': 2.6, 'infra': 2.9, 'shipments': 3.0, 'competence': 3.0, 'tracking': 3.0, 'timeliness': 3.2, 'region': 'Americas'},
        {'country': 'Brazil', 'iso': 'BRA', 'rank': 51, 'overall': 3.2, 'customs': 2.9, 'infra': 3.2, 'shipments': 3.2, 'competence': 3.3, 'tracking': 3.4, 'timeliness': 3.4, 'region': 'Americas'},
        {'country': 'South Africa', 'iso': 'ZAF', 'rank': 56, 'overall': 3.1, 'customs': 2.9, 'infra': 3.1, 'shipments': 3.1, 'competence': 3.2, 'tracking': 3.2, 'timeliness': 3.3, 'region': 'Africa'},
        {'country': 'Indonesia', 'iso': 'IDN', 'rank': 61, 'overall': 3.0, 'customs': 2.8, 'infra': 2.9, 'shipments': 3.0, 'competence': 3.0, 'tracking': 3.0, 'timeliness': 3.3, 'region': 'Asia'},
        {'country': 'Egypt', 'iso': 'EGY', 'rank': 57, 'overall': 3.0, 'customs': 2.8, 'infra': 3.0, 'shipments': 3.0, 'competence': 2.9, 'tracking': 3.0, 'timeliness': 3.2, 'region': 'MENA'},
        {'country': 'Vietnam', 'iso': 'VNM', 'rank': 43, 'overall': 3.3, 'customs': 3.1, 'infra': 3.2, 'shipments': 3.3, 'competence': 3.3, 'tracking': 3.4, 'timeliness': 3.5, 'region': 'Asia'},
        {'country': 'Russia', 'iso': 'RUS', 'rank': 88, 'overall': 2.6, 'customs': 2.3, 'infra': 2.8, 'shipments': 2.6, 'competence': 2.6, 'tracking': 2.7, 'timeliness': 2.8, 'region': 'Europe'},
    ]


def _sg_lpi_color(score):
    if score >= 4.0: return '#00ffc8'
    if score >= 3.5: return '#7fb800'
    if score >= 3.0: return '#ffd000'
    if score >= 2.5: return '#ff7a00'
    return '#ff2952'


def render_lpi_tab():
    """Render the LPI tab (Tab 13)."""
    st.markdown("""
    <div style="margin-bottom:16px;">
      <div style="font-size:18px; font-weight:600; color:#e0e8f0;">Logistics Performance Index (LPI)</div>
      <div style="font-size:12px; color:#5a6b82; margin-top:4px;">
        World Bank LPI 2023 &middot; 6 dimensions &middot; Country corridor performance benchmark (higher = better)
      </div>
    </div>
    """, unsafe_allow_html=True)

    lpi_data = _sg_lpi_data()
    dims = {
        'customs': 'Efficiency of customs & border clearance',
        'infra': 'Quality of trade & transport infrastructure',
        'shipments': 'Ease of arranging competitively priced shipments',
        'competence': 'Competence & quality of logistics services',
        'tracking': 'Ability to track & trace consignments',
        'timeliness': 'Frequency of shipments arriving within scheduled time',
    }

    regions = ['All'] + sorted(set(d['region'] for d in lpi_data))
    sel_region = st.selectbox("Filter by region", regions, key='sg_lpi_region')

    filtered = lpi_data if sel_region == 'All' else [d for d in lpi_data if d['region'] == sel_region]
    filtered = sorted(filtered, key=lambda x: x['overall'], reverse=True)

    avg_overall = sum(d['overall'] for d in filtered) / max(len(filtered), 1)
    best = filtered[0] if filtered else None
    worst = filtered[-1] if filtered else None

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.markdown(f"""
        <div style='background:rgba(0,20,45,0.4); border:1px solid rgba(0,212,255,0.12);
                    border-radius:8px; padding:12px 16px;'>
          <div style='font-size:10px; color:#5a6b82; letter-spacing:1px;'>REGION AVERAGE</div>
          <div style='font-size:22px; color:#e0e8f0; font-weight:700;'>{avg_overall:.2f}</div>
          <div style='font-size:10px; color:#8aa0bc;'>out of 5.0</div>
        </div>
        """, unsafe_allow_html=True)
    with col_s2:
        if best:
            st.markdown(f"""
            <div style='background:rgba(0,20,45,0.4); border:1px solid rgba(0,255,200,0.25);
                        border-radius:8px; padding:12px 16px;'>
              <div style='font-size:10px; color:#5a6b82; letter-spacing:1px;'>TOP PERFORMER</div>
              <div style='font-size:16px; color:#e0e8f0; font-weight:700;'>{best['country']}</div>
              <div style='font-size:11px; color:#00ffc8; font-weight:600;'>{best['overall']:.1f} &middot; Rank #{best['rank']}</div>
            </div>
            """, unsafe_allow_html=True)
    with col_s3:
        if worst:
            st.markdown(f"""
            <div style='background:rgba(0,20,45,0.4); border:1px solid rgba(255,122,0,0.25);
                        border-radius:8px; padding:12px 16px;'>
              <div style='font-size:10px; color:#5a6b82; letter-spacing:1px;'>LOWEST IN VIEW</div>
              <div style='font-size:16px; color:#e0e8f0; font-weight:700;'>{worst['country']}</div>
              <div style='font-size:11px; color:#ff7a00; font-weight:600;'>{worst['overall']:.1f} &middot; Rank #{worst['rank']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div style='display:grid; grid-template-columns: 1.8fr 0.6fr 0.7fr 0.7fr 0.7fr 0.8fr 0.7fr 0.7fr;
                gap:6px; padding:10px 14px; font-size:10px; color:#5a6b82;
                letter-spacing:1.5px; font-weight:700;
                border-bottom:1px solid rgba(0,212,255,0.15); margin:18px 0 6px 0;'>
      <div>COUNTRY</div>
      <div style='text-align:center;'>OVERALL</div>
      <div style='text-align:center;'>CUSTOMS</div>
      <div style='text-align:center;'>INFRA</div>
      <div style='text-align:center;'>SHIPMENTS</div>
      <div style='text-align:center;'>COMPETENCE</div>
      <div style='text-align:center;'>TRACKING</div>
      <div style='text-align:center;'>TIMELINESS</div>
    </div>
    """, unsafe_allow_html=True)

    for d in filtered:
        color = _sg_lpi_color(d['overall'])
        st.markdown(f"""
        <div style='display:grid; grid-template-columns: 1.8fr 0.6fr 0.7fr 0.7fr 0.7fr 0.8fr 0.7fr 0.7fr;
                    gap:6px; padding:9px 14px; align-items:center;
                    background:rgba(0,20,45,0.3); border:1px solid rgba(0,212,255,0.08);
                    border-left:3px solid {color}; border-radius:6px; margin-bottom:5px;
                    font-size:12px;'>
          <div>
            <div style='color:#e0e8f0; font-weight:600;'>{d['country']}</div>
            <div style='font-size:10px; color:#5a6b82; margin-top:2px;'>Rank #{d['rank']} &middot; {d['region']}</div>
          </div>
          <div style='text-align:center;'>
            <span style='font-size:15px; font-weight:700; color:{color};'>{d['overall']:.1f}</span>
          </div>
          <div style='text-align:center; color:{_sg_lpi_color(d['customs'])};'>{d['customs']:.1f}</div>
          <div style='text-align:center; color:{_sg_lpi_color(d['infra'])};'>{d['infra']:.1f}</div>
          <div style='text-align:center; color:{_sg_lpi_color(d['shipments'])};'>{d['shipments']:.1f}</div>
          <div style='text-align:center; color:{_sg_lpi_color(d['competence'])};'>{d['competence']:.1f}</div>
          <div style='text-align:center; color:{_sg_lpi_color(d['tracking'])};'>{d['tracking']:.1f}</div>
          <div style='text-align:center; color:{_sg_lpi_color(d['timeliness'])};'>{d['timeliness']:.1f}</div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("Dimension definitions"):
        for k, v in dims.items():
            st.markdown(f"""
            <div style='display:flex; gap:12px; padding:6px 10px;
                        background:rgba(0,20,45,0.3); border-radius:4px; margin-bottom:4px;
                        font-size:12px;'>
              <div style='color:#00d4ff; font-weight:600; width:110px; letter-spacing:0.5px;'>{k.upper()}</div>
              <div style='color:#bdd2ea;'>{v}</div>
            </div>
            """, unsafe_allow_html=True)

    st.caption("Source: World Bank LPI 2023 (lpi.worldbank.org). Updated every 2-3 years.")
