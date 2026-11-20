"""
Integrates committee_endpoints.py into dashboard_backend.py and updates SPA HTML.
"""
import shutil
from pathlib import Path

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
BACKUP_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py.bak_modulared_20261119')

def integrate():
    if BACKEND_PATH.exists():
        shutil.copy2(BACKEND_PATH, BACKUP_PATH)
        print("Backup created at:", BACKUP_PATH)
        
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    # 1. Add import committee_endpoints
    if "import committee_endpoints" not in code:
        code = "import committee_endpoints\n" + code
        
    # 2. Add routing in do_GET
    if "self.path == '/api/committee/latest'" not in code:
        routing = """        elif self.path == '/api/committee/latest':
            self.send_json(committee_endpoints.get_committee_latest())
        elif self.path == '/api/committee/history':
            self.send_json(committee_endpoints.get_committee_history())"""
        code = code.replace("elif self.path == '/api/system':", routing + "\n        elif self.path == '/api/system':")
        
    BACKEND_PATH.write_text(code, encoding='utf-8')
    print("dashboard_backend.py successfully integrated with committee_endpoints module.")

if __name__ == '__main__':
    integrate()
