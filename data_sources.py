"""
NERAI Intelligence Hub — External Data Sources
Fetches data from ACLED, World Bank, Commodity APIs, and Think Tank RSS feeds.
"""

import os
import json
import time
import datetime
import pandas as pd
import urllib.request
import urllib.parse

# ================================================================
# 1. ACLED — Armed Conflict Location & Event Data
# ================================================================
ACLED_API_URL = "https://acleddata.com/acled/read"
ACLED_EMAIL   = os.getenv("ACLED_EMAIL", "")
ACLED_KEY     = os.getenv("ACLED_KEY", "")

def fetch_acled(countries=None, days_back=90, limit=5000):
    """
    Fetch recent conflict events from ACLED.
    Register at https://acleddata.com/register/ for free API key.
    """
    if not ACLED_EMAIL or not ACLED_KEY:
        print("[ACLED] Skipped — set ACLED_EMAIL and ACLED_KEY env vars")
        return None

    since = (datetime.date.today() - datetime.timedelta(days=days_back)).strftime("%Y-%m-%d")
    params = {
        "key":          ACLED_KEY,
        "email":        ACLED_EMAIL,
        "event_date":   f"{since}|{datetime.date.today().isoformat()}",
        "event_date_where": "BETWEEN",
        "limit":        limit,
        "fields":       "event_date|country|event_type|sub_event_type|fatalities|actor1|actor2|notes|latitude|longitude",
    }
    if countries:
        params["country"] = "|".join(countries)

    url = ACLED_API_URL + "?" + urllib.parse.urlencode(params, safe="|")
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        if "data" in data and data["data"]:
            df = pd.DataFrame(data["data"])
            df["event_date"] = pd.to_datetime(df["event_date"])
            df["fatalities"] = pd.to_numeric(df["fatalities"], errors="coerce").fillna(0).astype(int)
            print(f"[ACLED] Fetched {len(df)} events")
            return df
        print("[ACLED] No data returned")
        return None
    except Exception as e:
        print(f"[ACLED] Error: {e}")
        return None


# ================================================================
# 2. WORLD BANK — Economic Indicators
# ================================================================
WB_API_URL = "https://api.worldbank.org/v2"

WB_INDICATORS = {
    "gdp_growth":     "NY.GDP.MKTP.KD.ZG",
    "gdp_current":    "NY.GDP.MKTP.CD",
    "inflation":      "FP.CPI.TOTL.ZG",
    "unemployment":   "SL.UEM.TOTL.ZS",
    "trade_pct_gdp":  "TG.VAL.TOTL.GD.ZS",
    "fdi_inflows":    "BX.KLT.DINV.CD.WD",
    "debt_pct_gni":   "DT.DOD.DECT.GN.ZS",
}

