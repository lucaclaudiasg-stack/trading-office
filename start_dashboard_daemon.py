"""
Starts dashboard_backend.py as a background daemon process.
"""
import subprocess
import sys
import time

def start():
    print("Starting dashboard_backend.py in background...")
    proc = subprocess.Popen(
        [sys.executable, "/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)
    print("Dashboard daemon started with PID:", proc.pid)

if __name__ == '__main__':
    start()
