"""Execution cost estimation and TCA-based throttles per v1.0 design."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


TIER_A = {
    "EURUSD",
    "USDJPY",
    "GBPUSD",
    "AUDUSD",
    "USDCAD",
    "USDCHF",
}


@dataclass(frozen=True)
class CostParams:
    alpha_spr: float = 1.2
    alpha_imp: float = 1.0
    buffer_bps: float = 0.1
    core_max_bps: float = 2.0
    sat_max_bps: float = 3.0
    gamma_core: float = 0.15
    gamma_sat: float = 0.20


def cost_params_from_config(config) -> CostParams:
    return CostParams(
        alpha_spr=1.2,
        alpha_imp=1.0,
        buffer_bps=0.1,
        core_max_bps=config.cost.core_threshold_bps,
        sat_max_bps=config.cost.sat_threshold_bps,
        gamma_core=config.cost.gamma_core,
        gamma_sat=config.cost.gamma_sat,
    )


@dataclass(frozen=True)
class LiquidityTierParams:
    k_tier_a: float = 50.0
    k_tier_b: float = 20.0


def spread_bps(bid: float, ask: float, mid: float) -> float:
    if mid <= 0.0:
        return 0.0
    return (ask - bid) / mid * 1e4


def liquidity_tier(pair: str) -> str:
    return "A" if pair in TIER_A else "B"


def q_ref(nav: float, tier: str, tier_params: LiquidityTierParams) -> float:
    k = tier_params.k_tier_a if tier == "A" else tier_params.k_tier_b
    return k * nav


def participation_rate(delta_w: float, nav: float, qref: float) -> float:
    if qref <= 0.0:
        return 0.0
    return abs(delta_w) * nav / qref


def impact_bps(exec_vol_bps: float, rho: float, alpha_imp: float) -> float:
    return alpha_imp * exec_vol_bps * (rho ** 0.5)


def expected_cost_bps(spread: float, impact: float, alpha_spr: float, buffer_bps: float) -> float:
    return 0.5 * alpha_spr * spread + impact + buffer_bps


def estimate_expected_cost_bps(
    bid: float,
    ask: float,
    mid: float,
    exec_vol_bps: float,
    delta_w: float,
    nav: float,
    pair: str,
    cost_params: CostParams,
    tier_params: LiquidityTierParams,
) -> float:
    spr = spread_bps(bid, ask, mid)
    tier = liquidity_tier(pair)
    qref = q_ref(nav, tier, tier_params)
    rho = participation_rate(delta_w, nav, qref)
    imp = impact_bps(exec_vol_bps, rho, cost_params.alpha_imp)
    return expected_cost_bps(spr, imp, cost_params.alpha_spr, cost_params.buffer_bps)


def trade_allowed(exp_cost_bps: float, is_satellite: bool, cost_params: CostParams) -> bool:
    limit = cost_params.sat_max_bps if is_satellite else cost_params.core_max_bps
    return exp_cost_bps <= limit


def adjust_raw_score_for_cost(raw_score: float, exp_cost_bps: float, gamma: float) -> float:
    return raw_score - gamma * exp_cost_bps


def tca_throttle(
    real_cost_avg: float,
    exp_cost_avg: float,
    smoothing: float,
) -> Tuple[float, bool]:
    if exp_cost_avg <= 0.0:
        return smoothing, True
    if real_cost_avg > 1.2 * exp_cost_avg:
        return smoothing * 0.8, False
    return smoothing, True
