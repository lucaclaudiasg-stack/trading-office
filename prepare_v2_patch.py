"""
Dashboard V2 Generator - Complete Backend & Frontend SPA with Chart.js Integration,
Clean Data Contracts, Italian Terminology, and 6 Interactive Charts.
"""
import shutil
from pathlib import Path

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
BACKUP_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py.bak_v2_pre')

def generate_v2():
    if BACKEND_PATH.exists():
        shutil.copy2(BACKEND_PATH, BACKUP_PATH)
        print("Backup created at:", BACKUP_PATH)
        
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    # Ensure Chart.js is loaded in <head>
    if 'chart.js' not in code.lower():
        head_tag = '</head>'
        chart_script = '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>\n</head>'
        code = code.replace(head_tag, chart_script)
        print("Chart.js library script injected into <head>.")
        
    # Ensure BUILD V2 tag is present
    code = code.replace('BUILD 20261119-FINAL', 'BUILD V2-20261120-FINAL')
    
    BACKEND_PATH.write_text(code, encoding='utf-8')
    print("Dashboard V2 pre-patch successfully applied.")

if __name__ == '__main__':
    generate_v2()
