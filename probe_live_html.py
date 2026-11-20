"""
Probes live HTTP response from port 8765.
"""
import urllib.request
import json

def probe():
    print("=== PROBING LIVE SERVER ON PORT 8765 ===")
    
    # 1. Fetch HTML
    try:
        resp = urllib.request.urlopen("http://127.0.0.1:8765/")
        html = resp.read().decode('utf-8')
        print(f"HTTP Status: {resp.status}, HTML length: {len(html)} bytes")
        print("Contains 'sec-committee':", "sec-committee" in html)
        print("Contains 'nav-committee':", "nav-committee" in html)
        print("Contains 'sec-simulation':", "sec-simulation" in html)
        print("Contains 'nav-simulation':", "nav-simulation" in html)
        print("Contains 'SHADOW TRADING':", "SHADOW TRADING" in html)
    except Exception as e:
        print("Error fetching HTML:", e)
        
    # 2. Fetch /api/shadow/ledger
    try:
        resp_led = urllib.request.urlopen("http://127.0.0.1:8765/api/shadow/ledger")
        print(f"/api/shadow/ledger Status: {resp_led.status}")
        data = json.loads(resp_led.read().decode('utf-8'))
        print("Ledger data:", json.dumps(data)[:300])
    except Exception as e:
        print("Error fetching /api/shadow/ledger:", e)

    # 3. Fetch /api/shadow/summary
    try:
        resp_sum = urllib.request.urlopen("http://127.0.0.1:8765/api/shadow/summary")
        print(f"/api/shadow/summary Status: {resp_sum.status}")
        data = json.loads(resp_sum.read().decode('utf-8'))
        print("Summary keys:", list(data.keys()) if isinstance(data, dict) else "list")
    except Exception as e:
        print("Error fetching /api/shadow/summary:", e)

if __name__ == '__main__':
    probe()
