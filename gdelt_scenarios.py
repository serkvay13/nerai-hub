#!/usr/bin/env python3
"""
GDELT Scenario Engine: What-if / Counterfactual Analysis
=========================================================

This script allows users to inject geopolitical shocks into historical data
and re-forecast to see how the system would respond. It supports:
  - Pre-defined scenario templates (Iran crisis, Russia escalation, etc.)
  - Custom shocks injected via command-line arguments
  - Spillover effects propagated via causality network
  - Comparison of baseline vs. shocked forecasts
  - Human-readable summary reports

Usage:
  python gdelt_scenarios.py --scenario iran_nuclear_crisis
  python gdelt_scenarios.py --list-scenarios
  python gdelt_scenarios.py --custom-shock "topic=military_escalation,country=IR,magnitude=0.8,duration=6"
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import warnings

import pandas as pd
import numpy as np

warnings.filterwarnings('ignore')

# Try to import statsforecast for AutoARIMA; fall back to simple methods if unavailable
try:
    from statsforecast.models import AutoARIMA
    STATSFORECAST_AVAILABLE = True
except ImportError:
    STATSFORECAST_AVAILABLE = False


# ============================================================================
# SCENARIO TEMPLATES
# ============================================================================

SCENARIO_TEMPLATES = {
    'iran_nuclear_crisis': {
        'description': 'Iran accelerates nuclear program, triggering regional escalation',
        'shocks': [
            {'topic': 'military_escalation', 'country': 'IR', 'magnitude': 0.80, 'duration_months': 6},
            {'topic': 'international_crisis', 'country': 'IR', 'magnitude': 0.60, 'duration_months': 6},
            {'topic': 'military_escalation', 'country': 'IS', 'magnitude': 0.40, 'duration_months': 4},
        ],
        'spillover_countries': ['IS', 'SA', 'AE', 'IZ', 'LB'],
    },
    'russia_escalation': {
        'description': 'Russia escalates military operations in Eastern Europe',
        'shocks': [
            {'topic': 'military_escalation', 'country': 'RS', 'magnitude': 0.70, 'duration_months': 8},
            {'topic': 'military_clash', 'country': 'UP', 'magnitude': 0.90, 'duration_months': 8},
            {'topic': 'international_crisis', 'country': 'RS', 'magnitude': 0.50, 'duration_months': 6},
        ],
        'spillover_countries': ['UP', 'PO', 'GM', 'FR', 'UK'],
    },
    'china_taiwan_tension': {
        'description': 'China increases military pressure on Taiwan',
        'shocks': [
            {'topic': 'military_escalation', 'country': 'CH', 'magnitude': 0.75, 'duration_months': 5},
            {'topic': 'deteriorating_bilateral_relations', 'country': 'CH', 'magnitude': 0.60, 'duration_months': 6},
            {'topic': 'international_crisis', 'country': 'CH', 'magnitude': 0.50, 'duration_months': 5},
        ],
        'spillover_countries': ['JA', 'KS', 'US', 'AS', 'RP'],
    },
    'middle_east_oil_crisis': {
        'description': 'Attacks on oil infrastructure trigger regional instability',
        'shocks': [
            {'topic': 'instability', 'country': 'SA', 'magnitude': 0.65, 'duration_months': 4},
            {'topic': 'military_escalation', 'country': 'YM', 'magnitude': 0.70, 'duration_months': 6},
            {'topic': 'international_crisis', 'country': 'AE', 'magnitude': 0.45, 'duration_months': 4},
        ],
        'spillover_countries': ['IZ', 'KU', 'QA', 'IR'],
    },
    'global_democratic_backsliding': {
        'description': 'Wave of authoritarianism across multiple regions',
        'shocks': [
            {'topic': 'authoritarianism', 'country': 'TU', 'magnitude': 0.50, 'duration_months': 12},
            {'topic': 'political_repression', 'country': 'RS', 'magnitude': 0.55, 'duration_months': 12},
            {'topic': 'regime_instability', 'country': 'BR', 'magnitude': 0.40, 'duration_months': 8},
        ],
        'spillover_countries': ['AR', 'CO', 'MX', 'IN', 'PK'],
    },
}


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def get_shock_start_date():
    """Return today's date normalized to the start of the current month."""
    today = pd.Timestamp.now()
    return today.normalize().to_period('M').to_timestamp()


