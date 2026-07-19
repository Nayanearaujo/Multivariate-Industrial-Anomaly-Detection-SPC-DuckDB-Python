"""Prepare the normal-operation analytical layer and quality evidence."""

from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from chemical_process_analytics.data_io import load_rdata_file  # noqa: E402
from chemical_process_analytics.quality import (  # noqa: E402
    baseline_statistics,
    dataset_quality_summary,
    run_integrity,
    split_distribution_comparison,
)


SOURCE_FILES = {
    "normal_training": "TEP_FaultFree_Training.RData",
    "normal_testing": "TEP_FaultFree_Testing.RData",
}
EXPECTED_SAMPLES = {"normal_training": 500, "normal_testing": 960}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    raw_dir = ROOT / "data" / "raw"
    interim_dir = ROOT / "data" / "interim"
    processed_dir = ROOT / "data" / "processed"
    interim_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    missing = [filename for filename in SOURCE_FILES.values() if not (raw_dir / filename).exists()]
    if missing:
        raise FileNotFoundError(f"Missing complete normal-operation source files: {missing}")

    frames = [
        load_rdata_file(raw_dir / filename, split=split)
        for split, filename in SOURCE_FILES.items()
    ]
    normal = pd.concat(frames, ignore_index=True, sort=False)
    normal["simulationRun"] = normal["simulationRun"].astype("int32")
    normal["sample"] = normal["sample"].astype("int32")
    normal["faultNumber"] = normal["faultNumber"].astype("int8")

    quality = dataset_quality_summary(normal)
    integrity = run_integrity(normal, EXPECTED_SAMPLES)
    baseline = baseline_statistics(normal, "normal_training")
    shift = split_distribution_comparison(normal, "normal_training", "normal_testing")

    normal.to_parquet(interim_dir / "normal_operation_samples.parquet", index=False)
    quality.to_parquet(processed_dir / "data_quality_summary.parquet", index=False)
    integrity.to_parquet(processed_dir / "run_integrity.parquet", index=False)
    baseline.to_parquet(processed_dir / "normal_baseline_statistics.parquet", index=False)
    shift.to_parquet(processed_dir / "normal_split_comparison.parquet", index=False)

    run_summary = (
        normal.groupby("split")
        .agg(rows=("sample", "size"), runs=("simulationRun", "nunique"), samples_per_run=("sample", "nunique"))
        .reset_index()
    )
    audit = {
        "rows": int(len(normal)),
        "source_columns": 55,
        "process_signals": 52,
        "runs": int(normal[["split", "simulationRun"]].drop_duplicates().shape[0]),
        "complete_runs": int(integrity["is_complete"].sum()),
        "quality_checks_requiring_review": int(quality["status"].eq("Review").sum()),
        "source_files": [
            {
                "split": split,
                "filename": filename,
                "size_bytes": int((raw_dir / filename).stat().st_size),
                "sha256": sha256(raw_dir / filename),
            }
            for split, filename in SOURCE_FILES.items()
        ],
        "run_summary": run_summary.to_dict(orient="records"),
    }
    (processed_dir / "normal_baseline_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
