"""
Auto-commits all Dashboard V2 files and pushes to GitHub.
"""
import subprocess
from pathlib import Path

WORKSPACE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(WORKSPACE))
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def commit_and_push_v2():
    print("=== COMMITTING & PUSHING DASHBOARD V2 ===")
    run_cmd("git add .")
    out_cm, _, code_cm = run_cmd('git commit -m "feat(dashboard): release Dashboard V2 with Chart.js analytics, UI redesign, and independent multi-agent certification"')
    print(f"Commit code {code_cm}: {out_cm}")
    
    out_push, err_push, code_push = run_cmd("git push origin main")
    print(f"Push code {code_push}: {out_push} {err_push}")

if __name__ == '__main__':
    commit_and_push_v2()
