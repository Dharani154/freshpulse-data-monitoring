
import csv
from collections import Counter

from src.database import get_connection, ROOT

REPORT_DIR = ROOT / "reports"
REPORT_FILE = REPORT_DIR / "rejection_summary.csv"


def categorize_reason(reason):
    reason = reason or ""

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

    return reason


def generate_rejection_report():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT rejection_reason FROM rejected_records"
        ).fetchall()

    counts = Counter()

    for (reason,) in rows:
        # A record can have multiple reasons separated by semicolons.
        for reason_part in (reason or "").split("; "):
            category = categorize_reason(reason_part.strip())
            if category:
                counts[category] += 1

    with REPORT_FILE.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["rejection_category", "rejection_count"])

        for category, count in counts.most_common():
            writer.writerow([category, count])

    print(f"Rejection report created: {REPORT_FILE}")
    print(f"Total rejected records: {len(rows)}")
    print(f"Unique rejection categories: {len(counts)}")


if __name__ == "__main__":
    generate_rejection_report()
