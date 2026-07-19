# Chemical Process Performance Analytics

An industrial analytics project connecting chemical engineering, process performance, statistical process control, continuous improvement and business intelligence.

The project uses the **Tennessee Eastman Process** simulation dataset published through Harvard Dataverse. It studies how a multivariate chemical process moves from stable operation to abnormal behaviour, how quickly faults can be detected and which process variables should receive operational attention.

## Business question

How can an operations team monitor process stability, detect abnormal conditions early and prioritise improvement work without creating an excessive false-alarm burden?

## Why this project matters

Industrial performance is not only a modelling problem. A useful solution must connect process signals to operating decisions:

- identify when the process leaves its normal operating envelope;
- measure detection speed and false alarms;
- compare fault types and operating runs consistently;
- explain which measurements contribute most to an alert;
- translate findings into a practical monitoring and control plan.

## Project scope

| Workstream | Deliverable |
| --- | --- |
| Process understanding | Process map, variable dictionary and operating assumptions |
| Data engineering | Reproducible download, validation and Parquet preparation |
| Python analysis | Jupyter notebooks for quality, stability, fault patterns and root-cause evidence |
| SQL | DuckDB model and reusable KPI views |
| Statistical process control | Baseline limits, Hotelling T², Q residuals and alarm persistence |
| Machine learning | Interpretable fault-detection baselines and temporal validation |
| Business intelligence | Power BI monitoring model, dashboard specification and curated extracts |
| Continuous improvement | DMAIC-based prioritisation and control plan |

## Public data source

- **Dataset:** Additional Tennessee Eastman Process Simulation Data for Anomaly Detection Evaluation
- **Publisher:** Harvard Dataverse
- **DOI:** [10.7910/DVN/6C3JR1](https://doi.org/10.7910/DVN/6C3JR1)
- **Source type:** simulated multivariate chemical-process time series
- **Coverage:** normal operation and 20 process-fault scenarios
- **Structure:** 41 measured variables, 11 manipulated variables, simulation run, sample and fault number

The repository does not redistribute the raw source files. Run the download script to obtain them directly from the publisher.

## Decision-focused KPIs

1. **Fault Detection Rate** — percentage of eligible faulty runs in which the monitoring rule raises a confirmed alert.
2. **Median Detection Delay** — median minutes between fault introduction and the first confirmed alert.
3. **False Alarm Rate** — percentage of eligible normal samples that trigger a confirmed alert.
4. **Process Stability Rate** — percentage of eligible samples that remain inside the statistical operating envelope.
5. **Alarm Burden** — confirmed alert events per 100 operating hours.

These are monitoring and decision-support metrics. The source does not contain production volume, scheduled time, good units or cost data, so this project will not present OEE, yield, MTBF, MTTR or financial savings as observed results.

## Planned analysis path

1. Data source and process context
2. Data quality and operating baseline
3. Statistical process control
4. Fault pattern and Pareto analysis
5. Detection model comparison
6. Root-cause evidence and variable contribution
7. Threshold, persistence and workload scenarios
8. Executive findings and control plan

## Current validated evidence

The normal-operation foundation is complete and reproducible:

- 730,000 samples across 1,000 simulation runs;
- 52 expected process signals;
- 100% complete training and testing run sequences;
- no missing signal cells, non-finite values or duplicate composite keys;
- an independent normal-testing split retained for false-alarm evaluation;
- the largest testing-versus-training median shift is approximately 0.019 training IQR.

Read the detailed audit in [Notebook 02 — Data Quality and Operating Baseline](notebooks/02_data_quality_and_operating_baseline.ipynb).

## Repository structure

```text
chemical-process-performance-analytics/
├── config/                  # Project settings and visual palette
├── data/                    # Local raw, interim and processed data
├── docs/                    # Source, KPI, dashboard and project documentation
├── images/                  # Exported analytical figures
├── notebooks/               # Reader-facing Jupyter analysis
├── powerbi/                 # Model and dashboard handoff files
├── scripts/                 # Download and notebook build utilities
├── sql/                     # DuckDB schema and reusable KPI views
├── src/                     # Reusable Python modules
└── tests/                   # Metric and transformation checks
```

## Technology

Python · Pandas · NumPy · scikit-learn · Plotly · Jupyter · SQL · DuckDB · Parquet · Power BI · Power Query · GitHub

## Continuous-improvement frame

The project follows DMAIC without presenting simulated improvement as a real plant result:

- **Define:** delayed detection and excessive alarms as the operating problem;
- **Measure:** establish stable-operation and alerting baselines;
- **Analyse:** identify difficult faults and the variables driving abnormal behaviour;
- **Improve:** compare monitoring thresholds and persistence rules;
- **Control:** publish KPI definitions, SQL views, dashboard monitoring and response guidance.

## Status

**Phase 2 — Normal operating baseline validated.** Statistical process control and fault-file ingestion are the next active workstreams.
