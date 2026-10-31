-- Query 1: Show the latest pipeline runs
SELECT
    run_id,
    status,
    input_count,
    output_count,
    rejected_count
FROM pipeline_runs
ORDER BY start_time DESC
LIMIT 10;


-- Query 2: Count accepted records per dataset
SELECT
    dataset_id,
    COUNT(*) AS total_records
FROM dataset_events
GROUP BY dataset_id;


-- Query 3: Find rejected records and their reasons
SELECT
    source_file,
    source_row,
    rejection_reason
FROM rejected_records;


-- Query 4: Show open event-level alerts
SELECT
    dataset_id,
    alert_type,
    severity,
    alert_status
FROM sla_alerts
WHERE alert_status = 'open';


-- Query 5: Show open missing-dataset alerts
SELECT
    dataset_id,
    alert_type,
    deadline,
    message
FROM dataset_sla_alerts
WHERE alert_status = 'open';
