"""Run daily macro pipeline: ingest -> normalize -> QC -> store."""

from __future__ import annotations

import argparse
import json
import time

from data_pipeline.ingest.macro import ingest_macro
from data_pipeline.normalize.macro import normalize_rows
from data_pipeline.qc.macro import qc_macro_rows
from data_pipeline.store.macro import init_db, insert_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="CSV input path")
    parser.add_argument("--db", required=True, help="SQLite DB path")
    parser.add_argument("--source", required=True, help="Source identifier")
    parser.add_argument("--log", required=True, help="JSON log output path")
    args = parser.parse_args()

    start = time.time()
    raw = ingest_macro(args.input)
    normalized = normalize_rows(raw)
    qc_rows = qc_macro_rows(normalized)
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
