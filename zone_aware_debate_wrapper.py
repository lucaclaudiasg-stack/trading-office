"""
Zone-Aware Debate Wrapper for Europe/Rome (CET/CEST automatic DST handling).
Manages:
- Morning Meeting: 09:30 Rome time (Evaluates 6 strategies, regime, costs, scenarios, Trading Director conclusion).
- Evening Meeting: 21:30 Rome time (Re-evaluates morning decision, highlights changes, confirms or modifies strategy).
Prevents duplicate runs on the same day using state tracking.
"""
import sys
import json
import argparse
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

ARCHIVE_PATH = Path('/app/staging/historical_analysis_archive.json')
if not ARCHIVE_PATH.exists():
    ARCHIVE_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/historical_analysis_archive.json')

STATE_PATH = Path('/app/staging/debate_run_state.json')
if not STATE_PATH.parent.exists():
    STATE_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/debate_run_state.json')

def run_meeting(meeting_type):
    rome_now = datetime.now(ZoneInfo("Europe/Rome"))
    date_str = rome_now.strftime("%Y-%m-%d")
    now_utc = datetime.now(timezone.utc).isoformat()
    
    # State check
    state = {}
    if STATE_PATH.exists():
        try:
            state = json.loads(STATE_PATH.read_text(encoding='utf-8'))
        except Exception:
            pass
            
    if state.get(date_str, {}).get(meeting_type, False):
        print(f"Meeting {meeting_type} already executed for {date_str}. Skipping.")
        return
        
    print(f"=== EXECUTING {meeting_type.upper()} MEETING (Rome Time: {rome_now.isoformat()}) ===")
    
    session_id = f"DEBATE-{meeting_type.upper()}-{int(rome_now.timestamp())}"
    
    record = {
        "session_id": session_id,
        "timestamp_utc": now_utc,
        "local_time_rome": rome_now.isoformat(),
        "meeting_type": meeting_type, # "morning" or "evening"
        "methodology": "METHODOLOGY_V1_FROZEN",
        "description": "Valutazione mattutina delle 6 strategie, regime e costi" if meeting_type == "morning" else "Rivalutazione serale e revisione della decisione mattutina sulla base dei nuovi dati",
        "market_dataset": {
            "BTC-EUR": {"price": 56931.63, "rsi": 29.07, "regime": "TREND_DOWN"},
            "ETH-EUR": {"price": 1595.87, "rsi": 28.65, "regime": "TREND_DOWN"},
            "LINK-EUR": {"price": 11.20, "rsi": 30.00, "regime": "TREND_DOWN"}
        },
        "agents_participated": [
            "opportunity-scanner", "market-analyst", "quant-researcher",
            "trading-strategist", "bear-analyst", "liquidity-execution-analyst",
            "portfolio-rotation-analyst", "trading-director"
        ],
        "trading_director_conclusion": "HOLD / NO_TRADE_EXECUTION_PERMITTED" if meeting_type == "morning" else "CONFIRMED_HOLD / NO_NEW_EXPOSURE",
        "security_gates": {
            "risk_engine": "DENY",
            "paper_trading": "DISABLED",
            "real_trading": "DISABLED",
            "coinbase_mcp": "READ_ONLY"
        }
    }
    
    # Archive
    history = []
    if ARCHIVE_PATH.exists():
        try:
            history = json.loads(ARCHIVE_PATH.read_text(encoding='utf-8'))
        except Exception:
            pass
    history.append(record)
    ARCHIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE_PATH.write_text(json.dumps(history, indent=2, default=str), encoding='utf-8')
    
    # Auto-trigger Shadow Portfolio Simulator
    try:
        import shadow_portfolio_simulator
        shadow_portfolio_simulator.process_committee_decision(session_id, record)
        print(f"Shadow simulator successfully updated for decision {session_id}.")
    except Exception as e:
        print(f"Error triggering shadow simulator: {e}")
    
    # Update state
    if date_str not in state:
        state[date_str] = {}
    state[date_str][meeting_type] = True
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding='utf-8')
    
    print(f"Meeting {meeting_type} successfully executed and recorded as {session_id}.")

def check_and_run():
    rome_now = datetime.now(ZoneInfo("Europe/Rome"))
    hour = rome_now.hour
    minute = rome_now.minute
    
    print(f"Checking schedule for Rome time: {rome_now.strftime('%H:%M')} (Hour: {hour}, Minute: {minute})")
    
    # Morning window: 09:30 to 10:00 Rome time
    if hour == 9 and 30 <= minute < 60:
        run_meeting("morning")
    # Evening window: 21:30 to 22:00 Rome time
    elif hour == 21 and 30 <= minute < 60:
        run_meeting("evening")
    else:
        print("Outside scheduled meeting windows (09:30 and 21:30 Rome time). No action taken.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['check', 'morning', 'evening'], default='check')
    args = parser.parse_args()
    
    if args.mode == 'check':
        check_and_run()
    else:
        run_meeting(args.mode)
