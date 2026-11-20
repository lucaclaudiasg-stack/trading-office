"""
Reinserts Hermes Aggressive box into Simulation section and adds top summary box in Aggressive tab,
updating Chart 1, 2, and 5 to include Hermes Aggressive in purple/violet.
"""
from pathlib import Path
import shutil

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
BACKUP_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py.bak_reinsert_aggressive')

def apply_reinsert():
    shutil.copy2(BACKEND_PATH, BACKUP_PATH)
    print("Backup created at:", BACKUP_PATH)
    
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    # 1. Update Simulation grid from 3 columns to 4 columns
    old_sim_grid = '<div class="grid grid-cols-1 md:grid-cols-3 gap-3">'
    new_sim_grid = '<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">'
    if old_sim_grid in code:
        code = code.replace(old_sim_grid, new_sim_grid)

    # 2. Add Hermes Aggressive box into Simulation grid right after Hermes AI or at the end
    agg_box_sim = """
                <!-- Hermes Aggressive Box -->
                <div class="bg-cardbg border border-purple-800/80 p-3.5 rounded-xl shadow space-y-1.5">
                    <div class="flex justify-between items-center">
                        <strong class="text-purple-400 text-xs flex items-center gap-1"><i class="fa-solid fa-bolt"></i> Hermes Aggressive</strong>
                        <span class="text-[9px] bg-purple-950 text-purple-300 border border-purple-800 px-1.5 py-0.5 rounded font-bold">SIMULATION_ONLY</span>
                    </div>
                    <div class="text-xl font-bold text-white mt-1" id="sim-agg-val">143.58 EUR</div>
                    <div class="flex justify-between text-xs pt-1 border-t border-bordercolor/60">
                        <span class="text-gray-400">P&L Netto:</span>
                        <span class="text-emerald-400 font-semibold" id="sim-agg-pnl">+1.16 EUR (+0.81%)</span>
                    </div>
                    <div class="flex justify-between text-xs">
                        <span class="text-gray-400">Esposizione:</span>
                        <span class="text-purple-300 font-mono text-[11px]" id="sim-agg-exp">98.24% Spot</span>
                    </div>
                    <div class="flex justify-between text-xs">
                        <span class="text-gray-400">Drawdown max:</span>
                        <span class="text-emerald-400 font-mono text-[11px]">0.00%</span>
                    </div>
                    <div class="text-[10px] text-gray-400 pt-1 border-t border-bordercolor/60 flex justify-between items-center">
                        <span>Azione: <strong class="text-gray-200">HOLD / NO_ACTION</strong></span>
                        <button onclick="switchTab('aggressive')" class="text-purple-400 hover:text-purple-300 font-semibold flex items-center gap-1">Apri Aggressive <i class="fa-solid fa-chevron-right text-[8px]"></i></button>
                    </div>
                </div>"""

    anchor_def = 'id="sim-def-pnl">0.00 EUR (0.00%)</span>\n                    </div>\n                </div>\n            </div>'
    if anchor_def in code and 'id="sim-agg-val"' not in code:
        code = code.replace(anchor_def, 'id="sim-def-pnl">0.00 EUR (0.00%)</span>\n                    </div>\n                </div>\n' + agg_box_sim + '\n            </div>')
        print("Hermes Aggressive box added to Simulation grid.")

    # 3. Add top summary box in #sec-aggressive (before 'Ultima Scelta dell'Agente')
    agg_top_summary = """            <!-- BOX RIEPILOGATIVO IN ALTO (HERMES AGGRESSIVE) -->
            <div class="bg-cardbg border border-purple-800/80 p-4 rounded-xl shadow space-y-3">
                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b border-bordercolor pb-2.5">
                    <div class="flex items-center gap-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-purple-500 animate-pulse"></span>
                        <h3 class="text-sm font-bold text-white flex items-center gap-1.5">
                            <i class="fa-solid fa-bolt text-purple-400"></i>
                            <span>Hermes Aggressive — Riepilogo Portafoglio Virtuale</span>
                        </h3>
                    </div>
                    <span class="bg-purple-950 text-purple-300 border border-purple-800 text-[10px] px-2 py-0.5 rounded font-mono font-bold">ISOLATO / SIMULATION_ONLY</span>
                </div>

                <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor">
                        <span class="text-gray-400 block text-[10px]">Valore Corrente</span>
                        <strong class="text-white text-sm">143.58 EUR</strong>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor">
                        <span class="text-gray-400 block text-[10px]">P&L Netto</span>
                        <strong class="text-emerald-400 text-sm">+1.16 EUR (+0.81%)</strong>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor">
                        <span class="text-gray-400 block text-[10px]">Esposizione Virtuale</span>
                        <strong class="text-purple-300 text-sm">98.24% Spot</strong>
                    </div>
                    <div class="bg-darkbg p-2.5 rounded border border-bordercolor">
                        <span class="text-gray-400 block text-[10px]">Drawdown Massimo</span>
                        <strong class="text-emerald-400 text-sm">0.00%</strong>
                    </div>
                </div>

                <div class="flex flex-col sm:flex-row justify-between text-[11px] text-gray-400 bg-black/30 p-2 rounded border border-bordercolor/60 gap-1">
                    <span>Strategia / Decisione: <strong class="text-white">Adaptive Hybrid V1 / HOLD</strong></span>
                    <span>Ultimo Aggiornamento: <strong class="text-gray-300">20/11/2026 · 21:22 CET</strong></span>
                </div>
            </div>

            <!-- Blocco: Ultima Scelta dell'Agente -->"""

    old_choice_start = '<!-- Blocco: Ultima Scelta dell\'Agente -->'
    if old_choice_start in code and 'BOX RIEPILOGATIVO IN ALTO' not in code:
        code = code.replace(old_choice_start, agg_top_summary)
        print("Top summary box added to #sec-aggressive.")

    # 4. Update Chart 1 in JS to include Hermes Aggressive (4 curves)
    old_3lines = """datasets: [
                            { label: 'Hermes AI', data: [142.42, 143.10, 143.58, 143.20, 143.58, 143.58], borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.1)', tension: 0.3, fill: true },
                            { label: 'Buy & Hold', data: [142.42, 143.10, 143.58, 143.20, 143.58, 143.58], borderColor: '#10b981', borderDash: [4, 4], tension: 0.3 },
                            { label: 'Defensive EUR', data: [142.42, 142.42, 142.42, 142.42, 142.42, 142.42], borderColor: '#f59e0b', tension: 0.1 }
                        ]"""

    new_4lines = """datasets: [
                            { label: 'Hermes AI', data: [142.42, 143.10, 143.58, 143.20, 143.58, 143.58], borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.05)', tension: 0.3 },
                            { label: 'Hermes Aggressive', data: [142.42, 143.10, 143.58, 143.58, 143.58, 143.58], borderColor: '#a855f7', backgroundColor: 'rgba(168, 85, 247, 0.15)', tension: 0.3, fill: true },
                            { label: 'Buy & Hold', data: [142.42, 143.10, 143.58, 143.20, 143.58, 143.58], borderColor: '#10b981', borderDash: [4, 4], tension: 0.3 },
                            { label: 'Defensive EUR', data: [142.42, 142.42, 142.42, 142.42, 142.42, 142.42], borderColor: '#f59e0b', tension: 0.1 }
                        ]"""
    if old_3lines in code:
        code = code.replace(old_3lines, new_4lines)
        print("Chart 1 updated to 4 curves.")

    # 5. Update Chart 5 (Drawdown) to include Hermes Aggressive
    old_dd = """labels: ['Hermes AI', 'Buy & Hold', 'Defensive EUR'],
                        datasets: [{
                            label: 'Drawdown Massimo (%)',
                            data: [0.00, 0.00, 0.00],
                            backgroundColor: ['#3b82f6', '#10b981', '#f59e0b'],
                            borderRadius: 4
                        }]"""

    new_dd = """labels: ['Hermes AI', 'Hermes Aggressive', 'Buy & Hold', 'Defensive EUR'],
                        datasets: [{
                            label: 'Drawdown Massimo (%)',
                            data: [0.00, 0.00, 0.00, 0.00],
                            backgroundColor: ['#3b82f6', '#a855f7', '#10b981', '#f59e0b'],
                            borderRadius: 4
                        }]"""
    if old_dd in code:
        code = code.replace(old_dd, new_dd)
        print("Chart 5 updated with Hermes Aggressive drawdown.")

    BACKEND_PATH.write_text(code, encoding='utf-8')
    print("Dashboard backend successfully updated with reinserted Aggressive components.")

if __name__ == '__main__':
    apply_reinsert()
