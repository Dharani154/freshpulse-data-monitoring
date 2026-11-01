
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

from src.database import ROOT, get_connection

st.set_page_config(
    page_title="Data Engineering Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Data Engineering Pipeline Dashboard")
st.caption("Pipeline Monitoring • Data Quality • Testing • SLA Monitoring")

DB_PATH = ROOT / "data" / "monitoring.db"
REPORT_DIR = ROOT / "reports"


def load_table(table_name):
    """Load a database table safely if it exists."""
    conn = get_connection()
    try:
        exists = conn.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = ?
            """,
            (table_name,),
        ).fetchone()

        if not exists:
            return pd.DataFrame()

        return pd.read_sql_query(
            f'SELECT * FROM "{table_name}"', conn
        )
    finally:
        conn.close()


def categorize_reason(reason):
    reason = str(reason or "")

    if "event_id already exists:" in reason:
        return "Duplicate event ID already in database"
    if "Duplicate event_id in file:" in reason:
        return "Duplicate event ID within input file"
    if "expected_arrival" in reason:
        return "Invalid expected arrival timestamp"
    if "dataset_id is required" in reason:
        return "Missing dataset ID"
    if "Unknown dataset_id:" in reason:
        return "Unknown dataset ID"
    if "source_file does not match" in reason:
        return "Source file mismatch"
    if "Malformed row" in reason:
        return "Malformed CSV row"

    return reason or "Unspecified"


# Load current database information.
if not DB_PATH.exists():
    st.error(f"Database not found: {DB_PATH}")
    st.info(
        "Check your database path and initialize the project database."
    )
    st.stop()

try:
    runs = load_table("pipeline_runs")
    events = load_table("dataset_events")
    rejected = load_table("rejected_records")
    alerts = load_table("dataset_sla_alerts")
except Exception as exc:
    st.error(f"Could not read database: {exc}")
    st.stop()


# Sidebar navigation.
page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Pipeline Runs",
        "Execution Timeline",
        "Data Quality",
        "SLA Monitoring",
        "Test Results",
        "Reports",
    ],
)

# Calculate pipeline metrics.
total_runs = len(runs)
successful_runs = 0
failed_runs = 0
partial_runs = 0

if not runs.empty and "status" in runs.columns:
    statuses = runs["status"].fillna("").str.lower()
    successful_runs = int((statuses == "success").sum())
    failed_runs = int((statuses == "failed").sum())
    partial_runs = int((statuses == "partial_failed").sum())

accepted_total = (
    len(events)
    if not events.empty
    else 0
)

rejected_total = len(rejected)

if not runs.empty:
    if "output_count" in runs.columns:
        accepted_total = int(
            pd.to_numeric(
                runs["output_count"], errors="coerce"
            ).fillna(0).sum()
        )
    if "rejected_count" in runs.columns:
        rejected_total = int(
            pd.to_numeric(
                runs["rejected_count"], errors="coerce"
            ).fillna(0).sum()
        )


def show_run_table(data):
    if data.empty:
        st.info("No pipeline run records found.")
        return

    columns = [
        col for col in [
            "run_id",
            "start_time",
            "end_time",
            "status",
            "input_count",
            "output_count",
            "rejected_count",
            "error_reason",
        ]
        if col in data.columns
    ]

    st.dataframe(
        data[columns],
        use_container_width=True,
        hide_index=True,
    )


if page == "Overview":
    st.subheader("Project Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Pipeline Runs", total_runs)
    col2.metric("Successful Runs", successful_runs)
    col3.metric("Failed Runs", failed_runs)
    col4.metric("Total Rejected Records", rejected_total)

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Pipeline Run Status")

        if not runs.empty and "status" in runs.columns:
            status_counts = (
                runs["status"]
                .fillna("unknown")
                .value_counts()
                .rename_axis("Status")
                .reset_index(name="Runs")
            )

            st.bar_chart(
                status_counts,
                x="Status",
                y="Runs",
            )
        else:
            st.info("No pipeline status data available.")

    with right:
        st.subheader("Data Quality Summary")

        quality = pd.DataFrame(
            {
                "Record Type": ["Accepted", "Rejected"],
                "Count": [accepted_total, rejected_total],
            }
        )

        st.bar_chart(
            quality,
            x="Record Type",
            y="Count",
        )

        total_records = accepted_total + rejected_total

        if total_records:
            acceptance_rate = (
                accepted_total / total_records
            ) * 100

            st.metric(
                "Acceptance Rate",
                f"{acceptance_rate:.2f}%",
            )
        else:
            st.info("No record counts available.")

    st.subheader("Recent Pipeline Runs")

    if not runs.empty and "start_time" in runs.columns:
        recent = runs.sort_values(
            "start_time", ascending=False
        ).head(10)
        show_run_table(recent)
    else:
        show_run_table(runs)


elif page == "Execution Timeline":
    st.header("Pipeline Execution Timeline")

    runs = load_table("pipeline_runs")

    if runs.empty:
        st.info("No pipeline runs are available.")
    else:
        runs["start_time"] = pd.to_datetime(
            runs["start_time"], errors="coerce", utc=True
        )
        runs["end_time"] = pd.to_datetime(
            runs["end_time"], errors="coerce", utc=True
        )

        runs["duration_seconds"] = (
            runs["end_time"] - runs["start_time"]
        ).dt.total_seconds().round(2)

        runs = runs.sort_values("start_time", ascending=False)

        # Summary metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Runs", len(runs))
        col2.metric("Successful Runs", int((runs["status"] == "success").sum()))
        col3.metric("Failed Runs", int((runs["status"] == "failed").sum()))

        st.subheader("Run History")

        status_filter = st.selectbox(
            "Filter by status",
            ["All", "success", "failed", "partial_failed"]
        )

        filtered = runs.copy()
        if status_filter != "All":
            filtered = filtered[filtered["status"] == status_filter]

        st.dataframe(
            filtered[
                [
                    "run_id", "start_time", "end_time", "status",
                    "input_count", "output_count", "rejected_count",
                    "duration_seconds", "error_reason"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Records Processed per Run")

        chart_data = filtered.head(20).sort_values("start_time")
        if not chart_data.empty:
            st.bar_chart(
                chart_data.set_index("start_time")[
                    ["output_count", "rejected_count"]
                ]
            )

        st.subheader("Execution Duration")

        duration_data = filtered.dropna(
            subset=["duration_seconds"]
        ).head(20)

        if not duration_data.empty:
            st.bar_chart(
                duration_data.set_index("run_id")[["duration_seconds"]]
            )



elif page == "Pipeline Runs":
    st.subheader("Pipeline Run History")

    if not runs.empty and "status" in runs.columns:
        choices = [
            "All",
            *sorted(
                runs["status"].dropna().astype(str).unique()
            ),
        ]

        selected = st.selectbox("Filter by status", choices)

        filtered = runs.copy()

        if selected != "All":
            filtered = filtered[
                filtered["status"].astype(str) == selected
            ]

        show_run_table(filtered)
    else:
        show_run_table(runs)


elif page == "Data Quality":

    
    st.subheader("Dataset-wise Analytics")

    # Load the actual database tables
    dataset_config = load_table("dataset_config")
    accepted_events = load_table("dataset_events")
    rejected_records = load_table("rejected_records")

    if not dataset_config.empty:
        # Count accepted events per dataset
        accepted_counts = (
            accepted_events.groupby("dataset_id")
            .size()
            .rename("Accepted")
            .reset_index()
        )

        # Count recorded rejections by source file
        rejected_counts = (
            rejected_records.groupby("source_file")
            .size()
            .rename("Rejected")
            .reset_index()
        )

        # Match each source file to its configured dataset
        dataset_metrics = dataset_config[
            ["dataset_id", "source_file"]
        ].drop_duplicates().merge(
            accepted_counts,
            on="dataset_id",
            how="left"
        ).merge(
            rejected_counts,
            on="source_file",
            how="left"
        )

        dataset_metrics["Accepted"] = (
            dataset_metrics["Accepted"].fillna(0).astype(int)
        )
        dataset_metrics["Rejected"] = (
            dataset_metrics["Rejected"].fillna(0).astype(int)
        )

        total_records = (
            dataset_metrics["Accepted"] + dataset_metrics["Rejected"]
        )

        dataset_metrics["Acceptance Rate (%)"] = (
            dataset_metrics["Accepted"]
            .div(total_records.where(total_records > 0))
            .mul(100)
            .fillna(0)
            .round(2)
        )

        # Display metrics and chart
        st.dataframe(
            dataset_metrics[
                ["dataset_id", "Accepted", "Rejected", "Acceptance Rate (%)"]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Counts represent recorded database entries across pipeline runs."
        )

        st.bar_chart(
            dataset_metrics.set_index("dataset_id")[["Accepted", "Rejected"]]
        )
    else:
        st.info("No dataset configuration records found.")

    st.subheader("Data Quality and Rejections")

    if rejected.empty or "rejection_reason" not in rejected.columns:
        st.info("No rejection records are available.")
    else:
        rejection_data = rejected["rejection_reason"].apply(
            categorize_reason
        )

        summary = (
            rejection_data.value_counts()
            .rename_axis("Category")
            .reset_index(name="Count")
        )

        st.metric("Rejected Records", len(rejected))

        st.bar_chart(
            summary,
            x="Category",
            y="Count",
        )

        st.subheader("Rejection Category Details")
        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Sample Rejected Records")
        st.dataframe(
            rejected.head(100),
            use_container_width=True,
            hide_index=True,
        )


elif page == "SLA Monitoring":
    st.subheader("SLA Monitoring")

    if alerts.empty:
        st.info(
            "No SLA alert rows are available in the database. "
            "Run your SLA monitoring workflow to populate them."
        )
    else:
        st.metric("SLA Alert Records", len(alerts))

        if "alert_status" in alerts.columns:
            st.subheader("Alert Status")

            status_summary = (
                alerts["alert_status"]
                .fillna("unknown")
                .value_counts()
                .rename_axis("Status")
                .reset_index(name="Count")
            )

            st.bar_chart(
                status_summary,
                x="Status",
                y="Count",
            )

        st.subheader("SLA Alert Details")
        st.dataframe(
            alerts,
            use_container_width=True,
            hide_index=True,
        )

    sla_report = REPORT_DIR / "sla_report.csv"

    if sla_report.exists():
        with st.expander("View generated SLA report"):
            st.dataframe(
                pd.read_csv(sla_report),
                use_container_width=True,
                hide_index=True,
            )


elif page == "Test Results":
    st.subheader("Automated Test Results")

    st.write(
        "Run the existing Pytest suite to obtain a fresh test result."
    )

    if st.button("▶ Run Tests", type="primary"):
        with st.spinner("Running tests..."):
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests",
                    "-q",
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=300,
            )

        output = result.stdout + "\n" + result.stderr

        passed_match = re.search(
            r"(\d+)\s+passed", output
        )
        failed_match = re.search(
            r"(\d+)\s+failed", output
        )
        error_match = re.search(
            r"(\d+)\s+error(?:s)?", output
        )

        passed = (
            int(passed_match.group(1))
            if passed_match else 0
        )
        failed = (
            int(failed_match.group(1))
            if failed_match else 0
        )
        errors = (
            int(error_match.group(1))
            if error_match else 0
        )

        total = passed + failed + errors

        c1, c2, c3 = st.columns(3)
        c1.metric("Tests Passed", passed)
        c2.metric("Tests Failed", failed)
        c3.metric("Test Errors", errors)

        if result.returncode == 0:
            st.success(f"All {passed} tests passed.")
        else:
            st.error(
                f"Test execution finished with exit code "
                f"{result.returncode}."
            )

        if total:
            st.progress(passed / total)

        with st.expander("Full test output"):
            st.code(output or "No output returned.")

        if result.returncode == 0:
            st.caption(
                "These results are from the latest test execution "
                "in this dashboard session."
            )


elif page == "Reports":
    st.subheader("Generated Reports")

    report_files = [
        "rejection_summary.csv",
        "pipeline_run_summary.csv",
        "pipeline_summary.json",
        "rejected_records.csv",
        "sla_report.csv",
    ]

    for filename in report_files:
        filepath = REPORT_DIR / filename

        if filepath.exists():
            with st.expander(filename):
                st.write(
                    f"File size: {filepath.stat().st_size:,} bytes"
                )

                if filepath.suffix == ".csv":
                    preview = pd.read_csv(
                        filepath, nrows=100
                    )
                    st.dataframe(
                        preview,
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.caption(
                        "JSON report available in the reports folder."
                    )

                st.download_button(
                    label=f"Download {filename}",
                    data=filepath.read_bytes(),
                    file_name=filename,
                    key=f"download_{filename}",
                )
        else:
            st.caption(f"{filename}: not generated yet")

st.sidebar.divider()
st.sidebar.caption("Python • SQLite • Streamlit • Pytest")