def load_data(indices_path='./indices.csv', predictions_path='./predictions.csv',
              causality_path='./causality_network.csv'):
    """
    Load historical indices, baseline predictions, and causality network.

    Returns:
        tuple: (monthly_df, predictions_df, causality_df or None)
    """
    print("[*] Loading data...")

    indices_df = pd.read_csv(indices_path)

    # Handle wide format: date columns are 8-digit strings like '20260217'
    date_cols = [c for c in indices_df.columns
                 if c not in ('topic', 'country', 'date', 'value', 'unique_id')
                 and str(c).isdigit() and len(str(c)) == 8]
    if date_cols:
        print(f"[*] Wide format detected ({len(date_cols)} date columns). Converting to long format...")
        indices_df = indices_df.melt(
            id_vars=['topic', 'country'],
            value_vars=date_cols,
            var_name='date',
            value_name='value'
        )
        # Aggregate to monthly p90
        indices_df['date'] = pd.to_datetime(indices_df['date'].astype(str), format='%Y%m%d', errors='coerce')
        indices_df = indices_df.dropna(subset=['date'])
        indices_df['date'] = indices_df['date'].dt.to_period('M').dt.to_timestamp()
        indices_df = indices_df.groupby(['date', 'topic', 'country'], as_index=False)['value'].quantile(0.90)
    elif 'date' in indices_df.columns:
        indices_df['date'] = pd.to_datetime(indices_df['date'])
    elif 'Date' in indices_df.columns:
        indices_df['Date'] = pd.to_datetime(indices_df['Date'])
        indices_df.rename(columns={'Date': 'date'}, inplace=True)

    predictions_df = pd.read_csv(predictions_path)
    # Normalize date column name — could be 'ds', 'date', or 'Date'
    for col in ['ds', 'Date']:
        if col in predictions_df.columns and 'date' not in predictions_df.columns:
            predictions_df.rename(columns={col: 'date'}, inplace=True)
    if 'date' in predictions_df.columns:
        predictions_df['date'] = pd.to_datetime(predictions_df['date'])

    causality_df = None
    if os.path.exists(causality_path):
        print(f"[+] Loading causality network from {causality_path}")
        causality_df = pd.read_csv(causality_path)
    else:
        print("[!] Causality network not found; spillover effects will not be simulated.")

    print(f"[+] Loaded {len(indices_df)} historical observations")
    print(f"[+] Loaded {len(predictions_df)} baseline predictions")

    return indices_df, predictions_df, causality_df


def apply_shock(monthly_df, shock, shock_start_date, shock_id=1):
    """
    Apply a single shock to the historical data.

    Args:
        monthly_df (pd.DataFrame): Historical monthly data with 'date', 'topic', 'country', 'value' columns
        shock (dict): Shock spec with keys: topic, country, magnitude, duration_months
        shock_start_date (pd.Timestamp): Date to start the shock
        shock_id (int): Identifier for this shock (for tracking)

    Returns:
        pd.DataFrame: Modified dataframe with shock-induced synthetic observations appended
    """
    topic = shock['topic']
    country = shock['country']
    magnitude = shock['magnitude']
    duration_months = shock['duration_months']

    # Filter to the shocked series
    mask = (monthly_df['topic'] == topic) & (monthly_df['country'] == country)
    shocked_series = monthly_df[mask].copy()

    if shocked_series.empty:
        print(f"[!] Warning: No data found for {topic} / {country}. Skipping this shock.")
        return monthly_df

    # Get the last observed value
    last_value = shocked_series['value'].iloc[-1] if len(shocked_series) > 0 else 0
    if pd.isna(last_value) or last_value == 0:
        last_value = shocked_series['value'].dropna().iloc[-1] if len(shocked_series['value'].dropna()) > 0 else 1

    # Create synthetic shocked values
    shock_magnitude_additive = last_value * magnitude
    synthetic_rows = []

    shock_start_period = shock_start_date.to_period('M')
    for i in range(duration_months):
        future_period = shock_start_period + i
        future_date = future_period.to_timestamp()

        # Linearly interpolate shock magnitude (ramping in at the start, ramping out at the end)
        progress = i / max(duration_months - 1, 1)
        ramp_factor = min(progress, 1.0, 2.0 - progress)  # smooth ramp in/out
        shocked_value = last_value + (shock_magnitude_additive * ramp_factor)

        synthetic_rows.append({
            'date': future_date,
            'topic': topic,
            'country': country,
            'value': max(shocked_value, 0),
            'shock_id': shock_id,
        })

    synthetic_df = pd.DataFrame(synthetic_rows)

    # Remove any existing future observations in this series (avoid conflicts)
    future_mask = monthly_df['date'] >= shock_start_date
    monthly_df_trimmed = monthly_df[~(
        (monthly_df['topic'] == topic) &
        (monthly_df['country'] == country) &
        future_mask
    )]

    # Append synthetic shocks
    result_df = pd.concat([monthly_df_trimmed, synthetic_df], ignore_index=True)
    result_df = result_df.sort_values('date').reset_index(drop=True)

    print(f"[+] Applied shock: {topic}/{country} +{magnitude*100:.0f}% for {duration_months} months (last_value={last_value:.2f})")

    return result_df


