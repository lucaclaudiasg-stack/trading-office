"""
Archives the REAL_AGENT_DEBATE transcript into /app/staging/historical_analysis_archive.json.
Distinguishes REAL_AGENT_DEBATE from DETERMINISTIC_ANALYSIS.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

ARCHIVE_PATH = Path('/app/staging/historical_analysis_archive.json')
if not ARCHIVE_PATH.exists():
    ARCHIVE_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/historical_analysis_archive.json')

def archive_real_debate():
    now_utc = datetime.now(timezone.utc).isoformat()
    session_id = f"DEBATE-REAL-{int(datetime.now(timezone.utc).timestamp())}"
    
    debate_record = {
        "session_id": session_id,
        "timestamp_utc": now_utc,
        "type": "REAL_AGENT_DEBATE",
        "methodology": "METHODOLOGY_V1_FROZEN",
        "market_dataset": {
            "BTC-EUR": {"price": 56931.63, "rsi": 29.07, "ema20": 58446.24, "spread_bps": 1.2, "vol30d": 43.06},
            "ETH-EUR": {"price": 1595.87, "rsi": 28.65, "ema20": 1637.68, "spread_bps": 1.9, "vol30d": 57.70},
            "LINK-EUR": {"price": 11.20, "rsi": 30.00, "spread_bps": 5.4, "vol30d": 75.83}
        },
        "agents_participated": [
            "opportunity-scanner", "market-analyst", "quant-researcher",
            "trading-strategist", "bear-analyst", "liquidity-execution-analyst",
            "portfolio-rotation-analyst", "trading-director"
        ],
        "specialists_consensus": "Defensive Cash (7/7 Unanimous)",
        "bear_analyst_counter_thesis": "Trappola dell'ipervenduto (oversold trap), rischio dead cat bounce e asimmetria tra target economico (+3.51%) e budget di perdita (2.1%).",
        "liquidity_analyst_cost_assessment": "Attrito round-trip (spread + taker fee) assorbe dal 38% al 58% dell'intero budget settimanale (3 EUR). Richiesto guadagno lordo > +4.4%.",
        "trading_director_verdict": {
            "selected_strategy": "Defensive Cash (100% Liquidita / HOLD protettivo)",
            "alternative_strategy": "None (Mean Reversion scartata per asimmetria sfavorevole)",
            "reference_asset": "EUR (Cash)",
            "grande_opportunita": False,
            "decision": "HOLD / NO_TRADE_EXECUTION_PERMITTED"
        },
        "economic_parameters": {
            "reference_capital_eur": "142.42",
            "weekly_target_eur": "+5.00 EUR netti",
            "weekly_risk_budget_eur": "3.00 EUR max",
            "status": "PROTECTED_ZERO_LOSS"
        },
        "security_gates": {
            "risk_engine": "DENY",
            "paper_trading": "DISABLED",
            "real_trading": "DISABLED",
            "coinbase_mcp": "READ_ONLY"
        }
    }
    
    history = []
    if ARCHIVE_PATH.exists():
        try:
            history = json.loads(ARCHIVE_PATH.read_text(encoding='utf-8'))
        except Exception:
            pass
            
    history.append(debate_record)
    ARCHIVE_PATH.write_text(json.dumps(history, indent=2, default=str), encoding='utf-8')
    print("REAL_AGENT_DEBATE successfully archived:", session_id)

if __name__ == '__main__':
    archive_real_debate()
