"""
Adds the aggressive_lab_4h cron job definition to /opt/data/cron/jobs.json
so it is natively displayed in the dashboard System tab.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

JOBS_PATH = Path('/opt/data/cron/jobs.json')

def add_job():
    if not JOBS_PATH.exists():
        print("jobs.json not found.")
        return
        
    data = json.loads(JOBS_PATH.read_text(encoding='utf-8'))
    jobs = data.get("jobs", []) if isinstance(data, dict) else data
    
    # Check if aggressive_lab_4h already exists
    exists = any(j.get("id") == "aggressive_lab_4h" for j in jobs)
    if exists:
        print("aggressive_lab_4h job already exists in registry.")
        return
        
    new_job = {
        "id": "aggressive_lab_4h",
        "name": "Aggressive Lab Autonomous 4H Trading Cycle (SIMULATION_ONLY)",
        "prompt": "",
        "skills": [],
        "skill": None,
        "script": "aggressive_lab_autonomous_cycle.py",
        "no_agent": True,
        "schedule": {
            "kind": "cron",
            "expr": "0 */4 * * *",
            "display": "Ogni 4 ore (Europe/Rome)"
        },
        "schedule_display": "Ogni 4 ore (Europe/Rome)",
        "timezone": "Europe/Rome",
        "state": "scheduled",
        "enabled": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "next_run_at": "2026-11-21T04:00:00+01:00",
        "last_status": "ok",
        "failure_streak": 0
    }
    
    jobs.append(new_job)
    if isinstance(data, dict):
        data["jobs"] = jobs
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
    else:
        data = jobs
        
    JOBS_PATH.write_text(json.dumps(data, indent=2), encoding='utf-8')
    print("aggressive_lab_4h successfully added to jobs.json registry.")

if __name__ == '__main__':
    add_job()
