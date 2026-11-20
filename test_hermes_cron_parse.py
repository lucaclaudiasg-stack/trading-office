"""
Tests Hermes's compute_next_run with Europe/Rome timezone and 30 9,21 * * *.
"""
import sys
sys.path.insert(0, '/opt/hermes')

try:
    from cron.jobs import compute_next_run, parse_schedule
    
    schedule_dict = {
        "kind": "cron",
        "expr": "30 9,21 * * *",
        "display": "30 9,21 * * *"
    }
    
    next_rome = compute_next_run(schedule_dict, timezone="Europe/Rome")
    print("compute_next_run with Europe/Rome:", next_rome)
    
    # Also check with parse_schedule
    parsed = parse_schedule("30 9,21 * * *")
    print("parse_schedule('30 9,21 * * *'):", parsed)
    
except Exception as e:
    print("Error importing/testing hermes cron:", e)
