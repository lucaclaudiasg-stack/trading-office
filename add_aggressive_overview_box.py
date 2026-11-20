"""
Adds a compact Hermes Aggressive summary card into the Overview section (#sec-overview) of dashboard_backend.py.
"""
import shutil
from pathlib import Path

BACKEND_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py')
BACKUP_PATH = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e/dashboard_backend.py.bak_overview_agg')

AGG_OVERVIEW_CARD = """
            <!-- Hermes Aggressive Card (Overview) -->
            <div onclick="switchTab('aggressive')" class="bg-cardbg border border-purple-800/60 p-4 rounded-xl shadow cursor-pointer hover:border-purple-600 transition space-y-2">
                <div class="flex justify-between items-center">
                    <span class="text-xs font-semibold text-purple-400 flex items-center gap-1.5">
                        <i class="fa-solid fa-bolt"></i>
                        <span>HERMES AGGRESSIVE (Laboratorio)</span>
                    </span>
                    <span class="text-[9px] bg-purple-950 text-purple-300 border border-purple-800 px-1.5 py-0.5 rounded">AUTONOMO</span>
                </div>
                <div class="flex justify-between items-end">
                    <div>
                        <span class="text-gray-400 text-[10px] block">Valore Portafoglio Aggressivo</span>
                        <strong id="ov-agg-val" class="text-white text-base font-bold">143.58 EUR</strong>
                    </div>
                    <div class="text-right">
                        <span class="text-gray-400 text-[10px] block">P&L Netto</span>
                        <span id="ov-agg-pnl" class="text-emerald-400 font-semibold text-xs font-mono">+1.16 EUR (+0.81%)</span>
                    </div>
                </div>
                <div class="text-[10px] text-gray-400 pt-1 border-t border-bordercolor/60 flex justify-between">
                    <span>Ultima decisione: <strong class="text-gray-200">HOLD / NO_ACTION</strong> (20/11/2026 · 21:22 CET)</span>
                    <span class="text-purple-400 font-medium flex items-center gap-1">Apri Aggressive <i class="fa-solid fa-chevron-right text-[8px]"></i></span>
                </div>
            </div>"""

def patch_overview_agg():
    shutil.copy2(BACKEND_PATH, BACKUP_PATH)
    print("Backup created at:", BACKUP_PATH)
    
    code = BACKEND_PATH.read_text(encoding='utf-8')
    
    # Insert right after Shadow Trading card in Overview
    target = '<!-- Shadow Trading Card (Overview) -->'
    if target in code and 'HERMES AGGRESSIVE (Laboratorio)' not in code:
        # Find end of Shadow Trading card div
        idx = code.find(target)
        # Find closing div of Shadow card
        end_idx = code.find('</div>\n\n            <!-- Obiettivi Economici Card -->', idx)
        if end_idx != -1:
            code = code[:end_idx + 6] + AGG_OVERVIEW_CARD + code[end_idx + 6:]
            BACKEND_PATH.write_text(code, encoding='utf-8')
            print("Hermes Aggressive card added to Overview section successfully.")
        else:
            print("Error: Could not locate end of Shadow Trading card in Overview.")
    else:
        print("Error: Target anchor not found in dashboard_backend.py.")

if __name__ == '__main__':
    patch_overview_agg()
