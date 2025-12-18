import csv
import tempfile
import unittest

from data_pipeline.ingest import spot


class TestIngestSpot(unittest.TestCase):
    def test_ingest_valid(self):
        with tempfile.NamedTemporaryFile("w", delete=False, newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "symbol", "bid", "ask"])
            writer.writeheader()
            writer.writerow({"timestamp": "2025-01-01T00:00:00Z", "symbol": "EURUSD", "bid": "1.09", "ask": "1.11"})
            path = f.name
        rows = spot.ingest_spot(path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["symbol"], "EURUSD")

    def test_ingest_missing_field(self):
        with tempfile.NamedTemporaryFile("w", delete=False, newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "symbol", "bid"])
            writer.writeheader()
            writer.writerow({"timestamp": "2025-01-01T00:00:00Z", "symbol": "EURUSD", "bid": "1.09"})
            path = f.name
        with self.assertRaises(ValueError):
            spot.ingest_spot(path)


if __name__ == "__main__":
    unittest.main()
