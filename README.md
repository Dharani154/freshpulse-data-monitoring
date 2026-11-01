# FreshPulse – Dataset SLA Monitoring & Data Freshness Alerting System

## 1. Project Overview

FreshPulse is a Python-based Data Engineering project that monitors dataset arrivals, processing times, data quality, and data freshness.

In real-world applications, data must arrive and be processed within expected time limits. When data is delayed, missing, outdated, or contains incorrect records, it can affect reports and business decisions.

FreshPulse helps identify these problems through automated data validation, pipeline monitoring, SLA tracking, and alert generation.

The project also includes an interactive dashboard that allows users to view pipeline status, data quality information, SLA alerts, and monitoring reports in one place.

## 2. Project Objectives

The main objectives of this project are:

- Monitor whether datasets arrive on time.
- Check whether data processing is completed within the expected deadline.
- Identify missing, invalid, and duplicate records.
- Track rejected records and their reasons.
- Monitor dataset freshness and SLA violations.
- Generate automated monitoring reports.
- Maintain pipeline execution history.
- Display pipeline information through an interactive dashboard.

## 3. Technologies Used

| Technology | Purpose |
| Python | Develop the data processing and monitoring system |
| SQLite | Store datasets, processing history, and alerts |
| Pandas | Process and analyze data |
| Streamlit | Build the interactive dashboard |
| Plotly | Display interactive charts |
| CSV | Store input datasets and reports |
| JSON | Manage configurations and summary reports |
| Pytest | Test project functionality |
| Git & GitHub | Manage and maintain source code |

## 4. How the Project Works

The project follows a simple data processing workflow:

1. **Generate Data:** Create sample CSV datasets for testing.
2. **Validate Data:** Check incoming records for missing or invalid values.
3. **Detect Duplicates:** Identify records that have already been processed.
4. **Store Data:** Save valid and rejected records in the SQLite database.
5. **Monitor SLAs:** Check dataset arrival, processing deadlines, and freshness.
6. **Generate Alerts:** Identify missing datasets, late arrivals, and SLA violations.
7. **Generate Reports:** Export monitoring results into CSV and JSON files.
8. **View Dashboard:** Display pipeline health and monitoring results using Streamlit.

## 5. Project Architecture

FreshPulse uses a modular architecture. Each Python file is responsible for a specific task.

### Module Description

| Module | Description |
| `database.py` | Creates and manages the SQLite database |
| `validate.py` | Validates incoming data and checks records |
| `ingest.py` | Reads CSV files and processes incoming records |
| `sla_monitor.py` | Monitors dataset arrival, processing deadlines, and freshness |
| `pipeline.py` | Coordinates the complete data processing workflow |
| `dashboard.py` | Displays monitoring information through Streamlit |
| `generate_data.py` | Generates synthetic datasets for testing |

### Project Workflow

```text
Synthetic Data Generation
          |
          v
     Data Validation
          |
          v
     Data Ingestion
          |
          v
     SQLite Database
          |
          v
     SLA Monitoring
          |
          v
     Alert Generation
          |
          v
    Report Generation
          |
          v
   Streamlit Dashboard
```

## 6. Project Folder Structure

```text
freshpulse-data-monitoring/
│
├── config/
│   └── datasets.json
│
├── data/
│   ├── input/
│   ├── output/
│   ├── rejected/
│   └── monitoring.db
│
├── src/
│   ├── __init__.py
│   ├── database.py
│   ├── validate.py
│   ├── ingest.py
│   ├── sla_monitor.py
│   ├── pipeline.py
│   └── dashboard.py
│
├── scripts/
│   └── generate_data.py
│
├── tests/
│   ├── test_validate.py
│   ├── test_ingest.py
│   ├── test_sla_monitor.py
│   └── test_pipeline.py
│
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   └── sql_queries.md
│
├── reports/
│   ├── sla_report.csv
│   ├── pipeline_summary.json
│   └── rejected_records.csv
│
├── requirements.txt
├── .gitignore
└── README.md
```

## 7. Installation and Setup

Follow these steps to download and run FreshPulse on a Windows machine.

### Step 1: Clone the GitHub Repository

Open PowerShell or the VS Code terminal.

```powershell
git clone https://github.com/Dharani154/freshpulse-data-monitoring.git
```

Navigate to the project directory:

```powershell
cd freshpulse-data-monitoring
```

### Step 2: Create a Virtual Environment

A virtual environment keeps the project's Python dependencies separate from other projects.

```powershell
python -m venv venv
```

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again.

### Step 3: Install Dependencies for the First Run

Install the required Python libraries:

