"""Input, schema-validation and preparation helpers."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pyreadr


IDENTIFIER_COLUMNS = {"faultNumber", "simulationRun", "sample"}


def normalise_column_name(name: object) -> str:
    """Return a predictable camel-style name without changing signal meaning."""
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", str(name)).strip("_")
    aliases = {
        "fault_number": "faultNumber",
        "simulation_run": "simulationRun",
        "faultnumber": "faultNumber",
        "simulationrun": "simulationRun",
    }
    return aliases.get(cleaned.lower(), cleaned)


def validate_schema(frame: pd.DataFrame) -> None:
    missing = IDENTIFIER_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing identifier columns: {sorted(missing)}")

    signals = [column for column in frame if column.lower().startswith(("xmeas", "xmv"))]
    if len(signals) != 52:
        raise ValueError(f"Expected 52 process-signal columns; found {len(signals)}")

    if frame[list(IDENTIFIER_COLUMNS)].isna().any().any():
        raise ValueError("Identifier columns contain missing values")


def load_rdata_file(path: str | Path, split: str | None = None) -> pd.DataFrame:
    """Read every tabular object in one RData file into a single validated frame."""
    source = Path(path)
    objects = pyreadr.read_r(str(source))
    frames: list[pd.DataFrame] = []

    for object_name, value in objects.items():
        if not isinstance(value, pd.DataFrame):
            continue
        frame = value.copy()
        frame.columns = [normalise_column_name(column) for column in frame.columns]
        frame["source_object"] = object_name or source.stem
        frames.append(frame)

    if not frames:
        raise ValueError(f"No tabular objects found in {source.name}")

    combined = pd.concat(frames, ignore_index=True, sort=False)
    validate_schema(combined)
    combined["source_file"] = source.name
    combined["split"] = split or source.stem.lower()
    combined["elapsed_minutes"] = (combined["sample"].astype(int) - 1) * 3
    return combined


def load_raw_directory(raw_dir: str | Path) -> pd.DataFrame:
    """Load all RData files from the raw source directory."""
    paths = sorted(Path(raw_dir).glob("*.RData")) + sorted(Path(raw_dir).glob("*.rdata"))
    if not paths:
        raise FileNotFoundError("No RData files found. Run scripts/download_data.py first.")
    return pd.concat([load_rdata_file(path) for path in paths], ignore_index=True, sort=False)
