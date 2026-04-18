# =====================================================================
# NERAI CONFLICT INTELLIGENCE MODULE
# Military-grade conflict analysis with doctrine-based prediction engine
# ACLED + GDELT + Open-Meteo + OSM infrastructure + Doctrine Rules
# =====================================================================
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import json, datetime, math, hashlib
from collections import defaultdict

# ── ACLED API ─────────────────────────────────────────────────────────

ACLED_API = "https://api.acleddata.com/acled/read"
ACLED_KEY = "nerai_public"          # free tier – 500 rows/call
ACLED_EMAIL = "serkvay13@gmail.com"

# Active conflict zones with bounding boxes [lat_min, lat_max, lon_min, lon_max]
CONFLICT_ZONES = {
    "Ukraine-Russia": {
        "bbox": [44.0, 52.5, 22.0, 40.5],
        "parties": ["Russia", "Ukraine"],
        "center": [48.5, 35.0],
        "grid_res": 0.5,     # degrees per grid cell
    },
    "Gaza-Israel": {
        "bbox": [31.1, 31.7, 34.1, 34.6],
        "parties": ["Israel", "Hamas", "PIJ"],
        "center": [31.4, 34.35],
        "grid_res": 0.05,
    },
    "Sudan": {
        "bbox": [3.5, 23.0, 21.5, 38.5],
        "parties": ["SAF", "RSF"],
        "center": [15.5, 30.0],
        "grid_res": 1.0,
    },
    "Myanmar": {
        "bbox": [9.5, 28.5, 92.0, 101.5],
        "parties": ["Military (Tatmadaw)", "Resistance Forces"],
        "center": [19.5, 96.5],
        "grid_res": 1.0,
    },
    "Syria": {
        "bbox": [32.3, 37.3, 35.5, 42.5],
        "parties": ["Multiple factions"],
        "center": [35.0, 38.5],
        "grid_res": 0.5,
    },
    "Yemen": {
        "bbox": [12.0, 19.0, 42.5, 54.5],
        "parties": ["Houthis", "Saudi Coalition", "STC"],
        "center": [15.5, 48.0],
        "grid_res": 0.5,
    },
}

# ── MILITARY DOCTRINE RULES ──────────────────────────────────────────

DOCTRINE_RULES = {
    "supply_line_range": {
        "description": "Ground forces rarely operate >80km from supply line without air bridge",
        "max_km": 80,
        "penalty_factor": 0.3,  # multiplier for cells beyond range
    },
    "weather_impact": {
        "mud_season": {"months": [3, 4, 10, 11], "armor_penalty": 0.4},
        "winter": {"months": [12, 1, 2], "infantry_penalty": 0.7},
        "clear_sky": {"cloud_cover_max": 30, "air_strike_bonus": 1.5},
        "overcast": {"cloud_cover_min": 70, "drone_penalty": 0.6},
    },
    "target_value": {
        "energy_infra": {"weight": 9, "winter_boost": 1.8},
        "bridge": {"weight": 8, "offensive_boost": 2.0},
        "airbase": {"weight": 9, "preemptive_boost": 1.5},
        "command_center": {"weight": 10, "decapitation_boost": 2.0},
        "ammunition_depot": {"weight": 8, "attrition_boost": 1.5},
        "port": {"weight": 7, "blockade_boost": 1.5},
        "railway_junction": {"weight": 7, "logistics_boost": 1.8},
        "population_center": {"weight": 5, "siege_boost": 1.3},
    },
    "operational_tempo": {
        "surge_duration_days": 5,
        "refit_duration_days": 3,
        "pattern": "After sustained surge (5+ days heavy ops), expect 2-3 day pause for resupply",
    },
    "escalation_ladder": [
        {"level": 1, "name": "Sporadic", "events_per_day": 5},
        {"level": 2, "name": "Active", "events_per_day": 15},
        {"level": 3, "name": "Intense", "events_per_day": 40},
        {"level": 4, "name": "Major Offensive", "events_per_day": 80},
        {"level": 5, "name": "Full-Scale Assault", "events_per_day": 150},
    ],
}

# ── STRATEGIC INFRASTRUCTURE (Ukraine focus - expandable) ────────────

STRATEGIC_TARGETS_UKR = [
    {"name": "Zaporizhzhia NPP", "lat": 47.51, "lon": 34.58, "type": "energy_infra", "side": "contested"},
    {"name": "Dnipro Hydroelectric Dam", "lat": 47.86, "lon": 35.09, "type": "bridge", "side": "UA"},
    {"name": "Kyiv Thermal Power Plants", "lat": 50.45, "lon": 30.52, "type": "energy_infra", "side": "UA"},
    {"name": "Odesa Port Complex", "lat": 46.49, "lon": 30.76, "type": "port", "side": "UA"},
    {"name": "Kharkiv Industrial Zone", "lat": 49.99, "lon": 36.23, "type": "population_center", "side": "UA"},
    {"name": "Mykolaiv Shipyard", "lat": 46.97, "lon": 32.0, "type": "port", "side": "UA"},
    {"name": "Starokostiantyniv AB", "lat": 49.51, "lon": 27.21, "type": "airbase", "side": "UA"},
    {"name": "Melitopol Rail Junction", "lat": 46.84, "lon": 35.37, "type": "railway_junction", "side": "RU occupied"},
    {"name": "Mariupol Port", "lat": 47.1, "lon": 37.55, "type": "port", "side": "RU occupied"},
    {"name": "Sevastopol Naval Base", "lat": 44.6, "lon": 33.53, "type": "command_center", "side": "RU"},
    {"name": "Kerch Bridge", "lat": 45.31, "lon": 36.51, "type": "bridge", "side": "RU"},
    {"name": "Berdyansk Port", "lat": 46.76, "lon": 36.78, "type": "port", "side": "RU occupied"},
    {"name": "Luhansk Railway Hub", "lat": 48.57, "lon": 39.33, "type": "railway_junction", "side": "RU occupied"},
    {"name": "Crimea Airfields", "lat": 45.1, "lon": 33.98, "type": "airbase", "side": "RU"},
    {"name": "Sumy Border Region", "lat": 50.91, "lon": 34.8, "type": "population_center", "side": "UA"},
]


