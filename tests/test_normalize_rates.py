import unittest

from data_pipeline.normalize import rates


class TestNormalizeRates(unittest.TestCase):
    def test_normalize(self):
        row = {"ts": "2025-01-01", "ccy": "usd", "ois_1m": "0.05"}
        out = rates.normalize_row(row)
        self.assertEqual(out["ccy"], "USD")
        self.assertAlmostEqual(out["ois_1m"], 0.05)


if __name__ == "__main__":
    unittest.main()
