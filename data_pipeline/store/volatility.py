"""Backward-compatible wrapper for vol metrics storage."""

from __future__ import annotations

from data_pipeline.store.vol_metrics import init_db, insert_rows

__all__ = ["init_db", "insert_rows"]
