
import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_stage(name, command):
    print(f"\n{'=' * 60}")
    print(f"STAGE: {name}")
    print(f"COMMAND: {' '.join(command)}")
    print("=" * 60, flush=True)

    result = subprocess.run(command, cwd=ROOT)

    if result.returncode != 0:
        print(
            f"\nFAILED: {name} "
            f"(exit code {result.returncode})"
        )
        return False

    print(f"\nPASSED: {name}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Dataset SLA Monitoring pipeline runner"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of generated records per dataset",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible test data",
    )
    parser.add_argument(
        "--date",
        default="2026-10-30",
        help="Date used for synthetic data (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--skip-generate",
        action="store_true",
        help="Use existing CSV files instead of generating new ones",
    )
    args = parser.parse_args()

    if args.count < 0:
        parser.error("--count must be non-negative")

    start = datetime.now(timezone.utc)
    print("DATASET SLA MONITORING PIPELINE")
    print(f"Started at: {start.isoformat()}")

    stages = []

    stages.append(
        ("Initialize database", [sys.executable, "-m", "src.database"])
    )

    if not args.skip_generate:
        stages.append(
            (
                "Generate input data",
                [
                    sys.executable,
                    "scripts/generate_data.py",
                    "--count",
                    str(args.count),
                    "--seed",
                    str(args.seed),
                    "--date",
                    args.date,
                ],
            )
        )

    stages.extend(
        [
            ("Ingest and validate", [sys.executable, "-m", "src.ingest"]),
            ("Monitor SLAs", [sys.executable, "-m", "src.sla_monitor"]),
            ("Generate quality reports",[sys.executable, "-m", "src.quality_report"]),
        ]
    )

    failed_stage = None

    for name, command in stages:
        if not run_stage(name, command):
            failed_stage = name
            break

    end = datetime.now(timezone.utc)

    print(f"\n{'=' * 60}")
    print("PIPELINE SUMMARY")
    print(f"Started:  {start.isoformat()}")
    print(f"Finished: {end.isoformat()}")
    print(f"Duration: {(end - start).total_seconds():.2f} seconds")

    if failed_stage:
        print(f"Result: FAILED at {failed_stage}")
        sys.exit(1)

    print("Result: ALL STAGES COMPLETED")
    print("Check reports/sla_report.csv for the SLA report.")


if __name__ == "__main__":
    main()
