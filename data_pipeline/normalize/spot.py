"""Normalize spot rows to canonical schema."""

from __future__ import annotations

from typing import Dict, Iterable, List


def _to_float(value: str) -> float:
    return float(value)


def normalize_row(row: Dict[str, str]) -> Dict[str, object]:
    out = {
        "ts": row["ts"],
        "pair": row["pair"].upper().replace("/", ""),
        "mid": _to_float(row["mid"]),
        "bid": _to_float(row["bid"]),
        "ask": _to_float(row["ask"]),
        "open": _to_float(row["open"]) if row.get("open") else None,
        "high": _to_float(row["high"]) if row.get("high") else None,
        "low": _to_float(row["low"]) if row.get("low") else None,
        "close": _to_float(row["close"]) if row.get("close") else None,
    }
    return out


def normalize_rows(rows: Iterable[Dict[str, str]]) -> List[Dict[str, object]]:
    return [normalize_row(r) for r in rows]
