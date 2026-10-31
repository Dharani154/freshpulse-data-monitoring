
import csv
import json
import sqlite3
from datetime import datetime, timezone

from src.database import DB_PATH, ROOT

REPORT_DIR = ROOT / "reports"


def query_one(conn, sql):
    return conn.execute(sql).fetchone()[0]


def generate_report():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        # Pipeline run statistics
        run_count = query_one(
            conn, "SELECT COUNT(*) FROM pipeline_runs"
        )

        run_statuses = {
            status: count
            for status, count in conn.execute(
                """
                SELECT status, COUNT(*)
                FROM pipeline_runs
                GROUP BY status
                """
            ).fetchall()
        }

        latest_run = conn.execute(
            """
            SELECT run_id, start_time, end_time, status,
                   input_count, output_count, rejected_count,
                   error_reason
            FROM pipeline_runs
            ORDER BY start_time DESC
            LIMIT 1
            """
        ).fetchone()

        total_events = query_one(
            conn, "SELECT COUNT(*) FROM dataset_events"
        )

        total_rejected = query_one(
            conn, "SELECT COUNT(*) FROM rejected_records"
        )

        rejection_reasons = [
            {"reason": reason, "count": count}
            for reason, count in conn.execute(
                """
                SELECT rejection_reason, COUNT(*)
                FROM rejected_records
                GROUP BY rejection_reason
                ORDER BY COUNT(*) DESC
                """
            ).fetchall()
        ]

        dataset_counts = [
            {"dataset_id": dataset_id, "accepted_events": count}
            for dataset_id, count in conn.execute(
                """
                SELECT c.dataset_id, COUNT(e.event_id)
                FROM dataset_config c
                LEFT JOIN dataset_events e
                    ON c.dataset_id = e.dataset_id
                GROUP BY c.dataset_id
                ORDER BY c.dataset_id
                """
            ).fetchall()
        ]

        # Dataset-level alert table was introduced in Step 9.
        try:
            dataset_alert_count = query_one(
                conn,
                """
                SELECT COUNT(*)
                FROM dataset_sla_alerts
                WHERE alert_status = 'open'
                """,
            )
        except sqlite3.OperationalError:
            dataset_alert_count = None

        event_alert_count = query_one(
            conn,
            """
            SELECT COUNT(*)
            FROM sla_alerts
            WHERE alert_status = 'open'
            """,
        )

    latest_run_details = None

    if latest_run:
        (
            run_id,
            start_time,
            end_time,
            status,
            input_count,
            output_count,
            rejected_count,
            error_reason,
        ) = latest_run

        duration_seconds = None

        if start_time and end_time:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            duration_seconds = round(
                (end - start).total_seconds(), 2
            )

        latest_run_details = {
            "run_id": run_id,
            "start_time": start_time,
            "end_time": end_time,
            "status": status,
            "duration_seconds": duration_seconds,
            "input_count": input_count,
            "accepted_count": output_count,
            "rejected_count": rejected_count,
            "error_reason": error_reason,
        }

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pipeline": {
            "total_runs": run_count,
            "run_status_counts": run_statuses,
            "latest_run": latest_run_details,
        },
        "data_quality": {
            "total_accepted_events": total_events,
            "total_rejected_records": total_rejected,
            "acceptance_rate_percent": round(
                100 * total_events / (total_events + total_rejected), 2
            ) if total_events + total_rejected else 0,
            "rejection_reasons": rejection_reasons,
            "accepted_events_by_dataset": dataset_counts,
        },
        "alerts": {
            "open_event_alerts": event_alert_count,
            "open_dataset_alerts": dataset_alert_count,
        },
    }

    json_path = REPORT_DIR / "pipeline_summary.json"

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    rejected_path = REPORT_DIR / "rejected_records.csv"

    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """
            SELECT r.reject_id, r.run_id, r.source_file,
                   r.source_row, r.raw_record,
                   r.rejection_reason
            FROM rejected_records r
            ORDER BY r.reject_id
            """
        ).fetchall()

    fields = [
        "reject_id",
        "run_id",
        "source_file",
        "source_row",
        "raw_record",
        "rejection_reason",
    ]

    with open(
        rejected_path, "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        writer.writerows(rows)

    print(f"Summary report: {json_path}")
    print(f"Rejected records report: {rejected_path}")
    print(f"Total pipeline runs: {run_count}")
    print(f"Accepted events: {total_events}")
    print(f"Rejected records: {total_rejected}")
    print(f"Open event alerts: {event_alert_count}")
    print(f"Open dataset alerts: {dataset_alert_count}")


if __name__ == "__main__":
    generate_report()
