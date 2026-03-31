"""Store spot rows into SQLite."""

from __future__ import annotations

import sqlite3
from typing import Dict, Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS spot_data (
    ts TEXT NOT NULL,
    pair TEXT NOT NULL,
    mid REAL NOT NULL,
    bid REAL NOT NULL,
    ask REAL NOT NULL,
    spread_bps REAL,
    broker TEXT,
    spread REAL,
    spread_stress REAL,
    gap_flag INTEGER,
    duplicate_ts INTEGER,
    non_monotonic_ts INTEGER,
    time_gap_flag INTEGER,
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
                INSERT INTO spot_data
                (ts, pair, mid, bid, ask, spread_bps, broker, spread, spread_stress, gap_flag,
                 duplicate_ts, non_monotonic_ts, time_gap_flag, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["ts"],
                    row["pair"],
                    row["mid"],
                    row["bid"],
                    row["ask"],
                    row.get("spread_bps"),
                    row.get("broker"),
                    row.get("spread"),
                    row.get("spread_stress"),
                    1 if row.get("gap_flag") else 0,
                    1 if row.get("duplicate_ts") else 0,
                    1 if row.get("non_monotonic_ts") else 0,
                    1 if row.get("time_gap_flag") else 0,
                    source,
                ),
            )
            count += 1
        conn.commit()
        return count
    finally:
        conn.close()