def simulate_spillover(shocked_series_id, causality_network, magnitude, decay=0.4):
    """
    Look up which series the shocked series Granger-causes, and return spillover targets.

    Args:
        shocked_series_id (str): Series ID in format 'topic/country'
        causality_network (pd.DataFrame): Causality network with 'source', 'target', 'lag', 'p_value'
        magnitude (float): Original shock magnitude
        decay (float): Decay factor per hop (default 0.4 = 60% reduction)

    Returns:
        list: Spillover specs [{'topic': ..., 'country': ..., 'magnitude': ..., 'duration_months': ...}, ...]
    """
    if causality_network is None or causality_network.empty:
        return []

    spillovers = []

    # Find all targets caused by the shocked series
    targets = causality_network[causality_network['source'] == shocked_series_id]

    for _, row in targets.iterrows():
        target_id = row['target']
        p_value = row.get('p_value', 0.05)

        # Only apply spillover if causality is significant
        if p_value < 0.1:  # Granger causality significance threshold
            if '/' in target_id:
                target_topic, target_country = target_id.split('/')
            else:
                continue

            spillover_magnitude = magnitude * decay
            spillover = {
                'topic': target_topic,
                'country': target_country,
                'magnitude': spillover_magnitude,
                'duration_months': max(3, int(6 * decay)),
            }
            spillovers.append(spillover)

    return spillovers


def forecast_arima(series_data, periods=12, seasonal_periods=12):
    """
    Fit AutoARIMA (or fallback) and forecast.

    Args:
        series_data (pd.Series): Time series values
        periods (int): Number of periods to forecast
        seasonal_periods (int): Seasonal period (default 12 for monthly)

    Returns:
        np.ndarray: Forecast values
    """
    if len(series_data) < 2:
        return np.full(periods, series_data.iloc[-1] if len(series_data) > 0 else 0)

    if STATSFORECAST_AVAILABLE:
        try:
            model = AutoARIMA(season_length=seasonal_periods)
            fit = model.fit(series_data.values)
            forecast = fit.predict(h=periods).values.flatten()
            return forecast
        except Exception as e:
            print(f"[!] AutoARIMA fit failed: {e}. Falling back to simple exponential extrapolation.")

    # Fallback: exponential smoothing via numpy
    last_value = series_data.iloc[-1]
    if len(series_data) > 1:
        trend = (series_data.iloc[-1] - series_data.iloc[-2]) / max(abs(series_data.iloc[-2]), 1e-6)
        trend = np.clip(trend, -0.1, 0.1)  # Constrain trend
    else:
        trend = 0.0

    forecast = []
    current = last_value
    for _ in range(periods):
        current = current * (1 + trend) + np.random.normal(0, abs(last_value) * 0.01)
        forecast.append(max(current, 0))

    return np.array(forecast)


