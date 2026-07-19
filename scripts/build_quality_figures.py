"""Export the validated data-quality figures used by Notebook 02."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
IMAGES = ROOT / "images"
IMAGES.mkdir(parents=True, exist_ok=True)

NAVY = "#14213D"
TEAL = "#2A9D8F"
GUAVA = "#F08FA0"
SAND = "#F6F1EC"
AMBER = "#E9C46A"
STEEL = "#607A80"


def finish(figure: plt.Figure, filename: str) -> None:
    figure.savefig(IMAGES / filename, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def run_completeness_figure() -> None:
    integrity = pd.read_parquet(PROCESSED / "run_integrity.parquet")
    summary = (
        integrity.groupby("split")["is_complete"]
        .agg(complete="sum", total="size")
        .reset_index()
    )
    summary["incomplete"] = summary["total"] - summary["complete"]
    labels = summary["split"].str.replace("normal_", "", regex=False).str.title()

    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    ax.barh(labels, summary["complete"], color=TEAL)
    ax.barh(labels, summary["incomplete"], left=summary["complete"], color=GUAVA)
    for position, row in summary.iterrows():
        ax.text(row["complete"] - 10, position, f'{int(row["complete"]):,} / {int(row["total"]):,} complete',
                ha="right", va="center", color="white", weight="bold", fontsize=11)
    ax.set_title("Run-level sequence integrity", loc="left", color=NAVY, weight="bold", fontsize=16)
    ax.set_xlabel("Simulation runs")
    ax.set_xlim(0, 520)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", alpha=0.18)
    fig.text(0.01, -0.01, "A complete run starts at sample 1, ends at the expected sample and has no duplicates or gaps.", color=STEEL)
    fig.tight_layout()
    finish(fig, "02_run_sequence_integrity.png")


def split_stability_figure() -> None:
    shift = pd.read_parquet(PROCESSED / "normal_split_comparison.parquet").head(15).sort_values(
        "median_shift_on_training_iqr"
    )
    colours = np.where(shift["median_shift_on_training_iqr"].ge(0), TEAL, GUAVA)
    fig, ax = plt.subplots(figsize=(9.5, 7.0))
    bars = ax.barh(shift["signal"], shift["median_shift_on_training_iqr"], color=colours)
    for bar, value in zip(bars, shift["median_shift_on_training_iqr"], strict=True):
        offset = 0.00045 if value >= 0 else -0.00045
        ax.text(value + offset, bar.get_y() + bar.get_height() / 2, f"{value:+.3f}",
                va="center", ha="left" if value >= 0 else "right", fontsize=9, color=NAVY)
    limit = max(0.022, float(shift["absolute_median_shift"].max()) * 1.22)
    ax.axvline(0, color=NAVY, linewidth=1)
    ax.set_xlim(-limit, limit)
    ax.set_title("Normal-operation holdout medians remain aligned with training", loc="left", color=NAVY, weight="bold", fontsize=15)
    ax.set_xlabel("Testing median minus training median, divided by training IQR")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", alpha=0.18)
    fig.text(0.01, -0.01, "Displayed signals are the 15 largest absolute shifts. This is a descriptive comparison, not a control limit.", color=STEEL)
    fig.tight_layout()
    finish(fig, "02_normal_split_median_stability.png")


def baseline_variability_figure() -> None:
    baseline = pd.read_parquet(PROCESSED / "normal_baseline_statistics.parquet")
    baseline["relative_iqr"] = baseline["iqr"] / baseline["median"].abs().replace(0, np.nan)
    selected = baseline.nlargest(12, "relative_iqr").sort_values("relative_iqr")
    colours = [GUAVA if name.startswith("xmeas") else TEAL for name in selected["signal"]]

    fig, ax = plt.subplots(figsize=(9.5, 6.2))
    bars = ax.barh(selected["signal"], selected["relative_iqr"] * 100, color=colours)
    ax.bar_label(bars, labels=[f"{value:.1f}%" for value in selected["relative_iqr"] * 100], padding=4, fontsize=9)
    ax.set_title("Signals with the largest relative baseline spread", loc="left", color=NAVY, weight="bold", fontsize=15)
    ax.set_xlabel("Training IQR as a percentage of the absolute training median")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", alpha=0.18)
    ax.set_xlim(0, selected["relative_iqr"].max() * 100 * 1.16)
    fig.text(0.01, -0.01, "Relative spread supports prioritisation only; near-zero medians can increase this ratio and require engineering interpretation.", color=STEEL)
    fig.tight_layout()
    finish(fig, "02_relative_baseline_spread.png")


if __name__ == "__main__":
    run_completeness_figure()
    split_stability_figure()
    baseline_variability_figure()
    print("Exported three validated figures to images/")
