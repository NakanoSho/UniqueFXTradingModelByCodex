import csv
import tempfile
import unittest

from data_pipeline.ingest import macro


class TestIngestMacro(unittest.TestCase):
    def test_ingest_valid(self):
        with tempfile.NamedTemporaryFile("w", delete=False, newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["ts", "series_id", "value"])
            writer.writeheader()
            writer.writerow({"ts": "2025-01-01", "series_id": "CPI", "value": "3.2"})
            path = f.name
        rows = macro.ingest_macro(path)
        self.assertEqual(len(rows), 1)

    def test_ingest_missing(self):
        with tempfile.NamedTemporaryFile("w", delete=False, newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["ts", "series_id"])
            writer.writeheader()
            writer.writerow({"ts": "2025-01-01", "series_id": "CPI"})
            path = f.name
        with self.assertRaises(ValueError):
            macro.ingest_macro(path)


if __name__ == "__main__":
    unittest.main()
