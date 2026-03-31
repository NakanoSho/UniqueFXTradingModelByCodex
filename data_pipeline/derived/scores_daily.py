"""Compute daily scores for core sleeves."""

from __future__ import annotations

import json
import math
from typing import Dict, Iterable, List, Tuple

from trading.config import Config
from trading.risk import gates
from trading.signals import scoring


def _pair_series(bars: Iterable[Dict[str, object]]) -> Dict[str, List[Tuple[str, float]]]:
    by_pair: Dict[str, List[Tuple[str, float]]] = {}
    for row in bars:
        pair = str(row["pair"])
        by_pair.setdefault(pair, []).append((str(row["date"]), float(row["daily_close_mid"])))
    for pair, series in by_pair.items():
        series.sort(key=lambda x: x[0])
    return by_pair


def _returns(prices: List[float]) -> List[float]:
    rets: List[float] = []
    prev = None
    for p in prices:
        if prev is not None:
            if prev > 0.0 and p > 0.0:
                rets.append(math.log(p / prev))
            else:
                rets.append(0.0)
        prev = p
    return rets


def _ewma_sigma(returns: List[float], lam: float = 0.94) -> float:
    var = 0.0
    for r in returns:
        var = scoring.ewma_var(var, r, lam)
    return math.sqrt(var) if var > 0.0 else 0.0


def _latest_before(date: str, series: List[Tuple[str, float]]) -> List[float]:
    return [v for d, v in series if d <= date]


def scores_daily(
    bars: Iterable[Dict[str, object]],
    forward_rows: Iterable[Dict[str, object]],
    regime_row: Dict[str, object],
    config: Config,
    only_date: str | None = None,
    exp_cost_bps: Dict[Tuple[str, str], float] | None = None,
) -> List[Dict[str, object]]:
    by_pair = _pair_series(bars)
    forward_series: Dict[str, List[Tuple[str, float]]] = {}
    forward_latest: Dict[str, float] = {}
    for row in forward_rows:
        date = str(row["date"])
        pair = str(row["pair"])
        carry = scoring.carry_ann(float(row["fwd_1m_mid"]), float(row["spot_mid"]))
        forward_series.setdefault(pair, []).append((date, carry))
    for pair, series in forward_series.items():
        series.sort(key=lambda x: x[0])
        if only_date is not None:
            for d, carry in series:
                if d == only_date:
                    forward_latest[pair] = carry

    fxvol20 = float(regime_row.get("fxvol20", 0.0))
    voljump = float(regime_row.get("voljump", 0.0))
    spread_stress = float(regime_row.get("spread_stress", 0.0))
    risk_off = gates.risk_off_flag(fxvol20, voljump, spread_stress, config.risk_flags)

    rows: List[Dict[str, object]] = []
    for pair, series in by_pair.items():
        if only_date is not None:
            series = [x for x in series if x[0] <= only_date]
        if not series:
            continue
        dates = [d for d, _ in series]
        date = dates[-1]
        prices = [p for _, p in series]
        returns = _returns(prices)
        sigma20 = _ewma_sigma(returns)

        # Trend
        raw_trend = scoring.trend_raw(prices, sigma20)
        gates_applied = []
        if not scoring.trend_entry_ok(raw_trend, config.gates.trend_raw_min):
            raw_trend = 0.0
            gates_applied.append("trend_entry_off")
        raw_adj = raw_trend
        if exp_cost_bps is not None:
            raw_adj = raw_trend - config.cost.gamma_core * exp_cost_bps.get((pair, "trend"), 0.0)
        trend_score = scoring.score_from_raw(raw_adj)
        rows.append(
            {
                "date": date,
                "pair": pair,
                "sleeve": "trend",
                "raw_score": raw_trend,
                "score": trend_score,
                "gates_applied": json.dumps(gates_applied),
            }
        )

        # Carry
        gates_applied = []
        carry_raw = 0.0
        if pair in forward_latest:
            cs_z = scoring.cross_sectional_z(forward_latest).get(pair, 0.0)
            ts_vals = [v for d, v in forward_series.get(pair, []) if d <= date]
            ts_z = scoring.zscore_latest(ts_vals, 252)
            carry_raw = scoring.carry_raw(forward_latest[pair], cs_z, ts_z)
            carry_raw = scoring.apply_vol_scale(carry_raw, fxvol20)
        if risk_off:
            carry_raw = 0.0
            gates_applied.append("carry_risk_off")
        if abs(carry_raw) < config.gates.carry_raw_min:
            carry_raw = 0.0
            gates_applied.append("carry_entry_off")
        raw_adj = carry_raw
        if exp_cost_bps is not None:
            raw_adj = carry_raw - config.cost.gamma_core * exp_cost_bps.get((pair, "carry"), 0.0)
        carry_score = scoring.score_from_raw(raw_adj)
        rows.append(
            {
                "date": date,
                "pair": pair,
                "sleeve": "carry",
                "raw_score": carry_raw,
                "score": carry_score,
                "gates_applied": json.dumps(gates_applied),
            }
        )

        # Value
        gates_applied = []
        raw_value, z_val = scoring.value_raw(prices, window=756)
        t60 = scoring.trend_raw(prices, sigma20, horizons=(60,), weights=(1.0,))
        if not scoring.value_entry_ok(z_val, config.gates.value_z_min):
            raw_value = 0.0
            gates_applied.append("value_entry_off")
        if gates.value_gate(t60, fxvol20, config.gates) == 0.0:
            raw_value = 0.0
            gates_applied.append("value_gate_off")
        raw_adj = raw_value
        if exp_cost_bps is not None:
            raw_adj = raw_value - config.cost.gamma_core * exp_cost_bps.get((pair, "value"), 0.0)
        value_score = scoring.score_from_raw(raw_adj)
        rows.append(
            {
                "date": date,
                "pair": pair,
                "sleeve": "value",
                "raw_score": raw_value,
                "score": value_score,
                "gates_applied": json.dumps(gates_applied),
            }
        )
    return rows
