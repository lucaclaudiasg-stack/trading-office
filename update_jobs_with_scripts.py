"""
Updates /opt/data/cron/jobs.json to use native Hermes script fields pointing to /opt/data/scripts/ wrappers.
"""
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone
import sys

sys.path.insert(0, '/opt/hermes')
from cron.jobs import compute_next_run

JOBS_PATH = Path('/opt/data/cron/jobs.json')
BACKUP_PATH = Path('/opt/data/cron/jobs.json.bak_20261119_script_fix')

JOB_CONFIGS = [
    {
        "id": "master_score_4h",
        "name": "Trading 4H Multi-Strategy Scoring (DATA_ONLY)",
        "script": "master_score_4h_runner.py",
        "expr": "10 0,4,8,12,16,20 * * *",
        "display": "Ogni 4 ore (Europe/Rome)"
    },
    {
        "id": "master_debate_daily",
        "name": "Trading Twice-Daily Zone-Aware Debate (09:30 & 21:30 Rome)",
        "script": "zone_aware_debate_runner.py",
        "expr": "30 9,21 * * *",
        "display": "Biorario: 09:30 & 21:30 (Europe/Rome)"
    },
    {
        "id": "master_verify_daily",
        "name": "Trading Daily Forecast & Cost Verification (DATA_ONLY)",
        "script": "master_verify_daily_runner.py",
        "expr": "0 21 * * *",
        "display": "Giornaliero: 21:00 (Europe/Rome)"
    },
    {
        "id": "master_report_weekly",
        "name": "Trading Weekly Quality & Economic Report (DATA_ONLY)",
        "script": "master_report_weekly_runner.py",
        "expr": "30 21 * * 0",
        "display": "Settimanale: Domenica 21:30 (Europe/Rome)"
    }
]

def update_jobs():
    if JOBS_PATH.exists():
        shutil.copy2(JOBS_PATH, BACKUP_PATH)
        print(f"Backup created at {BACKUP_PATH}")
        
    data = {"jobs": [], "updated_at": datetime.now(timezone.utc).isoformat()}
    
    for cfg in JOB_CONFIGS:
        sched_dict = {
            "kind": "cron",
            "expr": cfg["expr"],
            "display": cfg["display"]
        }
        next_run = compute_next_run(sched_dict, timezone="Europe/Rome")
        
        job_rec = {
            "id": cfg["id"],
            "name": cfg["name"],
            "prompt": "",
            "skills": [],
            "skill": None,
            "script": cfg["script"],
            "no_agent": True,
            "schedule": sched_dict,
            "schedule_display": cfg["display"],
            "timezone": "Europe/Rome",
            "state": "active",
            "enabled": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "next_run_at": str(next_run) if next_run else None
        }
        data["jobs"].append(job_rec)
        print(f"Job {cfg['id']} updated with script={cfg['script']}, next_run_at={job_rec['next_run_at']}")
        
    JOBS_PATH.parent.mkdir(parents=True, exist_ok=True)
    JOBS_PATH.write_text(json.dumps(data, indent=2), encoding='utf-8')
    print("jobs.json updated successfully with native Hermes script fields.")

if __name__ == '__main__':
    update_jobs()
