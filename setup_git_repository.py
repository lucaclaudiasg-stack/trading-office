"""
Initializes Git repo in workspace, sets git user identity, creates .gitignore, and commits all files.
"""
import subprocess
from pathlib import Path

WORKSPACE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(WORKSPACE))
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def setup_repo():
    print("=== INITIALIZING GIT REPOSITORY ===")
    
    # 1. git init
    out, err, code = run_cmd("git init -b main")
    print(f"git init: code {code}, {out} {err}")
    
    # 2. git config
    run_cmd("git config user.name 'Trading Office Manager'")
    run_cmd("git config user.email 'trading-office-manager@hermes.local'")
    
    # 3. create .gitignore
    gitignore = WORKSPACE / ".gitignore"
    gitignore_content = """__pycache__/
*.pyc
*.pyo
cache/
scratch/
*.bak*
.DS_Store
"""
    gitignore.write_text(gitignore_content, encoding='utf-8')
    print("Created .gitignore")
    
    # 4. git add
    out_add, err_add, code_add = run_cmd("git add .")
    print(f"git add: code {code_add}, {out_add} {err_add}")
    
    # 5. git commit
    out_cm, err_cm, code_cm = run_cmd('git commit -m "feat: initialize trading-office project codebase with multi-asset suite & dashboard"')
    print(f"git commit: code {code_cm}, {out_cm}")
    
    # 6. check status
    out_st, err_st, _ = run_cmd("git status")
    print(f"Git status post commit:\n{out_st}")

if __name__ == '__main__':
    setup_repo()
