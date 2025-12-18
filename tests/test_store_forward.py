import os
import sqlite3
import tempfile
import unittest

from data_pipeline.store import forward


class TestStoreForward(unittest.TestCase):
    def test_store(self):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        path = tmp.name
        rows = [{"ts": "2025-01-01", "pair": "EURUSD", "fwd_1m_mid": 1.11, "spot_mid": 1.10, "forward_flag": False}]
        forward.init_db(path)
        inserted = forward.insert_rows(path, rows, source="test")
        self.assertEqual(inserted, 1)
        conn = sqlite3.connect(path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM forward_data")
            self.assertEqual(cur.fetchone()[0], 1)
        finally:
            conn.close()
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
