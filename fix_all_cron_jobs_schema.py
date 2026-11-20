"""
Fixes schema for all 4 master jobs in /opt/data/cron/jobs.json according to native Hermes cron schema.
Includes backup and next_run_at calculation.
"""
import json
import shutil
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, '/opt/hermes')
from cron.jobs import compute_next_run

JOBS_PATH = Path('/opt/data/cron/jobs.json')
BACKUP_PATH = Path('/opt/data/cron/jobs.json.bak_20261119')

CONFIGS = {
    "master_score_4h": {
        "expr": "10 0,4,8,12,16,20 * * *",
        "display": "10 0,4,8,12,16,20 * * *",
        "command": "python3 -B /opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/master_directive_engine.py --mode score"
    },
    "master_debate_daily": {
        "expr": "30 9,21 * * *",
        "display": "30 9,21 * * *",
        "command": "python3 -B /opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/zone_aware_debate_wrapper.py --mode check"
    },
    "master_verify_daily": {
        "expr": "0 21 * * *",
        "display": "0 21 * * *",
        "command": "python3 -B /opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/master_directive_engine.py --mode verify"
    },
    "master_report_weekly": {
        "expr": "30 21 * * 0",
        "display": "30 21 * * 0",
        "command": "python3 -B /opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/master_directive_engine.py --mode report"
    }
}

def fix_all():
    if not JOBS_PATH.exists():
        print("jobs.json not found.")
        return
        
    # 1. Backup
    shutil.copy2(JOBS_PATH, BACKUP_PATH)
    print(f"Backup created at {BACKUP_PATH}")
    
    data = json.loads(JOBS_PATH.read_text(encoding='utf-8'))
    
    for j in data.get("jobs", []):
        jid = j.get("id")
        if jid in CONFIGS:
            cfg = CONFIGS[jid]
            sched_dict = {
                "kind": "cron",
                "expr": cfg["expr"],
                "display": cfg["display"]
            }
            j["schedule"] = sched_dict
            j["schedule_display"] = cfg["display"]
            j["timezone"] = "Europe/Rome"
            j["command"] = cfg["command"]
            j["state"] = "active"
            j["enabled"] = True
            
            # Compute next run
            next_run = compute_next_run(sched_dict, timezone="Europe/Rome")
            j["next_run_at"] = str(next_run) if next_run else None
            print(f"Job {jid}: expr='{cfg['expr']}', next_run_at={j['next_run_at']}")
            
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    JOBS_PATH.write_text(json.dumps(data, indent=2), encoding='utf-8')
    print("Schema fix applied successfully to jobs.json.")

if __name__ == '__main__':
    fix_all()
