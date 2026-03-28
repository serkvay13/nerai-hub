#!/usr/bin/env python3
"""
GDELT FORECAST ENGINE v2.0  —  Deep Learning Time-Series Predictions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Model  : N-HiTS (Neural Hierarchical Interpolation for Time Series)
         – AAAI 2023 paper, global multi-series neural forecasting
         – Fallback: AutoARIMA (statsforecast) if neuralforecast unavailable

Improvements in v2.0:
  - Monthly aggregation: 90th percentile (not mean) — captures risk extremes
  - Tuned N-HiTS for monthly seasonality: 36-month input, 3 freq. scales
  - Dual-threshold trend detection: % AND absolute change required
  - Heteroscedastic confidence intervals: wider during high-volatility periods
  - Sparse series filtering: removes near-all-zero series pre-training
  - More robust calibration: robust scaler, 2000 training steps, early stopping

Input  : ./indices.csv        (daily topic×country GDELT indices)
Output : ./predictions.csv    (12-month-ahead forecasts per topic×country)
         ./forecast_trends.csv (trend summary: rising / stable / falling)

Install:
  pip install neuralforecast statsforecast pandas numpy

Usage:
  python gdelt_forecast.py
  python gdelt_forecast.py --horizon 6    # shorter horizon
  python gdelt_forecast.py --min-months 12
"""

import os
import sys
import datetime
import argparse
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

# ─── CONFIG ───────────────────────────────────────────────────
INPUT_FILE        = './indices.csv'
OUTPUT_PREDS      = './predictions.csv'
OUTPUT_TRENDS     = './forecast_trends.csv'

HORIZON           = 12    # months ahead to forecast
INPUT_SIZE        = 36    # months of lookback for the model (at least 3 full annual cycles)
MIN_MONTHS        = 18    # minimum historical months required per series

MONTHLY_AGG       = 'p90'   # 'mean' | 'p90' | 'max'  — aggregation method for daily→monthly


# ═══════════════════════════════════════════════════════════════
# 1.  DATA LOADING & MONTHLY AGGREGATION
# ═══════════════════════════════════════════════════════════════

def load_and_aggregate_monthly(filepath: str) -> pd.DataFrame:
    """
    Read indices.csv  →  long-format monthly data.

    indices.csv layout:
      rows   : MultiIndex (topic, country)
      columns: YYYYMMDD strings (daily observations)

    Returns DataFrame with columns:
      unique_id, ds (monthly timestamp), y, topic, country
    """
    print(f"\n[1] LOADING DATA")
    print(f"    File: {filepath}")

    df = pd.read_csv(filepath, index_col=[0, 1])

    # Keep only valid date columns (8-digit strings like 20230115)
    date_cols = [c for c in df.columns
                 if str(c).isdigit() and len(str(c)) == 8]
    df = df[date_cols]

    n_series = len(df)
    n_days   = len(date_cols)
    print(f"    {n_series:,} series  ×  {n_days:,} daily observations "
          f"({date_cols[0]} → {date_cols[-1]})")

    # --- Melt to long format ---
    df_reset = df.reset_index()
    df_reset.columns = ['topic', 'country'] + date_cols
    df_long = df_reset.melt(
        id_vars=['topic', 'country'],
        var_name='date_str', value_name='value'
    )

    # Parse dates
    df_long['ds'] = pd.to_datetime(df_long['date_str'], format='%Y%m%d')
    df_long['ym'] = df_long['ds'].dt.to_period('M')

    # Monthly aggregation (configurable: mean, p90, or max)
    # For risk indices, the 90th percentile is more informative than the mean:
    # a single extreme day in a month signals elevated risk better than the average.
    agg_dispatch = {
        'mean': lambda g: g.mean(),
        'p90':  lambda g: g.quantile(0.90),
        'max':  lambda g: g.max(),
    }
    agg_func = agg_dispatch.get(MONTHLY_AGG, agg_dispatch['p90'])

    monthly = (
        df_long
        .groupby(['topic', 'country', 'ym'])['value']
        .apply(agg_func)
        .reset_index()
    )
    monthly['ds']        = monthly['ym'].dt.to_timestamp()
    monthly['unique_id'] = monthly['topic'] + '||' + monthly['country']
    monthly              = monthly.rename(columns={'value': 'y'})
    monthly              = (monthly[['unique_id', 'ds', 'y', 'topic', 'country']]
                            .sort_values(['unique_id', 'ds'])
                            .reset_index(drop=True))

    n_months = monthly['ym'].nunique()
    n_uid    = monthly['unique_id'].nunique()
    print(f"    Monthly aggregation: {n_months} months  ×  {n_uid:,} series")
    return monthly


