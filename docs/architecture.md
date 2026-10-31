# Dataset SLA Monitoring and Data Freshness Alerting System

## Project Overview

This project checks whether datasets arrive on time and finish processing within the expected time. It also checks whether data is fresh or outdated.

The project uses Python to process data, CSV files as input, and SQLite to store records and alerts.

## Technologies Used

- Python
- Pandas
- SQLite
- CSV
- JSON
- Pytest

## How the Project Works

1. Generate sample CSV files.
2. Read and validate the input data.
3. Store valid records in the database.
4. Save invalid records with rejection reasons.
5. Check dataset arrival time, completion time, and freshness.
6. Generate alerts when SLA conditions are violated.
7. Create reports showing pipeline results.

## Benefits

- Detects missing or late datasets.
- Identifies invalid and duplicate records.
- Tracks pipeline execution results.
- Stores alerts for later review.
- Generates reports for data-quality analysis.

## Future Improvements

- Send email notifications for critical alerts.
- Schedule automatic pipeline execution.
- Improve alert recovery and closure.
- Test performance with large datasets.

## Performance Testing

The pipeline was tested using synthetic data generated for four datasets. The pipeline completed all configured stages, including data generation, ingestion, SLA monitoring, and quality report generation.

- **Execution time:** 23.94 seconds
- **Pipeline result:** All stages completed successfully
- **Performance test date:** 30 October 2026
- **Benchmark dataset size:** To be confirmed from the generator command and execution output
- **Accepted and rejected record counts:** To be verified from the generated reports and database
