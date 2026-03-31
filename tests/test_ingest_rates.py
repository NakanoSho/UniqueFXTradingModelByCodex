import csv
import tempfile
import unittest

from data_pipeline.ingest import rates


class TestIngestRates(unittest.TestCase):
    def test_ingest_valid(self):
        with tempfile.NamedTemporaryFile("w", delete=False, newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["ts", "ccy", "ois_1m"])
            writer.writeheader()
            writer.writerow({"ts": "2025-01-01", "ccy": "USD", "ois_1m": "0.05"})
            path = f.name
        rows = rates.ingest_rates(path)
        self.assertEqual(len(rows), 1)

    def test_ingest_missing(self):
        with tempfile.NamedTemporaryFile("w", delete=False, newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["ts", "ccy"])
            writer.writeheader()
            writer.writerow({"ts": "2025-01-01", "ccy": "USD"})
            path = f.name
        with self.assertRaises(ValueError):
            rates.ingest_rates(path)


if __name__ == "__main__":
    unittest.main()