def filter_valid_series(monthly: pd.DataFrame,
                        min_months: int = MIN_MONTHS) -> pd.DataFrame:
    """Drop series that have fewer than min_months non-NaN observations."""
    counts    = monthly.dropna(subset=['y']).groupby('unique_id')['y'].count()
    valid_ids = counts[counts >= min_months].index
    filtered  = monthly[monthly['unique_id'].isin(valid_ids)].copy()

    n_total = monthly['unique_id'].nunique()
    n_valid = len(valid_ids)
    print(f"    Valid series (≥ {min_months} months): {n_valid:,} / {n_total:,}")
    return filtered


def filter_sparse_series(monthly: pd.DataFrame,
                         max_zero_ratio: float = 0.80) -> pd.DataFrame:
    """
    Remove series where more than max_zero_ratio of values are zero.
    Sparse series (e.g., mass_killing in Iceland) produce meaningless
    near-zero forecasts and pollute the global model training.
    """
    def zero_ratio(group):
        return (group['y'] == 0).sum() / len(group)

    ratios = monthly.groupby('unique_id').apply(zero_ratio)
    valid  = ratios[ratios <= max_zero_ratio].index
    filtered = monthly[monthly['unique_id'].isin(valid)].copy()

    n_dropped = monthly['unique_id'].nunique() - len(valid)
    print(f"    Sparse series dropped (>{max_zero_ratio*100:.0f}% zeros): {n_dropped:,}")
    print(f"    Active series remaining: {len(valid):,}")
    return filtered


# ═══════════════════════════════════════════════════════════════
# 2.  N-HiTS  (primary — deep learning)
# ═══════════════════════════════════════════════════════════════

def forecast_nhits(monthly: pd.DataFrame,
                   horizon: int = HORIZON,
                   input_size: int = INPUT_SIZE) -> tuple:
    """
    Global N-HiTS model trained on ALL 2,400 series simultaneously.
    Returns (forecasts_df, model_name_str).
    """
    from neuralforecast import NeuralForecast
    from neuralforecast.models import NHITS

    print(f"\n[2] TRAINING N-HiTS  (Deep Learning — Global Model)")
    print(f"    Horizon    : {horizon} months")
    print(f"    Input size : {input_size} months")
    print(f"    Series     : {monthly['unique_id'].nunique():,}")

    train_df = monthly[['unique_id', 'ds', 'y']].copy()

    model = NHITS(
        h                   = horizon,
        input_size          = max(input_size, 36),   # at least 3 full annual cycles
        max_steps           = 2000,                   # more steps for better convergence
        learning_rate       = 3e-4,
        batch_size          = 64,
        # Monthly seasonality stack: annual → quarterly → monthly
        n_freq_downsample   = [4, 2, 1],
        stack_types         = ['identity', 'identity', 'identity'],
        n_blocks            = [2, 2, 1],
        mlp_units           = [[512, 512], [512, 512], [256, 256]],
        dropout_prob_theta  = 0.2,
        scaler_type         = 'robust',              # robust to outliers vs 'standard'
        val_check_steps     = 200,
        early_stop_patience_steps = 10,
        random_seed         = 42,
        verbose             = False,
    )

    nf = NeuralForecast(models=[model], freq='MS')
    nf.fit(train_df)

    print(f"    Generating {horizon}-month forecasts ...")
    preds = nf.predict().reset_index()

    # Column produced by neuralforecast is called 'NHITS'
    nhits_col = [c for c in preds.columns if 'NHITS' in str(c)]
    if not nhits_col:
        raise ValueError(f"Unexpected NeuralForecast columns: {preds.columns.tolist()}")
    preds = preds.rename(columns={nhits_col[0]: 'yhat'})
    preds = preds[['unique_id', 'ds', 'yhat']]

    # Heteroscedastic confidence intervals via rolling variance
    # Produces wider intervals during high-volatility periods
    try:
        insample = nf.predict_insample(step_size=1).reset_index()
        res_col  = [c for c in insample.columns if 'NHITS' in str(c)]
        if res_col and 'y' in insample.columns:
            insample['resid'] = (insample['y'] - insample[res_col[0]]).abs()
            # Rolling 3-month std for heteroscedastic sigma
            insample = insample.sort_values(['unique_id', 'ds'])
            insample['rolling_sigma'] = (
                insample.groupby('unique_id')['resid']
                .transform(lambda x: x.rolling(3, min_periods=1).std())
            )
            # Take the last (most recent) rolling sigma per series as forecast uncertainty base
            recent_sigma = insample.groupby('unique_id')['rolling_sigma'].last()
            # Add a horizon-scaling factor: uncertainty grows with forecast distance
            preds = preds.merge(recent_sigma.rename('base_sigma'), on='unique_id', how='left')
            preds['horizon_pos'] = preds.groupby('unique_id').cumcount() + 1
            preds['sigma'] = preds['base_sigma'] * (1 + 0.05 * preds['horizon_pos'])
            preds = preds.drop(columns=['base_sigma', 'horizon_pos'])
        else:
            preds['sigma'] = np.nan
    except Exception:
        preds['sigma'] = np.nan

    # Fill missing sigma with 20 % of mean yhat
    global_sigma = preds['yhat'].mean() * 0.20
    preds['sigma'] = preds['sigma'].fillna(global_sigma).clip(lower=1e-6)

    preds['yhat_lower'] = (preds['yhat'] - 1.645 * preds['sigma']).clip(lower=0)
    preds['yhat_upper'] =  preds['yhat'] + 1.645 * preds['sigma']
    preds = preds.drop(columns='sigma')

    return preds, 'N-HiTS (Deep Learning)'


