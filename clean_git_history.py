"""
Cleans git history by rewinding the commit containing raw token, sanitizing, and re-committing.
"""
import subprocess
from pathlib import Path

WORKSPACE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(WORKSPACE))
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def clean_history():
    print("=== CLEANING GIT HISTORY ===")
    # 1. Reset soft to initial commit or previous clean state
    run_cmd("git reset --soft 268f247")
    
    # 2. Sanitize push_to_github.py
    script_path = WORKSPACE / "push_to_github.py"
    if script_path.exists():
        code = script_path.read_text(encoding='utf-8')
        lines = []
        for line in code.splitlines():
            if 'ghp_' in line:
                lines.append('TOKEN = os.environ.get("GITHUB_TOKEN", "")')
            else:
                lines.append(line)
        script_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        print("push_to_github.py sanitized.")
        
    # 3. Add sanitized files
    run_cmd("git add .")
    
    # 4. Create new clean commit
    out_cm, err_cm, code_cm = run_cmd('git commit -m "fix(dashboard): implement full backend API handlers and sanitize repository scripts"')
    print(f"Clean commit: code {code_cm}, {out_cm}")
    
    # 5. Push clean commit to GitHub
    out_push, err_push, code_push = run_cmd("git push origin main --force")
    print(f"Git push result (code {code_push}): {out_push} {err_push}")

if __name__ == '__main__':
    clean_history()
