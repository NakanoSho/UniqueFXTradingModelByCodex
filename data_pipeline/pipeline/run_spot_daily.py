"""Run daily spot pipeline: ingest -> normalize -> QC -> store."""

from __future__ import annotations

import argparse
import json
import time

from data_pipeline.ingest.spot import ingest_spot
from data_pipeline.normalize.spot import normalize_rows
from data_pipeline.qc.spot import qc_spot_rows
from data_pipeline.store.spot import init_db, insert_rows
from trading.config import load_config


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Tick input path (CSV or Parquet)")
    parser.add_argument("--db", required=True, help="SQLite DB path")
    parser.add_argument("--source", required=True, help="Source identifier")
    parser.add_argument("--log", required=True, help="JSON log output path")
    parser.add_argument("--config", default="configs/v1_0.yaml", help="Config path")
    args = parser.parse_args()

    config = load_config(args.config)
    start = time.time()
    raw = ingest_spot(args.input)
    normalized = normalize_rows(raw)
    qc_rows = qc_spot_rows(normalized, max_gap_seconds=config.data_qc.max_gap_seconds)
    init_db(args.db)
    inserted = insert_rows(args.db, qc_rows, args.source)
    elapsed = time.time() - start

    log = {
        "input": args.input,
        "db": args.db,
        "source": args.source,
        "rows": inserted,
        "elapsed_sec": round(elapsed, 6),
        "config": args.config,
    }
    with open(args.log, "w") as f:
        json.dump(log, f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
