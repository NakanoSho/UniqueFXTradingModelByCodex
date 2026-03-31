import csv
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from data_pipeline.store import forward as forward_store


class TestRunWeek3Daily(unittest.TestCase):
    def test_week3_daily_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            tick_path = os.path.join(d, "ticks.csv")
            out_dir = os.path.join(d, "derived")
            log_bars = os.path.join(d, "bars_log.json")
            log_regime = os.path.join(d, "regime_log.json")
            log_scores = os.path.join(d, "scores_log.json")
            forward_db = os.path.join(d, "forward.db")

            with open(tick_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["timestamp", "symbol", "bid", "ask"])
                writer.writeheader()
                writer.writerow(
                    {"timestamp": "2025-01-02T23:00:00Z", "symbol": "EURUSD", "bid": "1.00", "ask": "1.02"}
                )
                writer.writerow(
                    {"timestamp": "2025-01-02T23:59:00Z", "symbol": "EURUSD", "bid": "1.02", "ask": "1.03"}
                )
                writer.writerow(
                    {"timestamp": "2025-01-03T00:00:00Z", "symbol": "EURUSD", "bid": "2.00", "ask": "2.02"}
                )
                writer.writerow(
                    {"timestamp": "2025-01-02T23:58:00Z", "symbol": "USDJPY", "bid": "110.0", "ask": "110.2"}
                )
                writer.writerow(
                    {"timestamp": "2025-01-03T00:00:00Z", "symbol": "USDJPY", "bid": "111.0", "ask": "111.2"}
                )

            forward_store.init_db(forward_db)
            forward_store.insert_rows(
                forward_db,
                [
                    {
                        "ts": "2025-01-02T00:00:00Z",
                        "pair": "EURUSD",
                        "fwd_1m_mid": 1.021,
                        "spot_mid": 1.01,
                    },
                    {
                        "ts": "2025-01-02T00:00:00Z",
                        "pair": "USDJPY",
                        "fwd_1m_mid": 110.1,
                        "spot_mid": 110.0,
                    },
                ],
                source="test",
            )

            cmd_bars = [
                sys.executable,
                "-m",
                "data_pipeline.pipeline.run_bars_daily",
                "--input",
                tick_path,
                "--date",
                "2025-01-02",
                "--output",
                out_dir,
                "--log",
                log_bars,
                "--config",
                os.path.join("configs", "v1_0.yaml"),
            ]
            subprocess.check_call(cmd_bars)

            bars_path = os.path.join(
                out_dir, "bars_daily", "v1_0", "pair=EURUSD", "date=2025-01-02", "data.csv"
            )
            with open(bars_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertAlmostEqual(float(rows[0]["daily_close_mid"]), (1.02 + 1.03) / 2.0)

            cmd_regime = [
                sys.executable,
                "-m",
                "data_pipeline.pipeline.run_regime_daily",
                "--date",
                "2025-01-02",
                "--output",
                out_dir,
                "--log",
                log_regime,
                "--config",
                os.path.join("configs", "v1_0.yaml"),
            ]
            subprocess.check_call(cmd_regime)

            cmd_scores = [
                sys.executable,
                "-m",
                "data_pipeline.pipeline.run_scores_daily",
                "--date",
                "2025-01-02",
                "--output",
                out_dir,
                "--forward-db",
                forward_db,
                "--log",
                log_scores,
                "--config",
                os.path.join("configs", "v1_0.yaml"),
            ]
            subprocess.check_call(cmd_scores)

            scores_path = os.path.join(
                out_dir, "scores_daily", "v1_0", "date=2025-01-02", "data.csv"
            )
            with open(scores_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            self.assertTrue(any(r["pair"] == "EURUSD" for r in rows))
            self.assertTrue(all(r["date"] == "2025-01-02" for r in rows))


if __name__ == "__main__":
    unittest.main()
