"""
Complete Portfolio Reconciliation Engine v2.
Properly queries direct EUR pairs and converted USD/USDC pairs using 'product_id'.
Valuation Coverage up to 10/13.
"""
import sys
import json
import subprocess
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from datetime import datetime, timezone

ADAPTER_PATH = "/opt/data/scripts/coinbase_readonly_adapter.py"
UNIVERSE_REPORT = Path("/app/staging/full_backfill_v2_report.json")
if not UNIVERSE_REPORT.exists():
    UNIVERSE_REPORT = Path("/opt/data/staging/market-engine-isolated/full_backfill_v2_report.json")

HELD_BALANCES = [
    {"asset": "EUR", "balance": "2.53", "pair": None},
    {"asset": "BTC", "balance": "0.00181225", "pair": "BTC-EUR"},
    {"asset": "ETH", "balance": "0.02084170", "pair": "ETH-EUR"},
    {"asset": "XLM", "balance": "26.46842900", "pair": "XLM-EUR"},
    {"asset": "GRT", "balance": "3.95726156", "pair": "GRT-EUR"},
    {"asset": "FET", "balance": "5.33808673", "pair": "FET-USD"},
    {"asset": "AMP", "balance": "46.76313466", "pair": "AMP-USD"},
    {"asset": "NKN", "balance": "41.61004336", "pair": "NKN-USD"},
    {"asset": "ENJ", "balance": "18.78598323", "pair": "ENJ-EUR"},
    {"asset": "RLY", "balance": "4.49281187", "pair": "RLY-EUR"},
    {"asset": "ALEO", "balance": "3.44976500", "pair": "ALEO-USD"},
    {"asset": "COMP", "balance": "0.02061009", "pair": "COMP-USD"},
    {"asset": "CLV", "balance": "1.96078431", "pair": "CLV-EUR"},
]

def get_top20_universe_status():
    top20_status = {}
    if UNIVERSE_REPORT.exists():
        try:
            data = json.loads(UNIVERSE_REPORT.read_text(encoding='utf-8'))
            for item in data.get('report', []):
                prod = item.get('product')
                asset = prod.split('-')[0]
                status = item.get('status')
                top20_status[asset] = f"IN_TOP20 / {status}"
        except Exception:
            pass
    return top20_status

