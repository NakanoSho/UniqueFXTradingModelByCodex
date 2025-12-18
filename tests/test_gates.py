import os
import unittest

from trading import config as cfg
from trading.risk import gates


class TestGates(unittest.TestCase):
    def test_risk_flags(self):
        thresholds = cfg.load_config(os.path.join("configs", "v1_0.yaml"))
        t = thresholds.risk_flags
        self.assertTrue(gates.risk_off_flag(12.1, 1.0, 1.0, t))
        self.assertTrue(gates.risk_off_flag(10.0, 1.6, 1.0, t))
        self.assertTrue(gates.risk_off_flag(10.0, 1.0, 1.6, t))
        self.assertTrue(gates.risk_on_flag(9.0, 1.1, 1.1, t))
        self.assertFalse(gates.risk_on_flag(10.1, 1.1, 1.1, t))

    def test_trend_gate(self):
        thresholds = cfg.load_config(os.path.join("configs", "v1_0.yaml"))
        t = thresholds.gates
        self.assertTrue(gates.trend_gate(True, 1.2, True, True, t))
        self.assertFalse(gates.trend_gate(True, 1.6, True, True, t))
        self.assertFalse(gates.trend_gate(False, 1.2, True, True, t))

    def test_carry_gate_and_crash(self):
        thresholds = cfg.load_config(os.path.join("configs", "v1_0.yaml"))
        t = thresholds.gates
        self.assertEqual(gates.carry_gate(True), 0.0)
        self.assertEqual(gates.carry_gate(False), 1.0)
        self.assertTrue(gates.carry_crash_stop(-0.03, t))
        self.assertFalse(gates.carry_crash_stop(-0.01, t))

    def test_value_gate(self):
        thresholds = cfg.load_config(os.path.join("configs", "v1_0.yaml"))
        t = thresholds.gates
        self.assertEqual(gates.value_gate(0.5, 11.0, t), 1.0)
        self.assertEqual(gates.value_gate(0.5, 13.0, t), 0.5)
        self.assertEqual(gates.value_gate(0.5, 15.0, t), 0.0)
        self.assertEqual(gates.value_gate(1.1, 11.0, t), 0.0)

    def test_satellite_gates(self):
        thresholds = cfg.load_config(os.path.join("configs", "v1_0.yaml"))
        t = thresholds.gates
        self.assertTrue(gates.satellite_m1_gate(True, 0.03, -0.01, True, t))
        self.assertFalse(gates.satellite_m1_gate(True, 0.05, -0.01, True, t))
        self.assertTrue(gates.satellite_m2_gate(True, 0.01, 1.0, 1.1, t))
        self.assertFalse(gates.satellite_m2_gate(True, 0.03, 1.0, 1.1, t))
        self.assertTrue(gates.satellite_stop(True, 0.0, 0.0))
        self.assertTrue(gates.satellite_stop(False, -0.02, 0.0))
        self.assertTrue(gates.satellite_stop(False, 0.0, -0.04))
        self.assertFalse(gates.satellite_stop(False, 0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
