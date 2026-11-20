"""
READ_ONLY Audit of the 09:30 Europe/Rome morning meeting (2026-11-19).
Inspects executions.db, debate_run_state.json, historical_analysis_archive.json, and shadow_portfolio_state.json.
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path('/opt/data/cron/executions.db')
STATE_PATH = Path('/app/staging/debate_run_state.json')
if not STATE_PATH.exists():
    STATE_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/debate_run_state.json')

ARCHIVE_PATH = Path('/app/staging/historical_analysis_archive.json')
if not ARCHIVE_PATH.exists():
    ARCHIVE_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/historical_analysis_archive.json')

SHADOW_PATH = Path('/app/staging/shadow_portfolio_state.json')
if not SHADOW_PATH.exists():
    SHADOW_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/shadow_portfolio_state.json')

def run_audit():
    print("=== AUDITING MORNING MEETING (09:30 Rome / 08:30 UTC) ===")
    
    # 1. Inspect executions.db for master_debate_daily
    executions = []
    if DB_PATH.exists():
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, job_id, source, status, claimed_at, started_at, finished_at, error 
                FROM executions 
                WHERE job_id = 'master_debate_daily'
                ORDER BY claimed_at DESC
            """)
            executions = cursor.fetchall()
            conn.close()
        except Exception as e:
            print("DB error:", e)
            
    print(f"Executions in DB for master_debate_daily: {len(executions)}")
    for ex in executions:
        print("EX ROW:", ex)
        
    # 2. Inspect debate run state
    run_state = {}
    if STATE_PATH.exists():
        try:
            run_state = json.loads(STATE_PATH.read_text(encoding='utf-8'))
        except Exception as e:
            print("State read error:", e)
    print("Debate Run State:", json.dumps(run_state, indent=2))
    
    # 3. Inspect historical archive for morning session
    history = []
    if ARCHIVE_PATH.exists():
        try:
            history = json.loads(ARCHIVE_PATH.read_text(encoding='utf-8'))
        except Exception:
            pass
            
    morning_records = [h for h in history if h.get("meeting_type") == "morning" or "MORNING" in h.get("session_id", "")]
    print(f"Morning records in archive: {len(morning_records)}")
    for r in morning_records:
        print("RECORD:", r.get("session_id"), r.get("timestamp_utc"), r.get("local_time_rome"), r.get("trading_director_conclusion"))
        
    # 4. Inspect shadow portfolio ledger
    shadow = {}
    if SHADOW_PATH.exists():
        try:
            shadow = json.loads(SHADOW_PATH.read_text(encoding='utf-8'))
        except Exception:
            pass
    print("Shadow Ledger Entry Count:", len(shadow.get("ledger", [])))
    if shadow.get("ledger"):
        print("Latest Shadow Entry:", shadow.get("ledger")[0])

if __name__ == '__main__':
    run_audit()
