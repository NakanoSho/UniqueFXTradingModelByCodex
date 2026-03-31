"""Normalize macro rows to canonical schema."""

from __future__ import annotations

from typing import Dict, Iterable, List


def _to_float(value: str) -> float:
    return float(value)


def normalize_row(row: Dict[str, str]) -> Dict[str, object]:
    return {
        "ts": row["ts"],
        "series_id": row["series_id"],
        "value": _to_float(row["value"]),
    }


def normalize_rows(rows: Iterable[Dict[str, str]]) -> List[Dict[str, object]]:
    return [normalize_row(r) for r in rows]

