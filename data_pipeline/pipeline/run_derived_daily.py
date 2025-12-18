"""Run bars/regime/scores daily jobs."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Tick input path (CSV or Parquet)")
    parser.add_argument("--output", required=True, help="Derived output base dir")
    parser.add_argument("--forward-db", required=True, help="Forward SQLite DB path")
    parser.add_argument("--date", required=True, help="Process date (YYYY-MM-DD)")
    parser.add_argument("--config", default="configs/v1_0.yaml", help="Config path")
    parser.add_argument("--cost-db", default=None, help="Expected cost DB path")
    parser.add_argument("--log-dir", default=None, help="Log output directory")
    args = parser.parse_args()

    log_dir = args.log_dir or os.path.join(args.output, "logs")
    os.makedirs(log_dir, exist_ok=True)
    bars_log = os.path.join(log_dir, "bars_daily.json")
    regime_log = os.path.join(log_dir, "regime_daily.json")
    scores_log = os.path.join(log_dir, "scores_daily.json")

    cmd_bars = [
        sys.executable,
        "-m",
        "data_pipeline.pipeline.run_bars_daily",
        "--input",
        args.input,
        "--output",
        args.output,
        "--date",
        args.date,
        "--config",
        args.config,
        "--log",
        bars_log,
    ]
    subprocess.check_call(cmd_bars)

    cmd_regime = [
        sys.executable,
        "-m",
        "data_pipeline.pipeline.run_regime_daily",
        "--output",
        args.output,
        "--date",
        args.date,
        "--config",
        args.config,
        "--log",
        regime_log,
    ]
    subprocess.check_call(cmd_regime)

    cmd_scores = [
        sys.executable,
        "-m",
        "data_pipeline.pipeline.run_scores_daily",
        "--forward-db",
        args.forward_db,
        "--output",
        args.output,
        "--date",
        args.date,
        "--config",
        args.config,
        "--log",
        scores_log,
    ]
    if args.cost_db:
        cmd_scores.extend(["--cost-db", args.cost_db])
    subprocess.check_call(cmd_scores)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
