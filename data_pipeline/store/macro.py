"""Store macro rows into SQLite."""

from __future__ import annotations

import sqlite3
from typing import Dict, Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS macro_data (
    ts TEXT NOT NULL,
    series_id TEXT NOT NULL,
    value REAL NOT NULL,
    qc_flag INTEGER,
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


def insert_rows(path: str, rows: Iterable[Dict[str, object]], source: str) -> int:
    conn = sqlite3.connect(path)
    try:
        conn.execute(SCHEMA)
        cur = conn.cursor()
        count = 0
        for row in rows:
            cur.execute(
                """
                INSERT INTO macro_data (ts, series_id, value, qc_flag, source)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    row["ts"],
                    row["series_id"],
                    row["value"],
                    1 if row.get("qc_flag") else 0,
                    source,
                ),
            )
            count += 1
        conn.commit()
        return count
    finally:
        conn.close()

