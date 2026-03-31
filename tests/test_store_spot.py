import os
import sqlite3
import tempfile
import unittest

from data_pipeline.store import spot


class TestStoreSpot(unittest.TestCase):
    def test_store_rows(self):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        path = tmp.name
        rows = [
            {
                "ts": "2025-01-01T00:00:00Z",
                "pair": "EURUSD",
                "mid": 1.1,
                "bid": 1.09,
                "ask": 1.11,
                "spread_bps": 18.18,
                "broker": "demo",
                "spread": 0.02,
                "spread_stress": 1.0,
                "gap_flag": False,
                "duplicate_ts": False,
                "non_monotonic_ts": False,
                "time_gap_flag": False,
            }
        ]
        spot.init_db(path)
        inserted = spot.insert_rows(path, rows, source="test")
        self.assertEqual(inserted, 1)
        conn = sqlite3.connect(path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM spot_data")
            count = cur.fetchone()[0]
            self.assertEqual(count, 1)
        finally:
            conn.close()
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
