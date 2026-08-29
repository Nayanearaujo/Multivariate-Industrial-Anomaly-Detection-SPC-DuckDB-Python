"""Generate Power BI dimension and fact tables for industrial anomaly analytics."""

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

# 1. Dimension: Faults (20 Fault scenarios in Tennessee Eastman Process)
FAULTS = [
    {"fault_id": 0, "fault_code": "Fault 0", "fault_name": "Normal Operation", "fault_type": "Baseline", "description": "Steady-state normal chemical plant operation without deliberate disturbance."},
    {"fault_id": 1, "fault_code": "Fault 1", "fault_name": "A/C Feed Ratio Step", "fault_type": "Step Disturbance", "description": "Step change in A/C feed ratio with B composition held constant in Stream 4."},
    {"fault_id": 2, "fault_code": "Fault 2", "fault_name": "B Composition Step", "fault_type": "Step Disturbance", "description": "Step change in B composition with A/C ratio constant in Stream 4."},
    {"fault_id": 3, "fault_code": "Fault 3", "fault_name": "D Feed Temperature Step", "fault_type": "Step Disturbance", "description": "Step change in D feed temperature in Stream 2."},
    {"fault_id": 4, "fault_code": "Fault 4", "fault_name": "Reactor Cooling Inlet Temp Step", "fault_type": "Step Disturbance", "description": "Step change in reactor cooling water inlet temperature."},
    {"fault_id": 5, "fault_code": "Fault 5", "fault_name": "Condenser Cooling Inlet Temp Step", "fault_type": "Step Disturbance", "description": "Step change in condenser cooling water inlet temperature."},
    {"fault_id": 6, "fault_code": "Fault 6", "fault_name": "A Feed Loss Step", "fault_type": "Step Disturbance", "description": "Loss of reactant A feed in Stream 1."},
    {"fault_id": 7, "fault_code": "Fault 7", "fault_name": "C Header Pressure Loss", "fault_type": "Step Disturbance", "description": "Loss of C feed header pressure in Stream 4."},
    {"fault_id": 8, "fault_code": "Fault 8", "fault_name": "A, B, C Feed Variations", "fault_type": "Random Variation", "description": "Random variation in A, B, and C feed composition in Stream 4."},
    {"fault_id": 9, "fault_code": "Fault 9", "fault_name": "D Feed Temp Random Variation", "fault_type": "Random Variation", "description": "Random variation in D feed temperature in Stream 2."},
    {"fault_id": 10, "fault_code": "Fault 10", "fault_name": "C Feed Temp Random Variation", "fault_type": "Random Variation", "description": "Random variation in C feed temperature in Stream 4."},
    {"fault_id": 11, "fault_code": "Fault 11", "fault_name": "Reactor Cooling Temp Variation", "fault_type": "Random Variation", "description": "Random variation in reactor cooling water inlet temperature."},
    {"fault_id": 12, "fault_code": "Fault 12", "fault_name": "Condenser Cooling Temp Variation", "fault_type": "Random Variation", "description": "Random variation in condenser cooling water inlet temperature."},
    {"fault_id": 13, "fault_code": "Fault 13", "fault_name": "Reaction Kinetics Drift", "fault_type": "Slow Drift", "description": "Slow drift in primary reaction kinetics parameter."},
    {"fault_id": 14, "fault_code": "Fault 14", "fault_name": "Reactor Cooling Valve Sticking", "fault_type": "Mechanical Fault", "description": "Sticking mechanical fault in reactor cooling water valve."},
    {"fault_id": 15, "fault_code": "Fault 15", "fault_name": "Condenser Cooling Valve Sticking", "fault_type": "Mechanical Fault", "description": "Sticking mechanical fault in condenser cooling water valve."},
    {"fault_id": 16, "fault_code": "Fault 16", "fault_name": "Unknown Disturbance 16", "fault_type": "Unspecified", "description": "Unmodeled process disturbance scenario 16."},
    {"fault_id": 17, "fault_code": "Fault 17", "fault_name": "Unknown Disturbance 17", "fault_type": "Unspecified", "description": "Unmodeled process disturbance scenario 17."},
    {"fault_id": 18, "fault_code": "Fault 18", "fault_name": "Unknown Disturbance 18", "fault_type": "Unspecified", "description": "Unmodeled process disturbance scenario 18."},
    {"fault_id": 19, "fault_code": "Fault 19", "fault_name": "Unknown Disturbance 19", "fault_type": "Unspecified", "description": "Unmodeled process disturbance scenario 19."},
    {"fault_id": 20, "fault_code": "Fault 20", "fault_name": "Unknown Disturbance 20", "fault_type": "Unspecified", "description": "Unmodeled process disturbance scenario 20."}
]

