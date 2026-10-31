
from src.validate import validate_record, validate_schema
from datetime import datetime
from zoneinfo import ZoneInfo

from src.sla_monitor import evaluate_dataset_arrival

IST = ZoneInfo("Asia/Kolkata")

KNOWN_DATASETS = {"customers", "sales", "payments", "inventory"}


def valid_record():
    return {
        "event_id": "customers-00000001",
        "dataset_id": "customers",
        "expected_arrival": "2026-10-30T09:00:00+05:30",
        "actual_arrival": "2026-10-30T08:55:00+05:30",
        "completion_time": "2026-10-30T09:10:00+05:30",
        "source_file": "customers.csv",
    }


def test_valid_record():
    assert validate_record(
        valid_record(), KNOWN_DATASETS
    ) == []


def test_missing_required_dataset_id():
    record = valid_record()
    record["dataset_id"] = ""

    errors = validate_record(record, KNOWN_DATASETS)

    assert "dataset_id is required" in errors


def test_unknown_dataset_reference():
    record = valid_record()
    record["dataset_id"] = "unknown_dataset"

    errors = validate_record(record, KNOWN_DATASETS)

    assert any("Unknown dataset_id" in e for e in errors)


def test_malformed_timestamp():
    record = valid_record()
    record["expected_arrival"] = "not-a-date"

    errors = validate_record(record, KNOWN_DATASETS)

    assert any("not a valid ISO-8601" in e for e in errors)


def test_timestamp_requires_timezone():
    record = valid_record()
    record["expected_arrival"] = "2026-10-30T09:00:00"

    errors = validate_record(record, KNOWN_DATASETS)

    assert any("must include a timezone" in e for e in errors)


def test_completion_cannot_precede_arrival():
    record = valid_record()
    record["completion_time"] = "2026-10-30T08:50:00+05:30"

    errors = validate_record(record, KNOWN_DATASETS)

    assert "completion_time cannot precede actual_arrival" in errors


def test_missing_arrival_is_allowed():
    record = valid_record()
    record["actual_arrival"] = ""
    record["completion_time"] = ""

    assert validate_record(record, KNOWN_DATASETS) == []


def test_missing_csv_column():
    columns = [
        "event_id",
        "dataset_id",
        "expected_arrival",
    ]

    errors = validate_schema(columns)

    assert any("Missing columns" in e for e in errors)


def test_empty_csv_header():
    assert validate_schema(None) == ["CSV header is missing"]


def test_duplicate_event_id_is_deterministic():
    first = valid_record()
    second = valid_record()

    assert first["event_id"] == second["event_id"]

def test_dataset_missing_after_deadline():
    config = {
        "dataset_id": "payments",
        "expected_arrival_time": "11:00",
    }
    as_of = datetime(2026, 10, 30, 11, 30, tzinfo=IST)

    result = evaluate_dataset_arrival(config, None, as_of)

    assert result["status"] == "missing"


def test_dataset_awaiting_before_deadline():
    config = {
        "dataset_id": "payments",
        "expected_arrival_time": "11:00",
    }
    as_of = datetime(2026, 10, 30, 10, 30, tzinfo=IST)

    result = evaluate_dataset_arrival(config, None, as_of)

    assert result["status"] == "awaiting"


def test_dataset_arrived_by_deadline():
    config = {
        "dataset_id": "payments",
        "expected_arrival_time": "11:00",
    }
    latest_arrival = "2026-10-30T10:55:00+05:30"
    as_of = datetime(2026, 10, 30, 11, 30, tzinfo=IST)

    result = evaluate_dataset_arrival(
        config, latest_arrival, as_of
    )

    assert result["status"] == "arrived"