# =====================================================================
# NERAI GLOBAL VIEW - 3D rotating globe (ECharts-GL) with 8 intelligence layers
# Chokepoints · Ports · Trade arcs · Sanctions · Materials · GDELT · Weather · Country Risk
# =====================================================================
import streamlit as st
import streamlit.components.v1 as components
import json


# ---------- LAYER DATA ----------

def _gv_chokepoints():
    return [
        {'name': 'Strait of Hormuz', 'lat': 26.57, 'lon': 56.25, 'score': 92, 'info': 'CRITICAL · 20% of global oil transit'},
        {'name': 'Bab el-Mandeb / Red Sea', 'lat': 12.58, 'lon': 43.33, 'score': 78, 'info': 'HIGH · Houthi attacks ongoing'},
        {'name': 'Suez Canal', 'lat': 30.42, 'lon': 32.36, 'score': 72, 'info': 'HIGH · ~50% traffic down'},
        {'name': 'Strait of Malacca', 'lat': 2.5, 'lon': 101.5, 'score': 55, 'info': 'ELEVATED · 30% global oil'},
        {'name': 'Taiwan Strait', 'lat': 24.5, 'lon': 119.5, 'score': 68, 'info': 'ELEVATED · 88% advanced chips'},
        {'name': 'Panama Canal', 'lat': 9.08, 'lon': -79.68, 'score': 45, 'info': 'MODERATE · Drought recovery'},
        {'name': 'Bosphorus', 'lat': 41.12, 'lon': 29.07, 'score': 58, 'info': 'ELEVATED · Black Sea exports'},
        {'name': 'Danish Straits', 'lat': 55.5, 'lon': 11.5, 'score': 42, 'info': 'MODERATE · Russian shadow fleet'},
    ]


def _gv_ports():
    return [
        {'name': 'Shanghai', 'lat': 31.24, 'lon': 121.50, 'rank': 'Global #1'},
        {'name': 'Singapore', 'lat': 1.27, 'lon': 103.84, 'rank': 'Global #2'},
        {'name': 'Rotterdam', 'lat': 51.93, 'lon': 4.14, 'rank': 'EU #1'},
        {'name': 'Busan', 'lat': 35.10, 'lon': 129.04, 'rank': 'Global #7'},
        {'name': 'Los Angeles', 'lat': 33.75, 'lon': -118.2, 'rank': 'US #1'},
        {'name': 'Hamburg', 'lat': 53.55, 'lon': 9.99, 'rank': 'EU #3'},
        {'name': 'Antwerp', 'lat': 51.26, 'lon': 4.4, 'rank': 'EU #2'},
        {'name': 'New York / NJ', 'lat': 40.67, 'lon': -74.1, 'rank': 'US #3'},
        {'name': 'Jebel Ali (Dubai)', 'lat': 25.03, 'lon': 55.07, 'rank': 'MENA #1'},
        {'name': 'Houston', 'lat': 29.74, 'lon': -95.27, 'rank': 'US #7'},
        {'name': 'Tokyo', 'lat': 35.45, 'lon': 139.65, 'rank': 'Japan #1'},
        {'name': 'Hong Kong', 'lat': 22.32, 'lon': 114.17, 'rank': 'Asia hub'},
    ]


