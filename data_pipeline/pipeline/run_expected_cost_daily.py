"""Compute expected costs from trade intents and store them."""

from __future__ import annotations

import argparse
import csv
import json
import time
from typing import Dict, List

from trading.config import load_config
from trading.tca.cost import (
    LiquidityTierParams,
    cost_params_from_config,
    estimate_expected_cost_bps,
    trade_allowed,
)
from data_pipeline.store.cost import init_db, insert_rows


def read_intents(path: str) -> List[Dict[str, str]]:
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="CSV input path")
    parser.add_argument("--db", required=True, help="SQLite DB path")
    parser.add_argument("--source", required=True, help="Source identifier")
    parser.add_argument("--log", required=True, help="JSON log output path")
    parser.add_argument("--config", default="configs/v1_0.yaml", help="Config path")
    args = parser.parse_args()

    start = time.time()
    rows = read_intents(args.input)
    config = load_config(args.config)
    cost_params = cost_params_from_config(config)
    tier_params = LiquidityTierParams()
    out_rows = []
    for row in rows:
        exp = estimate_expected_cost_bps(
            bid=float(row["bid"]),
            ask=float(row["ask"]),
            mid=float(row["mid"]),
            exec_vol_bps=float(row["exec_vol_bps"]),
            delta_w=float(row["delta_w"]),
            nav=float(row["nav"]),
            pair=row["pair"].upper().replace("/", ""),
            cost_params=cost_params,
            tier_params=tier_params,
        )
        if row.get("is_satellite") is not None and str(row.get("is_satellite")).strip() != "":
            is_sat = str(row.get("is_satellite")).strip().lower() in ("1", "true", "yes", "y")
            sleeve = "satellite" if is_sat else "core"
        else:
            sleeve = row.get("sleeve", "core").lower()
            is_sat = sleeve == "satellite"
        allowed = trade_allowed(exp, is_sat, cost_params)
        out_rows.append(
            {
                "ts": row["ts"],
                "pair": row["pair"].upper().replace("/", ""),
                "sleeve": sleeve,
                "exp_cost_bps": exp,
                "trade_allowed": allowed,
            }
        )
    init_db(args.db)
    inserted = insert_rows(args.db, out_rows, args.source)
    elapsed = time.time() - start
    with open(args.log, "w") as f:
        json.dump({"rows": inserted, "elapsed_sec": round(elapsed, 6), "config": args.config}, f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
