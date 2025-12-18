import unittest

from ops.alerts import monitor


class TestMonitor(unittest.TestCase):
    def test_alerts(self):
        metrics = {
            "pnl_daily": -0.03,
            "pnl_weekly": -0.01,
            "pnl_monthly": 0.0,
            "dd": 0.13,
            "spread_stress": 1.6,
            "real_to_exp_cost_ratio": 1.3,
        }
        alerts = monitor.evaluate_alerts(metrics, monitor.AlertThresholds())
        self.assertIn("daily_loss_limit", alerts)
        self.assertIn("dd_soft_limit", alerts)
        self.assertIn("spread_stress", alerts)
        self.assertIn("cost_ratio", alerts)


if __name__ == "__main__":
    unittest.main()