def _gv_trade_arcs():
    """Key bilateral trade flows: source -> target."""
    return [
        {'from_lat': 24.47, 'from_lon': 39.61, 'to_lat': 35.86, 'to_lon': 104.19, 'label': 'Saudi oil -> China', 'category': 'oil', 'intensity': 10},
        {'from_lat': 60.0, 'from_lon': 90.0, 'to_lat': 20.59, 'to_lon': 78.96, 'label': 'Russia oil -> India', 'category': 'oil', 'intensity': 9},
        {'from_lat': 60.0, 'from_lon': 90.0, 'to_lat': 35.86, 'to_lon': 104.19, 'label': 'Russia oil -> China', 'category': 'oil', 'intensity': 8},
        {'from_lat': 33.0, 'from_lon': 44.0, 'to_lat': 51.16, 'to_lon': 10.45, 'label': 'Iraq oil -> Germany', 'category': 'oil', 'intensity': 5},
        {'from_lat': 29.76, 'from_lon': -95.37, 'to_lat': 51.16, 'to_lon': 10.45, 'label': 'US LNG -> Germany', 'category': 'lng', 'intensity': 8},
        {'from_lat': 25.29, 'from_lon': 51.53, 'to_lat': 35.67, 'to_lon': 139.65, 'label': 'Qatar LNG -> Japan', 'category': 'lng', 'intensity': 7},
        {'from_lat': -25.27, 'from_lon': 133.77, 'to_lat': 35.86, 'to_lon': 104.19, 'label': 'Australia LNG -> China', 'category': 'lng', 'intensity': 9},
        {'from_lat': 23.69, 'from_lon': 120.96, 'to_lat': 35.86, 'to_lon': 104.19, 'label': 'Taiwan chips -> China', 'category': 'chip', 'intensity': 10},
        {'from_lat': 23.69, 'from_lon': 120.96, 'to_lat': 37.09, 'to_lon': -95.71, 'label': 'Taiwan chips -> USA', 'category': 'chip', 'intensity': 8},
        {'from_lat': 35.90, 'from_lon': 127.76, 'to_lat': 35.86, 'to_lon': 104.19, 'label': 'Korea chips -> China', 'category': 'chip', 'intensity': 9},
        {'from_lat': 60.0, 'from_lon': 90.0, 'to_lat': 26.82, 'to_lon': 30.80, 'label': 'Russia wheat -> Egypt', 'category': 'food', 'intensity': 6},
        {'from_lat': 60.0, 'from_lon': 90.0, 'to_lat': 38.96, 'to_lon': 35.24, 'label': 'Russia wheat -> Turkiye', 'category': 'food', 'intensity': 5},
        {'from_lat': -25.27, 'from_lon': 133.77, 'to_lat': 35.86, 'to_lon': 104.19, 'label': 'Australia iron -> China', 'category': 'ore', 'intensity': 10},
        {'from_lat': -14.23, 'from_lon': -51.92, 'to_lat': 35.86, 'to_lon': 104.19, 'label': 'Brazil iron -> China', 'category': 'ore', 'intensity': 8},
        {'from_lat': 35.86, 'from_lon': 104.19, 'to_lat': 51.16, 'to_lon': 10.45, 'label': 'China REE -> Germany', 'category': 'material', 'intensity': 7},
        {'from_lat': 35.86, 'from_lon': 104.19, 'to_lat': 37.09, 'to_lon': -95.71, 'label': 'China REE -> USA', 'category': 'material', 'intensity': 6},
        {'from_lat': -4.04, 'from_lon': 21.75, 'to_lat': 35.86, 'to_lon': 104.19, 'label': 'DRC cobalt -> China', 'category': 'material', 'intensity': 8},
        {'from_lat': -14.23, 'from_lon': -51.92, 'to_lat': 35.86, 'to_lon': 104.19, 'label': 'Brazil soy -> China', 'category': 'food', 'intensity': 9},
    ]


def _gv_sanctioned_countries():
    return [
        {'name': 'Russia', 'lat': 61.52, 'lon': 105.31, 'severity': 95},
        {'name': 'Iran', 'lat': 32.43, 'lon': 53.69, 'severity': 92},
        {'name': 'North Korea', 'lat': 40.34, 'lon': 127.51, 'severity': 98},
        {'name': 'Belarus', 'lat': 53.71, 'lon': 27.95, 'severity': 80},
        {'name': 'Syria', 'lat': 34.80, 'lon': 38.99, 'severity': 78},
        {'name': 'Myanmar', 'lat': 21.91, 'lon': 95.95, 'severity': 75},
        {'name': 'Venezuela', 'lat': 6.42, 'lon': -66.58, 'severity': 72},
        {'name': 'Cuba', 'lat': 21.52, 'lon': -77.78, 'severity': 60},
    ]


