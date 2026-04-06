"""
commodity_data.py â Fetch daily commodity & market prices via yfinance
Saves to commodities.csv for use in NERAI dashboard Q&A context.
Run daily via GitHub Actions.
"""

import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timezone, timedelta

TICKERS = {
    # Energy
    "CL=F":     {"name": "WTI Crude Oil",    "category": "energy",     "unit": "USD/bbl"},
    "BZ=F":     {"name": "Brent Crude Oil",  "category": "energy",     "unit": "USD/bbl"},
    "NG=F":     {"name": "Natural Gas",      "category": "energy",     "unit": "USD/MMBtu"},
    "HO=F":     {"name": "Heating Oil",      "category": "energy",     "unit": "USD/gal"},
    # Metals
    "GC=F":     {"name": "Gold",             "category": "metals",     "unit": "USD/oz"},
    "SI=F":     {"name": "Silver",           "category": "metals",     "unit": "USD/oz"},
    "HG=F":     {"name": "Copper",           "category": "metals",     "unit": "USD/lb"},
    "PL=F":     {"name": "Platinum",         "category": "metals",     "unit": "USD/oz"},
    # Agriculture
    "ZW=F":     {"name": "Wheat",            "category": "agriculture","unit": "USc/bu"},
    "ZC=F":     {"name": "Corn",             "category": "agriculture","unit": "USc/bu"},
    "ZS=F":     {"name": "Soybeans",         "category": "agriculture","unit": "USc/bu"},
    # Financial / Macro
    "^VIX":     {"name": "VIX Fear Index",   "category": "financial",  "unit": "index"},
    "DX-Y.NYB": {"name": "USD Index",        "category": "financial",  "unit": "index"},
    "^TNX":     {"name": "10Y US Treasury",  "category": "financial",  "unit": "% yield"},
    "EURUSD=X": {"name": "EUR/USD",          "category": "financial",  "unit": "rate"},
    "USDRUB=X": {"name": "USD/RUB",          "category": "financial",  "unit": "rate"},
    "USDCNY=X": {"name": "USD/CNY",          "category": "financial",  "unit": "rate"},
    "^GSPC":    {"name": "S&P 500",          "category": "financial",  "unit": "index"},
}


def fetch_prices() -> pd.DataFrame:
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
                    "date":     str(date_idx.date()),
                    "ticker":   ticker_sym,
                    "name":     meta["name"],
                    "category": meta["category"],
                    "unit":     meta["unit"],
                    "price":    round(close, 4),
                })

            print(f"[COMM] {meta['name']} ({ticker_sym}): {len(hist)} rows")

        except Exception as e:
            print(f"[COMM] Error fetching {ticker_sym}: {e}")

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    return df.sort_values(["ticker", "date"]).reset_index(drop=True)


def compute_changes(df: pd.DataFrame) -> pd.DataFrame:
    dfs = []
    for ticker, grp in df.groupby("ticker"):
        grp = grp.sort_values("date").copy()
        grp["chg_1d_pct"] = grp["price"].pct_change(1).round(4)
        grp["chg_7d_pct"] = grp["price"].pct_change(7).round(4)
        dfs.append(grp)
    return pd.concat(dfs, ignore_index=True) if dfs else df


# --- FAZ 2d: Time alignment with GDELT weekly data ---
def resample_weekly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resample daily commodity data to weekly frequency (ISO weeks),
    aligned with GDELT weekly aggregation period boundaries.
    Returns: DataFrame with weekly OHLC-style aggregation per ticker.
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    weekly_dfs = []
    for ticker, grp in df.groupby("ticker"):
        grp = grp.set_index("date").sort_index()
        # Resample to week-ending Sunday (ISO standard, matches GDELT)
        w = grp["price"].resample("W-SUN").agg(
            price_open="first",
            price_close="last",
            price_high="max",
            price_low="min",
            price_mean="mean",
            n_trading_days="count",
        ).dropna(subset=["price_close"])

        # Weekly returns
        w["chg_1w_pct"] = w["price_close"].pct_change(1).round(4)
        w["chg_4w_pct"] = w["price_close"].pct_change(4).round(4)

        # Carry forward metadata
        meta = grp[["name", "category", "unit"]].iloc[0]
        w["ticker"]   = ticker
        w["name"]     = meta["name"]
        w["category"] = meta["category"]
        w["unit"]     = meta["unit"]

        w = w.reset_index().rename(columns={"date": "week_end"})
        # ISO year-week key for merging with GDELT
        w["yw"] = w["week_end"].dt.isocalendar().year.astype(str) + "-W" + \
                  w["week_end"].dt.isocalendar().week.astype(str).str.zfill(2)
        weekly_dfs.append(w)

    if not weekly_dfs:
        return pd.DataFrame()
    return pd.concat(weekly_dfs, ignore_index=True)


def align_with_gdelt(commodity_weekly: pd.DataFrame,
                     gdelt_weekly: pd.DataFrame) -> pd.DataFrame:
    """
    Merge weekly commodity data with GDELT weekly indices on the ISO year-week key.
    Both DataFrames must have a "yw" column (e.g. "2024-W03").
    Returns: merged DataFrame with commodity prices alongside GDELT risk indices.
    """
    if "yw" not in commodity_weekly.columns:
        raise ValueError("commodity_weekly must have a yw column. Use resample_weekly() first.")
    if "yw" not in gdelt_weekly.columns:
        raise ValueError("gdelt_weekly must have a yw column.")

    # Pivot commodity data: one column per ticker
    comm_pivot = commodity_weekly.pivot_table(
        index="yw",
        columns="name",
        values=["price_mean", "chg_1w_pct"],
        aggfunc="first"
    )
    # Flatten multi-index columns
    comm_pivot.columns = [f"{val}_{col}" for val, col in comm_pivot.columns]
    comm_pivot = comm_pivot.reset_index()

    merged = gdelt_weekly.merge(comm_pivot, on="yw", how="left")

    # Forward-fill commodity prices for weeks with no trading data
    price_cols = [c for c in merged.columns if c.startswith("price_mean_")]
    for col in price_cols:
        merged[col] = merged[col].ffill()

    n_matched = merged[price_cols[0]].notna().sum() if price_cols else 0
    print(f"[ALIGN] Merged {len(comm_pivot)} commodity weeks with {len(gdelt_weekly)} GDELT weeks -> {n_matched} matched")
    return merged


def run():
    print(f"[COMM] Starting commodity fetch at {datetime.now(timezone.utc).isoformat()}")

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

    # FAZ 2d: Also export weekly-resampled data for GDELT alignment
    weekly = resample_weekly(df)
    weekly_path = "commodities_weekly.csv"
    weekly.to_csv(weekly_path, index=False)
    print(f"[COMM] Saved {len(weekly)} weekly rows to {weekly_path}")

    latest_date = df["date"].max()
    latest = df[df["date"] == latest_date][["name", "price", "unit", "chg_1d_pct"]].copy()
    latest["chg_1d_pct"] = (latest["chg_1d_pct"] * 100).round(2).astype(str) + "%"
    print(f"\n[COMM] Latest prices ({latest_date}):")
    print(latest.to_string(index=False))


if __name__ == "__main__":
    run()
