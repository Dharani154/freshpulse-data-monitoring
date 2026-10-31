import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from src.database import get_connection, ROOT

REPORT_DIR = ROOT / "reports"
CONFIG_PATH = ROOT / "config" / "datasets.json"

def parse_timestamp(value):
    if not value:
        return None

    result = datetime.fromisoformat(value)

    if result.tzinfo is None:
        raise ValueError(
            f"Timestamp must include a timezone: {value}"
        )

    return result


def stable_alert_id(event_id, alert_type):
    """Create a deterministic ID to prevent repeated alerts."""
    value = f"{event_id}|{alert_type}"
    return hashlib.sha256(value.encode()).hexdigest()


def evaluate_event(event, config, as_of):
    """Return event status, delay, freshness and alert candidates."""
    expected = parse_timestamp(event["expected_arrival"])
    actual = parse_timestamp(event["actual_arrival"])
    completion = parse_timestamp(event["completion_time"])

    arrival_deadline = expected
    completion_deadline = expected.timestamp() + (
        config["completion_sla_minutes"] * 60
    )
    completion_deadline = datetime.fromtimestamp(
        completion_deadline, tz=timezone.utc
    )

    alerts = []
    delay_minutes = None

    if actual is None:
        if as_of > arrival_deadline:
            arrival_status = "missing"
            alerts.append((
                "missing_arrival",
                "critical",
                "Expected dataset arrival deadline has passed"
            ))
        else:
            arrival_status = "awaiting"
    else:
        delay_minutes = (
            actual - arrival_deadline
        ).total_seconds() / 60

        if delay_minutes > 0:
            arrival_status = "late"
            alerts.append((
                "late_arrival",
                "warning",
                f"Arrival was {delay_minutes:.1f} minutes late"
            ))
        else:
            arrival_status = "on_time"

    completion_status = "not_arrived"

    if actual is not None:
        if completion is not None:
            if completion > completion_deadline:
                completion_status = "late"
                alerts.append((
                    "late_completion",
                    "warning",
                    "Completion exceeded the configured deadline"
                ))
            else:
                completion_status = "completed_on_time"

        elif as_of > completion_deadline:
            completion_status = "overdue"
            alerts.append((
                "incomplete_processing",
                "critical",
                "Processing completion deadline has passed"
            ))
        else:
            completion_status = "processing"

    freshness_minutes = None

    if actual is not None:
        freshness_minutes = (
            as_of - actual
        ).total_seconds() / 60

        if freshness_minutes < 0:
            freshness_status = "future_timestamp"
        elif (
            freshness_minutes
            > config["freshness_threshold_minutes"]
        ):
            freshness_status = "stale"
        else:
            freshness_status = "fresh"
    else:
        freshness_status = "unknown"

    if freshness_status == "stale":
        alerts.append((
            "stale_data",
            "warning",
            f"Data age is {freshness_minutes:.1f} minutes"
        ))

    return {
        "event_id": event["event_id"],
        "dataset_id": event["dataset_id"],
        "expected_arrival": event["expected_arrival"],
        "actual_arrival": event["actual_arrival"] or "",
        "completion_time": event["completion_time"] or "",
        "arrival_status": arrival_status,
        "delay_minutes": (
            round(delay_minutes, 2)
            if delay_minutes is not None else ""
        ),
        "completion_status": completion_status,
        "freshness_minutes": (
            round(freshness_minutes, 2)
            if freshness_minutes is not None else ""
        ),
        "freshness_status": freshness_status,
        "alerts": alerts,
    }


def evaluate_dataset_arrival(config, latest_arrival, as_of):
    """
    Check whether a configured dataset arrived by its deadline.
    """
    dataset_id = config["dataset_id"]
    expected_time = config["expected_arrival_time"]

    hour, minute = map(int, expected_time.split(":"))

    from zoneinfo import ZoneInfo

    local_now = as_of.astimezone(ZoneInfo("Asia/Kolkata"))

    deadline = local_now.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0,
    )

    if latest_arrival is not None:
        latest = parse_timestamp(latest_arrival)

        if latest is not None and latest <= deadline:
            return {
                "dataset_id": dataset_id,
                "status": "arrived",
                "deadline": deadline.isoformat(),
                "message": "Dataset has arrived by its deadline",
            }

    if local_now > deadline:
        return {
            "dataset_id": dataset_id,
            "status": "missing",
            "deadline": deadline.isoformat(),
            "message": "Expected arrival deadline has passed",
        }

    return {
        "dataset_id": dataset_id,
        "status": "awaiting",
        "deadline": deadline.isoformat(),
        "message": "Arrival deadline has not passed",
    }


