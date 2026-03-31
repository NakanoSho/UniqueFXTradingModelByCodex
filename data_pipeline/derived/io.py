"""I/O helpers for derived datasets."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def write_csv(path: str, rows: Iterable[Dict[str, object]]) -> None:
    rows_list = list(rows)
    if not rows_list:
        return
    ensure_dir(str(Path(path).parent))
    fieldnames = list(rows_list[0].keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows_list:
            writer.writerow(row)


def read_csv(path: str) -> List[Dict[str, str]]:
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def write_partitioned_csv(base_dir: str, version: str, rows: Iterable[Dict[str, object]], partition_keys: List[str]) -> None:
    rows_list = list(rows)
    if not rows_list:
        return
    buckets: Dict[str, List[Dict[str, object]]] = {}
    for row in rows_list:
        parts = [f"{key}={row[key]}" for key in partition_keys]
        rel = "/".join(parts)
        buckets.setdefault(rel, []).append(row)
    for rel, bucket_rows in buckets.items():
        path = Path(base_dir) / version / rel / "data.csv"
        write_csv(str(path), bucket_rows)