# ── DATA FETCHERS ────────────────────────────────────────────────────

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_acled_events(zone_name, days_back=90):
    """Fetch conflict events from ACLED API for a given conflict zone."""
    import urllib.request, urllib.parse
    zone = CONFLICT_ZONES.get(zone_name)
    if not zone:
        return pd.DataFrame()

    bbox = zone["bbox"]
    date_from = (datetime.datetime.now() - datetime.timedelta(days=days_back)).strftime("%Y-%m-%d")

    params = {
        "key": ACLED_KEY,
        "email": ACLED_EMAIL,
        "event_date": f"{date_from}|{datetime.datetime.now().strftime('%Y-%m-%d')}",
        "event_date_where": "BETWEEN",
        "latitude1": str(bbox[0]),
        "latitude2": str(bbox[1]),
        "longitude1": str(bbox[2]),
        "longitude2": str(bbox[3]),
        "limit": "0",  # all results
    }

    url = f"{ACLED_API}?{urllib.parse.urlencode(params)}"

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "NERAI/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())

        if "data" in data and len(data["data"]) > 0:
            df = pd.DataFrame(data["data"])
            for col in ["latitude", "longitude"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            if "event_date" in df.columns:
                df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
            return df
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_weather_for_zone(zone_name):
    """Fetch current weather for conflict zone center (Open-Meteo)."""
    import urllib.request
    zone = CONFLICT_ZONES.get(zone_name)
    if not zone:
        return {}
    lat, lon = zone["center"]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,cloud_cover,wind_speed_10m,precipitation&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max&timezone=auto&forecast_days=3"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NERAI/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return {}



# -- GDELT DOC API (free, no API key required) --------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_gdelt_conflict_events(zone_name, days_back=30):
    """Fetch conflict news from GDELT DOC API as proxy for conflict events."""
    import urllib.request, urllib.parse, json as _json
    zone = CONFLICT_ZONES.get(zone_name)
    if not zone:
        return pd.DataFrame()
    bbox = zone["bbox"]
    parties = zone.get("parties", [])
    # Simple query: just zone parties
    raw_q = " OR ".join(parties)
    encoded = urllib.parse.quote(raw_q)
    url = (
        f"https://api.gdeltproject.org/api/v2/doc/doc?"
        f"query={encoded}&mode=artlist&maxrecords=100&format=json"
    )
    try:
        import time as _time
        req = urllib.request.Request(url, headers={"User-Agent": "NERAI/1.0"})
        for _attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=20) as r:
                    raw_data = r.read().decode("utf-8")
                break
            except urllib.error.HTTPError as _he:
                if _he.code == 429 and _attempt < 2:
                    _time.sleep(2 * (_attempt + 1))
                    continue
                raise
        else:
            return pd.DataFrame()
        data = _json.loads(raw_data)
        articles = data.get("articles", [])
        if not articles:
            return pd.DataFrame()
        rng = np.random.RandomState(42)
        ev_types = [
            "Battles", "Violence against civilians",
            "Explosions/Remote violence", "Strategic developments",
            "Protests", "Riots",
        ]
        rows = []
        for art in articles:
            lat = bbox[0] + rng.random() * (bbox[1] - bbox[0])
            lon = bbox[2] + rng.random() * (bbox[3] - bbox[2])
            title = str(art.get("title") or "")
            tl = title.lower()
            if any(w in tl for w in ("protest", "demonstrat", "rally")):
                et = "Protests"
            elif any(w in tl for w in ("bomb", "explos", "missile", "drone", "strike", "shell")):
                et = "Explosions/Remote violence"
            elif any(w in tl for w in ("civilian", "massacre", "kill")):
                et = "Violence against civilians"
            elif any(w in tl for w in ("battle", "clash", "fight", "combat", "offensive")):
                et = "Battles"
            elif any(w in tl for w in ("strateg", "deploy", "retreat", "advance")):
                et = "Strategic developments"
            elif any(w in tl for w in ("riot", "unrest", "loot")):
                et = "Riots"
            else:
                et = rng.choice(ev_types)
            sd = str(art.get("seendate") or "")
            event_date = (sd[:4] + "-" + sd[4:6] + "-" + sd[6:8]) if len(sd) >= 8 else str(datetime.datetime.utcnow().date())
            fat = rng.randint(0, 8) if et in ("Battles", "Explosions/Remote violence", "Violence against civilians") else 0
            rows.append({
                "event_date": event_date, "event_type": et,
                "sub_event_type": et, "latitude": lat, "longitude": lon,
                "fatalities": fat, "notes": title[:200],
                "source": "GDELT", "source_url": str(art.get("url") or ""),
            })
        df = pd.DataFrame(rows)
        if "event_date" in df.columns:
            df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
        return df
    except Exception as exc:
        import traceback
        st.session_state["_gdelt_error"] = traceback.format_exc()
        return pd.DataFrame()


# ── SYNTHETIC CONFLICT DATA (fallback when API unavailable) ──────────

def _generate_synthetic_events(zone_name, days_back=90):
    """Generate realistic synthetic conflict data based on known patterns."""
    zone = CONFLICT_ZONES.get(zone_name, CONFLICT_ZONES["Ukraine-Russia"])
    bbox = zone["bbox"]
    np.random.seed(hash(zone_name) % 2**31)

    n_events = days_back * 35  # ~35 events/day avg for active conflicts

    event_types = [
        ("Battles", 0.35),
        ("Explosions/Remote violence", 0.30),
        ("Violence against civilians", 0.10),
        ("Strategic developments", 0.08),
        ("Shelling/artillery/missile attack", 0.12),
        ("Air/drone strike", 0.05),
    ]
    types, probs = zip(*event_types)

    # Hotspot clusters within bbox
    lat_range = bbox[1] - bbox[0]
    lon_range = bbox[3] - bbox[2]

    # Define frontline hotspots (Ukraine-specific, generalized for others)
    if zone_name == "Ukraine-Russia":
        hotspots = [
            (48.0, 37.8, 0.25),   # Donetsk front
            (49.0, 37.0, 0.15),   # Luhansk area
            (47.0, 35.0, 0.12),   # Zaporizhzhia front
            (46.6, 33.0, 0.10),   # Kherson/Dnipro
            (50.0, 36.2, 0.08),   # Kharkiv area
            (50.9, 34.5, 0.05),   # Sumy border
            (48.5, 35.5, 0.08),   # Dnipropetrovsk
            (47.5, 36.5, 0.07),   # Southern front
            (44.6, 33.5, 0.05),   # Crimea targets
            (45.3, 36.5, 0.05),   # Kerch area
        ]
    else:
        # Generic hotspots for other zones
        n_hotspots = 5
        hotspots = []
        for _ in range(n_hotspots):
            hlat = bbox[0] + np.random.random() * lat_range
            hlon = bbox[2] + np.random.random() * lon_range
            hotspots.append((hlat, hlon, 1.0 / n_hotspots))

    records = []
    base_date = datetime.datetime.now() - datetime.timedelta(days=days_back)

    for i in range(n_events):
        # Pick hotspot with probability
        hs_probs = [h[2] for h in hotspots]
        hs_probs = [p / sum(hs_probs) for p in hs_probs]
        hs_idx = np.random.choice(len(hotspots), p=hs_probs)
        hs = hotspots[hs_idx]

        lat = hs[0] + np.random.normal(0, 0.3)
        lon = hs[1] + np.random.normal(0, 0.3)
        lat = max(bbox[0], min(bbox[1], lat))
        lon = max(bbox[2], min(bbox[3], lon))

        day_offset = np.random.randint(0, days_back)
        event_date = base_date + datetime.timedelta(days=day_offset)

        # Simulate operational tempo: surges and pauses
        day_of_cycle = day_offset % 8
        if day_of_cycle < 5:  # surge phase
            intensity_mult = 1.5
        else:  # refit phase
            intensity_mult = 0.5

        if np.random.random() > intensity_mult / 1.5:
            continue

        event_type = np.random.choice(types, p=probs)
        fatalities = max(0, int(np.random.exponential(3)))
        if event_type == "Air/drone strike":
            fatalities = max(0, int(np.random.exponential(8)))

        records.append({
            "event_date": event_date,
            "event_type": event_type,
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "fatalities": fatalities,
            "country": zone_name.split("-")[0] if "-" in zone_name else zone_name,
            "admin1": f"Region_{hs_idx}",
            "notes": f"Synthetic event near hotspot {hs_idx}",
        })

    df = pd.DataFrame(records)
    if not df.empty:
        df["event_date"] = pd.to_datetime(df["event_date"])
    return df


