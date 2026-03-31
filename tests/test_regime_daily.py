import datetime as dt
import unittest

from data_pipeline.derived.regime_daily import regime_daily


class TestRegimeDaily(unittest.TestCase):
    def test_regime_output(self):
        bars = []
        start = dt.date(2025, 1, 1)
        for i in range(61):
            date = (start + dt.timedelta(days=i)).isoformat()
            bars.append(
                {
                    "date": date,
                    "pair": "EURUSD",
                    "daily_close_mid": 1.0 + i * 0.001,
                    "spread_bps_median": 1.0,
                }
            )
        rows = regime_daily(bars, only_date="2025-03-02")
        self.assertEqual(len(rows), 1)
        self.assertIn("fxvol20", rows[0])


if __name__ == "__main__":
    unittest.main()