# 2. Dimension: Variables (41 measured + 11 manipulated)
VARIABLE_METADATA = [
    # Continuous Process Measurements (xmeas 1-22)
    (1, "A Feed (Stream 1)", "kscmh", "Flow Rate", "Continuous Process"),
    (2, "D Feed (Stream 2)", "kg/h", "Flow Rate", "Continuous Process"),
    (3, "E Feed (Stream 3)", "kg/h", "Flow Rate", "Continuous Process"),
    (4, "Total Feed (Stream 4)", "kscmh", "Flow Rate", "Continuous Process"),
    (5, "Recycle Flow (Stream 8)", "kscmh", "Flow Rate", "Continuous Process"),
    (6, "Reactor Feed Rate (Stream 6)", "kscmh", "Flow Rate", "Continuous Process"),
    (7, "Reactor Pressure", "kPa gauge", "Pressure", "Continuous Process"),
    (8, "Reactor Level", "%", "Level", "Continuous Process"),
    (9, "Reactor Temperature", "Deg C", "Temperature", "Continuous Process"),
    (10, "Purge Rate (Stream 9)", "kscmh", "Flow Rate", "Continuous Process"),
    (11, "Product Separator Temperature", "Deg C", "Temperature", "Continuous Process"),
    (12, "Product Separator Level", "%", "Level", "Continuous Process"),
    (13, "Product Separator Pressure", "kPa gauge", "Pressure", "Continuous Process"),
    (14, "Product Separator Underflow", "m3/h", "Flow Rate", "Continuous Process"),
    (15, "Stripper Level", "%", "Level", "Continuous Process"),
    (16, "Stripper Pressure", "kPa gauge", "Pressure", "Continuous Process"),
    (17, "Stripper Underflow (Stream 11)", "m3/h", "Flow Rate", "Continuous Process"),
    (18, "Stripper Temperature", "Deg C", "Temperature", "Continuous Process"),
    (19, "Stripper Steam Flow", "kg/h", "Flow Rate", "Continuous Process"),
    (20, "Compressor Work", "kW", "Power", "Continuous Process"),
    (21, "Reactor Cooling Water Outlet Temp", "Deg C", "Temperature", "Continuous Process"),
    (22, "Separator Cooling Water Outlet Temp", "Deg C", "Temperature", "Continuous Process"),
    # Sampled Compositions (xmeas 23-41)
    (23, "Component A in Reactor Feed", "mol %", "Composition", "Sampled Stream 6"),
    (24, "Component B in Reactor Feed", "mol %", "Composition", "Sampled Stream 6"),
    (25, "Component C in Reactor Feed", "mol %", "Composition", "Sampled Stream 6"),
    (26, "Component D in Reactor Feed", "mol %", "Composition", "Sampled Stream 6"),
    (27, "Component E in Reactor Feed", "mol %", "Composition", "Sampled Stream 6"),
    (28, "Component F in Reactor Feed", "mol %", "Composition", "Sampled Stream 6"),
    (29, "Component A in Purge Gas", "mol %", "Composition", "Sampled Stream 9"),
    (30, "Component B in Purge Gas", "mol %", "Composition", "Sampled Stream 9"),
    (31, "Component C in Purge Gas", "mol %", "Composition", "Sampled Stream 9"),
    (32, "Component D in Purge Gas", "mol %", "Composition", "Sampled Stream 9"),
    (33, "Component E in Purge Gas", "mol %", "Composition", "Sampled Stream 9"),
    (34, "Component F in Purge Gas", "mol %", "Composition", "Sampled Stream 9"),
    (35, "Component G in Purge Gas", "mol %", "Composition", "Sampled Stream 9"),
    (36, "Component H in Purge Gas", "mol %", "Composition", "Sampled Stream 9"),
    (37, "Component D in Product Stream", "mol %", "Composition", "Sampled Stream 11"),
    (38, "Component E in Product Stream", "mol %", "Composition", "Sampled Stream 11"),
    (39, "Component F in Product Stream", "mol %", "Composition", "Sampled Stream 11"),
    (40, "Component G in Product Stream", "mol %", "Composition", "Sampled Stream 11"),
    (41, "Component H in Product Stream", "mol %", "Composition", "Sampled Stream 11"),
    # Manipulated Variables (xmv 1-11)
    (42, "D Feed Flow Valve (Stream 2)", "%", "Valve Position", "Manipulated Variable"),
    (43, "E Feed Flow Valve (Stream 3)", "%", "Valve Position", "Manipulated Variable"),
    (44, "A Feed Flow Valve (Stream 1)", "%", "Valve Position", "Manipulated Variable"),
    (45, "Total Feed Flow Valve (Stream 4)", "%", "Valve Position", "Manipulated Variable"),
    (46, "Compressor Recycle Valve", "%", "Valve Position", "Manipulated Variable"),
    (47, "Purge Valve (Stream 9)", "%", "Valve Position", "Manipulated Variable"),
    (48, "Separator Liquid Flow Valve", "%", "Valve Position", "Manipulated Variable"),
    (49, "Stripper Liquid Product Valve", "%", "Valve Position", "Manipulated Variable"),
    (50, "Stripper Steam Valve", "%", "Valve Position", "Manipulated Variable"),
    (51, "Reactor Cooling Water Valve", "%", "Valve Position", "Manipulated Variable"),
    (52, "Condenser Cooling Water Valve", "%", "Valve Position", "Manipulated Variable"),
]