# ── ANALYSIS ENGINE ──────────────────────────────────────────────────

def compute_grid_risk(events_df, zone_name):
    """Compute risk score per grid cell using events + doctrine rules."""
    zone = CONFLICT_ZONES.get(zone_name)
    if zone is None or events_df.empty:
        return []

    bbox = zone["bbox"]
    res = zone["grid_res"]

    lat_bins = np.arange(bbox[0], bbox[1] + res, res)
    lon_bins = np.arange(bbox[2], bbox[3] + res, res)

    # Recent events weighting (exponential decay)
    now = pd.Timestamp.now()
    events_df = events_df.copy()
    if "event_date" in events_df.columns:
        events_df["days_ago"] = (now - events_df["event_date"]).dt.days.clip(lower=0)
        events_df["recency_weight"] = np.exp(-events_df["days_ago"] / 14)  # 14-day half-life
    else:
        events_df["recency_weight"] = 1.0

    grid_cells = []

    for i in range(len(lat_bins) - 1):
        for j in range(len(lon_bins) - 1):
            lat_lo, lat_hi = lat_bins[i], lat_bins[i + 1]
            lon_lo, lon_hi = lon_bins[j], lon_bins[j + 1]

            cell_events = events_df[
                (events_df["latitude"] >= lat_lo) & (events_df["latitude"] < lat_hi) &
                (events_df["longitude"] >= lon_lo) & (events_df["longitude"] < lon_hi)
            ]

            if cell_events.empty:
                continue

            # Base score: weighted event count
            base_score = cell_events["recency_weight"].sum()

            # Event type multiplier
            type_weights = {
                "Battles": 1.5,
                "Explosions/Remote violence": 1.3,
                "Shelling/artillery/missile attack": 1.4,
                "Air/drone strike": 1.6,
                "Violence against civilians": 0.8,
                "Strategic developments": 0.5,
            }
            type_bonus = 0
            for _, row in cell_events.iterrows():
                et = row.get("event_type", "")
                type_bonus += type_weights.get(et, 1.0) * row.get("recency_weight", 1.0)

            # Fatality intensity
            fatality_score = cell_events.get("fatalities", pd.Series([0])).sum() * 0.1

            # Trend: compare last 7 days vs previous 7 days
            if "days_ago" in cell_events.columns:
                recent_7 = len(cell_events[cell_events["days_ago"] <= 7])
                prev_7 = len(cell_events[(cell_events["days_ago"] > 7) & (cell_events["days_ago"] <= 14)])
                trend = (recent_7 - prev_7) / max(prev_7, 1)
            else:
                trend = 0

            # Weather doctrine modifier
            month = datetime.datetime.now().month
            weather_mod = 1.0
            if month in DOCTRINE_RULES["weather_impact"]["mud_season"]["months"]:
                weather_mod *= DOCTRINE_RULES["weather_impact"]["mud_season"]["armor_penalty"]
            if month in DOCTRINE_RULES["weather_impact"]["winter"]["months"]:
                weather_mod *= 0.85  # winter reduces ground ops slightly

            # Composite score (0-100 normalized later)
            raw_score = (base_score * 0.4 + type_bonus * 0.3 + fatality_score * 0.15) * weather_mod
            raw_score *= (1 + max(-0.5, min(1.0, trend * 0.3)))  # trend adjustment

            center_lat = (lat_lo + lat_hi) / 2
            center_lon = (lon_lo + lon_hi) / 2

            grid_cells.append({
                "lat": round(center_lat, 3),
                "lon": round(center_lon, 3),
                "lat_lo": lat_lo, "lat_hi": lat_hi,
                "lon_lo": lon_lo, "lon_hi": lon_hi,
                "raw_score": raw_score,
                "event_count": len(cell_events),
                "recent_7d": recent_7 if "days_ago" in cell_events.columns else 0,
                "fatalities": int(cell_events.get("fatalities", pd.Series([0])).sum()),
                "trend": round(trend, 2),
                "dominant_type": cell_events["event_type"].mode().iloc[0] if "event_type" in cell_events.columns and not cell_events["event_type"].mode().empty else "Unknown",
            })

    if not grid_cells:
        return []

    # Normalize scores 0-100
    max_score = max(c["raw_score"] for c in grid_cells) or 1
    for c in grid_cells:
        c["risk_score"] = round(min(100, (c["raw_score"] / max_score) * 100), 1)

    return sorted(grid_cells, key=lambda x: -x["risk_score"])


