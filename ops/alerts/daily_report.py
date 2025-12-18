"""Generate daily monitoring report from metrics JSON."""

from __future__ import annotations

import argparse
import json

from ops.alerts.monitor import AlertThresholds, build_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", required=True, help="Input metrics JSON")
    parser.add_argument("--output", required=True, help="Output report JSON")
    args = parser.parse_args()

    with open(args.metrics, "r") as f:
        metrics = json.load(f)
    report = build_report(metrics, AlertThresholds())
    with open(args.output, "w") as f:
        json.dump(report, f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
