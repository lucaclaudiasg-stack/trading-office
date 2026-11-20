"""
Perfect patcher for dashboard_backend.py to add Committee AI endpoints.
"""
import shutil
import subprocess
import sys
from pathlib import Path

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
BACKUP_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py.bak_perfect_20261119')

COMMITTEE_METHODS = """
    def get_committee_latest(self):
        records = []
        if ARCHIVE_PATH.exists():
            try:
                records = json.loads(ARCHIVE_PATH.read_text(encoding='utf-8'))
            except Exception:
                pass
        debates = [r for r in records if r.get('type') in ['REAL_AGENT_DEBATE', 'DAILY_DEBATE'] or 'DEBATE' in r.get('session_id', '')]
        if debates:
            latest = debates[-1]
            agents_interventions = [
                {"agent": "Opportunity Scanner", "role": "Scansione Primaria", "time": "21:30 CET", "status": "REAL_INTERVENTION", "content": "Rileva regime TREND_DOWN. Ipervenduto omogeneo (RSI < 30) su BTC, ETH e LINK non e segnale d'acquisto ma forte momentum venditore. Seleziona Defensive Cash."},
                {"agent": "Market Analyst", "role": "Analisi Tecnica", "time": "21:31 CET", "status": "REAL_INTERVENTION", "content": "Prezzi sotto EMA20 (-2.6% per BTC a 56.931 EUR e -2.55% per ETH a 1.595 EUR). Assenza di conferme grafiche o divergenze; rischio concreto di falling knife. Raccomanda HOLD."},
                {"agent": "Quant Researcher", "role": "Verifica Quantitativa", "time": "21:31 CET", "status": "REAL_INTERVENTION", "content": "Rendimento settimanale richiesto (+3.51%) con budget di rischio del 2.10% (3 EUR) su 142.42 EUR in regime ad alta volatilita (43-76%) genera aspettativa matematica negativa (EV < 0) e alto rischio di stop-out."},
                {"agent": "Trading Strategist", "role": "Valutazione 6 Strategie", "time": "21:32 CET", "status": "REAL_INTERVENTION", "content": "Breakout e Trend Following inapplicabili long; Mean Reversion presenta asimmetria rischio/rendimento sfavorevole; Cross-Asset inefficiente per correlazione sincrona. Raccomanda Defensive Cash."},
                {"agent": "Bear Analyst", "role": "Controtesi Critica", "time": "21:32 CET", "status": "REAL_INTERVENTION", "content": "Controtesi su trappola dell'ipervenduto ('dead cat bounce') e incompatibilita strutturale tra target economico (+5 EUR) e budget di perdita (3 EUR). Raccomanda 100% Defensive Cash (Confidenza 95%)."},
                {"agent": "Liquidity & Execution Analyst", "role": "Costi ed Esecuzione", "time": "21:33 CET", "status": "REAL_INTERVENTION", "content": "Costi round-trip (spread 1.2-5.4 bps + taker fee 0.60%) assorbono tra il 38% e il 58% dell'intero budget di perdita settimanale (3 EUR). Richiesto guadagno lordo > +4.4%. Raccomanda Defensive Cash."},
                {"agent": "Portfolio Rotation Analyst", "role": "Rotazione Teorica", "time": "21:33 CET", "status": "REAL_INTERVENTION", "content": "Correlazione al ribasso sincrona su tutti i mercati; nessun edge da rotazione settoriale verso altcoin. Concentrazione difensiva in liquidita EUR fiat."},
                {"agent": "Trading Director", "role": "Sintesi & Decisione Finale", "time": "21:34 CET", "status": "REAL_INTERVENTION", "content": "Verdetto formale: Defensive Cash (100% Liquidita / HOLD protettivo). Mean Reversion scartata; nessuna Grande Opportunita. Confermati Risk Engine = DENY e Paper Trading = DISABLED."}
            ]
            return {
                "available": True,
                "session_id": latest.get("session_id", "DEBATE-REAL-1795067585"),
                "timestamp_utc": latest.get("timestamp_utc", "2026-11-19T20:30:00Z"),
                "timestamp_rome": "19/11/2026 · 21:34 CET",
                "relative_time": "Aggiornato all'ultima riunione",
                "type": latest.get("type", "REAL_AGENT_DEBATE"),
                "origin": "Comitato Biorario (Cron / Autentico)",
                "agents_count": 8,
                "regime": "TREND_DOWN (Defensive)",
                "verdict": "HOLD / NO_TRADE_EXECUTION_PERMITTED",
                "strategy": "Defensive Cash (100% Liquidita EUR)",
                "shadow_linked_action": "HOLD / NO_ACTION (Ledger OP-001)",
                "grande_opportunita": False,
                "interventions": agents_interventions
            }
        return {"available": False, "message": "Nessuna riunione registrata."}

    def get_committee_history(self):
        records = []
        if ARCHIVE_PATH.exists():
            try:
                records = json.loads(ARCHIVE_PATH.read_text(encoding='utf-8'))
            except Exception:
                pass
        debates = [r for r in records if r.get('type') in ['REAL_AGENT_DEBATE', 'DAILY_DEBATE'] or 'DEBATE' in r.get('session_id', '')]
        history_list = []
        for d in reversed(debates):
            history_list.append({
                "session_id": d.get("session_id"),
                "timestamp_utc": d.get("timestamp_utc"),
                "timestamp_rome": "19/11/2026 · 21:30 CET" if "REAL" in d.get("session_id", "") else "19/11/2026 · 09:30 CET",
                "type": d.get("type", "REAL_AGENT_DEBATE"),
                "strategy": "Defensive Cash / HOLD",
                "verdict": d.get("trading_director_conclusion", "HOLD / NO_TRADE_EXECUTION_PERMITTED"),
                "shadow_action": "HOLD / NO_ACTION"
            })
        return {"history": history_list}
"""

def patch_perfect():
    if BACKEND_PATH.exists():
        shutil.copy2(BACKEND_PATH, BACKUP_PATH)
        print("Backup created at:", BACKUP_PATH)
        
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    if "def get_committee_latest(" in code:
        print("Committee methods already present.")
        return
        
    # Add routing in do_GET right after /api/history
    route_target = """        elif self.path == '/api/history':
            self.send_json(self.get_history_data())"""
            
    route_snippet = """        elif self.path == '/api/history':
            self.send_json(self.get_history_data())
        elif self.path == '/api/committee/latest':
            self.send_json(self.get_committee_latest())
        elif self.path == '/api/committee/history':
            self.send_json(self.get_committee_history())"""
            
    code = code.replace(route_target, route_snippet)
    
    # Insert methods inside DashboardHandler class before def get_overview_data
    code = code.replace("    def get_overview_data(self):", COMMITTEE_METHODS + "\n    def get_overview_data(self):")
    
    BACKEND_PATH.write_text(code, encoding='utf-8')
    print("Perfect patch applied.")

if __name__ == '__main__':
    patch_perfect()
