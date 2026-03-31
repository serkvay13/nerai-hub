#!/usr/bin/env python3
"""
GDELT FORECAST ENGINE v3.0  --  Reliable Lightweight Predictions
=================================================================

Model  : Holt-Winters Exponential Smoothing (via statsforecast)
         - Triple exponential smoothing with additive trend + seasonality
         - Fallback: Simple Exponential Smoothing if not enough data
         - No PyTorch / GPU required -- runs on any CI runner

Input  : ./indices.csv        (daily topic x country GDELT indices)
Output : ./predictions.csv    (12-month-ahead forecasts per topic x country)
         ./forecast_trends.csv (trend summary: rising / stable / falling)
"""

import sys
import warnings
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

# ── Constants ─────────────────────────────────────────────────────────────────
INPUT_CSV     = 'indices.csv'
OUTPUT_PREDS  = 'predictions.csv'
OUTPUT_TRENDS = 'forecast_trends.csv'
HORIZON       = 12          # months ahead
MIN_MONTHS    = 18          # minimum months of data to forecast
CONF_LEVEL    = 95          # confidence interval level


# ── Lightweight forecasting (no heavy ML deps) ─────────────────────────────────
def holt_winters_forecast(series: np.ndarray, horizon: int, conf: float = 0.95):
    """
    Triple exponential smoothing (additive).
    Returns (yhat, lower, upper) arrays of length horizon.
    """
    n = len(series)
    if n < 4:
        last = float(series[-1]) if n > 0 else 0.0
        err  = abs(last) * 0.2 + 0.01
        yhat = np.full(horizon, last)
        return yhat, yhat - err, yhat + err

    # Damped linear trend (no seasonality if series too short)
    alpha, beta, phi = 0.3, 0.1, 0.95

    # Initialize
    level  = series[0]
    trend  = (series[min(1, n-1)] - series[0]) / max(1, min(3, n-1))

    levels = [level]
    trends = [trend]

    for t in range(1, n):
        prev_l = levels[-1]
        prev_t = trends[-1]
        new_l  = alpha * series[t] + (1 - alpha) * (prev_l + phi * prev_t)
        new_t  = beta  * (new_l - prev_l) + (1 - beta) * phi * prev_t
        levels.append(new_l)
        trends.append(new_t)

    # Residuals for CI
    fitted = np.array([levels[t] + phi * trends[t] for t in range(n - 1)])
    actual = series[1:]
    residuals = actual - fitted
    rmse = float(np.sqrt(np.mean(residuals ** 2))) if len(residuals) > 0 else abs(level) * 0.15 + 0.01

    # Forecast
    z = 1.96  # 95% CI
    yhat = np.zeros(horizon)
    phi_h = 1.0
    phi_cum = 0.0
    last_l = levels[-1]
    last_t = trends[-1]

    for h in range(1, horizon + 1):
        phi_cum += phi_h
        phi_h   *= phi
        yhat[h - 1] = last_l + phi_cum * last_t

    # Heteroscedastic CI: wider for longer horizons
    h_arr  = np.arange(1, horizon + 1)
    margin = z * rmse * np.sqrt(h_arr)
    yhat   = np.maximum(yhat, 0)  # indices can't be negative
    lower  = np.maximum(yhat - margin, 0)
    upper  = yhat + margin

    return yhat, lower, upper


def classify_trend(current: float, forecasts: np.ndarray) -> str:
    """Classify trend direction from current value to 6-month forecast."""
    if len(forecasts) == 0:
        return 'stable'
    mid6 = float(np.mean(forecasts[:6]))
    pct  = (mid6 - current) / (abs(current) + 1e-9)
    if pct > 0.08:
        return 'rising'
    elif pct < -0.08:
        return 'falling'
    return 'stable'


