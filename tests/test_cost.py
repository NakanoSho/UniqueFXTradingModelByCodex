import unittest

from trading.tca import cost


class TestCost(unittest.TestCase):
    def test_spread_bps(self):
        self.assertAlmostEqual(cost.spread_bps(99.5, 100.5, 100.0), 100.0, places=6)

    def test_expected_cost(self):
        params = cost.CostParams()
        tier_params = cost.LiquidityTierParams()
        exp = cost.estimate_expected_cost_bps(
            bid=99.99,
            ask=100.01,
            mid=100.0,
            exec_vol_bps=0.2,
            delta_w=0.001,
            nav=1000000.0,
            pair="EURUSD",
            cost_params=params,
            tier_params=tier_params,
        )
        self.assertTrue(exp > 0.0)
        self.assertTrue(cost.trade_allowed(exp, is_satellite=False, cost_params=params))

    def test_adjust_raw_score(self):
        params = cost.CostParams()
        raw_adj = cost.adjust_raw_score_for_cost(1.0, 2.0, params.gamma_core)
        self.assertAlmostEqual(raw_adj, 1.0 - 2.0 * params.gamma_core, places=12)

    def test_tca_throttle(self):
        new_rho, m2_ok = cost.tca_throttle(1.3, 1.0, 0.5)
        self.assertAlmostEqual(new_rho, 0.4, places=12)
        self.assertFalse(m2_ok)
        new_rho2, m2_ok2 = cost.tca_throttle(1.1, 1.0, 0.5)
        self.assertAlmostEqual(new_rho2, 0.5, places=12)
        self.assertTrue(m2_ok2)


if __name__ == "__main__":
    unittest.main()