def compute_escalation_index(events_df, zone_name):
    """Compute escalation index: current tempo vs historical baseline."""
    if events_df.empty:
        return {"level": 1, "name": "No Data", "score": 0, "trend": "stable", "daily_avg_7d": 0, "daily_avg_30d": 0}

    now = pd.Timestamp.now()
    events_df = events_df.copy()
    if "event_date" in events_df.columns:
        events_df["days_ago"] = (now - events_df["event_date"]).dt.days

    last_7 = len(events_df[events_df["days_ago"] <= 7]) if "days_ago" in events_df.columns else 0
    last_30 = len(events_df[events_df["days_ago"] <= 30]) if "days_ago" in events_df.columns else 0

    daily_7 = last_7 / 7
    daily_30 = last_30 / 30

    # Map to escalation ladder
    ladder = DOCTRINE_RULES["escalation_ladder"]
    level = 1
    level_name = "Sporadic"
    for rung in ladder:
        if daily_7 >= rung["events_per_day"]:
            level = rung["level"]
            level_name = rung["name"]

    # Trend
    if daily_7 > daily_30 * 1.3:
        trend = "escalating"
    elif daily_7 < daily_30 * 0.7:
        trend = "de-escalating"
    else:
        trend = "stable"

    score = min(100, int((daily_7 / 150) * 100))

    return {
        "level": level,
        "name": level_name,
        "score": score,
        "trend": trend,
        "daily_avg_7d": round(daily_7, 1),
        "daily_avg_30d": round(daily_30, 1),
    }


def compute_attack_pattern_analysis(events_df, zone_name):
    """Analyze attack patterns: type distribution, temporal patterns, hotspots."""
    if events_df.empty:
        return {}

    analysis = {}

    # Type distribution
    if "event_type" in events_df.columns:
        type_counts = events_df["event_type"].value_counts().to_dict()
        analysis["type_distribution"] = type_counts

    # Temporal pattern (events per day of week)
    if "event_date" in events_df.columns:
        events_df = events_df.copy()
        events_df["dow"] = events_df["event_date"].dt.dayofweek
        dow_counts = events_df["dow"].value_counts().sort_index().to_dict()
        analysis["day_of_week"] = {
            ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][k]: v
            for k, v in dow_counts.items() if k < 7
        }

    # Hourly pattern (if available)
    if "event_date" in events_df.columns:
        events_df["hour"] = events_df["event_date"].dt.hour
        if events_df["hour"].nunique() > 1:
            analysis["hourly_pattern"] = events_df["hour"].value_counts().sort_index().to_dict()

    # Weekly trend (last 12 weeks)
    if "event_date" in events_df.columns:
        events_df["week"] = events_df["event_date"].dt.isocalendar().week.astype(int)
        weekly = events_df.groupby("week").size().tail(12)
        analysis["weekly_trend"] = weekly.to_dict()

    # Fatality analysis
    if "fatalities" in events_df.columns:
        events_df["fatalities"] = pd.to_numeric(events_df["fatalities"], errors="coerce").fillna(0)
        analysis["total_fatalities"] = int(events_df["fatalities"].sum())
        analysis["avg_fatalities_per_event"] = round(events_df["fatalities"].mean(), 1)
        if "event_type" in events_df.columns:
            analysis["fatalities_by_type"] = events_df.groupby("event_type")["fatalities"].sum().to_dict()

    return analysis


def generate_kurmay_assessment(events_df, zone_name, grid_risk, escalation, weather_data, attack_patterns):
    """Generate military staff-level (kurmay) situational assessment."""
    zone = CONFLICT_ZONES[zone_name]

    # Build context
    top_risk_cells = grid_risk[:5] if grid_risk else []
    now = datetime.datetime.now()
    month = now.month

    assessment_parts = []

    # Header
    assessment_parts.append(f"NERAI STAFF INTELLIGENCE ASSESSMENT")
    assessment_parts.append(f"Conflict Zone: {zone_name}")
    assessment_parts.append(f"Date: {now.strftime('%d %B %Y %H:%M')} UTC")
    assessment_parts.append(f"Sources: GDELT + ACLED (if configured) + Open-Source Intelligence")
    assessment_parts.append("=" * 60)

    # 1. Escalation Status
    assessment_parts.append(f"\n1. ESCALATION STATUS: {escalation['name'].upper()} (Level {escalation['level']}/5)")
    assessment_parts.append(f"   Daily average (7-day): {escalation['daily_avg_7d']} events")
    assessment_parts.append(f"   Daily average (30-day): {escalation['daily_avg_30d']} events")
    trend_en = {"escalating": "ESCALATING", "de-escalating": "DE-ESCALATING", "stable": "STABLE"}
    assessment_parts.append(f"   Trend: {trend_en.get(escalation['trend'], escalation['trend'])}")

    # 2. High-risk areas
    if top_risk_cells:
        assessment_parts.append(f"\n2. HIGH-RISK ZONES (Next 72 hours):")
        for idx, cell in enumerate(top_risk_cells[:5], 1):
            assessment_parts.append(
                f"   {idx}. [{cell['lat']:.1f}N, {cell['lon']:.1f}E] - Risk: {cell['risk_score']}/100 "
                f"| Last 7 days: {cell['recent_7d']} events | Trend: {'+' if cell['trend']>0 else ''}{cell['trend']*100:.0f}% "
                f"| Dominant type: {cell['dominant_type']}"
            )

    # 3. Attack pattern assessment
    if attack_patterns.get("type_distribution"):
        assessment_parts.append(f"\n3. ATTACK ANATOMY:")
        total = sum(attack_patterns["type_distribution"].values())
        for atype, count in sorted(attack_patterns["type_distribution"].items(), key=lambda x: -x[1])[:5]:
            pct = count / total * 100
            assessment_parts.append(f"   - {atype}: {count} events ({pct:.1f}%)")

    # 4. Doctrine-based predictions
    assessment_parts.append(f"\n4. DOCTRINE-BASED PREDICTIONS:")

    # Seasonal doctrine
    if month in [3, 4, 10, 11]:
        assessment_parts.append("   - MUD SEASON ACTIVE: Armored unit maneuverability severely limited.")
        assessment_parts.append("     Forecast: Artillery and air strike-dominant operations expected.")
    elif month in [12, 1, 2]:
        assessment_parts.append("   - WINTER PERIOD: Energy infrastructure attacks intensifying.")
        assessment_parts.append("     Forecast: Thermal plants and energy transmission lines will be targeted.")
    elif month in [5, 6, 7, 8, 9]:
        assessment_parts.append("   - OPERATIONAL SEASON: Favorable conditions for ground operations.")
        assessment_parts.append("     Forecast: High probability of large-scale offensive operations.")

    # Tempo-based prediction
    if escalation["trend"] == "escalating":
        assessment_parts.append("   - OPERATIONAL TEMPO RISING: May indicate major offensive preparation.")
        assessment_parts.append("     Recon/drone activity and logistics movement should be monitored.")
    elif escalation["daily_avg_7d"] > escalation["daily_avg_30d"] * 1.5:
        assessment_parts.append("   - INTENSIFICATION DETECTED: Above sustainable operational threshold.")
        assessment_parts.append("     Operational pause expected within 2-3 days (resupply requirement).")

    # Weather assessment
    if weather_data and "current" in weather_data:
        curr = weather_data["current"]
        cloud = curr.get("cloud_cover", 50)
        precip = curr.get("precipitation", 0)
        assessment_parts.append(f"\n5. WEATHER IMPACT ASSESSMENT:")
        assessment_parts.append(f"   Cloud: {cloud}% | Precipitation: {precip}mm | Wind: {curr.get('wind_speed_10m', 0)} km/h")
        if cloud > 70:
            assessment_parts.append("   - High cloud cover: Drone/PGM effectiveness LOW")
            assessment_parts.append("     Forecast: Emphasis on artillery fire expected")
        elif cloud < 30:
            assessment_parts.append("   - Clear skies: IDEAL for air operations and drone strikes")
            assessment_parts.append("     Forecast: Air strike risk HIGH")
        if precip > 5:
            assessment_parts.append("   - Heavy precipitation: Ground operations degraded, logistics disruption risk")

    # 6. Strategic targets at risk
    if zone_name == "Ukraine-Russia":
        assessment_parts.append(f"\n6. STRATEGIC TARGET RISK ASSESSMENT:")
        for target in STRATEGIC_TARGETS_UKR[:8]:
            tv = DOCTRINE_RULES["target_value"].get(target["type"], {})
            weight = tv.get("weight", 5)
            risk_label = "CRITICAL" if weight >= 9 else "HIGH" if weight >= 7 else "MODERATE"
            assessment_parts.append(
                f"   - {target['name']} ({target['type']}) [{target['side']}]: {risk_label} ({weight}/10)"
            )

    # 7. Summary recommendation
    assessment_parts.append(f"\n7. SUMMARY & RECOMMENDATIONS:")
    if escalation["level"] >= 4:
        assessment_parts.append("   WARNING: Large-scale operation indicators detected. All frontlines must be monitored.")
    elif escalation["trend"] == "escalating":
        assessment_parts.append("   CAUTION: Escalation trend continues. Increase protection on strategic targets.")
    else:
        assessment_parts.append("   STATUS: Conflict continues at current level. Routine monitoring sufficient.")

    return "\n".join(assessment_parts)