def run_scenario(scenario_name, custom_shocks=None, causality_network=None,
                 horizon=12, indices_df=None, predictions_df=None, output_dir='.'):
    """
    Main scenario execution: apply shocks, simulate spillovers, re-forecast, and compare.

    Args:
        scenario_name (str): Name of scenario template or 'custom'
        custom_shocks (list): Custom shocks if scenario_name is 'custom'
        causality_network (pd.DataFrame): Causality network for spillover (optional)
        horizon (int): Forecast horizon in months
        indices_df (pd.DataFrame): Historical indices (optional; loads if None)
        predictions_df (pd.DataFrame): Baseline predictions (optional; loads if None)
        output_dir (str): Output directory (default '.')

    Returns:
        dict: Results dict with 'results_df', 'scenario_name', 'scenario_desc', 'shocks_applied'
    """

    # Load data if not provided
    if indices_df is None or predictions_df is None:
        indices_df, predictions_df, causality_network = load_data()

    # Get scenario spec
    if scenario_name in SCENARIO_TEMPLATES:
        scenario = SCENARIO_TEMPLATES[scenario_name]
        scenario_desc = scenario['description']
        shocks = scenario['shocks']
        spillover_countries = scenario.get('spillover_countries', [])
    elif scenario_name == 'custom' and custom_shocks:
        scenario_desc = "Custom scenario"
        shocks = custom_shocks
        spillover_countries = []
    else:
        raise ValueError(f"Unknown scenario: {scenario_name}")

    print(f"\n{'='*70}")
    print(f"SCENARIO: {scenario_name.upper()}")
    print(f"DESCRIPTION: {scenario_desc}")
    print(f"{'='*70}\n")

    shock_start_date = get_shock_start_date()
    print(f"[*] Shock start date: {shock_start_date.date()}")

    # Prepare working copy of historical data
    shocked_monthly_df = indices_df.copy()

    # Standardize column names
    if 'Date' in shocked_monthly_df.columns:
        shocked_monthly_df.rename(columns={'Date': 'date'}, inplace=True)
    if 'topic' not in shocked_monthly_df.columns and 'Topic' in shocked_monthly_df.columns:
        shocked_monthly_df.rename(columns={'Topic': 'topic'}, inplace=True)
    if 'country' not in shocked_monthly_df.columns and 'Country' in shocked_monthly_df.columns:
        shocked_monthly_df.rename(columns={'Country': 'country'}, inplace=True)
    if 'value' not in shocked_monthly_df.columns and 'Value' in shocked_monthly_df.columns:
        shocked_monthly_df.rename(columns={'Value': 'value'}, inplace=True)

    # Apply direct shocks
    shocks_applied = []
    shock_id = 1
    for shock in shocks:
        shocked_monthly_df = apply_shock(shocked_monthly_df, shock, shock_start_date, shock_id)
        shocks_applied.append(shock)
        shock_id += 1

    # Simulate spillovers
    if causality_network is not None and not causality_network.empty:
        print("\n[*] Simulating spillover effects via causality network...")
        for shock in shocks:
            series_id = f"{shock['topic']}/{shock['country']}"
            spillovers = simulate_spillover(series_id, causality_network, shock['magnitude'], decay=0.4)
            for spillover in spillovers:
                print(f"  -> Spillover detected: {spillover['topic']}/{spillover['country']} +{spillover['magnitude']*100:.0f}%")
                shocked_monthly_df = apply_shock(shocked_monthly_df, spillover, shock_start_date, shock_id)
                shocks_applied.append(spillover)
                shock_id += 1

    # Re-forecast from shocked data
    print("\n[*] Re-forecasting from shocked data...")

    # Identify all affected series (topic/country combinations)
    affected_series = []
    for _, row in shocked_monthly_df.iterrows():
        series_key = (row.get('topic'), row.get('country'))
        if series_key not in affected_series:
            affected_series.append(series_key)

    results_rows = []

    for topic, country in affected_series:
        series_mask = (shocked_monthly_df['topic'] == topic) & (shocked_monthly_df['country'] == country)
        historical = shocked_monthly_df[series_mask].sort_values('date').copy()

        if len(historical) < 2:
            continue

        values = historical['value'].values

        # Forecast from shocked data
        shocked_forecast = forecast_arima(pd.Series(values), periods=horizon)

        # Get baseline forecast for comparison
        baseline_mask = (predictions_df['topic'] == topic) & (predictions_df['country'] == country)
        baseline = predictions_df[baseline_mask].sort_values('date')

        if len(baseline) > 0:
            baseline_forecast = baseline['yhat'].values[:horizon]
            if len(baseline_forecast) < horizon:
                baseline_forecast = np.pad(baseline_forecast, (0, horizon - len(baseline_forecast)), 'edge')
        else:
            baseline_forecast = np.full(horizon, values[-1])

        # Compute metrics
        baseline_avg = np.nanmean(baseline_forecast)
        shocked_avg = np.nanmean(shocked_forecast)
        delta_pct = ((shocked_avg - baseline_avg) / max(abs(baseline_avg), 1e-6)) * 100

        peak_month = np.argmax(shocked_forecast) + 1

        if shocked_avg > baseline_avg * 1.05:
            direction = 'escalating'
        elif shocked_avg < baseline_avg * 0.95:
            direction = 'de-escalating'
        else:
            direction = 'stable'

        results_rows.append({
            'topic': topic,
            'country': country,
            'baseline_avg': baseline_avg,
            'shocked_avg': shocked_avg,
            'delta_pct': delta_pct,
            'peak_month': peak_month,
            'direction': direction,
            'is_directly_shocked': any(s['topic'] == topic and s['country'] == country for s in shocks),
        })

    results_df = pd.DataFrame(results_rows)

    # Save results
    output_path = os.path.join(output_dir, 'scenario_results.csv')
    results_df.to_csv(output_path, index=False)
    print(f"[+] Scenario results saved to {output_path}")

    # Generate and save report
    generate_report(results_df, scenario_name, scenario_desc, output_dir)

    return {
        'results_df': results_df,
        'scenario_name': scenario_name,
        'scenario_desc': scenario_desc,
        'shocks_applied': shocks_applied,
        'shock_start_date': shock_start_date,
    }


