"""Run daily bars derivation from tick input."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from data_pipeline.derived.bars_daily import ticks_to_daily_bars
from data_pipeline.derived.io import write_partitioned_csv
from data_pipeline.ingest.spot import ingest_spot
from data_pipeline.normalize.spot import normalize_rows
from data_pipeline.qc.spot import qc_spot_rows
from trading.config import load_config


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Tick input path (CSV or Parquet)")
    parser.add_argument("--output", required=True, help="Derived output base dir")
    parser.add_argument("--date", default=None, help="Process only this date (YYYY-MM-DD)")
    parser.add_argument("--config", default="configs/v1_0.yaml", help="Config path")
    parser.add_argument("--log", required=True, help="JSON log output path")
    args = parser.parse_args()

    config = load_config(args.config)
    start = time.time()
    raw = ingest_spot(args.input)
    normalized = normalize_rows(raw)
    qc_rows = qc_spot_rows(normalized, max_gap_seconds=config.data_qc.max_gap_seconds)
    bars = ticks_to_daily_bars(qc_rows, config.bars_daily.close_time_utc, only_date=args.date)
    write_partitioned_csv(
        str(Path(args.output) / "bars_daily"),
        config.version,
        bars,
        partition_keys=["pair", "date"],
    )
    elapsed = time.time() - start
    log = {
        "rows": len(bars),
        "elapsed_sec": round(elapsed, 6),
        "config": args.config,
        "output": args.output,
        "date": args.date,
    }
    with open(args.log, "w") as f:
        json.dump(log, f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
