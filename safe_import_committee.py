"""
Safely adds committee_endpoints import and route dispatching to dashboard_backend.py
without modifying class method indentations.
"""
import shutil
import subprocess
import sys
from pathlib import Path

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
BACKUP_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py.bak_safe_20261119')

def apply_safe_patch():
    if BACKEND_PATH.exists():
        shutil.copy2(BACKEND_PATH, BACKUP_PATH)
        print("Backup created at:", BACKUP_PATH)
        
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    # 1. Add import committee_endpoints at top
    if "import committee_endpoints" not in code:
        code = "import committee_endpoints\n" + code
        
    # 2. Add routing right at the start of do_GET
    if "self.path == '/api/committee/latest'" not in code:
        doget_target = "def do_GET(self):"
        routing_snippet = """    def do_GET(self):
        if self.path == '/api/committee/latest':
            self.send_json(committee_endpoints.get_committee_latest())
            return
        elif self.path == '/api/committee/history':
            self.send_json(committee_endpoints.get_committee_history())
            return"""
        code = code.replace(doget_target, routing_snippet)
        
    BACKEND_PATH.write_text(code, encoding='utf-8')
    print("Safe patch applied.")

if __name__ == '__main__':
    apply_safe_patch()
