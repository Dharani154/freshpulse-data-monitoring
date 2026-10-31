
import csv
from datetime import datetime


REQUIRED_COLUMNS = {
    "event_id",
    "dataset_id",
    "expected_arrival",
    "actual_arrival",
    "completion_time",
    "source_file",
}


def validate_schema(fieldnames):
    """Check whether a CSV has the expected columns."""
    if not fieldnames:
        return ["CSV header is missing"]

    missing = REQUIRED_COLUMNS - set(fieldnames)
    unexpected = set(fieldnames) - REQUIRED_COLUMNS

    errors = []

    if missing:
        errors.append(
            f"Missing columns: {', '.join(sorted(missing))}"
        )

    if unexpected:
        errors.append(
            f"Unexpected columns: {', '.join(sorted(unexpected))}"
        )

    return errors


def valid_timestamp(value, field_name, required=False):
    if value is None or not value.strip():
        if required:
            return None, f"{field_name} is required"
        return None, None

    try:
        timestamp = datetime.fromisoformat(value.strip())

        # Require an explicit timezone to avoid ambiguous times.
        if timestamp.tzinfo is None:
            return None, f"{field_name} must include a timezone"

        return timestamp, None

    except ValueError:
        return None, f"{field_name} is not a valid ISO-8601 timestamp"


def validate_record(record, known_datasets):
    """Return a list of validation errors for one record."""
    errors = []

    for field in REQUIRED_COLUMNS:
        if field not in record:
            errors.append(f"Missing field: {field}")

    if errors:
        return errors

    event_id = (record.get("event_id") or "").strip()
    dataset_id = (record.get("dataset_id") or "").strip()
    source_file = (record.get("source_file") or "").strip()

    if not event_id:
        errors.append("event_id is required")

    if not dataset_id:
        errors.append("dataset_id is required")
    elif dataset_id not in known_datasets:
        errors.append(f"Unknown dataset_id: {dataset_id}")

    if not source_file:
        errors.append("source_file is required")

    expected, error = valid_timestamp(
        record.get("expected_arrival"),
        "expected_arrival",
        required=True,
    )
    if error:
        errors.append(error)

    actual, error = valid_timestamp(
        record.get("actual_arrival"),
        "actual_arrival",
    )
    if error:
        errors.append(error)

    completion, error = valid_timestamp(
        record.get("completion_time"),
        "completion_time",
    )
    if error:
        errors.append(error)

    if actual and completion and completion < actual:
        errors.append(
            "completion_time cannot precede actual_arrival"
        )

    if completion and not actual:
        errors.append(
            "completion_time cannot exist without actual_arrival"
        )

    return errors