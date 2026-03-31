import unittest

from data_pipeline.qc import forward


class TestQCForward(unittest.TestCase):
    def test_qc_flag(self):
        rows = [{"ts": "2025-01-01", "pair": "EURUSD", "fwd_1m_mid": 1.5, "spot_mid": 1.0}]
        out = forward.qc_forward_rows(rows)
        self.assertTrue(out[0]["forward_flag"])


if __name__ == "__main__":
    unittest.main()
