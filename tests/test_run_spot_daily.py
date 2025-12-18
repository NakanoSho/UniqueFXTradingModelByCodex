import csv
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest


class TestRunSpotDaily(unittest.TestCase):
    def test_pipeline_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            input_path = os.path.join(d, "spot.csv")
            db_path = os.path.join(d, "spot.db")
            log_path = os.path.join(d, "log.json")
            with open(input_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["ts", "pair", "mid", "bid", "ask"])
                writer.writeheader()
                writer.writerow({"ts": "2025-01-01", "pair": "EURUSD", "mid": "1.1", "bid": "1.09", "ask": "1.11"})
            cmd = [
                sys.executable,
                "-m",
                "data_pipeline.pipeline.run_spot_daily",
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
                cur.execute("SELECT COUNT(*) FROM spot_data")
                count = cur.fetchone()[0]
                self.assertEqual(count, 1)
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()
