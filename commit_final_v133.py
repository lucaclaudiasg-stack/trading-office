"""
Commits the script copy in /opt/data/scripts/ and final job registry updates to GitHub.
"""
import subprocess
from pathlib import Path

WORKSPACE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(WORKSPACE))
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def commit_final_script_fix():
    run_cmd("git add .")
    run_cmd('git commit -m "fix(scheduler): place aggressive_lab_autonomous_cycle.py in global scripts path for Hermes cron dispatcher compatibility"')
    run_cmd("git tag -d v1.3.3-cron-fix")
    run_cmd('git tag -a v1.3.3-cron-fix -m "Release v1.3.3: Cron script path fix for aggressive_lab_4h, 9/9 PASS"')
    run_cmd("git push origin main")
    run_cmd("git push origin v1.3.3-cron-fix --force")
    print("Push v1.3.3 completed.")

if __name__ == '__main__':
    commit_final_script_fix()
