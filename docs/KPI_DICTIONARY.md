# KPI Dictionary

The monitoring framework uses a small set of decision-focused KPIs. Firm targets will be set only after the normal-operation baseline and validation results are available.

## Primary KPIs

### 1. Fault Detection Rate

**Question:** How consistently does the monitoring rule identify a fault?  
**Definition:** Faulty runs with at least one confirmed post-onset alert divided by eligible faulty runs.  
**Grain:** fault type and simulation run.  
**Direction:** higher is better.  
**Guardrail:** report together with false alarm rate and detection delay.

### 2. Median Detection Delay

**Question:** How long does the system take to identify abnormal behaviour?  
**Definition:** Median elapsed minutes from documented fault onset to the first confirmed alert among detected runs.  
**Grain:** fault type and simulation run.  
**Direction:** lower is better.  
**Guardrail:** always report the undetected-run count.

### 3. False Alarm Rate

**Question:** How often does the monitoring rule interrupt normal operation unnecessarily?  
**Definition:** Confirmed alert samples during eligible normal operation divided by eligible normal samples.  
**Grain:** simulation run and monitoring method.  
**Direction:** lower is better.  
**Guardrail:** use an explicit persistence rule so isolated statistical noise is not counted as an operating event.

### 4. Process Stability Rate

**Question:** What share of eligible operation remains within the learned statistical operating envelope?  
**Definition:** Samples without a confirmed multivariate alert divided by eligible samples.  
**Grain:** simulation run, fault type and operating segment.  
**Direction:** higher is better for normal operation.  
**Caveat:** this is a statistical stability measure, not conformance to product specifications.

### 5. Alarm Burden

**Question:** What workload does the monitoring design create?  
**Definition:** Distinct confirmed alert events per 100 simulated operating hours. Adjacent alert samples are grouped into one event.  
**Grain:** monitoring method, run and fault type.  
**Direction:** contextual; lower is preferable when detection performance is maintained.

## Diagnostic metrics

- Fault-level recall and precision
- Average Run Length under normal operation (`ARL0`)
- Average Run Length after fault onset (`ARL1`)
- Share of runs not detected
- Variable deviation burden per alert event
- Top contributing variables by fault type
- Alert persistence and duration
- Data completeness by source file and run

## Metrics intentionally excluded

The source does not include the fields required for observed OEE, yield, production volume, good units, planned operating time, maintenance duration, MTBF, MTTR or financial savings. These terms must not appear as calculated results unless a future source adds the required denominators and event records.

