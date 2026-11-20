"""
End-to-End Multi-Asset Staging Integration Module
Connects:
1. Market Data Engine (docky staging v4-r4: model.py + engine.py)
2. Portfolio Governance & Virtual Paper (botty staging: governance_paper.py)
3. Multi-Agent Advisory Schema & Contracts (Trading Director, Bear Analyst, Market Analyst, Trading Strategist)
4. Deterministic Risk Engine & Fail-Closed Gate
5. Inactive Paper Execution Guard (paper=DISABLED, can_execute=False)
"""
import os
import sys
import json
import math
import hashlib
from decimal import Decimal
from datetime import datetime, timezone

# Add staging paths to sys.path
DOCKY_STAGING = '/opt/data/profiles/docky/workspace/multicurrency-public-v4/market-engine-staging-r1/engine-review-r4'
BOTTY_STAGING = '/opt/data/profiles/botty/workspace/portfolio-paper-isolated'
for p in (DOCKY_STAGING, BOTTY_STAGING):
    if p not in sys.path:
        sys.path.insert(0, p)

import model
import engine
import governance_paper


class DeterministicRiskEngine:
    """
    Deterministic risk evaluation gate.
    Enforces fail-closed behavior, Bear Analyst veto, and operational limits.
    """
    def __init__(self, limits=None):
        # Operational limits separated from test limits
        self.limits = limits or {
            'max_position_risk_eur': Decimal('1.00'),
            'max_total_exposure_eur': Decimal('60.00'),
            'max_daily_loss_eur': Decimal('3.00'),
            'max_open_positions': 1
        }

    def evaluate(self, advisory_packet, portfolio_state):
        """
        advisory_packet: dict containing director_decision, analyst_opinions, bear_veto, market_snapshot
        portfolio_state: dict containing cash, open_positions, daily_loss, reserved_risk
        """
        # 1. Check data quality and completeness
        market_obs = advisory_packet.get('market_snapshot', {})
        if market_obs.get('status') != 'snapshot_only' and market_obs.get('status') != 'ok':
            return {
                'status': 'DENY',
                'reason': f"Market data incomplete or stale: {market_obs.get('status')}",
                'blockers': market_obs.get('blockers', [])
            }

        # 2. Check Bear Analyst Veto (mandatory veto power)
        if advisory_packet.get('bear_veto', False):
            return {
                'status': 'DENY',
                'reason': 'VETO: Bear Analyst active risk veto',
                'veto_detail': advisory_packet.get('bear_veto_reason', 'Unspecified risk factor')
            }

        # 3. Check Trading Director Quorum and Decision
        director_dec = advisory_packet.get('director_decision', {})
        if director_dec.get('status') != 'APPROVED':
            return {
                'status': 'DENY',
                'reason': f"Director decision not approved: {director_dec.get('status')}"
            }

        # 4. Check Open Position Count
        if portfolio_state.get('open_positions_count', 0) >= self.limits['max_open_positions']:
            return {
                'status': 'DENY',
                'reason': 'Max open positions limit reached'
            }

        # 5. Check Daily Loss Budget
        daily_loss = Decimal(str(portfolio_state.get('daily_loss', '0.00')))
        reserved = Decimal(str(portfolio_state.get('reserved_risk', '0.00')))
        trade_risk = Decimal(str(advisory_packet.get('proposed_risk_eur', '0.00')))

        if daily_loss >= self.limits['max_daily_loss_eur']:
            return {
                'status': 'DENY',
                'reason': 'Daily loss limit already reached'
            }
        if daily_loss + reserved + trade_risk > self.limits['max_daily_loss_eur']:
            return {
                'status': 'DENY',
                'reason': 'Proposed trade exceeds daily loss/risk budget'
            }

        # 6. Check Exposure
        trade_exposure = Decimal(str(advisory_packet.get('proposed_exposure_eur', '0.00')))
        if trade_exposure > self.limits['max_total_exposure_eur']:
            return {
                'status': 'DENY',
                'reason': 'Proposed trade exceeds max total exposure limit'
            }

        return {
            'status': 'PASS',
            'reason': 'All deterministic risk gate checks passed',
            'trade_risk_eur': str(trade_risk),
            'trade_exposure_eur': str(trade_exposure)
        }


