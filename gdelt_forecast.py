#!/usr/bin/env python3
"""
GDELT FORECAST ENGINE v6.0 - Hybrid: statsmodels + N-HiTS
Primary: statsmodels ExponentialSmoothing (always available)
Optional: N-HiTS deep learning (if neuralforecast installed)
Blend: 0.55*statsmodels + 0.45*N-HiTS when both available
"""
import os, sys, datetime, warnings
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

INPUT_FILE   = './indices.csv'
OUTPUT_PREDS = './predictions.csv'
OUTPUT_TRENDS = './forecast_trends.csv'
HORIZON      = 12
MIN_MONTHS   = 4
BLEND_SM     = 0.55
BLEND_NF     = 0.45


def load_monthly(filepath):
    print(f"[DATA] Loading {filepath}")
    raw = pd.read_csv(filepath, index_col=[0, 1])
    date_cols = [c for c in raw.columns if str(c).isdigit() and len(str(c)) == 8]
    if not date_cols:
        raise ValueError("No YYYYMMDD columns found")
    raw = raw[date_cols]
    print(f"[DATA] {len(raw):,} series x {len(date_cols):,} days")

    df = raw.reset_index()
    df.columns = ['topic', 'country'] + date_cols
    long = df.melt(id_vars=['topic', 'country'], var_name='date_str', value_name='value')
    long['ds'] = pd.to_datetime(long['date_str'], format='%Y%m%d', errors='coerce')
    long = long.dropna(subset=['ds'])
    long['ym'] = long['ds'].dt.to_period('M')

    monthly = (long.groupby(['topic', 'country', 'ym'])['value']
               .quantile(0.90).reset_index())
    monthly['ds'] = monthly['ym'].dt.to_timestamp()
    monthly['unique_id'] = monthly['topic'] + '||' + monthly['country']
    monthly = monthly.rename(columns={'value': 'y'})
    monthly = (monthly[['unique_id', 'ds', 'y', 'topic', 'country']]
               .sort_values(['unique_id', 'ds']).reset_index(drop=True))

    counts = monthly.dropna(subset=['y']).groupby('unique_id')['y'].count()
    valid_ids = counts[counts >= MIN_MONTHS].index
    monthly = monthly[monthly['unique_id'].isin(valid_ids)].copy()

    zero_ratio = monthly.groupby('unique_id')['y'].apply(
        lambda s: (s == 0).sum() / max(len(s), 1))
    active_ids = zero_ratio[zero_ratio <= 0.85].index
    monthly = monthly[monthly['unique_id'].isin(active_ids)].copy()

    print(f"[DATA] {monthly['unique_id'].nunique():,} active series")
    return monthly


# Ã¢ÂÂÃ¢ÂÂ TIER 1: statsmodels (always available) Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

