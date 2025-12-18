import datetime as dt
import unittest

from data_pipeline.qc import spot


class TestQCSpot(unittest.TestCase):
    def test_qc_spread_stress(self):
        rows = []
        start = dt.datetime(2025, 1, 1)
        for i in range(65):
            ts = (start + dt.timedelta(days=i)).strftime("%Y-%m-%dT00:00:00Z")
            rows.append(
                {
                    "ts": ts,
                    "pair": "EURUSD",
                    "mid": 1.0 + i * 0.001,
                    "bid": 0.999 + i * 0.001,
                    "ask": 1.001 + i * 0.001,
                }
            )
        out = spot.qc_spot_rows(rows, max_gap_seconds=60 * 60 * 24)
        self.assertEqual(len(out), 65)
        # After 60 rows, spread_stress should be computed
        self.assertTrue(out[-1]["spread_stress"] >= 0.9)
        self.assertIn("gap_flag", out[-1])
        self.assertIn("time_gap_flag", out[-1])


if __name__ == "__main__":
    unittest.main()
