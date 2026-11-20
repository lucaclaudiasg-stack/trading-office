"""
Probes available markets on Coinbase for the 8 unvalued assets (EUR, USD, USDC pairs)
and checks conversion rates USDC-EUR and EUR-USD.
"""
import sys
import json
import subprocess

ADAPTER_PATH = "/opt/data/scripts/coinbase_readonly_adapter.py"

ASSETS = ["FET", "AMP", "NKN", "ENJ", "RLY", "ALEO", "COMP", "CLV"]
PAIRS_TO_CHECK = []
for a in ASSETS:
    PAIRS_TO_CHECK.extend([f"{a}-EUR", f"{a}-USD", f"{a}-USDC"])

# Also add conversion pairs
PAIRS_TO_CHECK.extend(["USDC-EUR", "EUR-USD", "USDC-USD"])

def check_tickers():
    results = {}
    for pair in PAIRS_TO_CHECK:
        req = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "coinbase_products_ticker", "arguments": {"product_id": pair}}
        }) + "\n"
        try:
            proc = subprocess.Popen(
                [sys.executable, ADAPTER_PATH],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, _ = proc.communicate(input=req, timeout=10)
            for line in stdout.strip().split("\n"):
                try:
                    res = json.loads(line)
                    if "result" in res:
                        struct = res["result"].get("structuredContent", {})
                        if struct and "trades" in struct and struct["trades"]:
                            results[pair] = {
                                "price": struct["trades"][0]["price"],
                                "time": struct["trades"][0].get("time"),
                                "best_bid": struct.get("best_bid"),
                                "best_ask": struct.get("best_ask")
                            }
                        elif struct and "best_bid" in struct:
                            results[pair] = {
                                "price": struct["best_bid"],
                                "time": None,
                                "best_bid": struct.get("best_bid"),
                                "best_ask": struct.get("best_ask")
                            }
                        else:
                            content_list = res["result"].get("content", [])
                            for c in content_list:
                                if c.get("type") == "text":
                                    txt = json.loads(c.get("text", "{}"))
                                    if "trades" in txt and txt["trades"]:
                                        results[pair] = {
                                            "price": txt["trades"][0]["price"],
                                            "time": txt["trades"][0].get("time"),
                                            "best_bid": txt.get("best_bid"),
                                            "best_ask": txt.get("best_ask")
                                        }
                                    elif "best_bid" in txt:
                                        results[pair] = {
                                            "price": txt["best_bid"],
                                            "time": None,
                                            "best_bid": txt.get("best_bid"),
                                            "best_ask": txt.get("best_ask")
                                        }
                                    elif "message" in txt:
                                        results[pair] = {"error": txt["message"]}
                    elif "error" in res:
                        results[pair] = {"error": res["error"].get("message", "unknown error")}
                except Exception:
                    pass
        except Exception as e:
            results[pair] = {"error": str(e)}

    print("PROBE RESULTS:")
    print(json.dumps(results, indent=2))
    
    out_path = "/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/coinbase_products_probe_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

if __name__ == '__main__':
    check_tickers()
