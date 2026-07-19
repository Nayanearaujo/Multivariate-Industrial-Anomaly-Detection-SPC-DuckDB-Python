"""Data-quality and baseline-profile utilities for process time series."""

from __future__ import annotations

import re

import numpy as np
import pandas as pd


SIGNAL_PATTERN = re.compile(r"^(xmeas|xmv)_\d+$", flags=re.IGNORECASE)


def signal_columns(frame: pd.DataFrame) -> list[str]:
    """Return measured and manipulated signal columns in source order."""
    return [column for column in frame.columns if SIGNAL_PATTERN.match(column)]


def dataset_quality_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Produce a compact, decision-ready quality scorecard."""
    signals = signal_columns(frame)
    numeric = frame[signals].to_numpy(dtype=float)
    key = ["split", "simulationRun", "sample"]
    checks = [
        ("Rows available", len(frame), len(frame), "Context"),
        ("Expected process signals", len(signals), 52, "Critical"),
        ("Missing signal cells", int(frame[signals].isna().sum().sum()), 0, "Critical"),
        ("Non-finite signal cells", int((~np.isfinite(numeric)).sum()), 0, "Critical"),
        ("Duplicate composite keys", int(frame.duplicated(key).sum()), 0, "Critical"),
        ("Missing identifier cells", int(frame[key].isna().sum().sum()), 0, "Critical"),
        ("Unexpected fault labels", int(frame["faultNumber"].ne(0).sum()), 0, "High"),
        ("Zero-variance signals", int(frame[signals].nunique(dropna=False).le(1).sum()), 0, "High"),
    ]
    result = pd.DataFrame(checks, columns=["check", "observed", "expected", "severity"])
    result["status"] = np.where(result["observed"].eq(result["expected"]), "Pass", "Review")
    result.loc[result["check"].eq("Rows available"), "status"] = "Information"
    return result


def run_integrity(frame: pd.DataFrame, expected_samples: dict[str, int]) -> pd.DataFrame:
    """Check run length, sample continuity and key uniqueness for every run."""
    records: list[dict] = []
    for (split, run), group in frame.groupby(["split", "simulationRun"], sort=True):
        ordered = group["sample"].sort_values()
        expected_count = expected_samples.get(str(split))
        records.append(
            {
                "split": split,
                "simulation_run": int(run),
                "rows": len(group),
                "expected_rows": expected_count,
                "first_sample": int(ordered.iloc[0]),
                "last_sample": int(ordered.iloc[-1]),
                "duplicate_samples": int(ordered.duplicated().sum()),
                "missing_sequence_steps": int(ordered.diff().dropna().ne(1).sum()),
                "is_complete": bool(
                    expected_count is not None
                    and len(group) == expected_count
                    and ordered.iloc[0] == 1
                    and ordered.iloc[-1] == expected_count
                    and not ordered.duplicated().any()
                    and ordered.diff().dropna().eq(1).all()
                ),
            }
        )
    return pd.DataFrame(records)


def baseline_statistics(frame: pd.DataFrame, training_split: str) -> pd.DataFrame:
    """Calculate descriptive training-only reference statistics per signal."""
    baseline = frame.loc[frame["split"].eq(training_split)]
    if baseline.empty:
        raise ValueError(f"Training split not found: {training_split}")
    signals = signal_columns(baseline)
    description = baseline[signals].agg(["count", "mean", "std", "min", "median", "max"]).T
    quartiles = baseline[signals].quantile([0.25, 0.75]).T.rename(columns={0.25: "q1", 0.75: "q3"})
    profile = description.join(quartiles)
    profile["iqr"] = profile["q3"] - profile["q1"]
    profile["robust_lower_reference"] = profile["q1"] - 3 * profile["iqr"]
    profile["robust_upper_reference"] = profile["q3"] + 3 * profile["iqr"]
    profile.index.name = "signal"
    return profile.reset_index()


def split_distribution_comparison(
    frame: pd.DataFrame,
    training_split: str,
    testing_split: str,
) -> pd.DataFrame:
    """Compare holdout medians with training medians on the training IQR scale."""
    signals = signal_columns(frame)
    training = frame.loc[frame["split"].eq(training_split), signals]
    testing = frame.loc[frame["split"].eq(testing_split), signals]
    if training.empty or testing.empty:
        raise ValueError("Both training and testing splits are required")

    train_median = training.median()
    test_median = testing.median()
    train_iqr = training.quantile(0.75) - training.quantile(0.25)
    comparison = pd.DataFrame(
        {
            "signal": signals,
            "training_median": train_median.reindex(signals).to_numpy(),
            "testing_median": test_median.reindex(signals).to_numpy(),
            "training_iqr": train_iqr.reindex(signals).to_numpy(),
        }
    )
    comparison["median_shift_on_training_iqr"] = np.where(
        comparison["training_iqr"].ne(0),
        (comparison["testing_median"] - comparison["training_median"])
        / comparison["training_iqr"],
        np.nan,
    )
    comparison["absolute_median_shift"] = comparison["median_shift_on_training_iqr"].abs()
    return comparison.sort_values("absolute_median_shift", ascending=False).reset_index(drop=True)
