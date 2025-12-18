import unittest

from data_pipeline.normalize import spot


class TestNormalizeSpot(unittest.TestCase):
    def test_normalize_row(self):
        row = {
            "timestamp": "2025-01-01T00:00:00Z",
            "symbol": "eur/usd",
            "bid": "1.09",
            "ask": "1.11",
            "broker": "demo",
        }
        out = spot.normalize_row(row)
        self.assertEqual(out["pair"], "EURUSD")
        self.assertAlmostEqual(out["mid"], 1.1)
        self.assertAlmostEqual(out["spread_bps"], (1.11 - 1.09) / 1.1 * 1e4)


if __name__ == "__main__":
    unittest.main()
