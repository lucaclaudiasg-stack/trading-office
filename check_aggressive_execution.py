"""
Queries executions.db for aggressive_lab_4h execution history and checks jobs.json status.
"""
import sqlite3
import json
from pathlib import Path

DB_PATH = Path('/opt/data/cron/executions.db')
if not DB_PATH.exists():
    DB_PATH = Path('/opt/data/state.db')

JOBS_PATH = Path('/opt/data/cron/jobs.json')

def check_exec():
    print("=== AGGRESSIVE JOB EXECUTION AUDIT ===")
    if JOBS_PATH.exists():
        data = json.loads(JOBS_PATH.read_text(encoding='utf-8'))
        jobs = data.get("jobs", []) if isinstance(data, dict) else data
        j = next((x for x in jobs if x.get("id") == "aggressive_lab_4h"), None)
        print("Jobs.json entry:", json.dumps(j, indent=2))
        
    if DB_PATH.exists():
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute("""
            SELECT id, job_id, source, status, claimed_at, started_at, finished_at, error 
            FROM executions 
            WHERE job_id = 'aggressive_lab_4h'
            ORDER BY claimed_at DESC
            LIMIT 5
        """)
        rows = c.fetchall()
        print(f"\nExecutions in DB for aggressive_lab_4h ({len(rows)}):")
        for r in rows:
            print("  ", r)
        conn.close()

if __name__ == '__main__':
    check_exec()
