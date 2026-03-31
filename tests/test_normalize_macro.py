import unittest

from data_pipeline.normalize import macro


class TestNormalizeMacro(unittest.TestCase):
    def test_normalize(self):
        row = {"ts": "2025-01-01", "series_id": "CPI", "value": "3.2"}
        out = macro.normalize_row(row)
        self.assertEqual(out["series_id"], "CPI")
        self.assertAlmostEqual(out["value"], 3.2)


if __name__ == "__main__":
    unittest.main()
