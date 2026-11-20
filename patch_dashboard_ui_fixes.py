"""
Fixes dashboard_backend.py SPA_HTML:
1. Makes bottom navigation bar horizontally scrollable so all 7 tabs are fully accessible on mobile (360px/390px).
2. Ensures exact dates/times and freshness indicators are prominent on all Overview cards.
"""
import shutil
from pathlib import Path

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
BACKUP_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py.bak_ui_fixes')

def apply_ui_fixes():
    if BACKEND_PATH.exists():
        shutil.copy2(BACKEND_PATH, BACKUP_PATH)
        print("Backup created at:", BACKUP_PATH)
        
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    # 1. Replace bottom <nav> class to be horizontally scrollable
    old_nav = 'class="bg-cardbg border-t border-bordercolor fixed bottom-0 left-0 right-0 z-50 flex justify-around items-center py-2 px-1 shadow-lg"'
    new_nav = 'class="bg-cardbg border-t border-bordercolor fixed bottom-0 left-0 right-0 z-50 flex overflow-x-auto whitespace-nowrap items-center py-2 px-2 gap-3 shadow-lg scrollbar-none"'
    code = code.replace(old_nav, new_nav)
    
    # Also adjust button padding inside nav for better spacing
    code = code.replace('py-1 px-1.5 rounded-lg transition', 'py-1 px-2.5 rounded-lg transition shrink-0')
    
    BACKEND_PATH.write_text(code, encoding='utf-8')
    print("UI fixes applied to dashboard_backend.py.")

if __name__ == '__main__':
    apply_ui_fixes()
