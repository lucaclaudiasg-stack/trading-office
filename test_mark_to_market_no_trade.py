"""
Mandatory Test Suite for Continuous Mark-to-Market Valuation Without Trades.
Validates requirement 6 from the Master Directive.
"""
from decimal import Decimal
import json
from pathlib import Path
import mark_to_market_engine

def run_mtm_test():
    print("=== STARTING MARK-TO-MARKET NO-TRADE MANDATORY TEST ===")
    
    # 1. Initial State Check
    initial_q = dict(mark_to_market_engine.QUANTITIES)
    initial_result = mark_to_market_engine.update_mark_to_market()
    initial_val = Decimal(initial_result["current_live_valuated_eur"])
    
    # 2. Simulate spot price shift (BTC drops by -5%, ETH drops by -4%)
    simulated_prices = {
        "BTC-EUR": Decimal("52174.00"), # -5%
        "ETH-EUR": Decimal("1483.20"),  # -4%
        "XLM-EUR": Decimal("0.110"),
        "GRT-EUR": Decimal("0.014")
    }
    
    # 3. Execute Mark-to-Market recalculation
    shifted_result = mark_to_market_engine.update_mark_to_market(live_prices=simulated_prices)
    shifted_val = Decimal(shifted_result["current_live_valuated_eur"])
    
    # 4. Verifications
    results = {}
    
    # Check A: Quantities must be 100% identical
    final_q = dict(mark_to_market_engine.QUANTITIES)
    quantities_identical = (initial_q == final_q)
    results["test_A_quantities_unaltered"] = {
        "status": "PASS" if quantities_identical else "FAIL",
        "initial": {k: str(v) for k, v in initial_q.items()},
        "final": {k: str(v) for k, v in final_q.items()}
    }
    
    # Check B: Valuated total EUR must change according to price shift
    val_changed = (shifted_val != initial_val and shifted_val < initial_val)
    results["test_B_value_eur_recalculated"] = {
        "status": "PASS" if val_changed else "FAIL",
        "initial_total_eur": str(initial_val),
        "shifted_total_eur": str(shifted_val),
        "difference_eur": str(shifted_val - initial_val)
    }
    
    # Check C: Trade count must remain 0 (no fake orders generated)
    trades_hermes_ai = shifted_result["portfolios"]["hermes_ai"]["trade_count"]
    trades_buy_hold = shifted_result["portfolios"]["buy_and_hold"]["trade_count"]
    zero_trades = (trades_hermes_ai == 0 and trades_buy_hold == 0)
    results["test_C_zero_trades_generated"] = {
        "status": "PASS" if zero_trades else "FAIL",
        "trade_count_hermes_ai": trades_hermes_ai,
        "trade_count_buy_hold": trades_buy_hold
    }
    
    # Check D: Rome timestamp updated
    has_rome_ts = bool(shifted_result.get("timestamp_rome"))
    results["test_D_timestamp_updated"] = {
        "status": "PASS" if has_rome_ts else "FAIL",
        "timestamp_rome": shifted_result.get("timestamp_rome")
    }

    # Print summary
    print("\n=== MARK-TO-MARKET TEST RESULTS ===")
    total = len(results)
    passed = sum(1 for v in results.values() if v["status"] == "PASS")
    print(f"Summary: {passed}/{total} tests PASSED.")
    for k, v in results.items():
        print(f"  {k}: {v['status']}")
        
    # Re-run default live MTM after test
    mark_to_market_engine.update_mark_to_market()
    return results

if __name__ == '__main__':
    run_mtm_test()
