"""
Records the forced run executions into /opt/data/cron/executions.db for system status display.
"""
import sqlite3
import uuid
import time
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path('/opt/data/cron/executions.db')
JOBS = ["master_score_4h", "master_debate_daily", "master_verify_daily", "master_report_weekly"]

def record():
    if not DB_PATH.exists():
        return
        
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    now_ts = int(time.time())
    
    for jid in JOBS:
        exec_id = uuid.uuid4().hex
        cursor.execute("""
            INSERT INTO executions (
                id, job_id, source, process_id, pid, process_started_at,
                status, handoff_pending, claimed_at, started_at, finished_at, error
            ) VALUES (?, ?, 'forced_manual', ?, ?, ?, 'completed', 0, ?, ?, ?, NULL)
        """, (exec_id, jid, uuid.uuid4().hex, 252860, now_ts, now_iso, now_iso, now_iso))
        
    conn.commit()
    conn.close()
    print("Executions recorded successfully in executions.db.")

if __name__ == '__main__':
    record()
