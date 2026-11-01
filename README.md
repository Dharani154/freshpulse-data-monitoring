# Dataset SLA Monitoring & Data Freshness Alerting System

## 1. Project Overview

The **Dataset SLA Monitoring & Data Freshness Alerting System** is a Python-based Data Engineering project designed to monitor dataset arrivals, data processing completion times, data quality, and data freshness.

In real-world data engineering environments, data pipelines are expected to receive and process data within specific time limits. If a dataset arrives late, contains invalid records, or is not updated on time, it can affect downstream applications, reports, and business decisions.

This project addresses these problems by building an automated monitoring system that:

- Generates synthetic datasets for testing.
- Validates incoming records against predefined schemas.
- Identifies duplicate and invalid records.
- Stores rejected records with their rejection reasons.
- Monitors dataset arrival and processing deadlines.
- Detects late, missing, and stale datasets.
- Generates event-level and dataset-level SLA alerts.
- Maintains pipeline execution history.
- Produces CSV and JSON monitoring reports.
- Displays pipeline health and monitoring results through an interactive dashboard.

The backend is developed using **Python and SQLite**, while the interactive dashboard is developed using **Streamlit, Pandas, and Plotly**.

---

## 2. Purpose of the Project

The main purpose of this project is to understand how data engineering teams monitor the reliability and quality of data pipelines.

It focuses on solving the following real-world problems:

1. **Late Data Arrival:** Identify when a dataset does not arrive within its expected schedule.
2. **Data Freshness:** Check whether the latest available data is up to date.
3. **Data Quality:** Identify missing fields, invalid values, and incorrect records.
4. **Duplicate Detection:** Prevent duplicate events from being processed multiple times.
5. **SLA Monitoring:** Check whether datasets meet their arrival and processing deadlines.
6. **Alert Management:** Generate alerts when datasets violate their configured SLAs.
7. **Pipeline Tracking:** Maintain execution history and record processing statistics.
8. **Visual Monitoring:** Provide an interactive dashboard to understand pipeline health without manually checking database tables.

---

## 3. Technologies Used

| Technology | Purpose |
| Python | Core programming language and pipeline development |
| SQLite | Database for storing datasets, events, pipeline runs, and alerts |
| Pandas | Data processing and dashboard data handling |
| Streamlit | Building the interactive monitoring dashboard |
| Plotly | Interactive charts and visualizations |
| CSV | Input datasets and exported reports |
| JSON | Dataset configuration and summary reports |
| Pytest | Unit testing and integration testing |
| Git & GitHub | Version control and project hosting |

### Python Libraries

- sqlite3
- csv
- json
- uuid
- datetime
- pathlib
- pandas
- streamlit
- plotly
- pytest

---

## 4. Project Architecture

The project follows a modular architecture.

**Overall workflow:**

Synthetic Data Generation → Schema Validation → Data Ingestion → SQLite Database → SLA Monitoring → Alert Generation → Report Generation → Streamlit Dashboard

### Module Description

| Module | Responsibility |
| `database.py` | Creates and manages the SQLite database |
| `validate.py` | Validates incoming datasets and records |
| `ingest.py` | Processes CSV files and stores accepted/rejected records |
| `sla_monitor.py` | Evaluates arrival, completion, and freshness SLAs |
| `pipeline.py` | Coordinates the pipeline execution |
| `dashboard.py` | Displays monitoring information through Streamlit |
| `generate_data.py` | Generates synthetic datasets for testing |

---

## 5. Project Structure

