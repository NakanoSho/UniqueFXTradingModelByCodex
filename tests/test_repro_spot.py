import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest


class TestReproSpot(unittest.TestCase):
    def test_repro_ok(self):
        with tempfile.TemporaryDirectory() as d:
            input_path = os.path.join(d, "spot.csv")
            out_path = os.path.join(d, "repro.json")
            db1 = os.path.join(d, "spot1.db")
            db2 = os.path.join(d, "spot2.db")
            with open(input_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["timestamp", "symbol", "bid", "ask"])
                writer.writeheader()
                writer.writerow({"timestamp": "2025-01-01T00:00:00Z", "symbol": "EURUSD", "bid": "1.09", "ask": "1.11"})
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
                out_path,
                "--config",
                os.path.join("configs", "v1_0.yaml"),
            ]
            subprocess.check_call(cmd)
            with open(out_path, "r") as f:
                data = json.load(f)
            self.assertTrue(data["hash_match"])


if __name__ == "__main__":
    unittest.main()
