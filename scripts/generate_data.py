import argparse
import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "datasets.json"
OUTPUT = ROOT / "data" / "input"

FIELDS = [
    "event_id",
    "dataset_id",
    "expected_arrival",
    "actual_arrival",
    "completion_time",
    "source_file"
]


def make_timestamp(day, hour, minute):
    return day.replace(
        hour=hour, minute=minute, second=0,
        microsecond=0
    ).isoformat()


def generate_records(config, count, seed, day):
    rng = random.Random(seed)
    records = []

    dataset_id = config["dataset_id"]
    hour, minute = map(
        int,
        config["expected_arrival_time"].split(":")
    )

    expected = day.replace(
        hour=hour, minute=minute,
        second=0, microsecond=0
    )

    for i in range(count):
        # Include on-time, late, and missing arrivals
        scenario = i % 10

        if scenario == 0:
            actual = None
            completed = None
        else:
            delay = (
                rng.randint(1, 60)
                if scenario in (1, 2)
                else -rng.randint(0, 15)
            )
            actual = expected + timedelta(minutes=delay)
            completed = actual + timedelta(
                minutes=rng.randint(5, 50)
            )

        records.append({
            "event_id": f"{dataset_id}-{i:08d}",
            "dataset_id": dataset_id,
            "expected_arrival": expected.isoformat(),
            "actual_arrival": (
                actual.isoformat() if actual else ""
            ),
            "completion_time": (
                completed.isoformat() if completed else ""
            ),
            "source_file": config["source_file"]
        })

    return records


def add_invalid_records(records):
    if not records:
        return

    # Duplicate event ID
    records.append(records[0].copy())

    # Missing required dataset ID
    invalid = records[0].copy()
    invalid["event_id"] += "-null"
    invalid["dataset_id"] = ""
    records.append(invalid)

    # Invalid reference to unknown dataset
    invalid = records[0].copy()
    invalid["event_id"] += "-reference"
    invalid["dataset_id"] = "unknown_dataset"
    records.append(invalid)

    # Malformed timestamp
    invalid = records[0].copy()
    invalid["event_id"] += "-timestamp"
    invalid["expected_arrival"] = "invalid-date"
    records.append(invalid)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--count", type=int, default=20
    )
    parser.add_argument(
        "--seed", type=int, default=42
    )
    parser.add_argument(
        "--date", default="2026-10-30"
    )
    args = parser.parse_args()

    if args.count < 0:
        parser.error("--count must be non-negative")

    day = datetime.strptime(
        args.date, "%Y-%m-%d"
    ).replace(tzinfo=ZoneInfo("Asia/Kolkata"))

    with open(CONFIG, encoding="utf-8") as f:
        configs = json.load(f)["datasets"]

    OUTPUT.mkdir(parents=True, exist_ok=True)

    for config in configs:
        records = generate_records(
            config, args.count, args.seed, day
        )
        add_invalid_records(records)

        filepath = OUTPUT / config["source_file"]

        with open(
            filepath, "w", newline="", encoding="utf-8"
        ) as f:
            writer = csv.DictWriter(
                f, fieldnames=FIELDS
            )
            writer.writeheader()
            writer.writerows(records)

        print(
            f"Created {filepath.name}: "
            f"{len(records)} records"
        )

if __name__ == "__main__":
    main()