import os
import sqlite3
import tempfile
import unittest

from data_pipeline.store import cost


class TestStoreCost(unittest.TestCase):
    def test_store(self):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        path = tmp.name
        rows = [{"ts": "2025-01-01", "pair": "EURUSD", "sleeve": "core", "exp_cost_bps": 1.0, "trade_allowed": True}]
        cost.init_db(path)
        inserted = cost.insert_rows(path, rows, source="test")
        self.assertEqual(inserted, 1)
        conn = sqlite3.connect(path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM expected_costs")
            self.assertEqual(cur.fetchone()[0], 1)
        finally:
            conn.close()
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
