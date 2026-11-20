"""
Patches dashboard_backend.py to integrate Shadow Trading endpoints and frontend UI.
"""
import re
from pathlib import Path

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
SHADOW_STATE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/shadow_portfolio_state.json')

def patch_backend():
    content = BACKEND_PATH.read_text(encoding='utf-8')
    
    # 1. Add shadow data methods to DashboardHandler if not present
    if "def get_shadow_summary" not in content:
        shadow_methods = """
    def get_shadow_summary(self):
        if SHADOW_STATE.exists():
            try:
                return json.loads(SHADOW_STATE.read_text(encoding='utf-8'))
            except Exception:
                pass
        return {"status": "NOT_INITIALIZED"}

    def get_shadow_ledger(self):
        if SHADOW_STATE.exists():
            try:
                data = json.loads(SHADOW_STATE.read_text(encoding='utf-8'))
                return {"ledger": data.get("ledger", [])}
            except Exception:
                pass
        return {"ledger": []}
"""
        # Insert before SPA_HTML definition
        content = content.replace("SPA_HTML = ", shadow_methods + "\n\nSPA_HTML = ")
        
    # 2. Add routing in do_GET
    if "self.path == '/api/shadow/summary'" not in content:
        routing_code = """
        elif self.path == '/api/shadow/summary':
            self.send_json(self.get_shadow_summary())
        elif self.path == '/api/shadow/ledger':
            self.send_json(self.get_shadow_ledger())"""
        content = content.replace("elif self.path == '/api/system':", routing_code + "\n        elif self.path == '/api/system':")
        
    BACKEND_PATH.write_text(content, encoding='utf-8')
    print("Backend patched with shadow endpoints.")

if __name__ == '__main__':
    patch_backend()
