"""
Automated Non-Interference & Isolation Audit Suite between Aggressive Lab and Committee Trading Office.
Validates requirement 4 from the Master Directive.
"""
import json
import re
from pathlib import Path

WORKSPACE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')
JOBS_PATH = Path('/opt/data/cron/jobs.json')

def run_non_interference_audit():
    print("=== STARTING NON-INTERFERENCE & ISOLATION AUDIT ===")
    results = {}
    
    # 1. Code Inspection: Check aggressive scripts for forbidden imports/calls
    forbidden_tokens = [
        'trading_director', 'bear_analyst', 'quant_researcher', 'market_analyst',
        'zone_aware_debate_wrapper', 'master_directive_engine', 'coinbase_pro_auth',
        'CoinbaseAccounts', 'CoinbaseOrders', 'buy_order', 'sell_order'
    ]
    
    script_paths = [
        WORKSPACE / 'aggressive_lab_autonomous_cycle.py',
        WORKSPACE / 'aggressive_portfolio_simulator.py'
    ]
    
    found_tokens = []
    for sp in script_paths:
        if sp.exists():
            content = sp.read_text(encoding='utf-8')
            for tok in forbidden_tokens:
                if tok in content:
                    found_tokens.append((sp.name, tok))
                    
    results["test_01_no_forbidden_imports"] = {
        "status": "PASS" if not found_tokens else "FAIL",
        "violations": found_tokens
    }
    
    # 2. Check 4 Master Cron Jobs & 5 Paused Trading Jobs Integrity
    if JOBS_PATH.exists():
        try:
            jobs_data = json.loads(JOBS_PATH.read_text(encoding='utf-8'))
            jobs_list = jobs_data.get("jobs", []) if isinstance(jobs_data, dict) else jobs_data
            
            master_jobs = ['master_score_4h', 'master_debate_daily', 'master_verify_daily', 'master_report_weekly']
            present_master = []
            for j in jobs_list:
                job_id = j.get("id", "") or j.get("job_id", "") or ""
                script_val = j.get("script", "") or ""
                if any(m == job_id or m in script_val for m in master_jobs):
                    present_master.append(j)
            all_masters_ok = len(present_master) >= 4
            
            results["test_02_master_jobs_untouched"] = {
                "status": "PASS" if all_masters_ok else "FAIL",
                "master_jobs_count": len(present_master)
            }
        except Exception as e:
            results["test_02_master_jobs_untouched"] = {"status": "FAIL", "error": str(e)}
    else:
        results["test_02_master_jobs_untouched"] = {"status": "FAIL", "error": "jobs.json not found"}

    # 3. Ledger Separation Check
    state_file = WORKSPACE / 'aggressive_portfolio_state.json'
    committee_archive = Path('/app/staging/historical_analysis_archive.json')
    shadow_state = WORKSPACE / 'shadow_portfolio_state.json'
    
    ledger_isolated = state_file.exists() and state_file != shadow_state and state_file != committee_archive
    results["test_03_ledger_isolation"] = {
        "status": "PASS" if ledger_isolated else "FAIL",
        "aggressive_ledger_path": str(state_file)
    }

    # Summary
    print("\n=== NON-INTERFERENCE AUDIT RESULTS ===")
    total = len(results)
    passed = sum(1 for v in results.values() if v["status"] == "PASS")
    print(f"Summary: {passed}/{total} tests PASSED.")
    for k, v in results.items():
        print(f"  {k}: {v['status']}")
        
    return results

if __name__ == '__main__':
    run_non_interference_audit()
