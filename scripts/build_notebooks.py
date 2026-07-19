"""Build the reader-facing Jupyter notebooks with nbformat."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"


def markdown(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(source: str):
    return nbf.v4.new_code_cell(dedent(source).strip())


def build_source_context_notebook() -> Path:
    notebook = nbf.v4.new_notebook()
    notebook["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
    }
    notebook["cells"] = [
        markdown(
            """
            # 01 · Data source and chemical-process context

            **Goal.** Establish a reproducible source record, verify the expected dataset contract and frame the operating problem before any model is trained.

            This notebook is intentionally evidence-first. It does not report a performance result until the publisher-supplied files are present and pass the schema checks.
            """
        ),
        markdown(
            """
            ## Decision context

            The Tennessee Eastman Process is a simulated multivariate chemical process with a reactor, condenser, compressor, separator and stripper. The portfolio project asks:

            > How can an operations team monitor process stability, detect abnormal conditions early and prioritise improvement work without creating an excessive false-alarm burden?

            The analytical unit is a timestamped process sample within a simulation run. Results will be compared by fault type, run and monitoring method.
            """
        ),
        code(
            """
            from pathlib import Path
            import json
            import sys

            import matplotlib.pyplot as plt
            import pandas as pd

            PROJECT_ROOT = Path.cwd().resolve().parent if Path.cwd().name == "notebooks" else Path.cwd().resolve()
            SRC = PROJECT_ROOT / "src"
            if str(SRC) not in sys.path:
                sys.path.insert(0, str(SRC))

            RAW_DIR = PROJECT_ROOT / "data" / "raw"
            MANIFEST = RAW_DIR / "source_manifest.json"
            PALETTE = {
                "navy": "#14213D",
                "teal": "#2A9D8F",
                "guava": "#F08FA0",
                "sand": "#F6F1EC",
                "amber": "#E9C46A",
                "steel": "#607A80",
            }
            """
        ),
        markdown(
            """
            ## Source record

            - **Publisher:** Harvard Dataverse
            - **Dataset:** Additional Tennessee Eastman Process Simulation Data for Anomaly Detection Evaluation
            - **DOI:** [10.7910/DVN/6C3JR1](https://doi.org/10.7910/DVN/6C3JR1)
            - **Sampling interval:** 3 minutes
            - **Expected signals:** 41 measured variables and 11 manipulated variables
            - **Operating labels:** normal operation plus 20 simulated fault scenarios

            The source is a process simulation, not observed production from a named plant. That boundary will remain visible throughout the analysis.
            """
        ),
        code(
            """
            source_contract = pd.DataFrame(
                {
                    "Variable family": ["Measured process variables", "Manipulated variables"],
                    "Count": [41, 11],
                    "Role": ["Process response and state", "Control actions"],
                }
            )
            source_contract
            """
        ),
        code(
            """
            fig, ax = plt.subplots(figsize=(8, 3.8))
            bars = ax.barh(
                source_contract["Variable family"],
                source_contract["Count"],
                color=[PALETTE["teal"], PALETTE["guava"]],
            )
            ax.bar_label(bars, padding=5, fontsize=11)
            ax.set_title("Documented process-signal families", loc="left", color=PALETTE["navy"], weight="bold")
            ax.set_xlabel("Number of variables")
            ax.spines[["top", "right", "left"]].set_visible(False)
            ax.grid(axis="x", alpha=0.2)
            plt.tight_layout()
            plt.show()
            """
        ),
        markdown(
            """
            ## Reproducibility checkpoint

            Raw files are deliberately excluded from Git. Download them directly from Harvard Dataverse:

            ```bash
            python scripts/download_data.py
            ```

            The script writes `data/raw/source_manifest.json` with source identifiers, retrieval time and SHA-256 checksums.
            """
        ),
        code(
            """
            raw_files = sorted(RAW_DIR.glob("*.RData")) + sorted(RAW_DIR.glob("*.rdata"))

            if MANIFEST.exists():
                manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
                manifest_summary = pd.DataFrame(manifest["files"])[
                    ["filename", "size_bytes", "sha256", "status"]
                ]
                display(manifest_summary)
            else:
                print("Source manifest not found. Run: python scripts/download_data.py")

            print(f"RData source files available: {len(raw_files)}")
            """
        ),
        markdown(
            """
            ## Schema validation

            The following cell runs only when publisher files are present. It checks the three identifiers, the 52 expected process signals and missing identifiers before showing a bounded structural summary.
            """
        ),
        code(
            """
            if raw_files:
                from chemical_process_analytics.data_io import load_raw_directory

                process = load_raw_directory(RAW_DIR)
                signal_columns = [
                    column for column in process
                    if column.lower().startswith(("xmeas", "xmv"))
                ]
                validation_summary = pd.Series(
                    {
                        "rows": len(process),
                        "columns": process.shape[1],
                        "process_signals": len(signal_columns),
                        "simulation_runs": process["simulationRun"].nunique(),
                        "fault_labels": process["faultNumber"].nunique(),
                        "missing_identifier_cells": int(
                            process[["faultNumber", "simulationRun", "sample"]].isna().sum().sum()
                        ),
                    },
                    name="value",
                )
                display(validation_summary.to_frame())
                display(process.head(3))
            else:
                print("Validation skipped because no raw RData files are present.")
            """
        ),
        markdown(
            """
            ## Analytical boundaries

            The source supports process-stability, detection-delay, false-alarm and alert-workload analysis. It does **not** provide observed good units, scheduled operating time, maintenance-event duration or financial values. Consequently, OEE, yield, MTBF, MTTR and cost savings will not be presented as measured outcomes.

            **Next notebook:** establish data quality rules and define the normal-operation baseline used by the monitoring methods.
            """
        ),
    ]

    NOTEBOOKS.mkdir(parents=True, exist_ok=True)
    destination = NOTEBOOKS / "01_data_source_and_process_context.ipynb"
    nbf.write(notebook, destination)
    return destination


if __name__ == "__main__":
    print(build_source_context_notebook())