def forecast_series_sm(y_values, h=HORIZON):
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    y = np.array(y_values, dtype=float)
    y = np.clip(y, 0, None)
    n = len(y)

    if n < 3:
        last = y[-1] if n > 0 else 0
        return np.full(h, last), np.full(h, last*0.7), np.full(h, last*1.3)

    fc = None
    resid = None

    # Try seasonal ETS first (24+ months)
    if n >= 24:
        try:
            model = ExponentialSmoothing(
                y, trend='add', damped_trend=True,
                seasonal='add', seasonal_periods=12,
                initialization_method='estimated')
            fit = model.fit(optimized=True, use_brute=True)
            fc = np.clip(fit.forecast(h), 0, None)
            resid = y - fit.fittedvalues
        except Exception:
            fc = None

    # Fall back to non-seasonal ETS
    if fc is None:
        try:
            model = ExponentialSmoothing(
                y, trend='add', damped_trend=True,
                seasonal=None,
                initialization_method='estimated')
            fit = model.fit(optimized=True, use_brute=True)
            fc = np.clip(fit.forecast(h), 0, None)
            resid = y - fit.fittedvalues
        except Exception:
            return forecast_series_numpy(y, h)

    # Check if forecast lacks month-to-month variation
    fc_mean = np.mean(fc) if np.mean(fc) > 1e-9 else 1e-9
    fc_std = np.std(fc)
    cv = fc_std / abs(fc_mean) if abs(fc_mean) > 1e-9 else 0

    if cv < 0.03:  # Coefficient of variation < 3% = too flat
        # 1. Compute trend from recent history
        lookback = min(n, 12)
        recent = y[-lookback:]
        x_hist = np.arange(lookback)
        slope, _ = np.polyfit(x_hist, recent, deg=1)

        # 2. Extract monthly seasonal pattern from historical data
        # Detrend the full series, then compute avg deviation per month position
        x_full = np.arange(n)
        trend_coef = np.polyfit(x_full, y, deg=1)
        detrended = y - np.polyval(trend_coef, x_full)

        cycle_len = min(n, 12)
        seasonal = np.zeros(cycle_len)
        counts = np.zeros(cycle_len)
        for i in range(n):
            pos = i % cycle_len
            seasonal[pos] += detrended[i]
            counts[pos] += 1
        seasonal = seasonal / np.maximum(counts, 1)
        seasonal = seasonal - np.mean(seasonal)  # center

        # 3. Build forecast: ETS level + damped trend + seasonal pattern
        base = fc[0]
        phi = 0.95
        cumulative = 0.0
        for k in range(h):
            cumulative += slope * (phi ** (k + 1))
            season_k = seasonal[(n + k) % cycle_len]
            fc[k] = max(base + cumulative + season_k, 0)

    sigma = max(np.std(resid) if resid is not None else fc_mean * 0.1,
                fc_mean * 0.05, 0.01)
    steps = np.arange(1, h + 1)
    lo = np.clip(fc - 1.645 * sigma * np.sqrt(steps), 0, None)
    hi = fc + 1.645 * sigma * np.sqrt(steps)

    return fc, lo, hi

def forecast_series_numpy(y_values, h=HORIZON):
    y = np.array(y_values, dtype=float)
    y = np.clip(y, 0, None)
    n = len(y)

    if n < 2:
        last = y[-1] if n > 0 else 0
        return np.full(h, last), np.full(h, last*0.7), np.full(h, last*1.3)

    # Linear trend
    x = np.arange(n)
    slope, intercept = np.polyfit(x, y, deg=1)

    # Extract seasonal pattern from detrended data
    detrended = y - (intercept + slope * x)
    cycle_len = min(n, 12)
    seasonal = np.zeros(cycle_len)
    counts = np.zeros(cycle_len)
    for i in range(n):
        pos = i % cycle_len
        seasonal[pos] += detrended[i]
        counts[pos] += 1
    seasonal = seasonal / np.maximum(counts, 1)
    seasonal = seasonal - np.mean(seasonal)

    # Build forecast: damped trend + seasonal
    phi = 0.90
    fc = []
    for k in range(1, h + 1):
        damped = slope * phi * (1 - phi**k) / (1 - phi)
        season_k = seasonal[(n + k - 1) % cycle_len]
        fc.append(max(intercept + slope * (n - 1) + damped + season_k, 0))
    fc = np.array(fc)

    resid = y - (intercept + slope * x)
    sigma = max(np.std(resid), np.mean(np.abs(y)) * 0.05, 0.01)
    steps = np.arange(1, h + 1)
    lo = np.clip(fc - 1.645 * sigma * np.sqrt(steps), 0, None)
    hi = fc + 1.645 * sigma * np.sqrt(steps)

    return fc, lo, hi

def forecast_statsmodels(monthly, horizon=HORIZON):
    print(f"[SM] Forecasting {monthly['unique_id'].nunique():,} series with ExponentialSmoothing ...")
    rows = []
    total = monthly['unique_id'].nunique()
    done = 0
    for uid, grp in monthly.sort_values('ds').groupby('unique_id'):
        y = grp['y'].fillna(0).values
        last_ds = grp['ds'].max()
        try:
            yhat, lo, hi = forecast_series_sm(y, horizon)
        except Exception:
            yhat, lo, hi = forecast_series_numpy(y, horizon)
        for k in range(horizon):
            ds_k = last_ds + pd.DateOffset(months=k + 1)
            rows.append({'unique_id': uid, 'ds': ds_k.replace(day=1),
                         'yhat': float(yhat[k]), 'yhat_lower': float(lo[k]),
                         'yhat_upper': float(hi[k])})
        done += 1
        if done % 200 == 0:
            print(f"  [{done}/{total}] ...")
    print(f"[SM] Done. {len(rows):,} forecast rows.")
    return pd.DataFrame(rows)


