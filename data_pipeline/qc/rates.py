"""Quality checks for rates data."""

from __future__ import annotations

from typing import Dict, List


def qc_rates_rows(rows: List[Dict[str, object]], min_rate: float = -0.05, max_rate: float = 0.2) -> List[Dict[str, object]]:
    output: List[Dict[str, object]] = []
    for row in rows:
        rate = float(row["ois_1m"])
        flag = rate < min_rate or rate > max_rate
        out = dict(row)
        out["qc_flag"] = flag
        out["rate_flag"] = flag
        output.append(out)
    return output
