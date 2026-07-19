# Data Source and Scope

## Authoritative source

**Additional Tennessee Eastman Process Simulation Data for Anomaly Detection Evaluation**  
Harvard Dataverse · DOI: [10.7910/DVN/6C3JR1](https://doi.org/10.7910/DVN/6C3JR1)

The data accompany Rieth et al. (2017) and provide repeated Tennessee Eastman Process simulations for evaluating anomaly-detection and fault-monitoring methods.

## Process context

The Tennessee Eastman Process is a benchmark chemical-process simulation with interconnected units including a reactor, condenser, compressor, vapour-liquid separator and stripper. Its multivariate dynamics make it useful for process monitoring, fault detection and diagnostic analysis.

## Expected source structure

Each published data frame contains 55 columns:

- `faultNumber` — normal operation (`0`) or one of 20 fault scenarios;
- `simulationRun` — independent simulation run identifier;
- `sample` — sequential three-minute sample;
- `xmeas_1` to `xmeas_41` — measured process variables;
- `xmv_1` to `xmv_11` — manipulated process variables.

Training runs contain 500 samples and testing runs contain 960 samples. The source documentation states that faults are introduced after an initial normal operating period. The exact onset rule will be validated against the downloaded metadata before KPI calculations are finalised.

## Use policy

- Download files directly from Harvard Dataverse.
- Keep raw files outside Git version control.
- Store the DOI, publisher, retrieval timestamp and file checksum.
- Preserve original column names in the raw layer.
- Add readable engineering labels only in curated metadata.
- Never call a statistical control limit an engineering specification limit.

## Important limitation

This is simulated process data. It is appropriate for method development and portfolio demonstration, but it does not prove performance in an operating plant. The dashboard will label the source as simulation data in every public-facing view.

