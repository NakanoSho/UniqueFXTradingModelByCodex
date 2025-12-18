import csv
import tempfile
import unittest

from data_pipeline.ingest import forward


class TestIngestForward(unittest.TestCase):
    def test_ingest_valid(self):
        with tempfile.NamedTemporaryFile("w", delete=False, newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["ts", "pair", "fwd_1m_mid", "spot_mid"])
            writer.writeheader()
            writer.writerow({"ts": "2025-01-01", "pair": "EURUSD", "fwd_1m_mid": "1.11", "spot_mid": "1.10"})
            path = f.name
        rows = forward.ingest_forward(path)
        self.assertEqual(len(rows), 1)

    def test_ingest_missing(self):
        with tempfile.NamedTemporaryFile("w", delete=False, newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["ts", "pair", "fwd_1m_mid"])
            writer.writeheader()
            writer.writerow({"ts": "2025-01-01", "pair": "EURUSD", "fwd_1m_mid": "1.11"})
            path = f.name
        with self.assertRaises(ValueError):
            forward.ingest_forward(path)


if __name__ == "__main__":
    unittest.main()
