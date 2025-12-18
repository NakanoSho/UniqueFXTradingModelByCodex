import os
import unittest

from trading import config


class TestConfig(unittest.TestCase):
    def test_load_config(self):
        cfg = config.load_config(os.path.join("configs", "v1_0.yaml"))
        self.assertEqual(cfg.version, "v1_0")
        self.assertGreater(cfg.risk_flags.fxvol20_off, 0.0)
        self.assertGreater(cfg.gates.trend_spreadstress_max, 0.0)
        self.assertGreater(cfg.data_qc.max_gap_seconds, 0)


if __name__ == "__main__":
    unittest.main()
