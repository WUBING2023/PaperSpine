"""Reproduce the frozen bike-demand intake pilot from UCI's ZIP."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import mean, median
from zipfile import ZipFile


def analyze(archive: Path, phase: str) -> dict:
    with ZipFile(archive) as bundle:
        body = bundle.read('hour.csv')
    observations = {}
    calendar = defaultdict(list)
    start, stop = {
        'pilot': (date(2012, 1, 1), date(2012, 7, 1)),
        'holdout': (date(2012, 7, 1), date(2013, 1, 1)),
    }[phase]
    eligible = []

    for row in csv.DictReader(io.StringIO(body.decode('utf-8-sig'))):
        day = date.fromisoformat(row['dteday'])
        hour = int(row['hr'])
        workday = int(row['workingday'])
        time = datetime(day.year, day.month, day.day, hour)
        target = int(row['cnt'])
        if time in observations or target < 0 or workday not in (0, 1):
            raise ValueError(f'Invalid or duplicate observation at {time.isoformat()}')
        observations[time] = target
        group = (hour, workday)
        if day.year == 2011:
            calendar[group].append(target)
        if start <= day < stop:
            eligible.append((time, group, int(row['casual']) + int(row['registered'])))

    historical = {group: median(counts) for group, counts in calendar.items()}
    baseline_errors = []
    lag_errors = []
    week_differences = defaultdict(list)
    reconstruction_errors = []
    for time, group, reconstruction in eligible:
        observed = observations[time]
        reconstruction_errors.append(abs(reconstruction - observed))
        past = time - timedelta(days=7)
        if past not in observations:
            continue
        baseline_error = abs(historical[group] - observed)
        lag_error = abs(observations[past] - observed)
        baseline_errors.append(baseline_error)
        lag_errors.append(lag_error)
        week = time.date() - timedelta(days=time.weekday())
        week_differences[week].append(lag_error - baseline_error)

    weekly = [mean(errors) for errors in week_differences.values()]
    return {
        'phase': phase, 'start_inclusive': str(start), 'end_exclusive': str(stop),
        'hour_csv_sha256': hashlib.sha256(body).hexdigest(),
        'training_hours': sum(len(counts) for counts in calendar.values()),
        'available_hours': len(eligible), 'paired_hours': len(lag_errors),
        'missing_week_lag': len(eligible) - len(lag_errors),
        'calendar_median_mae': mean(baseline_errors), 'weekly_lag_mae': mean(lag_errors),
        'paired_mae_difference_lag_minus_calendar': mean(lag_errors) - mean(baseline_errors),
        'weeks': len(weekly), 'weeks_favoring_lag': sum(difference < 0 for difference in weekly),
        'median_weekly_difference': median(weekly),
        'reconstruction_diagnostic_max_abs_error': max(reconstruction_errors),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('phase', choices=('pilot', 'holdout'))
    options = parser.parse_args()
    print(json.dumps(analyze(options.archive, options.phase), indent=2))
