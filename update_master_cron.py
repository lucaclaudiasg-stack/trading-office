"""
Updates /opt/data/cron/jobs.json to match Section 13 of Master Directive.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

JOBS_PATH = Path('/opt/data/cron/jobs.json')

MASTER_JOBS = [
    {
        "id": "master_score_4h",
        "name": "Trading 4H Multi-Strategy Scoring (DATA_ONLY)",
        "schedule": "10 0,4,8,12,16,20 * * *",
        "command": "python3 -B /opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/master_directive_engine.py --mode score",
        "state": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "master_debate_daily",
        "name": "Trading Daily Multi-Agent Debate (DATA_ONLY)",
        "schedule": "30 20 * * *",
        "command": "python3 -B /opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/master_directive_engine.py --mode debate",
        "state": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "master_verify_daily",
        "name": "Trading Daily Forecast & Cost Verification (DATA_ONLY)",
        "schedule": "0 21 * * *",
        "command": "python3 -B /opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/master_directive_engine.py --mode verify",
        "state": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "master_report_weekly",
        "name": "Trading Weekly Quality & Economic Report (DATA_ONLY)",
        "schedule": "30 21 * * 0",
        "command": "python3 -B /opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/master_directive_engine.py --mode report",
        "state": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
]

def update_cron():
    data = {
        "jobs": MASTER_JOBS,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    JOBS_PATH.write_text(json.dumps(data, indent=2), encoding='utf-8')
    print("Master Directive Cron Jobs Successfully Registered in /opt/data/cron/jobs.json")

if __name__ == '__main__':
    update_cron()
