"""Store expected cost estimates into SQLite."""

from __future__ import annotations

import sqlite3
from typing import Dict, Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS expected_costs (
    ts TEXT NOT NULL,
    pair TEXT NOT NULL,
    sleeve TEXT NOT NULL,
    exp_cost_bps REAL NOT NULL,
    trade_allowed INTEGER,
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
                INSERT INTO expected_costs (ts, pair, sleeve, exp_cost_bps, trade_allowed, source)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row["ts"],
                    row["pair"],
                    row["sleeve"],
                    row["exp_cost_bps"],
                    1 if row.get("trade_allowed") else 0,
                    source,
                ),
            )
            count += 1
        conn.commit()
        return count
    finally:
        conn.close()

