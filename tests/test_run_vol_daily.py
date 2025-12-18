import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest


class TestRunVolDaily(unittest.TestCase):
    def test_pipeline_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            spot_db = os.path.join(d, "spot.db")
            vol_db = os.path.join(d, "vol.db")
            log_path = os.path.join(d, "log.json")
            conn = sqlite3.connect(spot_db)
            try:
                conn.execute("CREATE TABLE spot_data (ts TEXT, pair TEXT, mid REAL, spread REAL)")
                mid = 1.0
                for i in range(70):
                    mid *= 1.001
                    conn.execute(
                        "INSERT INTO spot_data (ts, pair, mid, spread) VALUES (?, ?, ?, ?)",
                        (f"2025-01-{i+1:02d}", "EURUSD", mid, 0.001),
                    )
                conn.commit()
            finally:
                conn.close()
            cmd = [
                sys.executable,
                "-m",
                "data_pipeline.pipeline.run_vol_daily",
                "--spot-db",
                spot_db,
                "--db",
                vol_db,
                "--ts",
                "2025-01-01",
                "--source",
                "test",
                "--log",
                log_path,
            ]
            subprocess.check_call(cmd)
            with open(log_path, "r") as f:
                log = json.load(f)
            self.assertIn("elapsed_sec", log)
            conn = sqlite3.connect(vol_db)
            try:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM vol_metrics")
                self.assertEqual(cur.fetchone()[0], 1)
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()