def _gv_material_producers():
    return [
        {'material': 'Rare Earths', 'country': 'China (Inner Mongolia)', 'lat': 40.82, 'lon': 111.65, 'share': 70},
        {'material': 'Rare Earths', 'country': 'Australia (Mt Weld)', 'lat': -28.85, 'lon': 122.55, 'share': 14},
        {'material': 'Rare Earths', 'country': 'USA (Mountain Pass)', 'lat': 35.47, 'lon': -115.53, 'share': 9},
        {'material': 'Cobalt', 'country': 'DRC (Katanga)', 'lat': -10.72, 'lon': 25.47, 'share': 70},
        {'material': 'Lithium', 'country': 'Australia (Greenbushes)', 'lat': -33.87, 'lon': 116.08, 'share': 47},
        {'material': 'Lithium', 'country': 'Chile (Atacama)', 'lat': -23.50, 'lon': -68.20, 'share': 24},
        {'material': 'Copper', 'country': 'Chile', 'lat': -33.45, 'lon': -70.67, 'share': 24},
        {'material': 'Uranium', 'country': 'Kazakhstan', 'lat': 48.02, 'lon': 66.92, 'share': 43},
        {'material': 'Gallium', 'country': 'China', 'lat': 31.65, 'lon': 117.27, 'share': 98},
        {'material': 'Nickel', 'country': 'Indonesia (Sulawesi)', 'lat': -2.78, 'lon': 121.08, 'share': 50},
        {'material': 'Palladium', 'country': 'Russia (Norilsk)', 'lat': 69.35, 'lon': 88.20, 'share': 40},
        {'material': 'Platinum', 'country': 'South Africa (Bushveld)', 'lat': -25.40, 'lon': 27.50, 'share': 70},
        {'material': 'Tungsten', 'country': 'China (Jiangxi)', 'lat': 27.82, 'lon': 115.95, 'share': 80},
        {'material': 'Natural Gas', 'country': 'Qatar (North Field)', 'lat': 25.80, 'lon': 51.75, 'share': 20},
        {'material': 'Oil', 'country': 'Saudi Arabia (Ghawar)', 'lat': 25.70, 'lon': 49.50, 'share': 16},
    ]


def _gv_gdelt_events():
    return [
        {'event': 'US-Iran talks failed (Islamabad)', 'lat': 33.68, 'lon': 73.04, 'severity': 'HIGH', 'days_ago': 3},
        {'event': 'Israel strikes in Lebanon (Black Wednesday)', 'lat': 33.89, 'lon': 35.50, 'severity': 'CRITICAL', 'days_ago': 5},
        {'event': 'Iran mining threat - Hormuz', 'lat': 26.57, 'lon': 56.25, 'severity': 'CRITICAL', 'days_ago': 4},
        {'event': 'Houthi attacks resume - Red Sea', 'lat': 13.5, 'lon': 42.8, 'severity': 'HIGH', 'days_ago': 2},
        {'event': 'PLA Taiwan exercises', 'lat': 24.5, 'lon': 119.5, 'severity': 'ELEVATED', 'days_ago': 6},
        {'event': 'Russia-Ukraine escalation', 'lat': 48.02, 'lon': 37.80, 'severity': 'HIGH', 'days_ago': 1},
        {'event': 'Iraq leadership change', 'lat': 33.32, 'lon': 44.36, 'severity': 'ELEVATED', 'days_ago': 7},
        {'event': 'Ghana military unrest', 'lat': 7.95, 'lon': -1.03, 'severity': 'ELEVATED', 'days_ago': 4},
        {'event': 'Kuwait diplomatic tension', 'lat': 29.31, 'lon': 47.48, 'severity': 'ELEVATED', 'days_ago': 3},
        {'event': 'US Yemen strikes', 'lat': 15.55, 'lon': 48.52, 'severity': 'HIGH', 'days_ago': 2},
        {'event': 'Panama slot auction spike', 'lat': 9.08, 'lon': -79.68, 'severity': 'MODERATE', 'days_ago': 5},
        {'event': 'EU Russia sanctions 15th package', 'lat': 50.85, 'lon': 4.35, 'severity': 'MODERATE', 'days_ago': 8},
    ]


