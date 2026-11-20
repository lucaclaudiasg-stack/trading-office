"""
Checks git status, gh CLI auth, and git remote configuration in the workspace.
"""
import subprocess

WORKSPACE = '/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e'

def run_cmd(cmd, cwd=WORKSPACE):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def check_status():
    print("=== GIT & GH CLI CHECK ===")
    out, err, code = run_cmd("git status")
    print(f"Git status (code {code}):\n{out}\n{err}")
    
    out_remote, err_remote, code_remote = run_cmd("git remote -v")
    print(f"Git remote:\n{out_remote}")
    
    out_gh, err_gh, code_gh = run_cmd("gh auth status")
    print(f"GH Auth status:\n{out_gh}\n{err_gh}")

if __name__ == '__main__':
    check_status()
