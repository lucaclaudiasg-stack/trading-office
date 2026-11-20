"""
Aggressive Portfolio Simulator & Time-to-Ruin Analysis Engine for HERMES AGGRESSIVE portfolio.
Operates strictly in SIMULATION_ONLY / DATA_ONLY mode.
"""
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

STATE_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/aggressive_portfolio_state.json')

def quant_dec(val, places='0.01'):
    return Decimal(str(val)).quantize(Decimal(places), rounding=ROUND_HALF_UP)

def init_aggressive_portfolio():
    # Initial common snapshot matching reference valuation
    initial_state = {
        "portfolio_name": "HERMES AGGRESSIVE",
        "created_at_utc": "2026-11-20T19:15:00Z",
        "created_at_rome": "20/11/2026 · 20:15 CET",
        "reference_capital_eur": "142.42",
        "initial_partial_val_eur": "143.58",
        "current_val_eur": "143.58",
        "cash_eur": "2.53",
        "holdings": {
            "BTC": {"balance": "0.00181225", "price_eur": "56931.20", "value_eur": "103.17"},
            "ETH": {"balance": "0.02084170", "price_eur": "1595.40", "value_eur": "33.25"},
            "XLM": {"balance": "26.468", "price_eur": "0.125", "value_eur": "3.31"},
            "GRT": {"balance": "3.957", "price_eur": "0.015", "value_eur": "0.06"}
        },
        "metrics": {
            "pnl_eur": "0.00",
            "pnl_pct": "0.00%",
            "max_drawdown_pct": "0.00%",
            "cumulative_fees_eur": "0.00",
            "total_trades": 0,
            "win_rate_pct": "N/D (Nessun trade chiuso)",
            "virtual_exposure_pct": "98.24%",
            "turnover_rate": "0.00"
        },
        "ruin_analysis": {
            "initial_capital_eur": "142.42",
            "current_capital_eur": "143.58",
            "ruin_thresholds": {
                "loss_10_pct": {"threshold_eur": "128.18", "status": "Non raggiunta", "timestamp": None},
                "loss_25_pct": {"threshold_eur": "106.82", "status": "Non raggiunta", "timestamp": None},
                "loss_50_pct": {"threshold_eur": "71.21", "status": "Non raggiunta", "timestamp": None},
                "loss_75_pct": {"threshold_eur": "35.61", "status": "Non raggiunta", "timestamp": None},
                "loss_90_pct": {"threshold_eur": "14.24", "status": "Non raggiunta", "timestamp": None},
                "loss_100_pct": {"threshold_eur": "0.00", "status": "Non raggiunta", "timestamp": None}
            },
            "time_to_ruin_estimate": "Infinito / Capitale Integro"
        },
        "active_strategy": "Adaptive Hybrid Aggressive V1",
        "last_decision": {
            "timestamp_rome": "20/11/2026 · 20:15 CET",
            "decision_id": "DEC-AGG-001",
            "strategy": "Adaptive Hybrid (Volatility Breakout + Relative Strength)",
            "action": "HOLD / NO_ACTION",
            "reason": "Regime TREND_DOWN. Posizioni mantenute in ossequio al controllo del rischio sperimentale."
        },
        "ledger": []
    }
    STATE_PATH.write_text(json.dumps(initial_state, indent=2), encoding='utf-8')
    print("Aggressive portfolio initialized at:", STATE_PATH)
    return initial_state

def get_aggressive_state():
    if not STATE_PATH.exists():
        return init_aggressive_portfolio()
    try:
        return json.loads(STATE_PATH.read_text(encoding='utf-8'))
    except Exception:
        return init_aggressive_portfolio()

if __name__ == '__main__':
    get_aggressive_state()
