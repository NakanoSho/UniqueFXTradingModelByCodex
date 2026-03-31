"""Compute daily volatility indicators from spot data and store them."""

from __future__ import annotations

import argparse
import json
import time

from data_pipeline.features.volatility import (
    compute_fxvol20,
    compute_spread_stress,
    compute_voljump,
    fetch_spot_series,
)
from data_pipeline.store.vol import init_db, insert_row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spot-db", required=True, help="SQLite spot DB path")
    parser.add_argument("--db", required=True, help="SQLite metrics DB path")
    parser.add_argument("--ts", required=True, help="Timestamp label")
    parser.add_argument("--source", required=True, help="Source identifier")
    parser.add_argument("--log", required=True, help="JSON log output path")
    args = parser.parse_args()

    start = time.time()
    series = fetch_spot_series(args.spot_db)
    fxvol20 = compute_fxvol20(series)
    voljump = compute_voljump(series)
    spread_stress = compute_spread_stress(series)
    init_db(args.db)
    insert_row(
        args.db,
        {
            "ts": args.ts,
            "fxvol20": fxvol20,
            "voljump": voljump,
            "spread_stress": spread_stress,
        },
        args.source,
    )
    elapsed = time.time() - start
    with open(args.log, "w") as f:
        json.dump({"ts": args.ts, "elapsed_sec": round(elapsed, 6)}, f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