# Ã¢ÂÂÃ¢ÂÂ TIER 2: N-HiTS (optional deep learning) Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

def forecast_nhits(monthly, horizon=HORIZON):
    try:
        import torch
        os.environ['CUDA_VISIBLE_DEVICES'] = ''
        from neuralforecast import NeuralForecast
        from neuralforecast.models import NHITS

        train = monthly[['unique_id', 'ds', 'y']].copy()
        n_uid = train['unique_id'].nunique()
        print(f"[NF] Training N-HiTS on {n_uid:,} series (max_steps=1500) ...")

        model = NHITS(
            h=horizon, input_size=max(12, horizon),
            max_steps=1500, learning_rate=3e-4, batch_size=32,
            n_freq_downsample=[4, 2, 1],
            stack_types=['identity', 'identity', 'identity'],
            n_blocks=[2, 2, 1],
            mlp_units=[[128, 128], [128, 128], [128, 128]],
            dropout_prob_theta=0.1, scaler_type='robust',
            val_check_steps=100, early_stop_patience_steps=5,
            accelerator='cpu', random_seed=42, verbose=False,
        )
        nf = NeuralForecast(models=[model], freq='MS')
        nf.fit(train)
        preds = nf.predict().reset_index()

        nhits_col = [c for c in preds.columns
                     if 'NHITS' in str(c) and 'lo' not in c and 'hi' not in c]
        if not nhits_col:
            print(f"[NF] Unexpected columns: {preds.columns.tolist()}")
            return None
        preds = preds.rename(columns={nhits_col[0]: 'yhat_nf'})
        preds['yhat_nf'] = preds['yhat_nf'].clip(lower=0)

        # Validate: check N-HiTS output isn't garbage (row-index correlated)
        if len(preds) > 100:
            corr = abs(np.corrcoef(np.arange(len(preds)), preds['yhat_nf'].values)[0, 1])
            if corr > 0.90:
                print(f"[NF] WARNING: Output correlates with row index (r={corr:.3f}) - discarding")
                return None

        # Residual-based uncertainty
        global_sigma = preds['yhat_nf'].mean() * 0.15
        preds['yhat_lower_nf'] = (preds['yhat_nf'] - 1.645 * global_sigma).clip(lower=0)
        preds['yhat_upper_nf'] = preds['yhat_nf'] + 1.645 * global_sigma

        print(f"[NF] Done. {len(preds):,} forecast rows.")
        return preds[['unique_id', 'ds', 'yhat_nf', 'yhat_lower_nf', 'yhat_upper_nf']]

    except Exception as exc:
        print(f"[NF] N-HiTS failed ({type(exc).__name__}: {exc}) - skipping")
        return None


# Ã¢ÂÂÃ¢ÂÂ BLEND Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

def blend(sm_fc, nf_fc, w_sm=BLEND_SM, w_nf=BLEND_NF):
    merged = sm_fc.merge(nf_fc, on=['unique_id', 'ds'], how='left')
    have_nf = merged['yhat_nf'].notna()
    merged['yhat'] = np.where(
        have_nf,
        w_sm * merged['yhat'] + w_nf * merged['yhat_nf'],
        merged['yhat'])
    merged['yhat_lower'] = np.where(
        have_nf,
        np.minimum(merged['yhat_lower'], merged['yhat_lower_nf']),
        merged['yhat_lower'])
    merged['yhat_upper'] = np.where(
        have_nf,
        np.maximum(merged['yhat_upper'], merged['yhat_upper_nf']),
        merged['yhat_upper'])
    n_blended = have_nf.sum()
    print(f"[BLEND] {n_blended:,}/{len(merged):,} rows blended "
          f"(SM*{w_sm} + NF*{w_nf})")
    return merged[['unique_id', 'ds', 'yhat', 'yhat_lower', 'yhat_upper']]


# Ã¢ÂÂÃ¢ÂÂ MAIN Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

