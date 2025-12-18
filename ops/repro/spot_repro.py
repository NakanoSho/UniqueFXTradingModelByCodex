"""Reproducibility check for spot pipeline outputs."""

from __future__ import annotations

import argparse
import json
import sqlite3
import tempfile

from data_pipeline.ingest.spot import ingest_spot
from data_pipeline.normalize.spot import normalize_rows
from data_pipeline.qc.spot import qc_spot_rows
from data_pipeline.store.spot import init_db, insert_rows


def _run_spot(input_path: str, db_path: str, source: str) -> int:
    raw = ingest_spot(input_path)
    normalized = normalize_rows(raw)
    qc_rows = qc_spot_rows(normalized)
    init_db(db_path)
    return insert_rows(db_path, qc_rows, source)


def _fetch_rows(db_path: str):
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT ts, pair, mid, bid, ask, open, high, low, close, spread, spread_stress, gap_flag, source FROM spot_data ORDER BY ts, pair"
        )
        return cur.fetchall()
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Spot CSV input path")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument("--source", default="repro", help="Source identifier")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as d:
        db1 = f"{d}/spot1.db"
        db2 = f"{d}/spot2.db"
        count1 = _run_spot(args.input, db1, args.source)
        count2 = _run_spot(args.input, db2, args.source)
        rows1 = _fetch_rows(db1)
        rows2 = _fetch_rows(db2)
        ok = rows1 == rows2 and count1 == count2

    report = {"ok": ok, "rows": count1}
    with open(args.output, "w") as f:
        json.dump(report, f)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
