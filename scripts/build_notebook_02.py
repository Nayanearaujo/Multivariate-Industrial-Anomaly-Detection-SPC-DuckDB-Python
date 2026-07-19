"""Build Notebook 02 as a detailed, reader-facing data-quality report."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "notebooks" / "02_data_quality_and_operating_baseline.ipynb"


def md(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip())


def build() -> Path:
    notebook = nbf.v4.new_notebook()
    notebook["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
    }
    notebook["cells"] = [
        md(
            """
            # 02 · Data quality and normal operating baseline

            **Purpose.** Decide whether the normal-operation data are reliable enough to define a statistical reference for process monitoring.

            A fault-detection system is only as credible as the baseline against which abnormal behaviour is judged. This notebook therefore treats data quality as an operating-control requirement, not as a preliminary cleaning exercise.
            """
        ),
        md(
            """
            ## tl;dr

            The validated normal-operation layer contains **730,000 process samples**, **1,000 simulation runs** and all **52 expected process signals**.

            - Training: 250,000 samples across 500 complete runs of 500 samples each.
            - Testing: 480,000 samples across 500 complete runs of 960 samples each.
            - No missing signal values, non-finite values, duplicate composite keys or missing sequence steps were found.
            - All normal-operation runs carry the expected fault label `0`.
            - The largest testing-versus-training median shift is approximately **0.019 training IQR**, indicating close alignment between the two normal-operation splits.

            **Decision.** The training split is suitable for estimating a normal statistical reference. The testing split remains isolated as a holdout for measuring false alarms and baseline stability. It must not be used to tune thresholds.
            """
        ),
        md(
            """
            ## Context & methods

            ### Operating decision

            Before building PCA, Hotelling T², Q residual or machine-learning monitoring, the project must answer four questions:

            1. Is the analytical grain unique and complete?
            2. Does every run contain the expected sequence of three-minute samples?
            3. Are all process signals numerically usable and sufficiently variable?
            4. Is the independent normal-testing split broadly consistent with the training reference?

            Passing these checks does not prove that the simulation represents a real plant. It shows only that the supplied normal-operation data are internally consistent enough for the next analytical stage.
            """
        ),
        md(
            """
            ### Analytical grain

            One row represents one three-minute process observation within a simulation run.

            The composite key is:

            ```text
            split + simulationRun + sample
            ```

            `simulationRun` is not globally unique because run identifiers restart between training and testing. Excluding `split` from the key would therefore create false duplicates and an incorrect join design.
            """
        ),
        md(
            """
            ### Split policy and leakage prevention

            | Split | Role | Allowed use | Prohibited use |
            | --- | --- | --- | --- |
            | `normal_training` | Reference population | Estimate scaling, covariance, PCA loadings and candidate limits | Final false-alarm reporting |
            | `normal_testing` | Independent normal holdout | Evaluate baseline transfer and false alarms | Threshold selection or model fitting |

            This separation is retained in Parquet, SQL and Power BI. A visually appealing dashboard is not a reason to combine reference and holdout populations.
            """
        ),
        md(
            """
            ### Key assumptions

            - The Harvard Dataverse files are the authoritative source.
            - `faultNumber = 0` represents normal simulated operation.
            - Samples are spaced three minutes apart; elapsed time is derived from the sample sequence.
            - Training runs are expected to contain 500 samples and testing runs 960 samples.
            - Statistical reference limits are not engineering specification limits.
            - No source variable is silently removed because it looks unusual. Exclusion requires a documented quality or modelling reason.
            """
        ),
        md(
            """
            ### Acceptance criteria

            | Control | Acceptance rule | Consequence of failure |
            | --- | --- | --- |
            | Schema | 52 process signals and 3 identifiers | Stop ingestion |
            | Composite key | Zero duplicates | Investigate source or transformation |
            | Required values | Zero missing identifiers and signal cells | Stop baseline estimation |
            | Numeric validity | Zero infinite or non-finite signal values | Quarantine affected records |
            | Run integrity | At least 99% complete runs | Exclude incomplete runs with an audit trail |
            | Label validity | Only fault label 0 in normal files | Stop and correct source assignment |
            | Signal variability | No constant process signals | Review before scaling or PCA |

            The 99% run-coverage rule is a project guardrail. The observed source passes at 100%, so no exclusion is applied.
            """
        ),
        md("## Data"),
        md(
            """
            ### 1. Load the curated analytical layer

            The original RData files remain unchanged in `data/raw/`. The preparation script validates their source schema, adds split and elapsed-time fields, applies compact integer types to identifiers and writes the combined normal-operation layer to Parquet.

            Rebuild the layer with:

            ```bash
            python scripts/prepare_normal_baseline.py
            ```
            """
        ),
        code(
            """
            from pathlib import Path
            import json
            import sys

            import matplotlib.pyplot as plt
            import numpy as np
            import pandas as pd

            PROJECT_ROOT = Path.cwd().resolve().parent if Path.cwd().name == "notebooks" else Path.cwd().resolve()
            SRC = PROJECT_ROOT / "src"
            if str(SRC) not in sys.path:
                sys.path.insert(0, str(SRC))

            INTERIM = PROJECT_ROOT / "data" / "interim"
            PROCESSED = PROJECT_ROOT / "data" / "processed"
            normal = pd.read_parquet(INTERIM / "normal_operation_samples.parquet")
            quality = pd.read_parquet(PROCESSED / "data_quality_summary.parquet")
            integrity = pd.read_parquet(PROCESSED / "run_integrity.parquet")
            baseline = pd.read_parquet(PROCESSED / "normal_baseline_statistics.parquet")
            split_comparison = pd.read_parquet(PROCESSED / "normal_split_comparison.parquet")
            audit = json.loads((PROCESSED / "normal_baseline_audit.json").read_text())
            """
        ),
        md("### 2. Confirm shape, split and source contract"),
        code(
            """
            split_summary = (
                normal.groupby("split")
                .agg(
                    rows=("sample", "size"),
                    runs=("simulationRun", "nunique"),
                    first_sample=("sample", "min"),
                    last_sample=("sample", "max"),
                    fault_labels=("faultNumber", "nunique"),
                )
                .reset_index()
            )
            split_summary
            """
        ),
        md(
            """
            The row counts reconcile exactly to the publisher's run design: `500 × 500 = 250,000` training rows and `500 × 960 = 480,000` testing rows. This reconciliation is stronger than checking only the final total because it verifies both run count and sequence length.
            """
        ),
        md("### 3. Review the quality scorecard"),
        code("quality"),
        md(
            """
            All critical and high-severity checks pass. No imputation, duplicate removal or row exclusion is required for the normal-operation layer. That result should not be interpreted as proof that future faulty files will pass the same controls; every source file will be audited independently.
            """
        ),
        md("## Results"),
        md(
            """
            ### 4. Validate every run, not only the combined table

            Aggregate row counts can conceal a short run and a duplicated run that happen to offset each other. Run-level validation therefore checks the first sample, last sample, row count, duplicates and sequence gaps for all 1,000 runs.
            """
        ),
        code(
            """
            run_result = (
                integrity.groupby("split")
                .agg(
                    runs=("simulation_run", "size"),
                    complete_runs=("is_complete", "sum"),
                    duplicate_samples=("duplicate_samples", "sum"),
                    missing_sequence_steps=("missing_sequence_steps", "sum"),
                )
                .reset_index()
            )
            run_result["complete_run_rate"] = run_result["complete_runs"] / run_result["runs"]
            run_result
            """
        ),
        md(
            """
            ![Run-level sequence integrity](../images/02_run_sequence_integrity.png)

            **Interpretation.** All 500 training runs and all 500 testing runs are complete. Because no run is excluded, subsequent KPI denominators can be tied directly to the source design without a hidden population adjustment.
            """
        ),
        md(
            """
            ### 5. Test normal-operation transfer before defining alarms

            For each of the 52 signals, the testing median is compared with the training median and divided by the training IQR. This creates a unitless diagnostic that can compare signals measured on different scales.

            It is a descriptive stability check, not an alarm threshold. A small median shift does not prove that covariance, tails or time dependence are identical.
            """
        ),
        code(
            """
            split_comparison[
                ["signal", "training_median", "testing_median", "training_iqr", "median_shift_on_training_iqr"]
            ].head(15)
            """
        ),
        md(
            """
            ![Normal split median stability](../images/02_normal_split_median_stability.png)

            **Observed result.** The largest absolute median shift is approximately 0.019 training IQR. No signal reaches 0.10 training IQR. This supports using the testing split as a normal-operation holdout, while leaving multivariate covariance checks to the statistical-process-control notebook.
            """
        ),
        md(
            """
            ### 6. Profile baseline spread without confusing it with specifications

            IQR describes the middle 50% of the training distribution and is less sensitive to extreme observations than standard deviation. Dividing IQR by the absolute median provides a screening view of relative spread across variables with different units.

            This ratio is used only for prioritisation. Signals with medians close to zero can show a large ratio even when their absolute variation is small.
            """
        ),
        code(
            """
            variability = baseline.copy()
            variability["relative_iqr"] = variability["iqr"] / variability["median"].abs().replace(0, np.nan)
            variability.nlargest(12, "relative_iqr")[
                ["signal", "median", "q1", "q3", "iqr", "relative_iqr"]
            ]
            """
        ),
        md(
            """
            ![Relative baseline spread](../images/02_relative_baseline_spread.png)

            **Interpretation.** `xmeas_37` has the highest relative IQR because its median is close to zero. It must not be labelled unstable based on this ratio alone. The next notebook will evaluate signals jointly after scaling, using covariance-aware statistics rather than separate percentage rules.
            """
        ),
        md(
            """
            ### 7. Preserve a governed baseline contract

            `normal_baseline_statistics.parquet` stores one row per process signal with count, mean, standard deviation, quartiles, median, IQR and robust descriptive references.

            These fields provide a traceable reference for later notebooks. The robust lower and upper values are profiling fences; they are not process-control limits and not product specifications.
            """
        ),
        code(
            """
            baseline[
                [
                    "signal", "count", "mean", "std", "median", "q1", "q3", "iqr",
                    "robust_lower_reference", "robust_upper_reference"
                ]
            ].head(10)
            """
        ),
        md(
            """
            ### 8. Connect Parquet to SQL and Power BI

            Parquet is the governed analytical storage format because it is columnar, compressed and preserves numeric types. DuckDB can query it directly without loading a database server:

            ```sql
            SELECT split, COUNT(*) AS samples, COUNT(DISTINCT simulationRun) AS runs
            FROM read_parquet('data/interim/normal_operation_samples.parquet')
            GROUP BY split;
            ```

            Power BI will consume curated extracts and SQL views rather than the original RData files. This separates source ingestion from presentation and prevents dashboard transformations from becoming the only record of business logic.
            """
        ),
        md("## Takeaways"),
        md(
            """
            1. **The analytical grain is controlled.** The composite key is unique and includes the split identifier.
            2. **The normal-operation source is structurally complete.** All 1,000 runs contain the expected uninterrupted sample sequence.
            3. **No corrective cleaning was needed.** Missing-value treatment, imputation and duplicate removal would add unnecessary transformations.
            4. **Training and testing remain separated.** Training defines the reference; testing measures transfer and false alarms.
            5. **Univariate profiling is not the monitoring solution.** The process is multivariate and coupled, so the next stage must account for covariance and persistent alerts.
            6. **The baseline is suitable for the next stage.** This conclusion applies to internal simulation-data quality, not to real-plant representativeness.
            """
        ),
        md(
            """
            ## Next step

            **Notebook 03 — Statistical Process Control** will:

            - standardise signals using training-only parameters;
            - use PCA to represent correlated process behaviour;
            - calculate Hotelling T² and Q residual monitoring statistics;
            - set candidate limits from the normal-training reference;
            - measure false alarms on normal-testing runs;
            - apply a persistence rule so isolated statistical noise does not become an operating alert;
            - produce the first governed monitoring table for SQL and Power BI.
            """
        ),
    ]
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, DESTINATION)
    return DESTINATION


if __name__ == "__main__":
    print(build())
