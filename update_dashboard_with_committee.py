"""
Enhances dashboard_backend.py:
1. Adds /api/committee/latest and /api/committee/history
2. Updates /api/overview with exact Italian timestamps and freshness flags
3. Adds Comitato AI section with timeline of agent interventions and meeting history
4. Adds timestamp rows to Overview cards and explains 143.58 EUR vs 142.42 EUR
5. Backs up and restarts daemon on port 8765
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
BACKUP_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py.bak_committee_20261119')
ARCHIVE_PATH = Path('/app/staging/historical_analysis_archive.json')
if not ARCHIVE_PATH.exists():
    ARCHIVE_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/historical_analysis_archive.json')

def format_rome(dt_iso):
    if not dt_iso:
        return "Data non disponibile"
    try:
        dt = datetime.fromisoformat(dt_iso.replace('Z', '+00:00'))
        dt_rome = dt.astimezone(ZoneInfo("Europe/Rome"))
        tz_name = dt_rome.strftime("%Z")
        return dt_rome.strftime(f"%d/%m/%Y · %H:%M {tz_name}")
    except Exception:
        return dt_iso[:19].replace('T', ' ')

def get_relative_time(dt_iso):
    if not dt_iso:
        return ""
    try:
        dt = datetime.fromisoformat(dt_iso.replace('Z', '+00:00'))
        diff_sec = (datetime.now(timezone.utc) - dt).total_seconds()
        if diff_sec < 60:
            return "Aggiornato pochi secondi fa"
        elif diff_sec < 3600:
            return f"Aggiornato {int(diff_sec // 60)} min fa"
        elif diff_sec < 86400:
            return f"Aggiornato {int(diff_sec // 3600)} h fa"
        else:
            return f"Aggiornato {int(diff_sec // 86400)} gg fa"
    except Exception:
        return ""

print("Applying Committee & Timestamp updates...")
