"""
Adds committee_endpoints import and route handlers to dashboard_backend.py cleanly.
"""
from pathlib import Path
import subprocess
import sys

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')

def add_routes():
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    if "import committee_endpoints" not in code:
        code = "import committee_endpoints\n" + code
        
    if "self.path == '/api/committee/latest'" not in code:
        route_snippet = """        elif self.path == '/api/committee/latest':
            self.send_json(committee_endpoints.get_committee_latest())
        elif self.path == '/api/committee/history':
            self.send_json(committee_endpoints.get_committee_history())"""
        code = code.replace("elif self.path == '/api/system':", route_snippet + "\n        elif self.path == '/api/system':")
        
    BACKEND_PATH.write_text(code, encoding='utf-8')
    print("Routes added successfully to dashboard_backend.py.")

if __name__ == '__main__':
    add_routes()
