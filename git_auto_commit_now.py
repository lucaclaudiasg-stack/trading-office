"""
Auto-commits all latest backend and UI fixes to git repo and pushes to GitHub.
"""
import os
import subprocess
from pathlib import Path

WORKSPACE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(WORKSPACE))
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def auto_commit():
    print("=== GIT AUTO-COMMIT & PUSH ===")
    run_cmd("git add .")
    out_cm, err_cm, code_cm = run_cmd('git commit -m "fix(dashboard): resolve slow loading by implementing missing API handlers and dynamic committee parser"')
    print(f"Commit esito (code {code_cm}): {out_cm}")
    
    out_push, err_push, code_push = run_cmd("git push origin main")
    print(f"Push esito (code {code_push}): {out_push} {err_push}")

if __name__ == '__main__':
    auto_commit()
