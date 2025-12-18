import unittest

from data_pipeline.normalize import forward


class TestNormalizeForward(unittest.TestCase):
    def test_normalize(self):
        row = {"ts": "2025-01-01", "pair": "eur/usd", "fwd_1m_mid": "1.11", "spot_mid": "1.10"}
        out = forward.normalize_row(row)
        self.assertEqual(out["pair"], "EURUSD")
        self.assertAlmostEqual(out["fwd_1m_mid"], 1.11)


if __name__ == "__main__":
    unittest.main()