def _gv_weather_advisories():
    return [
        {'port': 'Houston', 'lat': 29.74, 'lon': -95.27, 'event': 'Heat advisory'},
        {'port': 'New York', 'lat': 40.67, 'lon': -74.1, 'event': 'Coastal fog'},
        {'port': 'Singapore', 'lat': 1.27, 'lon': 103.84, 'event': 'Afternoon storms'},
        {'port': 'Rotterdam', 'lat': 51.93, 'lon': 4.14, 'event': 'North Sea gale'},
        {'port': 'Savannah', 'lat': 32.08, 'lon': -81.1, 'event': 'Tropical watch'},
    ]


def _gv_country_risk_markers():
    return [
        {'country': 'Germany', 'lat': 51.16, 'lon': 10.45, 'risk': 70},
        {'country': 'Japan', 'lat': 36.20, 'lon': 138.25, 'risk': 74},
        {'country': 'S.Korea', 'lat': 35.90, 'lon': 127.76, 'risk': 81},
        {'country': 'India', 'lat': 20.59, 'lon': 78.96, 'risk': 56},
        {'country': 'USA', 'lat': 37.09, 'lon': -95.71, 'risk': 31},
        {'country': 'Singapore', 'lat': 1.27, 'lon': 103.84, 'risk': 78},
        {'country': 'Turkiye', 'lat': 38.96, 'lon': 35.24, 'risk': 60},
        {'country': 'Brazil', 'lat': -14.23, 'lon': -51.92, 'risk': 28},
        {'country': 'Italy', 'lat': 41.87, 'lon': 12.57, 'risk': 68},
        {'country': 'Egypt', 'lat': 26.82, 'lon': 30.80, 'risk': 56},
    ]


# ---------- COLOR HELPERS ----------

def _severity_color_hex(score):
    if score >= 90: return '#ff2952'
    if score >= 75: return '#ff7a00'
    if score >= 55: return '#ffd000'
    if score >= 30: return '#7fb800'
    return '#00d4ff'


def _category_color_hex(cat):
    return {
        'oil': '#ff7a00',
        'lng': '#00d4ff',
        'chip': '#c864ff',
        'food': '#ffd000',
        'ore': '#b49664',
        'material': '#ff29c8',
    }.get(cat, '#969696')


def _event_severity_color(sev):
    return {'CRITICAL': '#ff2952', 'HIGH': '#ff7a00', 'ELEVATED': '#ffd000', 'MODERATE': '#7fb800'}.get(sev, '#00d4ff')


# ---------- GLOBE HTML (ECharts-GL) ----------

