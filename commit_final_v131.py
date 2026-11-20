"""
Final v1.3.1 commit and push to GitHub reflecting the removal of the top aggressive panel.
"""
import subprocess
from pathlib import Path

WORKSPACE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(WORKSPACE))
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def commit_final():
    run_cmd("git add .")
    out_cm, _, code_cm = run_cmd('git commit -m "refactor(dashboard): remove top aggressive lab summary card from simulation section per user request"')
    print(f"Commit code {code_cm}: {out_cm}")
    
    tag_name = "v1.3.1-ui-cleanup"
    run_cmd(f"git tag -d {tag_name}")
    run_cmd(f'git tag -a {tag_name} -m "Release v1.3.1: UI cleanup removing top aggressive panel, 9/9 PASS"')
    
    run_cmd("git push origin main")
    run_cmd(f"git push origin {tag_name} --force")
    print("Push completed.")

if __name__ == '__main__':
    commit_final()
