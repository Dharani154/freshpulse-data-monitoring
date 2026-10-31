# Data Dictionary

## 1. dataset_config

Stores the configuration of each dataset.

- `dataset_id`: Unique name of the dataset.
- `source_file`: Name of the input CSV file.
- `expected_arrival_time`: Expected arrival time.
- `completion_sla_minutes`: Maximum allowed processing time.
- `freshness_threshold_minutes`: Maximum allowed data age.

## 2. pipeline_runs

Stores information about each pipeline execution.

- `run_id`: Unique ID for a pipeline run.
- `start_time`: Time when the run started.
- `end_time`: Time when the run finished.
- `status`: Result of the pipeline run.
- `input_count`: Number of input records.
- `output_count`: Number of accepted records.
- `rejected_count`: Number of rejected records.
- `error_reason`: Details of any recorded error.

## 3. dataset_events

Stores valid dataset records.

- `event_id`: Unique ID for an event.
- `dataset_id`: Name of the dataset.
- `expected_arrival`: Expected arrival timestamp.
- `actual_arrival`: Actual arrival timestamp.
- `completion_time`: Processing completion timestamp.
- `source_file`: Source CSV filename.
- `run_id`: Pipeline run that processed the record.

## 4. rejected_records

Stores invalid records.

- `reject_id`: Unique rejection ID.
- `run_id`: Pipeline run that rejected the record.
- `source_file`: Input filename.
- `source_row`: Row number in the input file.
- `raw_record`: Original record data.
- `rejection_reason`: Why the record was rejected.

## 5. sla_alerts

Stores SLA alerts associated with accepted events.

- `alert_id`: Unique alert ID.
- `event_id`: Related event.
- `dataset_id`: Related dataset.
- `alert_type`: Type of SLA problem.
- `severity`: Importance of the alert.
- `detected_at`: Time when the alert was detected.
- `alert_status`: Current alert status.

## 6. dataset_sla_alerts

Stores dataset-level alerts, including missing arrivals.

- `alert_id`: Unique alert ID.
- `dataset_id`: Dataset with the issue.
- `alert_type`: Type of problem.
- `severity`: Alert importance.
- `detected_at`: Detection time.
- `alert_status`: Current alert status.
- `message`: Explanation of the problem.
- `deadline`: Expected arrival deadline.
