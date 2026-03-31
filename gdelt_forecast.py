#!/usr/bin/env python3
"""
GDELT FORECAST ENGINE v4.0  --  Best-Quality Hybrid Forecasting
===============================================================

Strategy: always try the best available model tier, never fail silently.

Tier 1 (BEST): neuralforecast N-HiTS on CPU
  - Deep learning, neural hierarchical interpolation
  - Best for capturing complex non-linear patterns
  - Used when available AND enough memory

Tier 2 (EXCELLENT): statsforecast 3-model ensemble
  - AutoARIMA + AutoETS + AutoTheta combination
  - Won M3/M4/M5 international forecasting competitions
  - Statistically proven on monthly macroeconomic data
  - Always reliable, no GPU/memory constraints

Tier 3 (FALLBACK): built-in Holt-Winters
  - Pure numpy, zero dependencies
  - Only used if both above fail

Blending: if both Tier 1 + Tier 2 produce results,
  final = 0.45 * N-HiTS + 0.55 * statsforecast ensemble
  (statsforecast gets higher weight for monthly macro series
   per M4 competition findings)

Input  : ./indices.csv
Output : ./predictions.csv   (date, topic, country, yhat, yhat_lower, yhat_upper)
         ./forecast_trends.csv (topic, country, trend, current_value, forecast_6m, ...)
"""

import os, sys, warnings, gc
import pandas as pd
import numpy as np
from datetime import datetime

warnings.filterwarnings('ignore')

INPUT_CSV     = 'indices.csv'
OUTPUT_PREDS  = 'predictions.csv'
OUTPUT_TRENDS = 'forecast_trends.csv'
HORIZON       = 12
MIN_MONTHS    = 18
CONF_LEVEL    = 95

# ─── Tier detection ───────────────────────────────────────────────────────────
HAVE_NF = False
HAVE_SF = False

try:
    from statsforecast import StatsForecast
    from statsforecast.models import AutoARIMA, AutoETS, AutoTheta
    HAVE_SF = True
    print("[FORECAST] Tier 2 available: statsforecast (AutoARIMA + AutoETS + AutoTheta)")
except ImportError:
    print("[FORECAST] statsforecast not installed")

try:
    import torch
    from neuralforecast import NeuralForecast
    from neuralforecast.models import NHITS
    HAVE_NF = True
    print(f"[FORECAST] Tier 1 available: neuralforecast N-HiTS (torch {torch.__version__})")
    # Check available memory -- skip NF if < 3GB free
    try:
        import psutil
        free_gb = psutil.virtual_memory().available / 1e9
        print(f"[FORECAST]   Available RAM: {free_gb:.1f} GB")
        if free_gb < 3.0:
            HAVE_NF = False
            print("[FORECAST]   Insufficient RAM for N-HiTS -- using statsforecast only")
    except ImportError:
        pass  # psutil not available, try anyway
except ImportError:
    print("[FORECAST] neuralforecast not installed")


# ─── Data loading ─────────────────────────────────────────────────────────────
def load_monthly():
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"[FORECAST] ERROR: {INPUT_CSV} not found.")
        sys.exit(1)

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    print(f"[FORECAST] Loaded {len(df):,} rows ({df['date'].min().date()} to {df['date'].max().date()})")

    cols = df.columns.tolist()
    if 'topic' in cols and 'country' in cols:
        val = [c for c in cols if c not in ('date','topic','country')][0]
        df_long = df[['date','topic','country',val]].copy()
        df_long.columns = ['date','topic','country','value']
    else:
        series_cols = [c for c in cols if c != 'date']
        df_long = df.melt(id_vars='date', value_vars=series_cols,
                          var_name='series', value_name='value')
        df_long['topic']   = df_long['series'].apply(lambda x: '_'.join(x.split('_')[:-1]))
        df_long['country'] = df_long['series'].apply(lambda x: x.split('_')[-1])
        df_long = df_long[['date','topic','country','value']]

    df_long['value'] = pd.to_numeric(df_long['value'], errors='coerce').fillna(0)
    df_long['month'] = df_long['date'].dt.to_period('M')

    monthly = (df_long.groupby(['month','topic','country'])['value']
               .quantile(0.75).reset_index())
    monthly['ds'] = monthly['month'].dt.to_timestamp()
    monthly = monthly.sort_values('ds').rename(columns={'value': 'y'})
    monthly['unique_id'] = monthly['topic'] + '|' + monthly['country']
    return monthly


