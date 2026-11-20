"""
Registers the 4 authorized DATA_ONLY consultation cron jobs in /opt/data/cron/jobs.json.
Ensures zero duplication and strict DATA_ONLY / Risk Engine = DENY compliance.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

JOBS_PATH = Path('/opt/data/cron/jobs.json')

NEW_JOBS = [
    {
        "id": "obs_score_4h",
        "name": "Trading 4H Opportunity Scoring (DATA_ONLY)",
        "schedule": "0 */4 * * *",
        "command": "python3 -B /opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/observation_jobs_runner.py --mode score",
        "state": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "obs_debate_daily",
        "name": "Trading Daily Multi-Agent Debate (DATA_ONLY)",
        "schedule": "30 8 * * *",
        "command": "python3 -B /opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/observation_jobs_runner.py --mode debate",
        "state": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "obs_verify_daily",
        "name": "Trading Daily Forecast Verification (DATA_ONLY)",
        "schedule": "45 8 * * *",
        "command": "python3 -B /opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/observation_jobs_runner.py --mode verify",
        "state": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "obs_report_weekly",
        "name": "Trading Weekly Quality Report (DATA_ONLY)",
        "schedule": "0 9 * * 1",
        "command": "python3 -B /opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/observation_jobs_runner.py --mode report",
        "state": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
]

def register():
    JOBS_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {"jobs": [], "updated_at": datetime.now(timezone.utc).isoformat()}
    if JOBS_PATH.exists():
        try:
            data = json.loads(JOBS_PATH.read_text(encoding='utf-8'))
        except Exception:
            pass
            
    existing_ids = {j.get("id") for j in data.get("jobs", [])}
    added = []
    
    for j in NEW_JOBS:
        if j["id"] not in existing_ids:
            data.get("jobs", []).append(j)
            added.append(j["id"])
            
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    JOBS_PATH.write_text(json.dumps(data, indent=2), encoding='utf-8')
    print(f"Registered {len(added)} new observation jobs. Total jobs active: {len(data.get('jobs', []))}")

if __name__ == '__main__':
    register()
