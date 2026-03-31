"""Quality checks for macro data."""

from __future__ import annotations

from typing import Dict, List


def qc_macro_rows(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    out_rows: List[Dict[str, object]] = []
    for row in rows:
        value = float(row["value"])
        flag = value != value  # NaN check
        out = dict(row)
        out["qc_flag"] = flag
        out_rows.append(out)
    return out_rows

