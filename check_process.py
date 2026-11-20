"""
Checks if dashboard_backend.py is running.
"""
import subprocess

res = subprocess.run(["ps", "aux"], capture_output=True, text=True)
for line in res.stdout.split("\n"):
    if "dashboard_backend.py" in line:
        print("FOUND:", line)