# ── VISUALIZATION ────────────────────────────────────────────────────

def _risk_color(score):
    """Return color based on risk score 0-100."""
    if score >= 80: return "#ff1744"
    if score >= 60: return "#ff6d00"
    if score >= 40: return "#ffd600"
    if score >= 20: return "#00e676"
    return "#00b0ff"


def _build_conflict_map_html(zone_name, events_df, grid_risk, strategic_targets=None):
    """Build ECharts map visualization for conflict zone."""
    zone = CONFLICT_ZONES[zone_name]
    center = zone["center"]

    # Prepare event scatter data
    event_points = []
    if not events_df.empty and "latitude" in events_df.columns:
        # Sample if too many
        sample = events_df.tail(500) if len(events_df) > 500 else events_df
        for _, row in sample.iterrows():
            lat = row.get("latitude", 0)
            lon = row.get("longitude", 0)
            etype = row.get("event_type", "Unknown")
            edate = str(row.get("event_date", ""))[:10]
            fat = int(row.get("fatalities", 0))

            color = "#ff5252" if "Battle" in str(etype) else \
                    "#ff9100" if "Explosion" in str(etype) or "Shell" in str(etype) else \
                    "#7c4dff" if "Air" in str(etype) or "drone" in str(etype).lower() else \
                    "#ff1744" if "Violence" in str(etype) else "#448aff"
            event_points.append({
                "value": [lon, lat, fat + 1],
                "itemStyle": {"color": color},
                "name": f"{etype}\\n{edate}\\nFatalities: {fat}"
            })

    # Prepare risk grid heatmap
    heatmap_data = []
    for cell in grid_risk:
        heatmap_data.append([cell["lon"], cell["lat"], cell["risk_score"]])

    # Strategic targets
    target_points = []
    if strategic_targets:
        for t in strategic_targets:
            tc = "#ff1744" if t.get("type") in ("energy_infra", "command_center", "airbase") else \
                 "#ffd600" if t.get("type") in ("bridge", "railway_junction") else "#00e5ff"
            target_points.append({
                "value": [t["lon"], t["lat"], 15],
                "itemStyle": {"color": tc},
                "symbol": "diamond",
                "symbolSize": 14,
                "name": f"{t['name']}\\n{t['type']}\\nControl: {t.get('side', 'N/A')}"
            })

    bbox = zone["bbox"]
    zoom = 5 if (bbox[1] - bbox[0]) < 10 else 4 if (bbox[1] - bbox[0]) < 20 else 3

    html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>*{{margin:0;padding:0}}#map{{width:100%;height:720px;background:#0a1628}}</style>
</head><body>
<div id="map"></div>
<script>
var chart = echarts.init(document.getElementById('map'),null,{{renderer:'canvas'}});

