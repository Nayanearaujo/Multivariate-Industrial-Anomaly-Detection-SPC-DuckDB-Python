"""Build Notebook 01 as a detailed source and process-context report."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "notebooks" / "01_data_source_and_process_context.ipynb"


def md(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip())


def build_source_context_notebook() -> Path:
    notebook = nbf.v4.new_notebook()
    notebook["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
    }
    notebook["cells"] = [
        md(
            """
            # 01 · Data source and chemical-process context

            **Purpose.** Establish why the process matters, what the source represents and which decisions the analytical system may support before any model is fitted.

            This notebook connects chemical-process behaviour, source governance, analytical grain and the future monitoring workflow. It is the project charter in executable form.
            """
        ),
        md(
            """
            ## tl;dr

            The project uses the Tennessee Eastman Process simulation published through Harvard Dataverse. The source represents an interconnected chemical process with reactor, condenser, separator, recycle compressor and stripper operations.

            The published structure provides **41 measured variables**, **11 manipulated variables**, repeated simulation runs, normal operation and 20 fault scenarios at three-minute intervals.

            **Decision frame.** The project will measure whether abnormal behaviour can be detected consistently and early without creating an impractical alert workload. It will not present simulated results as observed plant savings, product quality or maintenance performance.
            """
        ),
        md("## Context & methods"),
        md(
            """
            ### Business question

            > How can an operations team monitor process stability, detect abnormal conditions early and prioritise improvement work without creating an excessive false-alarm burden?

            The question deliberately includes both detection performance and operational workload. A method that identifies faults but continuously interrupts operators is not an effective control system.
            """
        ),
        md(
            """
            ### Process context

            The Tennessee Eastman Process is a benchmark simulation originally designed as a plant-wide process-control challenge. Reactants A, C, D and E are converted into products G and H, with additional inert and by-product behaviour. Material and energy interactions pass through multiple controlled units and a recycle loop.

            Original process reference: [Downs and Vogel (1993), *A plant-wide industrial process control problem*](https://doi.org/10.1016/0098-1354(93)80018-I).
            """
        ),
        md(
            """
            ![Simplified Tennessee Eastman process context](../images/01_process_context.png)

            **Why this matters analytically.** A disturbance may first appear in one measurement and then propagate through pressure, temperature, composition, flow and manipulated control actions. Independent limits applied to each variable can therefore miss the multivariate structure or generate repeated alarms for the same event.
            """
        ),
        md(
            """
            ### Unit-operation view

            | Process area | Operating role | Monitoring relevance |
            | --- | --- | --- |
            | Reactor | Converts reactants through coupled reactions | Temperature, pressure, composition and feed interactions |
            | Condenser | Removes heat and supports phase change | Cooling response and downstream separation stability |
            | Vapour-liquid separator | Separates phases after reaction and condensation | Level, pressure, recycle and underflow behaviour |
            | Recycle compressor | Returns unreacted material to the process | Feedback effects and disturbance propagation |
            | Stripper | Recovers products and removes lighter components | Product flow, steam demand, temperature and level response |

            This is a simplified operating interpretation. It supports analytical communication but does not replace the full process model or operating procedures.
            """
        ),
        md("### Source governance"),
        md(
            """
            - **Publisher:** Harvard Dataverse
            - **Dataset:** Additional Tennessee Eastman Process Simulation Data for Anomaly Detection Evaluation
            - **DOI:** [10.7910/DVN/6C3JR1](https://doi.org/10.7910/DVN/6C3JR1)
            - **Source format:** RData
            - **Source type:** repeated process simulation
            - **Sampling interval:** three minutes
            - **Operating labels:** normal operation plus 20 fault scenarios

            Raw files are downloaded directly from the publisher, retained unchanged and excluded from Git. Derived files record their source filename, size and SHA-256 checksum.
            """
        ),
        md(
            """
            ### Key assumptions

            - `faultNumber = 0` identifies normal simulated operation.
            - `simulationRun` identifies an independent run within a source split.
            - `sample` is sequential and is converted to elapsed minutes using the three-minute interval.
            - Training data define analytical references; testing data remain independent for evaluation.
            - Source labels indicate simulated fault scenarios, not confirmed maintenance work orders.
            - Statistical alert limits are not engineering specification limits.
            """
        ),
        md("## Data"),
        md("### 1. Configure source and project paths"),
        code(
            """
            from pathlib import Path
            import json
            import sys

            import pandas as pd

            PROJECT_ROOT = Path.cwd().resolve().parent if Path.cwd().name == "notebooks" else Path.cwd().resolve()
            RAW = PROJECT_ROOT / "data" / "raw"
            INTERIM = PROJECT_ROOT / "data" / "interim"
            PROCESSED = PROJECT_ROOT / "data" / "processed"
            SRC = PROJECT_ROOT / "src"
            if str(SRC) not in sys.path:
                sys.path.insert(0, str(SRC))

            SOURCE_DOI = "10.7910/DVN/6C3JR1"
            SAMPLE_INTERVAL_MINUTES = 3
            """
        ),
        md("### 2. Define the publisher's data contract"),
        code(
            """
            source_contract = pd.DataFrame(
                {
                    "field_group": ["Identifiers", "Measured variables", "Manipulated variables"],
                    "columns": [3, 41, 11],
                    "examples": ["faultNumber, simulationRun, sample", "xmeas_1 ... xmeas_41", "xmv_1 ... xmv_11"],
                    "analytical_role": ["Grain, sequence and outcome label", "Process response and state", "Control actions"],
                }
            )
            source_contract
            """
        ),
        md(
            """
            `xmeas` and `xmv` names are preserved in the analytical layer. Readable engineering descriptions will be attached through metadata rather than replacing the source fields. This protects traceability between notebooks, SQL and future Power BI visuals.
            """
        ),
        md("### 3. Record the validated normal-operation inventory"),
        code(
            """
            audit_path = PROCESSED / "normal_baseline_audit.json"
            if audit_path.exists():
                audit = json.loads(audit_path.read_text(encoding="utf-8"))
                inventory = pd.DataFrame(audit["source_files"])
                display(inventory[["split", "filename", "size_bytes", "sha256"]])
                display(pd.DataFrame(audit["run_summary"]))
            else:
                print("Normal-operation audit not built. Run: python scripts/prepare_normal_baseline.py")
            """
        ),
        md(
            """
            The validated normal files contain 730,000 rows across 1,000 complete runs. Fault files are governed separately and are not treated as available until their downloads and checksums are complete.
            """
        ),
        md("### 4. Establish the analytical grain"),
        md(
            """
            One analytical row represents one process observation within one run and one source split.

            ```text
            split + simulationRun + sample
            ```

            Including `split` is essential because run identifiers restart between training and testing. The derived `elapsed_minutes` field is calculated as `(sample - 1) × 3` and never replaces the original sequence field.
            """
        ),
        md("### 5. Inspect the curated layer when available"),
        code(
            """
            curated_path = INTERIM / "normal_operation_samples.parquet"
            if curated_path.exists():
                normal = pd.read_parquet(curated_path)
                signal_columns = [column for column in normal if column.startswith(("xmeas_", "xmv_"))]
                structural_summary = pd.Series(
                    {
                        "rows": len(normal),
                        "columns": normal.shape[1],
                        "process_signals": len(signal_columns),
                        "splits": normal["split"].nunique(),
                        "runs_across_splits": normal[["split", "simulationRun"]].drop_duplicates().shape[0],
                        "fault_labels": normal["faultNumber"].nunique(),
                    },
                    name="observed",
                )
                display(structural_summary.to_frame())
                display(normal[["split", "simulationRun", "sample", "elapsed_minutes", "faultNumber"]].head(5))
            else:
                print("Curated Parquet layer not found. Run: python scripts/prepare_normal_baseline.py")
            """
        ),
        md("## Results"),
        md(
            """
            ### 6. Separate source evidence from presentation

            ![Data-to-decision lineage](../images/01_data_to_decision_lineage.png)

            The dashboard will not read or transform the publisher's RData files directly. Python owns source validation and preparation; Parquet and DuckDB own the reusable analytical layer; Power BI presents governed measures and operating views.
            """
        ),
        md(
            """
            ### 7. Define what the source can support

            | Supported evidence | Reason |
            | --- | --- |
            | Process stability | Repeated multivariate samples under normal and faulty conditions |
            | Fault detection rate | Known simulated fault labels and repeated runs |
            | Detection delay | Ordered samples and documented three-minute interval |
            | False-alarm rate | Independent fault-free testing runs |
            | Alarm burden | Consecutive alert samples can be grouped into events |
            | Variable contribution | Measured and manipulated signals are retained |
            """
        ),
        md(
            """
            ### 8. Define what the source cannot support

            The source does not include good units, total production, planned operating time, maintenance start and finish timestamps, product specifications or financial values.

            Therefore the project will not report observed OEE, yield, MTBF, MTTR, downtime savings or financial benefit. If those measures appear later, they must be labelled as scenario assumptions and kept separate from observed analytical results.
            """
        ),
        md(
            """
            ### 9. Connect analysis to continuous improvement

            | DMAIC stage | Project contribution |
            | --- | --- |
            | Define | Delayed fault recognition and excessive alarm workload |
            | Measure | Normal baseline, detection rate, delay and false alarms |
            | Analyse | Fault Pareto, multivariate statistics and contributing variables |
            | Improve | Threshold and persistence scenarios at equal workload |
            | Control | SQL views, Power BI monitoring and documented response rules |

            DMAIC structures the decision path. It does not convert a simulation into a completed plant-improvement claim.
            """
        ),
        md("## Takeaways"),
        md(
            """
            1. The dataset is relevant because it represents an interconnected process-control problem, not an isolated classification table.
            2. The analytical grain, source split and sample interval are explicit before modelling begins.
            3. Raw source, transformation logic and dashboard presentation have separate responsibilities.
            4. The project will balance detection performance with alert workload.
            5. Claims are limited to what simulation data can support.
            6. Normal and faulty files are admitted only after file-level and run-level validation.
            """
        ),
        md(
            """
            ## Next step

            **Notebook 02 — Data Quality and Normal Operating Baseline** tests completeness, uniqueness, run continuity, numeric validity, signal variability and training-versus-testing stability. Only after those checks pass can the training data define a statistical monitoring reference.
            """
        ),
    ]
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, DESTINATION)
    return DESTINATION


if __name__ == "__main__":
    print(build_source_context_notebook())