def _build_globe_html(layers_enabled):
    """Generate ECharts-GL HTML with 3D globe and selected intelligence layers."""
    # Prepare series data
    chokepoints = [{
        'name': d['name'],
        'value': [d['lon'], d['lat'], d['score']],
        'itemStyle': {'color': _severity_color_hex(d['score'])},
        'info': d['info']
    } for d in _gv_chokepoints()]

    ports = [{
        'name': d['name'],
        'value': [d['lon'], d['lat'], 1],
        'rank': d['rank']
    } for d in _gv_ports()]

    arcs = [{
        'coords': [[d['from_lon'], d['from_lat']], [d['to_lon'], d['to_lat']]],
        'label': d['label'],
        'lineStyle': {'color': _category_color_hex(d['category']), 'width': 1 + d['intensity'] / 3}
    } for d in _gv_trade_arcs()]

    sanctions = [{
        'name': d['name'],
        'value': [d['lon'], d['lat'], d['severity']],
        'itemStyle': {'color': '#ff2952', 'opacity': 0.75}
    } for d in _gv_sanctioned_countries()]

    materials = [{
        'name': d['material'] + ' · ' + d['country'],
        'value': [d['lon'], d['lat'], d['share']],
        'itemStyle': {'color': '#ff29c8'},
        'share': d['share']
    } for d in _gv_material_producers()]

    events = [{
        'name': d['event'],
        'value': [d['lon'], d['lat'], 1],
        'itemStyle': {'color': _event_severity_color(d['severity'])},
        'severity': d['severity'],
        'days_ago': d['days_ago']
    } for d in _gv_gdelt_events()]

    weather = [{
        'name': d['port'],
        'value': [d['lon'], d['lat'], 1],
        'itemStyle': {'color': '#ffff00'},
        'event': d['event']
    } for d in _gv_weather_advisories()]

    risk = [{
        'name': d['country'],
        'value': [d['lon'], d['lat'], d['risk']],
        'itemStyle': {'color': _severity_color_hex(d['risk']), 'opacity': 0.7}
    } for d in _gv_country_risk_markers()]

    payload = json.dumps({
        'chokepoints': chokepoints, 'ports': ports, 'arcs': arcs,
        'sanctions': sanctions, 'materials': materials, 'events': events,
        'weather': weather, 'risk': risk
    })
    enabled = json.dumps(layers_enabled)

    html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/echarts-gl@2.0.9/dist/echarts-gl.min.js"></script>
<style>
  body { margin:0; padding:0; background:#0a0e17; color:#e0e8f0;
         font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; overflow:hidden; }
  #container { width:100%; height:720px; }
  #legend { position:absolute; top:12px; right:12px; z-index:5;
            background:rgba(0,15,35,0.85); border:1px solid rgba(0,212,255,0.25);
            border-radius:8px; padding:10px 14px; font-size:11px; color:#bdd2ea; max-width:240px; }
  #legend .item { display:flex; align-items:center; gap:8px; margin:4px 0; }
  #legend .dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }
  #errbox { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
            padding:14px 20px; background:rgba(255,41,82,0.1); border:1px solid #ff2952;
            border-radius:8px; color:#ff7a00; font-size:12px; max-width:500px; display:none; }
</style>
</head>
<body>
<div id="container"></div>
<div id="errbox"></div>
<div id="legend">
  <div style="color:#00d4ff; font-weight:700; letter-spacing:1.5px; margin-bottom:6px;
              border-bottom:1px solid rgba(0,212,255,0.2); padding-bottom:4px;">LEGEND</div>
  <div class="item"><div class="dot" style="background:#ff2952"></div>Chokepoint CRITICAL</div>
  <div class="item"><div class="dot" style="background:#ff7a00"></div>Chokepoint HIGH</div>
  <div class="item"><div class="dot" style="background:#ffd000"></div>Chokepoint ELEVATED</div>
  <div class="item"><div class="dot" style="background:rgba(255,41,82,0.5)"></div>Sanctioned jurisdiction</div>
  <div class="item"><div class="dot" style="background:#00d4ff"></div>Port (Top 12 global)</div>
  <div class="item"><div class="dot" style="background:#ff29c8"></div>Critical material source</div>
  <div class="item"><div class="dot" style="background:#ff2952"></div>Recent geopolitical event</div>
  <div class="item"><div class="dot" style="background:#ffff00"></div>Weather advisory</div>
  <div style="margin-top:8px; color:#5a6b82; font-size:10px;">Trade arcs colored by commodity · drag to rotate</div>
</div>
<script>
const D = __PAYLOAD__;
const EN = __ENABLED__;