def generate_report(results_df, scenario_name, scenario_desc, output_dir='.'):
    """
    Generate and save a human-readable scenario report.

    Args:
        results_df (pd.DataFrame): Results from run_scenario()
        scenario_name (str): Scenario name
        scenario_desc (str): Scenario description
        output_dir (str): Output directory (default '.')
    """
    report_lines = [
        "=" * 80,
        f"GDELT SCENARIO ENGINE - WHAT-IF ANALYSIS REPORT",
        "=" * 80,
        f"Scenario: {scenario_name.upper()}",
        f"Description: {scenario_desc}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "RESULTS SUMMARY",
        "-" * 80,
    ]

    # Sort by absolute delta for most impactful first
    results_sorted = results_df.sort_values('delta_pct', key=abs, ascending=False)

    # Directly shocked series
    directly_shocked = results_sorted[results_sorted['is_directly_shocked']]
    if len(directly_shocked) > 0:
        report_lines.append("\nDIRECTLY SHOCKED SERIES:")
        for _, row in directly_shocked.iterrows():
            line = (f"  {row['topic']:30s} / {row['country']:4s}: "
                   f"{row['delta_pct']:+7.1f}% | "
                   f"Baseline: {row['baseline_avg']:8.2f}, "
                   f"Shocked: {row['shocked_avg']:8.2f} | "
                   f"Direction: {row['direction']:15s} | "
                   f"Peak: Month {row['peak_month']}")
            report_lines.append(line)

    # Spillover / affected series
    spillover = results_sorted[~results_sorted['is_directly_shocked']]
    if len(spillover) > 0:
        report_lines.append("\nSPILLOVER / AFFECTED SERIES:")
        for _, row in spillover.iterrows():
            line = (f"  {row['topic']:30s} / {row['country']:4s}: "
                   f"{row['delta_pct']:+7.1f}% | "
                   f"Baseline: {row['baseline_avg']:8.2f}, "
                   f"Shocked: {row['shocked_avg']:8.2f} | "
                   f"Direction: {row['direction']:15s} | "
                   f"Peak: Month {row['peak_month']}")
            report_lines.append(line)

    report_lines.extend([
        "",
        "-" * 80,
        f"Total affected series: {len(results_df)}",
        f"Escalating series: {len(results_df[results_df['direction'] == 'escalating'])}",
        f"De-escalating series: {len(results_df[results_df['direction'] == 'de-escalating'])}",
        f"Stable series: {len(results_df[results_df['direction'] == 'stable'])}",
        "",
        "=" * 80,
    ])

    report_text = "\n".join(report_lines)
    print("\n" + report_text)

    # Save report
    report_path = os.path.join(output_dir, 'scenario_report.txt')
    with open(report_path, 'w') as f:
        f.write(report_text)
    print(f"\n[+] Report saved to {report_path}")


