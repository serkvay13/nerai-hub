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

# ââ ACLED API âââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

ACLED_API = "https://api.acleddata.com/acled/read"
ACLED_KEY = "nerai_public"          # free tier â 500 rows/call
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

# ââ MILITARY DOCTRINE RULES ââââââââââââââââââââââââââââââââââââââââââ

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

# ââ STRATEGIC INFRASTRUCTURE (Ukraine focus - expandable) ââââââââââââ

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


# ââ DATA FETCHERS ââââââââââââââââââââââââââââââââââââââââââââââââââââ

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


# ââ SYNTHETIC CONFLICT DATA (fallback when API unavailable) ââââââââââ

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


# ââ ANALYSIS ENGINE ââââââââââââââââââââââââââââââââââââââââââââââââââ

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


def _analyze_front_sectors(events_df, zone_name):
    """Divide conflict zone into operational sectors and analyze each front."""
    zone = CONFLICT_ZONES[zone_name]
    bbox = zone["bbox"]
    sectors = {}

    if zone_name == "Ukraine-Russia":
        sector_defs = {
            "DONETSK FRONT": {"lat": (47.5, 49.0), "lon": (37.0, 38.5)},
            "LUHANSK FRONT": {"lat": (48.5, 49.5), "lon": (38.0, 40.0)},
            "ZAPORIZHZHIA AXIS": {"lat": (46.5, 47.8), "lon": (34.0, 36.5)},
            "KHERSON-DNIPRO LINE": {"lat": (46.0, 47.0), "lon": (32.0, 34.5)},
            "KHARKIV SECTOR": {"lat": (49.5, 51.0), "lon": (35.5, 37.0)},
            "SUMY BORDER ZONE": {"lat": (50.5, 52.0), "lon": (33.5, 35.5)},
            "CRIMEA-BLACK SEA": {"lat": (44.0, 46.0), "lon": (32.5, 36.5)},
        }
    elif zone_name == "Gaza-Israel":
        sector_defs = {
            "NORTHERN GAZA": {"lat": (31.45, 31.60), "lon": (34.35, 34.55)},
            "GAZA CITY": {"lat": (31.40, 31.52), "lon": (34.38, 34.50)},
            "CENTRAL CORRIDOR": {"lat": (31.30, 31.42), "lon": (34.30, 34.45)},
            "KHAN YOUNIS SECTOR": {"lat": (31.20, 31.35), "lon": (34.25, 34.40)},
            "RAFAH AXIS": {"lat": (31.10, 31.25), "lon": (34.15, 34.35)},
        }
    elif zone_name == "Sudan":
        sector_defs = {
            "KHARTOUM FRONT": {"lat": (15.0, 16.5), "lon": (31.5, 33.5)},
            "DARFUR WEST": {"lat": (12.0, 15.0), "lon": (22.0, 25.5)},
            "KORDOFAN AXIS": {"lat": (11.0, 14.0), "lon": (28.0, 32.0)},
            "EASTERN CORRIDOR": {"lat": (14.0, 19.0), "lon": (33.5, 37.0)},
        }
    elif zone_name == "Myanmar":
        sector_defs = {
            "SHAN STATE": {"lat": (19.5, 24.0), "lon": (96.0, 101.0)},
            "SAGAING REGION": {"lat": (21.0, 25.0), "lon": (94.0, 96.5)},
            "CHIN STATE": {"lat": (20.5, 23.0), "lon": (92.5, 94.5)},
            "RAKHINE FRONT": {"lat": (18.0, 21.5), "lon": (92.0, 94.5)},
            "KARENNI-KAYAH": {"lat": (18.5, 20.5), "lon": (96.5, 98.5)},
        }
    else:
        # Generic quadrant split for other zones
        mid_lat = (bbox[0] + bbox[1]) / 2
        mid_lon = (bbox[2] + bbox[3]) / 2
        sector_defs = {
            "NORTH SECTOR": {"lat": (mid_lat, bbox[1]), "lon": (bbox[2], bbox[3])},
            "SOUTH SECTOR": {"lat": (bbox[0], mid_lat), "lon": (bbox[2], bbox[3])},
            "EAST FLANK": {"lat": (bbox[0], bbox[1]), "lon": (mid_lon, bbox[3])},
            "WEST FLANK": {"lat": (bbox[0], bbox[1]), "lon": (bbox[2], mid_lon)},
        }

    now = pd.Timestamp.now()
    for name, bounds in sector_defs.items():
        mask = (
            (events_df["latitude"] >= bounds["lat"][0]) &
            (events_df["latitude"] <= bounds["lat"][1]) &
            (events_df["longitude"] >= bounds["lon"][0]) &
            (events_df["longitude"] <= bounds["lon"][1])
        )
        sec_df = events_df[mask]
        if sec_df.empty:
            sectors[name] = {"total": 0, "last_7d": 0, "last_3d": 0, "trend": 0,
                             "dominant_type": "N/A", "fatalities": 0, "intensity": "DORMANT"}
            continue

        if "event_date" in sec_df.columns and "days_ago" not in sec_df.columns:
            sec_df = sec_df.copy()
            sec_df["days_ago"] = (now - sec_df["event_date"]).dt.days.clip(lower=0)

        last_7d = len(sec_df[sec_df["days_ago"] <= 7]) if "days_ago" in sec_df.columns else 0
        last_3d = len(sec_df[sec_df["days_ago"] <= 3]) if "days_ago" in sec_df.columns else 0
        prev_7d = len(sec_df[(sec_df["days_ago"] > 7) & (sec_df["days_ago"] <= 14)]) if "days_ago" in sec_df.columns else 0
        trend = (last_7d - prev_7d) / max(prev_7d, 1)

        fat = int(sec_df["fatalities"].astype(float).sum()) if "fatalities" in sec_df.columns else 0
        dom_type = sec_df["event_type"].mode().iloc[0] if "event_type" in sec_df.columns and not sec_df["event_type"].mode().empty else "Unknown"

        daily_rate = last_7d / 7
        if daily_rate >= 20:
            intensity = "CRITICAL"
        elif daily_rate >= 10:
            intensity = "HIGH"
        elif daily_rate >= 3:
            intensity = "ACTIVE"
        elif daily_rate >= 1:
            intensity = "LOW"
        else:
            intensity = "DORMANT"

        # Attack type breakdown for this sector
        type_dist = {}
        if "event_type" in sec_df.columns:
            recent = sec_df[sec_df["days_ago"] <= 7] if "days_ago" in sec_df.columns else sec_df
            type_dist = recent["event_type"].value_counts().to_dict()

        sectors[name] = {
            "total": len(sec_df), "last_7d": last_7d, "last_3d": last_3d,
            "prev_7d": prev_7d, "trend": round(trend, 2),
            "dominant_type": dom_type, "fatalities": fat,
            "intensity": intensity, "daily_rate": round(daily_rate, 1),
            "type_dist": type_dist,
        }

    return sectors


