"""
rss_enrichment.py -- Fetch quality geopolitical & economic articles via RSS
Saves to enriched_articles.csv for use in NERAI dashboard Q&A context.
Run daily via GitHub Actions.
"""

import feedparser
import pandas as pd
import hashlib
import re
import os
from datetime import datetime, timezone, timedelta
from time import mktime

FEEDS = [
    {"url": "https://www.foreignaffairs.com/rss.xml",            "source": "Foreign Affairs",        "category": "foreign_policy"},
    {"url": "https://foreignpolicy.com/feed/",                   "source": "Foreign Policy",         "category": "foreign_policy"},
    {"url": "https://warontherocks.com/feed/",                   "source": "War on the Rocks",       "category": "security"},
    {"url": "https://responsiblestatecraft.org/feed/",           "source": "Responsible Statecraft", "category": "security"},
    {"url": "https://www.brookings.edu/feed/",                   "source": "Brookings",              "category": "policy"},
    {"url": "https://www.rand.org/blog.xml",                     "source": "RAND",                   "category": "policy"},
    {"url": "https://carnegieendowment.org/rss/solr/articles",   "source": "Carnegie Endowment",     "category": "policy"},
    {"url": "https://www.csis.org/rss.xml",                      "source": "CSIS",                   "category": "policy"},
    {"url": "https://www.atlanticcouncil.org/feed/",             "source": "Atlantic Council",       "category": "policy"},
    {"url": "https://ecfr.eu/feed/",                             "source": "ECFR",                   "category": "policy"},
    {"url": "https://www.chathamhouse.org/rss.xml",              "source": "Chatham House",          "category": "policy"},
    {"url": "https://www.lowyinstitute.org/the-interpreter/rss.xml", "source": "Lowy Institute",    "category": "policy"},
    {"url": "https://www.crisisgroup.org/rss.xml",               "source": "ICG Crisis Group",       "category": "conflict"},
    {"url": "https://www.bellingcat.com/feed/",                  "source": "Bellingcat",             "category": "investigation"},
    {"url": "https://www.geopoliticalfutures.com/feed/",         "source": "Geopolitical Futures",   "category": "geopolitics"},
    {"url": "https://blogs.worldbank.org/en/rss.xml",            "source": "World Bank Blog",        "category": "economics"},
    {"url": "https://www.imf.org/en/News/rss?language=eng",      "source": "IMF",                    "category": "economics"},
    {"url": "https://www.eia.gov/rss/todayinenergy.xml",         "source": "EIA",                    "category": "energy"},
    {"url": "https://oilprice.com/rss/main",                     "source": "OilPrice.com",           "category": "energy"},
    {"url": "https://www.cnas.org/feed",                         "source": "CNAS",                   "category": "security"},
    {"url": "https://acleddata.com/feed/",                       "source": "ACLED",                  "category": "conflict"},
]

COUNTRY_KEYWORDS = {
    "russia": ["russia", "russian", "kremlin", "moscow", "putin", "ukraine"],
    "ukraine": ["ukraine", "ukrainian", "kyiv", "zelensky", "donbas"],
    "china": ["china", "chinese", "beijing", "xi jinping", "pla", "taiwan"],
    "usa": ["united states", "american", "washington", "biden", "trump", "pentagon"],
    "iran": ["iran", "iranian", "tehran", "irgc", "ayatollah"],
    "israel": ["israel", "israeli", "tel aviv", "netanyahu", "gaza", "idf"],
    "turkey": ["turkey", "turkish", "ankara", "erdogan"],
    "saudi arabia": ["saudi", "riyadh", "opec", "aramco"],
    "india": ["india", "indian", "delhi", "modi"],
    "pakistan": ["pakistan", "islamabad"],
    "north korea": ["north korea", "dprk", "pyongyang", "kim jong"],
    "germany": ["germany", "german", "berlin"],
    "france": ["france", "french", "paris", "macron"],
    "uk": ["united kingdom", "britain", "british", "london"],
    "brazil": ["brazil", "brasilia", "lula"],
    "venezuela": ["venezuela", "maduro", "caracas"],
    "ethiopia": ["ethiopia", "addis ababa", "tigray"],
    "myanmar": ["myanmar", "burma", "naypyidaw"],
    "afghanistan": ["afghanistan", "kabul", "taliban"],
    "syria": ["syria", "damascus"],
    "iraq": ["iraq", "baghdad", "isis"],
}