def parse_custom_shock(shock_str):
    """
    Parse a custom shock from command-line format.

    Example: "topic=military_escalation,country=IR,magnitude=0.8,duration=6"

    Returns:
        dict: Shock spec with keys topic, country, magnitude, duration_months
    """
    parts = shock_str.split(',')
    shock = {}
    for part in parts:
        key, val = part.split('=')
        key = key.strip()
        val = val.strip()

        if key == 'topic':
            shock['topic'] = val
        elif key == 'country':
            shock['country'] = val
        elif key == 'magnitude':
            shock['magnitude'] = float(val)
        elif key == 'duration' or key == 'duration_months':
            shock['duration_months'] = int(val)

    # Validate
    required = {'topic', 'country', 'magnitude', 'duration_months'}
    if not required.issubset(shock.keys()):
        raise ValueError(f"Custom shock missing required fields. Got: {shock}")

    return shock


def list_scenarios():
    """Print available scenario templates."""
    print("\nAvailable Scenario Templates:")
    print("=" * 70)
    for name, spec in SCENARIO_TEMPLATES.items():
        print(f"\n{name.upper()}")
        print(f"  Description: {spec['description']}")
        print(f"  Shocks: {len(spec['shocks'])}")
        for shock in spec['shocks']:
            print(f"    - {shock['topic']}/{shock['country']}: +{shock['magnitude']*100:.0f}% for {shock['duration_months']} months")
    print("\n" + "=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='GDELT Scenario Engine: What-if / Counterfactual Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gdelt_scenarios.py --scenario iran_nuclear_crisis
  python gdelt_scenarios.py --list-scenarios
  python gdelt_scenarios.py --custom-shock "topic=military_escalation,country=IR,magnitude=0.8,duration=6"
        """
    )

    parser.add_argument('--scenario', type=str, default=None,
                       help='Scenario name (see --list-scenarios for options)')
    parser.add_argument('--list-scenarios', action='store_true',
                       help='List available scenario templates and exit')
    parser.add_argument('--custom-shock', type=str, default=None,
                       help='Custom shock spec: topic=X,country=Y,magnitude=Z,duration=N (repeatable)')
    parser.add_argument('--indices', type=str, default='./indices.csv',
                       help='Path to indices CSV file (default: ./indices.csv)')
    parser.add_argument('--predictions', type=str, default='./predictions.csv',
                       help='Path to baseline predictions CSV file (default: ./predictions.csv)')
    parser.add_argument('--causality', type=str, default='./causality_network.csv',
                       help='Path to causality network CSV file (optional)')
    parser.add_argument('--horizon', type=int, default=12,
                       help='Forecast horizon in months (default: 12)')
    parser.add_argument('--output', type=str, default='.',
                       help='Output directory (default: current directory)')

    args = parser.parse_args()

    # List scenarios and exit
    if args.list_scenarios:
        list_scenarios()
        sys.exit(0)

    # Validate scenario selection
    if args.scenario is None and args.custom_shock is None:
        parser.print_help()
        print("\n[!] Error: Please specify --scenario or --custom-shock")
        sys.exit(1)

    # Create output directory if needed
    Path(args.output).mkdir(parents=True, exist_ok=True)

    # Load data
    try:
        indices_df, predictions_df, causality_df = load_data(
            indices_path=args.indices,
            predictions_path=args.predictions,
            causality_path=args.causality
        )
    except FileNotFoundError as e:
        print(f"[!] Error loading data: {e}")
        sys.exit(1)

    # Run scenario
    try:
        if args.custom_shock:
            shocks = []
            if isinstance(args.custom_shock, list):
                for shock_str in args.custom_shock:
                    shocks.append(parse_custom_shock(shock_str))
            else:
                shocks.append(parse_custom_shock(args.custom_shock))

            results = run_scenario(
                scenario_name='custom',
                custom_shocks=shocks,
                causality_network=causality_df,
                horizon=args.horizon,
                indices_df=indices_df,
                predictions_df=predictions_df,
                output_dir=args.output
            )
        else:
            results = run_scenario(
                scenario_name=args.scenario,
                custom_shocks=None,
                causality_network=causality_df,
                horizon=args.horizon,
                indices_df=indices_df,
                predictions_df=predictions_df,
                output_dir=args.output
            )

        print(f"\n[+] Scenario completed successfully!")
        print(f"[+] Results saved to {args.output}/scenario_results.csv")
        print(f"[+] Report saved to {args.output}/scenario_report.txt")

    except Exception as e:
        print(f"[!] Error running scenario: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
