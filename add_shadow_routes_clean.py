"""
Ensures shadow summary and ledger endpoints are correctly routed in DashboardHandler.do_GET.
"""
from pathlib import Path
import shutil

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')

def add_routes():
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    if "self.path == '/api/shadow/summary'" not in code:
        target = "elif self.path == '/api/history':"
        snippet = """        elif self.path == '/api/history':
            self.send_json(self.get_history_data())
        elif self.path == '/api/shadow/summary':
            self.send_json(self.get_shadow_summary())
        elif self.path == '/api/shadow/ledger':
            self.send_json(self.get_shadow_ledger())"""
        code = code.replace(target, snippet)
        BACKEND_PATH.write_text(code, encoding='utf-8')
        print("Shadow routes added successfully.")
    else:
        print("Shadow routes already present.")

if __name__ == '__main__':
    add_routes()
