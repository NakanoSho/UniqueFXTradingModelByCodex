import datetime as dt
import os
import unittest

from data_pipeline.derived.scores_daily import scores_daily
from trading.config import load_config


class TestScoresDaily(unittest.TestCase):
    def test_scores_rows(self):
        bars = []
        start = dt.date(2024, 1, 1)
        for i in range(260):
            date = (start + dt.timedelta(days=i)).isoformat()
            bars.append(
                {
                    "date": date,
                    "pair": "EURUSD",
                    "daily_close_mid": 1.0 + i * 0.0001,
                    "spread_bps_median": 1.0,
                }
            )
        forward_rows = [
            {"date": bars[-1]["date"], "pair": "EURUSD", "fwd_1m_mid": 1.01, "spot_mid": 1.0}
        ]
        regime_row = {"date": bars[-1]["date"], "fxvol20": 9.0, "voljump": 1.1, "spread_stress": 1.1}
        config = load_config(os.path.join("configs", "v1_0.yaml"))
        rows = scores_daily(bars, forward_rows, regime_row, config, only_date=bars[-1]["date"])
        sleeves = {r["sleeve"] for r in rows}
        self.assertTrue({"trend", "carry", "value"}.issubset(sleeves))


if __name__ == "__main__":
    unittest.main()
