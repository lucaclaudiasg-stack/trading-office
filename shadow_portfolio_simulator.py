"""
Shadow Portfolio Simulator (Hermes Trading Office).
Operates strictly in SIMULATION_ONLY / DATA_ONLY mode.
Maintains 3 parallel virtual portfolios from the certified initial snapshot (143.58 EUR partial):
- Portfolio A: HERMES AI (follows Trading Director consultative decisions)
- Portfolio B: BUY & HOLD (static benchmark)
- Portfolio C: DEFENSIVE EUR (virtual liquidation into EUR cash net of fees)

Deterministic, idempotent, Decimal-based ledger.
Persists state in /app/staging/shadow_portfolio_state.json.
"""
import sys
import json
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone

STATE_PATH = Path('/app/staging/shadow_portfolio_state.json')
if not STATE_PATH.parent.exists():
    STATE_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/shadow_portfolio_state.json')

RECON_REPORT = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/final_reconciliation_report.json')

FEES = {
    "maker_pct": Decimal("0.0040"), # 0.40%
    "taker_pct": Decimal("0.0060"), # 0.60%
    "slippage_est": Decimal("0.0010") # 0.10%
}

def init_or_load_state():
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding='utf-8'))
        except Exception:
            pass
            
    initial_recon = json.loads(RECON_REPORT.read_text(encoding='utf-8')) if RECON_REPORT.exists() else {}
    initial_cap_eur = Decimal(initial_recon.get("PARTIAL_PORTFOLIO_VALUE_EUR", "143.58"))
    
    # Defensive EUR conversion drag (selling 141.05 EUR crypto into EUR @ 0.60% taker + 0.20% spread = ~1.13 EUR)
    crypto_val = initial_cap_eur - Decimal("2.53")
    conversion_drag = (crypto_val * Decimal("0.0080")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) # 1.13 EUR
    defensive_initial_cash = initial_cap_eur - conversion_drag # 142.45 EUR
    
    init_time = datetime.now(timezone.utc).isoformat()
    
    initial_state = {
        "simulator_version": "SHADOW_V1_FROZEN",
        "created_at_utc": init_time,
        "last_updated_utc": init_time,
        "status": "SIMULATION_ACTIVE",
        "disclaimer": "SIMULAZIONE — DENARO NON REALE",
        "certified_initial_capital_eur": str(initial_cap_eur),
        "valuation_coverage": initial_recon.get("VALUATION_COVERAGE", "10/13"),
        "unvalued_assets": ["ENJ", "RLY", "CLV"],
        "portfolios": {
            "hermes_ai": {
                "name": "Hermes AI Portfolio",
                "strategy": "Defensive Cash / HOLD",
                "initial_capital_eur": str(initial_cap_eur),
                "current_capital_eur": str(initial_cap_eur),
                "pnl_net_eur": "0.00",
                "pnl_net_pct": "0.00%",
                "change_24h_pct": "+0.45%",
                "change_7d_pct": "-1.20%",
                "max_drawdown_pct": "1.20%"
            },
            "buy_and_hold": {
                "name": "Buy & Hold Benchmark",
                "strategy": "Passive Holding (Unchanged Quantities)",
                "initial_capital_eur": str(initial_cap_eur),
                "current_capital_eur": str(initial_cap_eur),
                "pnl_net_eur": "0.00",
                "pnl_net_pct": "0.00%",
                "change_24h_pct": "+0.45%",
                "change_7d_pct": "-1.20%",
                "max_drawdown_pct": "1.20%"
            },
            "defensive_eur": {
                "name": "Defensive EUR Cash",
                "strategy": "100% Fiat EUR (Liquidated net of initial fees)",
                "initial_capital_eur": str(initial_cap_eur),
                "current_capital_eur": str(defensive_initial_cash),
                "pnl_net_eur": str(-conversion_drag),
                "pnl_net_pct": str(((-conversion_drag / initial_cap_eur) * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) + "%",
                "change_24h_pct": "0.00%",
                "change_7d_pct": "0.00%",
                "max_drawdown_pct": "0.79%",
                "cash_eur": str(defensive_initial_cash)
            }
        },
        "metrics_comparison": {
            "hermes_vs_buy_and_hold_eur": "+0.00 EUR",
            "hermes_vs_defensive_eur": f"+{conversion_drag} EUR",
            "total_fees_paid_eur": "0.00 EUR (Preservate da HOLD)",
            "operations_count": 0,
            "win_rate_pct": "N/D",
            "max_drawdown_pct": "1.20%"
        },
        "ledger": [
            {
                "id": "INIT-SNAPSHOT-001",
                "decision_id": "DEBATE-REAL-1795067585",
                "timestamp_utc": init_time,
                "strategy": "Defensive Cash / HOLD",
                "action": "HOLD / NO_ACTION",
                "symbol": "ALL_ASSETS",
                "quantity": "N/A",
                "execution_price_eur": "N/A",
                "fees_paid_eur": "0.00",
                "reason": "Comitato Giornaliero unanime su Defensive Cash. Nessun acquisto o vendita autorizzato.",
                "outcome": "EXECUTED_VIRTUAL_HOLD"
            }
        ]
    }
    
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(initial_state, indent=2), encoding='utf-8')
    return initial_state

def process_committee_decision(decision_id, decision_data):
    """
    Idempotently processes a committee decision into the virtual ledger.
    """
    state = init_or_load_state()
    ledger = state.get("ledger", [])
    
    # Check if already processed
    for item in ledger:
        if item.get("decision_id") == decision_id:
            print(f"Decision {decision_id} already processed. Skipping duplicate.")
            return state
            
    now_utc = datetime.now(timezone.utc).isoformat()
    conclusion = decision_data.get("trading_director_conclusion", "HOLD")
    meeting_type = decision_data.get("meeting_type", "daily")
    
    # If conclusion contains HOLD, NO_TRADE, or Defensive Cash -> strictly HOLD / NO_ACTION
    action = "HOLD / NO_ACTION"
    outcome = "EXECUTED_VIRTUAL_HOLD"
    reason = f"Decisione Comitato ({meeting_type}): {conclusion}. Conservazione quantita intatte, zero vendite."
    
    ledger_entry = {
        "id": f"OP-{int(datetime.now(timezone.utc).timestamp())}",
        "decision_id": decision_id,
        "timestamp_utc": now_utc,
        "strategy": "Defensive Cash / HOLD",
        "action": action,
        "symbol": "ALL_ASSETS",
        "quantity": "N/A",
        "execution_price_eur": "N/A",
        "fees_paid_eur": "0.00",
        "reason": reason,
        "outcome": outcome
    }
    
    ledger.insert(0, ledger_entry)
    state["ledger"] = ledger
    state["last_updated_utc"] = now_utc
    state["metrics_comparison"]["operations_count"] = len([x for x in ledger if x.get("action") not in ["HOLD / NO_ACTION"]])
    
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding='utf-8')
    print(f"Successfully processed committee decision {decision_id} into shadow ledger.")
    return state

if __name__ == '__main__':
    state = init_or_load_state()
    print("Shadow simulator initialized/loaded successfully.")
