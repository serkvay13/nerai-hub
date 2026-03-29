#!/usr/bin/env python3
"""
Granger Causality Analysis for GDELT Indices

Performs Granger causality testing across all (topic × country) pairs from indices.csv
and produces a causality network for consumption by the forecast engine and dashboard.
"""

import pandas as pd
import numpy as np
import warnings
import sys
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from statsmodels.tsa.stattools import grangercausalitytests
from scipy import stats

warnings.filterwarnings('ignore')

# Configuration
CONFIG = {
    'INPUT_FILE': './indices.csv',
    'OUTPUT_NETWORK': './causality_network.csv',
    'OUTPUT_STATS': './causality_stats.csv',
    'MONTHLY_AGG': 'p90',
    'MIN_MONTHS': 1,
    'MAX_ZERO_RATIO': 0.80,
    'MAX_LAG': 2,                   # reduced from 3 → 33% fewer tests per pair
    'P_VALUE_THRESHOLD': 0.10,  # relaxed 0.05→0.10: more relationships detected
    'CORRELATION_PREFILTER': 0.15,  # lowered: GDELT series have low cross-topic correlation
    'MAX_WORKERS': 4,
}


def load_and_aggregate(input_file):
    """
    Load indices.csv and aggregate daily data to monthly using p90.
    Handles both wide format (dates as columns) and long format (ds column).
    """
    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)

    if 'topic' not in df.columns or 'country' not in df.columns:
        raise ValueError("Input file must have 'topic' and 'country' columns")

    # Detect wide vs long format
    # Wide: date columns are numeric strings like '20260217'
    date_cols = [c for c in df.columns if c not in ('topic', 'country', 'ds', 'value', 'unique_id')
                 and str(c).isdigit() and len(str(c)) == 8]

    if date_cols:
        # Wide format → melt to long
        print(f"Detected wide format with {len(date_cols)} date columns. Converting to long format...")
        df = df.melt(
            id_vars=['topic', 'country'],
            value_vars=date_cols,
            var_name='ds',
            value_name='value'
        )

    # Ensure ds is datetime
    df['ds'] = pd.to_datetime(df['ds'].astype(str), format='%Y%m%d', errors='coerce')
    df = df.dropna(subset=['ds'])

    df['unique_id'] = df['topic'].astype(str) + '_' + df['country'].astype(str)

    # Aggregate to monthly using p90
    df['year_month'] = df['ds'].dt.to_period('M')

    agg_df = df.groupby(['year_month', 'unique_id', 'topic', 'country']).agg({
        'value': lambda x: x.quantile(0.90)
    }).reset_index()

    agg_df.rename(columns={'value': 'y'}, inplace=True)
    agg_df['ds'] = agg_df['year_month'].dt.to_timestamp()

    print(f"Aggregated to {len(agg_df['year_month'].unique())} months")
    print(f"Found {agg_df['unique_id'].nunique()} unique (topic, country) pairs")

    return agg_df[['ds', 'unique_id', 'topic', 'country', 'y']]


def filter_series(df):
    """
    Filter series:
    - Keep only series with >= MIN_MONTHS observations
    - Remove series with > MAX_ZERO_RATIO zeros
    """
    print("Filtering series...")
    min_months = CONFIG['MIN_MONTHS']
    max_zero_ratio = CONFIG['MAX_ZERO_RATIO']

    # Count months per series
    series_months = df.groupby('unique_id')['ds'].nunique()
    valid_series = series_months[series_months >= min_months].index.tolist()

    df = df[df['unique_id'].isin(valid_series)].copy()

    if df.empty:
        print("Warning: No series passed the MIN_MONTHS filter. Returning all series.")
        return df

    # Count zero ratio
    zero_ratio = df.groupby('unique_id').apply(
        lambda x: (x['y'] == 0).sum() / len(x)
    )
    valid_series = zero_ratio[zero_ratio <= max_zero_ratio].index.tolist()

    df = df[df['unique_id'].isin(valid_series)].copy()

    if df.empty:
        print("Warning: No series passed the zero-ratio filter. Relaxing threshold.")
        return df

    print(f"After filtering: {df['unique_id'].nunique()} series retained")

    return df


