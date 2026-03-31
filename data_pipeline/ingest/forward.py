"""Forward data ingestion from CSV to raw rows."""

from __future__ import annotations

import csv
from typing import Dict, Iterable, List


REQUIRED_FIELDS = ["ts", "pair", "fwd_1m_mid", "spot_mid"]


def read_forward_csv(path: str) -> List[Dict[str, str]]:
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def validate_fields(rows: Iterable[Dict[str, str]]) -> None:
    for row in rows:
        for field in REQUIRED_FIELDS:
            if field not in row or row[field] == "":
                raise ValueError(f"missing required field: {field}")


def ingest_forward(path: str) -> List[Dict[str, str]]:
    rows = read_forward_csv(path)
    validate_fields(rows)
    return rows
