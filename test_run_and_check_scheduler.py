"""
Inspects aggressive_lab_4h schedule in jobs.json and executes a test run of aggressive_lab_autonomous_cycle.py.
"""
import json
import subprocess
from pathlib import Path

JOBS_PATH = Path('/opt/data/cron/jobs.json')
WORKSPACE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')
STATE_PATH = WORKSPACE / 'aggressive_portfolio_state.json'

def check_and_test():
    print("=== INSPECTING AGGRESSIVE LAB SCHEDULING ===")
    if JOBS_PATH.exists():
        data = json.loads(JOBS_PATH.read_text(encoding='utf-8'))
        jobs = data.get("jobs", []) if isinstance(data, dict) else data
        agg_job = next((j for j in jobs if j.get("id") == "aggressive_lab_4h"), None)
        if agg_job:
            print("Found aggressive_lab_4h job in registry:")
            print(json.dumps(agg_job, indent=2))
        else:
            print("WARNING: aggressive_lab_4h job NOT found in jobs.json.")
            
    print("\n=== EXECUTING TEST RUN OF AGGRESSIVE LAB ===")
    res = subprocess.run(
        ["python3", "-B", str(WORKSPACE / "aggressive_lab_autonomous_cycle.py")],
        capture_output=True, text=True, cwd=str(WORKSPACE)
    )
    print(f"Test run exit code: {res.returncode}")
    print("STDOUT:\n", res.stdout)
    if res.stderr:
        print("STDERR:\n", res.stderr)
        
    if STATE_PATH.exists():
        state_data = json.loads(STATE_PATH.read_text(encoding='utf-8'))
        print("\nUpdated Aggressive State (last cycle):")
        print(json.dumps(state_data.get("last_cycle"), indent=2))

if __name__ == '__main__':
    check_and_test()