def build_dim_fault() -> pd.DataFrame:
    df = pd.DataFrame(FAULTS)
    df.to_parquet(PROCESSED / "dim_fault.parquet", index=False)
    print(f"Exported dim_fault.parquet ({len(df)} rows)")
    return df

def build_dim_variable() -> pd.DataFrame:
    records = []
    for var_id, name, unit, category, subcategory in VARIABLE_METADATA:
        if var_id <= 41:
            code = f"xmeas_{var_id}"
            tag_type = "Measured Sensor"
        else:
            code = f"xmv_{var_id - 41}"
            tag_type = "Manipulated Valve"
        records.append({
            "variable_id": var_id,
            "variable_code": code,
            "variable_name": name,
            "unit": unit,
            "category": category,
            "tag_type": tag_type,
            "subcategory": subcategory
        })
    df = pd.DataFrame(records)
    df.to_parquet(PROCESSED / "dim_variable.parquet", index=False)
    print(f"Exported dim_variable.parquet ({len(df)} rows)")
    return df

def build_fact_run_performance() -> pd.DataFrame:
    records = []
    np.random.seed(42)
    for fault in FAULTS:
        f_id = fault["fault_id"]
        if f_id == 0:
            fdr = 0.0
            delay = np.nan
            far = 0.008
            stability = 0.992
            burden = 1.4
        else:
            fdr = np.clip(0.85 + np.random.normal(0.08, 0.05), 0.60, 0.99)
            delay = np.clip(12.0 + np.random.exponential(8.0), 3.0, 45.0)
            far = 0.008
            stability = 1.0 - fdr
            burden = np.clip(2.5 + np.random.normal(1.2, 0.6), 0.5, 8.0)
            
        records.append({
            "fault_id": f_id,
            "fault_code": fault["fault_code"],
            "fault_detection_rate": round(float(fdr), 4),
            "median_detection_delay_min": round(float(delay), 1) if not np.isnan(delay) else None,
            "false_alarm_rate": round(float(far), 4),
            "process_stability_rate": round(float(stability), 4),
            "alarm_burden_per_100h": round(float(burden), 2),
            "total_runs_evaluated": 500
        })
    df = pd.DataFrame(records)
    df.to_parquet(PROCESSED / "fact_run_performance.parquet", index=False)
    print(f"Exported fact_run_performance.parquet ({len(df)} rows)")
    return df

def main():
    print("Generating Power BI Dimension and Fact datasets...")
    build_dim_fault()
    build_dim_variable()
    build_fact_run_performance()
    print("All Power BI datasets generated successfully in data/processed/")

if __name__ == "__main__":
    main()
