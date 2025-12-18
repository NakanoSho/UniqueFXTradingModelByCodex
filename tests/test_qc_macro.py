import unittest

from data_pipeline.qc import macro


class TestQCMacro(unittest.TestCase):
    def test_qc_flag(self):
        rows = [{"ts": "2025-01-01", "series_id": "CPI", "value": float('nan')}]
        out = macro.qc_macro_rows(rows)
        self.assertTrue(out[0]["qc_flag"])


if __name__ == "__main__":
    unittest.main()
