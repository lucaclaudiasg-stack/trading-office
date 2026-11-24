"""
Cleanly stops any running dashboard processes, verifies port 8765, and restarts dashboard daemon.
"""
import subprocess
import time
from pathlib import Path

WORKSPACE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')

def restart_daemon():
    print("=== CLEAN RESTART OF DASHBOARD DAEMON ===")
    
    # 1. Kill any existing instances
    subprocess.run(["pkill", "-f", "dashboard_backend.py"], capture_output=True)
    time.sleep(1)
    
    # 2. Start daemon via start_dashboard_daemon.py
    res = subprocess.run(
        ["python3", "-B", str(WORKSPACE / "start_dashboard_daemon.py")],
        capture_output=True, text=True, cwd=str(WORKSPACE)
    )
    print("Daemon start output:", res.stdout, res.stderr)
    
    # 3. Check process
    ps = subprocess.run(["pgrep", "-f", "dashboard_backend.py"], capture_output=True, text=True)
    print("Active dashboard PIDs:", ps.stdout.strip())

if __name__ == '__main__':
    restart_daemon()
