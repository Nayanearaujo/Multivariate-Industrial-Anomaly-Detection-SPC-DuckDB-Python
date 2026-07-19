-- DuckDB analytical model for curated Tennessee Eastman monitoring outputs.
CREATE SCHEMA IF NOT EXISTS process_analytics;

CREATE OR REPLACE VIEW process_analytics.process_samples AS
SELECT *
FROM read_parquet('data/processed/process_samples.parquet');

CREATE OR REPLACE VIEW process_analytics.alert_results AS
SELECT *
FROM read_parquet('data/processed/alert_results.parquet');

CREATE OR REPLACE VIEW process_analytics.fault_dimension AS
SELECT DISTINCT
    faultNumber AS fault_number,
    CASE WHEN faultNumber = 0 THEN 'Normal operation'
         ELSE 'Fault ' || CAST(faultNumber AS VARCHAR)
    END AS fault_label
FROM process_analytics.process_samples;
