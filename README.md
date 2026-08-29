# Chemical Process Performance Analytics

An industrial analytics project connecting chemical engineering, process performance, statistical process control, continuous improvement, and business intelligence.

The project uses the **Tennessee Eastman Process** simulation dataset published through Harvard Dataverse to study how a multivariate chemical process moves from stable operation to abnormal behaviour, how quickly faults can be detected, and which process variables require operational attention.

## Objectives

The goal is to answer a core operational question: **How can an operations team monitor process stability, detect abnormal conditions early, and prioritise improvement work without creating an excessive false-alarm burden?**

To achieve this, the project connects raw process signals to operational decisions by:
1. Defining statistical normal operating envelopes.
2. Measuring detection speed (delay) and false-alarm frequency.
3. Structuring consistent performance comparisons across different fault types and operating runs.
4. Mapping which process measurements drive specific anomaly alerts.
5. Providing structured inputs for a practical monitoring and control dashboard.

## Technology Stack

* **Language/Processing:** Python, Pandas, NumPy, scikit-learn
* **Database & SQL:** DuckDB, Parquet
* **Visualization & Reporting:** Power BI, Power Query, Plotly, Jupyter Notebooks

## Repository Structure

```text
chemical-process-performance-analytics/
├── config/                  # Visual palettes and configurations
├── data/                    # Raw, interim, and processed datasets
├── docs/                    # Dashboards, KPIs, and project specifications
├── images/                  # Exported plots and analytics charts
├── notebooks/               # Step-by-step Jupyter notebooks
├── powerbi/                 # Power BI files and data models
├── scripts/                 # Download, processing, and build utilities
├── sql/                     # DuckDB database schema and KPI views
├── src/                     # Shared Python library modules
└── tests/                   # Code and metric integrity checks
```

## Data Source

* **Dataset:** Additional Tennessee Eastman Process Simulation Data for Anomaly Detection Evaluation
* **Publisher:** Harvard Dataverse
* **DOI:** [10.7910/DVN/6C3JR1](https://doi.org/10.7910/DVN/6C3JR1)
* **Format:** Multivariate time series representing normal operation and 20 distinct process-fault scenarios.
* **Signals:** 41 measured variables, 11 manipulated variables, plus simulation metadata (run, sample, fault number).

*Note: Raw source files are not tracked in this repository. Follow the setup steps below to download them directly from the source.*

## How to Reproduce

### 1. Environment Setup
Clone the repository and install the dependencies:
```bash
git clone https://github.com/Nayanearaujo/chemical-process-performance-analytics.git
cd chemical-process-performance-analytics
pip install -r requirements.txt
```

### 2. Download Raw Data
Download the Tennessee Eastman datasets from Harvard Dataverse:
```bash
python scripts/download_data.py
```
This script downloads the raw `.RData` files into `data/raw/` and generates `source_manifest.json` with checksums for verification.

### 3. Build the Normal-Operation Baseline
Run the preprocessing script to clean, validate, and prepare the normal-operation baseline:
```bash
python scripts/prepare_normal_baseline.py
```
This exports processed `.parquet` files and updates the baseline audit in `data/processed/normal_baseline_audit.json`.

---

## Decision-Focused KPIs

The project evaluates performance using five operational metrics:

1. **Fault Detection Rate (FDR):** Percentage of eligible faulty runs that trigger a confirmed alert.
2. **Median Detection Delay:** Median time (in minutes) from fault onset to the first confirmed alert.
3. **False Alarm Rate (FAR):** Percentage of normal-operation samples that trigger a false alert.
4. **Process Stability Rate:** Percentage of samples that remain within the defined statistical envelope.
5. **Alarm Burden:** Count of confirmed alerts per 100 operating hours.

*Note: Because the Tennessee Eastman simulation does not model production volumes, costs, or repair events, this project does not track financial savings, yield, OEE, MTTR, or MTBF.*

## Development & Analysis Path

1. **Context & Setup:** Data source mapping and process boundaries.
2. **Data Quality & Baseline:** Validating training/testing datasets.
3. **Statistical Process Control:** Defining Hotelling $T^2$ and Q-residual thresholds.
4. **Pattern Analysis:** Pareto charts of faults and alarm occurrences.
5. **Model Evaluation:** Performance comparison of detection methods.
6. **Root Cause Analysis:** Contribution plots to isolate driving variables.
7. **Operational Tuning:** Sensitivity analysis on alert persistence rules.
8. **Control Plan:** Control charts, SQL views, and dashboard specifications.

## Current Project Status

**Phase 2 - Baseline Validated**
* Loaded and verified 730,000 samples across 1,000 simulation runs.
* Confirmed 52 process signals with 0 missing, non-finite, or duplicated keys.
* Established the normal-testing partition for false-alarm testing.
* Validated that the maximum training-to-testing median shift is minimal (approx. 0.019 IQR).

You can review the full data audit in [Notebook 02 - Data Quality and Operating Baseline](notebooks/02_data_quality_and_operating_baseline.ipynb).

## Continuous Improvement (DMAIC) Framework

The analysis steps are structured using the DMAIC method:
* **Define:** Scope detection delays and false alerts as the core problem.
* **Measure:** Establish base metrics under stable operating conditions.
* **Analyse:** Identify difficult-to-detect faults and pinpoint variables driving deviation.
* **Improve:** Evaluate alarm persistence filters to balance sensitivity and workload.
* **Control:** Provide KPI views, SQL scripts, and Power BI specifications for production monitoring.