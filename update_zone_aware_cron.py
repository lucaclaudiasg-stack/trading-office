"""
Updates master_debate_daily job in /opt/data/cron/jobs.json to use zone_aware_debate_wrapper.py --mode check
running hourly, handling Europe/Rome CET/CEST automatic time zones.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

JOBS_PATH = Path('/opt/data/cron/jobs.json')

def update():
    if not JOBS_PATH.exists():
        return
    data = json.loads(JOBS_PATH.read_text(encoding='utf-8'))
    
    for j in data.get("jobs", []):
        if j.get("id") == "master_debate_daily":
            j["name"] = "Trading Twice-Daily Zone-Aware Debate (09:30 & 21:30 Rome)"
            j["schedule"] = "0 * * * *" # Hourly check, wrapper handles Rome 09:30 & 21:30 exactly
            j["command"] = "python3 -B /opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/zone_aware_debate_wrapper.py --mode check"
            j["state"] = "active"
            
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    JOBS_PATH.write_text(json.dumps(data, indent=2), encoding='utf-8')
    print("master_debate_daily updated to use zone_aware_debate_wrapper.py successfully.")

if __name__ == '__main__':
    update()
