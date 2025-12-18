import unittest

from data_pipeline.ingest import forward


class TestForwardPipelineCompat(unittest.TestCase):
    def test_module_import(self):
        self.assertTrue(hasattr(forward, "ingest_forward"))


if __name__ == "__main__":
    unittest.main()
