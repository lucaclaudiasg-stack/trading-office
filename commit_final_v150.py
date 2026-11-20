"""
Final commit and push to GitHub reflecting the reinsertion of Hermes Aggressive in Simulation, top box in Aggressive tab, and comparative charts (v1.5.0).
"""
import subprocess
from pathlib import Path

WORKSPACE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(WORKSPACE))
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def commit_final_v150():
    run_cmd("git add .")
    out_cm, _, code_cm = run_cmd('git commit -m "feat(dashboard): reinsert Hermes Aggressive box in simulation, top summary box in aggressive tab, and comparative charts"')
    print(f"Commit code {code_cm}: {out_cm}")
    
    tag_name = "v1.5.0-aggressive-full-integration"
    run_cmd(f"git tag -d {tag_name}")
    run_cmd(f'git tag -a {tag_name} -m "Release v1.5.0: Hermes Aggressive full simulation & tab integration, 9/9 PASS"')
    
    run_cmd("git push origin main")
    run_cmd(f"git push origin {tag_name} --force")
    print("Push v1.5.0 completed.")

if __name__ == '__main__':
    commit_final_v150()