```text
Dats-Engineering-Project/
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
├── reports/
│   ├── sla_report.csv
│   ├── pipeline_summary.json
│   └── rejected_records.csv
│
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   └── sql_queries.md
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 6. Dashboard Module

The project includes an interactive dashboard developed using Streamlit.

**Dashboard file:** `src/dashboard.py`

The dashboard reads information from the SQLite database (`data/monitoring.db`) and generated reports in the `reports/` directory.

It helps users understand the health of the data pipeline through visual summaries, charts, tables, and monitoring information.

### Dashboard Pages

#### 1. Overview

Provides a high-level summary of the complete data pipeline.

Displays:

- Total datasets.
- Total processed records.
- Accepted records.
- Rejected records.
- SLA alerts.
- Overall pipeline health.
- Monitoring charts.

#### 2. Pipeline Runs

Displays pipeline execution history.

Includes:

- Pipeline run details.
- Execution timestamps.
- Processing status.
- Record counts.
- Pipeline execution history.

#### 3. Data Quality

Helps identify the quality of incoming datasets.

Displays:

- Accepted records.
- Rejected records.
- Duplicate records.
- Validation failures.
- Rejection reasons.
- Data quality summaries.

#### 4. SLA Monitoring

Monitors dataset arrival and freshness conditions.

Displays:

- Dataset arrival status.
- Processing completion status.
- SLA deadlines.
- Freshness status.
- Event-level alerts.
- Dataset-level alerts.
- Alert severity and status.

#### 5. Test Results

Provides an option to execute the automated Pytest test suite from the dashboard.

Displays test execution results to help understand whether the project modules are functioning correctly.

#### 6. Reports

Provides access to the generated monitoring reports.

Available reports:

- `sla_report.csv`
- `pipeline_summary.json`
- `rejected_records.csv`

### Run the Dashboard

After initializing the database and generating the reports, execute:

```powershell
python -m streamlit run src/dashboard.py
```

Streamlit starts the dashboard locally and provides a URL, usually:

```text
http://localhost:8501
```

Open the URL in your browser to access the monitoring dashboard.

---

## 7. Installation and Setup

Follow these steps to run the project on a Windows machine using PowerShell.

### Step 1: Clone the Repository

```powershell
git clone https://github.com/Dharani154/YOUR-REPOSITORY.git
```

Navigate to the project directory:

```powershell
cd Dats-Engineering-Project
```

### Step 2: Create a Virtual Environment

```powershell
python -m venv venv
```

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

The project uses Pandas, Streamlit, Plotly, and Pytest along with Python's built-in libraries.

If you need to install the dashboard dependencies separately:

```powershell
pip install streamlit pandas plotly
```

### Step 4: Save Dependencies

After installing the required libraries, update the requirements file:

```powershell
pip freeze > requirements.txt
```

---

## 8. Database Initialization

Initialize the SQLite database:

```powershell
python -m src.database
```

This creates the database and the required tables.

**Database location:**

```text
data/monitoring.db
```

The database stores:

- Dataset configurations.
- Accepted events.
- Rejected records.
- Pipeline execution history.
- SLA monitoring information.
- Event-level and dataset-level alerts.

---

## 9. Generate Synthetic Data

The project uses synthetic CSV datasets instead of real business data.

This allows repeatable testing without depending on external data sources.

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

The generator also creates additional test records to exercise validation and duplicate detection.

The `--seed 42` option helps generate repeatable synthetic data.

Generated files are stored in:

```text
data/input/
```

---

## 10. Run the Data Ingestion Process

Execute:

```powershell
python -m src.ingest
```

The ingestion module:

1. Reads CSV files from the input directory.
2. Checks records against the configured schema.
3. Identifies missing or invalid values.
4. Detects duplicate events.
5. Stores valid records in SQLite.
6. Tracks rejected records and their rejection reasons.

This ensures that only valid records are accepted into the processing database.

---

## 11. Run SLA Monitoring

Execute:

```powershell
python src/sla_monitor.py --as-of "2026-10-30T23:59:00+05:30"
```

The `--as-of` parameter specifies the reference date and time used for SLA evaluation.

The `+05:30` timezone represents Indian Standard Time (IST).

The monitoring module checks:

- Expected dataset arrival time.
- Actual dataset arrival time.
- Processing completion deadline.
- Dataset freshness.
- Missing datasets.
- Late arrivals.
- SLA violations.

It generates alerts when configured SLA conditions are violated.

Replace the example timestamp with the required monitoring reference time when performing another test.

---

## 12. Run the Complete Pipeline

The project also provides a pipeline execution module.

For a standard run:

```powershell
python -m src.pipeline --count 100 --seed 42
```

For a large-volume run:

```powershell
python -m src.pipeline --count 25000 --seed 42
```

The complete pipeline coordinates the required processing stages, including database initialization, synthetic data generation, ingestion, monitoring, and report generation as configured.

Use a clean test database when benchmarking repeated runs because previously processed event IDs may be identified as duplicates.

---

## 13. Generate and View Reports

The project generates reports in the `reports/` directory.

### SLA Report

```text
reports/sla_report.csv
```

Contains dataset arrival, processing completion, freshness, and SLA monitoring results.

### Pipeline Summary

```text
reports/pipeline_summary.json
```

Contains pipeline execution information and data-quality statistics.

### Rejected Records

```text
reports/rejected_records.csv
```

Contains rejected records along with their rejection reasons.

These reports can be used for further analysis and displayed through the dashboard.

---

## 14. Run Automated Tests

The project uses Pytest for unit and integration testing.

Run all tests:

```powershell
python -m pytest -v
```

Run tests from the tests directory:

```powershell
python -m pytest tests -v
```

The recorded test result was:

**27 tests passed in 0.52 seconds.**

The test suite checks:

- Schema validation.
- Record validation.
- Duplicate detection.
- Data ingestion.
- Rejected-record handling.
- SLA calculations.
- Pipeline functionality.

Rerun the tests before submission to confirm the latest results.

---

## 15. Complete Command Execution Order

For someone running this project for the first time, follow this command sequence.

### Initial Setup

```powershell
git clone https://github.com/Dharani154/YOUR-REPOSITORY.git

