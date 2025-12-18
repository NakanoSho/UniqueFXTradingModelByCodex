"""Quality checks for spot data (gap, spread stress)."""

from __future__ import annotations

import math
import statistics
from typing import Dict, List, Tuple


def _log_return(curr: float, prev: float) -> float:
    if prev <= 0.0 or curr <= 0.0:
        return 0.0
    return math.log(curr / prev)


def qc_spot_rows(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    # Process per pair in order of ts (assumed ordered input).
    by_pair: Dict[str, List[Dict[str, object]]] = {}
    for row in rows:
        pair = row["pair"]
        by_pair.setdefault(pair, []).append(row)

    output: List[Dict[str, object]] = []
    for pair, series in by_pair.items():
        spreads: List[float] = []
        returns: List[float] = []
        prev_mid = None
        for row in series:
            mid = float(row["mid"])
            bid = float(row["bid"])
            ask = float(row["ask"])
            spread = max(0.0, ask - bid)
            spreads.append(spread)

            gap_flag = False
            if prev_mid is not None:
                r = _log_return(mid, prev_mid)
                returns.append(r)
                if len(returns) >= 60:
                    window = returns[-60:]
                    mean = sum(window) / 60
                    var = sum((x - mean) ** 2 for x in window) / 60
                    std = math.sqrt(var)
                    if std > 0.0 and abs(r) > 8.0 * std:
                        gap_flag = True
            prev_mid = mid

            if len(spreads) >= 60:
                med = statistics.median(spreads[-60:])
                spread_stress = (spread / med) if med > 0.0 else 1.0
            else:
                spread_stress = 1.0

            out = dict(row)
            out["spread"] = spread
            out["spread_stress"] = spread_stress
            out["gap_flag"] = gap_flag
            output.append(out)
    return output
