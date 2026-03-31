import unittest

from data_pipeline.qc import rates


class TestQCRates(unittest.TestCase):
    def test_rate_flag(self):
        rows = [{"ts": "2025-01-01", "ccy": "USD", "ois_1m": 0.5}]
        out = rates.qc_rates_rows(rows)
        self.assertTrue(out[0]["rate_flag"])


if __name__ == "__main__":
    unittest.main()
