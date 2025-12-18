"""Volatility indicators derived from spot data."""

from __future__ import annotations

import math
import sqlite3
import statistics
from typing import Dict, List, Tuple


def _log_return(curr: float, prev: float) -> float:
    if prev <= 0.0 or curr <= 0.0:
        return 0.0
    return math.log(curr / prev)


def fetch_spot_series(db_path: str) -> Dict[str, List[Tuple[str, float, float]]]:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT ts, pair, mid, spread FROM spot_data ORDER BY ts")
        rows = cur.fetchall()
    finally:
        conn.close()
    by_pair: Dict[str, List[Tuple[str, float, float]]] = {}
    for ts, pair, mid, spread in rows:
        by_pair.setdefault(pair, []).append((ts, float(mid), float(spread)))
    return by_pair


def realized_vol(returns: List[float]) -> float:
    if not returns:
        return 0.0
    mean = sum(returns) / len(returns)
    var = sum((x - mean) ** 2 for x in returns) / len(returns)
    return math.sqrt(var) * math.sqrt(252)


def compute_fxvol20(by_pair: Dict[str, List[Tuple[str, float, float]]]) -> float:
    vols: List[float] = []
    for series in by_pair.values():
        returns: List[float] = []
        prev = None
        for _, mid, _ in series:
            if prev is not None:
                returns.append(_log_return(mid, prev))
            prev = mid
        if len(returns) >= 20:
            vols.append(realized_vol(returns[-20:]))
    if not vols:
        return 0.0
    return statistics.median(vols)


def compute_voljump(by_pair: Dict[str, List[Tuple[str, float, float]]]) -> float:
    jumps: List[float] = []
    for series in by_pair.values():
        returns: List[float] = []
        prev = None
        for _, mid, _ in series:
            if prev is not None:
                returns.append(_log_return(mid, prev))
            prev = mid
        if len(returns) >= 60:
            vol5 = realized_vol(returns[-5:])
            vol60 = realized_vol(returns[-60:])
            if vol60 > 0.0:
                jumps.append(vol5 / vol60)
    if not jumps:
        return 0.0
    return statistics.median(jumps)


def compute_spread_stress(by_pair: Dict[str, List[Tuple[str, float, float]]]) -> float:
    stresses: List[float] = []
    for series in by_pair.values():
        spreads = [s for _, _, s in series]
        if len(spreads) >= 60:
            med = statistics.median(spreads[-60:])
            if med > 0.0:
                stresses.append(spreads[-1] / med)
    if not stresses:
        return 0.0
    return statistics.median(stresses)

