import json
import os
import subprocess
import sys
import tempfile
import unittest


class TestDailyReport(unittest.TestCase):
    def test_report_generation(self):
        with tempfile.TemporaryDirectory() as d:
            metrics_path = os.path.join(d, "metrics.json")
            output_path = os.path.join(d, "report.json")
            with open(metrics_path, "w") as f:
                json.dump({"pnl_daily": 0.0, "pnl_weekly": 0.0, "pnl_monthly": 0.0, "dd": 0.0}, f)
            cmd = [
                sys.executable,
                "-m",
                "ops.alerts.daily_report",
                "--metrics",
                metrics_path,
                "--output",
                output_path,
            ]
            subprocess.check_call(cmd)
            with open(output_path, "r") as f:
                report = json.load(f)
            self.assertIn("alerts", report)
            self.assertTrue(report["ok"])


if __name__ == "__main__":
    unittest.main()
