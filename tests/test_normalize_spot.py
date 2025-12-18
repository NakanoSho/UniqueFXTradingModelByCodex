import unittest

from data_pipeline.normalize import spot


class TestNormalizeSpot(unittest.TestCase):
    def test_normalize_row(self):
        row = {
            "ts": "2025-01-01",
            "pair": "eur/usd",
            "mid": "1.1",
            "bid": "1.09",
            "ask": "1.11",
            "open": "1.0",
            "high": "1.2",
            "low": "0.9",
            "close": "1.05",
        }
        out = spot.normalize_row(row)
        self.assertEqual(out["pair"], "EURUSD")
        self.assertAlmostEqual(out["mid"], 1.1)
        self.assertAlmostEqual(out["open"], 1.0)


if __name__ == "__main__":
    unittest.main()
