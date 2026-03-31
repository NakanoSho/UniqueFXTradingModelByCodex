"""Compute daily regime metrics from bars."""

from __future__ import annotations

import math
import statistics
from typing import Dict, Iterable, List, Tuple


def _log_return(curr: float, prev: float) -> float:
    if curr <= 0.0 or prev <= 0.0:
        return 0.0
    return math.log(curr / prev)


def _realized_vol(returns: List[float]) -> float:
    if not returns:
        return 0.0
    mean = sum(returns) / len(returns)
    var = sum((x - mean) ** 2 for x in returns) / len(returns)
    return math.sqrt(var) * math.sqrt(252)


def _pair_series(bars: Iterable[Dict[str, object]]) -> Dict[str, List[Tuple[str, float, float]]]:
    by_pair: Dict[str, List[Tuple[str, float, float]]] = {}
    for row in bars:
        pair = str(row["pair"])
        by_pair.setdefault(pair, []).append(
            (str(row["date"]), float(row["daily_close_mid"]), float(row["spread_bps_median"]))
        )
    for pair, series in by_pair.items():
        series.sort(key=lambda x: x[0])
    return by_pair


def _compute_fxvol20(series: List[Tuple[str, float, float]]) -> float:
    returns: List[float] = []
    prev = None
    for _, mid, _ in series:
        if prev is not None:
            returns.append(_log_return(mid, prev))
        prev = mid
    if len(returns) < 20:
        return 0.0
    return _realized_vol(returns[-20:])


def _compute_voljump(series: List[Tuple[str, float, float]]) -> float:
    returns: List[float] = []
    prev = None
    for _, mid, _ in series:
        if prev is not None:
            returns.append(_log_return(mid, prev))
        prev = mid
    if len(returns) < 60:
        return 0.0
    vol5 = _realized_vol(returns[-5:])
    vol60 = _realized_vol(returns[-60:])
    if vol60 <= 0.0:
        return 0.0
    return vol5 / vol60


def _compute_spread_stress(series: List[Tuple[str, float, float]]) -> float:
    spreads = [s for _, _, s in series]
    if len(spreads) < 60:
        return 0.0
    med = statistics.median(spreads[-60:])
    if med <= 0.0:
        return 0.0
    return spreads[-1] / med


def regime_daily(bars: Iterable[Dict[str, object]], only_date: str | None = None) -> List[Dict[str, object]]:
    by_pair = _pair_series(bars)
    all_dates = sorted({date for series in by_pair.values() for date, _, _ in series})
    output: List[Dict[str, object]] = []
    for date in all_dates:
        if only_date is not None and date != only_date:
            continue
        fxvols: List[float] = []
        voljumps: List[float] = []
        spread_stresses: List[float] = []
        for series in by_pair.values():
            series_upto = [x for x in series if x[0] <= date]
            if not series_upto:
                continue
            fx = _compute_fxvol20(series_upto)
            vj = _compute_voljump(series_upto)
            ss = _compute_spread_stress(series_upto)
            if fx > 0.0:
                fxvols.append(fx)
            if vj > 0.0:
                voljumps.append(vj)
            if ss > 0.0:
                spread_stresses.append(ss)
        output.append(
            {
                "date": date,
                "fxvol20": statistics.median(fxvols) if fxvols else 0.0,
                "voljump": statistics.median(voljumps) if voljumps else 0.0,
                "spread_stress": statistics.median(spread_stresses) if spread_stresses else 0.0,
            }
        )
    return output
