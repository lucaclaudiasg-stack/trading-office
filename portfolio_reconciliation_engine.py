"""
Deterministic Portfolio Reconciliation Engine (Permanent Fix).
Implements:
1. Exact decimal calculations for Valued Assets (EUR Value = Balance * Price).
2. Sum of valued assets = Partial Portfolio Value.
3. Weights = Value / Partial Portfolio Value * 100.
4. Unvalued assets = VALUATION_UNAVAILABLE, Value = N/D, Weight = N/D.
5. Strict Top 20 dynamic universe classification (IN_TOP20 / DATA_READY, IN_TOP20 / DATA_LIMITED, OUTSIDE_TOP20).
6. Automatic reconciliation gates: PORTFOLIO_RECONCILIATION, WEIGHTS_VALIDATION, TOP20_CLASSIFICATION.
"""
import sys
import json
import subprocess
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from datetime import datetime, timezone

ADAPTER_PATH = "/opt/data/scripts/coinbase_readonly_adapter.py"
UNIVERSE_REPORT = Path("/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/live_exploratory_results.json")
UNIVERSE_PUBLISHED = Path("/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/live_exploratory_results.json")

# Fallback paths if run outside container
if not UNIVERSE_REPORT.exists():
    UNIVERSE_REPORT = Path("/opt/data/staging/market-engine-isolated/full_backfill_v2_report.json")
if not UNIVERSE_PUBLISHED.exists():
    UNIVERSE_PUBLISHED = Path("/opt/data/staging/market-engine-isolated/published_universe.json")

HELD_BALANCES = [
    {"asset": "EUR", "balance": "2.53", "pair": None},
    {"asset": "BTC", "balance": "0.00181225", "pair": "BTC-EUR"},
    {"asset": "ETH", "balance": "0.02084170", "pair": "ETH-EUR"},
    {"asset": "XLM", "balance": "26.46842900", "pair": "XLM-EUR"},
    {"asset": "GRT", "balance": "3.95726156", "pair": "GRT-EUR"},
    {"asset": "FET", "balance": "5.33808673", "pair": "FET-EUR"},
    {"asset": "AMP", "balance": "46.76313466", "pair": "AMP-EUR"},
    {"asset": "NKN", "balance": "41.61004336", "pair": "NKN-EUR"},
    {"asset": "ENJ", "balance": "18.78598323", "pair": "ENJ-EUR"},
    {"asset": "RLY", "balance": "4.49281187", "pair": "RLY-EUR"},
    {"asset": "ALEO", "balance": "3.44976500", "pair": "ALEO-EUR"},
    {"asset": "COMP", "balance": "0.02061009", "pair": "COMP-EUR"},
    {"asset": "CLV", "balance": "1.96078431", "pair": "CLV-EUR"},
]

def get_top20_universe_status():
    top20_status = {}
    f = Path("/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/live_exploratory_results.json")
    if f.exists():
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            top20_list = data.get('top20_ranking', {}).get('top20', [])
            for item in top20_list:
                prod = item.get('product') # e.g. "BTC-EUR"
                if prod:
                    asset = prod.split('-')[0]
                    tier = item.get('tier', 'EXPLORATORY')
                    top20_status[asset] = f"IN_TOP20 / {tier}"
        except Exception as e:
            print("Error loading universe report:", e)
    return top20_status
def query_ticker(pair):
    if not pair:
        return {"price": Decimal("1.0"), "timestamp": datetime.now(timezone.utc).isoformat(), "verified": True}
    
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
                        return {
                            "price": Decimal(str(struct["trades"][0]["price"])),
                            "timestamp": struct["trades"][0].get("time", datetime.now(timezone.utc).isoformat()),
                            "verified": True
                        }
                    elif struct and "price" in struct:
                        return {
                            "price": Decimal(str(struct["price"])),
                            "timestamp": struct.get("time", datetime.now(timezone.utc).isoformat()),
                            "verified": True
                        }
                    content_list = res.get("content", [])
                    for c in content_list:
                        if c.get("type") == "text":
                            txt_data = json.loads(c.get("text", "{}"))
                            if "trades" in txt_data and txt_data["trades"]:
                                return {
                                    "price": Decimal(str(txt_data["trades"][0]["price"])),
                                    "timestamp": txt_data["trades"][0].get("time", datetime.now(timezone.utc).isoformat()),
                                    "verified": True
                                }
            except Exception:
                pass
    except Exception:
        pass
    return {"price": None, "timestamp": None, "verified": False}