# ─── Tier 2: statsforecast ensemble ──────────────────────────────────────────
def forecast_statsforecast(panel: pd.DataFrame, horizon: int):
    print("[FORECAST] Running Tier 2: AutoARIMA + AutoETS + AutoTheta ensemble...")
    sf = StatsForecast(
        models=[
            AutoARIMA(season_length=12, approximation=True, stepwise=True, nmodels=20),
            AutoETS(season_length=12, damped=True),
            AutoTheta(season_length=12, decomposition_type='multiplicative'),
        ],
        freq='MS', n_jobs=-1,
        fallback_model=AutoETS(season_length=12)
    )
    fcst = sf.forecast(df=panel, h=horizon, level=[CONF_LEVEL])
    return fcst


# ─── Tier 1: neuralforecast N-HiTS ────────────────────────────────────────────
def forecast_nhits(panel: pd.DataFrame, horizon: int):
    print("[FORECAST] Running Tier 1: N-HiTS deep learning (CPU mode)...")
    nf = NeuralForecast(
        models=[NHITS(
            h=horizon,
            input_size=min(36, max(24, int(len(panel) / len(panel['unique_id'].unique()) * 0.6))),
            max_steps=300,          # reduced from 2000 for CI stability
            batch_size=32,
            n_freq_downsample=[2, 1, 1],
            mlp_units=[[128, 128], [128, 128], [128, 128]],  # smaller than default
            accelerator='cpu',
            enable_progress_bar=False,
            enable_model_summary=False,
        )],
        freq='MS'
    )
    nf.fit(panel)
    fcst = nf.predict()
    # Add confidence intervals using 1.5x std of residuals as proxy
    nf_yhat = fcst['NHITS'].values
    nf_std  = float(np.std(panel.groupby('unique_id')['y'].apply(lambda s: s.diff().dropna()).values.flatten())) + 0.01
    fcst['NHITS-lo-95'] = np.maximum(nf_yhat - 1.96 * nf_std * np.sqrt(np.tile(np.arange(1,horizon+1), len(fcst)//horizon + 1)[:len(nf_yhat)]), 0)
    fcst['NHITS-hi-95'] = nf_yhat + 1.96 * nf_std * np.sqrt(np.tile(np.arange(1,horizon+1), len(fcst)//horizon + 1)[:len(nf_yhat)])
    return fcst


# ─── Holt-Winters fallback ────────────────────────────────────────────────────
def _hw_single(y, h):
    n = len(y)
    if n < 2:
        v = float(y[-1]) if n else 0.0
        err = abs(v)*0.2+0.01
        yh = np.full(h, v)
        return yh, yh-err, yh+err
    alpha, beta, phi = 0.35, 0.12, 0.92
    l, t = y[0], (y[min(2,n-1)] - y[0]) / max(1, min(2,n-1))
    ls, ts = [l], [t]
    for v in y[1:]:
        nl = alpha*v + (1-alpha)*(ls[-1]+phi*ts[-1])
        nt = beta*(nl-ls[-1]) + (1-beta)*phi*ts[-1]
        ls.append(nl); ts.append(nt)
    fitted = np.array([ls[i]+phi*ts[i] for i in range(n-1)])
    rmse = float(np.sqrt(np.mean((y[1:]-fitted)**2)))+0.001
    yh = np.zeros(h); pc = 0.0; ph = 1.0
    for i in range(h):
        pc += ph; ph *= phi
        yh[i] = ls[-1] + pc*ts[-1]
    m = 1.96*rmse*np.sqrt(np.arange(1,h+1))
    yh = np.maximum(yh,0)
    return yh, np.maximum(yh-m,0), yh+m


# ─── Trend classification ─────────────────────────────────────────────────────
def classify_trend(current, yhat6):
    pct = (float(np.mean(yhat6)) - current) / (abs(current)+1e-9)
    if pct > 0.08:  return 'rising'
    if pct < -0.08: return 'falling'
    return 'stable'


# ─── Build output rows from forecast df ──────────────────────────────────────
def fcst_to_rows(fcst_df, model_col, lo_col, hi_col, monthly):
    pred_rows, trend_rows = [], []
    for uid, grp in fcst_df.groupby('unique_id'):
        topic, country = uid.split('|', 1)
        grp = grp.sort_values('ds').reset_index(drop=True)
        yhat  = np.maximum(grp[model_col].values.astype(float), 0)
        lower = np.maximum(grp[lo_col].values.astype(float), 0)  if lo_col in grp else np.maximum(yhat-1,0)
        upper = grp[hi_col].values.astype(float) if hi_col in grp else yhat+1

        for i, row in grp.iterrows():
            pred_rows.append({
                'date': str(row['ds'])[:10], 'topic': topic, 'country': country,
                'yhat': round(float(yhat[i]),4), 'yhat_lower': round(float(lower[i]),4),
                'yhat_upper': round(float(upper[i]),4),
            })

        hist = monthly[(monthly['topic']==topic) & (monthly['country']==country)].sort_values('ds')['y'].values
        current = float(hist[-1]) if len(hist) else 0.0
        trend   = classify_trend(current, yhat[:6])
        pct_chg = (float(np.mean(yhat[:6])) - current) / (abs(current)+1e-9)
        trend_rows.append({
            'topic': topic, 'country': country, 'trend': trend,
            'current_value': round(current,4),
            'forecast_6m':   round(float(np.mean(yhat[:6])),4),
            'pct_change_6m': round(pct_chg*100,2),
        })
    return pred_rows, trend_rows


# ─── Main ────────────────────────────────────────────────────────────────────
def run():
    print(f"[FORECAST] Starting v4.0 at {datetime.utcnow().isoformat()}Z")
    monthly = load_monthly()

    # Filter series with enough history
    counts  = monthly.groupby('unique_id')['ds'].count()
    valid   = counts[counts >= MIN_MONTHS].index
    panel   = monthly[monthly['unique_id'].isin(valid)][['unique_id','ds','y']].copy()
    skipped = len(counts) - len(valid)
    print(f"[FORECAST] Valid series: {len(valid)}  Skipped (< {MIN_MONTHS} months): {skipped}")

    if len(valid) == 0:
        print("[FORECAST] No valid series. Exiting.")
        sys.exit(1)

    last_month   = monthly['ds'].max()
    future_dates = pd.date_range(start=last_month+pd.offsets.MonthBegin(1), periods=HORIZON, freq='MS')

    sf_fcst = None
    nf_fcst = None

    # ── Tier 2: statsforecast (always try first as primary) ──────────────────
    if HAVE_SF:
        try:
            sf_fcst = forecast_statsforecast(panel, HORIZON)
            print(f"[FORECAST] statsforecast complete: {len(sf_fcst)} rows")
        except Exception as e:
            print(f"[FORECAST] statsforecast failed: {e}")
            sf_fcst = None

    # ── Tier 1: neuralforecast N-HiTS (enhancer) ─────────────────────────────
    if HAVE_NF and sf_fcst is not None:
        try:
            nf_fcst = forecast_nhits(panel, HORIZON)
            print(f"[FORECAST] N-HiTS complete: {len(nf_fcst)} rows")
        except Exception as e:
            print(f"[FORECAST] N-HiTS failed (non-fatal): {e}")
            nf_fcst = None
        finally:
            gc.collect()  # free torch memory

    # ── Build final predictions ───────────────────────────────────────────────
    pred_rows, trend_rows = [], []

    if sf_fcst is not None and nf_fcst is not None:
        # BLEND: 55% statsforecast + 45% N-HiTS
        print("[FORECAST] Blending statsforecast + N-HiTS (55% / 45%)")
        merged = sf_fcst.merge(nf_fcst[['unique_id','ds','NHITS','NHITS-lo-95','NHITS-hi-95']],
                               on=['unique_id','ds'], how='left')
        # statsforecast ensemble yhat
        sf_cols = ['AutoARIMA','AutoETS','AutoTheta']
        avail_sf = [c for c in sf_cols if c in merged.columns]
        sf_yhat  = merged[avail_sf].mean(axis=1).values
        nf_yhat  = merged['NHITS'].values
        blend_yhat = np.where(nf_yhat.isna() if hasattr(nf_yhat,'isna') else np.isnan(nf_yhat),
                              sf_yhat, 0.55*sf_yhat + 0.45*nf_yhat)

        # CI: take widest from both models for conservative estimate
        lo_sf = merged[[c for c in merged.columns if 'lo' in c and '95' in c and 'NHITS' not in c]].min(axis=1).values
        hi_sf = merged[[c for c in merged.columns if 'hi' in c and '95' in c and 'NHITS' not in c]].max(axis=1).values
        lo_nf = merged.get('NHITS-lo-95', pd.Series(lo_sf)).values
        hi_nf = merged.get('NHITS-hi-95', pd.Series(hi_sf)).values
        blend_lo = np.minimum(lo_sf, lo_nf)
        blend_hi = np.maximum(hi_sf, hi_nf)

        merged['yhat_blend'] = np.maximum(blend_yhat, 0)
        merged['lo_blend']   = np.maximum(blend_lo, 0)
        merged['hi_blend']   = blend_hi
        pred_rows, trend_rows = fcst_to_rows(merged, 'yhat_blend', 'lo_blend', 'hi_blend', monthly)

    elif sf_fcst is not None:
        # statsforecast only
        print("[FORECAST] Using statsforecast ensemble only")
        sf_cols = ['AutoARIMA','AutoETS','AutoTheta']
        avail   = [c for c in sf_cols if c in sf_fcst.columns]
        sf_fcst['yhat_ens'] = sf_fcst[avail].mean(axis=1)
        lo_col = next((c for c in sf_fcst.columns if 'lo' in c and '95' in c), None)
        hi_col = next((c for c in sf_fcst.columns if 'hi' in c and '95' in c), None)
        pred_rows, trend_rows = fcst_to_rows(sf_fcst, 'yhat_ens', lo_col or 'yhat_ens', hi_col or 'yhat_ens', monthly)

    else:
        # Tier 3: Holt-Winters fallback
        print("[FORECAST] Using built-in Holt-Winters fallback")
        for uid, grp in panel.groupby('unique_id'):
            topic, country = uid.split('|',1)
            y = grp.sort_values('ds')['y'].values
            yh, lo, hi = _hw_single(y, HORIZON)
            for i, dt in enumerate(future_dates):
                pred_rows.append({'date': dt.strftime('%Y-%m-%d'), 'topic': topic, 'country': country,
                                  'yhat': round(float(yh[i]),4), 'yhat_lower': round(float(lo[i]),4),
                                  'yhat_upper': round(float(hi[i]),4)})
            current = float(y[-1])
            pct = (float(np.mean(yh[:6]))-current)/(abs(current)+1e-9)
            trend_rows.append({'topic': topic, 'country': country,
                               'trend': classify_trend(current, yh[:6]),
                               'current_value': round(current,4),
                               'forecast_6m': round(float(np.mean(yh[:6])),4),
                               'pct_change_6m': round(pct*100,2)})

    if not pred_rows:
        print("[FORECAST] No predictions generated. Exiting.")
        sys.exit(1)

    pd.DataFrame(pred_rows).to_csv(OUTPUT_PREDS, index=False)
    pd.DataFrame(trend_rows).to_csv(OUTPUT_TRENDS, index=False)
    n = len(pd.DataFrame(pred_rows)[['topic','country']].drop_duplicates())
    print(f"[FORECAST] Saved {len(pred_rows):,} rows ({n} series x {HORIZON} months)")
    print(f"[FORECAST] Trend summary: {pd.DataFrame(trend_rows)['trend'].value_counts().to_dict()}")
    print(f"[FORECAST] DONE.")


if __name__ == '__main__':
    run()
