"""
Sanitizes push_to_github.py script on disk to remove raw credentials.
"""
from pathlib import Path

script_path = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/push_to_github.py')
if script_path.exists():
    code = script_path.read_text(encoding='utf-8')
    if "ghp_" in code:
        code_clean = ""
        for line in code.splitlines():
            if 'TOKEN = "ghp_' in line:
                code_clean += 'TOKEN = os.environ.get("GITHUB_TOKEN", "REDACTED")\n'
            else:
                code_clean += line + '\n'
        script_path.write_text(code_clean, encoding='utf-8')
        print("Script push_to_github.py sanitized successfully.")
