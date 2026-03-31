import unittest

from data_pipeline.derived.bars_daily import ticks_to_daily_bars


class TestBarsDaily(unittest.TestCase):
    def test_daily_close_and_spread(self):
        ticks = [
            {"ts": "2025-01-01T23:58:00Z", "pair": "EURUSD", "mid": 1.0, "bid": 0.99, "ask": 1.01, "spread_bps": 1.0},
            {"ts": "2025-01-01T23:59:00Z", "pair": "EURUSD", "mid": 1.1, "bid": 1.09, "ask": 1.11, "spread_bps": 2.0},
            {"ts": "2025-01-01T23:59:30Z", "pair": "EURUSD", "mid": 1.2, "bid": 1.19, "ask": 1.21, "spread_bps": 3.0},
        ]
        bars = ticks_to_daily_bars(ticks, close_time_utc="23:59:00", only_date="2025-01-01")
        self.assertEqual(len(bars), 1)
        self.assertAlmostEqual(bars[0]["daily_close_mid"], 1.1)
        self.assertEqual(bars[0]["tick_count"], 3)
        self.assertFalse(bars[0]["missing_close"])


if __name__ == "__main__":
    unittest.main()