cd Dats-Engineering-Project

python -m venv venv

.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### Initialize and Process Data

```powershell
python -m src.database

python scripts/generate_data.py --count 100 --seed 42

python -m src.ingest

python src/sla_monitor.py --as-of "2026-10-30T23:59:00+05:30"
```

### Execute Automated Tests

```powershell
python -m pytest -v
```

### Launch the Dashboard

```powershell
python -m streamlit run src/dashboard.py
```

Open:

```text
http://localhost:8501
```

**Important:** Run database initialization, data generation, ingestion, and monitoring before launching the dashboard so that it has data to display.

For subsequent runs, avoid generating the same event IDs into an existing database unless you intentionally want to test duplicate detection.

---

## 16. What I Learned From This Project

Through this project, I gained practical experience in:

- Building a modular Python data engineering application.
- Working with CSV and JSON data.
- Designing and managing SQLite databases.
- Implementing schema and record validation.
- Handling duplicate and rejected records.
- Understanding data ingestion workflows.
- Implementing dataset freshness monitoring.
- Working with event-level and dataset-level SLAs.
- Generating automated monitoring reports.
- Building interactive dashboards using Streamlit.
- Creating visualizations using Plotly.
- Writing unit and integration tests using Pytest.
- Testing pipelines with synthetic datasets of different sizes.

---

## 17. Limitations and Future Improvements

Possible improvements for future versions include:

- Implement automated alert closure and recovery handling.
- Integrate email or messaging notifications for critical SLA violations.
- Add scheduled pipeline execution.
- Improve schema evolution and partial-failure handling.
- Expand large-volume performance benchmarking.
- Add historical SLA trend analysis.
- Introduce role-based dashboard access.
- Integrate cloud-based data storage and monitoring.

---

## 18. Conclusion

The Dataset SLA Monitoring & Data Freshness Alerting System demonstrates how data engineering teams can monitor dataset reliability, data quality, and pipeline performance.

By combining Python, SQLite, automated validation, SLA monitoring, reporting, and an interactive Streamlit dashboard, the project provides an end-to-end example of a data pipeline monitoring solution.

It demonstrates practical knowledge of data ingestion, database management, data quality checks, monitoring, alerting, testing, and dashboard development.

**Project Type:** Data Engineering / Data Quality / Pipeline Monitoring
**Primary Language:** Python
**Database:** SQLite
**Dashboard:** Streamlit
**Testing:** Pytest

## Conclusion

The Dataset SLA Monitoring & Data Freshness Alerting System demonstrates an end-to-end approach to monitoring data pipeline reliability, data quality, and dataset freshness.

By using Python, SQLite, Pandas, and Streamlit, the project automates data ingestion, record validation, duplicate detection, SLA monitoring, alert generation, and report creation. The interactive dashboard provides a clear view of pipeline execution, data quality, SLA violations, and monitoring results.

This project helped me gain practical experience in Data Engineering concepts, database management, data validation, pipeline monitoring, automated testing, and dashboard development.
