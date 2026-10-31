
import csv
import json

import src.database as database
import src.ingest as ingest


def setup_test_environment(tmp_path, monkeypatch):
    """Create an isolated database, configuration, and input folder."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    config_path = tmp_path / "datasets.json"
    db_path = tmp_path / "monitoring.db"

    config = {
        "datasets": [
            {
                "dataset_id": "customers",
                "source_file": "customers.csv",
                "expected_arrival_time": "09:00",
                "completion_sla_minutes": 30,
                "freshness_threshold_minutes": 120,
            }
        ]
    }

    config_path.write_text(
        json.dumps(config), encoding="utf-8"
    )

    monkeypatch.setattr(database, "DB_PATH", db_path)
    monkeypatch.setattr(database, "CONFIG_PATH", config_path)
    monkeypatch.setattr(ingest, "INPUT_DIR", input_dir)
    monkeypatch.setattr(ingest, "CONFIG_PATH", config_path)

    database.initialize_database()

    return input_dir, db_path


def write_csv(path, rows):
    fields = [
        "event_id",
        "dataset_id",
        "expected_arrival",
        "actual_arrival",
        "completion_time",
        "source_file",
    ]

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def valid_record():
    return {
        "event_id": "customers-00000001",
        "dataset_id": "customers",
        "expected_arrival": "2026-10-30T09:00:00+05:30",
        "actual_arrival": "2026-10-30T09:05:00+05:30",
        "completion_time": "2026-10-30T09:15:00+05:30",
        "source_file": "customers.csv",
    }


def get_counts(db_path):
    import sqlite3

    with sqlite3.connect(db_path) as conn:
        events = conn.execute(
            "SELECT COUNT(*) FROM dataset_events"
        ).fetchone()[0]
        rejected = conn.execute(
            "SELECT COUNT(*) FROM rejected_records"
        ).fetchone()[0]
        runs = conn.execute(
            "SELECT COUNT(*) FROM pipeline_runs"
        ).fetchone()[0]

    return events, rejected, runs


def test_valid_record_is_ingested(tmp_path, monkeypatch):
    input_dir, db_path = setup_test_environment(
        tmp_path, monkeypatch
    )
    write_csv(input_dir / "customers.csv", [valid_record()])

    ingest.ingest_all()

    events, rejected, runs = get_counts(db_path)
    assert events == 1
    assert rejected == 0
    assert runs == 1


def test_duplicate_is_not_inserted_twice(tmp_path, monkeypatch):
    input_dir, db_path = setup_test_environment(
        tmp_path, monkeypatch
    )
    write_csv(input_dir / "customers.csv", [valid_record()])

    ingest.ingest_all()
    ingest.ingest_all()

    events, rejected, runs = get_counts(db_path)
    assert events == 1
    assert rejected == 1
    assert runs == 2


def test_empty_csv_is_handled(tmp_path, monkeypatch):
    input_dir, db_path = setup_test_environment(
        tmp_path, monkeypatch
    )
    write_csv(input_dir / "customers.csv", [])

    ingest.ingest_all()

    events, rejected, runs = get_counts(db_path)
    assert events == 0
    assert rejected == 0
    assert runs == 1


def test_missing_input_file_is_recorded_as_failure(
    tmp_path, monkeypatch
):
    _, db_path = setup_test_environment(tmp_path, monkeypatch)

    ingest.ingest_all()

    import sqlite3

    with sqlite3.connect(db_path) as conn:
        run = conn.execute(
            "SELECT status, error_reason FROM pipeline_runs"
        ).fetchone()

    assert run[0] == "failed"
    assert "input file not found" in run[1]


def test_duplicate_run_is_recorded_as_failed(tmp_path, monkeypatch):
    input_dir, db_path = setup_test_environment(
        tmp_path, monkeypatch
    )
    write_csv(input_dir / "customers.csv", [valid_record()])

    ingest.ingest_all()
    ingest.ingest_all()

    import sqlite3

    with sqlite3.connect(db_path) as conn:
        runs = conn.execute(
            """
            SELECT status, input_count, output_count, rejected_count
            FROM pipeline_runs
            ORDER BY start_time
            """
        ).fetchall()

    assert runs[0] == ("success", 1, 1, 0)
    assert runs[1] == ("failed", 1, 0, 1)


def test_run_counts_match_database_audit_records(
    tmp_path, monkeypatch
):
    input_dir, db_path = setup_test_environment(
        tmp_path, monkeypatch
    )
    write_csv(input_dir / "customers.csv", [valid_record()])

    ingest.ingest_all()

    import sqlite3

    with sqlite3.connect(db_path) as conn:
        run = conn.execute(
            """
            SELECT input_count, output_count, rejected_count
            FROM pipeline_runs
            """
        ).fetchone()

        event_count = conn.execute(
            "SELECT COUNT(*) FROM dataset_events"
        ).fetchone()[0]

        reject_count = conn.execute(
            "SELECT COUNT(*) FROM rejected_records"
        ).fetchone()[0]

    assert run == (1, 1, 0)
    assert event_count == run[1]
    assert reject_count == run[2]
    assert run[0] == run[1] + run[2]
