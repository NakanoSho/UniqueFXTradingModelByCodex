"""Backward-compatible wrapper for vol metrics storage."""

from __future__ import annotations

from typing import Dict, Iterable

from data_pipeline.store.vol import init_db, insert_row


def insert_rows(path: str, rows: Iterable[Dict[str, object]], source: str) -> int:
    count = 0
    for row in rows:
        insert_row(path, row, source)
        count += 1
    return count

__all__ = ["init_db", "insert_rows"]