function waitAndRender() {
  if (typeof echarts === 'undefined') {
    document.getElementById('errbox').style.display='block';
    document.getElementById('errbox').textContent='ECharts library failed to load';
    return;
  }
  if (!echarts.getMap && !echarts.registerMap) {
    // ECharts-GL not loaded yet, wait
    setTimeout(waitAndRender, 100);
    return;
  }

  const chart = echarts.init(document.getElementById('container'));
  const series = [];

  function scatter(name, data, symbolSize) {
    return {
      name: name, type: 'scatter3D', coordinateSystem: 'globe',
      data: data, symbolSize: symbolSize || 8,
      itemStyle: { borderColor: 'rgba(255,255,255,0.6)', borderWidth: 1 },
      emphasis: { itemStyle: { borderColor: '#fff', borderWidth: 2 }, label: { show: true, formatter: '{b}', color: '#fff', backgroundColor: 'rgba(0,15,35,0.9)', padding: [4,8], borderRadius: 4 } },
      blendMode: 'source-over'
    };
  }

  if (EN.chokepoints) series.push(Object.assign(scatter('Chokepoints', D.chokepoints, function(v){return 6 + v[2]/12;}), {}));
  if (EN.ports) series.push(scatter('Ports', D.ports, 5));
  if (EN.sanctions) series.push(scatter('Sanctions', D.sanctions, 14));
  if (EN.materials) series.push(scatter('Materials', D.materials, function(v){return 5 + v[2]/15;}));
  if (EN.events) series.push(scatter('Events', D.events, 10));
  if (EN.weather) series.push(scatter('Weather', D.weather, 8));
  if (EN.risk) series.push(scatter('Country Risk', D.risk, function(v){return 4 + v[2]/15;}));

  if (EN.arcs) {
    series.push({
      name: 'Trade Arcs', type: 'lines3D', coordinateSystem: 'globe',
      data: D.arcs,
      effect: { show: true, period: 4, trailWidth: 2, trailLength: 0.4, trailOpacity: 0.8 },
      blendMode: 'lighter',
      lineStyle: { width: 1.5, opacity: 0.7 }
    });
  }

  const option = {
    backgroundColor: '#0a0e17',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(0,15,35,0.95)',
      borderColor: 'rgba(0,212,255,0.5)',
      borderWidth: 1,
      textStyle: { color: '#e0e8f0', fontSize: 11 },
      formatter: function(p) {
        const d = p.data || {};
        let html = '<div style="color:#00d4ff;font-weight:700;letter-spacing:0.5px;margin-bottom:4px;font-size:10px;">'+(p.seriesName||'').toUpperCase()+'</div>';
        html += '<div style="font-weight:600;">'+(d.name||p.name||'')+'</div>';
        if (d.info) html += '<div style="color:#bdd2ea;margin-top:3px;">'+d.info+'</div>';
        if (d.rank) html += '<div style="color:#8aa0bc;margin-top:3px;">'+d.rank+'</div>';
        if (d.severity) html += '<div style="color:#ff7a00;margin-top:3px;">'+d.severity+(d.days_ago?' · '+d.days_ago+' days ago':'')+'</div>';
        if (d.event && p.seriesName==='Weather') html += '<div style="color:#ffd000;margin-top:3px;">'+d.event+'</div>';
        if (typeof d.share !== 'undefined') html += '<div style="color:#ff29c8;margin-top:3px;">Global share: '+d.share+'%</div>';
        if (d.label) html += '<div style="color:#bdd2ea;margin-top:3px;">'+d.label+'</div>';
        return html;
      }
    },
    globe: {
      globeRadius: 100,
      globeOuterRadius: 110,
      environment: '#0a0e17',
      shading: 'color',
      itemStyle: { color: '#1a2f4e' },
      atmosphere: { show: true, color: '#00d4ff', glowPower: 4, innerGlowPower: 2 },
      light: {
        main: { color: '#ffffff', intensity: 1.5, shadow: false, alpha: 40, beta: 40 },
        ambient: { color: '#ffffff', intensity: 0.4 }
      },
      viewControl: {
        autoRotate: true,
        autoRotateAfterStill: 3,
        autoRotateSpeed: 5,
        distance: 200,
        alpha: 25,
        beta: 160
      },
      postEffect: { enable: true, bloom: { enable: true, bloomIntensity: 0.15 } }
    },
    series: series
  };

  chart.setOption(option);
  window.addEventListener('resize', function(){ chart.resize(); });
}