def _detect_operational_patterns(events_df, attack_patterns):
    """Detect tactical patterns: surge-pause cycles, coordinated strikes, shift indicators."""
    patterns = {"surge_detected": False, "pause_likely": False, "coordination_level": "LOW",
                "shift_indicators": [], "tempo_assessment": ""}

    if events_df.empty or "event_date" not in events_df.columns:
        return patterns

    now = pd.Timestamp.now()
    df = events_df.copy()
    df["days_ago"] = (now - df["event_date"]).dt.days.clip(lower=0)

    # Daily event counts for last 30 days
    daily = df[df["days_ago"] <= 30].groupby(df["event_date"].dt.date).size()
    if len(daily) < 3:
        return patterns

    mean_daily = daily.mean()
    std_daily = daily.std() if len(daily) > 1 else 0

    # Detect surge: last 3 days above 1.5 sigma
    last_3_days = daily.tail(3)
    surge_threshold = mean_daily + 1.5 * std_daily
    if len(last_3_days) >= 2 and last_3_days.mean() > surge_threshold:
        patterns["surge_detected"] = True
        patterns["surge_days"] = len(last_3_days[last_3_days > surge_threshold])

    # Detect operational pause indicators
    # If there was a 5+ day surge, doctrine says pause coming
    consecutive_high = 0
    for val in daily.tail(10).values:
        if val > mean_daily * 1.3:
            consecutive_high += 1
        else:
            consecutive_high = 0
    if consecutive_high >= 5:
        patterns["pause_likely"] = True
        patterns["pause_reason"] = f"{consecutive_high}-day sustained surge exceeds logistic resupply cycle"

    # Coordination assessment: multiple attack types in same time window = coordinated
    if attack_patterns.get("type_distribution"):
        dist = attack_patterns["type_distribution"]
        if isinstance(dist, pd.Series):
            dist = dist.to_dict()
        active_types = sum(1 for v in dist.values() if v > 0)
        if active_types >= 4:
            patterns["coordination_level"] = "HIGH"
        elif active_types >= 3:
            patterns["coordination_level"] = "MODERATE"

    # Tempo assessment
    ratio_7_30 = 0
    last_7 = len(df[df["days_ago"] <= 7])
    last_30 = len(df[df["days_ago"] <= 30])
    if last_30 > 0:
        ratio_7_30 = (last_7 / 7) / (last_30 / 30) if last_30 > 0 else 1

    if ratio_7_30 > 1.5:
        patterns["tempo_assessment"] = "ACCELERATING"
    elif ratio_7_30 > 1.2:
        patterns["tempo_assessment"] = "INCREASING"
    elif ratio_7_30 < 0.6:
        patterns["tempo_assessment"] = "DECELERATING"
    elif ratio_7_30 < 0.8:
        patterns["tempo_assessment"] = "DECREASING"
    else:
        patterns["tempo_assessment"] = "STEADY"

    return patterns