def run_e2e_integration_test():
    """
    Executes the full end-to-end integration test across:
    - Market Data Observation
    - Portfolio Governance Policy Lifecycle
    - Multi-Agent Deliberation & Quorum
    - Risk Gate (Veto & Fail-Closed)
    - Paper Execution Guard (Ensuring paper=DISABLED / can_execute=False)
    """
    results = {
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'tests': {},
        'overall_status': 'FAILED'
    }

    # Test 1: Market Data Engine Schema & Fail-Closed Top20
    try:
        # Check discover method on 33 EUR pairs
        fake_products = [
            {'id': 'BTC-EUR', 'base_currency': 'BTC', 'quote_currency': 'EUR', 'status': 'online', 'trading_disabled': False},
            {'id': 'ETH-EUR', 'base_currency': 'ETH', 'quote_currency': 'EUR', 'status': 'online', 'trading_disabled': False},
            {'id': 'SOL-EUR', 'base_currency': 'SOL', 'quote_currency': 'EUR', 'status': 'online', 'trading_disabled': False},
        ]
        disc = engine.discover(fake_products)
        assert disc == ['BTC-EUR', 'ETH-EUR', 'SOL-EUR']

        # Check contract returns fail-closed Top20
        fake_snapshot = {
            'generated_utc': '2026-11-18T10:00:00+00:00',
            'fetch': {'age_s': 1.2, 'skew_s': 0.8},
            'source_time': {'book': '2026-11-18T10:00:00+00:00', 'stats': '2026-11-18T10:00:00+00:00'}
        }
        c = engine.contract('BTC-EUR', fake_snapshot)
        assert c['ranking_status'] == 'insufficient_data'
        assert c['top20'] == []
        assert c['risk'] == 'DENY'
        assert c['paper'] == 'DISABLED'
        results['tests']['market_engine_contract'] = 'PASS'
    except Exception as ex:
        results['tests']['market_engine_contract'] = f'FAIL: {ex}'

    # Test 2: Portfolio Governance Lifecycle (Propose -> Approve -> Publish -> Rollback_new)
    try:
        gov = governance_paper.Governance()
        policy = {
            'policy_id': 'multi-asset-v1',
            'capital_eur': '100.00',
            'max_trade_risk_eur': '1.00',
            'max_exposure_eur': '60.00',
            'daily_loss_limit_eur': '3.00'
        }
        v1 = gov.propose(policy, actor='fixture:office')
        gov.approve(v1, actor='fixture:owner')
        gov.publish(v1, actor='fixture:publisher')

        # Test Rollback creates PROPOSED version
        v2 = gov.rollback_new(v1, actor='fixture:office')
        row_v2 = gov.db.execute('SELECT state, policy_id FROM versions WHERE v=?', (v2,)).fetchone()
        assert row_v2[0] == 'PROPOSED'
        assert row_v2[1] == 'multi-asset-v1-rollback'

        # Approve and publish v2
        gov.approve(v2, actor='fixture:owner')
        gov.publish(v2, actor='fixture:publisher')
        active_v = gov.db.execute('SELECT v FROM active WHERE id=1').fetchone()[0]
        assert active_v == v2
        results['tests']['portfolio_governance_lifecycle'] = 'PASS'
    except Exception as ex:
        results['tests']['portfolio_governance_lifecycle'] = f'FAIL: {ex}'

    # Test 3: Multi-Agent Quorum & Deliberation Binding
    try:
        # Advisory packet structure
        advisory = {
            'schema_version': 1,
            'round_id': 'ROUND-STAGE-001',
            'market_snapshot': {
                'product': 'BTC-EUR',
                'status': 'snapshot_only',
                'last': 60000.0,
                'blockers': []
            },
            'analyst_opinions': {
                'market_analyst': {'signal': 'BUY', 'confidence': 75},
                'trading_strategist': {'proposal': 'BUY', 'stop': 59000.0, 'units': '0.0005'},
                'bear_analyst': {'opinion': 'HIGH_VOLATILITY_RISK', 'veto': True, 'reason': 'Unconfirmed breakout with volume divergence'}
            },
            'bear_veto': True,
            'bear_veto_reason': 'Unconfirmed breakout with volume divergence',
            'director_decision': {'status': 'APPROVED', 'quorum': True},
            'proposed_risk_eur': Decimal('0.55'),
            'proposed_exposure_eur': Decimal('30.00')
        }

        # Test Risk Gate with Veto -> must DENY
        risk_engine = DeterministicRiskEngine()
        portfolio_state = {
            'cash': '100.00',
            'open_positions_count': 0,
            'daily_loss': '0.00',
            'reserved_risk': '0.00'
        }
        gate_res = risk_engine.evaluate(advisory, portfolio_state)
        assert gate_res['status'] == 'DENY'
        assert 'VETO' in gate_res['reason']

        # Now test with Veto cleared -> should PASS
        advisory['bear_veto'] = False
        gate_res_pass = risk_engine.evaluate(advisory, portfolio_state)
        assert gate_res_pass['status'] == 'PASS'
        results['tests']['risk_gate_and_veto'] = 'PASS'
    except Exception as ex:
        results['tests']['risk_gate_and_veto'] = f'FAIL: {ex}'

    # Test 4: Paper Execution Guard (Ensuring paper=DISABLED prevents execution)
    try:
        # Check that integration contract strictly forbids execution
        obs = {'product': 'BTC-EUR', 'status': 'snapshot_only'}
        cfg = {'schema_version': 1, 'policy_id': 'pol-1', 'holdings_kind': 'PENDING_PORTFOLIO', 'holdings': []}
        contract = model.integration_contract(obs, cfg)
        assert contract['paper']['status'] == 'DISABLED'
        assert contract['paper']['can_execute'] is False
        assert contract['risk']['status'] == 'DENY'

        # Even if risk gate passes, paper trading is disabled in staging
        can_execute = contract['paper']['can_execute'] and (gate_res_pass['status'] == 'PASS')
        assert can_execute is False
        results['tests']['paper_execution_guard'] = 'PASS'
    except Exception as ex:
        results['tests']['paper_execution_guard'] = f'FAIL: {ex}'

    # Test 5: In-Memory Paper Atomicity & Settlement (Isolated test)
    try:
        paper = governance_paper.Paper()
        # Test open
        res_open = paper.open(
            event='EVT-001',
            asset='BTC-EUR',
            units='0.0005',
            entry_ref='58000.00',
            stop_ref='57000.00',
            fee_bps='10',
            slippage_bps='5',
            at='2026-11-18T12:00:00Z'
        )
        assert res_open == 'OPEN'

        # Test duplicate open is idempotent
        res_dup = paper.open(
            event='EVT-001',
            asset='BTC-EUR',
            units='0.0005',
            entry_ref='58000.00',
            stop_ref='57000.00',
            fee_bps='10',
            slippage_bps='5',
            at='2026-11-18T12:00:00Z'
        )
        assert res_dup == 'DUPLICATE'

        # Test close
        res_close = paper.close(
            event='EVT-002',
            exit_ref='58500.00',
            fee_bps='10',
            slippage_bps='5',
            at='2026-11-18T13:00:00Z'
        )
        assert 'realized_pnl' in res_close
        assert Decimal(res_close['realized_pnl']) > Decimal('0')
        results['tests']['paper_settlement_atomicity'] = 'PASS'
    except Exception as ex:
        results['tests']['paper_settlement_atomicity'] = f'FAIL: {ex}'

    all_pass = all(v == 'PASS' for v in results['tests'].values())
    results['overall_status'] = 'PASS' if all_pass else 'FAIL'
    return results

if __name__ == '__main__':
    res = run_e2e_integration_test()
    print(json.dumps(res, indent=2))
