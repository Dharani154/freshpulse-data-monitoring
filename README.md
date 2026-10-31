# Dataset SLA Monitoring & Data Freshness Alerting System

## 1. Project Overview

This project monitors dataset arrival times, processing completion times, and data freshness. It identifies missing or late data, validates incoming records, stores rejected records with reasons, and generates reports for monitoring data quality.

The project is built with Python and SQLite and uses synthetic CSV datasets for repeatable testing.

## 2. Technologies Used

- Python
- SQLite
- CSV and JSON
- Pytest
- Pandas

## 3. Features

- Configurable dataset arrival schedules and completion SLAs
- Input schema and record validation
- Duplicate event detection
- Rejected-record tracking with rejection reasons
- Dataset arrival and freshness monitoring
- Event-level and dataset-level SLA alerts
- Pipeline run history and record counts
- CSV and JSON reports
- Automated unit and integration tests
- Synthetic data generation for large-volume testing

## 4. Project Structure

```text
config/       Dataset configuration
data/input/   Generated input CSV files
data/output/  Output data, if configured
data/rejected/ Rejected data, if configured
src/          Database, ingestion, validation, monitoring and reporting
tests/        Unit and integration tests
docs/         Architecture, data dictionary and SQL queries
reports/      SLA and quality reports
scripts/      Data generation and utility scripts
```

## 5. Setup

Create and activate a virtual environment on Windows:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## 6. Run the Tests

```powershell
python -m pytest -v
```

## 7. Generate Synthetic Data

Generate 100 records per configured dataset:

```powershell
python scripts/generate_data.py --count 100 --seed 42
```

Generate 25,000 records per dataset for a large-volume test:

```powershell
python scripts/generate_data.py --count 25000 --seed 42
```

The generator also creates additional test records to exercise validation and duplicate handling.

## 8. Run the Pipeline

```powershell
python -m src.pipeline --count 100 --seed 42
```

The pipeline initializes the database, generates data, ingests records, evaluates SLA conditions, and generates quality reports when configured.

For a large-volume run:

```powershell
python -m src.pipeline --count 25000 --seed 42
```

Use a clean test copy for repeatable benchmarks because rerunning the same event IDs against an existing database causes duplicate rejections.

## 9. Reports

The project generates reports in the `reports/` directory, including:

- `sla_report.csv` — arrival, completion and freshness results
- `pipeline_summary.json` — pipeline and data-quality summary
- `rejected_records.csv` — rejected records and rejection reasons

## 10. Database

The SQLite database is stored at `data/monitoring.db`. It tracks configured datasets, pipeline runs, accepted events, rejected records and SLA alerts.

## 11. Test Results

The current recorded automated test run completed with 27 tests passing in 0.52 seconds. Rerun the tests before submission and update this section if the result changes.

## 12. Limitations and Future Improvements

- Add automatic alert closure and recovery handling.
- Add notifications for critical SLA violations.
- Improve handling of schema changes and partial failures.
- Expand benchmark measurements for larger datasets.
- Add scheduled execution and operational dashboards.

## 13. Reproducibility

The synthetic data generator supports a fixed random seed, allowing repeatable data generation. Run tests and benchmarks in a clean environment to avoid duplicate records from previous runs.
