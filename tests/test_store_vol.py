import os
import sqlite3
import tempfile
import unittest

from data_pipeline.store import vol


class TestStoreVol(unittest.TestCase):
    def test_store(self):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        path = tmp.name
        vol.init_db(path)
        vol.insert_row(path, {"ts": "2025-01-01", "fxvol20": 0.1, "voljump": 1.0, "spread_stress": 1.0}, source="test")
        conn = sqlite3.connect(path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM vol_metrics")
            self.assertEqual(cur.fetchone()[0], 1)
        finally:
            conn.close()
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
