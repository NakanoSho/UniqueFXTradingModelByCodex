"""Store forward rows into SQLite."""

from __future__ import annotations

import sqlite3
from typing import Dict, Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS forward_data (
    ts TEXT NOT NULL,
    pair TEXT NOT NULL,
    fwd_1m_mid REAL NOT NULL,
    spot_mid REAL NOT NULL,
    ln_fwd_spot REAL,
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
                INSERT INTO forward_data
                (ts, pair, fwd_1m_mid, spot_mid, ln_fwd_spot, qc_flag, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["ts"],
                    row["pair"],
                    row["fwd_1m_mid"],
                    row["spot_mid"],
                    row.get("ln_fwd_spot"),
                    1 if row.get("qc_flag") else 0,
                    source,
                ),
            )
            count += 1
        conn.commit()
        return count
    finally:
        conn.close()
