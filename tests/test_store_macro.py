import os
import sqlite3
import tempfile
import unittest

from data_pipeline.store import macro


class TestStoreMacro(unittest.TestCase):
    def test_store(self):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        path = tmp.name
        rows = [{"ts": "2025-01-01", "series_id": "CPI", "value": 3.2, "qc_flag": False}]
        macro.init_db(path)
        inserted = macro.insert_rows(path, rows, source="test")
        self.assertEqual(inserted, 1)
        conn = sqlite3.connect(path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM macro_data")
            self.assertEqual(cur.fetchone()[0], 1)
        finally:
            conn.close()
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
