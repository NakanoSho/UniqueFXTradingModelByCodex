import unittest

from data_pipeline.ingest import rates


class TestRatesPipelineCompat(unittest.TestCase):
    def test_module_import(self):
        self.assertTrue(hasattr(rates, "ingest_rates"))


if __name__ == "__main__":
    unittest.main()
