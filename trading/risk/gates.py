"""Risk gates and mode logic per v1.0 design."""

from __future__ import annotations

from trading.config import GateThresholds, RiskFlagsThresholds


def risk_off_flag(fxvol20: float, voljump: float, spreadstress: float, t: RiskFlagsThresholds) -> bool:
    return fxvol20 > t.fxvol20_off or voljump > t.voljump_off or spreadstress > t.spreadstress_off


def risk_on_flag(fxvol20: float, voljump: float, spreadstress: float, t: RiskFlagsThresholds) -> bool:
    return fxvol20 < t.fxvol20_on and voljump < t.voljump_on and spreadstress < t.spreadstress_on


def trend_gate(
    liquidity_ok: bool,
    spreadstress: float,
    data_ok: bool,
    exec_ok: bool,
    t: GateThresholds,
) -> bool:
    return liquidity_ok and data_ok and exec_ok and spreadstress <= t.trend_spreadstress_max


def carry_gate(risk_off: bool) -> float:
    return 0.0 if risk_off else 1.0


def carry_crash_stop(carry_pnl_5d: float, t: GateThresholds) -> bool:
    return carry_pnl_5d <= t.carry_crash_pnl_5d


def value_gate(z_trend_60: float, fxvol20: float, t: GateThresholds) -> float:
    if abs(z_trend_60) > t.value_trend_stop:
        return 0.0
    if fxvol20 > t.value_vol_stop:
        return 0.0
    if fxvol20 > t.value_vol_half:
        return 0.5
    return 1.0


def satellite_m1_gate(
    risk_on: bool, dd: float, month_pnl: float, trend_carry_align: bool, t: GateThresholds
) -> bool:
    return risk_on and dd <= t.sat_m1_dd_max and month_pnl > t.sat_m1_month_pnl_min and trend_carry_align


def satellite_m2_gate(
    m1_ok: bool, dd: float, spreadstress: float, slippage_ratio: float, t: GateThresholds
) -> bool:
    return (
        m1_ok
        and dd <= t.sat_m2_dd_max
        and spreadstress < t.sat_m2_spreadstress_max
        and slippage_ratio <= t.sat_m2_slip_ratio_max
    )


def satellite_stop(risk_off: bool, daily_pnl: float, weekly_pnl: float) -> bool:
    return risk_off or daily_pnl <= -0.02 or weekly_pnl <= -0.035
