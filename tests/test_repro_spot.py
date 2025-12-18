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
                "--output",
                out_path,
            ]
            subprocess.check_call(cmd)
            with open(out_path, "r") as f:
                data = json.load(f)
            self.assertTrue(data["ok"])
            self.assertEqual(data["rows"], 1)


if __name__ == "__main__":
    unittest.main()
