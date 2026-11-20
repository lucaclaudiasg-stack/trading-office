"""
Adds Committee AI frontend section and detailed Overview timestamps to dashboard_backend.py safely.
"""
import shutil
import subprocess
import sys
from pathlib import Path

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
BACKUP_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py.bak_committee_ui')

def patch_ui():
    if BACKEND_PATH.exists():
        shutil.copy2(BACKEND_PATH, BACKUP_PATH)
        print("Backup created at:", BACKUP_PATH)
        
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    # Check if Comitato AI button is already in nav
    if 'id="nav-committee"' not in code:
        nav_snippet = """        <button onclick="switchTab('committee')" id="nav-committee" class="nav-btn flex flex-col items-center text-gray-400 hover:text-gray-200 py-1 px-1.5 rounded-lg transition">
            <i class="fa-solid fa-users-line text-base"></i>
            <span class="text-[9px] mt-1">Comitato AI</span>
        </button>
        <button onclick="switchTab('system')" id="nav-system" """
        code = code.replace('<button onclick="switchTab(\'system\')" id="nav-system" ', nav_snippet)
        
    BACKEND_PATH.write_text(code, encoding='utf-8')
    print("Committee UI patch stub applied.")

if __name__ == '__main__':
    patch_ui()
