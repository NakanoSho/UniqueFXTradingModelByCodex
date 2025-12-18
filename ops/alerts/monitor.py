"""Daily monitoring alerts and report generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class AlertThresholds:
    daily_loss: float = -0.02
    weekly_loss: float = -0.035
    monthly_loss: float = -0.06
    dd_soft: float = 0.12
    dd_hard: float = 0.15
    spread_stress: float = 1.5
    cost_ratio: float = 1.2


def evaluate_alerts(metrics: Dict[str, float], t: AlertThresholds) -> List[str]:
    alerts: List[str] = []
    if metrics.get("pnl_daily", 0.0) <= t.daily_loss:
        alerts.append("daily_loss_limit")
    if metrics.get("pnl_weekly", 0.0) <= t.weekly_loss:
        alerts.append("weekly_loss_limit")
    if metrics.get("pnl_monthly", 0.0) <= t.monthly_loss:
        alerts.append("monthly_loss_limit")
    if metrics.get("dd", 0.0) >= t.dd_hard:
        alerts.append("dd_hard_limit")
    elif metrics.get("dd", 0.0) >= t.dd_soft:
        alerts.append("dd_soft_limit")
    if metrics.get("spread_stress", 0.0) > t.spread_stress:
        alerts.append("spread_stress")
    if metrics.get("real_to_exp_cost_ratio", 0.0) > t.cost_ratio:
        alerts.append("cost_ratio")
    return alerts


def build_report(metrics: Dict[str, float], t: AlertThresholds) -> Dict[str, object]:
    alerts = evaluate_alerts(metrics, t)
    return {
        "metrics": metrics,
        "alerts": alerts,
        "ok": len(alerts) == 0,
    }

