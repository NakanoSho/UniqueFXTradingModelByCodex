"""Risk gates and mode logic per v1.0 design."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskFlagsThresholds:
    fxvol20_off: float = 12.0
    voljump_off: float = 1.5
    spreadstress_off: float = 1.5
    fxvol20_on: float = 10.0
    voljump_on: float = 1.2
    spreadstress_on: float = 1.2


@dataclass(frozen=True)
class SatelliteGateThresholds:
    dd_m1: float = 0.04
    dd_m2: float = 0.02
    month_pnl_min: float = -0.02
    spreadstress_m2: float = 1.1
    slippage_ratio_m2: float = 1.2


def risk_off_flag(fxvol20: float, voljump: float, spreadstress: float, t: RiskFlagsThresholds) -> bool:
    return fxvol20 > t.fxvol20_off or voljump > t.voljump_off or spreadstress > t.spreadstress_off


def risk_on_flag(fxvol20: float, voljump: float, spreadstress: float, t: RiskFlagsThresholds) -> bool:
    return fxvol20 < t.fxvol20_on and voljump < t.voljump_on and spreadstress < t.spreadstress_on


def trend_gate(liquidity_ok: bool, spreadstress: float, data_ok: bool, exec_ok: bool) -> bool:
    return liquidity_ok and data_ok and exec_ok and spreadstress <= 1.5


def carry_gate(risk_off: bool) -> float:
    return 0.0 if risk_off else 1.0


def carry_crash_stop(carry_pnl_5d: float, threshold: float = -0.025) -> bool:
    return carry_pnl_5d <= threshold


def value_gate(z_trend_60: float, fxvol20: float, vol_half: float = 12.0, vol_stop: float = 14.0) -> float:
    if abs(z_trend_60) > 1.0:
        return 0.0
    if fxvol20 > vol_stop:
        return 0.0
    if fxvol20 > vol_half:
        return 0.5
    return 1.0


def satellite_m1_gate(risk_on: bool, dd: float, month_pnl: float, trend_carry_align: bool) -> bool:
    return risk_on and dd <= 0.04 and month_pnl > -0.02 and trend_carry_align


def satellite_m2_gate(m1_ok: bool, dd: float, spreadstress: float, slippage_ratio: float) -> bool:
    return m1_ok and dd <= 0.02 and spreadstress < 1.1 and slippage_ratio <= 1.2


def satellite_stop(risk_off: bool, daily_pnl: float, weekly_pnl: float) -> bool:
    return risk_off or daily_pnl <= -0.02 or weekly_pnl <= -0.035

