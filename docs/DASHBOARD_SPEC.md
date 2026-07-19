# Power BI Dashboard Specification

## Audience

Operations, process engineering, quality, reliability and performance-management teams.

## Visual identity

| Role | Colour |
| --- | --- |
| Primary | Midnight Navy `#14213D` |
| Stable operation | Industrial Teal `#2A9D8F` |
| Attention / brand accent | Guava `#F08FA0` |
| Warning | Amber `#E9C46A` |
| Background | Warm Sand `#F6F1EC` |
| Secondary text | Steel `#607A80` |

The palette is distinct from the retail dashboard while retaining the guava accent associated with NOA Data Studio.

## Page 1 — Executive Performance Overview

**Purpose:** show whether the monitoring design is operationally useful before the viewer explores details.

Hero metrics:

- Fault Detection Rate
- Median Detection Delay
- False Alarm Rate
- Process Stability Rate
- Alarm Burden

Charts:

- Detection coverage versus false-alarm burden by monitoring method
- Fault priority matrix: detection delay versus undetected-run rate
- Pareto of alert events by fault type
- Operating envelope summary with clear simulation-data label

## Page 2 — Process Stability

- Hotelling T² trend with confirmed alerts
- Q residual trend with confirmed alerts
- Measured-variable deviation heatmap
- Stable versus abnormal operating time
- Filters: data split, simulation run, operating segment

## Page 3 — Fault Performance

- Fault Detection Rate by fault type
- Median Detection Delay by fault type
- Undetected runs by fault type
- Detection-performance detail table
- Filters: fault number, monitoring method, run

## Page 4 — Root-Cause Evidence

- Top contributing variables by fault type
- Variable contribution heatmap
- Before/after onset small multiples for selected signals
- Engineering notes panel separating evidence from interpretation

## Page 5 — Improvement Priorities

- Fault-priority matrix
- Alarm-threshold and persistence scenario comparison
- DMAIC backlog with evidence, proposed action and validation measure
- Control-plan table with KPI, cadence, owner role and response trigger

## Page 6 — Data Quality and Method

- Source coverage and file checksums
- Run and sample completeness
- Training/testing separation
- Metric definitions and known limitations
- Dataset citation and refresh timestamp

## Interaction rules

- Default view must be useful without filters.
- Filters should affect every compatible visual on the page.
- All fault charts must show both the fault number and a readable description where verified metadata are available.
- Tooltips should include numerator, denominator and eligible-run count.
- External links should open the source DOI and GitHub methodology documentation.

