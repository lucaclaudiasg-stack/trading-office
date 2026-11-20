"""
Tests zoneinfo availability for Europe/Rome timezone.
"""
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
    rome_time = datetime.now(ZoneInfo("Europe/Rome"))
    print("ZoneInfo success! Rome time:", rome_time.isoformat())
except Exception as e:
    print("ZoneInfo error:", e)
    # Fallback to manual offset or pytz
    import pytz
    rome_time = datetime.now(pytz.timezone("Europe/Rome"))
    print("Pytz success! Rome time:", rome_time.isoformat())