def pivot_wide(df):
    """
    Pivot to wide format: months × unique_id, with value as 'y'.
    Returns (wide_df, series_metadata).
    """
    print("Pivoting to wide format...")

    # Get metadata for each unique_id
    metadata = df.groupby('unique_id').agg({
        'topic': 'first',
        'country': 'first'
    }).reset_index()

    # Pivot
    wide = df.pivot_table(
        index='ds',
        columns='unique_id',
        values='y',
        aggfunc='first'
    ).sort_index()

    # Fill missing values with forward fill then backward fill
    wide = wide.ffill().bfill()

    print(f"Wide matrix shape: {wide.shape} (months × series)")

    return wide, metadata


def test_pair(source_id, target_id, source_vals, target_vals):
    """
    Test if source_vals Granger-cause target_vals.
    Returns dict with results or None if test fails.
    """
    max_lag = CONFIG['MAX_LAG']
    p_threshold = CONFIG['P_VALUE_THRESHOLD']

    # Skip if insufficient data
    if len(source_vals) < max_lag + 5:
        return None

    try:
        # Drop NaN
        valid_idx = ~(np.isnan(source_vals) | np.isnan(target_vals))
        if valid_idx.sum() < max_lag + 5:
            return None

        src_clean = source_vals[valid_idx]  # already numpy array
        tgt_clean = target_vals[valid_idx]  # already numpy array

        # Run Granger causality test
        data = np.column_stack([tgt_clean, src_clean])

        # grangercausalitytests returns: {lag: [ssr_ftest_result]}
        # ssr_ftest_result is a tuple: (F-stat, p-value, df_num, df_denom)
        gc_result = grangercausalitytests(data, max_lag, verbose=False)

        # Extract p-values and F-stats for each lag
        best_lag = None
        best_p = 1.0
        best_f = 0.0

        for lag in range(1, max_lag + 1):
            try:
                ssr_ftest = gc_result[lag][0]['ssr_ftest']
                f_stat = ssr_ftest[0]
                p_val = ssr_ftest[1]

                if p_val < best_p:
                    best_p = p_val
                    best_lag = lag
                    best_f = f_stat
            except (KeyError, IndexError, TypeError):
                continue

        if best_lag is None or best_p >= p_threshold:
            return None

        return {
            'source_id': source_id,
            'target_id': target_id,
            'best_lag': best_lag,
            'p_value': best_p,
            'f_stat': best_f,
        }

    except Exception:
        # Skip pairs that cause any numerical or type issues
        return None