def save_dataset_arrival_alert(conn, config, result, as_of):
    """Persist a missing-arrival alert without requiring an event row."""
    import hashlib

    if result["status"] != "missing":
        return False

    dataset_id = config["dataset_id"]
    alert_type = "missing_dataset_arrival"

    # Stable ID makes repeated monitoring runs idempotent.
    alert_id = hashlib.sha256(
        f"{dataset_id}|{alert_type}|{result['deadline']}".encode("utf-8")
    ).hexdigest()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS dataset_sla_alerts (
            alert_id TEXT PRIMARY KEY,
            dataset_id TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            detected_at TEXT NOT NULL,
            alert_status TEXT NOT NULL,
            message TEXT NOT NULL,
            deadline TEXT NOT NULL,
            FOREIGN KEY (dataset_id)
                REFERENCES dataset_config(dataset_id)
        )
        """
    )

    cursor = conn.execute(
        """
        INSERT INTO dataset_sla_alerts (
            alert_id, dataset_id, alert_type, severity,
            detected_at, alert_status, message, deadline
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(alert_id) DO NOTHING
        """,
        (
            alert_id,
            dataset_id,
            alert_type,
            "critical",
            as_of.isoformat(),
            "open",
            result["message"],
            result["deadline"],
        ),
    )

    return cursor.rowcount == 1



def monitor(as_of=None):
    if as_of is None:
        as_of = datetime.now(timezone.utc)
    elif isinstance(as_of, str):
        as_of = parse_timestamp(as_of)

    with open(CONFIG_PATH, encoding="utf-8") as f:
        configs = {
            item["dataset_id"]: item
            for item in json.load(f)["datasets"]
        }

    with get_connection() as conn:
        conn.row_factory = __import__("sqlite3").Row

        events = conn.execute("""
            SELECT event_id, dataset_id, expected_arrival,
                   actual_arrival, completion_time, source_file
            FROM dataset_events
            ORDER BY dataset_id, expected_arrival, event_id
        """).fetchall()

        
# Check every configured dataset, including datasets with zero events.
        dataset_arrival_results = []

        for config in configs.values():
            latest_row = conn.execute(
                """
                SELECT MAX(actual_arrival)
                FROM dataset_events
                WHERE dataset_id = ?
                AND actual_arrival IS NOT NULL
                """,
                (config["dataset_id"],),
            ).fetchone()

            latest_arrival = latest_row[0] if latest_row else None

            result = evaluate_dataset_arrival(
                config,
                latest_arrival,
                as_of,
            )
            dataset_arrival_results.append(result)

            print(
                f"Dataset {result['dataset_id']}: "
                f"{result['status']} — {result['message']}"
            )


        # Keep the most recent successful arrival per dataset
        latest_arrivals = {}

        for event in events:
            if event["actual_arrival"]:
                actual = parse_timestamp(event["actual_arrival"])
                previous = latest_arrivals.get(
                    event["dataset_id"]
                )

                if previous is None or actual > previous[0]:
                    latest_arrivals[event["dataset_id"]] = (
                        actual, event["event_id"]
                    )

        results = []
        alert_count = 0

        for event in events:
            config = configs.get(event["dataset_id"])

            if config is None:
                continue

            result = evaluate_event(event, config, as_of)

            for alert_type, severity, message in result["alerts"]:
                alert_id = stable_alert_id(
                    event["event_id"], alert_type
                )

                conn.execute("""
                    INSERT INTO sla_alerts (
                        alert_id, event_id, dataset_id,
                        alert_type, severity, detected_at,
                        alert_status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, 'open')
                    ON CONFLICT(alert_id) DO NOTHING
                """, (
                    alert_id,
                    event["event_id"],
                    event["dataset_id"],
                    alert_type,
                    severity,
                    as_of.isoformat(),
                ))

                alert_count += 1

            results.append(result)

        

        # Check the most recent arrival for each dataset
        for dataset_id, config in configs.items():
            latest = latest_arrivals.get(dataset_id)

            if latest is None:
                continue

            latest_timestamp, event_id = latest
            age_minutes = (
                as_of - latest_timestamp
            ).total_seconds() / 60

            if (
                age_minutes > config["freshness_threshold_minutes"]
                and age_minutes >= 0
            ):
                alert_id = stable_alert_id(
                    event_id, "dataset_stale"
                )

                conn.execute("""
                    INSERT INTO sla_alerts (
                        alert_id, event_id, dataset_id,
                        alert_type, severity, detected_at,
                        alert_status
                    )
                    VALUES (?, ?, ?, 'dataset_stale',
                            'warning', ?, 'open')
                    ON CONFLICT(alert_id) DO NOTHING
                """, (
                    alert_id,
                    event_id,
                    dataset_id,
                    as_of.isoformat(),
                ))



    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / "sla_report.csv"

    columns = [
        "event_id",
        "dataset_id",
        "expected_arrival",
        "actual_arrival",
        "completion_time",
        "arrival_status",
        "delay_minutes",
        "completion_status",
        "freshness_minutes",
        "freshness_status",
    ]

    with open(
        report_path, "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()

        for result in results:
            writer.writerow({
                key: result[key] for key in columns
            })

    print(f"Monitoring time: {as_of.isoformat()}")
    print(f"Events evaluated: {len(results)}")
    print(f"Alert candidates evaluated: {alert_count}")
    print(f"Report created: {report_path}")

    for result in results:
        if result["alerts"]:
            print(
                f'{result["dataset_id"]} / '
                f'{result["event_id"]}: '
                f'{result["arrival_status"]}; '
                f'{result["completion_status"]}; '
                f'{result["freshness_status"]}'
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--as-of",
        help="Monitoring timestamp in ISO-8601 format"
    )
    args = parser.parse_args()

    monitor(args.as_of)
