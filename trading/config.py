"""Configuration loader for v1.0 parameters."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class RiskFlagsThresholds:
    fxvol20_off: float
    voljump_off: float
    spreadstress_off: float
    fxvol20_on: float
    voljump_on: float
    spreadstress_on: float


@dataclass(frozen=True)
class GateThresholds:
    trend_spreadstress_max: float
    trend_raw_min: float
    carry_raw_min: float
    carry_crash_pnl_5d: float
    value_z_min: float
    value_trend_stop: float
    value_vol_half: float
    value_vol_stop: float
    sat_raw_min: float
    sat_exit_raw: float
    sat_m1_dd_max: float
    sat_m1_month_pnl_min: float
    sat_m2_dd_max: float
    sat_m2_spreadstress_max: float
    sat_m2_slip_ratio_max: float


@dataclass(frozen=True)
class DataQCConfig:
    max_gap_seconds: int


@dataclass(frozen=True)
class BarsDailyConfig:
    close_time_utc: str


@dataclass(frozen=True)
class CostConfig:
    core_threshold_bps: float
    sat_threshold_bps: float
    gamma_core: float
    gamma_sat: float


@dataclass(frozen=True)
class Config:
    version: str
    risk_flags: RiskFlagsThresholds
    gates: GateThresholds
    data_qc: DataQCConfig
    bars_daily: BarsDailyConfig
    cost: CostConfig


def _load_json_like(path: Path) -> Dict[str, Any]:
    text = path.read_text()
    return json.loads(text)


def load_config(path: str) -> Config:
    data = _load_json_like(Path(path))
    risk = data["risk_flags"]
    gates = data["gates"]
    sat = gates["satellite"]
    cfg = Config(
        version=data["version"],
        risk_flags=RiskFlagsThresholds(
            fxvol20_off=risk["fxvol20_off"],
            voljump_off=risk["voljump_off"],
            spreadstress_off=risk["spreadstress_off"],
            fxvol20_on=risk["fxvol20_on"],
            voljump_on=risk["voljump_on"],
            spreadstress_on=risk["spreadstress_on"],
        ),
        gates=GateThresholds(
            trend_spreadstress_max=gates["trend"]["spreadstress_max"],
            trend_raw_min=gates["trend"]["rawtrend_min"],
            carry_raw_min=gates["carry"]["raw_min"],
            carry_crash_pnl_5d=gates["carry"]["crash_pnl_5d"],
            value_z_min=gates["value"]["z_val_min"],
            value_trend_stop=gates["value"]["trend_stop"],
            value_vol_half=gates["value"]["vol_half"],
            value_vol_stop=gates["value"]["vol_stop"],
            sat_raw_min=sat["raw_min"],
            sat_exit_raw=sat["exit_raw"],
            sat_m1_dd_max=sat["m1"]["dd_max"],
            sat_m1_month_pnl_min=sat["m1"]["month_pnl_min"],
            sat_m2_dd_max=sat["m2"]["dd_max"],
            sat_m2_spreadstress_max=sat["m2"]["spreadstress_max"],
            sat_m2_slip_ratio_max=sat["m2"]["slip_ratio_max"],
        ),
        data_qc=DataQCConfig(
            max_gap_seconds=int(data["data"]["qc"]["max_gap_seconds"])
        ),
        bars_daily=BarsDailyConfig(
            close_time_utc=data["data"]["bars_daily"]["close_time_utc"]
        ),
        cost=CostConfig(
            core_threshold_bps=data["cost"]["core_threshold_bps"],
            sat_threshold_bps=data["cost"]["sat_threshold_bps"],
            gamma_core=data["cost"]["gamma_core"],
            gamma_sat=data["cost"]["gamma_sat"],
        ),
    )
    return cfg
