# =====================================================================
# NERAI GLOBAL VIEW - 3D rotating globe (deck.gl) with 8 intelligence layers
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
        # Oil flows
        {'from_lat': 24.47, 'from_lon': 39.61, 'to_lat': 35.86, 'to_lon': 104.19, 'label': 'Saudi oil -> China', 'category': 'oil', 'intensity': 10},
        {'from_lat': 60.0, 'from_lon': 90.0, 'to_lat': 20.59, 'to_lon': 78.96, 'label': 'Russia oil -> India', 'category': 'oil', 'intensity': 9},
        {'from_lat': 60.0, 'from_lon': 90.0, 'to_lat': 35.86, 'to_lon': 104.19, 'label': 'Russia oil -> China', 'category': 'oil', 'intensity': 8},
        {'from_lat': 33.0, 'from_lon': 44.0, 'to_lat': 51.16, 'to_lon': 10.45, 'label': 'Iraq oil -> Germany', 'category': 'oil', 'intensity': 5},
        # LNG flows
        {'from_lat': 29.76, 'from_lon': -95.37, 'to_lat': 51.16, 'to_lon': 10.45, 'label': 'US LNG -> Germany', 'category': 'lng', 'intensity': 8},
        {'from_lat': 25.29, 'from_lon': 51.53, 'to_lat': 35.67, 'to_lon': 139.65, 'label': 'Qatar LNG -> Japan', 'category': 'lng', 'intensity': 7},
        {'from_lat': -25.27, 'from_lon': 133.77, 'to_lat': 35.86, 'to_lon': 104.19, 'label': 'Australia LNG -> China', 'category': 'lng', 'intensity': 9},
        # Chips
        {'from_lat': 23.69, 'from_lon': 120.96, 'to_lat': 35.86, 'to_lon': 104.19, 'label': 'Taiwan chips -> China', 'category': 'chip', 'intensity': 10},
        {'from_lat': 23.69, 'from_lon': 120.96, 'to_lat': 37.09, 'to_lon': -95.71, 'label': 'Taiwan chips -> USA', 'category': 'chip', 'intensity': 8},
        {'from_lat': 35.90, 'from_lon': 127.76, 'to_lat': 35.86, 'to_lon': 104.19, 'label': 'Korea chips -> China', 'category': 'chip', 'intensity': 9},
        # Wheat
        {'from_lat': 60.0, 'from_lon': 90.0, 'to_lat': 26.82, 'to_lon': 30.80, 'label': 'Russia wheat -> Egypt', 'category': 'food', 'intensity': 6},
        {'from_lat': 60.0, 'from_lon': 90.0, 'to_lat': 38.96, 'to_lon': 35.24, 'label': 'Russia wheat -> Turkiye', 'category': 'food', 'intensity': 5},
        # Iron Ore
        {'from_lat': -25.27, 'from_lon': 133.77, 'to_lat': 35.86, 'to_lon': 104.19, 'label': 'Australia iron -> China', 'category': 'ore', 'intensity': 10},
        {'from_lat': -14.23, 'from_lon': -51.92, 'to_lat': 35.86, 'to_lon': 104.19, 'label': 'Brazil iron -> China', 'category': 'ore', 'intensity': 8},
        # REE / Materials
        {'from_lat': 35.86, 'from_lon': 104.19, 'to_lat': 51.16, 'to_lon': 10.45, 'label': 'China REE -> Germany', 'category': 'material', 'intensity': 7},
        {'from_lat': 35.86, 'from_lon': 104.19, 'to_lat': 37.09, 'to_lon': -95.71, 'label': 'China REE -> USA', 'category': 'material', 'intensity': 6},
        # Cobalt
        {'from_lat': -4.04, 'from_lon': 21.75, 'to_lat': 35.86, 'to_lon': 104.19, 'label': 'DRC cobalt -> China', 'category': 'material', 'intensity': 8},
        # Soybean
        {'from_lat': -14.23, 'from_lon': -51.92, 'to_lat': 35.86, 'to_lon': 104.19, 'label': 'Brazil soy -> China', 'category': 'food', 'intensity': 9},
    ]


