"""
Checks existence and permissions of /opt/data/scripts/aggressive_lab_autonomous_cycle.py
"""
from pathlib import Path

script_p = Path('/opt/data/scripts/aggressive_lab_autonomous_cycle.py')
print("Exists:", script_p.exists())
if script_p.exists():
    print("Size:", script_p.stat().st_size)
    print("Content preview:", script_p.read_text(encoding='utf-8')[:100])
else:
    # Copy from workspace if missing
    src = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/aggressive_lab_autonomous_cycle.py')
    if src.exists():
        script_p.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')
        print("Copied successfully to /opt/data/scripts/")