def fetch_worldbank(country_code="all", indicator="gdp_growth", start_year=2015, end_year=2025):
    """Fetch economic indicator from World Bank API. No API key required."""
    ind_code = WB_INDICATORS.get(indicator, indicator)
    url = f"{WB_API_URL}/country/{country_code}/indicator/{ind_code}"
    params = urllib.parse.urlencode({"format": "json", "date": f"{start_year}:{end_year}", "per_page": 1000})
    full_url = f"{url}?{params}"

    try:
        with urllib.request.urlopen(full_url, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        if len(data) < 2 or not data[1]:
            return None
        rows = []
        for item in data[1]:
            rows.append({
                "country":      item.get("country", {}).get("value", ""),
                "country_code": item.get("countryiso3code", ""),
                "year":         int(item.get("date", 0)),
                "value":        item.get("value"),
                "indicator":    indicator,
            })
        df = pd.DataFrame(rows)
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        return df.dropna(subset=["value"])
    except Exception as e:
        print(f"[WorldBank] Error: {e}")
        return None


def fetch_worldbank_multi(country_code="US", indicators=None, start_year=2015, end_year=2025):
    """Fetch multiple World Bank indicators for a country."""
    if indicators is None:
        indicators = ["gdp_growth", "inflation", "unemployment"]
    frames = []
    for ind in indicators:
        df = fetch_worldbank(country_code, ind, start_year, end_year)
        if df is not None and len(df) > 0:
            frames.append(df)
        time.sleep(0.3)
    return pd.concat(frames, ignore_index=True) if frames else None


# ================================================================
# 3. IMF — International Monetary Fund Data
# ================================================================
IMF_API_URL = "https://www.imf.org/external/datamapper/api/v1"

IMF_INDICATORS = {
    "real_gdp":      "NGDP_R",
    "nominal_gdp":   "NGDP",
    "inflation":     "PCPIPCH",
    "unemployment":  "LUR",
    "gov_debt":      "GGXWDG_NGDP",
    "current_acct":  "BCA_NGDPD",
}

def fetch_imf(indicator="real_gdp", countries=None, start_year=2015, end_year=2025):
    """Fetch data from IMF DataMapper API. No API key required."""
    ind_code = IMF_INDICATORS.get(indicator, indicator)
    url = f"{IMF_API_URL}/{ind_code}"
    if countries:
        url += "/" + "/".join(countries)
    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "NERAI-Intelligence-Hub/1.0")
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        values = data.get("values", {}).get(ind_code, {})
        rows = []
        for ccode, yearly in values.items():
            for year_str, val in yearly.items():
                yr = int(year_str)
                if start_year <= yr <= end_year:
                    rows.append({"country_code": ccode, "year": yr, "value": float(val) if val else None, "indicator": indicator})
        return pd.DataFrame(rows).dropna(subset=["value"]) if rows else None
    except Exception as e:
        print(f"[IMF] Error: {e}")
        return None


# ================================================================
# 4. COMMODITY PRICES
# ================================================================
COMMODITY_SYMBOLS = {
    "crude_oil_wti": "CL=F", "crude_oil_brent": "BZ=F",
    "natural_gas": "NG=F", "gold": "GC=F", "silver": "SI=F",
    "copper": "HG=F", "wheat": "ZW=F", "corn": "ZC=F",
}

def fetch_commodities_yfinance(symbols=None, period="6mo"):
    """Fetch commodity prices using yfinance. No API key required."""
    try:
        import yfinance as yf
    except ImportError:
        print("[Commodities] Install yfinance: pip install yfinance")
        return None
    if symbols is None:
        symbols = COMMODITY_SYMBOLS
    frames = []
    for name, ticker in symbols.items():
        try:
            data = yf.download(ticker, period=period, progress=False)
            if data is not None and len(data) > 0:
                df = data[["Close", "Volume"]].reset_index()
                df.columns = ["date", "close", "volume"]
                df["commodity"] = name
                frames.append(df)
        except Exception as e:
            print(f"[Commodities] Error {name}: {e}")
        time.sleep(0.3)
    if frames:
        return pd.concat(frames, ignore_index=True)
    return None


# ================================================================
# 5. THINK TANK & SUBSTACK RSS FEEDS
# ================================================================
THINK_TANK_FEEDS = {
    "Brookings":          "https://www.brookings.edu/feed/",
    "Carnegie Endowment": "https://carnegieendowment.org/rss/",
    "CSIS":               "https://www.csis.org/analysis/feed",
    "CFR":                "https://www.cfr.org/rss/blog",
    "Chatham House":      "https://www.chathamhouse.org/rss",
    "Foreign Affairs":    "https://www.foreignaffairs.com/rss.xml",
    "RAND":               "https://www.rand.org/feeds/rand-review.xml",
}

SUBSTACK_FEEDS = {
    "Geopolitical Dispatch":  "https://geopoliticaldispatch.substack.com/feed",
    "Geopolitics Unplugged":  "https://geopoliticsunplugged.substack.com/feed",
    "EM & Geopolitics":       "https://timothyash.substack.com/feed",
    "The Octavian Report":    "https://octavian.substack.com/feed",
    "Drop Site":              "https://dropsite.substack.com/feed",
    "Sinification":           "https://sinification.substack.com/feed",
    "The Overshoot":          "https://theovershoot.substack.com/feed",
}

