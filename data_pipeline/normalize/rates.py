"""Normalize rates rows to canonical schema."""

from __future__ import annotations

from typing import Dict, Iterable, List


def _to_float(value: str) -> float:
    return float(value)


def normalize_row(row: Dict[str, str]) -> Dict[str, object]:
    return {
        "ts": row["ts"],
        "ccy": row["ccy"].upper(),
        "ois_1m": _to_float(row["ois_1m"]),
    }


def normalize_rows(rows: Iterable[Dict[str, str]]) -> List[Dict[str, object]]:
    return [normalize_row(r) for r in rows]