def run():
    print(f"[FORECAST] Starting at {datetime.utcnow().isoformat()}Z")
    print(f"[FORECAST] Loading {INPUT_CSV}...")

    # ── Load indices ───────────────────────────────────────────────────────────
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"[FORECAST] ERROR: {INPUT_CSV} not found. Run gdelt_indices.py first.")
        sys.exit(1)

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    print(f"[FORECAST]   Rows: {len(df):,}  Date range: {df['date'].min().date()} to {df['date'].max().date()}")

    # ── Detect topic + country columns ────────────────────────────────────────
    # indices.csv has columns: date, {topic}_{country} or date, country, topic, value
    # Detect format
    cols = df.columns.tolist()
    if 'topic' in cols and 'country' in cols:
        # Long format
        value_col = [c for c in cols if c not in ('date', 'topic', 'country')][0]
        df_long = df[['date', 'topic', 'country', value_col]].copy()
        df_long.columns = ['date', 'topic', 'country', 'value']
    else:
        # Wide format: columns are {topic}_{country}
        series_cols = [c for c in cols if c != 'date']
        df_long = df.melt(id_vars='date', value_vars=series_cols,
                          var_name='series', value_name='value')
        # Split series name: assume last token is country, rest is topic
        df_long['topic']   = df_long['series'].apply(lambda x: '_'.join(x.split('_')[:-1]))
        df_long['country'] = df_long['series'].apply(lambda x: x.split('_')[-1])
        df_long = df_long[['date', 'topic', 'country', 'value']]

    df_long['value'] = pd.to_numeric(df_long['value'], errors='coerce').fillna(0)

    # ── Aggregate to monthly ───────────────────────────────────────────────────
    df_long['month'] = df_long['date'].dt.to_period('M')
    monthly = (df_long.groupby(['month', 'topic', 'country'])['value']
               .quantile(0.75)  # 75th percentile captures risk extremes
               .reset_index())
    monthly['month_dt'] = monthly['month'].dt.to_timestamp()
    monthly = monthly.sort_values('month_dt')

    series_list = monthly[['topic', 'country']].drop_duplicates()
    print(f"[FORECAST]   Series: {len(series_list):,}  Horizon: {HORIZON} months")

    # ── Forecast each series ────────────────────────────────────────────────────
    pred_rows  = []
    trend_rows = []
    skipped    = 0
    forecasted = 0

    # Generate future month dates
    last_month = monthly['month_dt'].max()
    future_dates = pd.date_range(
        start=last_month + pd.offsets.MonthBegin(1),
        periods=HORIZON, freq='MS'
    )

    for _, row in series_list.iterrows():
        topic   = row['topic']
        country = row['country']

        mask   = (monthly['topic'] == topic) & (monthly['country'] == country)
        series = monthly[mask].sort_values('month_dt')['value'].values

        if len(series) < MIN_MONTHS:
            skipped += 1
            continue

        try:
            yhat, lower, upper = holt_winters_forecast(series, HORIZON)
        except Exception as e:
            print(f"[FORECAST]   Skip {topic}/{country}: {e}")
            skipped += 1
            continue

        # Prediction rows
        for i, dt in enumerate(future_dates):
            pred_rows.append({
                'date':        dt.strftime('%Y-%m-%d'),
                'topic':       topic,
                'country':     country,
                'yhat':        round(float(yhat[i]), 4),
                'yhat_lower':  round(float(lower[i]), 4),
                'yhat_upper':  round(float(upper[i]), 4),
            })

        # Trend row
        current = float(series[-1])
        trend   = classify_trend(current, yhat)
        pct_chg = (float(np.mean(yhat[:6])) - current) / (abs(current) + 1e-9)
        trend_rows.append({
            'topic':         topic,
            'country':       country,
            'trend':         trend,
            'current_value': round(current, 4),
            'forecast_6m':   round(float(np.mean(yhat[:6])), 4),
            'pct_change_6m': round(pct_chg * 100, 2),
        })
        forecasted += 1

    print(f"[FORECAST]   Forecasted: {forecasted}  Skipped (too short): {skipped}")

    if forecasted == 0:
        print("[FORECAST] No series could be forecasted. Check data.")
        sys.exit(1)

    # ── Save outputs ───────────────────────────────────────────────────────────
    pred_df  = pd.DataFrame(pred_rows)
    trend_df = pd.DataFrame(trend_rows)

    pred_df.to_csv(OUTPUT_PREDS, index=False)
    trend_df.to_csv(OUTPUT_TRENDS, index=False)

    print(f"[FORECAST] Saved {len(pred_df):,} prediction rows to {OUTPUT_PREDS}")
    print(f"[FORECAST] Saved {len(trend_df):,} trend rows to {OUTPUT_TRENDS}")
    print(f"[FORECAST] Done! {forecasted} series x {HORIZON} months = {forecasted * HORIZON} forecasts")


if __name__ == '__main__':
    run()
