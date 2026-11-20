"""
Patches dashboard_backend.py to use dynamic committee_endpoints module.
"""
from pathlib import Path
import shutil

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
BACKUP_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py.bak_delegate_committee')

def patch_backend():
    shutil.copy2(BACKEND_PATH, BACKUP_PATH)
    print("Backup created at:", BACKUP_PATH)
    
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    # 1. Add import at the top
    if 'import committee_endpoints' not in code:
        code = "import committee_endpoints\n" + code
        
    # 2. Replace get_committee_latest and get_committee_history implementation to delegate
    old_method_start = '    def get_committee_latest(self):'
    old_method_end = '    def get_shadow_summary(self):'
    
    idx1 = code.find(old_method_start)
    idx2 = code.find(old_method_end)
    
    if idx1 != -1 and idx2 != -1:
        new_methods = """    def get_committee_latest(self):
        return committee_endpoints.get_committee_latest()

    def get_committee_history(self):
        return committee_endpoints.get_committee_history()

"""
        code = code[:idx1] + new_methods + code[idx2:]
        BACKEND_PATH.write_text(code, encoding='utf-8')
        print("Delegated get_committee_latest and get_committee_history to committee_endpoints successfully.")
    else:
        print("Error: Could not locate method bounds in dashboard_backend.py.")

if __name__ == '__main__':
    patch_backend()
