import unittest

from data_pipeline.pipeline import run_expected_cost_daily


class TestExpectedCostPipelineCompat(unittest.TestCase):
    def test_main_exists(self):
        self.assertTrue(hasattr(run_expected_cost_daily, "main"))


if __name__ == "__main__":
    unittest.main()
