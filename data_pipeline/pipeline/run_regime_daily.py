"""Run daily regime derivation from bars."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from data_pipeline.derived.io import read_csv, write_partitioned_csv
from data_pipeline.derived.regime_daily import regime_daily
from trading.config import load_config


def _load_bars(base_dir: str, version: str) -> list[dict[str, object]]:
    base = Path(base_dir) / version
    rows: list[dict[str, object]] = []
    for path in base.rglob("data.csv"):
        rows.extend(read_csv(str(path)))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Derived output base dir")
    parser.add_argument("--bars", default=None, help="Bars base dir (default: <output>/bars_daily)")
    parser.add_argument("--date", default=None, help="Process only this date (YYYY-MM-DD)")
    parser.add_argument("--config", default="configs/v1_0.yaml", help="Config path")
    parser.add_argument("--log", required=True, help="JSON log output path")
    args = parser.parse_args()

    config = load_config(args.config)
    start = time.time()
    bars_base = args.bars or str(Path(args.output) / "bars_daily")
    bars = _load_bars(bars_base, config.version)
    regime_rows = regime_daily(bars, only_date=args.date)
    write_partitioned_csv(
        str(Path(args.output) / "regime_daily"),
        config.version,
        regime_rows,
        partition_keys=["date"],
    )
    elapsed = time.time() - start
    log = {
        "rows": len(regime_rows),
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