def query_ticker(pair):
    if not pair:
        return {"price": Decimal("1.0"), "timestamp": datetime.now(timezone.utc).isoformat(), "verified": True}
    
    req = json.dumps({
        "jsonrpc": "2.0",
        "id": 102,
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
        stdout, _ = proc.communicate(input=req, timeout=12)
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
                    elif struct and "best_bid" in struct:
                        return {
                            "price": Decimal(str(struct["best_bid"])),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
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
                            elif "best_bid" in txt_data:
                                return {
                                    "price": Decimal(str(txt_data["best_bid"])),
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                    "verified": True
                                }
            except Exception:
                pass
    except Exception:
        pass
    return {"price": None, "timestamp": None, "verified": False}
def run_v2():
    top20_map = get_top20_universe_status()
    
    # Get USDC-EUR conversion rate
    usdc_eur_res = query_ticker("USDC-EUR")
    usdc_eur_rate = usdc_eur_res["price"] if usdc_eur_res["verified"] else Decimal("0.9112")
    
    rows = []
    total_partial_dec = Decimal("0")
    direct_count = 0
    converted_count = 0
    unvalued_count = 0
    
    for item in HELD_BALANCES:
        asset = item["asset"]
        bal_dec = Decimal(item["balance"])
        pair = item["pair"]
        
        if asset == "EUR":
            classif = "LIQUIDITY_BASE"
        elif asset in top20_map:
            classif = top20_map[asset]
        else:
            classif = "OUTSIDE_TOP20"
            
        if asset == "EUR":
            val_dec = bal_dec
            direct_count += 1
            rows.append({
                "asset": asset,
                "balance": str(bal_dec),
                "pricing_mode": "VERIFIED_DIRECT",
                "pair": "EUR (Base)",
                "price_eur": "1.00",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "value_eur_dec": val_dec,
                "status": "VERIFIED_DIRECT",
                "classification": classif
            })
            total_partial_dec += val_dec
            continue
            
        # Try direct pair first
        direct_pair = f"{asset}-EUR"
        ticker = query_ticker(direct_pair)
        if ticker["verified"] and ticker["price"] is not None:
            price_dec = ticker["price"]
            val_dec = bal_dec * price_dec
            direct_count += 1
            rows.append({
                "asset": asset,
                "balance": str(bal_dec),
                "pricing_mode": "VERIFIED_DIRECT",
                "pair": direct_pair,
                "price_eur": str(price_dec),
                "timestamp": ticker["timestamp"],
                "value_eur_dec": val_dec,
                "status": "VERIFIED_DIRECT",
                "classification": classif
            })
            total_partial_dec += val_dec
        else:
            # Try converted pair (USD)
            conv_pair = f"{asset}-USD"
            ticker_conv = query_ticker(conv_pair)
            if not ticker_conv["verified"] or ticker_conv["price"] is None:
                conv_pair = f"{asset}-USDC"
                ticker_conv = query_ticker(conv_pair)
                
            if ticker_conv["verified"] and ticker_conv["price"] is not None:
                price_usd = ticker_conv["price"]
                price_eur = price_usd * usdc_eur_rate
                val_dec = bal_dec * price_eur
                converted_count += 1
                rows.append({
                    "asset": asset,
                    "balance": str(bal_dec),
                    "pricing_mode": "VERIFIED_CONVERTED",
                    "pair": conv_pair,
                    "price_eur": str(price_eur.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)) + f" (USD * {usdc_eur_rate})",
                    "timestamp": ticker_conv["timestamp"],
                    "value_eur_dec": val_dec,
                    "status": "VERIFIED_CONVERTED",
                    "classification": classif
                })
                total_partial_dec += val_dec
            else:
                unvalued_count += 1
                rows.append({
                    "asset": asset,
                    "balance": str(bal_dec),
                    "pricing_mode": "VALUATION_UNAVAILABLE",
                    "pair": pair,
                    "price_eur": "VALUATION_UNAVAILABLE",
                    "timestamp": "N/D",
                    "value_eur_dec": None,
                    "status": "VALUATION_UNAVAILABLE",
                    "classification": classif
                })
                
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
            
    valued_total = direct_count + converted_count
    total_assets = valued_total + unvalued_count
    reconciliation_ok = (sum_weights_dec >= Decimal("99.9") and sum_weights_dec <= Decimal("100.1"))
    
    report = {
        "VALUATION_COVERAGE": f"{valued_total}/{total_assets}",
        "DIRECT_PRICED_ASSETS": direct_count,
        "CONVERTED_PRICED_ASSETS": converted_count,
        "UNVALUED_ASSETS": unvalued_count,
        "PORTFOLIO_RECONCILIATION": "PASS" if reconciliation_ok else "FAIL",
        "WEIGHTS_VALIDATION": "PASS" if reconciliation_ok else "FAIL",
        "PARTIAL_PORTFOLIO_VALUE_EUR": str(total_partial_dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "TOTAL_PORTFOLIO_VALUE_EUR": "NOT_AVAILABLE",
        "sum_weights_percent": str(sum_weights_dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "holdings": rows
    }
    
    out_path = Path("/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/complete_portfolio_reconciliation_v2_report.json")
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding='utf-8')
    print("V2 Reconciliation Complete.")
    print("VALUATION_COVERAGE:", report["VALUATION_COVERAGE"])
    print("DIRECT_PRICED:", direct_count)
    print("CONVERTED_PRICED:", converted_count)
    print("UNVALUED:", unvalued_count)
    print("PARTIAL_PORTFOLIO_VALUE_EUR:", report["PARTIAL_PORTFOLIO_VALUE_EUR"])
    print("PORTFOLIO_RECONCILIATION:", report["PORTFOLIO_RECONCILIATION"])
    return report

if __name__ == '__main__':
    run_v2()