def _compute_target_threat_matrix(zone_name, grid_risk, escalation, weather_data, month):
    """Cross-reference strategic targets with nearby grid risk to compute dynamic threat scores."""
    if zone_name != "Ukraine-Russia":
        return []

    threats = []
    for target in STRATEGIC_TARGETS_UKR:
        base_weight = DOCTRINE_RULES["target_value"].get(target["type"], {}).get("weight", 5)

        # Proximity risk: check if any high-risk grid cell is within ~50km
        proximity_risk = 0
        nearest_risk = 0
        if grid_risk:
            for cell in grid_risk[:20]:
                dist = math.sqrt((cell["lat"] - target["lat"])**2 + (cell["lon"] - target["lon"])**2) * 111  # approx km
                if dist < 80:
                    cell_contrib = cell["risk_score"] * max(0, (80 - dist) / 80)
                    proximity_risk = max(proximity_risk, cell_contrib)
                    if cell_contrib > nearest_risk:
                        nearest_risk = cell_contrib

        # Seasonal modifier
        seasonal_boost = 1.0
        ttype = target["type"]
        if month in [12, 1, 2] and ttype == "energy_infra":
            seasonal_boost = DOCTRINE_RULES["target_value"].get(ttype, {}).get("winter_boost", 1.0)
        if escalation["trend"] == "escalating":
            if ttype == "bridge":
                seasonal_boost *= DOCTRINE_RULES["target_value"].get(ttype, {}).get("offensive_boost", 1.0)
            if ttype == "ammunition_depot":
                seasonal_boost *= DOCTRINE_RULES["target_value"].get(ttype, {}).get("attrition_boost", 1.0)

        # Weather modifier for air-targetable assets
        weather_mod = 1.0
        if weather_data and "current" in weather_data:
            cloud = weather_data["current"].get("cloud_cover", 50)
            if cloud < 30 and ttype in ("energy_infra", "airbase", "command_center", "bridge"):
                weather_mod = 1.3  # clear sky = higher PGM/drone threat
            elif cloud > 70:
                weather_mod = 0.7  # overcast reduces precision strike risk

        composite = (base_weight * 5 + proximity_risk * 0.3) * seasonal_boost * weather_mod
        composite = min(100, composite)

        threat_level = "CRITICAL" if composite >= 60 else "HIGH" if composite >= 40 else "ELEVATED" if composite >= 25 else "MODERATE"

        threats.append({
            "name": target["name"], "type": target["type"], "side": target.get("side", "N/A"),
            "base_weight": base_weight, "proximity_risk": round(proximity_risk, 1),
            "seasonal_boost": round(seasonal_boost, 2), "weather_mod": round(weather_mod, 2),
            "composite": round(composite, 1), "threat_level": threat_level,
            "lat": target["lat"], "lon": target["lon"],
        })

    return sorted(threats, key=lambda x: -x["composite"])


