"""
Unit and Integration Test Suite for:
1. Top 20 Esplorativa (exploratory_top20.py)
2. Multi-Currency Incremental History (multi_currency_history.py)
3. Analyst Exploratory Bridge & Risk Gate (analyst_exploratory_bridge.py)
4. OS_BLOCKED Security Assertion (engine.py)
"""
import sys
import unittest
import json
from decimal import Decimal

# Add staging paths
sys.path.insert(0, '/opt/data/profiles/docky/workspace/multicurrency-public-v4/market-engine-staging-r1/engine-review-r4')
sys.path.insert(0, '/opt/data/profiles/botty/workspace/portfolio-paper-isolated')
sys.path.insert(0, '/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')

import engine
import exploratory_top20
import multi_currency_history
import analyst_exploratory_bridge


class TestExploratoryAndPipeline(unittest.TestCase):

    def test_exploratory_classification(self):
        # Case 1: Valid book and stats, but stats has no timestamp -> EXPLORATORY
        book = {
            'bids': [['58000.00', '1.5'], ['57900.00', '2.0']],
            'asks': [['58100.00', '1.2'], ['58200.00', '3.0']],
            'time': '2026-11-18T12:00:00Z',
            'sequence': 123456
        }
        stats = {
            'last': '58050.00',
            'volume': '250.0'
            # No 'time'
        }
        res = exploratory_top20.classify_market_data('BTC-EUR', book, stats)
        self.assertEqual(res['tier'], 'EXPLORATORY')
        self.assertIn('stats endpoint lacks source timestamp', res['tier_reason'])
        self.assertEqual(res['operational_permission'], 'ANALYSIS_ONLY (No trade authorization allowed)')
        self.assertIsNotNone(res['metrics']['score'])

        # Case 2: Crossed book -> INSUFFICIENT_DATA
        crossed_book = {
            'bids': [['58200.00', '1.0']],
            'asks': [['58100.00', '1.0']]
        }
        res_crossed = exploratory_top20.classify_market_data('BTC-EUR', crossed_book, stats)
        self.assertEqual(res_crossed['tier'], 'INSUFFICIENT_DATA')

        # Case 3: Negative volume -> INSUFFICIENT_DATA
        bad_stats = {'last': '58000.0', 'volume': '-5.0'}
        res_bad = exploratory_top20.classify_market_data('BTC-EUR', book, bad_stats)
        self.assertEqual(res_bad['tier'], 'INSUFFICIENT_DATA')

    def test_top20_ranking_order(self):
        # Create a list of 25 simulated market results with tight spread within +/-1%
        # Both volume and depth decrease with i, so TOKEN1-EUR has the highest composite score
        markets = []
        for i in range(1, 26):
            p = f'TOKEN{i}-EUR'
            qty = str(100.0 - i)
            book = {
                'bids': [[str(100.0 - i * 0.01), qty]],
                'asks': [[str(100.0 + i * 0.01), qty]],
                'time': '2026-11-18T12:00:00Z'
            }
            stats = {
                'last': str(100.0),
                'volume': str(1000.0 * (26 - i)) # Higher volume for lower i
            }
            res = exploratory_top20.classify_market_data(p, book, stats)
            markets.append(res)
            
        ranking = exploratory_top20.build_exploratory_top20(markets)
        self.assertEqual(ranking['top20_count'], 20)
        self.assertEqual(ranking['eligible_count'], 25)
        self.assertEqual(ranking['top20'][0]['rank'], 1)
        self.assertEqual(ranking['top20'][0]['product'], 'TOKEN1-EUR')

    def test_multi_currency_history_readonly(self):
        # Check BTC-EUR read-only inspection
        btc_info = multi_currency_history.inspect_verified_archive('BTC-EUR')
        self.assertEqual(btc_info['status'], 'VERIFIED_READONLY')
        self.assertEqual(btc_info['quick_check'], 'ok')
        self.assertGreater(btc_info['hourly_candles_count'], 8000)

        # Check gap planning for 720h (window of 30 days)
        cutoff = 1795003200 # Fixed test cutoff
        gaps = multi_currency_history.plan_720h_incremental_gaps('BTC-EUR', cutoff)
        self.assertEqual(gaps['expected_total'], 720)
        self.assertIn('existing_count', gaps)
        self.assertIn('missing_count', gaps)
        self.assertIn('coverage_pct', gaps)
        self.assertLessEqual(gaps['bounded_batch_recommended_size'], 4)

    def test_analyst_bridge_veto_and_fail_closed(self):
        # Exploratory market
        market = {
            'product': 'SOL-EUR',
            'tier': 'EXPLORATORY',
            'metrics': {'spread_bps': 8.5, 'volume_eur_proxy_24h': 1200000.0, 'depth_total_1pct_eur': 45000.0, 'last_price_eur': 140.0}
        }
        packet = analyst_exploratory_bridge.generate_analyst_packet(market, {})
        # Must produce Bear Veto because it is EXPLORATORY
        self.assertTrue(packet['analysts']['bear_analyst']['veto'])
        # Strategist must recommend HOLD
        self.assertEqual(packet['analysts']['trading_strategist']['action'], 'HOLD')
        # Director must be REJECTED_BY_VETO
        self.assertEqual(packet['director']['decision'], 'REJECTED_BY_VETO')
        # Risk gate must be DENY
        self.assertEqual(packet['risk_gate']['gate_status'], 'DENY')
        self.assertFalse(packet['risk_gate']['can_execute'])

    def test_os_blocked_enforcement(self):
        # Verify that engine.create_stage strictly raises RuntimeError with OS_BLOCKED
        with self.assertRaises(RuntimeError) as cm:
            engine.create_stage()
        self.assertIn('OS_BLOCKED', str(cm.exception))


if __name__ == '__main__':
    unittest.main()
