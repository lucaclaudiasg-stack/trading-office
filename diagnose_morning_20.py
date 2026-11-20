"""
Diagnostics script for 20/11/2026 morning meeting execution and archive consistency.
"""
import sqlite3
import json
from pathlib import Path

DB_PATH = Path('/opt/data/cron/executions.db')
if not DB_PATH.exists():
    DB_PATH = Path('/opt/data/state.db')

ARCHIVE_PATH = Path('/app/staging/historical_analysis_archive.json')
if not ARCHIVE_PATH.exists():
    ARCHIVE_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/historical_analysis_archive.json')

STATE_PATH = Path('/app/staging/debate_run_state.json')
if not STATE_PATH.exists():
    STATE_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/debate_run_state.json')

def diagnose():
    print("=== COMMITTEE DIAGNOSTICS (2026-11-20) ===")
    
    # 1. Check executions.db
    if DB_PATH.exists():
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, job_id, source, status, claimed_at, started_at, finished_at, error 
            FROM executions 
            WHERE job_id = 'master_debate_daily'
            ORDER BY claimed_at DESC
            LIMIT 5
        """)
        rows = cursor.fetchall()
        print(f"Recent executions for master_debate_daily ({len(rows)}):")
        for r in rows:
            print("  ", r)
        conn.close()
        
    # 2. Check debate run state
    if STATE_PATH.exists():
        print("Debate Run State:", STATE_PATH.read_text(encoding='utf-8'))
        
    # 3. Check historical archive
    if ARCHIVE_PATH.exists():
        records = json.loads(ARCHIVE_PATH.read_text(encoding='utf-8'))
        debates = [r for r in records if r.get('type') in ['REAL_AGENT_DEBATE', 'DAILY_DEBATE', '4H_OPPORTUNITY_SCORING'] or 'DEBATE' in r.get('session_id', '')]
        print(f"Total debate/scoring records in archive: {len(debates)}")
        for d in debates[-5:]:
            print("  Record:", d.get("session_id"), d.get("timestamp_utc"), d.get("type"), d.get("meeting_type"))

if __name__ == '__main__':
    diagnose()
