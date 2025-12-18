"""Quality checks for forward data."""

from __future__ import annotations

import math
from typing import Dict, List


def qc_forward_rows(rows: List[Dict[str, object]], log_ratio_limit: float = 0.2) -> List[Dict[str, object]]:
    output: List[Dict[str, object]] = []
    for row in rows:
        fwd = float(row["fwd_1m_mid"])
        spot = float(row["spot_mid"])
        flag = False
        if fwd <= 0.0 or spot <= 0.0:
            flag = True
            log_ratio = 0.0
        else:
            log_ratio = math.log(fwd / spot)
            if abs(log_ratio) > log_ratio_limit:
                flag = True
        out = dict(row)
        out["ln_fwd_spot"] = log_ratio
        out["qc_flag"] = flag
        out["forward_flag"] = flag
        output.append(out)
    return output
