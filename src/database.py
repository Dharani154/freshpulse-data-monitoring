import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "monitoring.db"
CONFIG_PATH = ROOT / "config" / "datasets.json"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS dataset_config (
                dataset_id TEXT PRIMARY KEY,
                source_file TEXT NOT NULL,
                expected_arrival_time TEXT NOT NULL,
                completion_sla_minutes INTEGER NOT NULL
                    CHECK (completion_sla_minutes > 0),
                freshness_threshold_minutes INTEGER NOT NULL
                    CHECK (freshness_threshold_minutes > 0)
            );

            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                status TEXT NOT NULL,
                input_count INTEGER DEFAULT 0,
                output_count INTEGER DEFAULT 0,
                rejected_count INTEGER DEFAULT 0,
                error_reason TEXT
            );

            CREATE TABLE IF NOT EXISTS dataset_events (
                event_id TEXT PRIMARY KEY,
                dataset_id TEXT NOT NULL,
                expected_arrival TEXT NOT NULL,
                actual_arrival TEXT,
                completion_time TEXT,
                source_file TEXT NOT NULL,
                run_id TEXT NOT NULL,
                FOREIGN KEY (dataset_id)
                    REFERENCES dataset_config(dataset_id),
                FOREIGN KEY (run_id)
                    REFERENCES pipeline_runs(run_id)
            );

            CREATE TABLE IF NOT EXISTS rejected_records (
                reject_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                source_file TEXT NOT NULL,
                source_row INTEGER NOT NULL,
                raw_record TEXT NOT NULL,
                rejection_reason TEXT NOT NULL,
                FOREIGN KEY (run_id)
                    REFERENCES pipeline_runs(run_id)
            );

            CREATE TABLE IF NOT EXISTS sla_alerts (
                alert_id TEXT PRIMARY KEY,
                event_id TEXT NOT NULL,
                dataset_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                detected_at TEXT NOT NULL,
                alert_status TEXT NOT NULL,
                FOREIGN KEY (event_id)
                    REFERENCES dataset_events(event_id),
                FOREIGN KEY (dataset_id)
                    REFERENCES dataset_config(dataset_id)
            );
        """)

        with open(CONFIG_PATH, encoding="utf-8") as f:
            configs = json.load(f)["datasets"]

        for item in configs:
            conn.execute("""
                INSERT INTO dataset_config (
                    dataset_id, source_file,
                    expected_arrival_time,
                    completion_sla_minutes,
                    freshness_threshold_minutes
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(dataset_id) DO UPDATE SET
                    source_file = excluded.source_file,
                    expected_arrival_time =
                        excluded.expected_arrival_time,
                    completion_sla_minutes =
                        excluded.completion_sla_minutes,
                    freshness_threshold_minutes =
                        excluded.freshness_threshold_minutes
            """, (
                item["dataset_id"],
                item["source_file"],
                item["expected_arrival_time"],
                item["completion_sla_minutes"],
                item["freshness_threshold_minutes"]
            ))

    print("Database initialized successfully!")


if __name__ == "__main__":
    initialize_database()
