#!/usr/bin/env python3
"""
GDELT FORECAST ENGINE v3.1  --  High-Quality Statistical Forecasting
=====================================================================

Models  : AutoARIMA + AutoETS ensemble (via statsforecast)
          - AutoARIMA: gold-standard ARIMA with automatic order selection
          - AutoETS: Exponential Smoothing with automatic model selection
          - Ensemble: simple average of both models
          - Winner of M3, M4, M5 international forecasting competitions

Why statsforecast over neuralforecast:
  - 100x faster (Cython/C++ backend, no PyTorch)
  - Better accuracy on monthly macroeconomic series (proven by research)
  - Reliable on any CI runner (no GPU, no memory constraints)
  - Proper prediction intervals via maximum likelihood estimation

Input  : ./indices.csv        (daily topic x country GDELT indices)
Output : ./predictions.csv    (12-month-ahead forecasts per topic x country)
         ./forecast_trends.csv (trend summary: rising / stable / falling)
"""

import sys
import warnings
import pandas as pd
import numpy as np
from datetime import datetime

warnings.filterwarnings('ignore')

# ── Try importing statsforecast ───────────────────────────────────────────────
try:
    from statsforecast import StatsForecast
    from statsforecast.models import AutoARIMA, AutoETS, AutoTheta
    HAVE_STATSFORECAST = True
    print("[FORECAST] Using statsforecast (AutoARIMA + AutoETS + AutoTheta ensemble)")
except ImportError:
    HAVE_STATSFORECAST = False
    print("[FORECAST] statsforecast not available -- using built-in Holt-Winters")

# ── Constants ─────────────────────────────────────────────────────────────────
INPUT_CSV     = 'indices.csv'
OUTPUT_PREDS  = 'predictions.csv'
OUTPUT_TRENDS = 'forecast_trends.csv'
HORIZON       = 12      # months ahead
MIN_MONTHS    = 18      # minimum history required
CONF_LEVEL    = 95


# ── Fallback: built-in damped Holt-Winters ────────────────────────────────────
def _holt_winters_fallback(series: np.ndarray, horizon: int):
    n = len(series)
    if n < 2:
        v = float(series[-1]) if n else 0.0
        yhat = np.full(horizon, v)
        err  = abs(v) * 0.2 + 0.01
        return yhat, yhat - err, yhat + err

    alpha, beta, phi = 0.35, 0.12, 0.92
    level = series[0]
    trend = (series[min(2, n-1)] - series[0]) / max(1, min(2, n-1))
    levels, trends = [level], [trend]

    for t in range(1, n):
        pl, pt = levels[-1], trends[-1]
        nl = alpha * series[t] + (1 - alpha) * (pl + phi * pt)
        nt = beta * (nl - pl) + (1 - beta) * phi * pt
        levels.append(nl); trends.append(nt)

    fitted = np.array([levels[t] + phi * trends[t] for t in range(n - 1)])
    residuals = series[1:] - fitted
    rmse = float(np.sqrt(np.mean(residuals ** 2))) + 0.001

    yhat = np.zeros(horizon); phi_h = 1.0; phi_cum = 0.0
    ll, lt = levels[-1], trends[-1]
    for h in range(1, horizon + 1):
        phi_cum += phi_h; phi_h *= phi
        yhat[h - 1] = ll + phi_cum * lt

    margin = 1.96 * rmse * np.sqrt(np.arange(1, horizon + 1))
    yhat   = np.maximum(yhat, 0)
    return yhat, np.maximum(yhat - margin, 0), yhat + margin


# ── Trend classification ───────────────────────────────────────────────────────
def classify_trend(current: float, forecasts: np.ndarray) -> str:
    if len(forecasts) == 0:
        return 'stable'
    mid6 = float(np.mean(forecasts[:6]))
    pct  = (mid6 - current) / (abs(current) + 1e-9)
    if   pct >  0.08: return 'rising'
    elif pct < -0.08: return 'falling'
    return 'stable'


