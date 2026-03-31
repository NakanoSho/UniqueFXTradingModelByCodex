"""Scoring utilities per v1.0 design (trend/carry/value/satellite)."""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Sequence, Tuple


def ewma_var(prev_var: float, r: float, lam: float) -> float:
    return lam * prev_var + (1.0 - lam) * (r * r)


def zscore_latest(values: Sequence[float], window: int) -> float:
    if window <= 1:
        return 0.0
    if len(values) < window:
        return 0.0
    window_vals = values[-window:]
    mean = sum(window_vals) / window
    var = sum((x - mean) ** 2 for x in window_vals) / window
    if var <= 0.0:
        return 0.0
    std = math.sqrt(var)
    return (window_vals[-1] - mean) / std


def winsor(z: float, limit: float = 3.0) -> float:
    return min(limit, max(-limit, z))


def clip01(x: float) -> float:
    return math.tanh(x / 2.0)


def score_from_raw(raw: float) -> float:
    return clip01(winsor(raw, 3.0))


def sign(x: float) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def trend_raw(
    prices: Sequence[float],
    sigma20: float,
    horizons: Sequence[int] = (20, 60, 120),
    weights: Sequence[float] = (0.5, 0.3, 0.2),
) -> float:
    if sigma20 <= 0.0:
        return 0.0
    if len(horizons) != len(weights):
        raise ValueError("horizons and weights must be same length")
    raw = 0.0
    for h, w in zip(horizons, weights):
        if len(prices) <= h:
            return 0.0
        log_ratio = math.log(prices[-1] / prices[-1 - h])
        t_stat = log_ratio / (sigma20 * math.sqrt(h))
        raw += w * t_stat
    return raw


def trend_entry_ok(rawtrend: float, threshold: float = 0.5) -> bool:
    return abs(rawtrend) >= threshold


def carry_ann(forward_1m: float, spot: float, days: int = 30) -> float:
    if spot <= 0.0 or forward_1m <= 0.0:
        return 0.0
    return math.log(forward_1m / spot) * (365.0 / days)


def cross_sectional_z(values_by_pair: Dict[str, float]) -> Dict[str, float]:
    if not values_by_pair:
        return {}
    vals = list(values_by_pair.values())
    mean = sum(vals) / len(vals)
    var = sum((x - mean) ** 2 for x in vals) / len(vals)
    if var <= 0.0:
        return {k: 0.0 for k in values_by_pair}
    std = math.sqrt(var)
    return {k: (v - mean) / std for k, v in values_by_pair.items()}


def carry_raw(carry_ann_val: float, cs_z: float, ts_z: float) -> float:
    return 0.6 * cs_z + 0.4 * ts_z


def carry_vol_scale(fxvol20: float) -> float:
    if fxvol20 <= 10.0:
        return 1.0
    scale = 1.0 - max(0.0, fxvol20 - 10.0) / 4.0
    return max(0.0, min(1.0, scale))


def apply_vol_scale(raw: float, fxvol20: float) -> float:
    return carry_vol_scale(fxvol20) * raw


def value_raw(prices: Sequence[float], window: int = 756) -> Tuple[float, float]:
    if len(prices) < window:
        return 0.0, 0.0
    logs = [math.log(p) for p in prices[-window:]]
    mean = sum(logs) / window
    var = sum((x - mean) ** 2 for x in logs) / window
    if var <= 0.0:
        return 0.0, 0.0
    std = math.sqrt(var)
    z_val = (math.log(prices[-1]) - mean) / std
    raw = -z_val
    return raw, z_val


def value_entry_ok(z_val: float, threshold: float = 0.7) -> bool:
    return abs(z_val) >= threshold


def value_strong_trend_stop(t60: float, threshold: float = 1.0) -> bool:
    return abs(t60) > threshold


def donchian_mid(close_series: Sequence[float], lookback: int = 20) -> float:
    if len(close_series) < lookback:
        return 0.0
    window = close_series[-lookback:]
    high = max(window)
    low = min(window)
    return (high + low) / 2.0


def atr(highs: Sequence[float], lows: Sequence[float], closes: Sequence[float], lookback: int = 20) -> float:
    if len(highs) < lookback + 1 or len(lows) < lookback + 1 or len(closes) < lookback + 1:
        return 0.0
    trs: List[float] = []
    for i in range(-lookback, 0):
        high = highs[i]
        low = lows[i]
        prev_close = closes[i - 1]
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)
    return sum(trs) / lookback


def breakout_raw(close: float, mid: float, atr_val: float) -> float:
    if atr_val <= 0.0:
        return 0.0
    return (close - mid) / atr_val


def satellite_raw(raw_break: float, z_vr: float) -> float:
    return 0.7 * raw_break + 0.3 * z_vr * sign(raw_break)


def enforce_trend_alignment(raw_sat: float, raw_trend: float) -> float:
    if sign(raw_sat) == 0 or sign(raw_trend) == 0:
        return 0.0
    if sign(raw_sat) != sign(raw_trend):
        return 0.0
    return raw_sat


def satellite_entry_ok(raw_sat: float, threshold: float = 1.0) -> bool:
    return abs(raw_sat) >= threshold


def satellite_exit(raw_sat: float, threshold: float = 0.3) -> bool:
    return abs(raw_sat) < threshold

