"""Run daily rates pipeline: ingest -> normalize -> QC -> store."""

from __future__ import annotations

import argparse
import json
import time

from data_pipeline.ingest.rates import ingest_rates
from data_pipeline.normalize.rates import normalize_rows
from data_pipeline.qc.rates import qc_rates_rows
from data_pipeline.store.rates import init_db, insert_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="CSV input path")
    parser.add_argument("--db", required=True, help="SQLite DB path")
    parser.add_argument("--source", required=True, help="Source identifier")
    parser.add_argument("--log", required=True, help="JSON log output path")
    args = parser.parse_args()

    start = time.time()
    raw = ingest_rates(args.input)
    normalized = normalize_rows(raw)
    qc_rows = qc_rates_rows(normalized)
    init_db(args.db)
    inserted = insert_rows(args.db, qc_rows, args.source)
    elapsed = time.time() - start

    log = {
        "input": args.input,
        "db": args.db,
        "source": args.source,
        "rows": inserted,
        "elapsed_sec": round(elapsed, 6),
    }
    with open(args.log, "w") as f:
        json.dump(log, f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
