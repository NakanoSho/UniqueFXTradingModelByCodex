"""Backward-compatible wrapper for expected cost storage."""

from __future__ import annotations

from data_pipeline.store.cost import init_db, insert_rows

__all__ = ["init_db", "insert_rows"]
