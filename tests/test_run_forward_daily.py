import csv
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest


class TestRunForwardDaily(unittest.TestCase):
    def test_pipeline_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            input_path = os.path.join(d, "forward.csv")
            db_path = os.path.join(d, "forward.db")
            log_path = os.path.join(d, "log.json")
            with open(input_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["ts", "pair", "fwd_1m_mid", "spot_mid"])
                writer.writeheader()
                writer.writerow({"ts": "2025-01-01", "pair": "EURUSD", "fwd_1m_mid": "1.11", "spot_mid": "1.10"})
            cmd = [
                sys.executable,
                "-m",
                "data_pipeline.pipeline.run_forward_daily",
                "--input",
                input_path,
                "--db",
                db_path,
                "--source",
                "test",
                "--log",
                log_path,
            ]
            subprocess.check_call(cmd)
            with open(log_path, "r") as f:
                log = json.load(f)
            self.assertEqual(log["rows"], 1)
            conn = sqlite3.connect(db_path)
            try:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM forward_data")
                self.assertEqual(cur.fetchone()[0], 1)
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()