# ── Main ───────────────────────────────────────────────────────────────────────
def run():
    print(f"[FORECAST] Starting at {datetime.utcnow().isoformat()}Z")

    # ── Load indices ─────────────────────────────────────────────────────────
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"[FORECAST] ERROR: {INPUT_CSV} not found.")
        sys.exit(1)

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    print(f"[FORECAST] Loaded {len(df):,} rows  ({df['date'].min().date()} to {df['date'].max().date()})")

    # ── Detect format & convert to long ──────────────────────────────────────
    cols = df.columns.tolist()
    if 'topic' in cols and 'country' in cols:
        val_col = [c for c in cols if c not in ('date','topic','country')][0]
        df_long = df[['date','topic','country',val_col]].copy()
        df_long.columns = ['date','topic','country','value']
    else:
        series_cols = [c for c in cols if c != 'date']
        df_long = df.melt(id_vars='date', value_vars=series_cols,
                          var_name='series', value_name='value')
        df_long['topic']   = df_long['series'].apply(lambda x: '_'.join(x.split('_')[:-1]))
        df_long['country'] = df_long['series'].apply(lambda x: x.split('_')[-1])
        df_long = df_long[['date','topic','country','value']]

    df_long['value'] = pd.to_numeric(df_long['value'], errors='coerce').fillna(0)

    # ── Monthly aggregation (75th percentile -- captures risk spikes) ─────────
    df_long['month'] = df_long['date'].dt.to_period('M')
    monthly = (df_long.groupby(['month','topic','country'])['value']
               .quantile(0.75).reset_index())
    monthly['ds'] = monthly['month'].dt.to_timestamp()
    monthly = monthly.sort_values('ds').rename(columns={'value': 'y'})

    # Future dates for predictions
    last_month   = monthly['ds'].max()
    future_dates = pd.date_range(
        start=last_month + pd.offsets.MonthBegin(1),
        periods=HORIZON, freq='MS'
    )

    series_list = monthly[['topic','country']].drop_duplicates()
    print(f"[FORECAST] {len(series_list):,} unique series  |  horizon = {HORIZON} months")

    pred_rows  = []
    trend_rows = []
    forecasted = 0
    skipped    = 0

    # ════════════════════════════════════════════════════════════════════════════
    if HAVE_STATSFORECAST:
        # ── statsforecast batch forecasting ─────────────────────────────────
        # Build panel dataframe: unique_id = "topic|country"
        monthly['unique_id'] = monthly['topic'] + '|' + monthly['country']

        # Filter series with enough history
        counts = monthly.groupby('unique_id')['ds'].count()
        valid_ids = counts[counts >= MIN_MONTHS].index
        panel = monthly[monthly['unique_id'].isin(valid_ids)][['unique_id','ds','y']].copy()
        panel = panel.sort_values(['unique_id','ds'])

        print(f"[FORECAST] Forecasting {len(valid_ids):,} series with statsforecast...")
        skipped = len(series_list) - len(valid_ids)

        models = [
            AutoARIMA(season_length=12, approximation=True, stepwise=True),
            AutoETS(season_length=12, damped=True),
            AutoTheta(season_length=12),
        ]

        sf = StatsForecast(models=models, freq='MS', n_jobs=-1, fallback_model=AutoETS(season_length=12))

        try:
            fcst = sf.forecast(df=panel, h=HORIZON, level=[CONF_LEVEL])
        except Exception as e:
            print(f"[FORECAST] statsforecast error: {e} -- falling back to Holt-Winters")
            HAVE_STATSFORECAST_RUNTIME = False
        else:
            HAVE_STATSFORECAST_RUNTIME = True

        if HAVE_STATSFORECAST_RUNTIME:
            # Ensemble: average of all model yhats
            model_names = [type(m).__name__ for m in models]
            yhat_cols   = [c for c in fcst.columns if c in model_names or
                           any(c.startswith(mn) for mn in model_names
                               if not c.endswith('-lo-95') and not c.endswith('-hi-95'))]

            # Build output
            for uid, grp in fcst.groupby('unique_id'):
                topic, country = uid.split('|', 1)
                grp = grp.sort_values('ds').reset_index(drop=True)

                # Ensemble yhat (mean of all model predictions)
                yhat_arr = np.array([grp[mn].values for mn in model_names
                                     if mn in grp.columns]).mean(axis=0)

                # CI: use widest available (most conservative)
                lo_cols = [c for c in grp.columns if 'lo' in c and '95' in c]
                hi_cols = [c for c in grp.columns if 'hi' in c and '95' in c]
                if lo_cols and hi_cols:
                    lower = np.array([grp[c].values for c in lo_cols]).min(axis=0)
                    upper = np.array([grp[c].values for c in hi_cols]).max(axis=0)
                else:
                    rmse  = float(np.std(yhat_arr)) + 0.01
                    margin = 1.96 * rmse * np.sqrt(np.arange(1, HORIZON+1))
                    lower = np.maximum(yhat_arr - margin, 0)
                    upper = yhat_arr + margin

                yhat_arr = np.maximum(yhat_arr, 0)
                lower    = np.maximum(lower, 0)

                for i, dt in enumerate(grp['ds'].values):
                    pred_rows.append({
                        'date':       str(dt)[:10],
                        'topic':      topic,
                        'country':    country,
                        'yhat':       round(float(yhat_arr[i]), 4),
                        'yhat_lower': round(float(lower[i]), 4),
                        'yhat_upper': round(float(upper[i]), 4),
                    })

                # Trend
                hist_mask = (monthly['topic'] == topic) & (monthly['country'] == country)
                hist_vals = monthly[hist_mask].sort_values('ds')['y'].values
                current   = float(hist_vals[-1]) if len(hist_vals) > 0 else 0.0
                trend     = classify_trend(current, yhat_arr)
                pct_chg   = (float(np.mean(yhat_arr[:6])) - current) / (abs(current) + 1e-9)
                trend_rows.append({
                    'topic':         topic,
                    'country':       country,
                    'trend':         trend,
                    'current_value': round(current, 4),
                    'forecast_6m':   round(float(np.mean(yhat_arr[:6])), 4),
                    'pct_change_6m': round(pct_chg * 100, 2),
                    'model':         'AutoARIMA+AutoETS+AutoTheta ensemble',
                })
                forecasted += 1

    # ════════════════════════════════════════════════════════════════════════════
    if not HAVE_STATSFORECAST or forecasted == 0:
        # ── Fallback: series-by-series Holt-Winters ──────────────────────────
        print("[FORECAST] Using built-in Holt-Winters fallback...")
        for _, row in series_list.iterrows():
            topic, country = row['topic'], row['country']
            mask   = (monthly['topic'] == topic) & (monthly['country'] == country)
            series = monthly[mask].sort_values('ds')['y'].values
            if len(series) < MIN_MONTHS:
                skipped += 1; continue
            try:
                yhat, lower, upper = _holt_winters_fallback(series, HORIZON)
            except Exception:
                skipped += 1; continue

            for i, dt in enumerate(future_dates):
                pred_rows.append({
                    'date':       dt.strftime('%Y-%m-%d'),
                    'topic':      topic, 'country': country,
                    'yhat':       round(float(yhat[i]), 4),
                    'yhat_lower': round(float(lower[i]), 4),
                    'yhat_upper': round(float(upper[i]), 4),
                })

            current = float(series[-1])
            trend   = classify_trend(current, yhat)
            pct_chg = (float(np.mean(yhat[:6])) - current) / (abs(current) + 1e-9)
            trend_rows.append({
                'topic':         topic,    'country':       country,
                'trend':         trend,    'current_value': round(current, 4),
                'forecast_6m':   round(float(np.mean(yhat[:6])), 4),
                'pct_change_6m': round(pct_chg * 100, 2),
                'model':         'Holt-Winters damped trend',
            })
            forecasted += 1

    # ── Save ──────────────────────────────────────────────────────────────────
    print(f"[FORECAST] Forecasted: {forecasted}  Skipped (too short): {skipped}")
    if forecasted == 0:
        print("[FORECAST] No series forecasted. Exiting.")
        sys.exit(1)

    pd.DataFrame(pred_rows).to_csv(OUTPUT_PREDS, index=False)
    pd.DataFrame(trend_rows).to_csv(OUTPUT_TRENDS, index=False)
    print(f"[FORECAST] Saved {len(pred_rows):,} rows to {OUTPUT_PREDS}")
    print(f"[FORECAST] Saved {len(trend_rows):,} rows to {OUTPUT_TRENDS}")
    print(f"[FORECAST] Complete: {forecasted} x {HORIZON} = {forecasted*HORIZON} forecasts")


if __name__ == '__main__':
    run()
