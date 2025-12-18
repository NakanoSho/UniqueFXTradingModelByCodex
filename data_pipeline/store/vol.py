"""Store volatility metrics into SQLite."""

from __future__ import annotations

import sqlite3
from typing import Dict


SCHEMA = """
CREATE TABLE IF NOT EXISTS vol_metrics (
    ts TEXT NOT NULL,
    fxvol20 REAL,
    voljump REAL,
    spread_stress REAL,
    source TEXT
);
"""


def init_db(path: str) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.execute(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def insert_row(path: str, row: Dict[str, object], source: str) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.execute(SCHEMA)
        conn.execute(
            """
            INSERT INTO vol_metrics (ts, fxvol20, voljump, spread_stress, source)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                row["ts"],
                row.get("fxvol20"),
                row.get("voljump"),
                row.get("spread_stress"),
                source,
            ),
        )
        conn.commit()
    finally:
        conn.close()

