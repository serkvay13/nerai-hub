#!/usr/bin/env python3
"""
GDELT FORECAST ENGINE v5.0  â  Hybrid Deep Learning + Statistical Ensemble
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

Architecture (3 tiers, graceful degradation):

  Tier 1  â N-HiTS (Deep Learning, global model)
              neuralforecast Â· AAAI 2023 Â· trains on ALL series simultaneously
              CPU mode Â· max_steps=500 Â· batch_size=32 (GitHub Actions safe)

  Tier 2  â Statistical Ensemble  (always runs)
              AutoARIMA + AutoETS(damped) + AutoTheta  via statsforecast
              M4/M5 competition winners Â· fully parallelised Â· n_jobs=-1

  Blend   â When both succeed: 0.55 Ã StatEnsemble + 0.45 Ã N-HiTS
              Confidence intervals: take the wider (more conservative) bound

  Tier 3  â Built-in Holt-Winters  (pure numpy, zero dependencies)
              Runs only if BOTH libraries are absent

Input  : ./indices.csv        (wide format: rows=topicÃcountry, cols=YYYYMMDD)
Output : ./predictions.csv    (date, topic, country, yhat, yhat_lower, yhat_upper)
         ./forecast_trends.csv (topic, country, last_value, avg_12m, trend_pct, direction)
"""

import os
import sys
import datetime
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

