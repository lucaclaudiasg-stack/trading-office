"""
Tests committee API endpoints on local dashboard server.
"""
import urllib.request
import json

def test():
    for ep in ['/api/committee/latest', '/api/committee/history', '/api/overview']:
        url = f"http://127.0.0.1:8765{ep}"
        try:
            req = urllib.request.urlopen(url)
            data = json.loads(req.read().decode('utf-8'))
            print(f"Endpoint {ep}: OK (keys: {list(data.keys()) if isinstance(data, dict) else len(data)})")
        except Exception as e:
            print(f"Endpoint {ep}: ERROR -> {e}")

if __name__ == '__main__':
    test()