def run_causality_analysis(wide_df, metadata, max_series=None):
    """
    Run Granger causality analysis across all pairs using smart prefiltering.

    Strategy:
    1. Test same-country/same-topic pairs (dense)
    2. Test same-country/different-topic pairs (medium)
    3. Test different-country/same-topic pairs (medium)
    4. Test cross-country/cross-topic with correlation prefilter (sparse)
    """
    print("Running Granger causality analysis...")

    series_list = wide_df.columns.tolist()

    # Apply max_series limit if specified — sort by variance first (most active series)
    if max_series and max_series < len(series_list):
        variance_all = wide_df.std()
        series_list = variance_all.nlargest(max_series).index.tolist()
        wide_df = wide_df[series_list]
        print(f"[*] Limited to top {max_series} series by variance (from {len(variance_all)} total)")

    # Compute variance for prefiltering
    variance = wide_df.std()
    median_var = variance.median()
    min_var_threshold = median_var * 0.1

    # Compute correlation matrix for cross-category prefilter
    corr_matrix = wide_df.corr().abs()

    # Build pairs to test with priority
    pairs_to_test = []

    # Parse series metadata
    series_info = {}
    for _, row in metadata.iterrows():
        uid = row['unique_id']
        if uid in series_list:
            series_info[uid] = {
                'topic': row['topic'],
                'country': row['country']
            }

    # 1. Same-country pairs (all topics)
    countries = set(info['country'] for info in series_info.values())
    for country in countries:
        country_series = [s for s in series_list if series_info.get(s, {}).get('country') == country]
        for target in country_series:
            for source in country_series:
                if source != target and variance[source] > min_var_threshold:
                    pairs_to_test.append((source, target, 1))  # priority 1

    # 2. Same-topic pairs (all countries)
    topics = set(info['topic'] for info in series_info.values())
    for topic in topics:
        topic_series = [s for s in series_list if series_info.get(s, {}).get('topic') == topic]
        for target in topic_series:
            for source in topic_series:
                if source != target and variance[source] > min_var_threshold:
                    pair = (source, target, 2)  # priority 2
                    if pair not in pairs_to_test:
                        pairs_to_test.append(pair)

    # 3. Cross-country/cross-topic with correlation prefilter
    for target in series_list:
        if variance[target] < min_var_threshold:
            continue
        for source in series_list:
            if (source == target or
                variance[source] < min_var_threshold or
                (source, target, 1) in pairs_to_test or
                (source, target, 2) in pairs_to_test):
                continue

            # Check correlation prefilter
            try:
                corr_val = corr_matrix.loc[source, target]
                if corr_val > CONFIG['CORRELATION_PREFILTER']:
                    pairs_to_test.append((source, target, 3))  # priority 3
            except KeyError:
                continue

    same_country = sum(1 for _,_,p in pairs_to_test if p==1)
    same_topic   = sum(1 for _,_,p in pairs_to_test if p==2)
    cross_cat    = sum(1 for _,_,p in pairs_to_test if p==3)
    print(f"Total pairs to test: {len(pairs_to_test)} (same-country: {same_country}, same-topic: {same_topic}, cross-cat: {cross_cat})")
    print(f"Series in analysis: {len(series_list)}, series with metadata: {len(series_info)}")
    if len(pairs_to_test) == 0:
        print("[!] WARNING: 0 pairs to test — check that metadata matches series IDs")
        return pd.DataFrame()

    # Run tests in parallel
    edges = []
    pair_count = 0

    def worker(source_id, target_id):
        """Worker function for parallel execution."""
        result = test_pair(
            source_id, target_id,
            wide_df[source_id].values,
            wide_df[target_id].values
        )
        return result

    with ThreadPoolExecutor(max_workers=CONFIG['MAX_WORKERS']) as executor:
        futures = {
            executor.submit(worker, src, tgt): (src, tgt)
            for src, tgt, _ in pairs_to_test
        }

        for future in as_completed(futures):
            pair_count += 1
            if pair_count % 100 == 0:
                print(f"  Tested {pair_count}/{len(pairs_to_test)} pairs...")

            result = future.result()
            if result:
                edges.append(result)

    print(f"Found {len(edges)} significant causal relationships")

    return pd.DataFrame(edges) if edges else pd.DataFrame()


def compute_stats(edges_df, metadata, wide_df):
    """
    Compute causality stats for each series:
    - n_causes: how many series Granger-cause this series
    - n_caused_by: how many series this causes
    - top_cause: strongest Granger predictor
    - top_cause_lag: lag of that predictor
    """
    print("Computing causality statistics...")

    # ── Crash guard: empty DataFrame when no significant edges found ──
    if edges_df.empty or 'target_id' not in edges_df.columns:
        print("[!] No significant causal edges — returning empty stats.")
        _cols = ['unique_id', 'topic', 'country', 'n_causes',
                 'n_caused_by', 'top_cause', 'top_cause_lag']
        return pd.DataFrame(columns=_cols)

    series_list = wide_df.columns.tolist()

    stats_rows = []

    for uid in series_list:
        # Find metadata
        meta_row = metadata[metadata['unique_id'] == uid]
        if meta_row.empty:
            continue

        topic = meta_row['topic'].iloc[0]
        country = meta_row['country'].iloc[0]

        # Count incoming (what causes this series)
        incoming = edges_df[edges_df['target_id'] == uid]
        n_causes = len(incoming)

        # Count outgoing (what this series causes)
        outgoing = edges_df[edges_df['source_id'] == uid]
        n_caused_by = len(outgoing)

        # Find strongest predictor (lowest p-value in incoming)
        top_cause = None
        top_cause_lag = None
        if not incoming.empty:
            best_idx = incoming['p_value'].idxmin()
            top_cause = incoming.loc[best_idx, 'source_id']
            top_cause_lag = incoming.loc[best_idx, 'best_lag']

        stats_rows.append({
            'unique_id': uid,
            'topic': topic,
            'country': country,
            'n_causes': n_causes,
            'n_caused_by': n_caused_by,
            'top_cause': top_cause,
            'top_cause_lag': top_cause_lag,
        })

    return pd.DataFrame(stats_rows)


