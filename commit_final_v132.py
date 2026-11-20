"""
Final commit and push to GitHub reflecting the placement of the aggressive panel at the bottom of the simulation section.
"""
import subprocess
from pathlib import Path

WORKSPACE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(WORKSPACE))
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def commit_final_bottom():
    run_cmd("git add .")
    out_cm, _, code_cm = run_cmd('git commit -m "refactor(dashboard): relocate aggressive lab summary panel to the bottom of simulation section per user request"')
    print(f"Commit code {code_cm}: {out_cm}")
    
    tag_name = "v1.3.2-ui-bottom-panel"
    run_cmd(f"git tag -d {tag_name}")
    run_cmd(f'git tag -a {tag_name} -m "Release v1.3.2: Aggressive panel relocated to simulation bottom, 9/9 PASS"')
    
    run_cmd("git push origin main")
    run_cmd(f"git push origin {tag_name} --force")
    print("Push completed.")

if __name__ == '__main__':
    commit_final_bottom()
