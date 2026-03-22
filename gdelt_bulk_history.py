#!/usr/bin/env python3
"""
GDELT BULK HISTORY DOWNLOADER v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Downloads full historical GDELT data from 2013-04-01 (GDELT 2.0 launch)
to yesterday and saves to indices.csv.

Run ONCE before gdelt_forecast.py to build a rich historical database.

Usage:
  python gdelt_bulk_history.py                    # 2013-04-01 → yesterday
  python gdelt_bulk_history.py --start 20200101   # custom start date
  python gdelt_bulk_history.py --workers 16       # more parallel workers
"""

import os
import sys
import datetime
import argparse
import pandas as pd
import concurrent.futures

# Import core functions from gdelt_indices
from gdelt_indices import (
    OUTPUT_FILE, MAX_WORKERS, RETRY_COUNT, RETRY_DELAY,
    download_gdelt_day, compute_day_indices, load_existing_indices,
)

# GDELT 2.0 daily file availability starts around this date
GDELT_START = datetime.date(2013, 4, 1)
CHECKPOINT_EVERY = 100   # save to disk every N completed days


def get_missing_dates(indices, start_date):
    """Return list of YYYYMMDD ints that are in [start_date, yesterday] but not in indices."""
    yesterday = datetime.datetime.utcnow().date() - datetime.timedelta(days=1)
    existing  = set(str(c) for c in indices.columns)

    cur, date_list = start_date, []
    while cur <= yesterday:
        ds = cur.strftime('%Y%m%d')
        if ds not in existing:
            date_list.append(int(ds))
        cur += datetime.timedelta(days=1)

    return sorted(date_list)


def run_bulk(start_date=None, n_workers=None):
    if start_date is None:
        start_date = GDELT_START
    if n_workers is None:
        n_workers = MAX_WORKERS

    print("=" * 60)
    print("GDELT BULK HISTORY DOWNLOADER v1.0")
    print(f"  Start     : {start_date}")
    print(f"  Output    : {OUTPUT_FILE}")
    print(f"  Workers   : {n_workers}")
    print("=" * 60)

    indices   = load_existing_indices(OUTPUT_FILE)
    date_list = get_missing_dates(indices, start_date)

    if not date_list:
        print("\n✓ Nothing to download — database is already up to date.")
        return

    total = len(date_list)
    print(f"\n{total:,} days to download  "
          f"({date_list[0]} → {date_list[-1]})")
    est_min = total * 0.25 / n_workers
    print(f"Estimated time: ~{est_min:.0f} min with {n_workers} parallel workers\n")

    success, skipped = 0, 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = {executor.submit(download_gdelt_day, d): d for d in date_list}

        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            filename, df_day = future.result()

            if df_day is not None:
                day_results = compute_day_indices(df_day)
                if day_results:
                    indices[str(filename)] = pd.Series(day_results)
                    success += 1
                else:
                    skipped += 1
            else:
                skipped += 1

            # Periodic checkpoint + progress report
            if i % CHECKPOINT_EVERY == 0 or i == total:
                pct = i / total * 100
                indices_sorted = indices.reindex(sorted(indices.columns), axis=1)
                indices_sorted.to_csv(OUTPUT_FILE)
                print(f"  [{i:>6}/{total}] {pct:5.1f}% "
                      f"— ✓ {success} saved  ✗ {skipped} skipped  "
                      f"— checkpoint written")

    # Final sort & save
    indices = indices.reindex(sorted(indices.columns), axis=1)
    indices.to_csv(OUTPUT_FILE)

    print("\n" + "=" * 60)
    print(f"✓  Download complete!")
    print(f"   Days downloaded : {success:,}")
    print(f"   Days skipped    : {skipped:,}")
    print(f"   Total in DB     : {len(indices.columns):,} days")
    print(f"   Series          : {len(indices):,}  (topic × country)")
    print(f"   Saved to        : {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download full historical GDELT data and build indices.csv')
    parser.add_argument(
        '--start', type=str, default=None,
        help='Start date as YYYYMMDD (default: 20130401)')
    parser.add_argument(
        '--workers', type=int, default=None,
        help=f'Parallel download workers (default: {MAX_WORKERS})')
    args = parser.parse_args()

    start = GDELT_START
    if args.start:
        try:
            start = datetime.datetime.strptime(args.start, '%Y%m%d').date()
        except ValueError:
            print(f"[!] Invalid date format: {args.start}  (expected YYYYMMDD)")
            sys.exit(1)

    run_bulk(start_date=start, n_workers=args.workers)
