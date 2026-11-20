"""
Diagnostic script for coinbase_products_ticker argument names.
"""
import sys
import json
import subprocess

ADAPTER_PATH = "/opt/data/scripts/coinbase_readonly_adapter.py"

def test_ticker():
    for arg_name in ["product_id", "product", "symbol", "pair"]:
        req = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "coinbase_products_ticker",
                "arguments": {arg_name: "BTC-EUR"}
            }
        }) + "\n"
        proc = subprocess.Popen(
            [sys.executable, ADAPTER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, _ = proc.communicate(input=req, timeout=10)
        print(f"Arg name '{arg_name}':", stdout.strip())

if __name__ == '__main__':
    test_ticker()
