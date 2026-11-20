"""
Qualitative Audit of the first REAL_AGENT_DEBATE session.
Enforces methodological corrections and records audit findings in staging.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

REPORT_PATH = Path('/app/staging/qualitative_debate_audit_report.json')
if not REPORT_PATH.parent.exists():
    REPORT_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/qualitative_debate_audit_report.json')

def audit_session():
    audit_data = {
        "audit_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "target_session_id": "DEBATE-REAL-1795067585",
        "findings": {
            "1_llm_calls_verification": {
                "status": "PASS",
                "evidence": "7 specialist invocations dispatched via fan-out (proc_a157174c6cff) with unique delivery IDs + Trading Director synthesis (proc_748221276633)."
            },
            "2_portfolio_hold_vs_no_new_exposure_vs_defensive_cash": {
                "status": "REFINEMENT_NOTED",
                "detail": "La sessione ha trattato 'Defensive Cash' come sinonimo di astensione da nuove esposizioni. Correzione metodologica: distinguere esplicitamente HOLD del portafoglio esistente (BTC/ETH già detenuti) da NO NEW EXPOSURE e da posizionamento attivo in liquidità EUR."
            },
            "3_ev_negative_quant_evidence": {
                "status": "RECLASSIFIED",
                "detail": "L'affermazione EV < 0 formulata dal Quant Researcher viene formalmente riclassificata come 'ipotesi quantitativa derivata da stima di rischio/rendimento in regime di alta volatilità, non pienamente dimostrata da backtest formale out-of-sample'."
            },
            "4_execution_costs_break_even": {
                "status": "PASS",
                "detail": "Il calcolo dei costi (spread 1.2-5.4 bps + commissioni taker ~0.80%-1.20% round-trip) è risultato matematicamente corretto, dimostrando che l'attrito assorbe tra il 38% e il 58% del budget di rischio settimanale di 3 EUR."
            },
            "5_bear_analyst_independence_and_future_directive": {
                "status": "CORRECTION_APPLIED",
                "detail": "Il Bear Analyst ha presentato una controtesi indipendente (trappola dell'ipervenduto). Nuova regola metodologica permanente: nelle prossime riunioni, il Bear Analyst dovrà contestare attivamente anche le strategie difensive (es. costo opportunità del cash in caso di rimbalzo violento o inflazione/FX)."
            }
        },
        "security_gates": {
            "risk_engine": "DENY",
            "paper_trading": "DISABLED",
            "real_trading": "DISABLED",
            "coinbase_mcp": "READ_ONLY"
        }
    }
    
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(audit_data, indent=2, default=str), encoding='utf-8')
    print("Qualitative audit report generated successfully at:", REPORT_PATH)

if __name__ == '__main__':
    audit_session()
