import math
import unittest

from trading.signals import scoring


class TestScoring(unittest.TestCase):
    def test_winsor_clip_score(self):
        raw = 5.0
        score = scoring.score_from_raw(raw)
        expected = math.tanh(3.0 / 2.0)
        self.assertAlmostEqual(score, expected, places=12)

    def test_trend_raw(self):
        prices = [100.0]
        for _ in range(120):
            prices.append(prices[-1] * 1.001)
        sigma20 = 0.01
        raw = scoring.trend_raw(prices, sigma20)
        ln_step = math.log(1.001)
        expected = 0.0
        for h, w in zip((20, 60, 120), (0.5, 0.3, 0.2)):
            log_ratio = ln_step * h
            t_stat = log_ratio / (sigma20 * math.sqrt(h))
            expected += w * t_stat
        self.assertAlmostEqual(raw, expected, places=10)
        self.assertTrue(scoring.trend_entry_ok(raw))

    def test_carry_raw_and_scale(self):
        carry = scoring.carry_ann(101.0, 100.0, 30)
        self.assertTrue(carry > 0)
        raw = scoring.carry_raw(carry, cs_z=1.0, ts_z=0.5)
        scaled = scoring.apply_vol_scale(raw, fxvol20=12.0)
        self.assertAlmostEqual(raw, 0.8, places=12)
        self.assertAlmostEqual(scaled, 0.4, places=12)

    def test_value_raw(self):
        prices = [100.0, 101.0, 102.0, 103.0, 104.0]
        raw, z_val = scoring.value_raw(prices, window=5)
        logs = [math.log(p) for p in prices]
        mean = sum(logs) / 5
        var = sum((x - mean) ** 2 for x in logs) / 5
        std = math.sqrt(var)
        expected_z = (math.log(prices[-1]) - mean) / std
        self.assertAlmostEqual(z_val, expected_z, places=12)
        self.assertAlmostEqual(raw, -expected_z, places=12)
        self.assertTrue(scoring.value_entry_ok(z_val, threshold=0.7) == (abs(z_val) >= 0.7))

    def test_satellite_breakout_and_alignment(self):
        closes = [100 + i for i in range(25)]
        highs = [c + 0.5 for c in closes]
        lows = [c - 0.5 for c in closes]
        mid = scoring.donchian_mid(closes, lookback=20)
        atr_val = scoring.atr(highs, lows, closes, lookback=20)
        raw_break = scoring.breakout_raw(closes[-1], mid, atr_val)
        raw_sat = scoring.satellite_raw(raw_break, z_vr=1.0)
        aligned = scoring.enforce_trend_alignment(raw_sat, raw_trend=1.0)
        self.assertNotEqual(raw_break, 0.0)
        self.assertNotEqual(raw_sat, 0.0)
        self.assertEqual(aligned, raw_sat)
        self.assertTrue(scoring.satellite_entry_ok(raw_sat))
        self.assertTrue(scoring.satellite_exit(0.2))


if __name__ == "__main__":
    unittest.main()
