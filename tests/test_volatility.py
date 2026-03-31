import os
import sqlite3
import tempfile
import unittest

from data_pipeline.features import volatility
from data_pipeline.store import spot


class TestVolatility(unittest.TestCase):
    def test_compute_metrics(self):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        path = tmp.name
        spot.init_db(path)
        rows = []
        mid = 1.0
        for i in range(70):
            mid *= 1.001
            rows.append({
                "ts": f"2025-01-{i+1:02d}",
                "pair": "EURUSD",
                "mid": mid,
                "bid": mid - 0.0005,
                "ask": mid + 0.0005,
                "spread": 0.001,
                "spread_stress": 1.0,
                "gap_flag": False,
            })
        spot.insert_rows(path, rows, source="test")
        series = volatility.fetch_spot_series(path)
        fxvol20 = volatility.compute_fxvol20(series)
        voljump = volatility.compute_voljump(series)
        spread_stress = volatility.compute_spread_stress(series)
        self.assertTrue(fxvol20 >= 0.0)
        self.assertTrue(voljump >= 0.0)
        self.assertTrue(spread_stress >= 0.0)
        os.unlink(path)


if __name__ == "__main__":
    unittest.main()
