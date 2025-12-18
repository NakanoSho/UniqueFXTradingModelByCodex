import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest


class TestSpotRepro(unittest.TestCase):
    def test_repro(self):
        with tempfile.TemporaryDirectory() as d:
            input_path = os.path.join(d, "spot.csv")
            db1 = os.path.join(d, "spot1.db")
            db2 = os.path.join(d, "spot2.db")
            log_path = os.path.join(d, "log.json")
            with open(input_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["ts", "pair", "mid", "bid", "ask"])
                writer.writeheader()
                writer.writerow({"ts": "2025-01-01", "pair": "EURUSD", "mid": "1.1", "bid": "1.09", "ask": "1.11"})
            cmd = [
                sys.executable,
                "-m",
                "ops.repro.spot_repro",
                "--input",
                input_path,
                "--db1",
                db1,
                "--db2",
                db2,
                "--source",
                "test",
                "--log",
                log_path,
            ]
            subprocess.check_call(cmd)
            with open(log_path, "r") as f:
                log = json.load(f)
            self.assertTrue(log["hash_match"])


if __name__ == "__main__":
    unittest.main()