def _gv_sanctioned_countries():
    """Key sanctioned jurisdictions with approximate centroids."""
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
    """Critical material source countries with approximate mine locations."""
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
    """Recent geopolitical event flares (curated from Week 15 W14 incidents)."""
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
    """Current weather advisories for ports."""
    return [
        {'port': 'Houston', 'lat': 29.74, 'lon': -95.27, 'event': 'Heat advisory'},
        {'port': 'New York', 'lat': 40.67, 'lon': -74.1, 'event': 'Coastal fog'},
        {'port': 'Singapore', 'lat': 1.27, 'lon': 103.84, 'event': 'Afternoon storms'},
        {'port': 'Rotterdam', 'lat': 51.93, 'lon': 4.14, 'event': 'North Sea gale'},
        {'port': 'Savannah', 'lat': 32.08, 'lon': -81.1, 'event': 'Tropical watch'},
    ]


def _gv_country_risk_markers():
    """Country-level risk markers (top high-risk + top low-risk for context)."""
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

def _severity_color(score):
    """Return RGB tuple for severity 0-100."""
    if score >= 90: return [255, 41, 82]       # red
    if score >= 75: return [255, 122, 0]       # orange
    if score >= 55: return [255, 208, 0]       # yellow
    if score >= 30: return [127, 184, 0]       # green
    return [0, 212, 255]                        # cyan


def _category_color(cat):
    return {
        'oil': [255, 122, 0],
        'lng': [0, 212, 255],
        'chip': [200, 100, 255],
        'food': [255, 208, 0],
        'ore': [180, 150, 100],
        'material': [255, 41, 200],
    }.get(cat, [150, 150, 150])


# ---------- GLOBE HTML ----------

def _build_globe_html(layers_enabled):
    """Generate deck.gl HTML with GlobeView and selected layers."""
    # Prepare data for each layer
    chokepoints = [{'name': d['name'], 'coordinates': [d['lon'], d['lat']],
                    'score': d['score'], 'color': _severity_color(d['score']) + [220],
                    'radius': 40000 + (d['score'] * 2500), 'info': d['info']}
                   for d in _gv_chokepoints()]

    ports = [{'name': d['name'], 'coordinates': [d['lon'], d['lat']], 'rank': d['rank']}
             for d in _gv_ports()]

    arcs = [{'source': [d['from_lon'], d['from_lat']],
             'target': [d['to_lon'], d['to_lat']],
             'label': d['label'], 'category': d['category'],
             'color': _category_color(d['category']),
             'width': 1 + d['intensity'] / 3}
            for d in _gv_trade_arcs()]

    sanctions = [{'name': d['name'], 'coordinates': [d['lon'], d['lat']],
                  'severity': d['severity'],
                  'radius': 300000, 'color': [255, 41, 82, 80]}
                 for d in _gv_sanctioned_countries()]

    materials = [{'material': d['material'], 'country': d['country'],
                  'coordinates': [d['lon'], d['lat']],
                  'share': d['share'], 'size': 80000 + d['share'] * 2000}
                 for d in _gv_material_producers()]

    events = [{'event': d['event'], 'coordinates': [d['lon'], d['lat']],
               'severity': d['severity'],
               'color': _severity_color({'CRITICAL': 92, 'HIGH': 78, 'ELEVATED': 60, 'MODERATE': 45}.get(d['severity'], 50)) + [255],
               'radius': 60000 + (95 - d.get('days_ago', 5)) * 500,
               'days_ago': d['days_ago']}
              for d in _gv_gdelt_events()]

    weather = [{'port': d['port'], 'coordinates': [d['lon'], d['lat']], 'event': d['event']}
               for d in _gv_weather_advisories()]

    risk = [{'country': d['country'], 'coordinates': [d['lon'], d['lat']],
             'risk': d['risk'], 'color': _severity_color(d['risk']) + [180],
             'radius': 200000 + d['risk'] * 3000}
            for d in _gv_country_risk_markers()]

    data_json = json.dumps({
        'chokepoints': chokepoints, 'ports': ports, 'arcs': arcs,
        'sanctions': sanctions, 'materials': materials, 'events': events,
        'weather': weather, 'risk': risk
    })

    layers_json = json.dumps(layers_enabled)

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://unpkg.com/deck.gl@8.9.33/dist.min.js"></script>
<style>
  body {{ margin: 0; padding: 0; background: #0a0e17; color: #e0e8f0;
         font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}
  #container {{ position: relative; width: 100%; height: 720px; background: #0a0e17; }}
  #tooltip {{ position: absolute; pointer-events: none; z-index: 10;
              background: linear-gradient(135deg, rgba(0,25,55,0.95), rgba(0,15,35,0.95));
              border: 1px solid rgba(0,212,255,0.4); border-radius: 6px;
              padding: 10px 14px; font-size: 12px; max-width: 300px;
              box-shadow: 0 4px 20px rgba(0,212,255,0.2); display: none; }}
  #tooltip .title {{ color: #00d4ff; font-weight: 700; letter-spacing: 0.5px;
                     margin-bottom: 4px; font-size: 11px; text-transform: uppercase; }}
  #tooltip .content {{ color: #e0e8f0; line-height: 1.5; }}
  #legend {{ position: absolute; top: 12px; right: 12px; z-index: 5;
             background: rgba(0,15,35,0.85); border: 1px solid rgba(0,212,255,0.2);
             border-radius: 8px; padding: 10px 14px; font-size: 11px;
             color: #bdd2ea; max-width: 240px; }}
  #legend .item {{ display:flex; align-items:center; gap:8px; margin:4px 0; }}
  #legend .dot {{ width:10px; height:10px; border-radius:50%; flex-shrink:0; }}