# âââ CONFIG âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
INPUT_FILE   = './indices.csv'
OUTPUT_PREDS = './predictions.csv'
OUTPUT_TRENDS= './forecast_trends.csv'
HORIZON      = 12    # months ahead to forecast
INPUT_SIZE   = 6    # months of lookback (â¥3 annual cycles)
MIN_MONTHS   = 6    # minimum history required per series
BLEND_SF     = 0.55  # statsforecast weight in blend
BLEND_NF     = 0.45  # neuralforecast weight in blend


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# 1.  DATA LOADING
#     indices.csv layout:
#       row index cols 0,1 : topic, country
#       remaining columns   : YYYYMMDD date strings  (daily observations)
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def load_monthly(filepath: str = INPUT_FILE,
                 agg: str = 'p90',
                 min_months: int = MIN_MONTHS) -> pd.DataFrame:
    """
    Read wide-format indices.csv â long-format monthly DataFrame.

    Returns: unique_id, ds (month-start timestamp), y, topic, country
    """
    print(f"[DATA]  Loading {filepath}")
    raw = pd.read_csv(filepath, index_col=[0, 1])

    # Keep only 8-digit YYYYMMDD columns
    date_cols = [c for c in raw.columns
                 if str(c).isdigit() and len(str(c)) == 8]
    if not date_cols:
        raise ValueError(
            f"No YYYYMMDD columns found in {filepath}. "
            f"Sample columns: {list(raw.columns[:5])}"
        )

    raw = raw[date_cols]
    print(f"[DATA]  {len(raw):,} series  Ã  {len(date_cols):,} days "
          f"({date_cols[0]} â {date_cols[-1]})")

    # Melt to long format
    df = raw.reset_index()
    df.columns = ['topic', 'country'] + date_cols
    long = df.melt(id_vars=['topic', 'country'],
                   var_name='date_str', value_name='value')

    long['ds'] = pd.to_datetime(long['date_str'], format='%Y%m%d',
                                errors='coerce')
    long = long.dropna(subset=['ds'])
    long['ym'] = long['ds'].dt.to_period('M')

    # Monthly aggregation
    agg_fn = {
        'p90' : lambda x: x.quantile(0.90),
        'mean': lambda x: x.mean(),
        'max' : lambda x: x.max(),
    }.get(agg, lambda x: x.quantile(0.90))

    monthly = (
        long.groupby(['topic', 'country', 'ym'])['value']
            .apply(agg_fn)
            .reset_index()
    )
    monthly['ds']        = monthly['ym'].dt.to_timestamp()
    monthly['unique_id'] = monthly['topic'] + '||' + monthly['country']
    monthly              = monthly.rename(columns={'value': 'y'})
    monthly              = (monthly[['unique_id', 'ds', 'y', 'topic', 'country']]
                            .sort_values(['unique_id', 'ds'])
                            .reset_index(drop=True))

    # Filter: minimum history
    counts    = monthly.dropna(subset=['y']).groupby('unique_id')['y'].count()
    valid_ids = counts[counts >= min_months].index
    monthly   = monthly[monthly['unique_id'].isin(valid_ids)].copy()

    # Filter: sparse series (>80% zeros carry no signal)
    zero_ratio = monthly.groupby('unique_id')['y'].apply(
        lambda s: (s == 0).sum() / len(s)
    )
    active_ids = zero_ratio[zero_ratio <= 0.80].index
    dropped    = len(valid_ids) - len(active_ids)
    monthly    = monthly[monthly['unique_id'].isin(active_ids)].copy()

    n_uid = monthly['unique_id'].nunique()
    print(f"[DATA]  {n_uid:,} active series  "
          f"({dropped:,} sparse dropped, {len(counts)-len(valid_ids):,} short dropped)")
    return monthly


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# 2.  TIER 2 â STATISTICAL ENSEMBLE  (always-on backbone)
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def forecast_statsforecast(monthly: pd.DataFrame,
                           horizon: int = HORIZON) -> pd.DataFrame:
    """
    AutoARIMA + AutoETS(damped) + AutoTheta ensemble.
    Simple mean blend of the three models' point forecasts.
    Confidence intervals from the average of all three.
    """
    from statsforecast import StatsForecast
    from statsforecast.models import AutoARIMA, AutoETS, AutoTheta

    train = monthly[['unique_id', 'ds', 'y']].copy()
    n_uid = train['unique_id'].nunique()
    print(f"[SF]    Training AutoARIMA + AutoETS + AutoTheta on {n_uid:,} series ...")

    models = [
        AutoARIMA(season_length=12, approximation=True),
        AutoETS(season_length=12, damped=True),
        AutoTheta(season_length=12),
    ]
    sf = StatsForecast(models=models, freq='MS', n_jobs=-1, verbose=False)
    fc = sf.forecast(df=train, h=horizon, level=[90]).reset_index()

    # Columns: unique_id, ds, AutoARIMA, AutoARIMA-lo-90, AutoARIMA-hi-90,
    #          AutoETS, AutoETS-lo-90, AutoETS-hi-90, AutoTheta, AutoTheta-lo-90, AutoTheta-hi-90
    point_cols = [c for c in fc.columns
                  if c not in ('unique_id', 'ds')
                  and '-lo-' not in c and '-hi-' not in c]
    lo_cols    = [c for c in fc.columns if '-lo-90' in c]
    hi_cols    = [c for c in fc.columns if '-hi-90' in c]

    fc['yhat']       = fc[point_cols].mean(axis=1).clip(lower=0)
    fc['yhat_lower'] = fc[lo_cols].mean(axis=1).clip(lower=0) if lo_cols else fc['yhat'] * 0.8
    fc['yhat_upper'] = fc[hi_cols].mean(axis=1).clip(lower=0) if hi_cols else fc['yhat'] * 1.2

    print(f"[SF]    Done. {len(fc):,} forecast rows.")
    return fc[['unique_id', 'ds', 'yhat', 'yhat_lower', 'yhat_upper']]


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# 3.  TIER 1 â N-HiTS  (deep learning enhancer, CPU mode)
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def forecast_nhits(monthly: pd.DataFrame,
                   horizon: int = HORIZON,
                   input_size: int = INPUT_SIZE) -> pd.DataFrame | None:
    """
    Global N-HiTS model trained on all series simultaneously.
    CPU mode with conservative settings for GitHub Actions compatibility.
    Returns None on any failure (caller falls back to SF only).
    """
    try:
        import torch
        # Force CPU â avoids CUDA OOM on shared runners
        os.environ['CUDA_VISIBLE_DEVICES'] = ''

        from neuralforecast import NeuralForecast
        from neuralforecast.models import NHITS

        train = monthly[['unique_id', 'ds', 'y']].copy()
        n_uid = train['unique_id'].nunique()
        print(f"[NF]    Training N-HiTS (CPU) on {n_uid:,} series ...")
        print(f"        torch {torch.__version__} Â· max_steps=500 Â· batch_size=32")

        model = NHITS(
            h                         = horizon,
            input_size                = max(input_size, horizon),
            max_steps                 = 500,
            learning_rate             = 3e-4,
            batch_size                = 32,
            n_freq_downsample         = [4, 2, 1],
            stack_types               = ['identity', 'identity', 'identity'],
            n_blocks                  = [2, 2, 1],
            mlp_units                 = [[128, 128], [128, 128], [128, 128]],
            dropout_prob_theta        = 0.1,
            scaler_type               = 'robust',
            val_check_steps           = 50,
            early_stop_patience_steps = 5,
            accelerator               = 'cpu',
            random_seed               = 42,
            verbose                   = False,
        )

        nf = NeuralForecast(models=[model], freq='MS')
        nf.fit(train)
        preds = nf.predict().reset_index()

        nhits_col = [c for c in preds.columns if 'NHITS' in str(c) and 'lo' not in c and 'hi' not in c]
        if not nhits_col:
            print(f"[NF]    Unexpected columns: {preds.columns.tolist()}")
            return None

        preds = preds.rename(columns={nhits_col[0]: 'yhat_nf'})
        preds['yhat_nf'] = preds['yhat_nf'].clip(lower=0)

        # Build uncertainty: residual-based heteroscedastic sigma
        try:
            insample = nf.predict_insample(step_size=1).reset_index()
            res_col  = [c for c in insample.columns if 'NHITS' in str(c)]
            if res_col and 'y' in insample.columns:
                insample['resid'] = (insample['y'] - insample[res_col[0]]).abs()
                insample = insample.sort_values(['unique_id', 'ds'])
                insample['sigma'] = insample.groupby('unique_id')['resid'].transform(
                    lambda x: x.rolling(3, min_periods=1).std()
                )
                recent_sigma = insample.groupby('unique_id')['sigma'].last()
                preds = preds.merge(recent_sigma.rename('base_sigma'),
                                    on='unique_id', how='left')
                preds['horizon_pos'] = preds.groupby('unique_id').cumcount() + 1
                preds['sigma_nf']    = (preds['base_sigma']
                                        * (1 + 0.05 * preds['horizon_pos']))
                preds = preds.drop(columns=['base_sigma', 'horizon_pos'])
            else:
                preds['sigma_nf'] = np.nan
        except Exception:
            preds['sigma_nf'] = np.nan

        global_sigma = preds['yhat_nf'].mean() * 0.20
        preds['sigma_nf'] = preds['sigma_nf'].fillna(global_sigma).clip(lower=1e-6)

        preds['yhat_lower_nf'] = (preds['yhat_nf'] - 1.645 * preds['sigma_nf']).clip(lower=0)
        preds['yhat_upper_nf'] =  preds['yhat_nf'] + 1.645 * preds['sigma_nf']
        preds = preds.drop(columns='sigma_nf')

        print(f"[NF]    Done. {len(preds):,} forecast rows.")
        return preds[['unique_id', 'ds', 'yhat_nf', 'yhat_lower_nf', 'yhat_upper_nf']]

    except Exception as exc:
        print(f"[NF]    N-HiTS failed ({type(exc).__name__}: {exc}) â skipping")
        return None


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# 4.  TIER 3 â HOLT-WINTERS  (pure numpy, zero-dependency fallback)
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def holt_winters_forecast(series: np.ndarray, h: int,
                          alpha: float = 0.35,
                          beta:  float = 0.12,
                          phi:   float = 0.92) -> tuple:
    """Damped Holt-Winters. Returns (point, lower_90, upper_90)."""
    n = len(series)
    if n == 0:
        return np.zeros(h), np.zeros(h), np.zeros(h)

    L = float(series[0])
    T = float(series[1] - series[0]) if n > 1 else 0.0
    residuals = []

    for i in range(1, n):
        L_prev, T_prev = L, T
        L = alpha * series[i] + (1 - alpha) * (L_prev + phi * T_prev)
        T = beta  * (L - L_prev) + (1 - beta) * phi * T_prev
        residuals.append(series[i] - (L_prev + phi * T_prev))

    sigma = np.std(residuals) if residuals else abs(L) * 0.10

    forecasts, lower, upper = [], [], []
    phi_acc = phi
    for k in range(1, h + 1):
        f = L + phi_acc * T
        se = sigma * np.sqrt(k)
        forecasts.append(max(f, 0))
        lower.append(max(f - 1.645 * se, 0))
        upper.append(max(f + 1.645 * se, 0))
        phi_acc += phi ** (k + 1)

    return np.array(forecasts), np.array(lower), np.array(upper)


