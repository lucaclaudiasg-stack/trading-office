"""
Checks SSH keys, git environment, and GitHub connectivity.
"""
import os
import subprocess
from pathlib import Path

WORKSPACE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(WORKSPACE))
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def check_env():
    print("=== CHECKING GITHUB CONNECTIVITY ===")
    
    # 1. Check SSH keys
    ssh_dir = Path.home() / ".ssh"
    if ssh_dir.exists():
        keys = list(ssh_dir.glob("*"))
        print("SSH keys found in ~/.ssh:", [k.name for k in keys])
        
        # Test SSH connection to GitHub
        out, err, code = run_cmd("ssh -T -o StrictHostKeyChecking=no git@github.com")
        print(f"SSH test to GitHub (code {code}):\n{out}\n{err}")
    else:
        print("No ~/.ssh directory found.")
        
    # 2. Check tokens in env
    gh_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if gh_token:
        print(f"GitHub token present in env: {gh_token[:4]}... (len {len(gh_token)})")
    else:
        print("No GITHUB_TOKEN or GH_TOKEN found in environment.")

if __name__ == '__main__':
    check_env()
