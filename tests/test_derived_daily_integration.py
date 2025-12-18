import csv
import os
import subprocess
import sys
import tempfile
import unittest

from data_pipeline.derived.io import read_csv
from data_pipeline.store import forward as forward_store


class TestDerivedDailyIntegration(unittest.TestCase):
    def _write_ticks(self, path, rows):
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "symbol", "bid", "ask"])
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

    def _read_scores(self, base_dir, date):
        path = os.path.join(base_dir, "scores_daily", "v1_0", f"date={date}", "data.csv")
        return read_csv(path)

    def _read_regime(self, base_dir, date):
        path = os.path.join(base_dir, "regime_daily", "v1_0", f"date={date}", "data.csv")
        return read_csv(path)

    def test_no_lookahead(self):
        with tempfile.TemporaryDirectory() as d:
            date1 = "2025-01-02"
            date2 = "2025-01-03"
            ticks_full = [
                {"timestamp": f"{date1}T23:59:00Z", "symbol": "EURUSD", "bid": "1.00", "ask": "1.01"},
                {"timestamp": f"{date1}T23:59:30Z", "symbol": "USDJPY", "bid": "150.0", "ask": "150.1"},
                {"timestamp": f"{date2}T23:59:00Z", "symbol": "EURUSD", "bid": "2.00", "ask": "2.01"},
                {"timestamp": f"{date2}T23:59:30Z", "symbol": "USDJPY", "bid": "250.0", "ask": "250.1"},
            ]
            ticks_trunc = [row for row in ticks_full if row["timestamp"].startswith(date1)]

            input_full = os.path.join(d, "ticks_full.csv")
            input_trunc = os.path.join(d, "ticks_trunc.csv")
            self._write_ticks(input_full, ticks_full)
            self._write_ticks(input_trunc, ticks_trunc)

            forward_db = os.path.join(d, "forward.db")
            forward_store.init_db(forward_db)
            forward_store.insert_rows(
                forward_db,
                [
                    {
                        "ts": f"{date1}T00:00:00Z",
                        "pair": "EURUSD",
                        "fwd_1m_mid": 1.01,
                        "spot_mid": 1.0,
                    },
                    {
                        "ts": f"{date1}T00:00:00Z",
                        "pair": "USDJPY",
                        "fwd_1m_mid": 150.2,
                        "spot_mid": 150.0,
                    },
                    {
                        "ts": f"{date2}T00:00:00Z",
                        "pair": "EURUSD",
                        "fwd_1m_mid": 2.01,
                        "spot_mid": 2.0,
                    },
                ],
                source="test",
            )

            out_full = os.path.join(d, "full")
            out_trunc = os.path.join(d, "trunc")
            for out_base, input_path in [(out_full, input_full), (out_trunc, input_trunc)]:
                cmd = [
                    sys.executable,
                    "-m",
                    "data_pipeline.pipeline.run_derived_daily",
                    "--input",
                    input_path,
                    "--output",
                    out_base,
                    "--forward-db",
                    forward_db,
                    "--date",
                    date1,
                    "--config",
                    os.path.join("configs", "v1_0.yaml"),
                ]
                subprocess.check_call(cmd)

            scores_full = self._read_scores(out_full, date1)
            scores_trunc = self._read_scores(out_trunc, date1)
            self.assertEqual(scores_full, scores_trunc)

            regime_full = self._read_regime(out_full, date1)
            regime_trunc = self._read_regime(out_trunc, date1)
            self.assertEqual(regime_full, regime_trunc)


if __name__ == "__main__":
    unittest.main()