waitAndRender();
</script>
</body>
</html>
"""
    html = html.replace('__PAYLOAD__', payload).replace('__ENABLED__', enabled)
    return html


# ---------- RENDER ----------

def render_global_view():
    """Render the Global View page with 3D rotating globe + layer toggles."""
    st.markdown("""
    <div style="margin: 8px 0 16px 0;">
      <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
        <div style="font-size:11px; letter-spacing:3px; color:#00d4ff; font-weight:700;
                    text-transform:uppercase;">NERAI · GLOBAL VIEW</div>
        <div style="height:1px; flex:1;
                    background:linear-gradient(90deg, rgba(0,212,255,0.4), transparent);"></div>
        <div style="font-size:10px; color:#5a6b82; letter-spacing:1.5px;">3D INTELLIGENCE GLOBE</div>
      </div>
      <div style="font-size:30px; font-weight:700; color:#e0e8f0; margin-bottom:4px; letter-spacing:-0.5px;">
        Global Intelligence View
      </div>
      <div style="font-size:13px; color:#8aa0bc; max-width:760px; line-height:1.6;">
        Interactive 3D globe with 8 intelligence layers. Drag to rotate, scroll to zoom, hover for details.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Layer toggles
    st.markdown("<div style='font-size:11px; color:#00d4ff; font-weight:600; letter-spacing:1.5px; margin:10px 0 6px 0;'>LAYERS</div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        l_chokepoints = st.checkbox("Chokepoints", value=True, key='gv_l1')
        l_arcs = st.checkbox("Trade Arcs", value=True, key='gv_l2')
    with col2:
        l_ports = st.checkbox("Ports", value=True, key='gv_l3')
        l_materials = st.checkbox("Material Sources", value=True, key='gv_l4')
    with col3:
        l_sanctions = st.checkbox("Sanctions", value=True, key='gv_l5')
        l_events = st.checkbox("GDELT Events", value=True, key='gv_l6')
    with col4:
        l_weather = st.checkbox("Weather Alerts", value=True, key='gv_l7')
        l_risk = st.checkbox("Country Risk", value=False, key='gv_l8')

    layers_enabled = {
        'chokepoints': l_chokepoints, 'ports': l_ports, 'arcs': l_arcs,
        'sanctions': l_sanctions, 'materials': l_materials, 'events': l_events,
        'weather': l_weather, 'risk': l_risk
    }

    enabled_count = sum(1 for v in layers_enabled.values() if v)
    st.markdown(f"<div style='font-size:11px; color:#8aa0bc; margin-bottom:12px;'>{enabled_count} of 8 layers active · drag globe to rotate · scroll to zoom · hover dots for details</div>", unsafe_allow_html=True)

    # Render globe
    html = _build_globe_html(layers_enabled)
    components.html(html, height=740, scrolling=False)

    # Caption
    st.markdown("""
    <div style='margin-top:16px; padding:12px 16px; background:rgba(0,20,45,0.4);
                border:1px solid rgba(0,212,255,0.12); border-radius:8px;
                font-size:11px; color:#8aa0bc; line-height:1.6;'>
      <b style='color:#00d4ff;'>Data sources:</b> IMF PortWatch, UNCTAD, USGS, UN Comtrade, NOAA/NWS,
      GDELT · <b style='color:#00d4ff;'>Rendering:</b> ECharts-GL 3D Globe (WebGL) ·
      Trade arcs show great-circle paths with animated effects · All coordinates centroid-based
    </div>
    """, unsafe_allow_html=True)
