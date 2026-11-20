"""
Fixes schedule fields in /opt/data/cron/jobs.json to be clear human-readable strings.
"""
import json
from pathlib import Path

JOBS_PATH = Path('/opt/data/cron/jobs.json')

SCHEDULES = {
    "master_score_4h": "Ogni 4 ore (00:10, 04:10, 08:10, 12:10, 16:10, 20:10 UTC)",
    "master_debate_daily": "Giornaliero alle 20:30 UTC",
    "master_verify_daily": "Giornaliero alle 21:00 UTC",
    "master_report_weekly": "Domenica alle 21:30 UTC"
}

def fix():
    if not JOBS_PATH.exists():
        return
    data = json.loads(JOBS_PATH.read_text(encoding='utf-8'))
    for j in data.get("jobs", []):
        jid = j.get("id")
        if jid in SCHEDULES:
            j["schedule"] = SCHEDULES[jid]
            
    JOBS_PATH.write_text(json.dumps(data, indent=2), encoding='utf-8')
    print("Jobs schedule fixed in jobs.json.")

if __name__ == '__main__':
    fix()
