"""
Tests the dashboard backend API endpoints locally.
"""
import urllib.request
import json
import subprocess
import time
import sys

def test():
    # Start server in background
    proc = subprocess.Popen([sys.executable, "/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py"])
    time.sleep(1.5)
    
    try:
        endpoints = ['/api/overview', '/api/portfolio', '/api/market', '/api/history', '/api/system']
        for ep in endpoints:
            url = f"http://127.0.0.1:8765{ep}"
            req = urllib.request.urlopen(url)
            data = json.loads(req.read().decode('utf-8'))
            print(f"Endpoint {ep}: OK (keys: {list(data.keys())})")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == '__main__':
    test()