</style>
</head>
<body>
<div id="container"></div>
<div id="tooltip"></div>
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
const D = {data_json};
const ENABLED = {layers_json};

function rgbaOrRgb(c) {{
  if (c.length === 3) return c.concat([200]);
  return c;
}}

const layers = [];

// Layer 1: Chokepoints (pulsing scatter)
if (ENABLED.chokepoints) {{
  layers.push(new deck.ScatterplotLayer({{
    id: 'chokepoints',
    data: D.chokepoints,
    getPosition: d => d.coordinates,
    getFillColor: d => rgbaOrRgb(d.color),
    getRadius: d => d.radius,
    radiusUnits: 'meters',
    radiusMinPixels: 5,
    radiusMaxPixels: 22,
    stroked: true,
    getLineColor: [255, 255, 255, 200],
    lineWidthMinPixels: 1,
    pickable: true
  }}));
}}

// Layer 2: Sanctioned countries (glow circles)
if (ENABLED.sanctions) {{
  layers.push(new deck.ScatterplotLayer({{
    id: 'sanctions',
    data: D.sanctions,
    getPosition: d => d.coordinates,
    getFillColor: d => d.color,
    getRadius: d => d.radius,
    radiusUnits: 'meters',
    radiusMinPixels: 12,
    radiusMaxPixels: 60,
    stroked: true,
    getLineColor: [255, 41, 82, 180],
    lineWidthMinPixels: 2,
    pickable: true
  }}));
}}

// Layer 3: Country risk markers
if (ENABLED.risk) {{
  layers.push(new deck.ScatterplotLayer({{
    id: 'risk',
    data: D.risk,
    getPosition: d => d.coordinates,
    getFillColor: d => d.color,
    getRadius: d => d.radius,
    radiusUnits: 'meters',
    radiusMinPixels: 4,
    radiusMaxPixels: 20,
    stroked: false,
    pickable: true,
    opacity: 0.6
  }}));
}}

// Layer 4: Ports (small bright dots)
if (ENABLED.ports) {{
  layers.push(new deck.ScatterplotLayer({{
    id: 'ports',
    data: D.ports,
    getPosition: d => d.coordinates,
    getFillColor: [0, 212, 255, 230],
    getRadius: 40000,
    radiusUnits: 'meters',
    radiusMinPixels: 3,
    radiusMaxPixels: 8,
    stroked: true,
    getLineColor: [0, 255, 200, 255],
    lineWidthMinPixels: 1,
    pickable: true
  }}));
}}

// Layer 5: Trade arcs
if (ENABLED.arcs) {{
  layers.push(new deck.ArcLayer({{
    id: 'trade-arcs',
    data: D.arcs,
    getSourcePosition: d => d.source,
    getTargetPosition: d => d.target,
    getSourceColor: d => d.color.concat([180]),
    getTargetColor: d => d.color.concat([220]),
    getWidth: d => d.width,
    widthMinPixels: 1,
    widthMaxPixels: 4,
    greatCircle: true,
    pickable: true
  }}));
}}

// Layer 6: Material producers (diamond markers)
if (ENABLED.materials) {{
  layers.push(new deck.ScatterplotLayer({{
    id: 'materials',
    data: D.materials,
    getPosition: d => d.coordinates,
    getFillColor: [255, 41, 200, 220],
    getRadius: d => d.size,
    radiusUnits: 'meters',
    radiusMinPixels: 4,
    radiusMaxPixels: 14,
    stroked: true,
    getLineColor: [255, 255, 255, 180],
    lineWidthMinPixels: 1,
    pickable: true
  }}));
}}

