"""
Restores sec-aggressive-lab-panel exclusively at the bottom of the simulation section in dashboard_backend.py.
"""
import shutil
from pathlib import Path

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
BACKUP_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py.bak_bottom_agg_panel')

PANEL_HTML = """            <!-- AGGRESSIVE LAB PANEL (V2) - BOTTOM -->
            <div id="sec-aggressive-lab-panel" class="bg-cardbg border border-purple-800/80 p-4 rounded-xl shadow mt-4 space-y-3">
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
            </div>
            """

def restore_panel_bottom():
    shutil.copy2(BACKEND_PATH, BACKUP_PATH)
    print("Backup created at:", BACKUP_PATH)
    
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    target = '        </section>\n\n        <!-- SECTION 5: SISTEMA -->'
    if target in code:
        code = code.replace(target, f'            {PANEL_HTML}\n        </section>\n\n        <!-- SECTION 5: SISTEMA -->')
        BACKEND_PATH.write_text(code, encoding='utf-8')
        print("sec-aggressive-lab-panel successfully restored at the bottom of simulation section.")
    else:
        print("Error: Target anchor not found in dashboard_backend.py.")

if __name__ == '__main__':
    restore_panel_bottom()