# ═══════════════════════════════════════════════════════════════
# 3.  AutoARIMA  (fallback — statistical ML)
# ═══════════════════════════════════════════════════════════════

def forecast_arima(monthly: pd.DataFrame,
                   horizon: int = HORIZON) -> tuple:
    """AutoARIMA fallback via statsforecast. Fast and robust."""
    from statsforecast import StatsForecast
    from statsforecast.models import AutoARIMA

    print(f"\n[2] TRAINING AutoARIMA  (Statistical ML — Fallback)")
    print(f"    Horizon : {horizon} months")
    print(f"    Series  : {monthly['unique_id'].nunique():,}")

    train_df = monthly[['unique_id', 'ds', 'y']].copy()

    sf = StatsForecast(
        models  = [AutoARIMA(season_length=12, approximation=True)],
        freq    = 'MS',
        n_jobs  = -1,
    )
    fc = sf.forecast(df=train_df, h=horizon, level=[90]).reset_index()

    # Rename statsforecast output columns
    col_map = {
        'AutoARIMA'       : 'yhat',
        'AutoARIMA-lo-90' : 'yhat_lower',
        'AutoARIMA-hi-90' : 'yhat_upper',
    }
    fc = fc.rename(columns=col_map)
    fc['yhat_lower'] = fc['yhat_lower'].clip(lower=0)

    return fc[['unique_id', 'ds', 'yhat', 'yhat_lower', 'yhat_upper']], \
           'AutoARIMA (Statistical)'


def run_forecast(monthly: pd.DataFrame,
                 horizon: int = HORIZON) -> tuple:
    """Try N-HiTS; fall back to AutoARIMA; raise if neither is installed."""
    try:
        import neuralforecast  # noqa: F401
        return forecast_nhits(monthly, horizon)
    except ImportError:
        print("    [!] neuralforecast not installed — trying AutoARIMA fallback")
    try:
        import statsforecast  # noqa: F401
        return forecast_arima(monthly, horizon)
    except ImportError:
        raise RuntimeError(
            "No forecasting library found.\n"
            "Install one of:\n"
            "  pip install neuralforecast          # deep learning (recommended)\n"
            "  pip install statsforecast           # statistical fallback\n"
        )


# ═══════════════════════════════════════════════════════════════
# 4.  TREND METRICS
# ═══════════════════════════════════════════════════════════════

def compute_trend_metrics(monthly: pd.DataFrame,
                          forecasts: pd.DataFrame) -> pd.DataFrame:
    """
    For each (topic, country) series compute summary metrics:
      last_value  – most recent monthly observed value
      avg_12m     – mean of the 12-month forecast
      trend_pct   – % change: (avg_12m − last_value) / |last_value|
      direction   – 'rising' | 'stable' | 'falling'

    Direction classification requires BOTH percentage AND absolute change to avoid
    false signals on near-zero series (e.g., a series with value 0.0001 doubling to
    0.0002 shows a large %, but the absolute movement is negligible).
    """
    last_obs = (
        monthly.sort_values('ds')
               .groupby('unique_id')['y']
               .last()
               .reset_index()
               .rename(columns={'y': 'last_value'})
    )

    avg_fc = (
        forecasts.groupby('unique_id')['yhat']
                 .mean()
                 .reset_index()
                 .rename(columns={'yhat': 'avg_12m'})
    )

    metrics = last_obs.merge(avg_fc, on='unique_id', how='inner')
    metrics['trend_pct'] = (
        (metrics['avg_12m'] - metrics['last_value'])
        / (metrics['last_value'].abs() + 1e-9) * 100
    )

    # Absolute change threshold: avoids false signals on near-zero series
    abs_threshold = 0.0005   # minimum meaningful absolute movement

    def classify_direction(row):
        pct_ok = abs(row['trend_pct']) > 10
        abs_ok = abs(row['avg_12m'] - row['last_value']) > abs_threshold
        if row['trend_pct'] > 10  and abs_ok:
            return 'rising'
        if row['trend_pct'] < -10 and abs_ok:
            return 'falling'
        return 'stable'

    metrics['direction'] = metrics.apply(classify_direction, axis=1)

    metrics[['topic', 'country']] = (
        metrics['unique_id'].str.split('||', expand=True)
    )
    return metrics[['topic', 'country',
                    'last_value', 'avg_12m', 'trend_pct', 'direction']]