def fetch_rss_articles(feeds=None, max_per_feed=10):
    """Fetch articles from RSS/Atom feeds."""
    try:
        import feedparser
    except ImportError:
        print("[RSS] Install feedparser: pip install feedparser")
        return _fetch_rss_fallback(feeds, max_per_feed)
    if feeds is None:
        feeds = {**THINK_TANK_FEEDS, **SUBSTACK_FEEDS}
    all_entries = []
    for source_name, feed_url in feeds.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:max_per_feed]:
                published = getattr(entry, "published", "") or getattr(entry, "updated", "")
                summary = entry.get("summary", "")
                if "<" in summary:
                    import re
                    summary = re.sub(r"<[^>]+>", "", summary)[:500]
                tags = [t.term for t in entry.get("tags", [])] if hasattr(entry, "tags") else []
                all_entries.append({
                    "title": entry.get("title", ""), "summary": summary,
                    "link": entry.get("link", ""), "published": published,
                    "author": entry.get("author", ""), "source": source_name,
                    "tags": ", ".join(tags),
                })
        except Exception as e:
            print(f"[RSS] Error {source_name}: {e}")
        time.sleep(0.5)
    return pd.DataFrame(all_entries) if all_entries else None


def _fetch_rss_fallback(feeds=None, max_per_feed=5):
    """Fallback RSS parser using only stdlib."""
    import xml.etree.ElementTree as ET
    if feeds is None:
        feeds = {**THINK_TANK_FEEDS, **SUBSTACK_FEEDS}
    all_entries = []
    for source_name, feed_url in feeds.items():
        try:
            req = urllib.request.Request(feed_url)
            req.add_header("User-Agent", "NERAI-Intelligence-Hub/1.0")
            with urllib.request.urlopen(req, timeout=15) as resp:
                xml_data = resp.read()
            root = ET.fromstring(xml_data)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            items = root.findall(".//item") or root.findall(".//atom:entry", ns)
            for item in items[:max_per_feed]:
                title = item.findtext("title") or item.findtext("atom:title", namespaces=ns) or ""
                link = item.findtext("link") or ""
                if not link:
                    link_el = item.find("atom:link", ns)
                    if link_el is not None: link = link_el.get("href", "")
                all_entries.append({
                    "title": title, "summary": (item.findtext("description") or "")[:500],
                    "link": link, "published": item.findtext("pubDate") or "",
                    "author": item.findtext("author") or "", "source": source_name, "tags": "",
                })
        except Exception as e:
            print(f"[RSS-fallback] Error {source_name}: {e}")
        time.sleep(0.5)
    return pd.DataFrame(all_entries) if all_entries else None


# ================================================================
# MAIN
# ================================================================
def update_all_sources(output_dir="."):
    """Run all data fetchers and save results as CSV files."""
    print("=" * 60)
    print("NERAI Intelligence Hub — Updating External Data Sources")
    print("=" * 60)

    acled_df = fetch_acled()
    if acled_df is not None:
        acled_df.to_csv(os.path.join(output_dir, "acled_events.csv"), index=False)

    major_countries = ["US", "CN", "GB", "DE", "JP", "IN", "BR", "TR", "RU", "ZA"]
    wb_frames = []
    for cc in major_countries:
        df = fetch_worldbank_multi(cc)
        if df is not None: wb_frames.append(df)
        time.sleep(0.3)
    if wb_frames:
        pd.concat(wb_frames, ignore_index=True).to_csv(os.path.join(output_dir, "worldbank_indicators.csv"), index=False)

    comm_df = fetch_commodities_yfinance()
    if comm_df is not None:
        comm_df.to_csv(os.path.join(output_dir, "commodities.csv"), index=False)

    articles_df = fetch_rss_articles()
    if articles_df is not None:
        articles_df.to_csv(os.path.join(output_dir, "articles.csv"), index=False)

    print("Update complete!")


if __name__ == "__main__":
    update_all_sources()