def forecast_holtwinters(monthly: pd.DataFrame,
                         horizon: int = HORIZON) -> pd.DataFrame:
    """Apply Holt-Winters to every series. Pure Python, no dependencies."""
    print(f"[HW]    Running Holt-Winters on {monthly['unique_id'].nunique():,} series ...")
    rows = []
    for uid, grp in monthly.sort_values('ds').groupby('unique_id'):
        y = grp['y'].fillna(0).values
        if len(y) < 3:
            continue
        last_ds  = grp['ds'].max()
        yhat, lo, hi = holt_winters_forecast(y, horizon)
        for k in range(horizon):
            ds_k = last_ds + pd.DateOffset(months=k + 1)
            rows.append({'unique_id': uid,
                         'ds': ds_k.replace(day=1),
                         'yhat': yhat[k],
                         'yhat_lower': lo[k],
                         'yhat_upper': hi[k]})
    print(f"[HW]    Done. {len(rows):,} rows.")
    return pd.DataFrame(rows)


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# 5.  BLEND
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def blend(sf_fc: pd.DataFrame, nf_fc: pd.DataFrame,
          w_sf: float = BLEND_SF, w_nf: float = BLEND_NF) -> pd.DataFrame:
    """
    Merge SF and NF forecasts; blend point estimates by weight.
    Confidence intervals: take the wider (conservative) bound.
    """
    merged = sf_fc.merge(nf_fc, on=['unique_id', 'ds'], how='left',
                         suffixes=('_sf', '_nf'))

    have_nf = merged['yhat_nf'].notna()

    # Point forecast
    merged['yhat'] = np.where(
        have_nf,
        w_sf * merged['yhat_sf'] + w_nf * merged['yhat_nf'],
        merged['yhat_sf']
    )
    # Lower: take the minimum (wider interval)
    merged['yhat_lower'] = np.where(
        have_nf,
        np.minimum(merged['yhat_lower_sf'], merged['yhat_lower_nf']),
        merged['yhat_lower_sf']
    )
    # Upper: take the maximum (wider interval)
    merged['yhat_upper'] = np.where(
        have_nf,
        np.maximum(merged['yhat_upper_sf'], merged['yhat_upper_nf']),
        merged['yhat_upper_sf']
    )

    n_blended = have_nf.sum()
    n_total   = len(merged)
    print(f"[BLEND] {n_blended:,}/{n_total:,} rows blended "
          f"(SFÃ{w_sf} + NFÃ{w_nf}); "
          f"{n_total-n_blended:,} rows SF-only")

    return merged[['unique_id', 'ds', 'yhat', 'yhat_lower', 'yhat_upper']]


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# 6.  TREND METRICS
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def compute_trends(monthly: pd.DataFrame,
                   forecasts: pd.DataFrame) -> pd.DataFrame:
    """
    last_value, avg_12m, trend_pct, direction for each (topic, country).
    Dual-threshold direction: requires >10% AND meaningful absolute change.
    """
    last_obs = (monthly.sort_values('ds')
                       .groupby('unique_id')['y'].last()
                       .reset_index().rename(columns={'y': 'last_value'}))

    avg_fc = (forecasts.groupby('unique_id')['yhat'].mean()
                       .reset_index().rename(columns={'yhat': 'avg_12m'}))

    m = last_obs.merge(avg_fc, on='unique_id', how='inner')
    m['trend_pct'] = (
        (m['avg_12m'] - m['last_value']) / (m['last_value'].abs() + 1e-9) * 100
    )

    ABS_THR = 0.0005

    def direction(row):
        abs_ok = abs(row['avg_12m'] - row['last_value']) > ABS_THR
        if row['trend_pct'] >  10 and abs_ok: return 'rising'
        if row['trend_pct'] < -10 and abs_ok: return 'falling'
        return 'stable'

    m['direction'] = m.apply(direction, axis=1)
    _uid = monthly[['unique_id', 'topic', 'country']].drop_duplicates().set_index('unique_id')
    m['topic']   = m['unique_id'].map(_uid['topic'])
    m['country'] = m['unique_id'].map(_uid['country'])
    return m[['topic', 'country', 'last_value', 'avg_12m', 'trend_pct', 'direction']]


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# 7.  MAIN
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def run():
    t0  = datetime.datetime.utcnow()
    now = t0.strftime('%Y-%m-%dT%H:%M:%SZ')
    print("=" * 60)
    print("GDELT FORECAST ENGINE v5.0  â  Hybrid Ensemble")
    print(f"Run started: {now}")
    print("=" * 60)

    # ââ Capability detection âââââââââââââââââââââââââââââââââââââ
    HAVE_SF = False
    HAVE_NF = False

    try:
        import statsforecast  # noqa
        HAVE_SF = True
        print(f"[FORECAST] Tier 2 available: statsforecast {statsforecast.__version__}")
    except ImportError:
        print("[FORECAST] statsforecast not installed")

    try:
        import neuralforecast  # noqa
        import torch           # noqa
        HAVE_NF = True
        print(f"[FORECAST] Tier 1 available: neuralforecast (torch {torch.__version__})")
    except ImportError:
        print("[FORECAST] neuralforecast/torch not installed")

    try:
        import psutil
        ram_gb = psutil.virtual_memory().available / 1e9
        print(f"[FORECAST] Available RAM: {ram_gb:.1f} GB")
        if ram_gb < 2.0:
            print("[FORECAST] Low RAM â disabling N-HiTS")
            HAVE_NF = False
    except ImportError:
        pass

    # ââ Load data ââââââââââââââââââââââââââââââââââââââââââââââââ
    if not os.path.exists(INPUT_FILE):
        print(f"[!] {INPUT_FILE} not found. Run gdelt_indices.py first.")
        sys.exit(1)

    monthly = load_monthly(INPUT_FILE)

    if len(monthly) == 0:
        print(f"[!] No series with â¥{MIN_MONTHS} months of data.")
        sys.exit(1)

    # ââ Forecast âââââââââââââââââââââââââââââââââââââââââââââââââ
    if HAVE_SF:
        sf_fc = forecast_statsforecast(monthly, HORIZON)
    elif not HAVE_NF:
        # Last resort: pure Holt-Winters
        print("[FORECAST] No libraries â using built-in Holt-Winters")
        sf_fc = forecast_holtwinters(monthly, HORIZON)
    else:
        sf_fc = None

    if HAVE_NF:
        nf_fc = forecast_nhits(monthly, HORIZON, INPUT_SIZE)
    else:
        nf_fc = None

    # ââ Combine ââââââââââââââââââââââââââââââââââââââââââââââââââ
    if sf_fc is not None and nf_fc is not None:
        print("[FORECAST] Blending SF ensemble + N-HiTS ...")
        forecasts = blend(sf_fc, nf_fc)
        model_label = f"Hybrid (SFÃ{BLEND_SF} + N-HiTSÃ{BLEND_NF})"
    elif sf_fc is not None:
        forecasts = sf_fc
        model_label = "Statistical Ensemble (AutoARIMA + AutoETS + AutoTheta)"
    elif nf_fc is not None:
        forecasts = nf_fc.rename(columns={
            'yhat_nf': 'yhat',
            'yhat_lower_nf': 'yhat_lower',
            'yhat_upper_nf': 'yhat_upper'
        })
        model_label = "N-HiTS (Deep Learning)"
    else:
        print("[FORECAST] All tiers failed â using Holt-Winters")
        forecasts = forecast_holtwinters(monthly, HORIZON)
        model_label = "Holt-Winters (fallback)"


    # ââ Parse unique_id ââââââââââââââââââââââââââââââââââââââââââ
    _uid_map = monthly[['unique_id', 'topic', 'country']].drop_duplicates().set_index('unique_id')
    forecasts['topic']   = forecasts['unique_id'].map(_uid_map['topic'])
    forecasts['country'] = forecasts['unique_id'].map(_uid_map['country'])
    for col in ['yhat', 'yhat_lower', 'yhat_upper']:
        forecasts[col] = forecasts[col].clip(lower=0)

    # ââ Trend metrics ââââââââââââââââââââââââââââââââââââââââââââ
    print("\n[TRENDS] Computing trend metrics ...")
    trends = compute_trends(monthly, forecasts)

    # ââ Save âââââââââââââââââââââââââââââââââââââââââââââââââââââ
    out = forecasts[['topic', 'country', 'ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    out.to_csv(OUTPUT_PREDS,  index=False)
    trends.to_csv(OUTPUT_TRENDS, index=False)

    # ââ Summary ââââââââââââââââââââââââââââââââââââââââââââââââââ
    elapsed = (datetime.datetime.utcnow() - t0).seconds
    n_series = out[['topic', 'country']].drop_duplicates().shape[0]

    print(f"\n{'=' * 60}")
    print(f"â  Forecasting complete  ({elapsed}s)")
    print(f"   Model      : {model_label}")
    print(f"   Predictions: {len(out):,} rows  ({n_series:,} series Ã {HORIZON} months)")
    print(f"   Saved to   : {OUTPUT_PREDS}")
    print(f"   Trends     : {OUTPUT_TRENDS}")
    print("=" * 60)

    rising  = trends[trends['direction'] == 'rising'].nlargest(5, 'trend_pct')
    falling = trends[trends['direction'] == 'falling'].nsmallest(5, 'trend_pct')

    print("\nðº  TOP 5 RISING RISKS (next 12 months):")
    for _, r in rising.iterrows():
        print(f"   {r['topic']:<36}  {r['country']}  +{r['trend_pct']:.1f}%")

    print("\nð»  TOP 5 FALLING RISKS:")
    for _, r in falling.iterrows():
        print(f"   {r['topic']:<36}  {r['country']}  {r['trend_pct']:.1f}%")
    print()


if __name__ == '__main__':
    run()