def print_summary(edges_df, stats_df):
    """Print analysis summary."""
    print("\n" + "="*80)
    print("GRANGER CAUSALITY ANALYSIS SUMMARY")
    print("="*80)

    print(f"\nTotal significant relationships found: {len(edges_df)}")

    if len(edges_df) == 0:
        print("No significant causal relationships found.")
        return

    # Top 10 most infectious (highest n_caused_by)
    print("\nTop 10 Most Infectious Series (highest n_caused_by):")
    top_infect = stats_df.nlargest(10, 'n_caused_by')[
        ['unique_id', 'n_caused_by', 'topic', 'country']
    ]
    for idx, row in top_infect.iterrows():
        print(f"  {row['unique_id']}: {row['n_caused_by']} series caused")

    # Top 10 most receptive (highest n_causes)
    print("\nTop 10 Most Receptive Series (highest n_causes):")
    top_recept = stats_df.nlargest(10, 'n_causes')[
        ['unique_id', 'n_causes', 'topic', 'country']
    ]
    for idx, row in top_recept.iterrows():
        print(f"  {row['unique_id']}: {row['n_causes']} causes")

    # Most significant relationships (lowest p-value)
    print("\nMost Significant Causal Relationships (lowest p-value):")
    top_sig = edges_df.nsmallest(10, 'p_value')[
        ['source_id', 'target_id', 'best_lag', 'p_value', 'f_stat']
    ]
    for idx, row in top_sig.iterrows():
        print(f"  {row['source_id']} -> {row['target_id']} (lag={row['best_lag']}, "
              f"p={row['p_value']:.4f}, F={row['f_stat']:.2f})")

    print("\n" + "="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Granger causality analysis for GDELT indices'
    )
    parser.add_argument(
        '--max-series',
        type=int,
        default=None,
        help='Limit analysis to first N series (for testing)'
    )
    parser.add_argument(
        '--input',
        default=CONFIG['INPUT_FILE'],
        help='Input indices.csv file'
    )
    parser.add_argument(
        '--output-network',
        default=CONFIG['OUTPUT_NETWORK'],
        help='Output causality network CSV'
    )
    parser.add_argument(
        '--output-stats',
        default=CONFIG['OUTPUT_STATS'],
        help='Output causality stats CSV'
    )

    args = parser.parse_args()

    # Load and preprocess
    df = load_and_aggregate(args.input)
    df = filter_series(df)
    wide_df, metadata = pivot_wide(df)

    # Run analysis
    edges_df = run_causality_analysis(wide_df, metadata, max_series=args.max_series)

    if len(edges_df) > 0:
        # Merge metadata into edges
        edges_df = edges_df.merge(
            metadata[['unique_id', 'topic', 'country']],
            left_on='source_id',
            right_on='unique_id',
            how='left'
        ).drop('unique_id', axis=1)
        edges_df.rename(columns={'topic': 'source_topic', 'country': 'source_country'}, inplace=True)

        edges_df = edges_df.merge(
            metadata[['unique_id', 'topic', 'country']],
            left_on='target_id',
            right_on='unique_id',
            how='left'
        ).drop('unique_id', axis=1)
        edges_df.rename(columns={'topic': 'target_topic', 'country': 'target_country'}, inplace=True)

        # Reorder columns
        edges_df = edges_df[[
            'source_id', 'target_id', 'source_topic', 'source_country',
            'target_topic', 'target_country', 'best_lag', 'p_value', 'f_stat'
        ]]

    # Compute stats
    stats_df = compute_stats(edges_df, metadata, wide_df)

    # Print summary
    print_summary(edges_df, stats_df)

    # Save outputs
    print(f"Saving causality network to {args.output_network}...")
    edges_df.to_csv(args.output_network, index=False)

    print(f"Saving causality stats to {args.output_stats}...")
    stats_df.to_csv(args.output_stats, index=False)

    print("Done!")


if __name__ == '__main__':
    main()
