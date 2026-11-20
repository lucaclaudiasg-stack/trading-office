"""
Forces the sequential execution of all 4 master consultation jobs right now.
Operates strictly in DATA_ONLY mode.
"""
import subprocess
import sys
import json
from pathlib import Path

JOBS = [
    ("master_score_4h", "python3 -B /opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/master_directive_engine.py --mode score"),
    ("master_debate_daily", "python3 -B /opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/master_directive_engine.py --mode debate"),
    ("master_verify_daily", "python3 -B /opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/master_directive_engine.py --mode verify"),
    ("master_report_weekly", "python3 -B /opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/master_directive_engine.py --mode report")
]

def force_run():
    results = []
    for jid, cmd in JOBS:
        print(f"\n--- FORCING EXECUTION: {jid} ---")
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            print("Exit code:", res.returncode)
            print("Stdout:", res.stdout.strip())
            if res.stderr:
                print("Stderr:", res.stderr.strip())
            results.append({
                "job_id": jid,
                "exit_code": res.returncode,
                "success": res.returncode == 0
            })
        except Exception as e:
            print(f"Error running {jid}: {e}")
            results.append({
                "job_id": jid,
                "exit_code": -1,
                "success": False,
                "error": str(e)
            })
            
    print("\n=== ALL JOBS FORCED EXECUTION COMPLETE ===")
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    force_run()
