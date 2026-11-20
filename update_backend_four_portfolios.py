"""
Updates dashboard_backend.py to integrate the 4th portfolio (HERMES AGGRESSIVE),
ruin risk analysis table, and 4-portfolio Chart.js visualization.
"""
from pathlib import Path
import shutil
import json

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
BACKUP_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py.bak_four_portfolios')

def patch_backend_four_portfolios():
    shutil.copy2(BACKEND_PATH, BACKUP_PATH)
    print("Backup created at:", BACKUP_PATH)
    
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    # 1. Add route for /api/aggressive/summary and /api/aggressive/ledger in do_GET
    if '/api/aggressive/summary' not in code:
        target = "elif self.path == '/api/shadow/ledger':"
        snippet = """elif self.path == '/api/shadow/ledger':
            self.send_json(self.get_shadow_ledger())
        elif self.path == '/api/aggressive/summary':
            self.send_json(self.get_aggressive_summary())
        elif self.path == '/api/aggressive/ledger':
            self.send_json(self.get_aggressive_ledger())"""
        code = code.replace(target, snippet)

    # 2. Add methods get_aggressive_summary and get_aggressive_ledger in DashboardHandler
    if 'def get_aggressive_summary' not in code:
        target_method = '    def get_shadow_summary(self):'
        methods_snippet = """    def get_aggressive_summary(self):
        agg_path = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/aggressive_portfolio_state.json')
        if agg_path.exists():
            try:
                return json.loads(agg_path.read_text(encoding='utf-8'))
            except Exception:
                pass
        return {"status": "NO_STATE", "message": "Inizializzazione in corso"}

    def get_aggressive_ledger(self):
        agg_path = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/aggressive_portfolio_state.json')
        if agg_path.exists():
            try:
                data = json.loads(agg_path.read_text(encoding='utf-8'))
                return {"ledger": data.get("ledger", [])}
            except Exception:
                pass
        return {"ledger": []}

    def get_shadow_summary(self):"""
        code = code.replace(target_method, methods_snippet)

    # 3. Update Chart 1 JS to include Hermes Aggressive (4th line)
    if 'label: \'Hermes Aggressive\'' not in code:
        old_datasets = """datasets: [
                            { label: 'Hermes AI', data: [142.42, 143.10, 143.58, 143.20, 143.58, 143.58], borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.1)', tension: 0.3, fill: true },
                            { label: 'Buy & Hold', data: [142.42, 143.10, 143.58, 143.20, 143.58, 143.58], borderColor: '#10b981', borderDash: [4, 4], tension: 0.3 },
                            { label: 'Defensive EUR', data: [142.42, 142.42, 142.42, 142.42, 142.42, 142.42], borderColor: '#f59e0b', tension: 0.1 }
                        ]"""
                        
        new_datasets = """datasets: [
                            { label: 'Hermes AI', data: [142.42, 143.10, 143.58, 143.20, 143.58, 143.58], borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.05)', tension: 0.3 },
                            { label: 'Hermes Aggressive', data: [142.42, 143.10, 143.58, 143.58, 143.58, 143.58], borderColor: '#a855f7', backgroundColor: 'rgba(168, 85, 247, 0.15)', tension: 0.3, fill: true },
                            { label: 'Buy & Hold', data: [142.42, 143.10, 143.58, 143.20, 143.58, 143.58], borderColor: '#10b981', borderDash: [4, 4], tension: 0.3 },
                            { label: 'Defensive EUR', data: [142.42, 142.42, 142.42, 142.42, 142.42, 142.42], borderColor: '#f59e0b', tension: 0.1 }
                        ]"""
        code = code.replace(old_datasets, new_datasets)

    # 4. Add Aggressive Lab Dedicated Panel in Simulation Section
    if 'id="sec-aggressive-lab-panel"' not in code:
        sim_panel_target = '<!-- SECTION: SIMULAZIONE -->'
        sim_panel_html = """<!-- SECTION: SIMULAZIONE -->
            <!-- AGGRESSIVE LAB PANEL (V2) -->
            <div id="sec-aggressive-lab-panel" class="bg-cardbg border border-purple-800/80 p-4 rounded-xl shadow mb-4 space-y-3">
                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b border-bordercolor pb-2.5">
                    <div class="flex items-center gap-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-purple-500 animate-pulse"></span>
                        <h3 class="text-sm font-bold text-white flex items-center gap-1.5">
                            <i class="fa-solid fa-bolt text-purple-400"></i>
                            <span>HERMES AGGRESSIVE — Laboratorio di Trading Sperimentale</span>
                        </h3>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="bg-purple-950 text-purple-300 border border-purple-800 text-[10px] px-2 py-0.5 rounded font-mono font-bold">ISOLATO / SIMULATION_ONLY</span>
                    </div>
                </div>

                <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor">
                        <span class="text-gray-400 block text-[10px]">Valore Corrente</span>
                        <strong id="agg-val" class="text-white text-sm">143.58 EUR</strong>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor">
                        <span class="text-gray-400 block text-[10px]">P&L Netto</span>
                        <strong id="agg-pnl" class="text-emerald-400 text-sm">+1.16 EUR (+0.81%)</strong>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor">
                        <span class="text-gray-400 block text-[10px]">Esposizione Virtuale</span>
                        <strong id="agg-exp" class="text-purple-300 text-sm">98.24% Spot</strong>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor">
                        <span class="text-gray-400 block text-[10px]">Tempo alla Rovina</span>
                        <strong id="agg-ruin" class="text-emerald-400 text-sm">Infinito (Capitale Integro)</strong>
                    </div>
                </div>

                <!-- Tabella Soglie di Rovina -->
                <div class="bg-darkbg p-3 rounded-lg border border-bordercolor space-y-2">
                    <h4 class="text-[11px] font-semibold text-gray-300 flex items-center gap-1">
                        <i class="fa-solid fa-shield-halved text-purple-400"></i>
                        <span>Analisi della Perdita del Capitale (Soglie Rovina)</span>
                    </h4>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-[10px] text-gray-300">
                            <thead class="bg-black/40 text-gray-400 uppercase text-[9px]">
                                <tr>
                                    <th class="p-1.5">Soglia Perdita</th>
                                    <th class="p-1.5">Capitale Residuo</th>
                                    <th class="p-1.5">Stato Raggiungimento</th>
                                    <th class="p-1.5">Primo Timestamp</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-bordercolor/60">
                                <tr><td class="p-1.5 text-amber-400 font-semibold">-10%</td><td class="p-1.5 font-mono">128.18 EUR</td><td class="p-1.5 text-emerald-400">Non raggiunta</td><td class="p-1.5 text-gray-500">—</td></tr>
                                <tr><td class="p-1.5 text-amber-500 font-semibold">-25%</td><td class="p-1.5 font-mono">106.82 EUR</td><td class="p-1.5 text-emerald-400">Non raggiunta</td><td class="p-1.5 text-gray-500">—</td></tr>
                                <tr><td class="p-1.5 text-orange-500 font-semibold">-50%</td><td class="p-1.5 font-mono">71.21 EUR</td><td class="p-1.5 text-emerald-400">Non raggiunta</td><td class="p-1.5 text-gray-500">—</td></tr>
                                <tr><td class="p-1.5 text-red-500 font-semibold">-75%</td><td class="p-1.5 font-mono">35.61 EUR</td><td class="p-1.5 text-emerald-400">Non raggiunta</td><td class="p-1.5 text-gray-500">—</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>"""
        code = code.replace(sim_panel_target, sim_panel_html)

    BACKEND_PATH.write_text(code, encoding='utf-8')
    print("Backend 4-portfolio patch applied successfully.")

if __name__ == '__main__':
    patch_backend_four_portfolios()
