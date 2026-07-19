-- Decision-ready KPI views. These use the processed alert result contract.
CREATE OR REPLACE VIEW process_analytics.run_detection AS
SELECT
    monitoring_method,
    fault_number,
    simulation_run,
    MAX(CASE WHEN confirmed_alert THEN 1 ELSE 0 END) AS detected,
    MIN(CASE
        WHEN confirmed_alert AND sample >= fault_onset_sample
        THEN (sample - fault_onset_sample) * minutes_per_sample
    END) AS detection_delay_minutes
FROM process_analytics.alert_results
WHERE fault_number <> 0
GROUP BY ALL;

CREATE OR REPLACE VIEW process_analytics.kpi_by_method AS
WITH detection AS (
    SELECT
        monitoring_method,
        AVG(detected) AS fault_detection_rate,
        MEDIAN(detection_delay_minutes) AS median_detection_delay_minutes,
        SUM(CASE WHEN detected = 0 THEN 1 ELSE 0 END) AS undetected_runs
    FROM process_analytics.run_detection
    GROUP BY monitoring_method
),
sample_metrics AS (
    SELECT
        monitoring_method,
        AVG(CASE WHEN eligible_normal_sample THEN confirmed_alert::INTEGER END) AS false_alarm_rate,
        1 - AVG(confirmed_alert::INTEGER) AS process_stability_rate,
        COUNT(DISTINCT CASE WHEN alert_event_id > 0 THEN
            CAST(fault_number AS VARCHAR) || '-' ||
            CAST(simulation_run AS VARCHAR) || '-' ||
            CAST(alert_event_id AS VARCHAR)
        END)
            / (COUNT(*) * MAX(minutes_per_sample) / 60.0) * 100 AS alarm_events_per_100_hours
    FROM process_analytics.alert_results
    GROUP BY monitoring_method
)
SELECT *
FROM detection
JOIN sample_metrics USING (monitoring_method);