# ═══════════════════════════════════════════════════════════════
# 5.  MAIN
# ═══════════════════════════════════════════════════════════════

def main(horizon: int = HORIZON, min_months: int = MIN_MONTHS):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    print("=" * 60)
    print("GDELT FORECAST ENGINE v2.0")
    print(f"12-Month Risk Predictions  ·  {now}")
    print("=" * 60)

    # ── 1. Load & aggregate ──────────────────────────────────
    if not os.path.exists(INPUT_FILE):
        print(f"\n[!] {INPUT_FILE} not found.")
        print("    Run gdelt_indices.py or gdelt_bulk_history.py first.")
        sys.exit(1)

    monthly = load_and_aggregate_monthly(INPUT_FILE)
    monthly = filter_valid_series(monthly, min_months)
    monthly = filter_sparse_series(monthly)   # Remove near-all-zero series

    if len(monthly) == 0:
        print(f"\n[!] No series with ≥ {min_months} months of data.")
        print("    Download more history with gdelt_bulk_history.py.")
        sys.exit(1)

    # ── 2. Train & forecast ──────────────────────────────────
    forecasts, model_name = run_forecast(monthly, horizon)

    # ── 3. Parse unique_id → topic + country ─────────────────
    forecasts[['topic', 'country']] = (
        forecasts['unique_id'].str.split('||', expand=True)
    )
    forecasts['yhat']       = forecasts['yhat'].clip(lower=0)
    forecasts['yhat_lower'] = forecasts['yhat_lower'].clip(lower=0)
    forecasts['yhat_upper'] = forecasts['yhat_upper'].clip(lower=0)

    # ── 4. Trend metrics ─────────────────────────────────────
    print("\n[3] COMPUTING TREND METRICS")
    metrics = compute_trend_metrics(monthly, forecasts)

    # ── 5. Save ───────────────────────────────────────────────
    result = forecasts[['topic', 'country', 'ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    result.to_csv(OUTPUT_PREDS,  index=False)
    metrics.to_csv(OUTPUT_TRENDS, index=False)

    # ── 6. Summary ────────────────────────────────────────────
    n_series = result[['topic', 'country']].drop_duplicates().shape[0]
    print(f"\n{'=' * 60}")
    print(f"✓  Forecasting complete!")
    print(f"   Model      : {model_name}")
    print(f"   Predictions: {len(result):,} rows  ({n_series:,} series × {horizon} months)")
    print(f"   Saved to   : {OUTPUT_PREDS}")
    print(f"   Trends     : {OUTPUT_TRENDS}")
    print("=" * 60)

    # Top movers
    print("\n🔺  TOP 5 RISING RISKS  (next 12 months):")
    for _, r in metrics.nlargest(5, 'trend_pct').iterrows():
        print(f"   {r['topic']:<38} {r['country']}  +{r['trend_pct']:.1f}%")

    print("\n🔻  TOP 5 FALLING RISKS:")
    for _, r in metrics.nsmallest(5, 'trend_pct').iterrows():
        print(f"   {r['topic']:<38} {r['country']}  {r['trend_pct']:.1f}%")
    print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Train N-HiTS and generate 12-month GDELT risk forecasts')
    parser.add_argument(
        '--horizon', type=int, default=HORIZON,
        help=f'Forecast horizon in months (default: {HORIZON})')
    parser.add_argument(
        '--min-months', type=int, default=MIN_MONTHS,
        help=f'Minimum historical months per series (default: {MIN_MONTHS})')
    args = parser.parse_args()

    main(horizon=args.horizon, min_months=args.min_months)
