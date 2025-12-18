"""Spot tick ingestion (CSV or Parquet) to raw rows."""

from __future__ import annotations

import csv
from typing import Dict, Iterable, List


REQUIRED_FIELDS = ["timestamp", "bid", "ask"]
PAIR_FIELDS = ["symbol", "pair"]
OPTIONAL_FIELDS = ["broker"]


def read_spot_csv(path: str) -> List[Dict[str, str]]:
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def read_spot_parquet(path: str) -> List[Dict[str, str]]:
    try:
        import pyarrow.parquet as pq  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on optional deps
        raise RuntimeError("Parquet read requires pyarrow installed") from exc
    table = pq.read_table(path)
    rows: List[Dict[str, str]] = []
    for row in table.to_pylist():
        rows.append({k: "" if v is None else str(v) for k, v in row.items()})
    return rows


def validate_fields(rows: Iterable[Dict[str, str]]) -> None:
    for row in rows:
        for field in REQUIRED_FIELDS:
            if field not in row or row[field] == "":
                raise ValueError(f"missing required field: {field}")
        if not any((f in row and row[f] != "") for f in PAIR_FIELDS):
            raise ValueError("missing required field: symbol or pair")


def ingest_spot(path: str) -> List[Dict[str, str]]:
    if path.endswith(".parquet"):
        rows = read_spot_parquet(path)
    else:
        rows = read_spot_csv(path)
    validate_fields(rows)
    return rows
