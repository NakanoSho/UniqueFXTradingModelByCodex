"""Spot data ingestion from CSV to raw rows."""

from __future__ import annotations

import csv
from typing import Dict, Iterable, List


REQUIRED_FIELDS = ["ts", "pair", "mid", "bid", "ask"]
OPTIONAL_FIELDS = ["open", "high", "low", "close"]


def read_spot_csv(path: str) -> List[Dict[str, str]]:
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            rows.append(row)
        return rows


def validate_fields(rows: Iterable[Dict[str, str]]) -> None:
    for row in rows:
        for field in REQUIRED_FIELDS:
            if field not in row or row[field] == "":
                raise ValueError(f"missing required field: {field}")


def ingest_spot(path: str) -> List[Dict[str, str]]:
    rows = read_spot_csv(path)
    validate_fields(rows)
    return rows

