import csv
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest


class TestRunExpectedCostDaily(unittest.TestCase):
    def test_pipeline_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            input_path = os.path.join(d, "intents.csv")
            db_path = os.path.join(d, "cost.db")
            log_path = os.path.join(d, "log.json")
            with open(input_path, "w", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["ts", "pair", "bid", "ask", "mid", "exec_vol_bps", "delta_w", "nav", "sleeve"],
                )
                writer.writeheader()
                writer.writerow({
                    "ts": "2025-01-01",
                    "pair": "EURUSD",
                    "bid": "99.99",
                    "ask": "100.01",
                    "mid": "100.0",
                    "exec_vol_bps": "0.2",
                    "delta_w": "0.001",
                    "nav": "1000000",
                    "sleeve": "core",
                })
            cmd = [
                sys.executable,
                "-m",
                "data_pipeline.pipeline.run_expected_cost_daily",
                "--input",
                input_path,
                "--db",
                db_path,
                "--source",
                "test",
                "--log",
                log_path,
                "--config",
                os.path.join("configs", "v1_0.yaml"),
            ]
            subprocess.check_call(cmd)
            with open(log_path, "r") as f:
                log = json.load(f)
            self.assertEqual(log["rows"], 1)
            conn = sqlite3.connect(db_path)
            try:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM expected_costs")
                self.assertEqual(cur.fetchone()[0], 1)
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()