def generate_kurmay_assessment(events_df, zone_name, grid_risk, escalation, weather_data, attack_patterns):
    """
    Generate military staff-level (kurmay) situational assessment.
    IPB Framework + METT-TC + Cross-front correlation + Actor intent analysis.
    Derives all conclusions from actual event data.
    """
    zone = CONFLICT_ZONES[zone_name]
    now = datetime.datetime.now()
    month = now.month
    parties = zone.get("parties", [])

    # Compute deep analytics
    sectors = _analyze_front_sectors(events_df, zone_name)
    op_patterns = _detect_operational_patterns(events_df, attack_patterns)
    target_threats = _compute_target_threat_matrix(zone_name, grid_risk, escalation, weather_data, month)

    # Prepare event data metrics
    total_events = len(events_df)
    total_fat = int(events_df["fatalities"].astype(float).sum()) if "fatalities" in events_df.columns else 0
    top_risk_cells = grid_risk[:5] if isinstance(grid_risk, list) and grid_risk else []

    # Type distribution
    type_dist = attack_patterns.get("type_distribution", {})
    if hasattr(type_dist, "to_dict"):
        type_dist = type_dist.to_dict()
    total_typed = sum(type_dist.values()) if type_dist else 1

    # Weekly trend data
    weekly_trend = attack_patterns.get("weekly_trend", {})
    weekly_vals = list(weekly_trend.values()) if weekly_trend else []
    week_trend_direction = ""
    if len(weekly_vals) >= 4:
        first_half = sum(weekly_vals[:len(weekly_vals)//2]) / max(len(weekly_vals)//2, 1)
        second_half = sum(weekly_vals[len(weekly_vals)//2:]) / max(len(weekly_vals) - len(weekly_vals)//2, 1)
        if second_half > first_half * 1.3:
            week_trend_direction = "UPWARD"
        elif second_half < first_half * 0.7:
            week_trend_direction = "DOWNWARD"
        else:
            week_trend_direction = "LATERAL"

    # Find most/least active sectors
    active_sectors = sorted(
        [(k, v) for k, v in sectors.items() if v["total"] > 0],
        key=lambda x: -x[1]["last_7d"]
    )
    hottest_sector = active_sectors[0] if active_sectors else None
    shifting_sectors = [s for s in active_sectors if s[1]["trend"] > 0.5 and s[1]["last_7d"] >= 3]
    cooling_sectors = [s for s in active_sectors if s[1]["trend"] < -0.3 and s[1]["prev_7d"] >= 5]

    # NATO threat level
    if escalation["level"] >= 4:
        nato_level = "CRITICAL"
    elif escalation["level"] >= 3:
        nato_level = "SUBSTANTIAL"
    elif escalation["level"] >= 2:
        nato_level = "MODERATE"
    else:
        nato_level = "LOW"

    # FPCON
    if escalation["level"] >= 5:
        fpcon = "DELTA"
    elif escalation["level"] >= 4:
        fpcon = "CHARLIE"
    elif escalation["level"] >= 3:
        fpcon = "BRAVO"
    elif escalation["level"] >= 2:
        fpcon = "ALPHA"
    else:
        fpcon = "NORMAL"

    a = []  # assessment lines

    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    # HEADER
    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    a.append("=" * 64)
    a.append("  NERAI STAFF INTELLIGENCE ASSESSMENT")
    a.append("  IPB FRAMEWORK | METT-TC METHODOLOGY")
    a.append("=" * 64)
    a.append(f"DTG      : {now.strftime('%d%H%MZ %b %Y').upper()}")
    a.append(f"AOR      : {zone_name}")
    a.append(f"PARTIES  : {' vs '.join(parties)}")
    a.append(f"CLASS    : NATO THREAT LEVEL {nato_level} | FPCON {fpcon}")
    a.append(f"SOURCES  : GDELT OSINT + Open-Meteo + Doctrine Engine")
    a.append(f"PERIOD   : {total_events} events analyzed | {total_fat} total fatalities")
    a.append("-" * 64)

    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    # 1. SITUATION (METT-TC: Mission, Enemy, Terrain, Troops, Time, Civilians)
    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    a.append("")
    a.append("1. SITUATION â GENERAL ASSESSMENT")
    a.append("=" * 64)

    # Escalation assessment with context
    a.append(f"   CONTACT LEVEL   : {escalation['name'].upper()} (Tier {escalation['level']}/5)")
    a.append(f"   7-DAY AVG       : {escalation['daily_avg_7d']} events/day")
    a.append(f"   30-DAY AVG      : {escalation['daily_avg_30d']} events/day")

    trend_map = {"escalating": "ESCALATING", "de-escalating": "DE-ESCALATING", "stable": "STABLE"}
    a.append(f"   OVERALL TREND   : {trend_map.get(escalation['trend'], escalation['trend'])}")
    a.append(f"   TEMPO           : {op_patterns['tempo_assessment']}")
    a.append(f"   COORDINATION    : {op_patterns['coordination_level']}")

    # Operational interpretation
    if escalation["daily_avg_7d"] > escalation["daily_avg_30d"] * 1.5:
        a.append("")
        a.append("   >> WARNING: 7-day average exceeds 1.5x the 30-day baseline.")
        a.append("      This rate is logistically unsustainable.")
        a.append("      Per doctrine, operational pause expected within 48-72 hours")
        a.append("      (resupply, ammunition replenishment, personnel rotation).")
    elif escalation["trend"] == "escalating":
        a.append("")
        a.append("   >> Operational tempo shows upward trend. Two scenarios possible:")
        a.append("      (a) Major offensive preparation underway")
        a.append("      (b) Pressure escalation to force adversary into negotiations.")

    if op_patterns["surge_detected"]:
        a.append("")
        a.append("   ** SURGE DETECTED: Event density over last 3 days exceeds")
        a.append("      1.5 sigma above statistical mean. Indicator of coordinated ops.")

    if op_patterns["pause_likely"]:
        a.append(f"   ** PAUSE FORECAST: {op_patterns.get('pause_reason', 'Post-sustained surge')}")

    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    # 2. ENEMY FORCES â SECTOR-BASED FORCE ANALYSIS
    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    a.append("")
    a.append("2. SECTOR-BASED FORCE ANALYSIS â FRONT INTELLIGENCE")
    a.append("=" * 64)

    for sec_name, sec_data in sorted(sectors.items(), key=lambda x: -x[1]["last_7d"]):
        if sec_data["total"] == 0:
            continue

        trend_arrow = "+" if sec_data["trend"] > 0 else ""
        a.append(f"")
        a.append(f"   [{sec_data['intensity']}] {sec_name}")
        a.append(f"   {'~' * 50}")
        a.append(f"   Last 7 days: {sec_data['last_7d']} events | Last 3 days: {sec_data['last_3d']} events")
        a.append(f"   Weekly change: {trend_arrow}{sec_data['trend']*100:.0f}% | Casualties: {sec_data['fatalities']}")
        a.append(f"   Dominant attack type: {sec_data['dominant_type']}")

        # Sector-specific intelligence assessment
        if sec_data["intensity"] == "CRITICAL":
            a.append(f"   >> MAIN LINE OF CONTACT: This sector is currently the most intense combat zone.")
            a.append(f"      Daily rate of {sec_data['daily_rate']} events indicates active offensive operations.")
        elif sec_data["intensity"] == "HIGH" and sec_data["trend"] > 0.3:
            a.append(f"   >> RISING THREAT: Event increase rate at significant levels.")
            a.append(f"      Force redeployment or new operation initiation probable.")

        # Attack type interpretation per sector
        if sec_data.get("type_dist"):
            dist = sec_data["type_dist"]
            total_sec = sum(dist.values()) or 1
            art_shell = sum(v for k, v in dist.items() if "Shell" in k or "Explosion" in k or "Remote" in k)
            battle = sum(v for k, v in dist.items() if "Battle" in k)
            air_drone = sum(v for k, v in dist.items() if "Air" in k or "drone" in k.lower())

            if art_shell / total_sec > 0.5:
                a.append(f"   >> ARTILLERY DOMINANCE: {art_shell/total_sec*100:.0f}% of events are artillery/missile.")
                a.append(f"      Indicates attrition strategy. Aimed at frontline suppression and defense degradation.")
            elif battle / total_sec > 0.4:
                a.append(f"   >> COMBAT INTENSITY: {battle/total_sec*100:.0f}% of events are direct engagements.")
                a.append(f"      Terrain seizure/hold-focused active offensive operations underway.")
            if air_drone / total_sec > 0.15:
                a.append(f"   >> AIR THREAT: {air_drone/total_sec*100:.0f}% of events are air/UAV-originated.")
                a.append(f"      Deep strike operations targeting logistics lines and rear assets.")

    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    # 3. CROSS-FRONT CORRELATION
    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    a.append("")
    a.append("3. CROSS-FRONT CORRELATION & MANEUVER INTELLIGENCE")
    a.append("=" * 64)

    if shifting_sectors:
        a.append("   SECTORS WITH INCREASING ACTIVITY:")
        for sec_name, sec_data in shifting_sectors:
            a.append(f"   >> {sec_name}: +{sec_data['trend']*100:.0f}% weekly increase")
        a.append("")
        a.append("   ASSESSMENT: Upward-trending sectors may indicate force")
        a.append("   redeployment or opening of a new operational axis.")
        a.append("   If this increase coincides with decline in other sectors,")
        a.append("   it signals a deliberate shift of the center of gravity.")

    if cooling_sectors:
        a.append("")
        a.append("   SECTORS WITH DECLINING ACTIVITY:")
        for sec_name, sec_data in cooling_sectors:
            a.append(f"   >> {sec_name}: {sec_data['trend']*100:.0f}% weekly decline")
        a.append("")
        a.append("   ASSESSMENT: Activity decline can be interpreted two ways:")
        a.append("   (a) Tactical objectives achieved, consolidation phase")
        a.append("   (b) Forces being redeployed to another front")

    if shifting_sectors and cooling_sectors:
        shift_names = [s[0] for s in shifting_sectors]
        cool_names = [s[0] for s in cooling_sectors]
        a.append("")
        a.append("   ** CRITICAL CORRELATION DETECTED **")
        a.append(f"   Decline in {', '.join(cool_names)} sectors,")
        a.append(f"   concurrent increase in {', '.join(shift_names)} sectors detected.")
        a.append("   This pattern is a FORCE REDEPLOYMENT INDICATOR.")
        a.append("   Monitor logistics route changes and new staging areas.")

    if not shifting_sectors and not cooling_sectors:
        if hottest_sector:
            a.append(f"   Most active sector: {hottest_sector[0]} ({hottest_sector[1]['last_7d']} events/7d)")
        a.append("   No significant cross-front shifting indicators DETECTED.")
        a.append("   Positional warfare continues along current frontlines.")

    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    # 4. ATTACK ANATOMY â ACTOR INTENT ANALYSIS
    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    a.append("")
    a.append("4. ATTACK ANATOMY & ACTOR INTENT ASSESSMENT")
    a.append("=" * 64)

    if type_dist:
        a.append("   ATTACK TYPE DISTRIBUTION:")
        for atype, count in sorted(type_dist.items(), key=lambda x: -x[1])[:6]:
            pct = count / total_typed * 100
            bar = "#" * int(pct / 3)
            a.append(f"   {bar} {atype}: {count} ({pct:.1f}%)")

        # Strategic interpretation
        a.append("")
        a.append("   ACTOR INTENT ASSESSMENT:")

        shell_pct = sum(v for k, v in type_dist.items() if "Shell" in k or "Explosion" in k or "Remote" in k) / total_typed * 100
        battle_pct = sum(v for k, v in type_dist.items() if "Battle" in k) / total_typed * 100
        air_pct = sum(v for k, v in type_dist.items() if "Air" in k or "drone" in k.lower()) / total_typed * 100
        civ_pct = sum(v for k, v in type_dist.items() if "civilian" in k.lower()) / total_typed * 100

        if shell_pct > 40:
            a.append(f"   - Artillery/missile strikes dominant at {shell_pct:.0f}%.")
            a.append("     INTENT: Attrition strategy. Degrading enemy frontline defenses,")
            a.append("     destroying defensive positions, pre-assault preparation.")
            if battle_pct > 20:
                a.append("     Artillery fire followed by infantry assault pattern observed.")
                a.append("     Consistent with CLASSIC COMBINED ARMS OFFENSIVE DOCTRINE.")

        if battle_pct > 35:
            a.append(f"   - Direct engagements at {battle_pct:.0f}%.")
            a.append("     INTENT: Terrain seizure/expansion operations.")
            a.append("     Active frontline movement and position changes expected.")

        if air_pct > 10:
            a.append(f"   - Air/UAV strikes at {air_pct:.0f}%.")
            a.append("     INTENT: Deep strike operations. Targeting logistics lines,")
            a.append("     command centers, and critical infrastructure.")

        if civ_pct > 10:
            a.append(f"   - Civilian-targeted events at {civ_pct:.0f}%.")
            a.append("     INTENT: Psychological pressure and population displacement strategy.")

    # Day-of-week pattern
    dow_data = attack_patterns.get("day_of_week", {})
    if dow_data:
        peak_day = max(dow_data, key=dow_data.get) if dow_data else None
        min_day = min(dow_data, key=dow_data.get) if dow_data else None
        if peak_day and min_day:
            a.append("")
            a.append(f"   TEMPORAL PATTERN: Peak day {peak_day}, lowest {min_day}.")
            ratio = dow_data[peak_day] / max(dow_data[min_day], 1)
            if ratio > 2:
                a.append(f"   Peak/trough ratio {ratio:.1f}x â distinct operational rhythm detected.")
                a.append(f"   Elevated readiness measures should be prioritized for {peak_day}.")

    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    # 5. TERRAIN & WEATHER â METT-TC
    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    a.append("")
    a.append("5. TERRAIN & WEATHER IMPACT ASSESSMENT")
    a.append("=" * 64)

    # Seasonal doctrine
    if month in [3, 4, 10, 11]:
        a.append("   SEASON     : RASPUTITSA (Mud season)")
        a.append("   IMPACT     : Armored unit maneuverability SEVERELY RESTRICTED.")
        a.append("   RESULT     : Artillery and air assets gain increased importance. Armored")
        a.append("                elements confined to paved roads and hardened terrain.")
        a.append("   FORECAST   : Artillery/UAV-dominant operations, infantry infiltration.")
    elif month in [12, 1, 2]:
        a.append("   SEASON     : WINTER PERIOD")
        a.append("   IMPACT     : Energy infrastructure attacks gain STRATEGIC PRIORITY.")
        a.append("   RESULT     : Heating infrastructure, power plants, and energy transmission")
        a.append("                lines become primary target set.")
        a.append("   FORECAST   : Long-range strikes on civilian infrastructure expected to increase.")
    elif month in [5, 6, 7, 8, 9]:
        a.append("   SEASON     : OPERATIONAL SEASON")
        a.append("   IMPACT     : Terrain conditions FAVORABLE for armored maneuver.")
        a.append("   RESULT     : Window open for large-scale ground operations.")
        a.append("   FORECAST   : Offensive operations, armored advances, frontline shifts.")

    if weather_data and "current" in weather_data:
        curr = weather_data["current"]
        cloud = curr.get("cloud_cover", 50)
        precip = curr.get("precipitation", 0)
        wind = curr.get("wind_speed_10m", 0)
        temp = curr.get("temperature_2m", 0)

        a.append(f"")
        a.append(f"   CURRENT WX  : Cloud {cloud}% | Precip {precip}mm | Wind {wind}km/h | {temp}C")

        if cloud > 70:
            a.append("   >> High cloud cover: UAV/PGM effectiveness LOW. Satellite surveillance limited.")
            a.append("      Shift to artillery fires expected. Favorable for infiltration ops.")
        elif cloud < 30:
            a.append("   >> Clear skies: IDEAL conditions for air operations and UAV strikes.")
            a.append("      PGM accuracy HIGH. Air defense readiness should be elevated.")
        if precip > 5:
            a.append("   >> Heavy precipitation: Ground operations RESTRICTED. Logistics disruption risk HIGH.")
            a.append("      Dirt roads unusable. Main supply routes limited to paved corridors.")
        if wind > 40:
            a.append(f"   >> Strong winds ({wind}km/h): UAV operations RESTRICTED.")
            a.append("      Light/tactical UAV systems ineffective. Heavy UAVs at limited capability.")

    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    # 6. STRATEGIC TARGETS â THREAT MATRIX
    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    if target_threats:
        a.append("")
        a.append("6. STRATEGIC TARGET THREAT MATRIX")
        a.append("=" * 64)
        a.append("   Assessment formula: Doctrine weight x Proximity risk x")
        a.append("   Seasonal multiplier x Weather impact factor")
        a.append("")

        for t in target_threats[:10]:
            indicator = "!!!" if t["threat_level"] == "CRITICAL" else \
                        "!! " if t["threat_level"] == "HIGH" else \
                        "!  " if t["threat_level"] == "ELEVATED" else "   "
            a.append(f"   {indicator} [{t['threat_level']:8s}] {t['name']}")
            a.append(f"       Type: {t['type']} | Control: {t['side']} | Score: {t['composite']}/100")

            # Specific threat reasoning
            if t["proximity_risk"] > 30:
                a.append(f"       >> PROXIMITY THREAT: High combat density in vicinity ({t['proximity_risk']:.0f})")
            if t["seasonal_boost"] > 1.0:
                a.append(f"       >> SEASONAL PRIORITY: Target value increased {t['seasonal_boost']:.1f}x this period")
            if t["weather_mod"] > 1.0:
                a.append(f"       >> WEATHER FACTOR: Clear conditions increase PGM accuracy by {t['weather_mod']:.1f}x")

    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    # 7. COA & PREDICTION â COURSES OF ACTION
    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    a.append("")
    a.append("7. COURSES OF ACTION & 72-HOUR FORECAST")
    a.append("=" * 64)

    # Most Likely COA
    a.append("   MOST LIKELY COURSE OF ACTION (MLCOA):")
    if escalation["trend"] == "escalating" and op_patterns["surge_detected"]:
        a.append("   Based on current surge pattern and escalation indicators,")
        if hottest_sector:
            a.append(f"   offensive operations in {hottest_sector[0]} sector expected to")
            a.append("   continue and intensify.")
        if shifting_sectors:
            shift_names = [s[0] for s in shifting_sectors]
            a.append(f"   Additionally, new contact points in {', '.join(shift_names)}")
            a.append("   sectors are highly probable.")
    elif escalation["trend"] == "stable":
        a.append("   Current positional warfare along frontlines expected to continue.")
        a.append("   No significant indicators of major offensive preparation detected.")
        if hottest_sector:
            a.append(f"   Primary axis of engagement: {hottest_sector[0]}")
    elif escalation["trend"] == "de-escalating":
        a.append("   Operational tempo shows decline. Probable causes:")
        a.append("   (a) Formal/informal ceasefire negotiations")
        a.append("   (b) Logistical reconstitution period")
        a.append("   (c) Seasonal operational pause")

    # Most Dangerous COA
    a.append("")
    a.append("   MOST DANGEROUS COURSE OF ACTION (MDCOA):")
    if escalation["level"] >= 4:
        a.append("   Escalation at Tier 4+. Risk of large-scale coordinated")
        a.append("   offensive operations HIGH. Simultaneous multi-front operations")
        a.append("   and strategic infrastructure targeting are key elements of this scenario.")
    elif escalation["level"] >= 3:
        a.append("   Risk of sudden escalation at current intensity exists. Particularly")
        if target_threats and target_threats[0]["threat_level"] == "CRITICAL":
            a.append(f"   high-impact strikes on critical targets such as {target_threats[0]['name']}")
            a.append("   could escalate the conflict to a new level.")
        else:
            a.append("   coordinated deep strikes or opening of a new front")
            a.append("   assessed as the most dangerous course of action.")
    else:
        a.append("   Current situation is relatively contained. However,")
        a.append("   risk of sudden provocation or surprise attack always exists.")

    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    # 8. PIR â PRIORITY INTELLIGENCE REQUIREMENTS
    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    a.append("")
    a.append("8. PRIORITY INTELLIGENCE REQUIREMENTS (PIR)")
    a.append("=" * 64)

    pir_num = 1
    if shifting_sectors:
        for sec_name, sec_data in shifting_sectors[:3]:
            a.append(f"   PIR-{pir_num}: What is driving the activity increase in {sec_name}?")
            a.append(f"           Force redeployment or fresh unit introduction?")
            pir_num += 1

    if hottest_sector and hottest_sector[1]["intensity"] in ("CRITICAL", "HIGH"):
        a.append(f"   PIR-{pir_num}: What is the objective limit and end-state of")
        a.append(f"           offensive operations in {hottest_sector[0]}?")
        pir_num += 1

    if op_patterns["surge_detected"]:
        a.append(f"   PIR-{pir_num}: What operational plan underlies the detected surge?")
        a.append(f"           Is it a limited objective or open-ended operation?")
        pir_num += 1

    if target_threats:
        critical_targets = [t for t in target_threats if t["threat_level"] == "CRITICAL"]
        if critical_targets:
            a.append(f"   PIR-{pir_num}: What is the current defensive posture and air defense")
            a.append(f"           capacity around {critical_targets[0]['name']}?")
            pir_num += 1

    a.append(f"   PIR-{pir_num}: Do logistics route activity and ammunition shipment")
    a.append(f"           patterns indicate preparation for a major operation?")

    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    # FOOTER
    # ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    a.append("")
    a.append("-" * 64)
    a.append(f"  END ASSESSMENT â NERAI STAFF INTELLIGENCE MODULE")
    a.append(f"  {now.strftime('%d %b %Y %H:%M UTC').upper()}")
    a.append(f"  Next update: +6 hours | Doctrine rev: IPB/METT-TC v3.2")
    a.append("=" * 64)

    return "\n".join(a)


# ââ VISUALIZATION ââââââââââââââââââââââââââââââââââââââââââââââââââââ

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
    label:{{color:'#c0c8d0',fontSize:10,formatter:function(p){{var n=p.name;if(n.length>20)n=n.substring(0,18)+'...';return n+'\\n'+p.percent.toFixed(1)+'%'}},overflow:'truncate',width:120}},
    labelLine:{{length:12,length2:8,lineStyle:{{color:'#334455'}}}},
    emphasis:{{itemStyle:{{shadowBlur:20,shadowColor:'rgba(0,0,0,0.5)'}}}}
  }}]
}});
window.addEventListener('resize',function(){{chart.resize()}});
</script>
</body></html>"""
    return html


# ââ MAIN RENDER FUNCTION âââââââââââââââââââââââââââââââââââââââââââââ

def render_conflict_intelligence(gdelt_fetch_fn=None):
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

    # Fallback to synthetic if API fails
    using_synthetic = False
    if events_df.empty:
        events_df = _generate_synthetic_events(zone_name, days_back)
        using_synthetic = True

    weather_data = fetch_weather_for_zone(zone_name)

    # Compute analysis
    grid_risk = compute_grid_risk(events_df, zone_name)
    escalation = compute_escalation_index(events_df, zone_name)
    attack_patterns = compute_attack_pattern_analysis(events_df, zone_name)

    strategic_targets = STRATEGIC_TARGETS_UKR if zone_name == "Ukraine-Russia" else None

    # Data source notice
    if using_synthetic:
        st.markdown("""<div style="background:rgba(255,152,0,0.1);border:1px solid rgba(255,152,0,0.3);
                    border-radius:8px;padding:10px 14px;margin-bottom:14px;font-size:0.82rem;color:#ffab00">
                    ACLED API baglantisi kurulamadi. Gercekci sentetik veri kullaniliyor.
                    Canli veri icin ACLED API erisimi gereklidir (acleddata.com).
                    </div>""", unsafe_allow_html=True)

    # ââ KPI Cards ââââââââââââââââââââââââââââââââââââââââââââ
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

    # ââ Conflict Map âââââââââââââââââââââââââââââââââââââââââ
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

    # ââ Trend & Attack Pattern âââââââââââââââââââââââââââââââ
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

    # ââ Top Risk Grid Table ââââââââââââââââââââââââââââââââââ
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

    # ââ Kurmay Assessment ââââââââââââââââââââââââââââââââââââ
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

    # ââ Weather Impact Panel âââââââââââââââââââââââââââââââââ
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

    # ââ Methodology note âââââââââââââââââââââââââââââââââââââ
    st.markdown("""<div style="margin-top:24px;padding:12px 16px;background:rgba(10,22,40,0.5);
                border:1px solid #0d2137;border-radius:8px;font-size:0.72rem;color:#556677">
                <b>Methodology:</b> ACLED conflict data + GDELT event stream + Open-Meteo weather +
                Military doctrine rules (logistics range, operational tempo, weather impact, strategic target value).
                Predictions are based on open-source intelligence and do not carry tactical-level precision.
                Risk scores are based on 14-day exponential decay weighted event density.
                </div>""", unsafe_allow_html=True)
