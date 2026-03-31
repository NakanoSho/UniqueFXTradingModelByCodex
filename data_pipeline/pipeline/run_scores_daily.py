"""Run daily scores derivation from bars/forward/regime."""

from __future__ import annotations

import argparse
import json
import sqlite3
import time
from pathlib import Path

from data_pipeline.derived.io import read_csv, write_partitioned_csv
from data_pipeline.derived.scores_daily import scores_daily
from trading.config import load_config


def _load_bars(base_dir: str, version: str) -> list[dict[str, object]]:
    base = Path(base_dir) / version
    rows: list[dict[str, object]] = []
    for path in base.rglob("data.csv"):
        rows.extend(read_csv(str(path)))
    return rows


def _load_regime(base_dir: str, version: str, date: str) -> dict[str, object]:
    path = Path(base_dir) / version / f"date={date}" / "data.csv"
    rows = read_csv(str(path))
    return rows[0] if rows else {"date": date, "fxvol20": 0.0, "voljump": 0.0, "spread_stress": 0.0}


def _load_forward(db_path: str, date: str) -> list[dict[str, object]]:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT ts, pair, fwd_1m_mid, spot_mid FROM forward_data WHERE ts <= ?",
            (f"{date}T23:59:59Z",),
        )
        rows = cur.fetchall()
    finally:
        conn.close()
    return [
        {"date": ts.split("T")[0], "pair": pair, "fwd_1m_mid": fwd, "spot_mid": spot}
        for ts, pair, fwd, spot in rows
    ]


def _load_exp_costs(db_path: str, date: str) -> dict[tuple[str, str], float]:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT ts, pair, sleeve, exp_cost_bps FROM expected_costs WHERE ts LIKE ?",
            (f"{date}%",),
        )
        rows = cur.fetchall()
    finally:
        conn.close()
    return {(pair, sleeve): float(cost) for ts, pair, sleeve, cost in rows}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Derived output base dir")
    parser.add_argument("--bars", default=None, help="Bars base dir (default: <output>/bars_daily)")
    parser.add_argument("--regime", default=None, help="Regime base dir (default: <output>/regime_daily)")
    parser.add_argument("--forward-db", required=True, help="Forward SQLite DB path")
    parser.add_argument("--date", required=True, help="Process date (YYYY-MM-DD)")
    parser.add_argument("--config", default="configs/v1_0.yaml", help="Config path")
    parser.add_argument("--cost-db", default=None, help="Expected cost DB path")
    parser.add_argument("--log", required=True, help="JSON log output path")
    args = parser.parse_args()

    config = load_config(args.config)
    start = time.time()
    bars_base = args.bars or str(Path(args.output) / "bars_daily")
    regime_base = args.regime or str(Path(args.output) / "regime_daily")
    bars = _load_bars(bars_base, config.version)
    regime_row = _load_regime(regime_base, config.version, args.date)
    forward_rows = _load_forward(args.forward_db, args.date)
    exp_costs = _load_exp_costs(args.cost_db, args.date) if args.cost_db else None
    scores = scores_daily(
        bars,
        forward_rows,
        regime_row,
        config,
        only_date=args.date,
        exp_cost_bps=exp_costs,
    )
    write_partitioned_csv(
        str(Path(args.output) / "scores_daily"),
        config.version,
        scores,
        partition_keys=["date"],
    )
    elapsed = time.time() - start
    log = {
        "rows": len(scores),
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