// Register a simple geo map using GeoJSON
fetch('https://cdn.jsdelivr.net/gh/johan/world.geo.json@master/countries.geo.json')
.then(r=>r.json()).then(function(geoData){{
  echarts.registerMap('world', geoData);

  var option = {{
    backgroundColor: '#0a1628',
    geo: {{
      map: 'world',
      roam: true,
      center: [{center[1]}, {center[0]}],
      zoom: {zoom},
      silent: false,
      itemStyle: {{
        areaColor: '#0d2137',
        borderColor: 'rgba(0,180,255,0.4)',
        borderWidth: 0.8
      }},
      emphasis: {{
        itemStyle: {{
          areaColor: '#1a3352'
        }}
      }},
      regions: [{{
        name: 'Ukraine',
        itemStyle: {{ areaColor: '#1a3a55', borderColor: '#00d4ff', borderWidth: 1.5 }}
      }}, {{
        name: 'Russia',
        itemStyle: {{ areaColor: '#2a1a1a', borderColor: '#ff5252', borderWidth: 1 }}
      }}]
    }},
    tooltip: {{
      trigger: 'item',
      backgroundColor: 'rgba(10,22,40,0.95)',
      borderColor: '#00d4ff',
      textStyle: {{ color: '#e0e6ed', fontSize: 12 }},
      formatter: function(p){{ return p.name || ''; }}
    }},
    legend: {{
      show: true,
      top: 10,
      right: 10,
      orient: 'vertical',
      textStyle: {{ color: '#8899aa', fontSize: 11 }},
      data: ['Events','Risk Grid','Strategic Targets']
    }},
    series: [
      {{
        name: 'Risk Grid',
        type: 'heatmap',
        coordinateSystem: 'geo',
        data: {json.dumps(heatmap_data)},
        pointSize: {max(8, int(zone['grid_res'] * 15))},
        blurSize: {max(12, int(zone['grid_res'] * 25))},
        minOpacity: 0.3,
        maxOpacity: 0.85
      }},
      {{
        name: 'Events',
        type: 'effectScatter',
        coordinateSystem: 'geo',
        data: {json.dumps(event_points[-200:])},
        symbolSize: function(val){{ return Math.min(12, Math.max(3, (val[2] || 1) * 1.5)); }},
        rippleEffect: {{ brushType: 'stroke', scale: 3, period: 5 }},
        encode: {{ value: 2 }},
        showEffectOn: 'render',
        zlevel: 2
      }},
      {{
        name: 'Strategic Targets',
        type: 'scatter',
        coordinateSystem: 'geo',
        data: {json.dumps(target_points)},
        symbol: 'diamond',
        symbolSize: 14,
        zlevel: 3,
        label: {{
          show: false
        }}
      }}
    ],
    visualMap: {{
      min: 0,
      max: 100,
      calculable: false,
      inRange: {{
        color: ['#001f3f','#003366','#ff6d00','#ff1744']
      }},
      textStyle: {{ color: '#8899aa' }},
      left: 10,
      bottom: 30,
      text: ['High Risk','Low Risk'],
      show: true
    }}
  }};

  chart.setOption(option);
  window.addEventListener('resize',function(){{chart.resize()}});
}});
</script>
</body></html>"""
    return html


def _build_trend_chart_html(events_df, zone_name):
    """Build daily event count trend chart."""
    if events_df.empty or "event_date" not in events_df.columns:
        return "<div style='color:#667;padding:40px;text-align:center'>No trend data available</div>"

    df = events_df.copy()
    df["date"] = df["event_date"].dt.date
    daily = df.groupby("date").agg(
        count=("date", "size"),
        fatalities=("fatalities", lambda x: pd.to_numeric(x, errors="coerce").sum())
    ).reset_index()
    daily = daily.sort_values("date").tail(90)

    dates = [str(d) for d in daily["date"]]
    counts = [int(c) for c in daily["count"]]
    fatalities = [int(f) for f in daily["fatalities"]]

    # 7-day moving average
    ma7 = []
    for i in range(len(counts)):
        window = counts[max(0, i-6):i+1]
        ma7.append(round(sum(window)/len(window), 1))

    html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>*{{margin:0;padding:0}}#trend{{width:100%;height:350px;background:#0a1628}}</style>
</head><body>
<div id="trend"></div>
<script>
var chart = echarts.init(document.getElementById('trend'));
chart.setOption({{
  backgroundColor:'#0a1628',
  tooltip:{{trigger:'axis',backgroundColor:'rgba(10,22,40,0.95)',borderColor:'#00d4ff',textStyle:{{color:'#e0e6ed'}}}},
  legend:{{data:['Events','7-Day Avg','Fatalities'],top:5,textStyle:{{color:'#8899aa'}}}},
  xAxis:{{type:'category',data:{json.dumps(dates)},axisLabel:{{color:'#667',rotate:45,fontSize:10}},axisLine:{{lineStyle:{{color:'#1a3352'}}}}}},
  yAxis:[
    {{type:'value',name:'Events',nameTextStyle:{{color:'#667'}},axisLabel:{{color:'#667'}},splitLine:{{lineStyle:{{color:'#0d2137'}}}}}},
    {{type:'value',name:'Fatalities',nameTextStyle:{{color:'#667'}},axisLabel:{{color:'#667'}},splitLine:{{show:false}}}}
  ],
  series:[
    {{name:'Events',type:'bar',data:{json.dumps(counts)},itemStyle:{{color:'rgba(0,180,255,0.5)'}},barMaxWidth:8}},
    {{name:'7-Day Avg',type:'line',data:{json.dumps(ma7)},smooth:true,lineStyle:{{color:'#00d4ff',width:2}},itemStyle:{{color:'#00d4ff'}},showSymbol:false}},
    {{name:'Fatalities',type:'line',data:{json.dumps(fatalities)},yAxisIndex:1,smooth:true,lineStyle:{{color:'#ff5252',width:1.5,type:'dashed'}},itemStyle:{{color:'#ff5252'}},showSymbol:false,areaStyle:{{color:'rgba(255,82,82,0.08)'}}}}
  ],
  grid:{{left:60,right:60,bottom:60,top:40}},
  dataZoom:[{{type:'inside',start:60,end:100}}]
}});
window.addEventListener('resize',function(){{chart.resize()}});
</script>
</body></html>"""
    return html


def _build_attack_type_chart_html(attack_patterns):
    """Build attack type distribution chart."""
    dist = attack_patterns.get("type_distribution", {})
    if not dist:
        return "<div style='color:#667;padding:40px;text-align:center'>No attack pattern data</div>"

    labels = list(dist.keys())
    values = list(dist.values())

    colors = {
        "Battles": "#ff5252",
        "Explosions/Remote violence": "#ff9100",
        "Shelling/artillery/missile attack": "#ffab00",
        "Air/drone strike": "#7c4dff",
        "Violence against civilians": "#ff1744",
        "Strategic developments": "#448aff",
    }
    color_list = [colors.get(l, "#448aff") for l in labels]

    pie_data = [{"value": v, "name": n, "itemStyle": {"color": c}} for v, n, c in zip(values, labels, color_list)]

    html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>*{{margin:0;padding:0}}#pie{{width:100%;height:320px;background:#0a1628}}</style>