```powershell
pip install -r requirements.txt
```

The main external libraries used are:

```powershell
pip install pandas streamlit plotly pytest
```

### Step 4: Check Installed Packages

```powershell
pip list
```

This displays the installed Python packages.

## 8. Database Initialization

FreshPulse uses SQLite to store processed records, rejected records, pipeline history, and SLA alerts.

Initialize the database:

```powershell
python -m src.database
```

The database is stored at:

```text
data/monitoring.db
```

The database contains information about:

- Dataset configurations.
- Accepted records.
- Rejected records.
- Pipeline execution history.
- SLA monitoring results.
- Event-level and dataset-level alerts.

## 9. Generate Synthetic Data

The project uses synthetic CSV datasets for testing instead of real business data.

This helps test the pipeline with different record volumes.

### Generate 20 Records Per Dataset

```powershell
python scripts/generate_data.py --count 20 --seed 42
```

### Generate 100 Records Per Dataset

```powershell
python scripts/generate_data.py --count 100 --seed 42
```

### Generate 25,000 Records Per Dataset

```powershell
python scripts/generate_data.py --count 25000 --seed 42
```

**Understanding the command:**

- `--count`: Number of normal records to generate per configured dataset.
- `--seed 42`: Uses a fixed random seed to make test data generation repeatable.

The generator also creates additional test records for validation and duplicate detection.

Generated CSV files are stored in:

```text
data/input/
```

## 10. Data Ingestion and Validation

The ingestion module reads generated CSV files, validates records, and stores the results in SQLite.

Run the ingestion module:

```powershell
python -m src.ingest
```

The ingestion process performs the following operations:

1. Reads CSV files from the input directory.
2. Checks records against the configured schema.
3. Identifies missing and invalid values.
4. Detects duplicate events.
5. Stores valid records in the database.
6. Tracks rejected records with their rejection reasons.

This helps maintain data quality before records are used for further processing.

## 11. SLA Monitoring

SLA stands for **Service Level Agreement**.

In this project, an SLA defines the expected time by which a dataset should arrive or complete processing.

The monitoring module checks whether datasets meet these expected time limits.

Run SLA monitoring:

```powershell
python src/sla_monitor.py --as-of "2026-11-01T23:59:00+05:30"
```

The `--as-of` parameter specifies the reference date and time for SLA evaluation.

The `+05:30` represents Indian Standard Time (IST).

Replace the example timestamp with the required monitoring reference time when running another test.

### What Does SLA Monitoring Check?

- Expected dataset arrival time.
- Actual dataset arrival time.
- Processing completion deadline.
- Dataset freshness.
- Missing datasets.
- Late data arrivals.
- SLA violations.

When a dataset does not meet its configured SLA, the system generates an appropriate alert.

## 12. Run the Complete Pipeline

FreshPulse provides a pipeline module to coordinate the complete processing workflow.

### Standard Execution

```powershell
python -m src.pipeline --count 100 --seed 42
```

### Large-Volume Execution

```powershell
python -m src.pipeline --count 25000 --seed 42
```

The pipeline coordinates the configured processing stages:

1. Database initialization.
2. Synthetic data generation.
3. Data ingestion.
4. Data validation.
5. SLA monitoring.
6. Report generation.

This provides a convenient way to execute the complete workflow.

**Note:** The pipeline should be used as the main execution method for a complete run. Avoid running data generation and ingestion separately immediately before it unless you intentionally want to test those modules individually. Reusing existing event IDs can result in duplicate-record rejections.

## 13. Interactive Monitoring Dashboard

FreshPulse includes an interactive dashboard built using Streamlit, Pandas, and Plotly.

The dashboard reads monitoring information from the SQLite database and generated reports.

It helps users understand the condition of their data pipeline without manually checking database tables.

### Dashboard Sections

**1. Overview**
Displays a summary of the complete pipeline.

- Total datasets.
- Processed records.
- Accepted records.
- Rejected records.
- SLA alerts.
- Overall pipeline status.
- Monitoring charts.

**2. Pipeline Runs**
Displays pipeline execution history.

- Pipeline run details.
- Execution timestamps.
- Processing status.
- Record counts.

**3. Data Quality**
Helps understand the quality of incoming records.

- Accepted records.
- Rejected records.
- Duplicate records.
- Validation failures.
- Rejection reasons.

**4. SLA Monitoring**
Displays dataset monitoring information.

- Dataset arrival status.
- Processing completion status.
- SLA deadlines.
- Data freshness.
- Event-level alerts.
- Dataset-level alerts.
- Alert severity and status.

