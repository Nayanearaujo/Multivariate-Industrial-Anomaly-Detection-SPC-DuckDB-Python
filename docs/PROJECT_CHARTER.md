# Project Charter

## Project

Chemical Process Performance Analytics

## Operating problem

Complex industrial processes generate many correlated measurements. A single limit violation may be noise, while a real disturbance can propagate across units before becoming obvious. Operations teams therefore need monitoring that detects meaningful abnormal behaviour early without creating an unmanageable alarm queue.

## Audience

- operations and performance managers;
- process and quality engineers;
- continuous-improvement teams;
- maintenance and reliability teams;
- BI and analytics teams supporting manufacturing.

## Decisions supported

1. Which fault scenarios are detected reliably and which require further investigation?
2. How quickly does the monitoring approach detect each fault after introduction?
3. What threshold and persistence rule balances detection coverage and false alarms?
4. Which measured or manipulated variables contribute most to each fault pattern?
5. Which problems should enter the improvement backlog first?

## Deliverables

- eight reproducible Jupyter notebooks;
- processed Parquet datasets and a DuckDB analytical model;
- SQL views for run, fault and alert performance;
- documented KPI definitions and limitations;
- Power BI semantic-model specification and dashboard pages;
- figures suitable for GitHub and LinkedIn;
- executive summary and DMAIC control plan.

## Success criteria

- every reported metric traces to a documented calculation;
- normal and faulty simulations remain separated during temporal validation;
- model results are reported by fault type, not only as an overall average;
- false alarms and detection delay appear alongside detection coverage;
- no financial or production claim is made without corresponding source fields;
- another analyst can reproduce the workflow from a clean environment.

## Out of scope

- claiming plant savings, production yield or OEE from unavailable source fields;
- presenting simulation results as evidence from a real factory;
- deploying an autonomous process-control system;
- prescribing safety actions without plant-specific engineering review.

