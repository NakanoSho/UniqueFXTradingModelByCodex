"""Generate daily report and alert output from metrics JSON."""

from __future__ import annotations

import argparse
import csv
import json

from ops.alerts.monitor import AlertThresholds, build_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Metrics JSON path")
    parser.add_argument("--report", required=True, help="Report JSON output path")
    parser.add_argument("--csv", required=True, help="CSV output path")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        metrics = json.load(f)

    report = build_report(metrics, AlertThresholds())

    with open(args.report, "w") as f:
        json.dump(report, f)

    with open(args.csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        for k, v in metrics.items():
            writer.writerow([k, v])
        writer.writerow(["alerts", ";".join(report["alerts"])])
        writer.writerow(["ok", report["ok"]])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
