"""Reproducibility check for spot pipeline."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import time

from data_pipeline.ingest.spot import ingest_spot
from data_pipeline.normalize.spot import normalize_rows
from data_pipeline.qc.spot import qc_spot_rows
from data_pipeline.store.spot import init_db, insert_rows


def _run_pipeline(input_path: str, db_path: str, source: str) -> int:
    raw = ingest_spot(input_path)
    normalized = normalize_rows(raw)
    qc_rows = qc_spot_rows(normalized)
    init_db(db_path)
    return insert_rows(db_path, qc_rows, source)


def _hash_db(db_path: str) -> str:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT ts, pair, mid, bid, ask, spread, spread_stress, gap_flag FROM spot_data ORDER BY ts, pair")
        rows = cur.fetchall()
    finally:
        conn.close()
    h = hashlib.sha256()
    for row in rows:
        h.update(repr(row).encode("utf-8"))
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="CSV input path")
    parser.add_argument("--db1", required=True, help="First run DB path")
    parser.add_argument("--db2", required=True, help="Second run DB path")
    parser.add_argument("--source", required=True, help="Source identifier")
    parser.add_argument("--log", required=True, help="JSON log output path")
    args = parser.parse_args()

    start = time.time()
    rows1 = _run_pipeline(args.input, args.db1, args.source)
    rows2 = _run_pipeline(args.input, args.db2, args.source)
    hash1 = _hash_db(args.db1)
    hash2 = _hash_db(args.db2)
    elapsed = time.time() - start

    result = {
        "rows_run1": rows1,
        "rows_run2": rows2,
        "hash_match": hash1 == hash2,
        "elapsed_sec": round(elapsed, 6),
    }
    with open(args.log, "w") as f:
        json.dump(result, f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
