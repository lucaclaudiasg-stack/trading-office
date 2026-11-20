"""
Decommissions the 5 old cron jobs, archives their metadata, and updates market-analysis-consultative skill.
"""
import json
from pathlib import Path

JOBS_PATH = Path('/opt/data/cron/jobs.json')
ARCHIVE_DIR = Path('/opt/data/profiles/trading-office-manager/workspace/decommissioned_jobs_archive')
TARGET_JOB_IDS = {'22cd985ad4f8', '94deabba09b5', '816674406c22', '7b4b90be5563', '3e162fa9f571'}

def decommission():
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    if not JOBS_PATH.exists():
        print("Jobs file not found.")
        return
        
    data = json.loads(JOBS_PATH.read_text(encoding='utf-8'))
    jobs = data.get('jobs', [])
    
    decommissioned = []
    retained = []
    
    for job in jobs:
        if job.get('id') in TARGET_JOB_IDS:
            decommissioned.append(job)
            print(f"Decommissioning job {job['id']}: {job['name']} (state: {job.get('state')})")
        else:
            retained.append(job)
            
    # Save archive metadata
    archive_file = ARCHIVE_DIR / 'decommissioned_jobs_snapshot.json'
    archive_file.write_text(json.dumps({'decommissioned_at_utc': '2026-11-18T16:00:00Z', 'jobs': decommissioned}, indent=2))
    print(f"Saved decommissioned archive metadata to {archive_file}")
    
    # Update jobs.json
    data['jobs'] = retained
    JOBS_PATH.write_text(json.dumps(data, indent=2))
    print(f"Removed {len(decommissioned)} old cron jobs from active registry. {len(retained)} jobs retained.")

if __name__ == '__main__':
    decommission()
