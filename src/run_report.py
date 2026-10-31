
import csv

from src.database import get_connection, ROOT

REPORT_DIR = ROOT / "reports"
REPORT_FILE = REPORT_DIR / "pipeline_run_summary.csv"


def generate_run_report():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                run_id,
                start_time,
                end_time,
                status,
                input_count,
                output_count,
                rejected_count,
                error_reason
            FROM pipeline_runs
            ORDER BY start_time DESC
            """
        ).fetchall()

    with REPORT_FILE.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow([
            "run_id",
            "start_time",
            "end_time",
            "status",
            "input_count",
            "output_count",
            "rejected_count",
            "error_reason",
        ])
        writer.writerows(rows)

    print(f"Pipeline run report created: {REPORT_FILE}")
    print(f"Total pipeline runs: {len(rows)}")


if __name__ == "__main__":
    generate_run_report()