**5. Test Results**
Provides access to automated test execution and test results.

**6. Reports**
Displays the available monitoring reports.

- SLA report.
- Pipeline summary.
- Rejected records report.

### Start the Dashboard

Run the following command:

```powershell
python -m streamlit run src/dashboard.py
```

After starting Streamlit, open the following URL in your browser:

```text
http://localhost:8501
```

The dashboard will display the latest available monitoring information.

**Important:** Run the pipeline first so that the database and reports contain information for the dashboard to display.

## 14. Generated Reports

FreshPulse automatically generates monitoring reports in the `reports/` directory.

### 1. SLA Report

File:

```text
reports/sla_report.csv
```

Contains dataset arrival, processing completion, freshness, and SLA monitoring results.

### 2. Pipeline Summary

File:

```text
reports/pipeline_summary.json
```

Contains pipeline execution details and data-quality statistics.

### 3. Rejected Records

File:

```text
reports/rejected_records.csv
```

Contains rejected records along with the reasons they were rejected.

These reports help users understand pipeline performance and data quality.

## 15. Database Inspection

You can inspect the SQLite database using Python.

For example, to view dataset-level SLA alerts:

```powershell
python -c "import sqlite3; c=sqlite3.connect('data/monitoring.db'); print(*c.execute('SELECT dataset_id, alert_type, severity, alert_status, deadline FROM dataset_sla_alerts'), sep='\n'); c.close()"
```

This command displays:

- Dataset ID.
- Alert type.
- Alert severity.
- Alert status.
- SLA deadline.

The database can also be explored using an SQLite database viewer or Python SQL queries.

## 16. Run Automated Tests

FreshPulse uses Pytest to verify that the project modules work correctly.

Run all automated tests:

```powershell
python -m pytest -v
```

Run tests from the tests directory:

```powershell
python -m pytest tests -v
```

The previously recorded test result was:

**27 tests passed in 0.52 seconds.**

The test suite covers:

- Schema validation.
- Record validation.
- Duplicate detection.
- Data ingestion.
- Rejected-record handling.
- SLA calculations.
- Pipeline functionality.

Run the tests again after making code changes to verify the latest results.

## 17. Complete Command Execution Guide

For beginners, the following is the recommended command order for the first execution.

### Step 1: Clone the Repository

```powershell
git clone https://github.com/Dharani154/freshpulse-data-monitoring.git

cd freshpulse-data-monitoring
```

### Step 2: Create and Activate Virtual Environment

```powershell
python -m venv venv

.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Initialize the Database

```powershell
python -m src.database
```

### Step 5: Run the Complete Pipeline

```powershell
python -m src.pipeline --count 100 --seed 42
```

### Step 6: Execute Automated Tests

```powershell
python -m pytest -v
```

### Step 7: Start the Dashboard

```powershell
python -m streamlit run src/dashboard.py
```

### Step 8: Open the Dashboard

```text
http://localhost:8501
```

You can now explore the pipeline information, data quality, SLA alerts, and generated reports.

## 18. What I Learned

While developing FreshPulse, I gained practical experience in:

- Python programming and modular application development.
- Working with CSV and JSON files.
- SQLite database creation and management.
- Data ingestion and validation.
- Duplicate detection and error handling.
- Data quality monitoring.
- Dataset freshness and SLA monitoring.
- Generating automated reports.
- Building interactive dashboards using Streamlit.
- Creating charts using Plotly.
- Writing unit and integration tests using Pytest.
- Working with Git and GitHub for version control.

## 19. Future Improvements

Some improvements planned for future versions include:

- Add email notifications for critical SLA alerts.
- Implement automatic alert closure and recovery tracking.
- Add historical SLA trend analysis.
- Support scheduled pipeline execution.
- Improve handling of schema changes and partial failures.
- Add more performance testing for large datasets.
- Introduce role-based dashboard access.
- Explore cloud-based data storage and monitoring.

## 20. Conclusion

FreshPulse demonstrates how data engineering concepts can be used to build a data pipeline monitoring solution.

The project combines Python, SQLite, data validation, SLA monitoring, automated reporting, and an interactive Streamlit dashboard to help identify data quality issues and monitor dataset reliability.

Through this project, I gained practical experience in data ingestion, database management, pipeline monitoring, automated testing, and data visualization.

**Project Name:** FreshPulse

**Project Type:** Data Engineering / Data Quality / Pipeline Monitoring

**Programming Language:** Python

**Database:** SQLite

**Dashboard:** Streamlit

**Testing Framework:** Pytest

**Repository:** <https://github.com/Dharani154/freshpulse-data-monitoring>
