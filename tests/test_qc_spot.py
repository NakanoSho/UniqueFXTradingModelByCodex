import unittest

from data_pipeline.qc import spot


class TestQCSpot(unittest.TestCase):
    def test_qc_spread_stress(self):
        rows = []
        for i in range(65):
            rows.append({
                "ts": f"2025-01-{i+1:02d}",
                "pair": "EURUSD",
                "mid": 1.0 + i * 0.001,
                "bid": 0.999 + i * 0.001,
                "ask": 1.001 + i * 0.001,
            })
        out = spot.qc_spot_rows(rows)
        self.assertEqual(len(out), 65)
        # After 60 rows, spread_stress should be computed
        self.assertTrue(out[-1]["spread_stress"] >= 0.9)
        self.assertIn("gap_flag", out[-1])


if __name__ == "__main__":
    unittest.main()
