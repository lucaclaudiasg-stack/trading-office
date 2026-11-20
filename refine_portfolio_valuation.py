from pathlib import Path
"""
Refines portfolio valuation by querying verified EUR spot prices and timestamps via MCP Read-Only adapter.
Applies VALUATION_UNAVAILABLE for unquoted assets.
"""
import sys
import json
import subprocess
from datetime import datetime, timezone

ADAPTER_PATH = "/opt/data/scripts/coinbase_readonly_adapter.py"

HELD_ASSETS = [
    {"asset": "EUR", "balance": 2.53, "pair": None},
    {"asset": "BTC", "balance": 0.00181225, "pair": "BTC-EUR"},
    {"asset": "ETH", "balance": 0.02084170, "pair": "ETH-EUR"},
    {"asset": "XLM", "balance": 26.468429, "pair": "XLM-EUR"},
    {"asset": "GRT", "balance": 3.95726156, "pair": "GRT-EUR"},
    {"asset": "FET", "balance": 5.33808673, "pair": "FET-EUR"},
    {"asset": "AMP", "balance": 46.76313466, "pair": "AMP-EUR"},
    {"asset": "NKN", "balance": 41.61004336, "pair": "NKN-EUR"},
    {"asset": "ENJ", "balance": 18.78598323, "pair": "ENJ-EUR"},
    {"asset": "RLY", "balance": 4.49281187, "pair": "RLY-EUR"},
    {"asset": "ALEO", "balance": 3.44976500, "pair": "ALEO-EUR"},
    {"asset": "COMP", "balance": 0.02061009, "pair": "COMP-EUR"},
    {"asset": "CLV", "balance": 1.96078431, "pair": "CLV-EUR"},
]

def query_adapter_ticker(pair):
    if not pair:
        return {"price": 1.0, "timestamp": datetime.now(timezone.utc).isoformat(), "verified": True}
        
    req = json.dumps({
        "jsonrpc": "2.0",
        "id": 100,
        "method": "tools/call",
        "params": {
            "name": "coinbase_products_ticker",
            "arguments": {"product_id": pair}
        }
    }) + "\n"
    
    try:
        proc = subprocess.Popen(
            [sys.executable, ADAPTER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, _ = proc.communicate(input=req, timeout=15)
        for line in stdout.strip().split("\n"):
            try:
                parsed = json.loads(line)
                if "result" in parsed:
                    res = parsed["result"]
                    struct = res.get("structuredContent", {})
                    if struct and "trades" in struct and struct["trades"]:
                        last_trade = struct["trades"][0]
                        return {
                            "price": float(last_trade["price"]),
                            "timestamp": last_trade.get("time", datetime.now(timezone.utc).isoformat()),
                            "verified": True
                        }
                    elif struct and "best_bid" in struct:
                        return {
                            "price": float(struct["best_bid"]),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "verified": True
                        }
                    content_list = res.get("content", [])
                    for c in content_list:
                        if c.get("type") == "text":
                            txt_data = json.loads(c.get("text", "{}"))
                            if "trades" in txt_data and txt_data["trades"]:
                                return {
                                    "price": float(txt_data["trades"][0]["price"]),
                                    "timestamp": txt_data["trades"][0].get("time", datetime.now(timezone.utc).isoformat()),
                                    "verified": True
                                }
            except Exception:
                pass
    except Exception:
        pass
    return {"price": None, "timestamp": None, "verified": False}

def main():
    print("=== REFINING PORTFOLIO VALUATION ===")
    results = []
    total_valuable = 0.0
    unvalued_count = 0
    
    for item in HELD_ASSETS:
        asset = item["asset"]
        bal = item["balance"]
        pair = item["pair"]
        
        if asset == "EUR":
            val = bal
            results.append({
                "asset": asset,
                "balance": bal,
                "price_eur": 1.0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "value_eur": val,
                "status": "VERIFIED"
            })
            total_valuable += val
            continue
            
        ticker = query_adapter_ticker(pair)
        if ticker["verified"] and ticker["price"] is not None:
            price = ticker["price"]
            val = bal * price
            results.append({
                "asset": asset,
                "balance": bal,
                "pair": pair,
                "price_eur": price,
                "timestamp": ticker["timestamp"],
                "value_eur": val,
                "status": "VERIFIED"
            })
            if asset in ["BTC", "ETH"]:
                total_valuable += val
        else:
            results.append({
                "asset": asset,
                "balance": bal,
                "pair": pair,
                "price_eur": "VALUATION_UNAVAILABLE",
                "timestamp": None,
                "value_eur": 0.0,
                "status": "VALUATION_UNAVAILABLE"
            })
            unvalued_count += 1
            
    # Calculate weights based on total valuable (or partial total)
    for r in results:
        if r["status"] == "VERIFIED" and total_valuable > 0:
            r["weight_percent"] = round((r["value_eur"] / total_valuable) * 100, 2)
        else:
            r["weight_percent"] = 0.0
            
    output = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "total_valuable_eur": round(total_valuable, 2),
        "unvalued_assets_count": unvalued_count,
        "holdings": results
    }
    
    out_path = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/refined_portfolio_valuation.json')
    out_path.write_text(json.dumps(output, indent=2))
    print(f"Refined valuation saved to {out_path}. Total Valuable (BTC+ETH+EUR): {total_valuable:.2f} EUR")

if __name__ == '__main__':
    main()
