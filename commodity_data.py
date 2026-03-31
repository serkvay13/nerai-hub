"""
commodity_data.py -- Fetch daily commodity & market prices via yfinance
Saves to commodities.csv for NERAI dashboard Q&A context.
Run daily via GitHub Actions.
"""

import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timezone, timedelta

TICKERS = {
    "CL=F":     {"name": "WTI Crude Oil",    "category": "energy",     "unit": "USD/bbl"},
    "BZ=F":     {"name": "Brent Crude Oil",  "category": "energy",     "unit": "USD/bbl"},
    "NG=F":     {"name": "Natural Gas",      "category": "energy",     "unit": "USD/MMBtu"},
    "HO=F":     {"name": "Heating Oil",      "category": "energy",     "unit": "USD/gal"},
    "GC=F":     {"name": "Gold",             "category": "metals",     "unit": "USD/oz"},
    "SI=F":     {"name": "Silver",           "category": "metals",     "unit": "USD/oz"},
    "HG=F":     {"name": "Copper",           "category": "metals",     "unit": "USD/lb"},
    "PL=F":     {"name": "Platinum",         "category": "metals",     "unit": "USD/oz"},
    "ZW=F":     {"name": "Wheat",            "category": "agriculture","unit": "USc/bu"},
    "ZC=F":     {"name": "Corn",             "category": "agriculture","unit": "USc/bu"},
    "ZS=F":     {"name": "Soybeans",         "category": "agriculture","unit": "USc/bu"},
    "^VIX":     {"name": "VIX Fear Index",   "category": "financial",  "unit": "index"},
    "DX-Y.NYB": {"name": "USD Index",        "category": "financial",  "unit": "index"},
    "^TNX":     {"name": "10Y US Treasury",  "category": "financial",  "unit": "% yield"},
    "EURUSD=X": {"name": "EUR/USD",          "category": "financial",  "unit": "rate"},
    "USDRUB=X": {"name": "USD/RUB",          "category": "financial",  "unit": "rate"},
    "USDCNY=X": {"name": "USD/CNY",          "category": "financial",  "unit": "rate"},
    "^GSPC":    {"name": "S&P 500",          "category": "financial",  "unit": "index"},
}


def fetch_prices():
    end_date   = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=730)
    rows = []
    for ticker_sym, meta in TICKERS.items():
        try:
            tk   = yf.Ticker(ticker_sym)
            hist = tk.history(start=str(start_date), end=str(end_date), interval="1d")
            if hist.empty:
                print(f"[COMM] No data for {ticker_sym}")
                continue
            for date_idx, row in hist.iterrows():
                close = row.get("Close")
                if close is None:
                    continue
                if isinstance(close, pd.Series):
                    close = float(close.iloc[0])
                else:
                    close = float(close)
                rows.append({
                    "date": str(date_idx.date()), "ticker": ticker_sym,
                    "name": meta["name"], "category": meta["category"],
                    "unit": meta["unit"], "price": round(close, 4),
                })
            print(f"[COMM] {meta['name']}: {len(hist)} rows")
        except Exception as e:
            print(f"[COMM] Error {ticker_sym}: {e}")
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(["ticker", "date"]).reset_index(drop=True)


def compute_changes(df):
    dfs = []
    for ticker, grp in df.groupby("ticker"):
        grp = grp.sort_values("date").copy()
        grp["chg_1d_pct"] = grp["price"].pct_change(1).round(4)
        grp["chg_7d_pct"] = grp["price"].pct_change(7).round(4)
        dfs.append(grp)
    return pd.concat(dfs, ignore_index=True) if dfs else df


def run():
    print(f"[COMM] Starting at {datetime.now(timezone.utc).isoformat()}")
    df = fetch_prices()
    if df.empty:
        print("[COMM] No data fetched.")
        return
    df = compute_changes(df)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=730)).strftime("%Y-%m-%d")
    df = df[df["date"] >= cutoff]
    csv_path = "commodities.csv"
    df.to_csv(csv_path, index=False)
    print(f"[COMM] Saved {len(df)} rows to {csv_path}")
    latest_date = df["date"].max()
    latest = df[df["date"] == latest_date][["name","price","unit","chg_1d_pct"]].copy()
    latest["chg_1d_pct"] = (latest["chg_1d_pct"] * 100).round(2).astype(str) + "%"
    print(f"\n[COMM] Latest prices ({latest_date}):")
    print(latest.to_string(index=False))


if __name__ == "__main__":
    run()
