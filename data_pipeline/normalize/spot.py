"""Normalize spot tick rows to canonical schema."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Iterable, List


def _to_float(value: str) -> float:
    return float(value)


def _parse_ts(value: str) -> str:
    ts = value.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def _pair_from_row(row: Dict[str, str]) -> str:
    raw = row.get("symbol") or row.get("pair") or ""
    return raw.upper().replace("/", "")


def normalize_row(row: Dict[str, str]) -> Dict[str, object]:
    ts_value = row.get("timestamp") or row.get("ts") or ""
    bid = _to_float(row["bid"])
    ask = _to_float(row["ask"])
    mid = _to_float(row.get("mid") or (bid + ask) / 2.0)
    spread_bps = 0.0
    if mid > 0.0:
        spread_bps = (ask - bid) / mid * 1e4
    out = {
        "ts": _parse_ts(ts_value),
        "pair": _pair_from_row(row),
        "mid": mid,
        "bid": bid,
        "ask": ask,
        "spread_bps": spread_bps,
        "broker": row.get("broker") or None,
    }
    return out


def normalize_rows(rows: Iterable[Dict[str, str]]) -> List[Dict[str, object]]:
    return [normalize_row(r) for r in rows]
