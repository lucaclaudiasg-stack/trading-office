"""
Queries specific balance/positions using coinbase_balance or portfolio details via read-only adapter.
"""
import sys
import json
import subprocess

ADAPTER_PATH = "/opt/data/scripts/coinbase_readonly_adapter.py"

def get_balances():
    # Call coinbase_balance
    req = json.dumps({
        "jsonrpc": "2.0",
        "id": 10,
        "method": "tools/call",
        "params": {
            "name": "coinbase_balance",
            "arguments": {"portfolio_id": "bf5d6e63-e0bf-5671-8344-42a9ccb862db"}
        }
    }) + "\n"
    
    proc = subprocess.Popen(
        [sys.executable, ADAPTER_PATH],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = proc.communicate(input=req, timeout=20)
    for line in stdout.strip().split("\n"):
        try:
            parsed = json.loads(line)
            print("BALANCE RESULT:", json.dumps(parsed, indent=2))
        except Exception as e:
            print("RAW LINE:", line)

if __name__ == '__main__':
    get_balances()
