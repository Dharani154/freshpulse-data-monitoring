
import csv
import json
import sqlite3
import sys
import uuid
from contextlib import closing
from datetime import datetime, timezone

from src.validate import validate_record, validate_schema
from src.database import get_connection, ROOT

INPUT_DIR = ROOT / "data" / "input"
CONFIG_PATH = ROOT / "config" / "datasets.json"


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def ingest_all():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        configs = json.load(f)["datasets"]

    run_id = str(uuid.uuid4())
    start_time = utc_now()

    input_count = 0
    output_count = 0
    rejected_count = 0
    errors = []

    # Create the run record before processing files.
    with closing(get_connection()) as conn, conn:
        known_datasets = {
            row[0]
            for row in conn.execute(
                "SELECT dataset_id FROM dataset_config"
            )
        }

        existing_event_ids = {
            row[0]
            for row in conn.execute(
                "SELECT event_id FROM dataset_events"
            )
        }

        conn.execute(
            """
            INSERT INTO pipeline_runs (
                run_id, start_time, status,
                input_count, output_count, rejected_count
            )
            VALUES (?, ?, ?, 0, 0, 0)
            """,
            (run_id, start_time, "running"),
        )

    for config in configs:
        filename = config["source_file"]
        filepath = INPUT_DIR / filename

        if not filepath.is_file():
            errors.append(f"{filename}: input file not found")
            continue

        file_input = 0
        file_output = 0
        file_rejected = 0
        accepted_event_ids = set()

        try:
            with open(
                filepath, newline="", encoding="utf-8-sig"
            ) as f:
                reader = csv.DictReader(f)
                schema_errors = validate_schema(reader.fieldnames)

                if schema_errors:
                    errors.extend(
                        f"{filename}: {error}"
                        for error in schema_errors
                    )
                    continue

                seen_in_file = set()

                # All database changes for this file commit together.
                # If a database operation fails, this file rolls back.
                with closing(get_connection()) as conn, conn:
                    for row_number, record in enumerate(
                        reader, start=2
                    ):
                        file_input += 1
                        reasons = []

                        if None in record:
                            reasons.append(
                                "Malformed row: extra CSV fields"
                            )

                        reasons.extend(
                            validate_record(record, known_datasets)
                        )

                        if record.get("source_file") != filename:
                            reasons.append(
                                "source_file does not match input file"
                            )

                        event_id = (
                            record.get("event_id") or ""
                        ).strip()

                        if event_id:
                            if event_id in seen_in_file:
                                reasons.append(
                                    f"Duplicate event_id in file: "
                                    f"{event_id}"
                                )
                            elif event_id in existing_event_ids:
                                reasons.append(
                                    f"event_id already exists: "
                                    f"{event_id}"
                                )

                            seen_in_file.add(event_id)

                        if reasons:
                            conn.execute(
                                """
                                INSERT INTO rejected_records (
                                    run_id, source_file, source_row,
                                    raw_record, rejection_reason
                                )
                                VALUES (?, ?, ?, ?, ?)
                                """,
                                (
                                    run_id,
                                    filename,
                                    row_number,
                                    json.dumps(
                                        record,
                                        sort_keys=True,
                                    ),
                                    "; ".join(
                                        sorted(set(reasons))
                                    ),
                                ),
                            )
                            file_rejected += 1
                            continue

                        conn.execute(
                            """
                            INSERT INTO dataset_events (
                                event_id, dataset_id,
                                expected_arrival, actual_arrival,
                                completion_time, source_file, run_id
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                event_id,
                                record["dataset_id"].strip(),
                                record["expected_arrival"].strip(),
                                (
                                    record.get("actual_arrival") or ""
                                ).strip() or None,
                                (
                                    record.get("completion_time") or ""
                                ).strip() or None,
                                filename,
                                run_id,
                            ),
                        )

                        file_output += 1
                        accepted_event_ids.add(event_id)

            # Only count committed file results.
            input_count += file_input
            output_count += file_output
            rejected_count += file_rejected
            existing_event_ids.update(accepted_event_ids)

        except (OSError, csv.Error, sqlite3.Error) as exc:
            # Earlier inserts from this file are rolled back.
            # Count attempted input rows, but not rolled-back writes.
            input_count += file_input
            errors.append(
                f"{filename}: {type(exc).__name__}: {exc}"
            )

    
    if errors:
        status = (
            "failed" if output_count == 0 else "partial_failed"
        )
    elif input_count > 0 and output_count == 0:
        status = "failed"
    elif rejected_count > 0:
        status = "partial_failed"
    else:
        status = "success"

    # Explain failed or partially failed runs in the audit record.
    error_reason = "; ".join(errors) if errors else None

    if rejected_count > 0:
        rejection_summary = (
            f"{rejected_count} record(s) rejected"
        )
        error_reason = (
            f"{error_reason}; {rejection_summary}"
            if error_reason
            else rejection_summary
        )

    if status == "failed" and not error_reason:
        error_reason = "No records were accepted"


    with closing(get_connection()) as conn, conn:
        conn.execute(
            """
            UPDATE pipeline_runs
            SET end_time = ?, status = ?,
                input_count = ?, output_count = ?,
                rejected_count = ?, error_reason = ?
            WHERE run_id = ?
            """,
            (
                utc_now(),
                status,
                input_count,
                output_count,
                rejected_count,
                error_reason,
                run_id,
            ),
        )

    print(f"Run ID: {run_id}")
    print(f"Status: {status}")
    print(f"Input records: {input_count}")
    print(f"Accepted records: {output_count}")
    print(f"Rejected records: {rejected_count}")

    for error in errors:
        print(f"ERROR: {error}")

    return status


if __name__ == "__main__":
    status = ingest_all()

    if status == "failed":
        sys.exit(1)