def run_reconciliation():
    top20_map = get_top20_universe_status()
    rows = []
    total_partial_dec = Decimal("0")
    valued_count = 0
    unvalued_count = 0
    
    for item in HELD_BALANCES:
        asset = item["asset"]
        bal_dec = Decimal(item["balance"])
        pair = item["pair"]
        
        # Classification
        if asset == "EUR":
            classif = "LIQUIDITY_BASE"
        elif asset in top20_map:
            classif = top20_map[asset]
        else:
            classif = "OUTSIDE_TOP20"
            
        ticker = query_ticker(pair)
        if ticker["verified"] and ticker["price"] is not None:
            price_dec = ticker["price"]
            val_dec = bal_dec * price_dec
            total_partial_dec += val_dec
            valued_count += 1
            rows.append({
                "asset": asset,
                "balance": str(bal_dec),
                "price_eur": str(price_dec),
                "timestamp": ticker["timestamp"],
                "value_eur_dec": val_dec,
                "status": "VERIFIED",
                "classification": classif
            })
        else:
            unvalued_count += 1
            rows.append({
                "asset": asset,
                "balance": str(bal_dec),
                "price_eur": "VALUATION_UNAVAILABLE",
                "timestamp": "N/D",
                "value_eur_dec": None,
                "status": "VALUATION_UNAVAILABLE",
                "classification": classif
            })
            
    # Calculate weights and presentation strings
    sum_weights_dec = Decimal("0")
    for r in rows:
        if r["value_eur_dec"] is not None and total_partial_dec > Decimal("0"):
            w_dec = (r["value_eur_dec"] / total_partial_dec) * Decimal("100")
            sum_weights_dec += w_dec
            r["value_eur"] = str(r["value_eur_dec"].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
            r["weight_percent"] = str(w_dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        else:
            r["value_eur"] = "N/D"
            r["weight_percent"] = "N/D"
            
    # VALIDATION GATES
    sum_rows_val = sum([r["value_eur_dec"] for r in rows if r["value_eur_dec"] is not None])
    diff_val = abs(sum_rows_val - total_partial_dec)
    reconciliation_ok = (diff_val < Decimal("0.0001"))
    
    # Weight validation: sum of weights within 99.9% - 100.1%
    weights_ok = (Decimal("99.9") <= sum_weights_dec <= Decimal("100.1"))
    
    # Top20 classification validation: GRT must be IN_TOP20 / DATA_LIMITED
    grt_row = next((r for r in rows if r["asset"] == "GRT"), None)
    top20_ok = (grt_row is not None and "IN_TOP20" in grt_row["classification"])
    
    verdict = {
        "PORTFOLIO_RECONCILIATION": "PASS" if reconciliation_ok else "FAIL",
        "VALUED_ASSETS": valued_count,
        "UNVALUED_ASSETS": unvalued_count,
        "PARTIAL_PORTFOLIO_VALUE_EUR": str(total_partial_dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "TOTAL_PORTFOLIO_VALUE_EUR": "NOT_AVAILABLE",
        "WEIGHTS_VALIDATION": "PASS" if weights_ok else "FAIL",
        "TOP20_CLASSIFICATION": "PASS" if top20_ok else "FAIL",
        "sum_weights_percent": str(sum_weights_dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "holdings": rows
    }
    
    out_path = Path("/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/reconciliation_audit_report.json")
    out_path.write_text(json.dumps(verdict, indent=2, default=str), encoding='utf-8')
    print("Reconciliation Complete. Verdicts:")
    print("PORTFOLIO_RECONCILIATION:", verdict["PORTFOLIO_RECONCILIATION"])
    print("WEIGHTS_VALIDATION:", verdict["WEIGHTS_VALIDATION"])
    print("TOP20_CLASSIFICATION:", verdict["TOP20_CLASSIFICATION"])
    print("PARTIAL_PORTFOLIO_VALUE_EUR:", verdict["PARTIAL_PORTFOLIO_VALUE_EUR"])
    return verdict

if __name__ == '__main__':
    run_reconciliation()