TOPIC_KEYWORDS = {
    "military": ["military", "armed forces", "troops", "soldiers", "warfare", "airstrikes", "missile"],
    "nuclear": ["nuclear", "nuke", "warhead", "nonproliferation", "iaea"],
    "sanctions": ["sanctions", "embargo", "export controls"],
    "trade": ["trade", "tariff", "export", "import", "supply chain"],
    "energy": ["oil", "gas", "energy", "opec", "petroleum", "lng", "pipeline"],
    "economy": ["gdp", "inflation", "recession", "economy", "economic"],
    "elections": ["election", "vote", "ballot", "democracy"],
    "terrorism": ["terrorism", "terror", "isis", "al-qaeda"],
    "coup": ["coup", "overthrow", "military takeover", "junta"],
    "diplomacy": ["diplomacy", "summit", "treaty", "negotiations", "ceasefire"],
    "climate": ["climate change", "carbon", "emissions", "global warming"],
    "cyber": ["cyberattack", "hacking", "ransomware", "cyber"],
    "migration": ["migration", "refugee", "asylum", "border"],
    "commodities": ["commodity", "gold", "copper", "wheat", "corn", "metals"],
}


def _extract_text(entry):
    if hasattr(entry, "summary"):
        return re.sub(r"<[^>]+>", " ", entry.summary or "").strip()
    if hasattr(entry, "content"):
        for c in entry.content:
            if c.get("value"):
                return re.sub(r"<[^>]+>", " ", c["value"]).strip()
    return (entry.get("title") or "").strip()


def _detect_countries(text):
    lower = text.lower()
    found = [c for c, kws in COUNTRY_KEYWORDS.items() if any(k in lower for k in kws)]
    return ",".join(found[:10])


def _detect_topics(text):
    lower = text.lower()
    found = [t for t, kws in TOPIC_KEYWORDS.items() if any(k in lower for k in kws)]
    return ",".join(found[:10])


def _parse_date(entry):
    try:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            dt = datetime.fromtimestamp(mktime(entry.published_parsed), tz=timezone.utc)
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def fetch_feed(feed_cfg):
    articles = []
    try:
        parsed = feedparser.parse(feed_cfg["url"])
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        for entry in parsed.entries[:30]:
            date_str = _parse_date(entry)
            try:
                entry_dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except Exception:
                entry_dt = datetime.now(timezone.utc)
            if entry_dt < cutoff:
                continue
            title   = (entry.get("title") or "").strip()
            url     = (entry.get("link")  or "").strip()
            summary = _extract_text(entry)[:500].replace("\n", " ").strip()
            uid_src = url or f"{feed_cfg['source']}:{title}"
            uid     = hashlib.md5(uid_src.encode()).hexdigest()[:12]
            combined = f"{title} {summary}"
            articles.append({
                "date": date_str, "title": title, "summary": summary,
                "source": feed_cfg["source"], "category": feed_cfg["category"],
                "url": url, "countries": _detect_countries(combined),
                "topics": _detect_topics(combined), "uid": uid,
            })
    except Exception as e:
        print(f"[RSS] Error {feed_cfg['source']}: {e}")
    return articles


def run():
    print(f"[RSS] Starting at {datetime.now(timezone.utc).isoformat()}")
    all_articles = []
    for feed in FEEDS:
        arts = fetch_feed(feed)
        print(f"[RSS]  {feed['source']}: {len(arts)} articles")
        all_articles.extend(arts)
    if not all_articles:
        print("[RSS] No articles.")
        return
    df_new = pd.DataFrame(all_articles).drop_duplicates(subset=["uid"])
    csv_path = "enriched_articles.csv"
    if os.path.exists(csv_path):
        try:
            df_old = pd.read_csv(csv_path, dtype=str)
            df_all = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates(subset=["uid"])
            cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
            df_all = df_all[df_all["date"] >= cutoff]
        except Exception as e:
            print(f"[RSS] Merge error: {e}")
            df_all = df_new
    else:
        df_all = df_new
    df_all = df_all.sort_values("date", ascending=False).reset_index(drop=True)
    df_all.to_csv(csv_path, index=False)
    print(f"[RSS] Saved {len(df_all)} articles to {csv_path}")


if __name__ == "__main__":
    run()
