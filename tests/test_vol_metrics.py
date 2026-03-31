import unittest

from data_pipeline.features import volatility


class TestVolMetricsCompat(unittest.TestCase):
    def test_module_import(self):
        self.assertTrue(hasattr(volatility, "compute_fxvol20"))


if __name__ == "__main__":
    unittest.main()