def run():
    t0 = datetime.datetime.utcnow()
    print("=" * 60)
    print("GDELT FORECAST ENGINE v6.0 - Hybrid")
    print(f"Run: {t0.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print("=" * 60)

    if not os.path.exists(INPUT_FILE):
        print(f"[!] {INPUT_FILE} not found.")
        sys.exit(1)

    monthly = load_monthly(INPUT_FILE)
    if len(monthly) == 0:
        print("[!] No valid series.")
        sys.exit(1)

    # Tier 1: statsmodels (always runs)
    sm_fc = forecast_statsmodels(monthly, HORIZON)

    # Tier 2: N-HiTS (optional)
    HAVE_NF = False
    try:
        import neuralforecast, torch
        HAVE_NF = True
        print(f"[FORECAST] N-HiTS available (torch {torch.__version__})")
    except ImportError:
        print("[FORECAST] neuralforecast not installed - SM only")

    nf_fc = None
    if HAVE_NF:
        nf_fc = forecast_nhits(monthly, HORIZON)

    # Combine
    if nf_fc is not None:
        forecasts = blend(sm_fc, nf_fc)
        model_label = f"Hybrid (SM*{BLEND_SM} + N-HiTS*{BLEND_NF})"
    else:
        forecasts = sm_fc
        model_label = "ExponentialSmoothing (statsmodels)"

    # Map topic/country
    uid_map = monthly[['unique_id', 'topic', 'country']].drop_duplicates().set_index('unique_id')
    forecasts['topic'] = forecasts['unique_id'].map(uid_map['topic'])
    forecasts['country'] = forecasts['unique_id'].map(uid_map['country'])
    for col in ['yhat', 'yhat_lower', 'yhat_upper']:
        forecasts[col] = forecasts[col].clip(lower=0)

    # Final validation
    if len(forecasts) > 100:
        corr = abs(np.corrcoef(np.arange(len(forecasts)), forecasts['yhat'].values)[0, 1])
        if corr > 0.90:
            print(f"[!] WARNING: Final predictions still correlate with row index (r={corr:.3f})")

    # Trend metrics
    print("\n[TRENDS] Computing ...")
    last_obs = (monthly.sort_values('ds').groupby('unique_id')['y']
                .last().reset_index().rename(columns={'y': 'last_value'}))
    avg_fc = (forecasts.groupby('unique_id')['yhat'].mean()
              .reset_index().rename(columns={'yhat': 'avg_12m'}))
    m = last_obs.merge(avg_fc, on='unique_id', how='inner')
    m['trend_pct'] = ((m['avg_12m'] - m['last_value'])
                      / m['last_value'].abs().clip(lower=0.1) * 100).clip(-200, 200)

    def direction(row):
        if row['trend_pct'] > 5: return 'rising'
        if row['trend_pct'] < -5: return 'falling'
        return 'stable'

    m['direction'] = m.apply(direction, axis=1)
    _uid = monthly[['unique_id', 'topic', 'country']].drop_duplicates().set_index('unique_id')
    m['topic'] = m['unique_id'].map(_uid['topic'])
    m['country'] = m['unique_id'].map(_uid['country'])
    trends = m[['topic', 'country', 'last_value', 'avg_12m', 'trend_pct', 'direction']]

    # Save
    out = forecasts[['topic', 'country', 'ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    out.to_csv(OUTPUT_PREDS, index=False)
    trends.to_csv(OUTPUT_TRENDS, index=False)

    elapsed = (datetime.datetime.utcnow() - t0).seconds
    n_series = out[['topic', 'country']].drop_duplicates().shape[0]
    print(f"\n{'=' * 60}")
    print(f"Done ({elapsed}s) | {model_label}")
    print(f"{len(out):,} rows ({n_series:,} series x {HORIZON} months)")
    print("=" * 60)

    rising = trends[trends['direction'] == 'rising'].nlargest(5, 'trend_pct')
    falling = trends[trends['direction'] == 'falling'].nsmallest(5, 'trend_pct')
    print("\nTOP 5 RISING:")
    for _, r in rising.iterrows():
        print(f"  {r['topic']:<36} {r['country']} +{r['trend_pct']:.1f}%")
    print("\nTOP 5 FALLING:")
    for _, r in falling.iterrows():
        print(f"  {r['topic']:<36} {r['country']} {r['trend_pct']:.1f}%")


if __name__ == '__main__':
    run()