// Layer 7: GDELT events (pulsing flares)
if (ENABLED.events) {{
  layers.push(new deck.ScatterplotLayer({{
    id: 'events',
    data: D.events,
    getPosition: d => d.coordinates,
    getFillColor: d => d.color,
    getRadius: d => d.radius,
    radiusUnits: 'meters',
    radiusMinPixels: 6,
    radiusMaxPixels: 18,
    stroked: true,
    getLineColor: [255, 255, 255, 255],
    lineWidthMinPixels: 2,
    pickable: true
  }}));
}}

// Layer 8: Weather advisories
if (ENABLED.weather) {{
  layers.push(new deck.IconLayer({{
    id: 'weather',
    data: D.weather,
    getPosition: d => d.coordinates,
    getSize: 32,
    sizeScale: 1,
    getColor: [255, 255, 0, 230],
    // Using text layer fallback with triangle-like rendering via scatter
    getIcon: () => 'weather',
    iconAtlas: null,
    pickable: true
  }}));
  // Fallback: use scatter for weather since icon atlas unavailable
  layers.push(new deck.ScatterplotLayer({{
    id: 'weather-dots',
    data: D.weather,
    getPosition: d => d.coordinates,
    getFillColor: [255, 255, 0, 200],
    getRadius: 90000,
    radiusUnits: 'meters',
    radiusMinPixels: 5,
    radiusMaxPixels: 12,
    stroked: true,
    getLineColor: [255, 200, 0, 255],
    lineWidthMinPixels: 2,
    pickable: true
  }}));
}}

// Tooltip handler
function tooltipFn(info) {{
  const tt = document.getElementById('tooltip');
  if (!info || !info.object) {{ tt.style.display = 'none'; return; }}
  const o = info.object;
  let title = '', content = '';
  if (info.layer.id === 'chokepoints') {{
    title = 'CHOKEPOINT';
    content = '<b>' + o.name + '</b><br>' + o.info;
  }} else if (info.layer.id === 'ports') {{
    title = 'PORT';
    content = '<b>' + o.name + '</b><br>' + o.rank;
  }} else if (info.layer.id === 'trade-arcs') {{
    title = 'TRADE FLOW · ' + o.category.toUpperCase();
    content = o.label;
  }} else if (info.layer.id === 'sanctions') {{
    title = 'SANCTIONED';
    content = '<b>' + o.name + '</b><br>Severity: ' + o.severity + '/100';
  }} else if (info.layer.id === 'materials') {{
    title = 'CRITICAL MATERIAL';
    content = '<b>' + o.material + '</b><br>' + o.country + '<br>Global share: ' + o.share + '%';
  }} else if (info.layer.id === 'events') {{
    title = 'GEOPOLITICAL EVENT · ' + o.severity;
    content = '<b>' + o.event + '</b><br>' + o.days_ago + ' days ago';
  }} else if (info.layer.id === 'weather-dots') {{
    title = 'WEATHER ADVISORY';
    content = '<b>' + o.port + '</b><br>' + o.event;
  }} else if (info.layer.id === 'risk') {{
    title = 'COUNTRY RISK';
    content = '<b>' + o.country + '</b><br>Risk score: ' + o.risk + '/100';
  }}
  tt.innerHTML = '<div class="title">' + title + '</div><div class="content">' + content + '</div>';
  tt.style.display = 'block';
  tt.style.left = (info.x + 12) + 'px';
  tt.style.top = (info.y + 12) + 'px';
}}

const deckgl = new deck.DeckGL({{
  container: 'container',
  views: new deck.GlobeView({{id: 'globe', resolution: 10}}),
  initialViewState: {{
    longitude: 30,
    latitude: 25,
    zoom: 0.3
  }},
  controller: true,
  parameters: {{
    clearColor: [0.04, 0.055, 0.09, 1.0]
  }},
  onHover: tooltipFn,
  getTooltip: null,
  layers: [
    // Background: dark earth sphere
    new deck.SimpleMeshLayer({{
      id: 'earth-sphere',
      data: [{{position: [0, 0, 0]}}],
      getPosition: d => d.position,
      mesh: new deck.SphereGeometry({{radius: 6360000, nlat: 32, nlong: 32}}),
      getColor: [10, 20, 40, 255],
      wireframe: false,
      material: false
    }}),
    ...layers
  ]
}});
</script>
</body>
</html>
"""
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
      GDELT · <b style='color:#00d4ff;'>Rendering:</b> deck.gl GlobeView (WebGL 2.0) ·
      Trade arcs use great-circle paths · All coordinates centroid-based
    </div>
    """, unsafe_allow_html=True)