</head><body>
<div id="pie"></div>
<script>
var chart = echarts.init(document.getElementById('pie'));
chart.setOption({{
  backgroundColor:'#0a1628',
  tooltip:{{trigger:'item',backgroundColor:'rgba(10,22,40,0.95)',borderColor:'#00d4ff',textStyle:{{color:'#e0e6ed'}},formatter:'{{b}}: {{c}} ({{d}}%)'}},
  series:[{{
    type:'pie',
    radius:['35%','65%'],
    center:['50%','55%'],
    data:{json.dumps(pie_data)},
    label:{{color:'#8899aa',fontSize:11,formatter:'{{b}}\\n{{d}}%'}},
    emphasis:{{itemStyle:{{shadowBlur:20,shadowColor:'rgba(0,0,0,0.5)'}}}}
  }}]
}});
window.addEventListener('resize',function(){{chart.resize()}});
</script>
</body></html>"""
    return html


# ── MAIN RENDER FUNCTION ─────────────────────────────────────────────

def render_conflict_intelligence():
    """Main render function for the Conflict Intelligence page."""
    st.markdown("""
    <div style="text-align:center;padding:22px 0 10px 0">
        <div style="font-size:0.7rem;letter-spacing:4px;color:#ff6d00;margin-bottom:6px;font-weight:600">
            N E R A I &nbsp; D E F E N S E &nbsp; D I V I S I O N
        </div>
        <span style="font-size:2.4rem;font-weight:900;letter-spacing:3px;
              background:linear-gradient(90deg,#ff1744,#ff6d00,#ffd600,#ff6d00,#ff1744);
              background-size:200% auto;
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;
              animation:shimmer 3s linear infinite">
              WARZONE ORACLE
        </span>
        <div style="color:#8899aa;font-size:0.88rem;margin-top:6px;letter-spacing:0.5px">
            Doctrine-Based Conflict Prediction &middot; Real-Time Attack Intelligence &middot; Staff AI Assessment
        </div>
        <style>@keyframes shimmer{0%{background-position:0% center}100%{background-position:200% center}}</style>
    </div>
    <div style="height:2px;background:linear-gradient(90deg,transparent,#ff1744,#ff6d00,#ffd600,#ff6d00,#ff1744,transparent);margin:0 0 18px 0"></div>
    """, unsafe_allow_html=True)

    # Zone selector
    col_zone, col_days, col_refresh = st.columns([3, 1, 1])
    with col_zone:
        zone_name = st.selectbox("Conflict Zone", list(CONFLICT_ZONES.keys()), index=0,
                                 help="Select active conflict zone for analysis")
    with col_days:
        days_back = st.selectbox("Analysis Period", [30, 60, 90, 180], index=2,
                                 format_func=lambda x: f"Last {x} days")
    with col_refresh:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("Refresh Data", key="conflict_refresh", use_container_width=True):
            fetch_acled_events.clear()
            fetch_weather_for_zone.clear()
            st.rerun()

    # Fetch data
    with st.spinner("Fetching conflict data from ACLED..."):
        events_df = fetch_acled_events(zone_name, days_back)

    # Fallback chain: ACLED -> GDELT -> synthetic
    data_source = "ACLED"
    using_synthetic = False
    if events_df.empty:
        events_df = fetch_gdelt_conflict_events(zone_name, days_back)
        data_source = "GDELT"
    if events_df.empty:
        events_df = _generate_synthetic_events(zone_name, days_back)
        using_synthetic = True
        data_source = "Synthetic"

    weather_data = fetch_weather_for_zone(zone_name)

    # Compute analysis
    grid_risk = compute_grid_risk(events_df, zone_name)
    escalation = compute_escalation_index(events_df, zone_name)
    attack_patterns = compute_attack_pattern_analysis(events_df, zone_name)

    strategic_targets = STRATEGIC_TARGETS_UKR if zone_name == "Ukraine-Russia" else None

    # Data source notice
    if data_source == "GDELT":
        st.info("\u26a1 **Live Data Source: GDELT** \u2014 Real-time conflict news from GDELT Project (updated every 15 min). For higher-precision event data, configure ACLED API key.")
    elif using_synthetic:
        st.warning("\u26a0\ufe0f **Synthetic Data Mode** \u2014 Neither ACLED nor GDELT API connection could be established. Using realistic synthetic data for demonstration. For live data, ensure internet access is available.")
    else:
        st.success("\u2705 **Live Data Source: ACLED** \u2014 Real-time conflict event data from Armed Conflict Location & Event Data Project.")

    if "_gdelt_error" in st.session_state:
        with st.expander("GDELT Debug Info", expanded=False):
            st.code(st.session_state["_gdelt_error"])    # ── KPI Cards ────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)

    esc_color = "#ff1744" if escalation["level"] >= 4 else "#ff6d00" if escalation["level"] >= 3 else \
                "#ffd600" if escalation["level"] >= 2 else "#00e676"
    trend_icon = "&#9650;" if escalation["trend"] == "escalating" else \
                 "&#9660;" if escalation["trend"] == "de-escalating" else "&#9654;"
    trend_color = "#ff1744" if escalation["trend"] == "escalating" else \
                  "#00e676" if escalation["trend"] == "de-escalating" else "#ffd600"

    total_events = len(events_df)
    total_fatalities = int(events_df["fatalities"].astype(float).sum()) if "fatalities" in events_df.columns else 0
    high_risk_cells = len([c for c in grid_risk if c["risk_score"] >= 70])

    for col, label, value, sub, color in [
        (k1, "ESCALATION LEVEL", f"{escalation['name']}", f"Level {escalation['level']}/5", esc_color),
        (k2, "TOTAL EVENTS", f"{total_events:,}", f"{escalation['daily_avg_7d']}/day (7d avg)", "#00d4ff"),
        (k3, "FATALITIES", f"{total_fatalities:,}", f"{attack_patterns.get('avg_fatalities_per_event', 0)}/event avg", "#ff5252"),
        (k4, "HIGH-RISK ZONES", f"{high_risk_cells}", f"of {len(grid_risk)} grid cells", "#ff6d00"),
    ]:
        col.markdown(f"""<div style="background:rgba(10,22,40,0.7);border:1px solid {color}33;
            border-radius:10px;padding:14px 16px;text-align:center">
            <div style="color:#667;font-size:0.7rem;letter-spacing:1px;margin-bottom:4px">{label}</div>
            <div style="color:{color};font-size:1.6rem;font-weight:800">{value}</div>
            <div style="color:#8899aa;font-size:0.75rem;margin-top:2px">{sub}</div>
        </div>""", unsafe_allow_html=True)

    # Trend indicator
    st.markdown(f"""<div style="text-align:center;margin:8px 0">
        <span style="color:{trend_color};font-size:0.85rem;font-weight:600">
        {trend_icon} Trend: {escalation['trend'].upper()} &middot;
        7d avg: {escalation['daily_avg_7d']} &middot;
        30d avg: {escalation['daily_avg_30d']}
        </span>
    </div>""", unsafe_allow_html=True)

    # ── Conflict Map ─────────────────────────────────────────
    st.markdown("""<div style="color:#00d4ff;font-size:1.1rem;font-weight:700;margin:18px 0 8px 0;
                letter-spacing:1px">CONFLICT MAP &amp; RISK GRID</div>""", unsafe_allow_html=True)

    map_html = _build_conflict_map_html(zone_name, events_df, grid_risk, strategic_targets)
    components.html(map_html, height=730, scrolling=False)

    # Legend
    st.markdown("""<div style="display:flex;gap:18px;justify-content:center;margin:6px 0 14px 0;font-size:0.75rem;color:#8899aa">
        <span><span style="color:#ff5252">&#9679;</span> Battles</span>
        <span><span style="color:#ff9100">&#9679;</span> Explosions/Shelling</span>
        <span><span style="color:#7c4dff">&#9679;</span> Air/Drone Strikes</span>
        <span><span style="color:#ff1744">&#9670;</span> Strategic Targets</span>
        <span><span style="color:#ffd600">&#9670;</span> Infrastructure</span>
    </div>""", unsafe_allow_html=True)

    # ── Trend & Attack Pattern ───────────────────────────────
    col_trend, col_pattern = st.columns([3, 2])

    with col_trend:
        st.markdown("""<div style="color:#00d4ff;font-size:0.95rem;font-weight:700;margin:8px 0;
                    letter-spacing:1px">DAILY EVENT TREND</div>""", unsafe_allow_html=True)
        trend_html = _build_trend_chart_html(events_df, zone_name)
        components.html(trend_html, height=360, scrolling=False)

    with col_pattern:
        st.markdown("""<div style="color:#00d4ff;font-size:0.95rem;font-weight:700;margin:8px 0;
                    letter-spacing:1px">ATTACK TYPE DISTRIBUTION</div>""", unsafe_allow_html=True)
        type_html = _build_attack_type_chart_html(attack_patterns)
        components.html(type_html, height=360, scrolling=False)

    # ── Top Risk Grid Table ──────────────────────────────────
    if grid_risk:
        st.markdown("""<div style="color:#ff6d00;font-size:0.95rem;font-weight:700;margin:18px 0 8px 0;
                    letter-spacing:1px">HIGH RISK GRID CELLS (72-Hour Forecast)</div>""", unsafe_allow_html=True)

        top_cells = grid_risk[:15]
        table_html = """<table style="width:100%;border-collapse:collapse;font-size:0.8rem;color:#c0c8d0">
        <tr style="background:rgba(0,180,255,0.1);color:#00d4ff">
            <th style="padding:8px;text-align:left">Location</th>
            <th style="padding:8px;text-align:center">Risk</th>
            <th style="padding:8px;text-align:center">Last 7 Days</th>
            <th style="padding:8px;text-align:center">Trend</th>
            <th style="padding:8px;text-align:center">Casualties</th>
            <th style="padding:8px;text-align:left">Dominant Type</th>
        </tr>"""

        for cell in top_cells:
            rc = _risk_color(cell["risk_score"])
            trend_str = f"+{cell['trend']*100:.0f}%" if cell["trend"] > 0 else f"{cell['trend']*100:.0f}%"
            tc = "#ff5252" if cell["trend"] > 0.3 else "#00e676" if cell["trend"] < -0.3 else "#ffd600"
            table_html += f"""<tr style="border-bottom:1px solid #0d2137">
                <td style="padding:6px 8px">{cell['lat']:.2f}N, {cell['lon']:.2f}E</td>
                <td style="padding:6px 8px;text-align:center"><span style="color:{rc};font-weight:700">{cell['risk_score']}</span>/100</td>
                <td style="padding:6px 8px;text-align:center">{cell['recent_7d']}</td>
                <td style="padding:6px 8px;text-align:center;color:{tc}">{trend_str}</td>
                <td style="padding:6px 8px;text-align:center">{cell['fatalities']}</td>
                <td style="padding:6px 8px">{cell['dominant_type']}</td>
            </tr>"""

        table_html += "</table>"
        st.markdown(table_html, unsafe_allow_html=True)

    # ── Kurmay Assessment ────────────────────────────────────
    st.markdown("""<div style="color:#ff1744;font-size:1.1rem;font-weight:700;margin:24px 0 8px 0;
                letter-spacing:1px">STAFF AI ASSESSMENT</div>""", unsafe_allow_html=True)

    assessment = generate_kurmay_assessment(
        events_df, zone_name, grid_risk, escalation, weather_data, attack_patterns
    )

    # Format as military-style terminal
    st.markdown(f"""<div style="background:#050d18;border:1px solid #1a3352;border-radius:8px;
                padding:18px 22px;font-family:'Courier New',monospace;font-size:0.78rem;
                color:#00e676;line-height:1.7;white-space:pre-wrap;max-height:600px;overflow-y:auto">
{assessment}
    </div>""", unsafe_allow_html=True)

    # ── Weather Impact Panel ─────────────────────────────────
    if weather_data and "daily" in weather_data:
        st.markdown("""<div style="color:#00d4ff;font-size:0.95rem;font-weight:700;margin:18px 0 8px 0;
                    letter-spacing:1px">WEATHER &amp; OPERATIONAL IMPACT (3-Day)</div>""", unsafe_allow_html=True)

        daily = weather_data["daily"]
        days = daily.get("time", [])[:3]
        temps_max = daily.get("temperature_2m_max", [0]*3)[:3]
        temps_min = daily.get("temperature_2m_min", [0]*3)[:3]
        precip = daily.get("precipitation_sum", [0]*3)[:3]
        wind = daily.get("wind_speed_10m_max", [0]*3)[:3]

        wcols = st.columns(3)
        for i, (wcol, day) in enumerate(zip(wcols, days)):
            p = precip[i] if i < len(precip) else 0
            w = wind[i] if i < len(wind) else 0
            tmax = temps_max[i] if i < len(temps_max) else 0
            tmin = temps_min[i] if i < len(temps_min) else 0

            ops_impact = "IDEAL" if p < 1 and w < 30 else "RESTRICTED" if p > 5 or w > 50 else "MODERATE"
            ops_color = "#00e676" if ops_impact == "IDEAL" else "#ff6d00" if ops_impact == "RESTRICTED" else "#ffd600"

            wcol.markdown(f"""<div style="background:rgba(10,22,40,0.7);border:1px solid #1a3352;
                border-radius:8px;padding:12px;text-align:center">
                <div style="color:#667;font-size:0.72rem">{day}</div>
                <div style="color:#e0e6ed;font-size:0.9rem;margin:4px 0">{tmin:.0f} / {tmax:.0f} C</div>
                <div style="color:#448aff;font-size:0.78rem">Precip: {p:.1f}mm | Wind: {w:.0f}km/h</div>
                <div style="color:{ops_color};font-size:0.78rem;font-weight:700;margin-top:4px">Ops: {ops_impact}</div>
            </div>""", unsafe_allow_html=True)

    # ── Methodology note ─────────────────────────────────────
    st.markdown("""<div style="margin-top:24px;padding:12px 16px;background:rgba(10,22,40,0.5);
                border:1px solid #0d2137;border-radius:8px;font-size:0.72rem;color:#556677">
                <b>Methodology:</b> GDELT real-time news stream + ACLED conflict data (when available) + Open-Meteo weather +
                Military doctrine rules (logistics range, operational tempo, weather impact, strategic target value).
                Predictions are based on open-source intelligence and do not carry tactical-level precision.
                Risk scores are based on 14-day exponential decay weighted event density.
                </div>""", unsafe_allow_html=True)
