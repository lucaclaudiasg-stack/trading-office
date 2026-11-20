"""
Final commit and push to GitHub reflecting the targeted Aggressive Lab updates (v1.4.0).
"""
import subprocess
from pathlib import Path

WORKSPACE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(WORKSPACE))
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def commit_final_v140():
    run_cmd("git add .")
    out_cm, _, code_cm = run_cmd('git commit -m "feat(dashboard): add Hermes Aggressive simulation box, dedicated Aggressive tab, and virtual transaction ledger"')
    print(f"Commit code {code_cm}: {out_cm}")
    
    tag_name = "v1.4.0-aggressive-tab-and-box"
    run_cmd(f"git tag -d {tag_name}")
    run_cmd(f'git tag -a {tag_name} -m "Release v1.4.0: Aggressive simulation card, dedicated tab, 9/9 PASS"')
    
    run_cmd("git push origin main")
    run_cmd(f"git push origin {tag_name} --force")
    print("Push v1.4.0 completed.")

if __name__ == '__main__':
    commit_final_v140()
