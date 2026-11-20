"""
Removes sec-aggressive-lab-panel from the top of the simulation section in dashboard_backend.py
as requested by the user.
"""
import shutil
from pathlib import Path

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
BACKUP_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py.bak_remove_agg_panel')

def remove_panel():
    shutil.copy2(BACKEND_PATH, BACKUP_PATH)
    print("Backup created at:", BACKUP_PATH)
    
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    start_str = '<!-- SECTION: SIMULAZIONE -->'
    panel_str = '<!-- AGGRESSIVE LAB PANEL (V2) -->'
    next_sec_str = '<!-- GRAFICI SIMULAZIONE (V2) -->'
    
    idx_start = code.find(start_str)
    idx_next = code.find(next_sec_str)
    
    if idx_start != -1 and idx_next != -1:
        # Keep <!-- SECTION: SIMULAZIONE --> and jump directly to <!-- GRAFICI SIMULAZIONE (V2) -->
        new_block = '<!-- SECTION: SIMULAZIONE -->\n            '
        code = code[:idx_start] + new_block + code[idx_next:]
        BACKEND_PATH.write_text(code, encoding='utf-8')
        print("sec-aggressive-lab-panel successfully removed.")
    else:
        print("Error: Target anchors not found in dashboard_backend.py.")

if __name__ == '__main__':
    remove_panel()
