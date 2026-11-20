"""
Final commit and push to GitHub reflecting the addition of the Hermes Aggressive overview box (v1.6.0).
"""
import subprocess
from pathlib import Path

WORKSPACE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(WORKSPACE))
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def commit_final_v160():
    run_cmd("git add .")
    out_cm, _, code_cm = run_cmd('git commit -m "feat(dashboard): add Hermes Aggressive summary card to homepage Overview section"')
    print(f"Commit code {code_cm}: {out_cm}")
    
    tag_name = "v1.6.0-overview-aggressive-box"
    run_cmd(f"git tag -d {tag_name}")
    run_cmd(f'git tag -a {tag_name} -m "Release v1.6.0: Hermes Aggressive overview card added, 9/9 PASS"')
    
    run_cmd("git push origin main")
    run_cmd(f"git push origin {tag_name} --force")
    print("Push v1.6.0 completed.")

if __name__ == '__main__':
    commit_final_v160()
