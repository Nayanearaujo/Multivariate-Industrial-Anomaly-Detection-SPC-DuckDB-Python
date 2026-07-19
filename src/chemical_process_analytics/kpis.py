"""Transparent operating KPI calculations for process-monitoring results."""

from __future__ import annotations

import numpy as np
import pandas as pd


def confirm_persistent_alerts(alert: pd.Series, minimum_samples: int = 3) -> pd.Series:
    """Confirm an alert only after a consecutive run reaches the persistence rule."""
    if minimum_samples < 1:
        raise ValueError("minimum_samples must be at least 1")
    alert = alert.fillna(False).astype(bool)
    group = alert.ne(alert.shift(fill_value=False)).cumsum()
    run_position = alert.groupby(group).cumcount() + 1
    return alert & run_position.ge(minimum_samples)


def label_alert_events(alert: pd.Series) -> pd.Series:
    """Assign a positive identifier to each contiguous confirmed alert event."""
    alert = alert.fillna(False).astype(bool)
    starts = alert & ~alert.shift(fill_value=False)
    event_id = starts.cumsum()
    return event_id.where(alert, 0).astype(int)


def fault_detection_rate(
    frame: pd.DataFrame,
    *,
    run_column: str = "simulationRun",
    fault_column: str = "faultNumber",
    alert_column: str = "confirmed_alert",
) -> float:
    """Return the share of faulty runs with at least one confirmed alert."""
    faulty = frame.loc[frame[fault_column].ne(0)]
    if faulty.empty:
        return float("nan")
    detected_by_run = faulty.groupby([fault_column, run_column])[alert_column].any()
    return float(detected_by_run.mean())


def median_detection_delay(
    frame: pd.DataFrame,
    *,
    onset_sample: int,
    minutes_per_sample: int = 3,
    run_column: str = "simulationRun",
    fault_column: str = "faultNumber",
    sample_column: str = "sample",
    alert_column: str = "confirmed_alert",
) -> float:
    """Return median minutes from fault onset to first post-onset alert."""
    faulty = frame.loc[
        frame[fault_column].ne(0)
        & frame[sample_column].ge(onset_sample)
        & frame[alert_column].astype(bool)
    ]
    if faulty.empty:
        return float("nan")
    first_alert = faulty.groupby([fault_column, run_column])[sample_column].min()
    return float(np.median((first_alert - onset_sample) * minutes_per_sample))


def false_alarm_rate(
    frame: pd.DataFrame,
    *,
    normal_mask: pd.Series,
    alert_column: str = "confirmed_alert",
) -> float:
    """Return confirmed alert samples divided by eligible normal samples."""
    eligible = frame.loc[normal_mask]
    if eligible.empty:
        return float("nan")
    return float(eligible[alert_column].astype(bool).mean())


def process_stability_rate(frame: pd.DataFrame, alert_column: str = "confirmed_alert") -> float:
    """Return the share of eligible samples without a confirmed alert."""
    if frame.empty:
        return float("nan")
    return float((~frame[alert_column].fillna(False).astype(bool)).mean())


def alarm_burden_per_100_hours(
    frame: pd.DataFrame,
    *,
    event_column: str = "alert_event_id",
    minutes_per_sample: int = 3,
) -> float:
    """Return distinct alert events per 100 simulated operating hours."""
    if frame.empty:
        return float("nan")
    hours = len(frame) * minutes_per_sample / 60
    event_count = frame.loc[frame[event_column].gt(0), event_column].nunique()
    return float(event_count / hours * 100)
